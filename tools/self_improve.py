#!/usr/bin/env python3
"""제품 자가 개선 루프 — 감사 → 수정 대상 선정 → 검증까지 한 명령.

사용자 지시(2026-09-11): "이런 부분 너 스스로 개선하고 고쳐서 시뮬레이터까지
수정하고 나한테 보고할수는 없어? 루프돌리듯이 최선의 결과 완성을 향해서."

이 스크립트는 **고치지 않는다** — 고치는 것은 크론(또는 사람)이다. 이것이 하는 일은
"지금 무엇이 가장 잘못됐는가"를 매번 같은 기준으로 답하고, 고친 뒤에 그것이
정말 닫혔는지 기계로 확인하는 것이다. 판단은 도구가, 수정은 에이전트가 한다.

    tools/self_improve.py            # 진단: 다음에 뭘 고쳐야 하나
    tools/self_improve.py --verify   # 수정 후: 정말 좋아졌나 (게이트, exit 1 가능)

왜 나눠 놓았나: 감사기만 있으면 "고치기 전"만 보고, 테스트만 있으면 "무엇을 고칠지"를
모른다. 루프가 돌려면 둘 다 필요하고, 순서가 고정돼야 한다.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = str(ROOT / ".venv" / "bin" / "python")


def run(args, timeout=600):
    r = subprocess.run(args, capture_output=True, text=True, cwd=str(ROOT), timeout=timeout)
    return r.returncode, r.stdout, r.stderr


def diagnose() -> int:
    """다음에 고칠 것 하나를 고른다. 순서는 사람 취향이 아니라 고정 규칙이다."""
    print("═" * 62)
    print(" 제품 자가 개선 — 진단")
    print("═" * 62)

    # 1) UX 감사 (사용자가 매일 보는 화면의 정직성)
    code, out, _ = run([PY, str(ROOT / "tools" / "ux_audit.py"), "--json"])
    findings = json.loads(out) if out.strip().startswith("[") else []
    errs = [f for f in findings if f["severity"] == "error"]
    warns = [f for f in findings if f["severity"] == "warn"]

    print(f"\n[1] UX 감사 — 심각 {len(errs)} · 경고 {len(warns)} · 정보 "
          f"{len(findings)-len(errs)-len(warns)}")

    if errs:
        f = errs[0]
        print(f"\n  ▶ 이번 회차 작업: [{f['rule']}] {f['title']}")
        print(f"     위치: {f['where']}")
        print(f"     조치: {f['fix']}")
        print("\n  심각 위반은 물리 작업보다 우선합니다 — 사용자가 매일 쓰는 화면의")
        print("  거짓말이 미완 팩터 한 칸보다 급합니다.")
        return 0

    # 2) 심각이 없으면 물리/완성 격자
    print("     심각 위반 없음 → 모델 완성 작업으로")
    code, out, _ = run([PY, str(ROOT / "tools" / "completion.py"), "check"], timeout=900)
    head = [l for l in out.splitlines() if "완성 판정" in l]
    print(f"\n[2] 완성 격자 — {head[0] if head else '판정 실패'}")

    code, out, _ = run([PY, str(ROOT / "tools" / "blockers.py")], timeout=900)
    lines = [l for l in out.splitlines() if l.strip()][:8]
    print("\n[3] 병목 (파라미터 키 단위 — 키 하나가 여러 칸을 잡는다)")
    for l in lines:
        print(f"     {l}")

    if warns:
        f = warns[0]
        print(f"\n[4] UX 경고 1건 (심각이 0이므로 여유 있을 때): [{f['rule']}] {f['title']}")

    return 0


def verify() -> int:
    """수정 후 게이트. 하나라도 깨지면 커밋하지 마라."""
    print("═" * 62)
    print(" 제품 자가 개선 — 검증 게이트")
    print("═" * 62)
    bad = 0

    steps = [
        ("UX 감사 (심각 0건)", [PY, str(ROOT / "tools" / "ux_audit.py")], 600),
        ("감사 규칙 자체 검증", [PY, str(ROOT / "tools" / "test_ux_audit.py")], 600),
        ("단위·계약 테스트", [PY, "-m", "pytest", "-q"], 900),
    ]
    for label, cmd, to in steps:
        try:
            code, out, err = run(cmd, timeout=to)
        except subprocess.TimeoutExpired:
            print(f"  FAIL {label} — 타임아웃")
            bad += 1
            continue
        mark = "OK  " if code == 0 else "FAIL"
        tail = [l for l in out.strip().splitlines() if l.strip()][-1:] or [""]
        print(f"  {mark} {label}: {tail[0][:70]}")
        if code != 0:
            bad += 1

    # 3D/UI 검증은 서버가 떠 있을 때만
    try:
        import urllib.request
        urllib.request.urlopen("http://127.0.0.1:8848/api/health", timeout=3)
        alive = True
    except Exception:
        alive = False

    if alive:
        for label, script in [
            ("3D 스테이션 렌더", "test_stations_3d.py"),
            ("팩 선택 UI", "test_pack_select_ui.py"),
        ]:
            p = ROOT / "tools" / script
            if not p.exists():
                continue
            code, out, _ = run([PY, str(p)], timeout=600)
            mark = "OK  " if code == 0 else "FAIL"
            tail = [l for l in out.strip().splitlines() if l.strip()][-1:] or [""]
            print(f"  {mark} {label}: {tail[0][:70]}")
            if code != 0:
                bad += 1
    else:
        print("  ⚠    3D/UI 검증 건너뜀 — 8848 서버가 없습니다")
        print("       (UI를 만졌다면 서버를 띄우고 다시 돌리십시오)")

    print(f"\n{'✅ 통과 — 커밋해도 됩니다' if bad == 0 else f'❌ {bad}건 실패 — 커밋 금지'}")
    return 1 if bad else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--verify", action="store_true", help="수정 후 게이트로 실행")
    a = ap.parse_args()
    return verify() if a.verify else diagnose()


if __name__ == "__main__":
    sys.exit(main())
