# 디스크/컨디셔닝 전문가 (Disk & Conditioning)

## 임무
다이아몬드 디스크 설계(grit 크기·밀도·돌출), 컨디셔닝 압력/스윕이 패드 표면 재생과 수명에 미치는 영향을 모델링

## 현재 레벨: Lv3 완료 -> Lv4 진입(교수급, 상시)
- 이수 단원: Lv1-1, Lv1-2, Lv2-1, Lv2-2, Lv3-1, Lv3-2
- 커리큘럼 전 단원 [x] 이수 완료. 다음: Lv4 확장(최신 논문 상시 추적·타 에이전트 결합모델 설계 리뷰)

## 이수 기록
| 날짜 | 단원 | 산출 노트 | 자기시험 |
|---|---|---|---|
| 2026-09-04 | Lv1-1 컨디셔닝 목적과 메커니즘 | knowledge/equipment/conditioning-mechanism-asperity-regeneration.md | EXAMS.md Lv1-1 3문항 |
| 2026-09-04 | Lv1-2 다이아몬드 디스크 설계 변수 | knowledge/equipment/conditioner-grit-design-space.md | EXAMS.md Lv1-2 3문항 |
| 2026-09-05 | Lv2-1 디스크-패드 절삭 모델 | knowledge/equipment/conditioner-disk-pad-cutting-model.md | EXAMS.md Lv2-1 3문항 |
| 2026-09-05 | Lv2-2 컨디셔닝 레시피(압력·스윕·RPM) | knowledge/equipment/conditioner-sweep-kinematics-pcr-profile.md | EXAMS.md Lv2-2 3문항 |
| 2026-09-05 | Lv3-1 패드 수명 예측·컨디셔닝 최적화 최신연구 | knowledge/equipment/conditioner-asperity-population-balance.md | EXAMS.md Lv3-1 3문항 |
| 2026-09-05 | Lv3-2 컨디셔닝-패드마모 결합모델 구현 | (신규 노트 없음, 기존 conditioner-asperity-population-balance.md §5 설계 그대로 구현) | EXAMS.md Lv3-2 3문항 |

## 구현 기여
<!-- sim/ 모듈 기여 기록 -->
- 2026-09-05: `sim/tier2_physics/conditioner_pcr_decay.py` — 컨디셔너 PCR(cut rate) 지수감쇠
  모델. Entegris(2013) 앵커(50h→16%)로 tau≈27.28h 캘리브레이션. pad_wear_glazing.py를
  재사용(무수정, import만)해 컨디셔너 재생항을 추가한 결합 마모 시뮬레이션 구현.
  self-test 5/5 PASS, pytest 회귀 6건 추가(tests/test_conditioner_pcr_decay.py),
  전체 pytest 62/62 PASS.
- 2026-09-05: `sim/tier2_physics/conditioner_sweep_kinematics.py` — Zheng et al.(2023) Eq.1-9
  사인파 스윕 운동학 모델 재현(4중 회전 합성: 패드자전+팔스윕+디스크자전+입자위치). 대표
  다이아몬드 다수를 균등샘플해 반경별 누적 스크래치 거리(PCA/PCR 상대 프로파일) 히스토그램
  추출. self-test 5/5 PASS(정지상태 항등, 논문 Table1 조건 궤적범위 유효성, 스윕속도 위상
  스케일링, 도달불가반경 PCA=0, 프로파일 비영값 커버리지). pytest 회귀 5건 추가
  (tests/test_conditioner_sweep_kinematics.py), 전체 pytest 67/67 PASS.

- 2026-09-05: `sim/tier2_physics/conditioner_asperity_distribution.py` — Ring et al. Eq.9
  similarity solution의 "좌표 스케일링" 성질만 취해, 기존 conditioner_pcr_decay.py(스칼라
  평균 높이)에 asperity 분포 표준편차 2번째 상태량을 추가하는 최소 확장 구현(전체 PDE
  미이식, Lv3-1 §5 설계 판단 그대로 실행). conditioner_pcr_decay.pcr_decay()를 무수정
  재사용(import만)해 A_eff(t)=A0*PCR(t)/PCR0로 컨디셔너 노화가 분포 폭 축소력도 비례
  약화시키도록 결합. self-test 5/5 PASS(t=0 항등, 이상적 컨디셔너 캘리브레이션 자기재현,
  노화<이상적 순위, 단조 비증가, 정규분포 표본 직접 스케일링 시 이론 exp(2At)비 일치 —
  1차 시도 시 비율 역수 버그 발견해 정정 후 통과). pytest 회귀
  `tests/test_conditioner_asperity_distribution.py` 신규 5건, 전체 **77/77 PASS**
  (기존 72+신규 5, 회귀 없음). A0(similarity 상수)는 문헌에 공개 정량값이 없어(Lv3-1 §6
  fit parameter 한계) "48h 이상적 컨디셔닝→표준편차 절반"이라는 임의 정성 기준으로
  캘리브레이션 — **정량 예측치 아님, 정성 시연용으로 코드·이수기록 양쪽에 명시**.
