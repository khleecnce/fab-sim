"""새 슬러리를 **지수 없이** 넣을 수 있는가 — 절차의 실전 시험.

이 테스트가 묻는 것
──────────────────
"어떤 슬러리든 넣으면 모델식이 나오는가"가 목표였다. 그것을 확인하려면
저장소가 한 번도 본 적 없는 조성을 만들어 넣고, **사람이 지수를 하나도
적지 않은 채로** 결과가 나오는지 봐야 한다.

시험 대상은 특정 물질이 아니라 절차다. 그래서 조성 자체는 일반 변수로만
적는다 — 연마입자 크기·함량, 막질 경도, pH 같은 측정 가능한 값들.

합격 기준
─────────
1. 지수를 선언하지 않아도 팩이 로드되고 시뮬레이션이 돈다
2. 농도 지수가 **이론에서 유도**된다 (derived=True)
3. 기준 조건에서 MRR 배수가 정확히 1.0 (Kp 이중계상 없음)
4. 조성을 바꾸면 결과가 따라 변한다 (입력이 실제로 연결돼 있다)
5. 레짐이 바뀌면 지수가 따라 바뀐다 (고정 상수가 아니다)
"""
import os
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


# 저장소에 없는 조성. 값은 전부 측정 가능한 물리량이고,
# **지수는 하나도 적지 않는다.**
NEW_PACK = """
base: base
description: >
  절차 시험용 가상 조성. 저장소의 어떤 팩과도 다른 값을 쓴다.
  지수(abrasive_conc_exponent / abrasive_size_exponent)를 일부러 선언하지 않아
  이론이 그것을 유도해내는지 본다.

params:
  abrasive:
    value: test_abrasive
    unit: "-"
    source: "절차 시험 — 실제 물질 아님"
    confidence: unverified
  film:
    value: test_film
    unit: "-"
    source: "절차 시험 — 실제 물질 아님"
    confidence: unverified
  abrasive_wt_pct:
    value: 7.5
    unit: "wt%"
    source: "가상 조건"
    confidence: unverified
  abrasive_ref_wt_pct:
    value: 7.5
    unit: "wt%"
    source: "가상 조건 — 기준점을 본값과 일치시킨다"
    confidence: unverified
  abrasive_size_nm:
    value: 85.0
    unit: nm
    source: "가상 조건"
    confidence: unverified
  abrasive_ref_size_nm:
    value: 85.0
    unit: nm
    source: "가상 조건"
    confidence: unverified
  film_bulk_hardness_pa:
    value: 4.5e9
    unit: Pa
    source: "가상 조건 — 저장소의 어느 막질과도 다른 값"
    confidence: unverified
  kp_m_per_pa:
    value: 2.0e-13
    unit: "m/Pa"
    source: >
      가상 조건. Kp 는 이론이 유도하는 값이 아니라 **그 계의 기준 조건에서
      역산하는 축척**이다 — 새 슬러리를 넣을 때 사람이 주어야 하는 것은
      지수가 아니라 이 한 점이다. 절차가 요구하는 입력이 무엇인지 드러내려고
      일부러 남겨 둔다.
    confidence: unverified
"""


def run(pack_dir, pack, code):
    env = dict(os.environ)
    env["FABSIM_PACK_DIR"] = str(pack_dir)
    env["PYTHONWARNINGS"] = "ignore"
    r = subprocess.run([PY, "-c", code], capture_output=True, text=True,
                       env=env, cwd=str(ROOT), timeout=180)
    return r


