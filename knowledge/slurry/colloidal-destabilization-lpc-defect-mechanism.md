# 콜로이드 불안정화가 만드는 LPC 꼬리 — 응집 메커니즘과 스크래치 연결고리

> 에이전트: slurry-colloid Lv1-2 | 작성일: 2026-09-12
> [[dlvo-ionic-strength-ph-aggregation-kinetics]] [[../cmp/colloid-zeta-dlvo-slurry-stability]]
> 관련(겹치지 않음): [[../cmp/lpc-scratch-density-tail-correlation]]

## 1. 범위 — 형제 노트와 무엇이 다른가

`knowledge/cmp/lpc-scratch-density-tail-correlation.md`(slurry-abrasive Lv1-2, Remsen et al. 2006)는
"**제조된 입도분포의 꼬리**(대입자 개수, SPOS 계측)가 스크래치와 어떻게 정량 상관하는가"를
다룬다. 이 노트는 한 단계 앞선 질문을 다룬다 — "**콜로이드가 왜/어떻게 불안정화되어 그
꼬리가 생기는가**"다. Lv1-1([[dlvo-ionic-strength-ph-aggregation-kinetics]])의 응집 속도론을
실제 CMP 손상 데이터로 연결하는 것이 이 노트의 목적이며, 두 노트는 서로의 결과를 대체하지
않고 인과 체인의 앞뒤 단계를 채운다: **[이온강도·국소농도변동·전단(Lv1-1 응집속도론)]
→ [대입자/연성응집체 생성, 이 노트] → [LPC 계측치 ↔ 스크래치 상관(형제 노트)]**.

## 2. 1차 문헌 — Basim & Moudgil 2002 (University of Florida)

**Basim, G.B., Moudgil, B.M. (2002). "Effect of Soft Agglomerates on CMP Slurry Performance."
Journal of Colloid and Interface Science, 256(1), 137–142. DOI: 10.1006/jcis.2002.8352.**
미러 사이트(미러 사이트→미러 사이트)에서 전문 확보
(`papers/basim2002-jcis-soft-agglomerates-cmp-slurry.pdf`, fitz로 텍스트 추출,
`papers/basim2002-jcis-soft-agglomerates-cmp-slurry.pdf.txt`, 502줄, 표·본문 전부 확인).

### 2.1 실험 설계
0.2 µm 단분산 sol-gel 실리카(pH 10.5, 12 wt%) 기준 슬러리에 "연성 응집체(soft agglomerate)"를
3가지 독립 경로로 만들어 섞었다:
1. **건식 응집(dry aggregation)**: 초음파 분산을 불완전하게 걸어 건조 분말 응집체를 잔류.
2. **고분자 가교 플록(polymer flocculation)**: PEO(분자량 8×10⁶, 0.5 mg/g) 가교.
3. **염 응결(salt coagulation)**: NaCl 0.2/0.4/0.6 M 첨가(이 계의 임계응집농도 CCC=0.25 M,
   Coulter LS230 입도분석으로 저자들이 직접 측정).

이후 IC1000/Suba IV 패드, 7.0 psi, 150 rpm, 실리카-실리카 연마(SiO₂ PECVD 박막)로 연마하고
MRR·표면 RMS 거칠기·AFM 최대표면변형(Rmax, 결함 심도 대리지표)을 측정했다.

### 2.2 핵심 정량 결과 (원문 Table 1 그대로)
| 조건 | 평균 입경 | MRR (Å/min) | RMS (nm) | Rmax (nm) |
|---|---|---|---|---|
| 기준(베이스라인) | 0.2 µm | 3800±410 | 0.85±0.24 | 25 |
| 건식 응집 | 0.77 µm | 4300±470 | 2.66±0.98 | 65 |
| PEO 플록(미분산) | 5.82±0.67 µm | 3680±260 | 1.14±0.19 | 45 |
| PEO 재분산(대조) | ≈0.2 µm | 3090±240 | 0.77±0.09 | 20 |
| NaCl 0.2 M(CCC 미달) | 0.2 µm(불변) | 4650±260 | 0.86±0.28 | 50 |
| NaCl 0.4 M | 1.3 µm | 5210±500 | 1.70±0.86 | 100 |
| NaCl 0.6 M | 3.6 µm | 6000±120 | 2.76±1.01 | 120 |

