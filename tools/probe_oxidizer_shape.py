"""산화제 항이 단조 감소를 표현할 수 있는가 — 형태 한계를 실측한다.

현재 모델: f(C) = φ + (1-φ)·g(C),  g 는 Kaufman 단봉 (C_peak 에서 최대)
주장: 이 형태는 C_ref < C_peak 인 구간에서 **증가만** 가능하다.
      따라서 "농도를 올릴수록 MRR이 준다"는 계는 원리적으로 못 맞춘다.

검증: 팩 설정을 바꿔가며 f(C) 가 실제로 감소할 수 있는지 전수로 본다.
"""
import sys, pathlib, warnings
warnings.filterwarnings("ignore")
ROOT = pathlib.Path(__file__).resolve().parent.parent  # tools/ 의 부모 = 저장소 루트
sys.path.insert(0, str(ROOT))

from sim.chemistry import _oxidizer_term
from sim.params import load_pack, Param


def setval(pk, key, val):
    """런타임 덮어쓰기 — 탐침용. 근거는 '탐침'으로 남긴다."""
    pk.params[key] = Param(key=key, value=val, source="probe", confidence="estimated")
    return pk

pk = load_pack("cu_h2o2_bta")
print(f"cu_h2o2_bta: peak={pk.get('oxidizer_peak_wt_pct')} ref={pk.get('oxidizer_ref_wt_pct')} n={pk.get_or('oxidizer_curve_n',2.0)}")
print()

# 실제 특허 데이터 (US9200180): 농도 오를수록 MRR 감소
obs = [(1.0, 11.8), (2.5, 9.2), (5.0, 7.7)]
print("US9200180 구리 — 관측 vs 모델")
print(f"{'H2O2 wt%':>9} {'관측MRR':>8} {'관측비':>7} {'모델배수':>8}")
base_obs = obs[0][1]
for C, mrr in obs:
    p2 = load_pack("cu_h2o2_bta")
    setval(p2, "oxidizer_wt_pct", C)
    notes = []
    v = _oxidizer_term(p2, notes)
    print(f"{C:9.2f} {mrr:8.1f} {mrr/base_obs:7.3f} {v if v is None else f'{v:8.3f}'}")

print()
print("→ 관측은 1.000 → 0.780 → 0.653 (감소)")
print("  모델이 증가 방향이면 부호가 반대이고, 순위상관은 -1.0 이 된다.")
print()

# 형태 한계: peak 를 아무리 움직여도 감소를 만들 수 있나?
print("=== 형태 한계 전수 탐색 ===")
print("peak 를 바꿔가며 C=1→5 구간에서 모델이 감소하는지 확인")
found = []
for peak in [0.5, 1.0, 2.0, 3.0, 5.0, 8.0, 12.0]:
    vals = []
    for C in (1.0, 2.5, 5.0):
        p2 = load_pack("cu_h2o2_bta")
        setval(p2, "oxidizer_peak_wt_pct", peak)
        setval(p2, "oxidizer_wt_pct", C)
        notes = []
        v = _oxidizer_term(p2, notes)
        vals.append(v)
    if all(v is not None for v in vals):
        mono_dec = vals[0] > vals[1] > vals[2]
        tag = "✅ 감소" if mono_dec else "  증가/비단조"
        print(f"  peak={peak:5.1f} → {vals[0]:.3f} {vals[1]:.3f} {vals[2]:.3f}  {tag}")
        if mono_dec:
            found.append(peak)

print()
if found:
    print(f"감소를 만드는 peak 값이 있다: {found}")
    print("→ 단, 그 peak 는 '물리적으로 그 농도에서 최대'라는 뜻이어야 한다.")
    print("  데이터를 맞추려고 peak 를 고르면 그것은 회귀이지 모델이 아니다.")
else:
    print("❌ 어떤 peak 로도 단조 감소를 못 만든다 — 형태 자체가 부족하다.")
