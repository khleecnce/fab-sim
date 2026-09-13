"""최적화 루프 — 새 데이터·새 리서치를 받아 모델을 개선하되, 외우지는 않게.

왜 루프여야 하는가
─────────────────
모델은 한 번 만들고 끝나는 물건이 아니다. 새 실측이 들어오고 새 문헌이 나오면
반영해야 한다. 그런데 "반영"에는 두 가지가 섞여 있고 겉보기로 구분되지 않는다:

    (a) 물리를 더 정확히 넣었다   → 본 적 없는 조건에서도 맞는다
    (b) 자유도를 늘려 맞췄다      → 맞춘 조건에서만 맞는다

지표만 보면 (b)가 (a)보다 좋아 보인다. 그래서 이 루프는 **지표와 건강도를 항상
함께** 재고, 지표가 올라도 건강도가 나빠졌으면 개선으로 인정하지 않는다.

한 회차가 묻는 것 (입력 → 판단 기준 → 출력)
──────────────────────────────────────────
1. 물리 위생   — 극한 거동·차원·식별 가능성에 위반이 있는가
2. 정확도      — 본 적 없는 조건에서 경향이 맞는가
3. 과적합 위험 — 자유도·유도비율·편중·일반화격차·근거등급
4. 판정        — 지표와 건강도를 **함께** 보고 개선/후퇴/보류를 정한다

판정 규칙 (물질명 없음)
──────────────────────
  · 물리 위반이 새로 생겼으면      → 다른 무엇이 좋아졌든 **후퇴**다
  · 지표가 올랐는데 자유도가 늘었으면 → 개선이 아니라 **의심**이다
  · 지표가 그대로인데 자유도가 줄었으면 → **개선**이다(같은 설명을 더 적은
    가정으로 한다는 뜻)
  · 일반화 격차가 벌어졌으면      → 맞춘 곳에서만 맞기 시작했다는 신호

기록
────
회차마다 상태를 JSON 한 줄로 남긴다. 그래야 "언제부터 나빠졌는가"를 되짚을 수
있고, 지표만 오르고 건강도가 꾸준히 나빠지는 장기 추세를 볼 수 있다.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
PY = str(ROOT / ".venv" / "bin" / "python")
LEDGER = ROOT / "validation" / "loop_ledger.jsonl"


def _run(cmd: List[str], timeout: int = 900) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True,
                          cwd=str(ROOT), timeout=timeout)


def physics_health() -> Dict[str, object]:
    """1. 물리 위생 — 극한·차원·식별."""
    r = _run([PY, str(ROOT / "tools" / "model_hygiene.py"), "--json"])
    if r.returncode not in (0, 1):
        return {"ok": False, "error": r.stderr[-200:]}
    try:
        issues = json.loads(r.stdout)
    except Exception:
        # JSON 모드가 없으면 텍스트에서 집계
        out = r.stdout
        return {"severe": out.count("🔴"),
                "total": out.count("🔴") + out.count("🟡")}
    if not isinstance(issues, list):
        return {"ok": False, "error": "예상과 다른 JSON 형태"}
    # ⚠ 키 이름을 추측하지 않는다. 예상한 키가 없으면 0 을 내는 대신 실패로
    #   신고한다 — 감시기가 조용히 '위반 없음'을 보고하는 것이 가장 나쁘다.
    sev_key = None
    for cand in ("severity", "level", "grade"):
        if issues and cand in issues[0]:
            sev_key = cand
            break
    if issues and sev_key is None:
        return {"ok": False,
                "error": f"심각도 키를 못 찾았다: {sorted(issues[0])}"}
    sev = sum(1 for i in issues
              if str(i.get(sev_key, "")).lower() in ("error", "severe", "risk"))
    return {"severe": sev, "total": len(issues)}


def accuracy() -> Dict[str, object]:
    """2. 정확도 — 본 적 없는 조건에서의 경향."""
    # --write: 회차마다 RESULTS.md 를 다시 쓴다. 손으로 쓴 값은 묵어도
    # 아무도 모르기 때문이다(실제로 8일 묵은 수치가 외부 검토를 오도했다).
    r = _run([PY, str(ROOT / "validation" / "backtest.py"), "--write"], timeout=1200)
    out = r.stdout
    res: Dict[str, object] = {}
    for line in out.splitlines():
        if "그중 **통계적으로 유의한 것만**" in line or "유의한 것만" in line:
            # "(7개, 총 74조건): ρ=+0.944, 쌍별 적중률 96.5%"
            try:
                res["significant_n"] = int(line.split("(")[1].split("개")[0])
                res["rho_significant"] = float(
                    line.split("ρ=")[1].split(",")[0])
                res["pairwise_pct"] = float(
                    line.split("적중률")[1].replace("%", "").strip())
            except Exception:
                pass
        elif "held-out" in line and "전체 평균" in line:
            try:
                res["rho_all"] = float(line.split("ρ=")[1].split(",")[0])
            except Exception:
                pass
    return res


def overfit() -> Dict[str, object]:
    """3. 과적합 위험."""
    r = _run([PY, str(ROOT / "tools" / "overfit_guard.py"), "--json"])
    if r.returncode not in (0, 1):
        return {"error": r.stderr[-200:]}
    try:
        sigs = json.loads(r.stdout)
    except Exception:
        return {"error": "파싱 실패"}
    out: Dict[str, object] = {}
    for s in sigs:
        out[s["code"]] = s["value"]
        out[s["code"] + "_verdict"] = s["verdict"]
    out["risk_count"] = sum(1 for s in sigs if s["verdict"] == "risk")
    out["watch_count"] = sum(1 for s in sigs if s["verdict"] == "watch")
    return out


def tests() -> Dict[str, object]:
    r = _run([PY, "-m", "pytest", "-q"], timeout=1200)
    tail = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
    passed = "passed" in tail and "failed" not in tail
    return {"passed": passed, "summary": tail[:120]}


def confidence_caps() -> Dict[str, object]:
    """근거 등급 상한 — 문헌이 아니라 코드가 칸을 막고 있는가.

    격자가 며칠 정체한 원인이 코드에 박힌 등급 리터럴이었다. 겉으로는 "근거
    부족"으로 보여 다음 회차가 또 문헌을 찾으러 갔다. 이 신호가 있으면 문헌
    조사보다 코드 정리가 먼저다.
    """
    r = _run([PY, str(ROOT / "tools" / "confidence_cap_audit.py"), "--json"])
    if r.returncode not in (0, 1):
        return {"ok": False, "error": r.stderr[-200:]}
    try:
        d = json.loads(r.stdout)
    except Exception:
        return {"ok": False, "error": "파싱 실패"}
    if not isinstance(d, dict) or "pressed" not in d:
        return {"ok": False, "error": "예상과 다른 JSON 형태"}
    return {
        "pressed": len(d.get("pressed") or []),
        "unjustified_caps": len(d.get("unjustified_caps") or []),
    }


def grid_cells() -> Dict[str, object]:
    """완성 격자 칸 수 — 정체 자체를 신호로 삼는다.

    며칠 같은 숫자에 멈춰 있었는데 아무도 그것을 '이상'으로 보고하지 않았다.
    회차마다 기록해 두면 '오르지 않음'이 판정 대상이 된다.
    """
    r = _run([PY, str(ROOT / "tools" / "completion.py"), "check"], timeout=900)
    m = re.search(r"격자\s+(\d+)/(\d+)칸", r.stdout)
    if not m:
        return {"ok": False, "error": "칸 수를 읽지 못했다"}
    return {"done": int(m.group(1)), "total": int(m.group(2))}


def snapshot() -> Dict[str, object]:
    print("  · 물리 위생 검사…")
    ph = physics_health()
    print("  · 회귀 테스트…")
    ts = tests()
    print("  · 근거 등급 상한 감사…")
    cc = confidence_caps()
    print("  · 완성 격자…")
    gc = grid_cells()
    print("  · 과적합 감시…")
    of = overfit()
    print("  · 정확도 백테스트…")
    ac = accuracy()
    return {
        "ts": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "commit": _run(["git", "rev-parse", "--short", "HEAD"]).stdout.strip(),
        "physics": ph, "tests": ts, "overfit": of, "accuracy": ac,
        "caps": cc, "grid": gc,
    }


def previous() -> Optional[Dict[str, object]]:
    if not LEDGER.exists():
        return None
    lines = [l for l in LEDGER.read_text().splitlines() if l.strip()]
    if not lines:
        return None
    try:
        return json.loads(lines[-1])
    except Exception:
        return None


def judge(cur: Dict[str, object], prev: Optional[Dict[str, object]]) -> List[str]:
    """지표와 건강도를 **함께** 보고 판정한다."""
    v: List[str] = []
    phys = cur.get("physics") or {}
    if isinstance(phys, dict) and phys.get("ok") is False:
        v.append(f"🔴 물리 위생 검사를 읽지 못했다 ({phys.get('error')}) — "
                 "검사 결과를 모르는 상태는 '위반 없음'이 아니다.")
    p_sev = int((phys or {}).get("severe", 0) or 0)  # type: ignore[union-attr]
    if p_sev:
        v.append(f"🔴 물리 위반 {p_sev}건 — 다른 지표가 좋아도 이것이 먼저다. "
                 "극한에서 틀린 모델은 범위 밖에서 반드시 틀린다.")

    if not (cur.get("tests") or {}).get("passed", False):  # type: ignore[union-attr]
        v.append("🔴 회귀 테스트 실패 — 과거에 확정한 사실이 깨졌다.")

    of = cur.get("overfit") or {}
    if int(of.get("risk_count", 0) or 0):  # type: ignore[union-attr]
        v.append(f"🔴 과적합 위험 신호 {of.get('risk_count')}건.")  # type: ignore[union-attr]

    # 근거 등급 상한 — 문헌이 아니라 코드가 칸을 막고 있는가
    caps = cur.get("caps") or {}
    if isinstance(caps, dict):
        if caps.get("ok") is False:
            v.append(f"🔴 등급 상한 감사를 읽지 못했다 ({caps.get('error')}).")
        elif int(caps.get("unjustified_caps", 0) or 0):
            v.append(
                f"🔴 근거 없는 등급 하한 {caps.get('unjustified_caps')}곳 — "
                "문헌을 채워도 칸이 오르지 않는 구조다. **문헌 조사보다 코드 정리가 "
                "먼저다.** 하한이 정당하면 '가장 약한 고리가 무엇인가'를 주석에 적고, "
                "적을 수 없으면 제거하라.")

    if prev is None:
        v.append("ℹ️ 첫 회차 — 비교 대상이 없다. 이 기록이 기준선이 된다.")
        return v

    def g(d, *keys) -> Optional[float]:
        """중첩 dict 에서 수치를 꺼낸다. 수치가 아니면 None."""
        cur_: object = d
        for k in keys:
            cur_ = cur_.get(k) if isinstance(cur_, dict) else None
        return float(cur_) if isinstance(cur_, (int, float)) else None

    rho_now = g(cur, "accuracy", "rho_significant")
    rho_old = g(prev, "accuracy", "rho_significant")
    dof_now = g(cur, "overfit", "G1")
    dof_old = g(prev, "overfit", "G1")
    gap_now = g(cur, "overfit", "G4")
    gap_old = g(prev, "overfit", "G4")

    if rho_now is not None and rho_old is not None:
        d = rho_now - rho_old
        if dof_now is not None and dof_old is not None:
            if d > 0.005 and dof_now < dof_old:
                v.append(
                    f"🟡 지표는 올랐으나(ρ {rho_old:+.3f}→{rho_now:+.3f}) "
                    f"자유도 예산이 나빠졌다({dof_old:.2f}→{dof_now:.2f}). "
                    "물리를 넣은 것인지 파라미터로 맞춘 것인지 확인하라.")
            elif abs(d) <= 0.005 and dof_now > dof_old:
                v.append(
                    f"✅ 같은 설명을 더 적은 가정으로 한다 — 지표 유지, "
                    f"자유도 예산 {dof_old:.2f}→{dof_now:.2f} 개선.")
            elif d > 0.005 and dof_now >= dof_old:
                v.append(
                    f"✅ 지표와 건강도가 함께 좋아졌다 "
                    f"(ρ {rho_old:+.3f}→{rho_now:+.3f}, 예산 {dof_now:.2f}).")
            elif d < -0.02:
                v.append(f"🟡 지표 하락 ρ {rho_old:+.3f}→{rho_now:+.3f} — "
                         "물리를 바로잡느라 내려간 것인지 확인하라. "
                         "정직한 하락은 후퇴가 아니다.")

    # ── 정체 감지 — '오르지 않음'을 판정 대상으로 만든다 ────────────────
    # 격자가 며칠 같은 숫자였는데 아무도 이상으로 보고하지 않았다. 지표가
    # 나빠지는 것만 잡고 '안 움직이는 것'을 놓치면, 막힌 구조를 영영 못 찾는다.
    g_now = g(cur, "grid", "done")
    g_old = g(prev, "grid", "done")
    if g_now is not None and g_old is not None:
        if g_now > g_old:
            v.append(f"✅ 완성 격자 {g_old:.0f} → {g_now:.0f}칸.")
        elif g_now == g_old:
            v.append(
                f"🟡 완성 격자가 {g_now:.0f}칸에서 움직이지 않았다. 연속 정체라면 "
                "남은 칸이 '근거 부족'인지 '구조가 막은 것'인지 먼저 가려라 — "
                "후자면 문헌을 더 찾아도 오르지 않는다 "
                "(tools/confidence_cap_audit.py).")
        else:
            v.append(f"🟡 완성 격자 하락 {g_old:.0f} → {g_now:.0f}칸 — "
                     "판정 기준이 엄격해진 것인지 회귀인지 확인하라.")

    if gap_now is not None and gap_old is not None and gap_now > gap_old + 0.05:
        v.append(f"🟡 일반화 격차가 벌어졌다({gap_old:.3f}→{gap_now:.3f}) — "
                 "맞춘 곳에서만 맞기 시작했다는 신호다.")

    if not v:
        v.append("✅ 물리·정확도·건강도 모두 유지 또는 개선.")
    return v


def main() -> int:
    ap = argparse.ArgumentParser(
        description="최적화 루프 — 지표와 건강도를 함께 재고 판정한다")
    ap.add_argument("--record", action="store_true", help="원장에 기록")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    t0 = time.time()
    print("=" * 74)
    print(" 최적화 루프 — 개선인가, 외운 것인가")
    print("=" * 74)
    cur = snapshot()
    prev = previous()
    verdicts = judge(cur, prev)
    cur["verdicts"] = verdicts

    if a.json:
        print(json.dumps(cur, ensure_ascii=False, indent=2))
    else:
        ph, ts, of, ac = (cur["physics"], cur["tests"],
                          cur["overfit"], cur["accuracy"])
        print()
        print(f"커밋 {cur['commit']} · {time.time()-t0:.0f}s")
        print(f"  물리 위반  : 심각 {ph.get('severe','?')}건")       # type: ignore[union-attr]
        print(f"  회귀 테스트: {ts.get('summary','?')}")             # type: ignore[union-attr]
        print(f"  정확도     : 유의 {ac.get('significant_n','?')}개 "  # type: ignore[union-attr]
              f"ρ={ac.get('rho_significant','?')} "                   # type: ignore[union-attr]
              f"쌍별 {ac.get('pairwise_pct','?')}%")                  # type: ignore[union-attr]
        cc, gc = cur.get("caps", {}), cur.get("grid", {})
        print(f"  완성 격자  : {gc.get('done','?')}/{gc.get('total','?')}칸")   # type: ignore[union-attr]
        print(f"  등급 상한  : 눌린 칸 {cc.get('pressed','?')} · "             # type: ignore[union-attr]
              f"근거없는 하한 {cc.get('unjustified_caps','?')}곳")              # type: ignore[union-attr]
        print(f"  자유도 예산: {of.get('G1','?')} · 유도비율 {of.get('G2','?')} · "  # type: ignore[union-attr]
              f"편중 {of.get('G3','?')} · 일반화격차 {of.get('G4','?')}")            # type: ignore[union-attr]
        print()
        print("판정:")
        for v in verdicts:
            print(f"  {v}")

    if a.record:
        LEDGER.parent.mkdir(parents=True, exist_ok=True)
        with LEDGER.open("a") as fh:
            fh.write(json.dumps(cur, ensure_ascii=False) + "\n")
        print(f"\n원장 기록: {LEDGER}")

    return 1 if any(v.startswith("🔴") for v in verdicts) else 0


if __name__ == "__main__":
    sys.exit(main())
