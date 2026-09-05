# 공정 통합 엔지니어 (Process Integrator)

## 임무
장비 운동학(압력·RPM·스윕), 웨이퍼 스케일 균일도(WIWNU), 패턴 의존성(dishing/erosion), 전체 모델 통합을 담당

## 현재 레벨: Lv3 완료 (2/2) → **커리큘럼 전체 이수 완료**
- 이수 단원: Lv1-1, Lv1-2, Lv2-1, Lv2-2, Lv3-1, Lv3-2 (전체 6/6)
- 다음 단원: 없음(커리큘럼 종료) — Lv4(교수급 확장: 최신논문 추적, 다른 에이전트와의
  결합 모델 설계 리뷰)로 전환. Phase 0 우선순위 1번(process-integrator) 완주 →
  다음 회차부터 Phase 0 우선순위 2번(pad-mechanic, 이미 완료) 재확인 후 3번
  slurry-chemist/tribologist 학습 비중 확대 예정.
- 승급 근거: Lv3 단원 2/2(Lv3-1, Lv3-2) 이수 완료 → **process-integrator 커리큘럼 전체 이수**

## 이수 기록
| 날짜 | 단원 | 산출 노트 | 자기시험 |
|---|---|---|---|
| 2026-09-03 | Lv1-1 CMP 장비 구조 | [[knowledge/equipment/cmp-tool-architecture.md]] | 3문항 (EXAMS.md) |
| 2026-09-03 | Lv1-2 운동학: 상대속도 분포 | [[knowledge/physics/cmp-kinematics-rotary.md]] | 3문항 (EXAMS.md) |
| 2026-09-04 | Lv2-1 Preston/Luo-Dornfeld MRR 모델 정밀분석 | [[knowledge/cmp/preston-luo-dornfeld-mrr.md]] | 3문항 (EXAMS.md) |
| 2026-09-05 | Lv2-2 WIWNU: 압력·속도·슬러리 웨이퍼 스케일 결합 | [[knowledge/cmp/wiwnu-pressure-velocity-wafer-scale.md]] | 3문항 (EXAMS.md) |
| 2026-09-05 | Lv3-1 패턴 의존성: dishing/erosion, 밀도효과 모델 | [[knowledge/cmp/pattern-dependent-dishing-erosion.md]] | 3문항 (EXAMS.md) |
| 2026-09-05 | Lv3-2 통합 시뮬레이터 아키텍처 설계·조립 (sim 전체 오너) | [[knowledge/cmp/luo-dornfeld-integrated-cmp-framework.md]] | 3문항 (EXAMS.md) |

## 구현 기여
| 날짜 | 모듈 | 내용 | 검증 |
|---|---|---|---|
| 2026-09-03 | `sim/tier1_empirical/kinematics.py` | 회전식 폴리셔 상대속도장, 운동학 수 µ, 반경별 Preston MRR 프로파일 | self-test 7/7 PASS (Lai Eq.2.12 재현, NU=2\|µ\| 오차<1e-12) |
| 2026-09-04 | `sim/tier1_empirical/preston.py` | Preston(1927) 선형 MRR v0 (Kp·P·V), kinematics.py 속도장 재사용, 반경 프로파일·웨이퍼평균 API | self-test 5/5 PASS (선형성 회귀, 문헌범위 50-1000+ nm/min 대조, WIWNU=0 구조확인, kinematics.py와 교차검증 일치) |
| 2026-09-05 | `sim/tier1_empirical/wiwnu.py` | WIWNU 지표(half-range·σ·3σ), 반경 압력 프로파일(uniform/edge/zoned), preston.py 재사용해 MRR(r) 결합, 존압 민감도 | self-test 5/5 PASS (지표 산술 해석해 대조 rel 6e-5, 속도만 0.195% vs 압력만 14.1%로 압력지배 정량, 존압 +1%p당 ΔWIWNU≈0.49%p) |
| 2026-09-05 | `sim/tier1_empirical/pattern_density.py` | MIT effective-density(가우시안 가중 컨볼루션, RR=K/ρ_eff), step-height 비압축성/압축성/통합(h1=a1+a2exp(-ρ/a3)), overpolish removal-rate diagram 정상상태 d_ss | self-test 9/9 PASS (필터정규화 dev 1e-16, 밀도불변량 제거량×ρ_eff=K·t spread 0, 제거량∝1/ρ_eff, τ회수 0.8→0.8012, d_ss에서 Cu/oxide rate 교차일치) |
| 2026-09-05 | `sim/integration/spatiotemporal_removal.py` | wiwnu_pattern_combined(r×x 정상상태 RR)에 process_time 선형시간적분 조립 → thickness(r,x,t) 필드, Luo-Dornfeld "Preston식=3스케일 인터페이스" 프레임워크 적용 | self-test 4/4 PASS (t 선형성, rho_eff=1 극한 K(r)·t 일치, endpoint_time 배선 항등, 다이-CV 시간불변) |

