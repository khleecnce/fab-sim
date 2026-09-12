# 쉘프라이프·희석·2액형 혼합 — 웨이퍼에 닿기 전에 이미 결정되는 LPC

> 에이전트: slurry-colloid Lv2-2 | 작성일: 2026-09-13
> 선행: [[pou-filtration-recirculation-pump-shear-lpc]] [[colloidal-destabilization-lpc-defect-mechanism]]
>       [[dlvo-ionic-strength-ph-aggregation-kinetics]]
> 관련: [[../cmp/colloid-zeta-dlvo-slurry-stability]] [[../cmp/lpc-scratch-density-tail-correlation]]

## 1. 이 노트가 채우는 자리

선행 노트 [[pou-filtration-recirculation-pump-shear-lpc]]는 슬러리 수지(收支)를 이렇게 썼다:

```
LPC(웨이퍼 도달) = LPC(제조 시) + [펌프 전단 생성항] − [필터 제거항]
```

그런데 "LPC(제조 시)"를 상수로 둔 것이 거짓이다. 실제 슬러리는 제조 후 **드럼/토트에 보관되고
(수주~수개월), POU에서 UPW로 희석되고, 산화제 등 제2액과 혼합된** 다음에야 순환 루프에
들어간다. 이 노트는 그 세 단계를 각각 생성항으로 열고, 마지막에 현장에서 그것을 **무엇으로
잡아낼 수 있는가(QC 항목)**를 다룬다:

```
LPC(루프 진입) = LPC(제조 시) + [보관 시계 항] + [희석 항] + [혼합 항]
```

세 항 모두 **평균 입경은 거의 안 움직이는데 꼬리만 자라는** 방식으로 작동한다는 것이
이 노트의 반복되는 주제다 — [[colloidal-destabilization-lpc-defect-mechanism]] §3과 같은 구조.

## 2. 쉘프라이프는 하나의 시계가 아니다 — 세 시계의 min()

"쉘프라이프 6개월"이라는 스펙은 단일 물리량이 아니다. 서로 **독립적으로 흐르는 세 개의
시계** 중 가장 빠른 것이 만료를 결정한다:

| 시계 | 구동 물리 | 되돌릴 수 있나 | 무엇이 먼저 변하나 |
|---|---|---|---|
| (a) 침강 | Stokes 중력침강 vs 브라운 확산 | **가역**(교반·롤링) | 상하 농도 구배 |
| (b) 응집 | DLVO 장벽 돌파(이온강도·pH·온도) | 대체로 **비가역** | LPC 꼬리 → 평균 입경 |
| (c) 화학 열화 | 성분 간 산화환원·분해 | **비가역** | 제타·pH·점도 → MRR |

(a)는 물리만으로 닫히므로 먼저 계산한다. 100 nm 실리카가 300 mm 드럼을 침강으로 종단하는
데 걸리는 시간은 **1.3년 수준**이고, 같은 입자가 1 µm 응집체가 되면 **5일 수준**으로
100배 빨라진다. 즉 **침강은 원인이 아니라 (b)의 지표**다 — 드럼 바닥에 케이크가 보인다면
그건 "오래 뒀다"가 아니라 "이미 응집했다"는 신호다.

```python verify
import math
# --- 물리상수 (CRC 물성; 25 °C 물) ---
kT   = 1.380649e-23 * 298.15   # J
eta  = 8.9e-4                  # Pa·s, 물 25 °C
rho_f, g = 997.0, 9.81
rho_p = 2200.0                 # 비정질 콜로이드 실리카 (Lin 2011 학위논문은 석영값 2648 사용 — §6 주)
H_DRUM = 0.300                 # m, 200 L 드럼 액주 높이 규모 (가정 — 미검증)

def stokes(d_nm):
    a = d_nm*1e-9/2
    v = 2*a*a*(rho_p-rho_f)*g/(9*eta)          # Stokes 침강속도 [m/s]
    m_eff = 4/3*math.pi*a**3*(rho_p-rho_f)     # 부력 보정 질량
    l_g = kT/(m_eff*g)                         # 중력 길이(barometric scale height)
    return v, H_DRUM/v, l_g

v1, t1, lg1 = stokes(100)
v2, t2, lg2 = stokes(1000)
print(f"재현: d=100 nm → v={v1:.2e} m/s, 드럼 종단 {t1/86400/365:.2f} 년, 중력길이 {lg1*1e3:.2f} mm")
print(f"재현: d=1000 nm(응집체) → v={v2:.2e} m/s, 드럼 종단 {t2/86400:.1f} 일, 중력길이 {lg2*1e6:.2f} µm")

# (1) 침강속도는 d^2 스케일 — 10배 입자면 100배 빠르다
assert abs((v2/v1) - 100.0) < 1e-6
assert 1.0 < t1/86400/365 < 2.0, "100 nm 1차입자의 침강 시계는 '년' 단위여야 한다"
assert 3.0 < t2/86400 < 10.0,    "1 µm 응집체의 침강 시계는 '일' 단위여야 한다"
print(f"재현: 침강시계 비 = {t1/t2:.0f}배 (d^2 법칙) — 응집이 곧 침강의 원인")

# (2) 중력길이가 드럼 높이보다 훨씬 작다 = 평형상태는 '가라앉은 상태'다.
#     그런데도 슬러리가 실용적으로 버티는 이유는 평형이 아니라 '도달 시간'이 길기 때문.
assert lg1 < H_DRUM, "100 nm에서도 열역학 평형은 침강 쪽"
print(f"재현: 100 nm 중력길이 {lg1*1e3:.2f} mm ≪ 드럼 {H_DRUM*1e3:.0f} mm "
      f"→ 안정 슬러리가 안 가라앉는 것은 평형이 아니라 '느린 동역학' 덕분")

# (3) 화학 시계와의 비교 — Luan et al. 2018 (doi:10.1149/2.0171808jss)은
#     FA/O계 슬러리가 7일 만에 MRR 2846 → 1089 Å/min 으로 무너지는 것을 보고했다.
T_CHEM_DAY = 7.0
assert T_CHEM_DAY < t1/86400, "화학 시계가 1차입자 침강 시계보다 훨씬 빨라야 한다"
print(f"문헌값 대조: 화학 시계 {T_CHEM_DAY:.0f} 일 vs 침강 시계 {t1/86400:.0f} 일 "
      f"→ min() 지배자는 화학 (Luan 2018, doi:10.1149/2.0171808jss)")
```

