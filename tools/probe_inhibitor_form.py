"""억제제 항의 형태가 부족한가, 계수가 틀린가 — 전수 탐색으로 가른다.

왜 이 구분이 중요한가
────────────────────
계수가 틀린 것이면 문헌값을 찾아 넣으면 된다. 그런데 **형태가 부족한** 것이면
계수를 아무리 잘 골라도 못 맞춘다 — 그때 억지로 맞추려 보정항을 넣으면
시뮬레이터가 아니라 회귀식이 된다.

가르는 법: 자유 계수를 **전 범위 탐색**해서, 그 어떤 값으로도 관측 비를
재현할 수 없음을 보인다. 못 하면 형태 문제다(구조적 반증).

현재 형태
─────────
    잔여율(C) = exp(-k · θ(C)),   θ(C) = K·C/(1+K·C)   (Langmuir 단분자층)
    ψ = 잔여율(C) / 잔여율(C_ref)

관측 (Lee 2021, 니코틴산)
    0 mM → 19.196,  30 mM → 8.266,  50 mM → 5.246
    즉 0/30 = 2.322,  30/50 = 1.576

핵심 검정: 30→50 mM 구간에서 실측은 1.576배 줄어드는데, Langmuir 는
θ 가 이미 0.999 로 포화해 어떤 k 로도 1.00x 밖에 못 만든다.
"""
import sys
import pathlib
import math
import warnings

warnings.filterwarnings("ignore")
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import numpy as np                                    # noqa: E402

OBS = {0.0: 19.196, 30.0: 8.266, 50.0: 5.246}
R_0_30 = OBS[0.0] / OBS[30.0]     # 2.322
R_30_50 = OBS[30.0] / OBS[50.0]   # 1.576


def theta(C_mM, K):
    C = C_mM * 1e-3
    return K * C / (1.0 + K * C)


def psi_rel(C_mM, K, k, Cref_mM):
    return math.exp(-k * theta(C_mM, K)) / math.exp(-k * theta(Cref_mM, K))


print("=" * 76)
print("검정 — 어떤 (K, k) 조합으로도 관측 비를 재현할 수 있는가")
print("=" * 76)
print(f"  목표: 0/30 = {R_0_30:.3f},  30/50 = {R_30_50:.3f}")
print()

best = None
K_grid = np.logspace(0, 7, 200)       # 1 ~ 10^7 L/mol (7자릿수)
k_grid = np.linspace(0.05, 50.0, 400)  # 형상 계수

for K in K_grid:
    for k in k_grid:
        try:
            a = psi_rel(0.0, K, k, 1.0) / psi_rel(30.0, K, k, 1.0)
            b = psi_rel(30.0, K, k, 1.0) / psi_rel(50.0, K, k, 1.0)
        except (OverflowError, ValueError):
            continue
        if not (math.isfinite(a) and math.isfinite(b)):
            continue
        err = (math.log(a / R_0_30)) ** 2 + (math.log(b / R_30_50)) ** 2
        if best is None or err < best[0]:
            best = (err, K, k, a, b)

err, K, k, a, b = best
print(f"  전수 탐색 최적: K = {K:.4g} L/mol,  k = {k:.4g}")
print(f"     0/30 : 모델 {a:.4f}  vs  실측 {R_0_30:.4f}   "
      f"({(a/R_0_30-1)*100:+.1f}%)")
print(f"     30/50: 모델 {b:.4f}  vs  실측 {R_30_50:.4f}   "
      f"({(b/R_30_50-1)*100:+.1f}%)")

print()
print("  30/50 비의 **구조적 상한**을 따로 본다:")
print("  (Langmuir 는 θ 가 포화하므로 고농도 구간에서 비가 1 에 수렴한다)")
top = 0.0
arg = None
for K in K_grid:
    for k in k_grid:
        try:
            bb = psi_rel(30.0, K, k, 1.0) / psi_rel(50.0, K, k, 1.0)
        except (OverflowError, ValueError):
            continue
        if math.isfinite(bb) and bb > top:
            top, arg = bb, (K, k)
print(f"    전 범위에서 가능한 최대 30/50 비 = {top:.4f}  (K={arg[0]:.3g}, k={arg[1]:.3g})")
print(f"    실측 요구치                      = {R_30_50:.4f}")
if top < R_30_50:
    print()
    print("  ❌ **구조적 반증** — Langmuir 단분자층 형태로는 관측을 재현할 수 없다.")
    print("     계수를 어떻게 고르든 30→50 mM 구간의 감소를 만들지 못한다.")
    print("     계수 문제가 아니라 **형태 문제**다.")
else:
    print("  ✅ 형태로는 가능 — 계수 탐색 문제다.")

print()
print("=" * 76)
print("무엇이 부족한가 — 포화 이후에도 억제가 세지려면")
print("=" * 76)
print("""
  Langmuir 는 '표면 자리가 한정되어 있고 한 층만 덮인다'는 가정이다.
  그 가정에서는 자리가 다 차면 더 넣어도 변화가 없다 — 관측과 모순이다.

  포화 이후에도 억제가 세지는 경로는 물리적으로 몇 가지가 있다:
    · 다층 흡착        — 첫 층 위에 더 쌓인다 (BET 계열)
    · 흡착종 간 상호작용 — 덮일수록 결합이 강해지거나 약해진다 (Frumkin)
    · 막 치밀화/중합    — 같은 피복률에서도 막이 두꺼워지거나 촘촘해진다
    · 재생 속도        — 벗겨진 자리가 더 빨리 다시 덮인다

  어느 것인지는 이 데이터(3점)로 가를 수 없다.
  → 문헌이 어느 메커니즘을 지지하는지 확인한 뒤에 형태를 고른다.
    지금 임의로 항을 하나 더 붙이면 그것은 보정항이다.
""")
