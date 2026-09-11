#!/usr/bin/env python3
"""ux_audit.py 의 규칙이 **실제로 터졌던 결함을 잡는지** 검증한다.

왜 이 테스트가 필요한가:
  감사기는 "지금 깨끗하다"를 쉽게 보고한다 — 규칙이 아무것도 안 잡아도 그렇게 나온다.
  그래서 각 규칙마다 2026-09-11에 실제로 있었던 결함 상태를 인위로 재현해
  **그 규칙이 그때는 울렸는지** 확인한다. 울리지 않으면 그 규칙은 장식이다.

방법: 파일을 임시로 되돌린(결함 주입) 사본을 만들어 감사기를 그 위에서 돌린다.
원본은 건드리지 않는다.
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run_audit(root: Path) -> str:
    """주어진 저장소 사본에서 감사기를 돌려 JSON 을 돌려준다."""
    r = subprocess.run(
        [sys.executable, str(root / "tools" / "ux_audit.py"), "--json"],
        capture_output=True, text=True, cwd=str(root),
    )
    return r.stdout


def clone() -> Path:
    """감사에 필요한 파일만 임시 디렉토리로 복사 (전체 복사는 느리다)."""
    d = Path(tempfile.mkdtemp(prefix="uxaudit_"))
    for rel in ["tools/ux_audit.py", "sim/api.py", "sim/pack_meta.py",
                "sim/web/studio3d.html", "tools/serve_forever.sh"]:
        src = ROOT / rel
        if src.exists():
            (d / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, d / rel)
    (d / "sim" / "__init__.py").touch()
    # 팩 YAML 은 파일명만 필요
    (d / "knowledge" / "params").mkdir(parents=True, exist_ok=True)
    for p in (ROOT / "knowledge" / "params").glob("*.yaml"):
        (d / "knowledge" / "params" / p.name).write_text("params: {}\n")
    (d / "tools" / "test_sds_3d.py").write_text(
        (ROOT / "tools" / "test_sds_3d.py").read_text() if (ROOT / "tools" / "test_sds_3d.py").exists() else "")
    return d


CASES = []


def case(rule: str, desc: str):
    def deco(fn):
        CASES.append((rule, desc, fn))
        return fn
    return deco


@case("R1-internal-id", "팩 선택 목록에 내부 ID 노출 (2026-09-11 실제)")
def inject_r1(d: Path):
    p = d / "sim" / "web" / "studio3d.html"
    t = p.read_text()
    t = t.replace("<select id=\"sel-pack\">${opts}</select>",
                  "<select id=\"sel-pack\"><option>sic_ceria_h2o2 — SiC</option></select>")
    p.write_text(t)


@case("R2-no-geometry", "탭은 있는데 3D 실물이 없음 (SDS)")
def inject_r2(d: Path):
    p = d / "sim" / "web" / "studio3d.html"
    t = p.read_text()
    t = t.replace("hot.sds = nozzle;", "/* removed */")
    t = re.sub(r'STATION_PART\s*=\s*\{[^}]*\}', 'STATION_PART = { FI:"wafer" }', t)
    p.write_text(t)


@case("R3-cache", "/3d 에 캐시 금지 헤더 없음")
def inject_r3(d: Path):
    p = d / "sim" / "api.py"
    t = p.read_text()
    t = t.replace('"Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",', "")
    p.write_text(t)


@case("R4-canvas-fixed", "캔버스 고정 폭 → 폰에서 글자 축소")
def inject_r4(d: Path):
    p = d / "sim" / "web" / "studio3d.html"
    t = p.read_text()
    t = t.replace('<canvas id="cv-padsec" data-h="230">',
                  '<canvas id="cv-padsec" width="640" height="230">')
    p.write_text(t)


@case("R8-service-guard", "상시 서비스에 알림 상한 없음 → 폭주")
def inject_r8(d: Path):
    p = d / "tools" / "serve_forever.sh"
    t = p.read_text()
    t = t.replace("rate limit", "XXX")
    p.write_text(t)


@case("R9-meta-missing", "새 팩 추가 시 표시 메타 누락")
def inject_r9(d: Path):
    (d / "knowledge" / "params" / "poly_si_new.yaml").write_text("params: {}\n")


@case("R7-silent-dead", "엔진 미연결인데 dead 표시 없음")
def inject_r7(d: Path):
    p = d / "sim" / "web" / "studio3d.html"
    t = p.read_text()
    t = t.replace(
        '{k:"blend_tank_l", l:"Blend Tank Volume", u:"L", min:10, max:2000, step:10, pk:null,\n       dead:"Recorded only."}',
        '{k:"blend_tank_l", l:"Blend Tank Volume", u:"L", min:10, max:2000, step:10, pk:null}')
    p.write_text(t)


def main() -> int:
    print("=== 규칙이 과거 실제 결함을 잡는지 검증 ===\n")
    bad = 0

    # 0) 현재 상태에서 심각(error)이 0 이어야 한다
    cur = run_audit(ROOT)
    n_err = cur.count('"severity": "error"')
    print(f"  {'OK  ' if n_err == 0 else 'FAIL'} 현재 저장소 심각 위반 {n_err}건 (0이어야 함)")
    bad += (n_err != 0)

    # 1) 결함을 주입하면 해당 규칙이 울려야 한다
    for rule, desc, inject in CASES:
        d = clone()
        try:
            inject(d)
            out = run_audit(d)
            fired = rule in out
            print(f"  {'OK  ' if fired else 'FAIL'} [{rule}] {desc}")
            if not fired:
                bad += 1
        finally:
            shutil.rmtree(d, ignore_errors=True)

    print(f"\n{'ALL PASS' if bad == 0 else str(bad) + ' FAILURE(S)'}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