## 3. 핵심 발견 — "입도분포가 그대로인데 결함이 늘어난다"

NaCl 0.2 M은 이 계의 CCC(0.25 M)보다 낮아 **Coulter LS230 벌크 입도분포상 응집이 측정되지
않았다**(평균 입경 0.2 µm 그대로, §2.2 표). 그런데도 Rmax는 기준 25 nm → 50 nm로 **2배
증가**했다. 저자들은 이를 DLVO 장벽의 정량 감소로 설명한다: 상수-전하 가정 하 반발장벽이
염 무첨가 **720 kT → 0.2M NaCl에서 167 kT**로 낮아지며(원문 본문 수치, 계산 세부는 미기재
— **2차 재인용 불가, 원문 수치 자체를 인용**), 국소 입자농도 변동(동적 연마 조건) 구간에서
"일시적(transient)" 연성 응집체가 생성·재해리되어 평균 입도에는 안 잡히지만 연마 중 국소
손상을 만든다는 것이다.

이것이 시사하는 바: **벌크 광산란 입도계(Coulter LS230 같은 volume-weighted 계측)는 LPC
꼬리에 둔감하다** — 부피가중 분포는 미세 주 모드가 지배해 희소한 대입자/일시적 응집체
신호가 묻힌다. 이는 Remsen 2006·Kwon 2023이 쓰는 **개별입자 계수(SPOS/particle-counter)
방식이 bulk PSD보다 LPC tail 검출에 본질적으로 더 적합**한 이유를 설명한다 — 이 노트가
"측정" 방법론 차이에 대해 제공하는 핵심 관찰이다.

## 4. 독립 교차검증 — 스크래치 임계 직경의 수렴 (다른 화학종, 다른 실험실)

[[dlvo-ionic-strength-ph-aggregation-kinetics]] §6에 정리한 **Kwon et al. 2023**
(doi:10.3938/NPSM.73.920, CMP 세리아 슬러리, 입경 140 nm)은 LPC 계수 임계 직경을
**≥0.7 µm**로 잡았고, `knowledge/cmp/lpc-scratch-density-tail-correlation.md` §2.2의
**Remsen et al. 2006**(doi:10.1149/1.2184036, 퓸드실리카 슬러리)은 스크래치-LPC 상관의
Y절편이 0이 되는 임계 직경을 **0.68 µm**(실리카 등가)로 보고한다. **세리아와 퓸드실리카라는
서로 다른 화학종·서로 다른 연구진·서로 다른 측정 목적(전자는 응집 민감도 탐지, 후자는
스크래치 상관 회귀)인데 임계값이 0.68–0.7 µm로 수렴**한다는 것은 우연일 수도 있지만
(n=2, 통계적 검정 불가), "CMP 슬러리에서 서브마이크론 후반대(0.6~0.8 µm)가 스크래치 유발
입자의 공통 경계"라는 정성적 패턴을 두 독립 출처가 지지한다는 점은 기록할 가치가 있다.
**⚠ 미검증**: 이 수렴이 물리적 필연(예: CMP 패드-웨이퍼 간극 또는 접촉역학적 공통 상수에서
기인)인지 단순 우연인지는 본 노트의 두 문헌만으로 결론 내릴 수 없다.

## 5. 재현 코드 — 문헌값 정합성 검증

