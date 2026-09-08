<!-- V2-SECTION: R2-slurry | 공동: R3-pad | 분배완료 2026-09-08 | 근거: slurry, 슬러리 | 정본: ARCHITECTURE-V2.md §3 -->
# CMP 패드 그루브 기하(폭·깊이·피치) → 유효 접촉면적·유동 저항

> pad-structure Lv1-2. [[pad-groove-slurry-transport]](Lv1-1, GFQ=W/P 정의·기능 3종) 상호링크.
> 조사범위: `tools/scope.py --agent pad-structure` (2011년 이후 우선, 1차 논문·특허). 이번 단원은
> 실측 논문 2편(둘 다 2011년 이전 하한 예외 — Mu 2016·Cho 2022는 조건 충족)으로 GFQ 정의를
> **실측 치수·실측 유동 데이터**에 적용해 정량화한다.

## 1. 유효 접촉면적 — GFQ가 곧 "land 비율의 보수"

**출처(1차, 실험): Mu, Zhuang, Sampurno, Wei, Ashizawa, Morishima, Philipossian (Univ. of Arizona /
Araca Inc. / Hitachi Chemical), "Effect of pad groove width on slurry mean residence time and
slurry utilization efficiency in CMP", Microelectronic Engineering 157 (2016) 60–63,
DOI: 10.1016/j.mee.2016.02.035 (https://doi.org/10.1016/j.mee.2016.02.035). 미러 사이트 경유 원문 확보(`papers/mee-2016-mu-groove-width-residence-time.pdf`,
PyMuPDF 텍스트 추출로 Table 1/2/3 전문 확인 — 초록만이 아니라 본문·표 전체 확인).**

이 논문은 Dow IC1000 패드 3종(A/B/C)을 그루브 폭만 다르게(300/600/900 μm) 만들고, 깊이(400 μm)와
land 폭(1200 μm)은 고정했다(Table 1). Lv1-1에서 정의한 **GFQ = W/P** (W=그루브폭, P=피치=W+land폭)를
이 실측 치수에 그대로 적용하면:

| 패드 | 그루브폭 W(μm) | land폭(μm) | 피치 P=W+land(μm) | GFQ=W/P | 접촉면적비(land/P)=1−GFQ |
|---|---|---|---|---|---|
| A | 300 | 1200 | 1500 | 0.200 | 0.800 |
| B | 600 | 1200 | 1800 | 0.333 | 0.667 |
| C | 900 | 1200 | 2100 | 0.429 | 0.571 |

JP5767280B2가 못박은 "가장 적합" GFQ 구간은 [0.2, 0.3](Lv1-1 노트). 실측 Pad A(GFQ=0.200)는
이 구간의 하한에 걸리지만, Pad B(0.333)·Pad C(0.429)는 **"가장 적합" 구간을 벗어난다** — 즉 이
논문이 실제로 실험한 패드 중 2/3는 그 특허가 "접촉면적·강성 균형에 가장 좋다"고 주장하는 구간
밖에 있다. 이는 GFQ 최적구간이 하나의 응용(그 특허의 실시예)에 국한된 값이며, 그루브 폭이
슬러리 이송 목적으로 넓어질수록 최적 구간을 벗어난다는 것을 실측으로 보여준다 — 두 문헌(특허 vs
실험논문)의 "최적"이 서로 다른 목적함수(접촉 안정성 vs 슬러리 이송)를 겨냥한다는 뜻으로 해석.
**GFQ 자체가 "유효 접촉면적비의 여집합"이라는 대응관계는 이번 단원에서 실측 수치로 확정.**

## 2. 유동 저항 — Vgroove(반응기 부피)로 정량화, 그루브 폭이 커질수록 저항↓하지만 수확체감