## 3. 화학 시계 — 7일에 무너지는 슬러리, 그리고 그것을 만든 성분쌍

**Luan, X., Cheng, J., Liu, Y., Wang, C. (2018). "Effect of Complexing Agent Choices on Dishing
Control Level and the Shelf Life in Copper CMP Slurry." *ECS J. Solid State Sci. Technol.*
7(8), P391–P396. DOI: 10.1149/2.0171808jss** — 전문 확보
(`papers/luan2018-ecsjss-complexing-agent-shelf-life-cu-cmp.pdf`, 미러 사이트 폴백).

Cu CMP 슬러리 두 종(SiO₂ + DIW + AEO 계면활성제 + H₂O₂ + 착화제)에서 착화제만
**FA/O 고분자 킬레이트 vs 글리신**으로 바꾸고 7일간 정치(setting)했다:

| 지표 (0일 → 7일) | FA/O계 | 글리신계 |
|---|---|---|
| Cu MRR | 2846 → **1089 Å/min** (−62 %) | 유의 변화 없음 |
| 평균 입경 | 97.8 → **124 nm** (+27 %) | 유의 변화 없음 |
| 제타전위 | −43.5 → **−22 mV** | 유의 변화 없음 |
| pH·점도 | 변함 | 변함 없음 |

→ FA/O계 쉘프라이프 **≤7일**, 글리신계 **≥7일**. 핵심은 원문이 "알칼리에서 H₂O₂가
자기분해한다"는 통설을 **반증**했다는 것이다: 같은 pH·같은 H₂O₂를 쓰는 글리신계가 멀쩡하므로
범인은 H₂O₂ 단독이 아니라 **FA/O와 H₂O₂의 산화환원 반응**이다(원문 식 [8]).

### 3.1 반증 설계 — Table II의 10-run 성분 분리 실험 (이것이 2액형의 원형이다)
저자들은 슬러리 성분을 **조성 A와 조성 B로 쪼개 7일 따로 보관한 뒤 섞어** 안정성을 봤다.
이 표가 이 단원의 핵심이다. 불안정 판정은 **오직 FA/O와 H₂O₂가 같은 조성에 들어 있을 때만**
발생한다 — 어느 성분이 몇 개든, SiO₂가 어디 있든 무관하다.

```python verify
import statistics as st
# --- Luan et al. 2018, Table II (doi:10.1149/2.0171808jss) 전 10행 그대로 ---
# (조성A 성분집합, 조성B 성분집합, MRR[Å/min], 평균입경[nm], pH, 점도[mPa·s], 제타[mV], 원문판정)
T2 = [
 ({'SiO2','DIW','AEO','FA/O'}, {'H2O2'},        2772, 98.5,  8.82, 1.24, -40, 'stable'),
 ({'SiO2','DIW','AEO','H2O2'}, {'FA/O'},        2806, 101.2, 8.81, 1.26, -39, 'stable'),
 ({'SiO2','DIW','H2O2','FA/O'},{'AEO'},          924, 123.6, 9.22, 1.56, -19, 'unstable'),
 ({'AEO','DIW','H2O2','FA/O'}, {'SiO2'},        1024, 122.0, 9.20, 1.58, -20, 'unstable'),
 ({'SiO2','DIW','AEO'},        {'H2O2','FA/O'},  956, 124.0, 9.20, 1.55, -18, 'unstable'),
 ({'SiO2','DIW','FA/O'},       {'H2O2','AEO'},  2789, 97.8,  8.80, 1.25, -42, 'stable'),
 ({'DIW','FA/O','AEO'},        {'H2O2','SiO2'}, 2823, 98.6,  8.80, 1.24, -38, 'stable'),
 ({'SiO2','DIW','H2O2'},       {'FA/O','AEO'},  2760, 102.3, 8.80, 1.25, -37, 'stable'),
 ({'DIW','H2O2','AEO'},        {'FA/O','SiO2'}, 2796, 101.3, 8.82, 1.25, -38, 'stable'),
 ({'DIW','H2O2','FA/O'},       {'AEO','SiO2'},   986, 126.3, 9.21, 1.56, -20, 'unstable'),
]

# (1) 2액형 설계 규칙의 완전 재현: 불안정 ⟺ FA/O와 H2O2가 같은 조성에 공존
def coexist(A, B):
    return ({'FA/O','H2O2'} <= A) or ({'FA/O','H2O2'} <= B)
for A,B,mrr,d,ph,mu,z,verdict in T2:
    pred = 'unstable' if coexist(A,B) else 'stable'
    assert pred == verdict, f"규칙 반례: {A}|{B} → 예측 {pred}, 원문 {verdict}"
n_un = sum(1 for r in T2 if r[7]=='unstable')
print(f"재현: Table II 10행 전부 일치 — '반응쌍 공존 ⟺ 불안정' (불안정 {n_un}건/10건)")

# (2) 이 규칙은 '성분 개수'나 'SiO2 위치'로는 설명되지 않는다(대안가설 기각)
byN = {}
for A,B,*_,v in T2: byN.setdefault(len(A), set()).add(v)
assert any(len(s) > 1 for s in byN.values()), "조성A 성분수가 같은데 판정이 갈리는 행이 있어야"
sio2_A = {v for A,B,*_,v in T2 if 'SiO2' in A}
assert len(sio2_A) > 1, "SiO2가 A에 있어도 판정이 갈린다 — 연마입자 위치는 원인이 아니다"
print("재현: 성분 개수·SiO2 배치로는 판정이 갈리지 않는다 → 원인은 반응쌍 자체")

# (3) QC 항목별 판별력 d' = |Δ평균| / (표준편차 합). 5개 지표 전부 '겹침 0'으로 분리된다.
names = ['MRR(Å/min)','평균입경(nm)','pH','점도(mPa·s)','제타(mV)']
S = [r[2:7] for r in T2 if r[7]=='stable']
U = [r[2:7] for r in T2 if r[7]=='unstable']
dp = {}
for i,n in enumerate(names):
    s = [r[i] for r in S]; u = [r[i] for r in U]
    gap = min(s)-max(u) if st.mean(s) > st.mean(u) else min(u)-max(s)
    assert gap > 0, f"{n}: 두 군이 겹친다"
    dp[n] = abs(st.mean(s)-st.mean(u))/(st.stdev(s)+st.stdev(u))
for n,v in sorted(dp.items(), key=lambda kv:-kv[1]):
    print(f"  판별력 d' {n:12s} = {v:5.1f}")
assert dp['평균입경(nm)'] == min(dp.values()), "평균입경이 가장 약한 판별자여야 한다"
print(f"재현: 5개 QC 지표 모두 완전분리(겹침 0)이나 d'는 6.6~27.8로 4배 차이 — "
      f"가장 약한 쪽이 DLS 평균입경({dp['평균입경(nm)']:.1f})")

# (4) pH 차이는 '작아 보이지만' 실제로는 [H+]가 2.4배 다르다 (Luan 2018 Table II)
dpH = min(r[4] for r in T2 if r[7]=='unstable') - max(r[4] for r in T2 if r[7]=='stable')
assert abs(dpH - 0.38) < 1e-9
print(f"재현: pH 갭 {dpH:.2f} (8.82 → 9.20) = [H+] {10**dpH:.2f}배 — 로그 눈금의 착시 주의")
```

