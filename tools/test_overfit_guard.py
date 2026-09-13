"""과적합 감시기를 감시한다 — 위반을 주입했을 때 실제로 울리는가.

왜 필요한가
──────────
감시기는 "깨끗하다"를 너무 쉽게 보고한다. 규칙이 아무것도 잡지 못해도 결과는
똑같이 '정상'이기 때문이다. 그러면 **규칙을 무력화해 위반을 없애는 일**이
조용히 일어난다.

그래서 각 신호마다 그 신호가 잡아야 할 상황을 인위적으로 만들어 넣고,
등급이 실제로 내려가는지 확인한다. 안 울리면 그 규칙은 장식이다.
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = str(ROOT / ".venv" / "bin" / "python")
FAIL = []


def _say(ok, msg):
    print(f"  {'✅' if ok else '❌'} {msg}")
    if not ok:
        FAIL.append(msg)


def grades_in(pack_dir: Path):
    """주어진 팩 디렉토리로 감시기를 돌려 신호별 등급을 얻는다."""
    import json
    import os
    env = dict(os.environ)
    env["FABSIM_PACK_DIR"] = str(pack_dir)
    env["PYTHONWARNINGS"] = "ignore"
    r = subprocess.run([PY, str(ROOT / "tools" / "overfit_guard.py"), "--json"],
                       capture_output=True, text=True, env=env,
                       cwd=str(ROOT), timeout=600)
    if r.returncode not in (0, 1):
        raise RuntimeError(r.stderr[-300:])
    data = json.loads(r.stdout)
    return {s["code"]: s for s in data}


def main():
    print("기준선 — 현재 저장소 상태")
    tmp = Path(tempfile.mkdtemp(prefix="ofg_base_"))
    base_dir = tmp / "p"
    shutil.copytree(ROOT / "knowledge" / "params", base_dir)
    base = grades_in(base_dir)
    for c, s in sorted(base.items()):
        print(f"  [{c}] {s['value']} — {s['verdict']}")

    # ── G1: 자유 파라미터를 잔뜩 늘리면 자유도 예산이 나빠져야 한다 ──
    print()
    print("① [G1] 자유 파라미터를 주입하면 예산 등급이 내려가는가")
    t1 = Path(tempfile.mkdtemp(prefix="ofg_g1_"))
    d1 = t1 / "p"
    shutil.copytree(ROOT / "knowledge" / "params", d1)
    extra = "\n".join(
        f"  synthetic_{i}_exponent:\n    value: {0.1 * i:.2f}\n"
        f"    unit: \"-\"\n    source: \"과적합 감시기 시험용 주입값\"\n"
        f"    confidence: unverified"
        for i in range(30))
    p = d1 / "oxide_silica.yaml"
    p.write_text(p.read_text().rstrip() + "\n" + extra + "\n")
    g1 = grades_in(d1)
    worse = (g1["G1"]["value"] < base["G1"]["value"])
    _say(worse, f"자유파라미터 +30 → 예산 {base['G1']['value']} → {g1['G1']['value']}")
    _say(g1["G1"]["verdict"] == "risk",
         f"등급이 risk 로 내려갔다 (실제 {g1['G1']['verdict']})")

    # ── G3: 한 계에만 파라미터를 몰면 편중이 잡혀야 한다 ────────────
    print()
    print("② [G3] 특정 계에만 파라미터를 몰면 편중이 잡히는가")
    skew_before = base["G3"]["value"]
    skew_after = g1["G3"]["value"]
    _say(skew_after > skew_before,
         f"한 팩에만 주입 → 편중 {skew_before} → {skew_after}")
    _say(g1["G3"]["verdict"] == "risk",
         f"편중 등급이 risk (실제 {g1['G3']['verdict']})")

    # ── G5: 근거 없는 값을 늘리면 약한 근거 비율이 올라야 한다 ──────
    print()
    print("③ [G5] 근거 없는 값을 늘리면 약한 근거 비율이 오르는가")
    _say(g1["G5"]["value"] > base["G5"]["value"],
         f"unverified +30 → 약한근거 {base['G5']['value']} → {g1['G5']['value']}")

    # ── G2: 지수 유도를 끊으면 유도 비율이 떨어져야 한다 ────────────
    print()
    print("④ [G2] 지수 유도를 끊으면 유도 비율이 떨어지는가")
    t2 = Path(tempfile.mkdtemp(prefix="ofg_g2_"))
    d2 = t2 / "p"
    shutil.copytree(ROOT / "knowledge" / "params", d2)
    # 레짐 판정의 입력을 제거하면 유도가 불가능해진다
    b = d2 / "base.yaml"
    txt = b.read_text().replace("asperity_height_distribution:",
                                "disabled_asperity_height_distribution:")
    txt = txt.replace("real_contact_area_ratio:",
                      "disabled_real_contact_area_ratio:")
    b.write_text(txt)
    g2 = grades_in(d2)
    _say(g2["G2"]["value"] < base["G2"]["value"],
         f"판정 입력 제거 → 유도비율 {base['G2']['value']} → {g2['G2']['value']}")
    _say(g2["G2"]["verdict"] in ("watch", "risk"),
         f"유도 비율 등급이 내려갔다 (실제 {g2['G2']['verdict']})")

    for d in (tmp, t1, t2):
        shutil.rmtree(d, ignore_errors=True)

    print()
    print("=" * 70)
    if FAIL:
        print(f"❌ 감시기가 못 잡은 것 {len(FAIL)}건:")
        for f in FAIL:
            print(f"   · {f}")
        sys.exit(1)
    print("✅ 주입한 과적합 신호를 감시기가 전부 검출했다")


if __name__ == "__main__":
    main()