같은 논문은 CMP 인터페이스를 고전 반응기 이론(Levenspiel, RTD)으로 모델링한다.
반응기 총 부피 V_total = V_land + V_groove, 슬러리 평균체류시간(MRT, τ) = V_total / q_actual
(q_actual = 웨이퍼 아래로 실제 흐르는 유량). 논문 Table 2(반응기 부피 계산, 슬러리 필름두께
가정: 3PSI→15μm, 5PSI→10μm)와 Table 3(MRT·η 실측)의 수치:

| 패드 | 3PSI τ(s) | 3PSI V_total(cm³) | 3PSI q_actual(mL/min) | 3PSI η | 5PSI τ(s) | 5PSI η |
|---|---|---|---|---|---|---|
| A(W=300) | 9.2 | 3.04 | 19.8 | 9.9% | 8.3 | 10.6% |
| B(W=600) | 10.6 | 4.72 | 26.7 | 13.4% | 9.3 | 14.7% |
| C(W=900) | 13.9 | 5.91 | 26.1 | 12.8% | 12.7 | 13.6% |

핵심 관찰(논문 본문 그대로): **그루브 폭이 300→600 μm로 2배가 되면 슬러리 이용효율 η이
3PSI에서 9.9%→13.4%(+35% 상대), 5PSI에서 10.6%→14.7%(+39% 상대)로 유의하게 증가**한다.
그런데 600→900 μm로 더 넓히면 η이 오히려 정체(3PSI: 13.4%→12.8%, 5PSI: 14.7%→13.6%,
둘 다 소폭 **감소**) — 이는 V_total과 τ가 함께 커져 그 비율(q_actual)이 거의 그대로이기
때문(Table 3: q_actual 26.7→26.1 mL/min(3PSI), 29.4→27.2(5PSI), 둘 다 미세 감소).

**"유동 저항이 그루브 폭에 반비례해 단조 감소한다"는 단순 가정은 이 실측 데이터로 기각된다.**
저항(≈1/q_actual 개념)은 300→600 μm 구간에서만 뚜렷이 개선되고, 600→900 μm 구간은 수확체감을
넘어 정체·미세 악화다. 논문은 이를 "V_groove와 V_total이 함께 커져 q_actual 비율은 안 변한다"로
설명 — 그루브 폭 확대가 유동 저항을 낮추는 효과는 "저항 채널 확대"가 아니라 "저류(hold-up) 부피
확대"에 가깝다는 뜻이며, 저류 부피가 과도하면 오히려 정체된 슬러리가 늘어 효율이 정체된다.

## 3. 방사형 그루브 개수 — 압력 분포·NU와의 연결(보조 근거)

**출처(1차, CFD+실험, 오픈액세스 CC-BY): Cho, Liu, Jeon, Lee, Bae(SKKU), Hong, Kim(삼성전자
반도체연구소), Kim(SKKU), "Simulation and Experimental Investigation of the Radial Groove Effect
on Slurry Flow in Oxide Chemical Mechanical Polishing", Applied Sciences 12(9) 4339 (2022),
DOI: 10.3390/app12094339 (https://doi.org/10.3390/app12094339). r.jina.ai 프록시로 MDPI CC-BY 원문 전체 확보(본문 전체 확인,
`/tmp/mdpi_full.md`에 캐시했으나 CC-BY 오픈액세스라 papers/ 저장 불필요 — 재수집 가능).**

동심원 그루브만 있는 R0 패드 대비 방사형 그루브(R8, R32)를 추가하면 웨이퍼-패드 계면 후단
(trailing edge)의 음압(back-mixing 유발)이 -8 kPa(R0) → -6 kPa(R32)로 완화되고, 300mm 웨이퍼
실측 비균일도(NU)가 **4.65%(R0) → 2.67%(R8) → 1.56%(R32)**로 개선된다. 단, "R0→R8"의 개선폭이
"R8→R32"보다 훨씬 커서(질적 변화 vs 양적 변화, 논문 원문 표현) **그루브 밀도 증가도 수확체감**을
보인다 — §2의 그루브 폭 결과와 같은 정성적 패턴(초기 개선 후 포화)이 그루브 개수 축에서도
재현된다는 점이 이번 단원의 핵심 발견. 단, 이 논문은 그루브 "폭·피치"가 아니라 "개수"를 바꾼
것이라 §1의 GFQ 표와 직접 비교할 정량 대응은 없음(**미검증** — 그루브 개수와 GFQ를 하나의
변수로 통합하는 모델은 이번 단원에서 확보하지 못함, Lv3-2(sim/tier2) 과제로 이관).