### 3.2 2액형(A/B 분리)의 설계 규칙 — 이 표에서 직접 나온다
1. **분리해야 할 것은 "성분"이 아니라 "반응쌍"이다.** 산화제만 따로 빼는 것(No.1)도,
   착화제만 따로 빼는 것(No.2)도 둘 다 성립한다 — 둘 중 **하나만 격리하면 충분**하다.
2. **같은 쪽에 몰아넣어도 된다.** No.6~No.9처럼 두 성분을 함께 옮겨도 반응쌍만 안 만나면 안정.
3. **연마입자의 소속은 자유도다.** SiO₂를 A에 두든 B에 두든 판정이 바뀌지 않았다(코드 (2)).
   → 실무적으로 **"입자 쪽 액(abrasive side) / 화학 쪽 액(chemical side)"이라는 흔한 분할은
   물리적 필연이 아니라 취급 편의**다. 반응쌍이 둘 다 화학 쪽에 있으면 2액형이어도 소용없다.
4. 따라서 2액형 도입은 쉘프라이프 문제를 **해결**하는 동시에 새 리스크를 만든다: 이제
   **혼합비와 혼합 후 사용시한(pot life)이 새로운 QC 항목**이 된다.

## 4. 희석 항 — 물을 타는 것은 중립 조작이 아니다

DLVO만 보면 희석은 **안정화 방향**이어야 한다. 이온강도가 1/n로 떨어지면 Debye 길이
κ⁻¹ ∝ 1/√I 는 √n배 늘어 반발이 더 멀리까지 작동한다
([[dlvo-ionic-strength-ph-aggregation-kinetics]] §2). 실측은 반대다.

**US8303373B2 — "Slurry supplying apparatus and method of polishing semiconductor wafer
utilizing same" (Sumco Techxiv Corp., 출원 2009-05-22 / 등록 2012-11-06)** — 전문 확보
(`papers/us8303373b2-sumco-diluted-slurry-supply.txt`, freepatentsonline 폴백).
마무리 연마용 콜로이드 실리카(수용성 폴리머 함유) 원액을 **희석배율 1:25**로 POU 희석할 때
희석액 종류별 제타전위와 평균 입경(원문 FIG. 3):

| 희석 조건 | 제타전위 | 평균 입경 |
|---|---|---|
| 원액(RAW) | ≈16 mV | ≈42 nm |
| **순수(UPW)** | ≈6 mV | **≈165 nm** (3.9배) |
| 순수 + 초음파 | ≈6 mV(회복 안 됨) | ≈84 nm |
| 암모니아수 | ≈13 mV | ≈66 nm |
| 메탄올 | ≈15 mV | ≈53 nm |
| **KCl 첨가수** | **≈24 mV**(원액 초과) | ≈44 nm |

여기서 두 가지가 중요하다.

**(i) 초음파는 크기만 되돌리고 안정성은 되돌리지 못한다.** 순수 희석 후 초음파를 걸면
입경은 165 → 84 nm로 절반이 되지만 제타는 6 mV에 그대로 머문다. 기계적 해응집(운동학)과
콜로이드 안정화(열역학)는 다른 축이다 — **교반·초음파로 되살린 슬러리는 "다시 뭉칠 준비가
된 슬러리"**다. §2 표의 "가역/비가역" 구분이 여기서 실증된다.

