# PHM 2016 Data Challenge — CMP 실장비 데이터

> 2026-09-07 수집·검증. **읽기 전에 §쓸 수 없는 것을 먼저 보라.**

## 출처

- 원본: PHM Society 2016 Data Challenge (CMP tool health tracking)
- 미러: `github.com/akangel0307/PHM-Data-Challenge` (원본 Dropbox 링크는 HTML만 반환)
- 정답 파일 포함: `PHM16TestValidationAnswers/orig_CMP-{test,validation}-removalrate.csv`

## 규모 (실측)

```
MRR 라벨          2,829건 (training 1,981 + validation 424 + test 424)
시계열            25컬럼 × 186파일 (이 중 40파일 = 35.9MB 수집)
조건+MRR 연결     477 웨이퍼
```

지금까지 확보한 문헌 데이터가 최대 59조건이었으므로 **자릿수가 다르다.**

## ⚠ 쓸 수 없는 것 (먼저 읽어라)

### 1. 모든 컬럼이 스케일링되어 있다

공식 문서 원문:
> "Each column of data in Table 1 has been **scaled with hidden values**
> to protect proprietary information."

실측으로 확인:
- `MAIN_OUTER_AIR_BAG_PRESSURE` 0~498 → **psi가 아니다**
- `WAFER_ROTATION` 0~34.88 → **rpm이 아니다**

우리 모델은 `pressure_psi`, `rpm`을 물리 단위로 받아 Preston 식에 넣는다.
스케일값을 그대로 넣으면 숫자는 나오지만 **의미가 없다.**
→ 절대 MRR 예측 검증에는 **쓸 수 없다.**

### 2. 슬러리 조성이 없다

`SLURRY_FLOW_LINE_A/B/C`는 유량만 있고 **각 라인이 무슨 슬러리인지 안 알려준다.**
연마제 wt%, 산화제, 억제제, pH, 입자크기 전부 없음.
→ **화학층(chemistry.py) 검증에는 쓸 수 없다.**

### 3. 압력이 사실상 고정이다 — 이게 가장 중요하다

```
압력 분포: 258(35%) 270(31%) 269(18%) 257(12%)  ← 96%가 257~270
고유값 18개 / 477건
```

양산 라인이라 레시피가 고정이다. 압력을 바꿔가며 실험한 DOE가 아니다.

**압력이 통상범위를 벗어난 16건을 뽑아보면:**
```
압력 118.8 → MRR 142.21
압력 120.0 → MRR 154.21
압력 346.8 → MRR 149.13
압력 483.6 → MRR 149.99      ← 압력 4배인데 MRR 불변
```

전체 상관: 압력 vs MRR **ρ = -0.077** (사실상 무관)

⚠ **이것을 "Preston 식이 틀렸다"는 증거로 쓰면 안 된다.** 폐루프 제어가 걸린
양산 장비에서 압력은 독립변수가 아니다 — 목표 두께를 맞추려 장비가 스스로
조정하는 종속변수다. 교란요인(confounding)이지 물리의 반증이 아니다.
DOE 데이터가 아닌 관측 데이터로 인과를 논하면 안 된다.

## ✅ 쓸 수 있는 것

### 소모품 열화 → MRR 감소

```
드레서 사용량 vs MRR   ρ = -0.489  (전체 477건)
                       ρ = -0.696  (저속군 433건)
```

**우리 모델이 아직 다루지 않는 영역이다.** FabSim에는 패드/드레서 마모에 따른
MRR 시간 변화가 없다. 이 데이터는 그 항을 만들 때 검증 근거가 된다.

노트 `knowledge/equipment/conditioner-grit-wear-scratch-lifetime.md`와 연결된다.

## 정직한 평가

이 데이터로 **할 수 있는 것**: 소모품 열화 모델의 순위 검증, 장비 상태 추정.
이 데이터로 **할 수 없는 것**: 조성 스크리닝 검증(핵심 주장), 절대 MRR 정확도.

즉 **FabSim의 핵심 주장("조성 20개 → 5개 스크리닝")은 여전히 미검증이다.**
이 데이터를 근거로 "실장비 2,829건으로 검증했다"고 IR에 쓰면 첫 질문에서 무너진다.
정확히 말해야 한다: "장비 열화 항은 실장비 477웨이퍼로 순위 검증, 조성 항은 미검증."

## 재현

```bash
python3 validation/fetch_phm2016.py        # 다운로드 + 조인
```