```python verify
import numpy as np

# --- (1) Basim & Moudgil 2002, Table 1: 평균 입경과 Rmax(최대 표면변형) ---
sizes_um = np.array([0.2, 0.77, 5.82, 0.2, 0.2, 1.3, 3.6])   # baseline, dry-agg, PEO-floc,
rmax_nm  = np.array([25,  65,   45,   20,  50,  100, 120])   # PEO-disp, NaCl 0.2/0.4/0.6M

pearson_r = np.corrcoef(sizes_um, rmax_nm)[0, 1]
# 문헌 본문 주장: "입경만으로는 손상 정도를 못 예측한다 — 응집체 강성(rigidity)이 더 중요"
# (건식응집 0.77um이 PEO플록 5.82um보다 Rmax가 더 큼: 65 > 45)
assert rmax_nm[1] > rmax_nm[2], "건식응집(작은 입경) Rmax가 PEO플록(큰 입경)보다 커야 함"
assert 0.0 < pearson_r < 0.6, f"입경-Rmax 상관이 약해야(강성이 더 중요) 하는데 r={pearson_r:.3f}"
print(f"Pearson r(mean size, Rmax) = {pearson_r:.3f}  (약한 양의 상관 — 입경 단독 예측력 낮음)")

# --- (2) 0.2M NaCl: 벌크 입경 불변인데 Rmax는 증가 (CCC=0.25M 미달, transient 응집) ---
assert sizes_um[4] == sizes_um[0], "NaCl 0.2M은 CCC 미달 — 벌크 평균 입경 불변이어야 함(원문)"
assert rmax_nm[4] > rmax_nm[0], "입경 불변인데도 Rmax는 증가해야 함(문헌의 핵심 발견)"
rmax_increase_pct = (rmax_nm[4] - rmax_nm[0]) / rmax_nm[0] * 100
print(f"NaCl 0.2M: 평균입경 불변, Rmax {rmax_nm[0]}->{rmax_nm[4]} nm ({rmax_increase_pct:.0f}% 증가)")

# --- (3) 원문이 직접 제시한 DLVO 장벽값(상수전하 근사): 무첨가 720 kT vs 0.2M NaCl 167 kT ---
barrier_no_salt_kT = 720.0
barrier_02M_kT = 167.0
barrier_ratio = barrier_no_salt_kT / barrier_02M_kT
assert barrier_ratio > 4.0, f"장벽이 4배 이상 낮아져야 함(원문 수치): ratio={barrier_ratio:.2f}"
# 두 값 모두 전형적 안정성 경험적 문턱(~15-25 kT, Lv1-1 노트 §6)보다 훨씬 높다 ->
# "벌크 DLVO 장벽 기준으로는 여전히 안정"인데 결함은 늘었다 -> 모델 갭(아래 §6)
stability_threshold_kT = 25.0
assert barrier_02M_kT > stability_threshold_kT, (
    "0.2M NaCl 장벽(167kT)은 통상 안정성 문턱(~25kT)을 훨씬 넘는데도 Rmax가 늘었다 "
    "-> 벌크 정적 DLVO 장벽만으로는 이 손상 증가를 설명할 수 없음(정직한 모델 갭)")

# --- (4) 독립 교차검증: Remsen 2006(0.68um, 퓸드실리카) vs Kwon 2023(0.7um, 세리아) ---
d_remsen_um = 0.68
d_kwon_um = 0.7
diff_pct = abs(d_remsen_um - d_kwon_um) / d_remsen_um * 100
assert diff_pct < 5.0, f"두 독립 출처의 스크래치 임계직경 차이가 5%를 넘음: {diff_pct:.1f}%"
print(f"임계직경 수렴: Remsen2006={d_remsen_um}um vs Kwon2023={d_kwon_um}um, 차이 {diff_pct:.1f}%")
```

## 6. sim/factors.py에 대한 시사점 (직접 코딩하지 않음 — 구현 요청으로만 기록)

`sim/factors.py`의 `_f_delta`(Δ 손상 유발도)는 이미 `aggregate_ratio`를 드라이버 후보 키로
받아두고 있으나(L1022) 실제 계산(`val`)에는 쓰이지 않는다(d99만 사용, L1034-1041). 이 노트
§3의 NaCl 0.2M 사례(**입경 불변인데 손상 2배**)는 "입자 크기 지표(d99)만으로는 연성
응집체·일시적 불안정화로 인한 손상 증가를 포착할 수 없다"는 정량적 근거다 — d99 경로와는
**독립적인** 손상 경로가 있다는 뜻이며, 이것이 `aggregate_ratio`가 존재해야 하는 이유다.
구현 요청은 `agents/slurry-colloid/PROFILE.md`에 기록(코드는 건드리지 않음).