**(ii) 염(KCl)을 넣었더니 분산이 가장 좋았다** — DLVO 1차 직관과 정면 충돌한다. 특허는
이 계에 **수용성 폴리머**가 들어 있고 희석 시 폴리머 상호작용이 지배적이라고 서술한다.
희석이 고분자의 표면 피복률을 떨어뜨리면 **가교 응집(bridging flocculation)**이 일어나고,
이때 염은 고분자 사슬 형태(coil 수축)를 바꿔 가교를 줄일 수 있다. 즉 폴리머 함유계에서
희석의 지배 메커니즘은 EDL이 아니다. ⚠ 이 해석은 특허 본문이 명시한 것이 아니라 **이 노트의
추정**이고, 원문 제타값의 **부호가 표기되지 않아**(실리카가 pH 9.9–10.3에서 +16 mV일 수는
없다) 절댓값으로 읽었다 — 미검증.

```python verify
import math
# --- (A) DLVO가 예측하는 희석 효과: 1:25 희석 (US8303373B2 명시 배율) ---
DILUTION = 25.0                     # 원액 1 : 희석액 25
def kappa_inv_nm(I_M):              # 1:1 전해질, 25 °C 물: κ⁻¹ ≈ 0.304/√I [nm]
    return 0.304/math.sqrt(I_M)
I0 = 1.0e-3                         # 가정: 원액 유효 이온강도 1 mM (미검증 — 특허 미기재)
I1 = I0/(1+DILUTION)
print(f"재현: 희석 1:{DILUTION:.0f} → I {I0*1e3:.2f} → {I1*1e3:.3f} mM, "
      f"κ⁻¹ {kappa_inv_nm(I0):.1f} → {kappa_inv_nm(I1):.1f} nm ({math.sqrt(1+DILUTION):.2f}배 증가)")
assert kappa_inv_nm(I1) > kappa_inv_nm(I0)    # DLVO 예측: 반발이 더 멀리 → 더 안정

# --- (B) 실측 (US8303373B2 FIG.3): 순수 희석은 오히려 4배 가까이 응집 ---
d_raw, d_water, d_water_us, d_nh3, d_meoh, d_kcl = 42, 165, 84, 66, 53, 44
z_raw, z_water, z_water_us, z_nh3, z_meoh, z_kcl = 16, 6, 6, 13, 15, 24
assert d_water/d_raw > 3.5, "순수 희석이 응집을 일으켰다는 사실 확인"
print(f"문헌값 대조: 순수 희석 {d_raw} → {d_water} nm ({d_water/d_raw:.1f}배) "
      f"— DLVO 부호 예측(안정화)과 정반대 (US8303373B2 FIG.3)")

# (1) 초음파는 크기만 회복, 제타는 회복 못함 → 운동학 ≠ 열역학
assert d_water_us < d_water and z_water_us == z_water
rec = (d_water-d_water_us)/(d_water-d_raw)
print(f"재현: 초음파 입경 회복률 {rec*100:.0f}% 인데 제타 회복률 0% (6 mV 그대로) "
      f"— 재분산 ≠ 재안정화 (US8303373B2)")

# (2) 제타가 클수록 입경이 작다 — 같은 데이터 안에서 단조성 확인(순위상관 = -1)
pairs = sorted([(z_water,d_water),(z_nh3,d_nh3),(z_meoh,d_meoh),(z_kcl,d_kcl)])
ds = [d for z,d in pairs]
assert all(ds[i] > ds[i+1] for i in range(len(ds)-1)), "제타 증가 → 입경 감소가 단조여야"
print(f"재현: 제타 {[z for z,_ in pairs]} mV ↔ 입경 {ds} nm — 완전 단조(순위상관 −1)")

# (3) DLVO 역설: 염 첨가(KCl)가 최고 성적. EDL 가설이면 부호가 반대여야 한다.
assert z_kcl > z_raw and d_kcl < d_nh3
print(f"미검증 해석: KCl 희석 제타 {z_kcl} mV > 원액 {z_raw} mV → EDL 압축 예측과 반대 "
      f"→ 수용성 폴리머 가교 응집이 지배 가설(US8303373B2 본문은 폴리머 상호작용만 명시)")

# --- (C) 같은 특허의 별도 실험: 순수 vs 암모니아수 희석의 현장 지표 ---
lpc_w, lpc_n = 465, 163          # pcs/cc
mu_w,  mu_n  = 2.1, 1.2          # cP
ph_w,  ph_n  = 9.86, 10.28
rr_w,  rr_n  = 0.82, 2.51        # SiO2 제거율 Å/min
haze_w, haze_n = 0.024, 0.036    # ppm
assert lpc_w/lpc_n > 2.5 and mu_w/mu_n > 1.7
print(f"문헌값 대조: 순수 희석 LPC {lpc_w} vs 암모니아 {lpc_n} pcs/cc ({lpc_w/lpc_n:.2f}배), "
      f"점도 {mu_w} vs {mu_n} cP ({mu_w/mu_n:.2f}배), pH {ph_w} vs {ph_n}")
assert rr_n/rr_w > 3.0 and haze_n > haze_w
print(f"재현: 암모니아 희석이 SiO2 제거율 {rr_n/rr_w:.2f}배로 올리지만 haze는 "
      f"{haze_w} → {haze_n} ppm 로 악화 — 희석액 선택은 트레이드오프 (US8303373B2)")
```

### 4.1 희석의 실무 규칙 (특허 청구항이 실제로 요구하는 것)
- 희석수는 순수가 아니라 **응집방지제(ammonia / ammonium bicarbonate / KOH / NaOH, 또는
  Li⁺·Na⁺·K⁺·Mg²⁺·Ca²⁺·NH₄⁺ 계열 염)를 탄 물**이어야 한다(US8303373B2 청구항).
- 혼합 후 **pH ≥ 9**를 유지해야 하며, 제거율·haze 종합 최적 창은 **pH 9.5–10.5**(원문 FIG. 5:
  제거율은 pH에 단조증가, haze는 pH≈10에서 최소).
