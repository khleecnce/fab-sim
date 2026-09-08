"""FabSim HTTP API — 웹 배포용. Studio(단일 사용자)와 달리 여러 클라이언트를 받는다.

  uvicorn sim.api:app --host 0.0.0.0 --port 8080
  pip install 'fabsim[web]'

왜 별도인가: Streamlit은 세션당 스크립트를 통째로 재실행하는 구조라 다중 사용자·
자동화 연동에 맞지 않는다. 계산 코어는 같고(sim.slots / sim.engine), 이 파일은
그 코어를 HTTP로 노출하는 얇은 층이다.

엔드포인트
  GET  /api/health
  GET  /api/catalog        슬롯·구현·팩 목록 (UI가 이걸로 화면을 그린다)
  POST /api/simulate       레시피 + 슬롯 설정 → 결과
  GET  /api/scope/{agent}  조사 범위 (읽기 전용 — 웹에서 편집은 막는다)
  GET  /                   내장 웹 UI
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

try:
    from fastapi import FastAPI, HTTPException, UploadFile, File, Form
    from fastapi.responses import HTMLResponse
    from pydantic import BaseModel, Field
except ImportError:  # pragma: no cover
    raise SystemExit("웹 API에는 fastapi가 필요합니다: pip install 'fabsim[web]'")

from sim.engine import Recipe, available_models  # noqa: E402
from sim.metrics.uniformity import compute_metrics  # noqa: E402
from sim.params import available_packs, load_pack  # noqa: E402
import sim.models  # noqa: F401,E402
import sim.slots as S  # noqa: E402
from sim.recipe_builder import load_schemas, to_overrides, coverage  # noqa: E402

app = FastAPI(title="FabSim API", version="0.3.0")


class SimRequest(BaseModel):
    pack: str = "oxide_silica"
    wafer: str = "NPW"
    pressure_psi: Optional[float] = None
    rpm_wafer: Optional[float] = None
    rpm_platen: Optional[float] = None
    time_s: float = 60.0
    initial_thickness_nm: Optional[float] = None
    zone_pressures_psi: Optional[List[float]] = None
    zone_edges_norm: Optional[List[float]] = None
    meta: Dict[str, str] = Field(default_factory=dict)
    slots: Dict[str, str] = Field(default_factory=dict)
    # 구성요소 스키마 값 — "slurry.abrasive.primary_size_nm": 60 형식.
    # 연결된 것만 팩 오버라이드가 되고, 나머지는 경고로 돌아온다.
    components: Dict[str, Any] = Field(default_factory=dict)
    # V2 3D UI가 직접 던지는 팩 키 오버라이드 (예: {"slurry_ph": 11.0}).
    # 구성요소 경로를 거치지 않고 팩터를 즉시 흔들 수 있는 통로다.
    pack_overrides: Dict[str, float] = Field(default_factory=dict)
    model: str = "tier1.preston_radial"


@app.get("/api/health")
def health():
    return {"ok": True, "version": "0.3.0", "models": available_models()}


@app.get("/api/catalog")
def catalog():
    """UI가 화면을 그리는 데 필요한 전부 — 슬롯·구현·출처·팩."""
    reg = S.slots()
    slots = []
    for sid in S.SLOT_ORDER:
        slots.append({
            "id": sid, "label": S.SLOT_LABEL[sid], "owner": S.SLOT_OWNER[sid],
            "impls": [{
                "id": im.id, "label": im.label, "status": im.status,
                "note": im.note, "agent": im.agent, "warning": im.warning,
                "params": im.params,
            } for im in reg[sid].values()],
        })
    packs = []
    for name in available_packs():
        try:
            pk = load_pack(name)
            conf: Dict[str, int] = {}
            for prm in pk.params.values():
                conf[prm.confidence] = conf.get(prm.confidence, 0) + 1
            packs.append({"id": name, "description": pk.description,
                          "confidence_counts": conf,
                          "params": [{"key": p.key, "value": p.value, "unit": p.unit,
                                      "confidence": p.confidence,
                                      "source": p.source} for p in pk.params.values()]})
        except Exception as e:
            packs.append({"id": name, "error": str(e)})
    comps = []
    for cname, spec in load_schemas().items():
        comps.append({
            "id": cname, "label": spec.get("component", cname),
            "owner": spec.get("owner"), "description": spec.get("description", ""),
            "groups": [{
                "id": g["id"], "label": g.get("label", g["id"]),
                "origin": g.get("origin"), "owner": g.get("owner", spec.get("owner")),
                "why": g.get("why", ""),
                "fields": [{
                    "path": f"{cname}.{g['id']}.{fl['key']}",
                    "key": fl["key"], "label": fl.get("label", fl["key"]),
                    "type": fl.get("type", "text"), "unit": fl.get("unit", ""),
                    "options": fl.get("options"), "typical": fl.get("typical"),
                    "origin": fl.get("origin"), "status": fl.get("status"),
                    "maps_to": fl.get("maps_to"), "confidence": fl.get("confidence"),
                    "note": fl.get("note", ""),
                } for fl in g.get("fields", [])],
            } for g in spec.get("groups", [])],
        })
    return {"slots": slots, "default_config": S.default_config(), "packs": packs,
            "components": comps, "coverage": coverage()}


@app.post("/api/simulate")
def api_simulate(req: SimRequest):
    comp_over, comp_warn = to_overrides(req.components) if req.components else ({}, [])
    try:
        rec = Recipe(
            pack_overrides=comp_over,
            pack=req.pack, wafer=req.wafer,  # type: ignore[arg-type]
            pressure_psi=req.pressure_psi, rpm_wafer=req.rpm_wafer,
            rpm_platen=req.rpm_platen, time_s=req.time_s,
            initial_thickness_nm=req.initial_thickness_nm,
            zone_pressures_psi=req.zone_pressures_psi,
            zone_edges_norm=req.zone_edges_norm, meta=req.meta,
        ).resolve()
    except KeyError as e:
        raise HTTPException(400, f"팩 해석 실패: {e}")

    r_max = rec.wafer_radius_m - rec.edge_exclusion_m
    radius = np.linspace(0.0, r_max, rec.n_points)
    try:
        mrr, notes, trace = S.run_pipeline(rec, radius, req.slots)
    except KeyError as e:
        raise HTTPException(400, str(e))

    mrr_nm = mrr * 1e9 * 60
    removed = mrr_nm * (rec.time_s / 60)
    remaining = (rec.initial_thickness_nm - removed
                 if rec.initial_thickness_nm else None)
    m = compute_metrics(radius, removed if remaining is None else remaining,
                        n_points=rec.n_points)
    return {
        "mrr_mean_nm_min": float(np.mean(mrr_nm)),
        "mrr_min_nm_min": float(np.min(mrr_nm)),
        "mrr_max_nm_min": float(np.max(mrr_nm)),
        "removed_mean_nm": float(np.mean(removed)),
        "remaining_mean_nm": float(np.mean(remaining)) if remaining is not None else None,
        "metrics": {
            "ttv_nm": m.ttv_nm, "cv_pct": m.cv_pct,
            "radial_sigma_pct": m.radial_sigma_pct,
            "radial_range_pct": m.radial_range_pct,
            "radial_maxring_range_nm": m.radial_maxring_range_nm,
            "wiwnu_3sigma_pct": m.wiwnu_3sigma_pct,
            "wiwnu_halfrange_pct": m.wiwnu_halfrange_pct,
            "definition": m.definition,
        },
        "profile": {"radius_mm": (radius * 1000).round(2).tolist(),
                    "mrr_nm_min": mrr_nm.round(3).tolist()},
        "trace": trace,
        "notes": notes + comp_warn,
        "component_overrides": comp_over,
        "component_warnings": comp_warn,
        "not_computed": ["roughness_ra", "dishing", "erosion",
                         "metal_contamination", "defect_density"],
    }


@app.post("/api/simulate/v2")
def api_simulate_v2(req: SimRequest):
    """V2 엔드포인트 — 3D 인터페이스가 쓰는 통합 결과.

    /api/simulate(슬롯 파이프라인)와 달리 engine.simulate()를 그대로 태워서
    **병합 파라미터 + 장비 출력값**을 함께 돌려준다. 3D 화면의 각 파트를
    클릭했을 때 보여줄 것이 전부 여기 들어 있다.
    """
    from sim.engine import simulate as _simulate

    comp_over, comp_warn = to_overrides(req.components) if req.components else ({}, [])
    # 3D UI는 팩 키를 직접 던진다(예: slurry_ph). 구성요소 경로와 합친다.
    overrides = dict(comp_over)
    overrides.update(req.pack_overrides or {})
    try:
        res = _simulate(Recipe(
            pack=req.pack, wafer=req.wafer,  # type: ignore[arg-type]
            pressure_psi=req.pressure_psi, rpm_wafer=req.rpm_wafer,
            rpm_platen=req.rpm_platen, time_s=req.time_s,
            initial_thickness_nm=req.initial_thickness_nm,
            zone_pressures_psi=req.zone_pressures_psi,
            zone_edges_norm=req.zone_edges_norm, meta=req.meta,
            pack_overrides=overrides,
        ), model=req.model)
    except KeyError as e:
        raise HTTPException(400, f"팩 해석 실패: {e}")
    except Exception as e:
        raise HTTPException(400, f"{type(e).__name__}: {e}")

    s = res.summary()
    s["profile"] = {
        "radius_mm": (res.radius_m * 1000).round(2).tolist(),
        "mrr_nm_min": res.mrr_nm_per_min.round(3).tolist(),
        "removed_nm": res.removed_nm.round(3).tolist(),
        "remaining_nm": (res.remaining_nm.round(3).tolist()
                         if res.remaining_nm is not None else None),
    }
    s["component_warnings"] = comp_warn
    s["provenance"] = res.provenance
    # ── 모든 실행을 DB에 저장 (사용자 지시: 다음 시뮬레이션에 반영) ──────
    # 저장 실패가 시뮬레이션을 죽이면 안 된다 — 결과는 돌려주고 경고만 싣는다.
    try:
        from sim import store as _store
        inputs = {"pack": req.pack, "wafer": req.wafer, "model": req.model,
                  "pressure_psi": req.pressure_psi, "rpm_wafer": req.rpm_wafer,
                  "rpm_platen": req.rpm_platen, "time_s": req.time_s,
                  "initial_thickness_nm": req.initial_thickness_nm,
                  "zone_pressures_psi": req.zone_pressures_psi,
                  "pack_overrides": overrides}
        s["run_id"] = _store.save_run(s, inputs)
    except Exception as e:
        s["run_id"] = None
        s.setdefault("notes", []).append(f"⚠ 런 저장 실패: {type(e).__name__}: {e}")
    return s


# ═══════════════════════════════════════ 런 저장소 · 실측 임포트

@app.get("/api/runs")
def api_runs(limit: int = 50, pack: Optional[str] = None):
    from sim import store
    return {"runs": store.recent_runs(limit=limit, pack=pack), "stats": store.stats()}


@app.get("/api/runs/{rid}")
def api_run(rid: str):
    from sim import store
    r = store.get_run(rid)
    if not r:
        raise HTTPException(404, "없는 run id")
    return r


@app.get("/api/measurements")
def api_measurements(limit: int = 100):
    from sim import store
    return {"measurements": store.list_measurements(limit=limit)}


@app.post("/api/import")
async def api_import(file: UploadFile = File(...),
                     pack_hint: Optional[str] = Form(None),
                     label: Optional[str] = Form(None)):
    """엑셀/CSV/JSON 실측 파일을 그대로 넣으면 DB에 쌓인다.

    사용자 지시: "엑셀이나 다른 포맷 real data 파일을 넣으면 그냥 그대로
    빅데이터가 프로그램에 입력되도록".

    컬럼 매핑은 tools/ingest_measurement.py의 별칭 표를 쓴다(압력/psi/다운포스…).
    ⚠ 매핑이 안 되는 컬럼은 버리지 않고 `unmapped_columns`로 돌려준다.
      조건(압력·시간)이 없으면 저장은 하되 `comparable: false` — 시뮬레이션과
      비교할 수 없다는 사실을 숨기지 않는다.
    """
    import tempfile
    from sim import store
    sys.path.insert(0, str(ROOT / "tools"))
    import ingest_measurement as ing

    suffix = Path(file.filename or "upload").suffix.lower() or ".csv"
    if suffix not in (".csv", ".xlsx", ".xls", ".json", ".tsv", ".txt"):
        raise HTTPException(400, f"지원하지 않는 형식: {suffix} (csv/xlsx/json)")
    data = await file.read()
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(data)
        tmp_path = Path(tmp.name)
    try:
        r = ing.ingest(tmp_path, run_id=label or "upload", peek=True)
    except SystemExit as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(400, f"파싱 실패: {type(e).__name__}: {e}")
    finally:
        tmp_path.unlink(missing_ok=True)

    r["source_file"] = file.filename
    quality = {"blockers": r["blockers"], "warnings": r["warnings"],
               "unmapped_columns": r["unmapped_columns"],
               "column_mapping": r["column_mapping"], "comparable": r["comparable"]}
    mid = store.save_measurement(
        source_file=file.filename or "upload", conditions=r["conditions"],
        points=r["points"], quality=quality, run_label=label, pack_hint=pack_hint)
    iid = store.save_import(file.filename or "upload", r["n_points"], 1,
                            r["blockers"] + r["warnings"])
    return {"measurement_id": mid, "import_id": iid,
            "n_points": r["n_points"], "conditions": r["conditions"],
            "column_mapping": r["column_mapping"],
            "unmapped_columns": r["unmapped_columns"],
            "blockers": r["blockers"], "warnings": r["warnings"],
            "comparable": r["comparable"],
            "mrr_mean": store.get_measurement(mid)["mrr_mean"],
            "stats": store.stats()}


@app.get("/api/calibration/{pack}")
def api_calibration(pack: str):
    """이 팩에 대해 DB의 실측이 만드는 Kp 보정계수 — 실측이 반영되는 유일한 통로."""
    from sim import store
    from sim.engine import simulate as _simulate

    def _predict(cond):
        kw = {k: cond[k] for k in ("pressure_psi", "rpm_wafer", "rpm_platen", "time_s")
              if k in cond}
        return float(np.mean(_simulate(Recipe(pack=pack, **kw)).mrr_nm_per_min))

    cal = store.calibration_factor(pack, _predict)
    return cal.to_dict()


@app.get("/api/factors")
def api_factors():
    """병합 파라미터 정의 — UI가 축·파트 매핑을 그리는 데 쓴다."""
    from sim.factors import FACTOR_SPEC, MRR_COUPLED
    return {"factors": [
        {"key": k, "symbol": sym, "name": name, "axis": axis, "parts": parts,
         "mrr_coupled": k in MRR_COUPLED}
        for k, (sym, name, axis, parts) in FACTOR_SPEC.items()]}


@app.get("/api/scope/{agent}")
def api_scope(agent: str):
    sys.path.insert(0, str(ROOT / "tools"))
    try:
        import scope
    except Exception:
        raise HTTPException(503, "SCOPE.yaml 없음 (배포본에는 조사범위가 포함되지 않습니다)")
    try:
        e = scope.effective(agent)
    except Exception as ex:
        raise HTTPException(404, str(ex))
    e["queries"] = scope.queries(agent)
    return e


_INDEX = Path(__file__).resolve().parent / "web" / "index.html"
_STUDIO3D = Path(__file__).resolve().parent / "web" / "studio3d.html"


@app.get("/3d", response_class=HTMLResponse)
def studio3d():
    """3D 스튜디오 — V2의 메인 화면 (ARCHITECTURE-V2.md §0).

    실제 장비 모양을 그리고, 각 부위를 클릭하면 그 파트의 설정 패널이 열린다.
    """
    if _STUDIO3D.exists():
        return _STUDIO3D.read_text()
    raise HTTPException(404, "studio3d.html 없음")


@app.get("/", response_class=HTMLResponse)
def index():
    if _INDEX.exists():
        return _INDEX.read_text()
    return "<h1>FabSim API</h1><p>/docs 에서 API 문서를 보십시오.</p>"


def main() -> int:
    import uvicorn
    import os
    uvicorn.run(app, host=os.environ.get("FABSIM_HOST", "0.0.0.0"),
                port=int(os.environ.get("FABSIM_PORT", 8080)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