## 7. 한계·정직성 표기
- ⚠ **미검증**: §4의 임계직경 수렴(0.68 vs 0.7 µm)은 n=2 독립 출처로, 통계적 유의성을
  주장할 수 없다 — 정성적 일치 기록일 뿐이다.
- ⚠ **미검증**: Basim & Moudgil 2002의 DLVO 장벽값(720/167 kT)은 "상수-전하 가정" 계산이라고
  원문이 명시하나, 계산에 쓴 Hamaker 상수·반경 등 세부 입력값은 원문 본문에 나오지 않아
  이 노트는 결과값만 인용하고 독자 재계산으로 검증하지 않았다(원문 저자의 계산을 신뢰).
- ⚠ **확인 못함**: 실리카-실리카(학술 모델계) 결과가 Cu/W/세리아 등 CMP 양산 화학종에
  그대로 이식되는지는 이 노트의 범위 밖 — 방향성(연성 응집체가 벌크 PSD에 안 잡혀도 손상을
  만든다)만 일반화 가능하다고 본다.
- **Rmax의 물리적 의미**: 원문은 AFM 10×10 µm 스캔의 최대 표면변형으로 정의 — 스크래치
  "개수"가 아니라 "깊이" 계열 지표다. §4 임계직경(LPC 개수 기반)과는 다른 측정축이므로,
  이 노트는 둘을 같은 숫자로 엮지 않고 별개 관찰로 병치했다.

## 8. 자기시험
→ [[../../agents/slurry-colloid/EXAMS.md]] Lv1-2 문항 참조.


## 9. Δ(damage_exponent) 교차확증 - 실리카계 염응집 시리즈 회귀 (2026-09-12 추가, 정확도루프 Δ 갭)

`sim/factors.py::_f_delta`의 `damage_exponent`(기본값 n=3.0)에 대해 [[../cmp/abrasive-d99-scratch-hitachi-us8439995]]
가 세리아 1개 화학종(Hitachi 특허)에서 n약1.44(R^2=0.997)를 회귀했다. 이 절은 같은 논문(Basim & Moudgil
2002, 인용문헌)의 염응집(salt-coagulation) 시리즈를 사용해 실리카 화학종에서 독립적으로 n을
회귀하여 세리아계 결과와 교차확증을 시도한다.

### 9.1 데이터 (원문 Table 1, 그대로)
NaCl 첨가에 따른 평균 입경(광산란 측정)과 표면손상 지표 3점(baseline 포함):

| 조건 | 평균 입경 (um) | RMS 거칠기 (nm) | Rmax (nm) |
|---|---|---|---|
| Baseline (0M) | 0.2 | 0.85 | 25 |
| 0.4M NaCl | 1.3 | 1.70 | 100 |
| 0.6M NaCl | 3.6 | 2.76 | 120 |

(0.2M은 CCC 미달로 입경이 baseline과 동일해 이 회귀에서 제외 - 앞 절에서 이미 별도로 다룬 사례.)