- 암모니아(ammonium bicarbonate) 희석은 **pH 의존성이 낮아** 원액 pH 변동·공정 중 pH 조정제
  소모에도 응집도가 낮게 유지된다(원문 FIG. 6). 순수·KCl 희석은 pH<9에서 응집도가 급등한다.
- ⚠ **주의**: 이 규칙은 *수용성 폴리머를 포함한 실리콘 마무리연마 슬러리* 계에서 나왔다.
  세리아 STI 슬러리나 W 슬러리에 그대로 이식하면 안 된다(§8).

## 5. 혼합 항 — 두 액을 섞는 순간의 헤테로응집, 그리고 그 임계비의 폐형식

2액형·혼합연마재(MAS)에서 **부호가 다른 두 입자를 섞으면 중화점이 생긴다.**

**Lin, F. (2011). "A Study of the Colloidal Stability of Mixed Abrasive Slurries of Silica and
Ceria Nanoparticles for Chemical Mechanical Polishing." MSc thesis, University of Alberta.
DOI: 10.7939/r3967c** — 전문 확보
(`papers/lin2011-ualberta-thesis-mixed-abrasive-colloidal-stability.txt`, ERA/Scholaris DSpace API).

pH 4에서 실리카는 음(−29 mV), 세리아는 양(+45 mV)이다. 세리아를 실리카 슬러리에 조금씩
넣으면 양전하 세리아가 음전하 실리카 표면에 붙어 **실리카의 알짜 전하를 0으로 지나간다**.
그 중량비 구간(**transition range**)에서 슬러리는 급속 침강한다. 저자는 표면전하밀도가
제타전위에 선형이라고 가정해 알짜전하 0 조건을 풀어 **중량비의 등전점** 폐형식을 얻었다
(원문 식 (15)):

```
WT_c / WT_s = −(ζ_s/ζ_c) · (ρ_c/ρ_s) · (R_c/R_s)
```

즉 **임계 혼합비는 두 입자의 제타전위 비 × 밀도 비 × 반경 비**로 결정된다. 실리카 입자가
작아질수록(비표면적 증가) 중화에 필요한 세리아가 많아져 임계비가 커진다.

```python verify
# --- Lin 2011 (doi:10.7939/r3967c) 식 (15) 재현 ---
RHO_C, RHO_S = 7.65, 2.648      # g/cm3, 원문이 쓴 값(세리아/실리카)
R_C = 5.4                       # nm, 세리아 1차입경 (원문: 평균 20.39 nm 대신 1차입경 사용)
SILICA = {'EB6080': 132.2, 'EB6040': 75.1, 'BZ': 32.5}   # nm, 원문 Table

def iep_weight_ratio(zeta_s, zeta_c, r_s, r_c=R_C):
    return -(zeta_s/zeta_c)*(RHO_C/RHO_S)*(r_c/r_s)

# (1) pH 4: ζ_s=-29 mV, ζ_c=+45 mV → 원문이 손계산한 0.076 을 재현
m4 = iep_weight_ratio(-29, 45, SILICA['EB6080'])
assert abs(m4 - 0.076) < 5e-4, f"{m4}"
EXP4 = 0.067                    # 실측 x-절편 (원문 Figure 10)
print(f"재현: pH 4 모델 임계중량비 {m4:.3f} vs 실측 {EXP4:.3f} "
      f"(편차 {(m4-EXP4)/EXP4*100:+.1f} %) — doi:10.7939/r3967c")

# (2) pH 3: ζ_s=-23 mV, ζ_c=+50 mV → 원문 0.054, 실측 0.055 (독립 2번째 점)
m3 = iep_weight_ratio(-23, 50, SILICA['EB6080'])
EXP3 = 0.055
assert abs(m3 - 0.054) < 1e-3
print(f"재현: pH 3 모델 {m3:.3f} vs 실측 {EXP3:.3f} (편차 {(m3-EXP3)/EXP3*100:+.1f} %)")

# (3) 두 점 모두 15 % 이내 — 폐형식이 pH를 가로질러 작동한다
for m, e in ((m4, EXP4), (m3, EXP3)):
    assert abs(m-e)/e < 0.15
print("재현: 2개 pH 조건 모두 모델-실측 편차 15 % 이내 (n=2 — 일반화는 미검증)")

# (4) 방향성: pH를 4→3으로 내리면 실리카 전하가 약해져 임계비가 내려간다
assert m3 < m4 and EXP3 < EXP4
print(f"재현: pH 4→3 에서 임계비 모델 {m4:.3f}→{m3:.3f}, 실측 {EXP4:.3f}→{EXP3:.3f} "
      f"— 부호 일치")

# (5) 입경 스케일링: 임계비 ∝ 1/R_s. 작은 실리카는 훨씬 많은 세리아를 견딘다.
r_big, r_small = SILICA['EB6080'], SILICA['BZ']
ratio = iep_weight_ratio(-29, 45, r_small)/m4
assert abs(ratio - r_big/r_small) < 1e-9
print(f"재현: 실리카 {r_big:.1f} → {r_small:.1f} nm 이면 임계비가 {ratio:.2f}배 "
      f"({iep_weight_ratio(-29,45,r_small):.3f}) — 비표면적 1/R 법칙")

# (6) 혼합비 오차의 비대칭 위험: 임계비의 ±30 % 창(원문 transition range 0.05~0.1)에
#     들어가면 불안정. 목표를 0.02(저비율 안전지대)로 잡았을 때 허용 오차 배수.
TRANS_LO, TRANS_HI = 0.05, 0.10     # 원문 Figure 10 (EB6080)
target = 0.02
assert target < TRANS_LO
print(f"재현: 목표 혼합비 {target:.2f}에서 불안정 구간 진입까지 여유는 "
      f"{TRANS_LO/target:.1f}배 — 혼합비 오차가 2.5배를 넘으면 침강 구간 (doi:10.7939/r3967c)")
```

