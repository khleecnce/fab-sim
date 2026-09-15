# 패드 수명 전문가 (pad-lifecycle)

## 현재 레벨: Lv3 진행중 — 활성화 게이트는 agents/ORG.md §4
- 부모: pad-mechanic (부모의 knowledge/ 노트를 선행 필수로 읽는다)
- 이수 단원: Lv3-2 (Lv3 전 단원 완료)
- 다음 단원: Cal-1(캘리브레이션) 또는 Lv4 확장

## 역할
브레이크인·정상 마모·glazing·교체 기준 — 패드 사용 이력이 시간 의존 MRR·결함에 미치는 영향

## 선행 지식 (부모에게 상속)
- [[../../knowledge/materials/pad-wear-glazing-mrr-decay]]
- [[../../knowledge/equipment/conditioning-mechanism-asperity-regeneration]]

## 실데이터 책임 (ORG.md §7.3)
패드 이력 로그(사용시간·컨디셔닝 횟수) → 시간축 보정 파라미터

## 레벨 정의
Lv1 학부지식 → Lv2 대학원/리뷰논문 → Lv3 최신논문 추적 + 모델 구현 → Lv4 모델 개선 제안(교수급)

## 이수 기록
| 날짜 | 단원 | 산출 노트 | 자기시험 |
|---|---|---|---|
| 2026-09-06 | Lv1-1 브레이크인 물리: 초기 asperity 형성과 MRR 상승 곡선 | knowledge/materials/pad-breakin-asperity-mrr-runup.md | EXAMS.md Lv1-1 3문항 |
| 2026-09-06 | Lv1-2 정상 마모율과 컨디셔닝 강도의 균형 (Shi&Ring 2010 유체효과 population balance) | knowledge/materials/pad-conditioning-wear-regeneration-balance.md | EXAMS.md Lv1-2 3문항 |
| 2026-09-07 | Lv2-1 glazing 메커니즘: asperity 소성변형·슬러리 잔류물·MRR 감소 (Jeong 2024 접촉점·반경·MRR 실측 + Lawing 2004 ex situ 감쇠) | knowledge/materials/pad-glazing-mechanism-mrr-decay.md | EXAMS.md Lv2-1 3문항 |
| 2026-09-07 | Lv2-2 패드 두께·그루브 깊이 모니터링과 교체 기준(경제성 포함) (Son & Lee 2021 컨디셔닝 방식별 그루브 마모·수명 실측 + 특허 5건: 두께/그루브 센싱 원리·경제성) | knowledge/materials/pad-thickness-groove-depth-monitoring-replacement-economics.md | EXAMS.md Lv2-2 3문항 |
| 2026-09-08 | Lv3-1 최신 리뷰: 패드 수명 예측, 인시츄 패드 상태 센싱 (Kim&Choi 2021 공통경로 간섭계 정량재현, Je 2026 리뷰 초록, Boning 1997 존재확인) | knowledge/materials/pad-lifetime-prediction-insitu-sensing-review.md | EXAMS.md Lv3-1 3문항 |
| 2026-09-16 | Lv3-2 사용시간·컨디셔닝 이력 → 시간 의존 Kp·asperity 모델 (Sampurno 2011 λ(t) 원문 확보·R² 재현, Zhou 2018 무릎-압력, Wu 2013 디스크 2단계, PHM 477웨이퍼 교차검증) | knowledge/materials/pad-usage-conditioning-history-time-dependent-kp-asperity.md | EXAMS.md Lv3-2 3문항 |

