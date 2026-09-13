"""등급 상한 감사기를 감사한다 — 며칠 정체시킨 그 결함을 다시 잡는가.

배경
────
완성 격자가 며칠 12칸에 멈춰 있었다. 원인은 문헌 부족이 아니라 코드에 박힌
등급 리터럴이었다:

    f.confidence = _worst_conf(_pack_conf(pk, ...), "estimated")

파라미터가 전부 literature 여도 결과가 estimated 로 눌려, **문헌을 아무리
확보해도 칸이 오르지 않았다.** 그런데 겉보기로는 "근거 부족"이라 다음 회차가
또 문헌을 찾으러 갔다.

이 테스트는 그 결함을 인위로 되살려 감사기가 실제로 우는지 확인한다.
안 울면 같은 정체가 반복되고 아무도 모른다.
"""
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = str(ROOT / ".venv" / "bin" / "python")
SRC = ROOT / "sim" / "factors.py"
FAIL = []


def _say(ok, msg):
    print(f"  {'✅' if ok else '❌'} {msg}")
    if not ok:
        FAIL.append(msg)


def run_audit(repo: Path):
    """주어진 저장소 사본에서 감사기를 돌려 JSON 을 받는다."""
    import json
    import os
    env = dict(os.environ)
    env["PYTHONWARNINGS"] = "ignore"
    r = subprocess.run(
        [PY, str(repo / "tools" / "confidence_cap_audit.py"), "--json"],
        capture_output=True, text=True, env=env, cwd=str(repo), timeout=600)
    if r.returncode not in (0, 1):
        raise RuntimeError(r.stderr[-400:])
    return json.loads(r.stdout)


def make_copy() -> Path:
    """저장소의 최소 사본 — 원본은 절대 건드리지 않는다."""
    tmp = Path(tempfile.mkdtemp(prefix="capaudit_"))
    for d in ("sim", "tools", "knowledge"):
        shutil.copytree(ROOT / d, tmp / d)
    return tmp


def main():
    print("기준선 — 현재 저장소")
    base_repo = make_copy()
    base = run_audit(base_repo)
    n_unj = len(base.get("unjustified_caps") or [])
    n_pressed = len(base.get("pressed") or [])
    print(f"  근거 없는 하한 {n_unj}곳 · 눌린 칸 {n_pressed}개")
    _say(n_unj == 0, "현재는 근거 없는 하한이 없다")

    # ── ① 근거 없는 리터럴 하한을 되살린다 ─────────────────────────
    print()
    print("① 근거 없는 등급 하한을 주입하면 감사기가 잡는가")
    r1 = make_copy()
    p = r1 / "sim" / "factors.py"
    t = p.read_text()
    # χ 의 등급 계산을 옛 형태(리터럴 하한)로 되돌린다
    pat = re.compile(
        r'f\.confidence = _worst_conf\(\s*\n\s*_pack_conf\(pk, "oxidizer_wt_pct", '
        r'"slurry_ph", "ce3_fraction"\),\s*\n\s*_pack_conf\([^)]*\)\)', re.M)
    t2, n = pat.subn(
        'f.confidence = _worst_conf(\n'
        '        _pack_conf(pk, "oxidizer_wt_pct", "slurry_ph", "ce3_fraction"),\n'
        '        "estimated")', t)
    if n == 0:
        _say(False, "주입 실패 — χ 등급 계산부를 못 찾았다(테스트 갱신 필요)")
    else:
        # 주입 지점 주변의 근거 주석도 지워 '근거 없는 하한' 상태를 만든다
        t2 = t2.replace(
            "# 등급 하한 판정 (2026-09-13): κ 와 같은 규칙 — 화학 항의 형상 파라미터도\n"
            "    # 팩에 등급과 함께 선언돼 있으므로 리터럴 대신 그것을 읽는다.\n    ", "")
        p.write_text(t2)
        got = run_audit(r1)
        u = len(got.get("unjustified_caps") or [])
        pr = len(got.get("pressed") or [])
        _say(u > n_unj, f"근거 없는 하한 {n_unj} → {u}곳 (검출)")
        _say(pr > n_pressed, f"눌린 칸 {n_pressed} → {pr}개 (증가 감지)")

    # ── ② 하한은 두되 근거 주석만 지운다 ───────────────────────────
    print()
    print("② 하한이 정당해도 근거를 안 적으면 잡는가")
    r2 = make_copy()
    p2 = r2 / "sim" / "factors.py"
    t3 = p2.read_text()
    # Γ 의 정당한 하한에서 근거 주석만 제거
    before = t3
    t3 = re.sub(r"    # 등급 하한 판정 \(2026-09-13\) — 이 하한은 \*\*정당하다\*\*.*?\n"
                r"(?=    f\.confidence = _worst_conf\(_pack_conf\(pk, \*have)",
                "", t3, flags=re.S)
    if t3 == before:
        _say(False, "주입 실패 — Γ 근거 주석을 못 찾았다")
    else:
        p2.write_text(t3)
        got2 = run_audit(r2)
        u2 = len(got2.get("unjustified_caps") or [])
        _say(u2 > n_unj,
             f"주석만 지워도 근거 없는 하한 {n_unj} → {u2}곳 (검출)")

    for d in (base_repo, r1, r2):
        shutil.rmtree(d, ignore_errors=True)

    print()
    print("=" * 68)
    if FAIL:
        print(f"❌ 감사기가 못 잡은 것 {len(FAIL)}건:")
        for f in FAIL:
            print(f"   · {f}")
        sys.exit(1)
    print("✅ 격자를 며칠 막았던 결함 유형을 감사기가 전부 검출한다")


if __name__ == "__main__":
    main()
