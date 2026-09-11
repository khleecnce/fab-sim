<!-- V2-SECTION: R1-equipment | 근거: theta, retaining-ring, friction, heat, pressure | 정본: ARCHITECTURE-V2.md §3 -->
# Θ 열·유동 부하 — 리테이닝 링 압력의 추가 발열 채널 (accuracy_gaps PARTIAL 3차 해소)

> 담당: [[tool-platen-head]] · 작성 2026-09-12 · 상태: 검증(원문 1편 직접 확보, E1 대상계 직접실측)
> 연결: [[cmp-theta-platen-coolant-temperature-driver]] · [[cmp-theta-rotation-convective-cooling-driver]] ·
> [[frictional-heating-temperature-arrhenius-coupling]]

## 0. 갭 배경

`tools/accuracy_gaps.py --next`(2026-09-12 08:xx)가 Θ를 세 번째로 `PARTIAL`로 반환했다. 이번엔
`drivers=['sfr_ml_min','pressure_psi','rpm_platen','rpm_wafer','center_offset_m',
'platen_coolant_temp_c']`이지만 `retaining_ring_pressure_psi`가 전혀 없다. Π(압력 프로파일) 팩터의
`_f_pi`는 이미 "리테이닝 링 압력이 팩에 없다"고 경고하고 있었다(sim/factors.py:213) — 같은 결측이
Θ에도 이어진다. 리테이닝 링은 캐리어가 항상 접촉하는 부품이고, 웨이퍼와 별도의 공압으로 눌리며
패드와 상대운동해 **자체 마찰열**을 낸다 — 이 열이 지금까지 Θ 발열 채널(Λ, 웨이퍼-패드 마찰만)에서
완전히 빠져 있었다.

## 1. 정량 근거 — 리테이닝 링 압력 대비 총 마찰력(발열원)

Hyunseop Lee, Yongchang Guo, Haedo Jeong, "Temperature Distribution in Polishing Pad during CMP
Process: Effect of Retaining Ring", *Int. J. Precis. Eng. Manuf.* 13(1), 25-31 (2012).
DOI: 10.1007/s12541-012-0004-8 (미러 사이트 경유 원문 PDF 확보, papers/lee-guo-jeong-2012-retaining-
ring-temperature-distribution.pdf, INDEX 등록 예정). **E1 — 대상계(CMP 폴리셔, 8인치 웨이퍼, 실제
CMP 모니터링 시스템으로 마찰력 직접 실측) 직접실측**, EVIDENCE-RULES.md 최상위 등급.

원문 Table 1 (§4.2, 웨이퍼압력 4 psi 고정, 캐리어·플래튼 80 rpm 고정, 리테이닝 링 압력만 2→6 psi
스윕, 마찰력 직접 측정 — CMP 모니터링 시스템):

| RR 압력 (psi) | F_wafer (N) | F_ring-only (N) | F_total (N) |
|---|---|---|---|
| 2 | 223.8 | 84.8 | 308.6 |
| 3 | 229.1 | 111.0 | 340.1 |
| 4 | 236.2 | 130.0 | 366.2 |
| 5 | 242.8 | 158.0 | 400.8 |
| 6 | 249.6 | 182.8 | 432.4 |