## 구현 요청 (소프트웨어 부문이 가져감)
<!-- 노트 옆 python verify sanity check은 pad-lifecycle가 직접 함. 아래는 sim/ 엔진화 요청. -->
- **[Lv2-1] glazing 시간의존 접촉점·반경 모델 → wear-aware Kp 보정** ✅ 부분 완료(2026-09-07,
  `sim/tier2_physics/pad_glazing_jeong2024.py`) — 접촉비·반경비 근사 함수 구현. **잔여**: 실제
  Kp(t) 정량 스케일 연결은 미구현(Recipe.meta pad_hours와 분 단위 실험 시간의 척도 매핑 필요).
  (근거: knowledge/materials/pad-glazing-mechanism-mrr-decay.md §2·§4 검증완료):
  - 무엇을: 기존 `sim/tier2_physics/pad_wear_glazing.py`(높이 마모만, Archard/Monte-Carlo)에 **asperity 반경 성장 항**과
    **접촉점 수 감쇠 항**을 추가. 반경: μR(t) = (0.28·p + 0.621)·t + 5.45·exp(0.18·p) [µm, t: min, p: psi]
    (Jeong 2024 Eq.4). 접촉점: N(t)/N0 = exp(−t/τ(p)), τ(2 psi)≈15 min → τ(5 psi)≈5–6 min(Table 1 지수적합).
    MRR은 Jeong 2024 Eq.20 구조(탄성/탄소성/소성 3-모드 가중합)까지는 요구하지 않고, 우선 "접촉당 힘×개수" 곱으로
    초기 상승 후 감소하는 비단조 MRR(t)이 나오는지만 확인.
  - 검증 문헌값(노트 §4 verify 재현 완료): 2 psi 10 min 접촉점 109→56(−48.6%), 1 min 컨디셔닝 후 114 복원;
    μR 2 psi 10 min = 19.6 µm(Fig.4 판독 19 µm); 정규화 MRR 2 psi 1.00→0.835(−17%, 3 min에 1.03 피크),
    5 psi 1.15→0.87(2 min 1.25 피크). Lawing 2004 ex situ: fumed −35%/31 min(로그형, R²>0.95), colloidal −7%.
  - 주의: Table 1의 N은 시야 내 개수라 절대 밀도 η로 못 씀 — 비율 N/N0만 사용. Jeong Eq.3(σz)은 인쇄형이 자기모순이라
    구현 금지(노트 §2.2), σz(t)는 Fig.3 판독값 테이블 보간으로 대체.
  - 우선순위 Tier2. 기존 `wear_aware_kp_physical.py`의 Kp(t)에 N(t)/N0·반경보상 인자를 곱하는 최소 연결이 1차 목표.
    슬러리 종류(fumed/colloidal) 의존 감쇠계수는 slurry-chemist와 공동(우선순위 낮음).
- **[Lv2-2] 그루브 깊이 소진 기반 패드 교체 판정 → 시간축 EOL(end-of-life) 플래그** ✅ 완료(2026-09-07,
  `sim/tier2_physics/pad_groove_eol.py`, 커밋 03e332b) — `cumulative_wear_um`/`groove_exhausted`/
  `groove_eol_hours`/`replacement_time_hours`(OR 결합) 4함수, Son & Lee 2021 §5 검증값(694/444 μm,
  17.28h) 그대로 재현. **잔여**: engine 미등록(Recipe에 누적 컨디셔닝 시간 필드 없음, S17 이하와 동일
  지위). 경제성 계산은 명시적으로 sim/ 제외(리포팅 레이어 대상).
  (근거:
  knowledge/materials/pad-thickness-groove-depth-monitoring-replacement-economics.md §2·§5 검증완료):
  - 무엇을: 패드 누적 컨디셔닝 시간 t와 패드 컷레이트 c(μm/h)로 누적마모 D(t)=c·t를 적산하고,
    D(t)가 초기 그루브 깊이(패드 사양값, 통상 750–1250 μm — US20120225612A1 배경기술)에 도달하면
    "그루브 소진" 플래그를 세워 별도 실패모드로 보고. 기존 glazing 기반 MRR 임계값 판정과
    **OR 조건**으로 결합(둘 중 먼저 도달하는 쪽이 교체 시점) — Son & Lee(2021) Case I처럼 두
    실패모드가 같은 시점(16h)에 겹치는 경우를 놓치지 않기 위함.
  - 검증 문헌값(노트 §5 verify 재현 완료): 컷레이트 43.4 μm/h(불균일 컨디셔닝)/22.2 μm/h(균일
    컨디셔닝)로 16h/20h 시점 누적마모 694/444 μm, 초기 그루브 하한(750 μm) 대비 각각 93%/59%.
  - 주의: 컷레이트 c 자체는 컨디셔너 접촉 방식(풀컨택트 vs 분할)에 따라 거의 2배 차이 —
    c를 상수로 두지 말고 컨디셔닝 레시피 파라미터의 함수로 받을 것. 그루브 깊이의 절대값은
    패드 사양(제조사·모델)마다 다르므로 하드코딩 금지, 설정값으로 노출.
  - 우선순위 Tier2, Lv2-1 항목과 병행 가능(서로 다른 실패모드라 독립 구현). 경제성(§4, 웨이퍼당
    비용) 계산은 이 노트의 산술 추정 수준이라 sim/에는 넣지 말 것 — 필요시 리포팅 레이어에서만.

