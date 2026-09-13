"""NPW 카탈로그 검증 — knowledge/wafers/npw_catalog.yaml

검사: yaml 파싱 / 모든 wafer에 stack·source·initial / stack[].pack 이 knowledge/params 에 실존 /
pack 없는 층은 pack_missing_reason 또는 stop / status 가 첫 층 팩 유무와 일치 /
catalog_ok 웨이퍼는 sim.timeline 으로 실제 돌아가는지(--run).
사용: .venv/bin/python tools/check_npw_catalog.py [--run]
"""
import os, sys
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


def main(run: bool = False) -> int:
    p = os.path.join(ROOT, "knowledge", "wafers", "npw_catalog.yaml")
    d = yaml.safe_load(open(p, encoding="utf-8"))
    packs = {f[:-5] for f in os.listdir(os.path.join(ROOT, "knowledge", "params")) if f.endswith(".yaml")}
    ws = d["wafers"]
    assert len(ws) >= 10, f"최소 10종 필요, 현재 {len(ws)}"
    ids = []
    for w in ws:
        for k in ("id", "label", "stack", "source", "initial", "purpose", "status"):
            assert k in w and w[k], (w.get("id"), k)
        assert w["id"] not in ids, f"중복 id {w['id']}"
        ids.append(w["id"])
        for L in w["stack"]:
            for k in ("layer", "thickness_nm", "pack", "stop"):
                assert k in L, (w["id"], L)
            if L["pack"] is None:
                assert L.get("pack_missing_reason") or L["stop"], (w["id"], L["layer"], "pack 없는데 이유 없음")
            else:
                assert L["pack"] in packs, (w["id"], L["layer"], f"팩 '{L['pack']}' 없음 — 있는 팩: {sorted(packs)}")
        for k in ("ttv_nm", "roughness", "bow_um"):
            assert k in w["initial"] and "source" in w["initial"][k], (w["id"], k, "source 없음")
        assert (w["status"] == "pack_missing") == (w["stack"][0]["pack"] is None), (w["id"], "status 불일치")
    print(f"catalog OK: {len(ws)}종 — {ids}")

    if run:
        from sim.timeline import Layer, run_timeline
        from sim.engine import Recipe
        for w in ws:
            if w["status"] != "catalog_ok" or w["id"] == "sic_4h_bulk":
                continue
            layers = [Layer(name=L["layer"], thickness_nm=float(L["thickness_nm"]),
                            pack=L["pack"], stop=bool(L["stop"])) for L in w["stack"]]
            res = run_timeline(layers, Recipe(pack=layers[0].pack, pressure_psi=3.0), total_s=240, dt_s=5)
            bt = {k: v for k, v in res.layer_breakthrough_s.items() if v is not None}
            print(f"  {w['id']:34s} endpoint={res.endpoint_s} breakthrough={bt} mean_mrr={res.frames[1].mean_mrr:.1f} nm/min")
    return 0


if __name__ == "__main__":
    sys.exit(main(run="--run" in sys.argv))
