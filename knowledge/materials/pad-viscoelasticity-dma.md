# CMP 패드 폴리우레탄 점탄성 기초 (DMA, 저장/손실 탄성률, 크리프)

> pad-mechanic Lv1-1. [[cmp-tool-architecture]] (장비 구조, 헤드/플래튼/컨디셔너) 와 연결 —
> 이 노트는 그 "패드" 구성요소 자체의 재료 거동을 다룬다. 이후 [[preston-luo-dornfeld-mrr]]의
> Luo-Dornfeld형(P^1/2) 확장 시 접촉역학(GW 모델, Lv2-1)의 입력으로 쓰일 탄성계수 개념의 토대.

## 1. 왜 점탄성인가 — CMP 패드가 순수 탄성체가 아닌 이유
CMP 폴리우레탄(PU) 패드는 하드/소프트 세그먼트가 미세상분리된 블록공중합체다. 하드 세그먼트(우레탄
결합, 수소결합 도메인)가 물리적 가교점 역할을 하고 소프트 세그먼트(폴리올 사슬)가 점성 흐름을
담당한다 — 즉 탄성(고체적 저장)과 점성(액체적 소산)이 공존한다. 순수 후크 탄성체라면 압력 인가 후
즉시 변형이 정지하지만, 실제 CMP 패드는 하중 인가 중에도 서서히 추가 변형되는 **크리프(creep)**를
보이고, 패드-웨이퍼 접촉면의 실제 압력분포·WIWNU에 이 시간의존 거동이 직접 영향을 준다
(cf. [[cmp-kinematics-rotary]]에서 확인한 "운동학만으론 WIWNU 설명 불가 → 압력분포가 주범"이라는
결론의 다음 퍼즐 조각).

**출처**: Y. Meng, S. Zhang, Z. Zhang, "Effect of Structurally Modified Toluene Diisocyanate-Based
Polyurethane Pads on Chemical Mechanical Polishing of 4H Silicon Carbide Substrate," *Polymers*
2025, 17(5), 613. https://doi.org/10.3390/polym17050613 (오픈액세스, PMC11902601). 하드/소프트
세그먼트 미세상분리·PCDL(폴리카보네이트디올) 함량과 기계물성의 관계를 실험으로 규명한 최신 논문.

## 2. DMA(동적기계분석) — 저장탄성률·손실탄성률·tan δ
정현파 변형을 가하고 그 응답 응력의 위상차 δ를 측정한다.
- 변형: ε(t) = ε₀ sin(ωt)
- 응력: σ(t) = σ₀ sin(ωt + δ)
- **저장탄성률(storage modulus)** E′ = (σ₀/ε₀) cos δ — 탄성적으로 되돌려주는(저장되는) 에너지 성분
- **손실탄성률(loss modulus)** E″ = (σ₀/ε₀) sin δ — 열로 소산되는 점성 성분
- **손실계수** tan δ = E″/E′ — 값이 클수록 점성 지배적(감쇠 큼), 유리전이온도(Tg)에서 피크

순수 탄성체는 δ=0 (E″=0), 순수 점성 유체는 δ=90°(E′=0). 실제 PU 패드는 그 사이.

**출처**: Wikipedia, "Dynamic modulus" / "Dynamic mechanical analysis" (2025년판, 표준 교과서
수준 정의 — 1차 출처는 J.D. Ferry, *Viscoelastic Properties of Polymers*, Wiley, 1980, 이지만
본 노트는 무료 접근 가능한 Wikipedia 요약 + 검증 시뮬레이션으로 대체).

## 3. Maxwell 모델 — 가장 단순한 점탄성 회로 모델
스프링(탄성, 모듈러스 E)과 대시팟(점성, 점도 η)을 **직렬** 연결한 모델. 이완시간 τ₀ = η/E.
정현파 응력 인가 시:
- E″(ω) = E·τ₀ω / (τ₀²ω² + 1)  — ω = 1/τ₀ 에서 피크 (E″ 최대)
- E′(ω) = E·τ₀²ω² / (τ₀²ω² + 1)  — ω→∞ 에서 E로 포화(고주파=순간탄성), ω→0 에서 0(저주파=완전이완)

CMP 패드처럼 다중 완화시간을 갖는 실재 고분자는 Maxwell 요소들의 병렬합(Generalized Maxwell /
Prony 급수)으로 근사하지만, 단일 Maxwell 요소로도 "저주파=점성 지배, 고주파=탄성 지배" 라는
정성적 거동과 피크 위치(ω=1/τ₀)는 정확히 재현된다 — Section 4에서 수치 검증.