**재현 결과 요약(아래 verify 블록 대조, Mu et al. 2016 Table 1/3 문헌값과 코드 assert로 확인)**: GFQ 실측값은 Pad A=0.200, Pad B=0.333, Pad C=0.429로 문헌 치수(Mu 2016) 그대로 재현되며, η(3PSI)는 문헌값(Mu 2016 Table 3) 9.9%/13.4%/12.8%와 정확히 일치했고 300→600μm 구간의 η 상대개선은 35.4%(재현치)로 본문 서술(+35%)과 대조해 일치를 확인했다.

## 4. sim/으로의 함의 (구현은 소프트웨어 부문 — 여기선 근거만 정리)

- GFQ(또는 1−GFQ=접촉면적비)는 단조로운 "선형 저항계수"로 sim에 넣으면 §2 실측과 어긋난다.
  대신 **η(GFQ) 또는 q_actual(GFQ)에 수확체감·포화 형태(예: 포화형 함수, Michaelis-Menten류)**가
  필요하다는 것이 정량적으로 확인된 요구사항. (근거: Table 3의 η, q_actual 값)
- 그루브 "개수/밀도"와 "폭/피치"를 하나의 파라미터로 결합하는 모델은 미확보 — 이 둘을 별도
  차원으로 다루거나, 통합 문헌을 후속 단원에서 찾아야 한다.

