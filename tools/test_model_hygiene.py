"""model_hygiene.py 의 검사가 실제로 결함을 잡는지 확인한다.

감사기는 "지금 깨끗하다"를 너무 쉽게 보고한다 — 규칙이 아무것도 안 잡아도 그렇다.
그래서 결함을 인위로 주입해 그때 울리는지 확인한다. 원본은 건드리지 않는다.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path("/Users/khleecnce/fab-sim")
PY = str(ROOT / ".venv" / "bin" / "python")


def run(pack_dir: Path, extra_env=None) -> str:
    env = dict(os.environ)
    env["FABSIM_PACK_DIR"] = str(pack_dir)
    if extra_env:
        env.update(extra_env)
    r = subprocess.run([PY, str(ROOT / "tools" / "model_hygiene.py"), "--json"],
                       capture_output=True, text=True, env=env, cwd=str(ROOT), timeout=600)
    return r.stdout


def clone() -> Path:
    d = Path(tempfile.mkdtemp(prefix="mh_test_"))
    shutil.copytree(ROOT / "knowledge" / "params", d / "params")
    return d


def set_unit(pack_dir: Path, pack: str, key: str, unit: str):
    f = pack_dir / f"{pack}.yaml"
    t = f.read_text()
    pat = re.compile(rf"^(  {re.escape(key)}:\n    value: [-\d.eE+]+\n)(    unit:.*\n)?", re.M)
    t = pat.sub(lambda m: m.group(1) + f'    unit: "{unit}"\n', t, count=1)
    f.write_text(t)


def set_value(pack_dir: Path, pack: str, key: str, val):
    f = pack_dir / f"{pack}.yaml"
    t = f.read_text()
    pat = re.compile(rf"^(\s+{re.escape(key)}:\s*\n\s+value:\s*)([-\d.eE+]+)", re.M)
    f.write_text(pat.sub(lambda m: f"{m.group(1)}{val!r}", t, count=1))


def main() -> int:
    print("=== model_hygiene 규칙이 실제 결함을 잡는지 ===\n")
    bad = 0

    # 0) 현재 상태는 깨끗해야 한다
    base = run(ROOT / "knowledge" / "params")
    clean = base.strip() in ("[]", "")
    print(f"  {'OK  ' if clean else 'FAIL'} 현재 저장소 위반 0건")
    bad += (not clean)

    # 1) 차원 불일치 — nm 키에 m 단위
    d = clone()
    set_unit(d / "params", "oxide_silica", "abrasive_size_nm", "m")
    out = run(d / "params")
    hit = "단위 불일치" in out and "abrasive_size_nm" in out
    print(f"  {'OK  ' if hit else 'FAIL'} [차원] nm 키에 m 단위를 넣으면 잡는다")
    bad += (not hit)
    shutil.rmtree(d, ignore_errors=True)

    # 2) 극한 — 입자 0 wt% 인데 MRR 이 1.0 (conc 항 미계상)
    #    factors.py 를 직접 못 고치므로, 기준 농도를 0 으로 만들어
    #    "기준 조건에서 배수 ≠ 1.0" 또는 극한 위반이 잡히는지 본다
    d = clone()
    set_value(d / "params", "oxide_silica", "abrasive_ref_wt_pct", 0.0)
    out = run(d / "params")
    hit = "[L]" in out or "극한" in out or "기준 조건" in out
    print(f"  {'OK  ' if hit else 'FAIL'} [극한] 기준 농도를 0 으로 깨면 잡는다")
    bad += (not hit)
    shutil.rmtree(d, ignore_errors=True)

    # 3) 무차원 키에 단위
    d = clone()
    set_unit(d / "params", "oxide_silica", "abrasive_conc_exponent", "nm")
    out = run(d / "params")
    hit = "무차원" in out
    print(f"  {'OK  ' if hit else 'FAIL'} [차원] 지수에 단위를 붙이면 잡는다")
    bad += (not hit)
    shutil.rmtree(d, ignore_errors=True)

    print(f"\n{'ALL PASS' if bad == 0 else str(bad) + ' FAILURE(S)'}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