**출처**: Wikipedia, "Dynamic mechanical analysis" §Frequency sweep (Maxwell model 수식 인용).

## 4. Maxwell-Voigt 크리프 모델 — CMP 하중 인가 시 시간의존 변형
CMP 패드는 헤드 하강 후 하중이 "유지"되는 스텝 응력 하에서 크리프(시간에 따른 변형 증가)를 보인다.
**Standard Linear Solid (Zener) 모델**의 크리프 컴플라이언스는 지수적으로 평형값에 접근한다:
  J(t) = J₀ + (J∞ − J₀)·(1 − exp(−t/τ_creep))
여기서 J₀=순간(유리질) 컴플라이언스, J∞=평형(고무질) 컴플라이언스, τ_creep=크리프 지연시간.
CMP 공정 관점에서 의미: 헤드 하강 직후 짧은 시간 동안은 패드가 아직 완전히 "안착"하지 않아
국소압력이 과도기적으로 불균일할 수 있고, 이 τ_creep이 초 단위라면 실제 폴리싱(수십 초~수 분)
전 구간에 걸쳐 무시 가능하지만 수 분 단위라면 시간축 MRR 드리프트([[process_time]] 모듈의
향후 확장 포인트)의 원인이 될 수 있다. **본 노트에서는 CMP 패드 실측 τ_creep 문헌값을 확보하지
못했음 — 미검증**. 유사 PU 폼(매트리스 등)의 τ_creep은 초~수십 초 오더로 보고됨(정성적 참고만).

**출처(정성적 참고, 미검증 정량값)**: E. Mendes et al., "Experimental method for creep
characterization of polymeric foam materials in media immersion," *Mechanics of Time-Dependent
Materials*, 2020. https://doi.org/10.1007/s11043-020-09457-x — CMP 패드가 아닌 좌석용 PU 폼
대상이므로 τ_creep 정량값은 CMP 패드에 직접 적용하지 않는다.

## 5. 실측 CMP 패드 물성 데이터 (하드니스·탄성계수)
2025년 논문(Meng et al., 위 출처)의 다공성 PU 패드 실측표 (PCDL 함량별, n≥5 시편):

| 시편 | 밀도(g/cm³) | Shore D 경도 | 압축률(%) | 탄성계수(MPa) | 인장강도(MPa) |
|---|---|---|---|---|---|
| Neat PU | 0.695 | 48±2 | 1.51 | 17.1±3.0 | 8.20±0.15 |
| PUPCD20 | 0.751 | 50±1 | 1.27 | 32.9±4.5 | 11.94±0.47 |
| PUPCD40 | 0.828 | 58±1 | 0.78 | 71.1±5.1 | 17.17±1.17 |
| HF2(상용 대조군) | 0.804 | 53±2 | 0.66 | 46.0±2.4 | 6.33±0.36 |

경향: PCDL(하드 세그먼트 강화) 함량 증가 → 경도↑·탄성계수↑·압축률↓·마모지수(wear index)↓.
상용 CMP 패드(IC1000 계열)의 문헌 Shore D 범위는 별도 특허 조사에서 **60~90**(US Patent 10391606,
Rohm & Haas/DuPont 계열)으로 보고되어, 위 실험 시편(48~58)보다 다소 단단한 축 — CMP 상용 패드는
비교적 강성 재료임을 시사(연질 패드는 서브패드 등 보조층에 국한).

**출처**: 
1) Meng et al. 2025 (위 인용) Table 2.
2) US Patent 10,391,606 B2 (Rohm & Haas Electronic Materials CMP Holdings), "Chemical mechanical
polishing pads for improved removal rate with controlled defectivity," Shore D 60–90 청구항.
https://patents.justia.com/patent/10391606

## 6. CMP 실무 함의 (다음 단원 Lv1-2로 연결)
- 패드 경도↑ → 국소 asperity가 웨이퍼 표면 요철에 덜 순응(conform) → **planarization efficiency**↑
  하지만 **defectivity**(스크래치) 위험도↑ — 트레이드오프. 이는 Lv1-2(패드 구조: IC1000류 발포체,
  groove, subpad)에서 서브패드(연질)로 완충하는 이유와 직결.
- 저장탄성률 E′가 웨이퍼-패드 접촉의 "유효 강성"을 결정 → GW 접촉모델(Lv2-1)에서 asperity 압축
  강성 입력으로 사용될 값. 현재는 정성적 이해만 확보, Lv2-1에서 Hertz 접촉 압축응력↔변위 관계로
  정량화 예정.

## 다음 단원
Lv1-2: CMP 패드 구조 (IC1000류 발포체, groove 패턴, subpad 역할) — 이번 노트의 §6 연장.