def main():
    tmp = Path(tempfile.mkdtemp(prefix="newslurry_"))
    pdir = tmp / "packs"
    shutil.copytree(ROOT / "knowledge" / "params", pdir)
    (pdir / "novel_test.yaml").write_text(NEW_PACK)

    print("① 지수를 선언하지 않은 새 조성이 로드되고 돌아가는가")
    r = run(pdir, "novel_test", """
import json
from sim.engine import Recipe, simulate
rr = simulate(Recipe(pack="novel_test", pressure_psi=3.0))
m = 1.0
for k, f in rr.factors.items():
    if f.mrr_coupled and f.value is not None:
        m *= f.value
print(json.dumps({"mult": m, "mrr": float(sum(rr.mrr_nm_per_min)/len(rr.mrr_nm_per_min))}))
""")
    _say(r.returncode == 0, f"시뮬레이션 실행 (rc={r.returncode})")
    if r.returncode != 0:
        print("   " + (r.stderr.strip().splitlines() or ["?"])[-1][:160])
        shutil.rmtree(tmp, ignore_errors=True)
        return
    import json
    res = json.loads(r.stdout.strip().splitlines()[-1])
    print(f"     MRR = {res['mrr']:.2f} nm/min · 기준배수 = {res['mult']:.6f}")

    print()
    print("② 농도 지수가 이론에서 유도되는가 (사람이 안 적었는데)")
    r = run(pdir, "novel_test", """
import json
from sim.params import load_pack
from sim.regime_adapter import exponents_for
ex = exponents_for(load_pack("novel_test"), 3.0)
reg = ex["regime"]
print(json.dumps({"derived": ex["derived"], "n_conc": ex["n_conc"],
                  "chi": reg.chi, "alpha": reg.alpha, "conf": ex["confidence"],
                  "declared": load_pack("novel_test").has("abrasive_conc_exponent")}))
""")
    d = json.loads(r.stdout.strip().splitlines()[-1])
    _say(not d["declared"], "팩에 농도 지수가 선언되지 않았다 (전제 확인)")
    _say(bool(d["derived"]), f"지수가 유도됐다: n_C = {d['n_conc']:+.4f} "
                             f"(χ={d['chi']:.2f}, α={d['alpha']:.3f}, {d['conf']})")

    print()
    print("③ 기준 조건에서 배수가 정확히 1.0 인가 (Kp 이중계상 없음)")
    _say(abs(res["mult"] - 1.0) < 1e-6, f"기준배수 {res['mult']:.6f}")

    print()
    print("④ 조성을 바꾸면 결과가 따라 변하는가")
    r = run(pdir, "novel_test", """
import json
from sim.engine import Recipe, simulate
out = {}
for wt in (3.0, 7.5, 15.0):
    rr = simulate(Recipe(pack="novel_test", pressure_psi=3.0,
                         pack_overrides={"abrasive_wt_pct": wt}))
    out[str(wt)] = float(sum(rr.mrr_nm_per_min)/len(rr.mrr_nm_per_min))
print(json.dumps(out))
""")
    if r.returncode == 0:
        o = json.loads(r.stdout.strip().splitlines()[-1])
        vals = [o["3.0"], o["7.5"], o["15.0"]]
        mono = vals[0] < vals[1] < vals[2]
        _say(mono, f"농도 3→7.5→15 wt%: {vals[0]:.1f} → {vals[1]:.1f} → "
                   f"{vals[2]:.1f} nm/min (단조증가)")
        # 이론 지수와 실제 기울기가 맞는가
        import math
        slope = math.log(vals[2] / vals[0]) / math.log(15.0 / 3.0)
        _say(abs(slope - d["n_conc"]) < 0.02,
             f"실제 기울기 {slope:+.4f} = 유도 지수 {d['n_conc']:+.4f}")
    else:
        _say(False, f"조성 변경 실행 실패: {r.stderr.strip()[-120:]}")

    print()
    print("⑤ 레짐이 바뀌면 지수가 따라 바뀌는가 (고정 상수가 아님)")
    # 막질을 아주 무르게 → 접촉응력이 경도를 넘어 소성으로 전환되어야 한다
    soft = (pdir / "novel_test.yaml").read_text().replace(
        "value: 4.5e9", "value: 1.0e7")
    (pdir / "novel_soft.yaml").write_text(soft)
    r = run(pdir, "novel_soft", """
import json
from sim.params import load_pack
from sim.regime_adapter import exponents_for
ex = exponents_for(load_pack("novel_soft"), 3.0)
print(json.dumps({"n": ex["n_conc"], "alpha": ex["regime"].alpha,
                  "derived": ex["derived"]}))
""")
    if r.returncode == 0:
        s = json.loads(r.stdout.strip().splitlines()[-1])
        changed = s["alpha"] != d["alpha"]
        n_txt = "None" if s["n"] is None else f"{s['n']:+.3f}"
        _say(changed,
             f"경도를 450배 낮추니 α {d['alpha']:.3f} → {s['alpha']:.3f}, "
             f"n_C {d['n_conc']:+.3f} → {n_txt}")
    else:
        _say(False, "레짐 전환 시험 실패")

    shutil.rmtree(tmp, ignore_errors=True)

    print()
    print("=" * 68)
    if FAIL:
        print(f"❌ 실패 {len(FAIL)}건")
        for f in FAIL:
            print(f"   · {f}")
        sys.exit(1)
    print("✅ 새 슬러리가 지수 선언 없이 들어가고, 지수는 물성에서 유도된다")


if __name__ == "__main__":
    main()