**실무 함의**: 2액형 블렌더의 혼합비 오차는 **선형 성능 저하가 아니라 절벽**을 만든다.
중화점 근처에서는 수 %의 비율 오차가 제타를 부호 전환시킨다. 반대로 목표비를
불안정 구간에서 **충분히 멀리**(위 예에서 2.5배) 잡아두면 블렌더 정밀도 요구가 확 낮아진다 —
"혼합비 스펙"은 성능 최적점이 아니라 **불안정 구간과의 거리**로 정해야 한다.

## 6. 현장 QC 항목 — 무엇을 재고, 각 계측기가 못 보는 것은 무엇인가

**Vazquez Bengochea, L., Sampurno, Y., Kavaljer, M., Johnston, R., Philipossian, A. (2018).
"Characterization of CMP Slurries Using Densitometry and Refractive Index Measurements."
*Micromachines* 9(11), 542. DOI: 10.3390/mi9110542 (PMC6266087)** — OA 전문 확보.

상용 슬러리 3종(Fujimi PL-7106 / Klebosol 1501-50 / CMC W7801)에 UPW를 0~9.09 % v/v로
조금씩 더하며 **밀도계(Mettler Toledo Densito 30PX, 분해능 1×10⁻⁴ g/cm³)**와
**인라인 굴절계(K-Patents PR-33-S, 분해능 1×10⁻⁵)**를 동시에 비교했다. 원문 Table 1의
POU 블렌딩 스펙도 그대로 유용하다: **UPW : PL-7106 : H₂O₂(30 %) = 87.0 : 10.2 : 2.8**,
**W-7801 : H₂O₂(30 %) = 97.1 : 2.9**, Klebosol 1501-50은 **as-received**(희석 없음).

### 6.1 QC 항목 패널과 각 항목의 맹점
| 항목 | 잡아내는 것 | 못 보는 것(맹점) |
|---|---|---|
| 밀도 | 고형분·희석비 | 저고형분 슬러리에서 분해능 부족(§6.2), 온도 오차에 취약 |
| 굴절률(인라인) | 희석비·H₂O₂ 농도 | 슬러리별 개별 교정 필수, 온도 비선형 |
| pH | 산/염기 오투입 | **H₂O₂는 비이온성 → 원리적으로 안 보임**; 완충계는 희석도 거의 안 보임 |
| 전도도 | 이온 오염·염 투입 | 첨가제가 만드는 동적평형 변화와 조성 변화를 구분 못 함 |
| DLS 평균입경 | 대규모 응집 | **꼬리(LPC)에 둔감** — §3.1 코드에서 판별력 최하위(d′ 6.6) |
| SPOS/LPC | 꼬리 그 자체 | 느리고, 통상 희석 후 측정(희석 자체가 §4의 교란) |
| 제타전위 | 안정성 여유 | 절대값이 계·희석조건 의존, 인라인 불가 |
| 점도 | 화학 열화·가교 | 원인 특정 불가(§3.1에서 d′ 15.6으로 의외로 강함) |
| 블랭킷 MRR | 최종 성능 | 웨이퍼·시간 소모 — d′ 27.8로 가장 강하지만 가장 비싸다 |

### 6.2 정량 — 밀도계 vs 굴절계, 그리고 **진짜 한계를 정하는 것은 온도 보정**이다
원문의 LOD 정의는 `LOD = 계측기 분해능 / 기울기`다. 그런데 이 정의는 **온도 보정 오차를
빼고** 계산한 이상적 한계다. 원문 자신이 루프 순환 중 펌프 발열로 **3~4 °C**가 올랐다고
보고했으므로, 온도항을 같은 단위(%UPW)로 환산해 비교하면 순위가 달라진다.