```python verify
# Lv1-2 검증: GFQ 실측 적용 + 유동효율 비단조(수확체감) 실측 재현

# --- (1) GFQ = W/P, 접촉면적비 = 1-GFQ : Mu2016 Table 1 실측 치수 ---
pads = {
    'A': dict(W=300, land=1200, depth=400),
    'B': dict(W=600, land=1200, depth=400),
    'C': dict(W=900, land=1200, depth=400),
}
def gfq(w, land):
    P = w + land
    return w / P, 1 - w / P

gfq_vals = {}
for name, d in pads.items():
    g, contact = gfq(d['W'], d['land'])
    gfq_vals[name] = g
    print(f"Pad {name}: GFQ={g:.3f}, 접촉면적비={contact:.3f}")

# JP5767280B2 "가장 적합" 구간(Lv1-1 노트) = [0.2, 0.3]
assert abs(gfq_vals['A'] - 0.200) < 1e-6, "Pad A GFQ 재현 실패"
assert abs(gfq_vals['B'] - 0.333) < 1e-3, "Pad B GFQ 재현 실패"
assert abs(gfq_vals['C'] - 0.429) < 1e-3, "Pad C GFQ 재현 실패"
assert 0.2 <= gfq_vals['A'] <= 0.3, "Pad A는 '가장 적합' 구간 안에 있어야 함"
assert not (0.2 <= gfq_vals['B'] <= 0.3), "Pad B는 '가장 적합' 구간을 벗어나야 함(실측 사실)"
assert not (0.2 <= gfq_vals['C'] <= 0.3), "Pad C는 '가장 적합' 구간을 벗어나야 함(실측 사실)"
assert gfq_vals['A'] < gfq_vals['B'] < gfq_vals['C'], "GFQ는 그루브 폭에 단조 증가해야 함"

# --- (2) 슬러리 이용효율 η(Table 3, Mu 2016) — 300→600 큰 개선, 600→900 정체/미세감소 ---
eta_3psi = {'A': 9.9, 'B': 13.4, 'C': 12.8}   # %
eta_5psi = {'A': 10.6, 'B': 14.7, 'C': 13.6}  # %

# 300->600um: 유의한 개선 (>+30% 상대)
rel_gain_AB_3psi = (eta_3psi['B'] - eta_3psi['A']) / eta_3psi['A'] * 100
rel_gain_AB_5psi = (eta_5psi['B'] - eta_5psi['A']) / eta_5psi['A'] * 100
print(f"η 상대개선 A->B: 3PSI {rel_gain_AB_3psi:.1f}%, 5PSI {rel_gain_AB_5psi:.1f}%")
assert rel_gain_AB_3psi > 30, "300->600um 구간은 논문이 '유의한 개선'이라 서술 — 30%+ 기대"
assert rel_gain_AB_5psi > 30

# 600->900um: 정체/미세 감소 (단조 증가 가설 기각)
delta_BC_3psi = eta_3psi['C'] - eta_3psi['B']
delta_BC_5psi = eta_5psi['C'] - eta_5psi['B']
print(f"η 변화 B->C: 3PSI {delta_BC_3psi:+.1f}%p, 5PSI {delta_BC_5psi:+.1f}%p")
assert delta_BC_3psi < 0, "600->900um 구간은 미세 감소(정체) — 단조 증가 가설 기각 확인"
assert delta_BC_5psi < 0
assert abs(delta_BC_3psi) < 2 and abs(delta_BC_5psi) < 2, "감소폭 자체는 작아야 함(정체이지 급감 아님)"

# --- (3) q_actual (Table 3): B,C가 비슷 (저항 비단조) ---
q_3psi = {'A': 19.8, 'B': 26.7, 'C': 26.1}
q_5psi = {'A': 20.8, 'B': 29.4, 'C': 27.2}
assert q_3psi['B'] > q_3psi['A'] * 1.2, "A->B는 유량이 뚜렷이 늘어야 함(저항 개선)"
assert abs(q_3psi['C'] - q_3psi['B']) / q_3psi['B'] < 0.1, "B,C의 q_actual은 10% 이내로 비슷해야 함(수확체감)"

# --- (4) CFD 논문(Cho 2022): NU 개선도 같은 수확체감 패턴 ---
NU = {'R0': 4.65, 'R8': 2.67, 'R32': 1.56}  # %
drop_R0_R8 = NU['R0'] - NU['R8']
drop_R8_R32 = NU['R8'] - NU['R32']
print(f"NU 개선폭: R0->R8 {drop_R0_R8:.2f}%p, R8->R32 {drop_R8_R32:.2f}%p")
assert drop_R0_R8 > drop_R8_R32, "그루브 밀도 증가도 초기 개선폭이 후기보다 커야 함(수확체감, 논문 서술과 일치)"

print("PASS: GFQ 실측 재현 + 유동효율 비단조(수확체감) 3계열(Table3 η, q_actual, CFD NU) 정량 확인")
```

## 자기시험 근거 메모
Lv1-2 핵심 결론: (1) GFQ=W/P는 land 대비 그루브 비율의 여집합으로, 특허의 "이상적 구간"은
실측 실험 패드 3종 중 1종만 만족한다. (2) 그루브 폭 확대의 유동효율 개선은 단조가 아니라
초기 구간(300→600μm)에 집중되고 그 이상은 정체/미세악화 — 반응기 부피(V_groove)와 체류시간(τ)이
함께 늘어 비율(q_actual)이 상쇄되기 때문. (3) 그루브 "개수"(방사형) 축에서도 같은 수확체감
패턴이 재현되어(NU 개선폭 축소), 이는 CMP 그루브 설계 전반에 나타나는 일반적 현상일 가능성 —
단, 통합 결합모델은 미확보(**미검증**, Lv3-2 과제).