## 축적한 판단 (에이전트의 "의견")
- 운동학 비균일도는 자전 평균으로 대부분 상쇄된다(50/60rpm에서 edge/center MRR 1.0039).
  → 실측 WIWNU의 주범은 **압력분포**. WIWNU v0 모델은 압력 항 우선.
- 헤드 토크 Q_w = 0 이 동속(ω_w=ω_p) 세팅의 신호 → in-situ 진단·EPD 활용 여지 (아이디어, 미검증).
- JJMIE(2026) 논문의 속도 비균일도 보고값은 자기 수식과 4배 불일치 → 인용 시 주의.

- Preston 이후 모델 계보(Brown/Tseng-Wang/Bulsara/Luo-Dornfeld/Fu/Shi-Zhao/Bastawros)를
  정리한 결과, **입자스케일 모델(P^{1/2} 계열)은 접촉역학(GW, tribologist)과 슬러리
  입도분포(slurry-chemist)가 갖춰지기 전에는 구현해도 의미있는 계수를 못 채운다** →
  Tier1은 Preston 선형식으로 즉시 착수, Tier2로 Luo-Dornfeld형을 유보하는 판단을 확정.

- WIWNU 지표는 **산업 표준이 없다**(Lee & Boning ICMTS 1999). half-range·σ·3σ가 혼용되고
  값이 정의마다 달라지므로 시뮬레이터는 세 지표를 병기 출력한다(wiwnu.py). 값만 인용 금지.
- WIWNU v0을 코드로 닫음: MRR(r)=Kp·P(r)·V(r) + 지표. 속도만 0.195% vs 압력만 14.1%로
  **압력 지배를 70배 정량화** — "압력이 주범" 판단을 수치로 확정. 남은 자유도는 P(r)의
  물리적 결정뿐이라, pad-mechanic(엣지 굽힘)·equipment(멤브레인/링압)와의 결합 지점이 명확.
- 엣지효과 상쇄 3레버(링압=캐리어압, gap 최소화, 엣지존압 하향)는 문헌 정성결론이며
  절대 민감도(엣지존 +1%p당 ΔWIWNU≈0.49%p)는 압력 프로파일 형상 가정에 종속(미검증).

- 패턴 의존성(Lv3-1)으로 비균일도 그림이 2스케일로 닫혔다: **wafer-scale P(r)·V(r) × die-scale
  ρ_eff(x,y)**. 둘 다 결국 국소압 이야기 — die 안에서는 패드가 raised 영역만 만져(GW/Hertz와
  동일 물리) 국소압이 1/ρ_eff로 증폭돼 RR=K/ρ_eff가 된다. WIWNU v0(압력지배)와 밀도모델은
  같은 뿌리다. dummy fill이 die-level 평탄화 1차 레버인 이유가 여기서 정량적으로 나온다(ρ_eff
  편차 축소).
- Cu CMP의 interaction distance(50–100µm)가 oxide(3–5mm)보다 수십 배 짧다는 Park VMIC98
  실측은 중요한 모델링 함의: **Cu는 die-level 밀도필터보다 feature-level(피치·스페이스) 모델이
  지배적**. oxide처럼 mm 스케일 PL 컨볼루션으로 뭉개면 안 됨. dishing/erosion break point가
  스페이스 ~100µm에 걸리는 것도 이 짧은 스케일과 정합.
- pattern_density.py는 계수(K,PL,τ,a1..a3,dmax,b)를 특성화 마스크 실측으로 뽑는 구조라
  절대 dishing/erosion nm값은 **미검증**. 코드가 검증한 건 모델 내부정합(제거량∝1/ρ_eff,
  d_ss 교차, τ 회수)과 부호방향뿐 — Lv3-2 통합 시 실측/합성 캘리브레이션 레이어 필요.

- **Lv3-2로 커리큘럼 전체 이수 완료.** Luo & Dornfeld(2003) 리뷰를 읽고 "이미 만든 모듈들이
  사후적으로 정확히 이 리뷰가 그리는 3-스케일 통합 아키텍처(Fig.6)에 들어맞는다"는 게
  가장 중요한 확인이었다 — 즉 FabSim의 지식우선(트랙A→트랙B) 개발 순서가 우연이 아니라
  실제 CMP 모델링의 정론적 계층구조(입자/다이/웨이퍼)를 따라간 결과였음. 통합은 재작성이
  아니라 "조립 레이어 하나 추가"로 충분했다(spatiotemporal_removal.py, 새 물리가정 0개).
- GW 접촉모델(입자스케일 Kp 분해)과 wiwnu_pattern_combined(다이×웨이퍼)의 완전 연결은
  의도적으로 유보했다 — Kp가 P(r)의 함수가 되면 6개 기존 모듈의 "kp=상수" 시그니처
  가정이 깨져 회귀 위험이 크다. 이런 리팩터는 Lv4(교수급, 기존 모델 한계지적+개선제안)
  단계에서 별도 설계리뷰를 거쳐 진행하는 게 맞다는 판단.
