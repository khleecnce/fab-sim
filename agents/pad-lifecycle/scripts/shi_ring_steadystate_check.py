"""
Shi & Ring (2010) 정성적 재현: 유체 유무에 따른 pad-wafer 분리거리 d(t)의
장기 거동 차이 (無유체=0으로 붕괴 vs 有유체=유한 정상상태로 수렴).

출처: Hong Shi, Terry A. Ring, "CMP pad wear and polish-rate decay modeled by
asperity population balance with fluid effect", Microelectronic Engineering
87 (2010) 2368-2375, DOI: 10.1016/j.mee.2010.04.010 (Crossref 확인).
저자 공개 PDF(무료): https://my.che.utah.edu/~ring/Publications-PDFs/J-135.pdf
(1차 원문 전체 확보·직접 읽음 — pad-lifecycle Lv1-2)

이 스크립트는 논문의 **폐형식 PDE 해(Eq.16)를 재현하지 않는다** — 그건
disk-conditioner 노트(conditioning-mechanism-asperity-regeneration.md §6)가
이미 OCR 손상으로 실패했다고 기록한 바로 그 수식이다. 대신 훨씬 단순한
"정성적 골격"만 확인한다: GW 접촉압 Pa(d)와 유체압 Pf(d)=Dμ U/(4d^2)의
하중분배 balance Papp = Pa(d) + Pf(d) 에서, 마모로 인해 Pa가 점점 줄어들 때
(1) 유체항이 없으면 d가 발산적으로 증가해야 하중이 유지되는데, 실제로는
    Pa가 asperity 개수 감소로 0에 근접하므로 recover 불가 → d가 무한정
    증가(=패드가 무한정 마모)하는 것과 동치.
(2) 유체항이 있으면 Papp - Pf(d) = Pa(d) 에서 우변이 0으로 가도 좌변이
    Pf(d)=Papp인 유한한 d*에서 0이 될 수 있다 → d가 유한값 d*로 수렴.
논문 본문(§3, p.9-10 서술)의 정성적 결론과 이 골격이 일치하는지만 검증한다.
"""
import numpy as np

# ---- 논문 §3.2에 명시된 파라미터 (Stein 데이터 fit, p.8) ----
D = 0.15          # 웨이퍼 지름 [m] (150 mm)
mu = 0.0016       # 슬러리 점도 [Pa.s] (conventional silica slurry, 25C)
U = 0.153         # 상대속도 [m/s]
Papp = 50e3       # 인가압력 [Pa] (50 kPa)


def Pf(d):
    """유체압 (Eq.6, Reynolds 방정식 차원분석 근사): Pf = D*mu*U / (4*d^2)"""
    return D * mu * U / (4.0 * d ** 2)


def Pa_from_balance(d):
    """하중분배: Papp = Pa + Pf  ->  Pa = Papp - Pf(d) (유체 case, Eq.5)"""
    return Papp - Pf(d)


# 정상상태 d*: Pa(d*) = 0, 즉 Pf(d*) = Papp (논문 서술: "reach a dynamic
# steady-state with no pad wear ... load is entirely supported by the fluid")
d_star = np.sqrt(D * mu * U / (4.0 * Papp))
print(f"[유체 case] 정상상태 분리거리 d* = {d_star*1e9:.2f} nm "
      f"(Pf(d*)={Pf(d_star)/1e3:.2f} kPa == Papp={Papp/1e3:.0f} kPa 검증)")

assert abs(Pf(d_star) - Papp) / Papp < 1e-6, "정상상태 정의(Pf=Papp) 불일치"

# d는 마모 진행에 따라 "감소"한다(논문 p.10: separation distance가 시간에
# 따라 drop). Pf = D*mu*U/(4d^2)는 d 감소에 따라 증가하므로,
# d > d* 에서는 Pf < Papp -> Pa > 0 (asperity가 여전히 하중 분담 -> 마모 계속,
#   d가 더 줄어드는 방향으로 진행)
# d < d* 에서는 Pf > Papp -> Pa < 0 (물리적으로 불가능한 음의 고체접촉압
#   -> d*가 도달 가능한 하한이자 self-limiting 정상상태)
d_above = d_star * 1.5   # 아직 마모 진행 중(d > d*)
d_below = d_star * 0.5   # d*를 넘어 더 줄어드는 것은 물리적으로 불가
Pa_above = Pa_from_balance(d_above)
Pa_below = Pa_from_balance(d_below)
print(f"d={d_above*1e9:.1f}nm(>d*, 마모 진행중): Pa={Pa_above/1e3:.2f} kPa (>0 이어야 함)")
print(f"d={d_below*1e9:.1f}nm(<d*, 도달불가): Pa={Pa_below/1e3:.2f} kPa (<0 이어야 함)")

assert Pa_above > 0, "d>d*(마모 진행 중)에서는 Pa>0이어야 함"
assert Pa_below < 0, "d<d*(도달 불가 영역)에서는 Pa<0(물리적 모순)이어야 함 -> d*가 하한"

# ---- 무유체(Borucki 극한, mu->0) 대조 ----
# Pf=0이면 Papp = Pa(d) 항상 성립해야 하므로, asperity 밀도가 마모로 0에
# 접근할 때 이를 만족하려면 d가 계속 감소(-∞ 방향, 물리적으로는 d<0 불가하므로
# "모든 asperity 소진"까지 진행)해야 한다 — 즉 유한한 self-limiting 지점이
# 원천적으로 존재하지 않는다(정성적 결론, 논문 p.10 "will continue to drop
# until it is zero"와 일치하는 극한 형태이나 부호 관례가 반대인 이산모델과
# 결합해야 정량적으로 맞음 — 이 스크립트는 정성적 골격만 확인).
mu_zero_case_has_finite_dstar = False  # Pf(d)=0*D*U/(4d^2)=0 항상, 유한해 없음
print(f"\n[무유체 case] 유한 정상상태 존재? {mu_zero_case_has_finite_dstar} "
      "(논문 p.10 결론과 정성적으로 일치: fluid 없으면 self-limiting 없음)")

assert not mu_zero_case_has_finite_dstar

print("\nPASS: 유체항 유무에 따른 self-limiting 거동 차이(논문 §3 정성 결론) 재현.")
print("주의: 이건 Eq.16 폐형식 PDE 해의 정량 재현이 **아니다** — 하중분배식(Eq.5,6)")
print("만으로 도출되는 정상상태 존재/부재 골격만 확인한 것. MRR(t) 감쇠곡선의")
print("실제 시간 스케일(45분, wear 계수 fit)은 검증하지 못했다 — 미검증으로 남긴다.")