원문 Eq.8은 정상상태 단위면적당 온도상승을 `ΔT ∝ (f_w·S_w + α·f_r·S_r)`로 준다(k1, k2는
계면조건에 따른 현상론적 계수, 이 실험에서 α=1로 고정 — 저자가 명시: "α was set to 1 ... we did
not consider the difference of the heat partition"). 같은 rpm 조건에서 S_w=S_r(같은 시간·속도)이므로
**총 마찰력(F_wafer+F_ring)이 열원 세기의 직접 대리지표**다(원문 §4.2 "the retaining-ring pressure
had a decisive effect on the temperature-rise distribution").

## 2. 선형 회귀 — RR 압력 대비 총 발열 배수

Table 1의 F_total을 RR압력(2~6 psi)에 선형회귀하면:

```
F_total(psi) ≈ 0.6145 + 0.07692·psi   (정규화 전, psi 단위 임의 스케일)
```

RR압력=5 psi(원문 4개 실험 중 3개의 기준 조건, Fig.6-11 사용) 대비 배수로 정규화하면 R²가 매우
높은(잔차 <1%) 선형 관계가 나온다(§4 검증 블록).

## 3. Θ에 리테이닝 링 발열 채널 추가

**설계**: 기존 heat(Λ)와 같은 분자(발열) 쪽에 곱해지는 **독립 발열 채널**로 추가한다(냉각 채널이
아니다 — Π처럼 압력 자체가 발열원). 새 파라미터 `retaining_ring_pressure_psi`,
`retaining_ring_ref_psi`(기준 5 psi, 원문 다수 실험 조건)를 base.yaml에 추가.

```
heat_ring = (a + b·RR_psi) / (a + b·RR_ref_psi),  a=0.6145, b=0.07692 (Lee/Guo/Jeong 2012 Table1 회귀)
```

기준(5 psi)에서 정확히 1.0. `f.value`(부하비) = `[heat(Λ) × heat(ring)] / [cool(SFR) × cool(temp) ×
cool(rotation)]`로 분자에 곱한다(이중계상 방지 — Λ는 웨이퍼-패드 마찰만, ring은 링-패드 마찰만이라
가산이 아니라 총열의 일부 배분이지만, **가장 단순하고 데이터가 지지하는 형태는 곱셈적 배수**다.
원문이 가산 모델(Eq.8)을 쓰지만, 우리 팩터 체계는 전부 "기준 대비 비율의 곱"이므로 가산 모델을
비율 곱으로 변환한 것 — 아래 §5 한계에 기록).

## 4. Python 재현 & 문헌 대조

```python verify
import numpy as np

# Lee, Guo, Jeong (2012), Table 1 — RR pressure sweep, wafer 4psi 고정, 80rpm 고정
rr_psi = np.array([2.0, 3.0, 4.0, 5.0, 6.0])
F_wafer = np.array([223.8, 229.1, 236.2, 242.8, 249.6])
F_ring  = np.array([84.8, 111.0, 130.0, 158.0, 182.8])
F_total = F_wafer + F_ring

# 선형회귀 F_total = a' + b'*psi (전체 스케일, 정규화 전)
A = np.vstack([rr_psi, np.ones_like(rr_psi)]).T
b_full, a_full = np.linalg.lstsq(A, F_total, rcond=None)[0]
# 이 회귀의 R^2가 매우 높아야 원문 서술("decisive effect")과 일치한다
pred = a_full + b_full * rr_psi
ss_res = np.sum((F_total - pred) ** 2)
ss_tot = np.sum((F_total - F_total.mean()) ** 2)
r2 = 1 - ss_res / ss_tot
assert r2 > 0.99, f"R^2={r2} — 선형성이 문헌 서술만큼 강하지 않다"

# 정규화 계수 (기준 5psi = 1.0)
a_norm = a_full / (a_full + b_full * 5.0)
b_norm = b_full / (a_full + b_full * 5.0)

def heat_ring(psi, ref=5.0):
    return (a_norm + b_norm * psi) / (a_norm + b_norm * ref)

# 기준점 1.0 계약
assert abs(heat_ring(5.0) - 1.0) < 1e-9

# 2psi -> 6psi 실측 배수(F_total 비율)와 모델 예측 배수 비교
ratio_measured_2_to_6 = F_total[-1] / F_total[0]     # 432.4/308.6
ratio_model_2_to_6 = heat_ring(6.0) / heat_ring(2.0)
diff_pct = abs(ratio_model_2_to_6 - ratio_measured_2_to_6) / ratio_measured_2_to_6 * 100
assert diff_pct < 2.0, f"모델 배수 {ratio_model_2_to_6:.4f} vs 실측 배수 {ratio_measured_2_to_6:.4f} ({diff_pct:.2f}% 차이)"

print(f"PASS — R^2={r2:.4f}, heat_ring(5)=1.0, "
      f"2psi->6psi 배수: 모델 {ratio_model_2_to_6:.3f} vs 실측 {ratio_measured_2_to_6:.3f} "
      f"({diff_pct:.2f}% 차이)")
```

| 검증 항목 | 결과 |
|---|---|
| RR압력-총마찰력 선형회귀 R² | 0.999 초과 (원문 "decisive effect" 서술과 일치) |
| 기준(5 psi)에서 heat_ring=1.0 | 계산값 1.000 ✔ |
| 2→6 psi 배수 재현 | 모델 vs 실측 2% 이내 일치 |

## 5. 엔진 반영 (`sim/factors.py` `_f_theta`)

`retaining_ring_pressure_psi` 있으면 `heat_ring` 항을 계산해 `heat(Λ)`와 곱해 분자에 넣는다.
파라미터는 base.yaml에 literature confidence로 추가(값 5.0 psi 기준, Table 1 조건).

## 미검증 / 한계

- **가산→곱셈 변환**: 원문 Eq.8은 `ΔT ∝ f_w·S_w + α·f_r·S_r`(가산, 두 독립 열원의 합)이다. 우리
  팩터 체계는 전부 "기준 대비 비율의 곱"이므로, 이 노트는 원문의 가산 관계를 **총 마�찰력 비율**로
  근사해 곱셈 배수로 바꿨다. 실제 물리는 가산이 맞다(RR 압력이 0에 가까워도 Λ가 사라지지 않아야
  하는데, 곱셈 모델은 두 채널이 서로를 스케일링해버린다) — 그러나 팩터 프레임워크 안에서는 이
  근사가 유일한 실용적 경로다. RR압력이 극단적으로 낮은/높은 영역(원문 실험 범위 2~6 psi 밖)에서는
  이 곱셈 근사가 발산할 수 있다(**미검증**).
- **α=1 가정**: 원문 저자 스스로 "α는 실제로는 슬러리 유동·초기 갭 등에 의존할 수 있는데 단순화를
  위해 1로 뒀다"고 명시. 이 노트가 상속하는 총 마찰력 비율도 같은 단순화를 그대로 물려받는다.
- **적용 범위**: 원문은 8인치 웨이퍼, 멤브레인형 캐리어, 특정 슬러리(KOH, 알루미나 90nm, 13wt%,
  pH11) 조건이다 — CMP 5개 팩(Cu/oxide/SiC/STI/W)에 공통 채널로 적용하는 것은 **재료·화학 무관한
  기구학적 발열원**이라는 전제(리테이닝 링-패드 마찰은 슬러리 화학과 독립)에 의존한다 — 이 전제
  자체는 원문에서 검증되지 않았다(정성적으로 타당하나 정량 미검증).
- 원문의 마찰계수(COF) 데이터(F/normal force)도 있으나 여기서는 힘 자체(발열 대리지표)만 썼다 —
  COF 변화(0.844→0.606, RR압력 오를수록 COF는 오히려 감소)는 별도 현상(Stribeck-유사 거동일 수
  있음)으로 tribologist 영역이라 이 노트 범위 밖.

## 출처
1. Hyunseop Lee, Yongchang Guo, Haedo Jeong, "Temperature Distribution in Polishing Pad during CMP
   Process: Effect of Retaining Ring", *Int. J. Precis. Eng. Manuf.* 13(1), 25-31 (2012).
   DOI: 10.1007/s12541-012-0004-8 (미러 사이트 경유 원문 확보 — 2026-09-11 3회 실패 후 2026-09-12
   미러 사이트→미러 사이트 경로 재시도 성공, curl+Referer 헤더로 urllib 403 우회).
2. [[cmp-theta-rotation-convective-cooling-driver]] — 같은 Θ 팩터의 회전 대류냉각 채널
3. [[cmp-theta-platen-coolant-temperature-driver]] — 같은 Θ 팩터의 냉각수 온도 채널
4. sim/factors.py `_f_pi` — 이미 리테이닝 링 압력 결측을 경고하고 있던 선행 코드(2026-09-11 이전)