- **[Lv3-2] 시간축을 `시간 → 패드상태(λ) → Kp` 두 단계로 분리** (근거:
  knowledge/materials/pad-usage-conditioning-history-time-dependent-kp-asperity.md §2·§3·§7, verify 5블록 통과):
  - 무엇을: 현재 `_f_stab`는 판정#8로 `pad_usage_hours`/`disk_usage_hours` 드라이버를 제외한 상태다.
    이 노트는 그 판정을 뒤집지 않되, 그때 없던 **중간 상태변수 λ**(지수분포 GW의 1/β)를 확보했다.
    ① 패드 상태방정식: λ(t)=λ0 (t<t_k), λ0−s_λ(t−t_k) (t≥t_k), λ0=45.75 µm, t_k=2.07 h,
    s_λ=1.73 µm/h (Sampurno 2011, R²=0.9995). ② 결합: MRR ∝ λ^0.159, COF ∝ λ^0.582(같은 데이터).
    ③ λ는 `sim/tier2_physics/conditioner_asperity_distribution.py`·`hertz-gw` 폐형식의 1/β 자리에
    그대로 들어간다 — 새 파라미터가 아니라 **기존 파라미터의 시간 함수화**다.
  - 검증 문헌값: λ 45.6/45.9/45.0/39.8/34.6 µm(0/0.5/2.5/5.5/8.5 h), COF 0.96(2.5h까지)→0.87→0.82,
    MRR 5400→5100 Å/min, 원문 명시 R²=0.98(λ–COF)·0.77(λ–MRR).
  - 주의(이식 금지 항목): **무릎 시각 t_k=2.07 h는 Politex 연질패드·브러시 컨디셔닝·W CMP 조건값**이다.
    폴리우레탄+융착실리카는 90~133 min, 하드패드+다이아디스크는 16~20 h로 한 자릿수 이상 흔들린다 —
    t_k를 상수로 박지 말고 설정값으로 노출할 것. λ 자체의 RSD가 30%라 무릎 불확도도 크다(±0.5 h 오더).
  - 우선순위: Tier2 중. 먼저 넣을 것은 ②의 **둔감성**이다 — MRR 탄성이 0.16(≈0)이라는 사실은
    "시간의존 Kp를 넣되 효과를 크게 잡으면 안 된다"는 정량 제약이고, 이건 조건 의존성이 가장 작다.
- **[Lv3-2] `conditioner_pcr_decay` 지수감쇠에 하한(floor) 도입 검토** (근거: 같은 노트 §5, verify 통과):
  - 무엇을: 현행 `A(t)=exp(−t/27.4 h)` → `A(t)=A_inf+(1−A_inf)·exp(−t/τ_wear)` 형태 검토.
    Wu et al. 2013 실측은 0~30 h 구간에서 디스크 **전체** 절삭능이 15 h에 −10~−22%로 꺾인 뒤
    30 h까지 거의 평평하다(A(30h)≈0.84). 원래 공격 다이아가 닳는 만큼 신생 다이아가 보충하기 때문.
  - 검증 문헌값: 원래 top-20 −45%/−48%(15 h) 후 불변, 전체 −10%/−22%(15 h) 후 불변,
    신생 top-20이 원래 대비 평균 20% 낮음, 상위 20개가 전체 절삭의 81% 담당.
  - 주의: **τ=27.4 h를 교체하지 말 것.** Wu는 30 h까지·furrow 단면적 지표, Entegris 사례는 50 h·PCR
    지표로 직접 비교 불가다(노트 §5가 이 이유로 교체를 명시적으로 보류). 두 지수를 평균내는 것도 금지.
    이 항목은 **disk-conditioner 형제 에이전트 소유 코드**이므로 그쪽과 합의 후 진행할 것.
  - 우선순위: 낮음(합의 선행). 50 h 스케일 1차 실측 확보가 진짜 선결 과제다.