```python verify
import numpy as np

d_um = np.array([0.2, 1.3, 3.6])       # 원문 Table 1, 평균 입경
rms_nm = np.array([0.85, 1.70, 2.76])  # 원문 Table 1, RMS 거칠기
rmax_nm = np.array([25.0, 100.0, 120.0])  # 원문 Table 1, Rmax

d0 = d_um[0]
mask = d_um != d0
lnD = np.log(d_um / d0)

lnR_rms = np.log(rms_nm / rms_nm[0])
n_rms = float(np.sum(lnD[mask] * lnR_rms[mask]) / np.sum(lnD[mask] * lnD[mask]))
pred_rms = rms_nm[0] * (d_um / d0) ** n_rms
r2_rms = 1.0 - np.sum((rms_nm - pred_rms) ** 2) / np.sum((rms_nm - rms_nm.mean()) ** 2)
print(f"실리카 염응집 RMS 회귀: n={n_rms:.3f}, R^2={r2_rms:.4f}")
assert r2_rms > 0.9, f"거듭제곱 적합도 낮음(R^2={r2_rms:.3f})"

lnR_rmax = np.log(rmax_nm / rmax_nm[0])
n_rmax = float(np.sum(lnD[mask] * lnR_rmax[mask]) / np.sum(lnD[mask] * lnD[mask]))
pred_rmax = rmax_nm[0] * (d_um / d0) ** n_rmax
r2_rmax = 1.0 - np.sum((rmax_nm - pred_rmax) ** 2) / np.sum((rmax_nm - rmax_nm.mean()) ** 2)
print(f"실리카 염응집 Rmax 회귀: n={n_rmax:.3f}, R^2={r2_rmax:.4f}")

n_hitachi_ceria = 1.444
n_default = 3.0
assert n_rms < n_hitachi_ceria, "실리카 RMS n이 세리아 n(1.44)보다도 완만해야(더 작아야) 이 절의 결론이 성립"
assert n_rms < n_default and n_hitachi_ceria < n_default, (
    "두 독립 화학종(실리카 RMS, 세리아 스크래치카운트) 모두 n=3.0보다 훨씬 완만해야 한다")
print(f"교차확증: 세리아(Hitachi, 스크래치카운트) n={n_hitachi_ceria} vs "
      f"실리카(Basim, RMS거칠기) n={n_rms:.3f} - 둘 다 코드 기본값 n=3.0보다 훨씬 완만(방향 일치)")
```

### 9.2 해석 - 정직한 한계
- 방향 일치, 절대값은 불일치: 세리아 n약1.44 vs 실리카(RMS) n약0.40 - 둘 다 n=3.0보다 훨씬
  완만하다는 방향은 교차확증되지만, 절대 지수는 화학종/측정지표(스크래치 개수 vs RMS 거칠기)가
  달라 약 3.6배 차이로 수렴하지 않는다. 이는 이전 노트들이 이미 지적한 "지표 축이 다르면
  동일 숫자로 엮으면 안 된다"는 원칙을 그대로 재확인하는 결과다.
- 미검증: 표본 3점(자유도 2)으로 회귀한 n은 통계적으로 취약하다. Rmax 회귀(n약0.60,
  R^2약0.80 - 위 verify 블록에서 계산됨)는 RMS 회귀보다도 적합도가 낮아 지표에 따라 n
  추정치 자체가 갈린다는 사실도 정직하게 남긴다.
- damage_exponent=3.0 기본값 교체는 아직 하지 않는다. 세리아/실리카 두 화학종 모두 방향은
  같지만 절대값이 수렴하지 않으므로, "n을 몇으로 바꿀지"는 화학종별로 분리해야 할 가능성이 높다
  (팩별 damage_exponent를 다르게 주는 것이 정답에 가까울 수 있음 - 아래 9.3 구현 요청).

### 9.3 구현 요청 갱신 (agents/slurry-colloid/PROFILE.md, agents/slurry-abrasive/PROFILE.md 공통)
- 무엇을: `damage_exponent` 기본값(현재 전 팩 공통 n=3.0)을 화학종별로 분리하는 것을 검토.
  세리아계(sti_ceria, sic_ceria_h2o2)는 n약1.44(Hitachi 특허, 스크래치 카운트) 방향 근거,
  실리카계(oxide_silica)는 이 절의 n약0.40~0.60(Basim 2002, 거칠기 지표) 방향 근거 - 단
  둘 다 표본이 매우 작아(각 3~4점) 즉시 코드 상수를 교체하지 않는다. 추가 독립 화학종(Cu/W용
  세리아/알루미나) 문헌이 더 모이면 화학종별 통합 회귀를 다시 시도.
- 검증에 쓸 문헌값: 위 verify 블록(n_rms약0.40, n_hitachi_ceria=1.444, 둘 다 <3.0).
- 우선순위: 낮음(둘 다 방향성 확증 단계, 계수 대체는 표본 확충 후).