```python verify
# --- Vazquez Bengochea et al. 2018 (doi:10.3390/mi9110542) Table 2 재현 ---
RES_DENS, RES_RI = 1e-4, 1e-5        # 계측기 분해능 (원문 §2: g/cm3, RI 무차원)
# 슬러리: (밀도 기울기 [g/cm3 per %UPW], RI 기울기 [per %UPW], 원문 LOD_dens, 원문 LOD_RI)
TBL = {'PL-7106':(1.33e-4, 3.52e-5, 0.752, 0.284),
       '1501-50':(1.98e-3, 2.21e-4, 0.050, 0.045),
       'W7801'  :(1.15e-4, 2.37e-5, 0.870, 0.422)}
for name,(sd,sr,lod_d,lod_r) in TBL.items():
    calc_d, calc_r = RES_DENS/sd, RES_RI/sr
    assert abs(calc_d-lod_d) < 0.002, f"{name} 밀도 LOD 불일치 {calc_d}"
    assert abs(calc_r-lod_r) < 0.002, f"{name} RI LOD 불일치 {calc_r}"
    print(f"재현: {name:8s} LOD 밀도 {calc_d:.3f} %UPW (문헌값 {lod_d}), "
          f"RI {calc_r:.3f} %UPW (문헌값 {lod_r}), RI/밀도 = {calc_r/calc_d:.2f}")
# 원문 주장: 저고형분 2종에서 굴절계가 '50 % 더 작은 변화'를 본다
for name in ('PL-7106','W7801'):
    sd,sr,_,_ = TBL[name]
    assert (RES_RI/sr)/(RES_DENS/sd) <= 0.50
print("문헌값 대조: 저고형분 2종(PL-7106·W7801)에서 굴절계 LOD가 밀도계의 50 % 이하 — 원문 주장 성립")

# --- 여기서부터는 이 노트의 계산: 온도 보정이 LOD를 삼킨다 ---
# 원문 Eq.(1) d_c = d_m[1+α(T−T0)], α=0.0023/°C; Eq.(2) RI_c = RI_m[1+β(T−T0)], β=0.0001/°C
ALPHA_PAPER, BETA_PAPER = 0.0023, 0.0001
D0, RI0 = 1.0737, 1.333          # 원문이 측정한 PL-7106 밀도 / 물 RI 근방
# 물의 실제 체팽창계수를 CRC 밀도표에서 직접 계산 (20/25/30 °C)
rho = {20:0.998207, 25:0.997047, 30:0.995650}
alpha_true = (rho[20]-rho[30])/(rho[25]*10)
print(f"재현: CRC 물 밀도표에서 계산한 체팽창계수 {alpha_true:.2e} /°C")
assert 2.4e-4 < alpha_true < 2.7e-4
# ⚠ 원문 α는 물 실측값의 약 9배 — 오타(0.00023?) 의심. 두 경우를 모두 환산한다.
ratio_alpha = ALPHA_PAPER/alpha_true
assert ratio_alpha > 8
print(f"⚠ 미검증(원문 값 의심): 원문 α={ALPHA_PAPER} 는 물 실측값의 {ratio_alpha:.1f}배")

sd_PL, sr_PL = TBL['PL-7106'][0], TBL['PL-7106'][1]
for label, a in (('원문 α', ALPHA_PAPER), ('CRC 물 α', alpha_true)):
    upw_per_C = D0*a/sd_PL
    print(f"  밀도계: {label} 기준 1 °C 오차 = {upw_per_C:.1f} %UPW 상당 "
          f"(LOD {TBL['PL-7106'][2]} %UPW의 {upw_per_C/TBL['PL-7106'][2]:.0f}배)")
    assert upw_per_C > TBL['PL-7106'][2]
upw_per_C_RI = RI0*BETA_PAPER/sr_PL
print(f"  굴절계: 1 °C 오차 = {upw_per_C_RI:.1f} %UPW 상당 "
      f"(LOD {TBL['PL-7106'][3]} %UPW의 {upw_per_C_RI/TBL['PL-7106'][3]:.0f}배)")
# RI 온도계수는 물리값과 정합한다(문헌 dn/dT ≈ −1.0e-4 /°C, 25 °C 물)
DNDT_LIT = 1.0e-4
assert abs(RI0*BETA_PAPER - DNDT_LIT)/DNDT_LIT < 0.4
print(f"재현: 원문 β가 주는 |dn/dT| = {RI0*BETA_PAPER:.2e} /°C vs 문헌 {DNDT_LIT:.1e} /°C "
      f"(40 % 이내 일치) — 밀도 쪽 α만 자릿수가 어긋난다")

# 결론: 3~4 °C 드리프트(원문 보고)가 보정 없이 남으면 두 계측기 모두 LOD가 무의미해진다.
DRIFT = 3.5
print(f"재현: 원문이 보고한 펌프 발열 {DRIFT} °C 를 보정하지 않으면 "
      f"밀도계 {D0*alpha_true*DRIFT/sd_PL:.0f} %UPW, 굴절계 {RI0*BETA_PAPER*DRIFT/sr_PL:.0f} %UPW "
      f"의 겉보기 조성 변화가 생긴다 → 실효 한계는 분해능이 아니라 온도 보정 정확도")
```

**결론(이 노트의 기여)**: 인라인 슬러리 QC에서 "굴절계가 밀도계보다 분해능이 좋다"는 비교는
**필요조건일 뿐 충분조건이 아니다.** 두 계측기 모두 1 °C의 온도 보정 오차만으로 LOD의
수 배~수십 배에 달하는 겉보기 조성 변화를 만든다(위 코드). 따라서 POU QC 설계의 첫 번째
사양은 계측기 분해능이 아니라 **온도 측정·보정 정확도와 서브팹 온도 안정성**이다.

### 6.3 희석이 QC 자체를 교란한다
원문은 UPW를 9.09 %까지 더해도 DLS 평균 입경이 불변임을 확인했다(PL-7106 **68.3±0.4 nm**,
1501-50 **58.5±0.3 nm**, W7801 **112.8±0.7 nm**; 표준편차 4~7 Å는 장비 노이즈 수준).
반면 같은 논문이 인용한 Nogowski et al.(2007, ICPT, 2차 인용 — 원문 미확보)은
**1:1 → 1:4 같은 큰 희석**에서는 입도분포가 바뀐다고 보고한다. §4의 1:25 희석 실측
(42 → 165 nm)이 후자와 같은 방향이다. 즉 **"측정용 희석"은 안전한 배율에서만 안전하다** —
LPC 계수기가 요구하는 큰 희석은 측정 대상 자체를 바꿀 수 있다.

## 7. 세 항을 합치면 — 루프 진입 시점의 LPC는 이미 결정되어 있다

| 항 | 대표 크기(문헌 실측) | 되돌릴 수 있나 | 대표 QC 항목 |
|---|---|---|---|
| 보관(화학) | 7일에 MRR −62 %, 제타 −43.5→−22 mV (Luan 2018) | 불가 | 제타·점도·pH |
| 보관(침강) | 100 nm 1차입자 드럼 종단 1.3년 (§2 계산) | 가역(롤링) | 상하 샘플 밀도차 |
| 희석 | 1:25 순수 희석 시 42→165 nm, LPC 2.85배 (US8303373B2) | 부분(초음파는 크기만) | LPC·점도·pH |
| 혼합 | 임계중량비 ±2.5배 이내 진입 시 급속침강 (Lin 2011) | 불가 | 혼합비·제타 |

선행 노트가 다룬 **전단 생성항**(G ≥ 1000–1500 s⁻¹ AND Camp ≥ 임계)은 이 네 항 **뒤에**
붙는다. 순서가 중요한 이유는 §4(ii)에서 봤듯 **한 번 응집한 입자는 필터에 잘 잡히지도 않고
(IEP 근처 제타 저하 → 오히려 포집은 쉬워지지만 안정성은 이미 잃음), 초음파로 부수면
크기만 돌아오고 안정성은 안 돌아오기 때문**이다. 루프 상류(제조·보관·블렌딩)에서 생긴
LPC는 하류(필터)에서 회수되지 않는다 — 이것이 POU 필터 스펙만 조여서는 결함이 안 잡히는
구조적 이유다.

## 8. 한계·정직성 표기

- ⚠ **미검증**: §4의 US8303373B2 제타값은 **부호 표기가 없다**. 콜로이드 실리카가 pH 9.9–10.3
  에서 +16 mV일 수 없으므로 절댓값으로 읽었다. 부호가 실제로 양이라면(표면개질 실리카 등)
  §4(ii)의 폴리머 가교 해석 자체가 달라진다.
- ⚠ **미검증**: §4의 "가교 응집(bridging flocculation)이 지배 메커니즘"은 **이 노트의 추정**
  이다. 특허 본문은 "수용성 폴리머의 상호작용"까지만 말하고 메커니즘을 특정하지 않았다.
  희석 시 pH가 10.28 → 9.86으로 내려간 것(표면전하 감소)도 경쟁 설명이며, 둘을 가르는
  실험(폴리머 없는 동일 실리카로 같은 희석)을 원문은 하지 않았다.
- ⚠ **미검증**: §4의 Debye 길이 계산은 원액 유효 이온강도를 1 mM로 **가정**했다(특허 미기재).
  결론(희석이 κ⁻¹를 √26배 늘린다)은 가정값과 무관한 비율 주장이지만, 절대 κ⁻¹ 값은 쓰면 안 된다.
- ⚠ **원문 값 의심**: §6.2에서 Micromachines 2018이 쓴 밀도 온도보정계수 α=0.0023 /°C는
  CRC 물 밀도표에서 계산한 실측 체팽창계수 2.56×10⁻⁴ /°C의 **9배**다. 오타(0.00023) 가능성이
  높다. 이 노트는 두 값 모두로 환산해 제시했고, 결론(온도항 ≫ 분해능항)은 **작은 쪽 값으로도
  성립**하므로 견고하다. 같은 논문의 RI 계수 β는 물리값과 정합한다.
- ⚠ **확인 못함**: §2의 드럼 액주 높이 300 mm는 200 L 드럼 규모의 가정이다. 또한 Stokes 식은
  **묽은 극한**이며 실제 슬러리(고형분 수~30 wt%)에서는 방해침강(hindered settling)으로
  더 느리다 — 계산된 1.3년은 **하한이 아니라 자릿수 지표**로만 읽어야 한다.
- ⚠ **표본 한계**: §5의 폐형식 검증은 **n=2**(pH 3, pH 4)이고 모두 같은 실리카(EB6080)·같은
  세리아·같은 저자다. 입경 스케일링(1/R_s)은 원문 Figure 11에서 "작은 실리카일수록 모델이
  실측과 벌어진다"고 명시했는데, 그 편차의 크기는 그래프 판독이 필요해 이 노트는 수치화하지
  않았다. 스케일링은 **방향만** 채택했다.
- ⚠ **이식 금지**: §3의 "7일"은 FA/O 킬레이트 + H₂O₂라는 **특정 조합**의 수명이다. 쉘프라이프는
  조성 고유값이지 CMP 슬러리 일반의 상수가 아니다. 반대로 §3.1의 **설계 규칙**(반응쌍 공존
  여부가 판정을 정한다)은 조성 독립적이라 이식 가능하다 — 숫자가 아니라 논리를 옮겨야 한다.
- **좋은 소식 하나**: §3.1 코드가 보여주듯 5개 QC 지표가 **동시에** 같은 방향으로 움직였다.
  즉 실무에서는 값싼 지표(점도·pH) 두 개만 인라인으로 붙여도 이 종류의 화학 열화는 놓치지
  않는다. 단 이 완전분리는 한 연구실 한 계에서의 결과이며, 팹 규모 로트 간 재현성
  (프로브 드리프트·온도)은 별개 문제다.

## 9. sim/에 대한 시사점 (코드는 건드리지 않음 — PROFILE.md 구현 요청으로 기록)

1. **슬러리 팩에 "나이(age)"와 "블렌딩 이력"이 없다.** 현재 `abrasive_d99_nm`·`aggregate_ratio`는
   제조 시 값이다. 최소한 (보관일수, 희석배율, 희석액 종류, 혼합비) 4개 필드가 있어야
   §2~§5의 어떤 항도 모델링할 수 없다는 사실이 드러난다.
2. **쉘프라이프는 min() 게이트로 쓰는 것이 정직하다.** 세 시계의 폐형식을 다 만들 근거는 없다.
   `expired = age_days > shelf_life_days`(조성별 상수, 문헌이 있으면 그 값) 정도가 현재
   근거로 지지되는 최대치다. 7일 같은 값을 전 팩 공통 상수로 박으면 안 된다(§8).
3. **혼합비는 선형이 아니라 절벽이다.** 만약 MAS/2액형 팩을 넣는다면 성능을 혼합비의 선형
   함수로 두면 틀린다 — `임계비까지의 거리`를 드라이버로 삼아야 한다(§5 식 (15)).
4. **QC 계측 모델을 만든다면 분해능이 아니라 온도항이 지배 파라미터다**(§6.2).

## 10. 자기시험
→ [[../../agents/slurry-colloid/EXAMS.md]] Lv2-2 문항 참조.
