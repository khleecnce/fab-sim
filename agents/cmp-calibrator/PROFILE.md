# CMP 캘리브레이션 과학자 (cmp-calibrator)

## 현재 레벨: [대기] — 활성화 게이트는 agents/ORG.md §4
- 부모: cmp-integrator (부모의 knowledge/ 노트를 선행 필수로 읽는다)
- 이수 단원: Lv2-1
- 다음 단원: Lv2-2

## 역할
물리 prior + 고객 실데이터 → 잔차 보정 모델. 소량 데이터 GP/BNN, NPW→PTW 전이, 불확실성, 드리프트. 제품의 핵심 기술

## 선행 지식 (부모에게 상속)
- (없음 — 공개 문헌부터)

## 실데이터 책임 (ORG.md §7.3)
이 에이전트가 §7 전체의 기술 소유자. 각 서브에이전트가 정의한 보정 파라미터를 실제로 피팅한다

## 레벨 정의
Lv1 학부지식 → Lv2 대학원/리뷰논문 → Lv3 최신논문 추적 + 모델 구현 → Lv4 모델 개선 제안(교수급)

## 이수 기록
(크론이 갱신)

- 2026-09-16 Lv1-1 베이지안 캘리브레이션 기초(KOH 프레임워크) 이수.
  노트: `knowledge/calibration/bayesian-calibration-koh-discrepancy.md`.
  1차 출처 2건 원문 PDF 확보·직접 판독(Kennedy & O'Hagan 2001, DOI 10.1111/1467-9868.00294;
  Arendt, Apley & Chen 2012, DOI 10.1115/1.4007390). check_knowledge.py·verify_claims.py
  둘 다 통과. verify 블록 2개(δ의 자유도가 θ 식별을 결정하는 메커니즘의 합성 데이터 재현 +
  Arendt2012 Table 2 문헌값 전사 대조)가 실제로 실행·통과함.
  핵심 결론: `sim/calibration/series_scale.py`의 "계열당 배율 1개" 설계는 KOH의 δ(x)를
  상수 1자유도로 제약한 특수 케이스이며, 이것이 Arendt2012가 제시하는 두 식별성 처방
  중 "δ의 함수공간을 제약"하는 쪽(정보적 사전보다 원칙적으로 더 나은 처방)의 극단형에
  해당한다는 것을 문헌으로 확인.

- 2026-09-16 Lv1-2 소량 데이터 GP 회귀(커널 설계·하이퍼파라미터·물리 기반 평균함수)
  이수. 노트: `knowledge/calibration/gp-regression-small-data-kernel-prior-mean.md`.
  1차 출처 3건(Bachoc 2013 DOI 10.1016/j.csda.2013.03.016 — arXiv 1301.4320v3로 전문
  확보; Hoffer, Geiger & Kern 2022 DOI 10.3390/app12031089 — TU Graz 리포지토리 오픈
  액세스 전문 확보; Kennedy & O'Hagan 2001, 기존 노트에서 확보한 것과 동일 문헌 재인용)
  전부 원문 판독. check_knowledge.py·verify_claims.py 둘 다 통과. verify 블록 2개
  (Bachoc2013의 var(σ²_ML)=2/n Cramér-Rao bound 문헌값을 Monte Carlo로 재현·상대오차
  10% 이내 확인 + 물리 기반 평균함수 GP가 외삽 구간에서 물리모델 예측값으로 회귀함을
  수치로 확인, 영-평균 GP는 대조군으로 0에 붕괴함을 같이 확인)가 실제로 실행·통과.
  핵심 결론: (1) 매끄러움 가정이 강한 커널(RBF)은 그 가정을 뒷받침할 데이터가 부족하면
  실전에서 더 거친 커널보다 못할 수 있음을 Bachoc2013 Table 2/3(n=100 vs n=70)에서
  확인 — CMP 계열 데이터(n<30)에서는 Matérn 3/2가 RBF보다 안전한 기본값이라는 정성적
  근거(정량적 경계는 미검증). (2) ML/CV는 점추정이라 소량 n에서 길이척도가 폭주해도
  그 불확실성이 예측에 반영 안 되는 반면, KOH의 완전 베이지안 틀은 폭주를 넓은
  사후분포로 정직하게 반영한다. MAP의 역할은 1차 문헌 미확보로 미검증 남김. (3) GP
  평균함수를 물리모델 η(x,θ)로 두는 설계는 "평균함수는 보간 성능에 덜 중요하다"는
  Bachoc2013의 결론과 모순되지 않는다 — 그 결론은 보간에 대한 것이고, FabSim이
  물리 기반 평균을 쓰는 목적은 외삽 시 안전망이기 때문. series_scale.py의 배율-고정
  설계가 이 관점에서도 정당화됨을 확인.

- 2026-09-16 Lv2-1 전이학습(NPW 보정치를 prior로 PTW 잔차 학습 — 계층 베이지안)
  이수. 노트: `knowledge/calibration/hierarchical-bayesian-npw-ptw-transfer.md`.
  1차 출처 2건 원문/전문 확보·직접 판독(Qian & Wu 2008, DOI 10.1198/004017008000000082
  — 저자 개인 페이지에서 전문 PDF 36쪽 확보; Perdikaris, Venturi, Royset & Karniadakis
  2015, DOI 10.1098/rspa.2015.0018 — PMC 전문 HTML 확보), Kennedy & O'Hagan 2001은
  기존 [[bayesian-calibration-koh-discrepancy]] 노트에서 이미 판독한 것 재인용.
  check_knowledge.py·verify_claims.py 둘 다 통과. verify 블록 3개: (A)(B) QW2008이
  유도한 ρ0 조건부 사후분포(정밀도가중평균 형태)를 구현해 NPW 사전 정밀도가 커질수록
  사후평균이 사전값으로 수축(v_rho→0에서 오차<1e-3)하고 PTW 표본 수가 늘수록 사후분산이
  단조 감소함을 확인, (C) Perdikaris2015의 AR(1) 다중신뢰도 사후분산식(Var=Σ_Z2+ρ1²Σ_Z1)이
  결합계수 ρ1의 제곱에 비례해 NPW 불확실성을 전파함을 확인, (D) QW2008 Table 3의
  11개 held-out 예측값에서 SRMSE를 직접 재계산해 논문 보고값(8%/15%/9%/7%)과 1.5%p
  이내로 독립 재현.
  핵심 결론: NPW→PTW 전이는 "저비용·다량(LE) vs 고비용·소량(HE) 실험 통합"이라는
  기존 통계학 문헌의 표준 문제로 정확히 대응되며, 전이 강도(수축 정도)를 결정하는
  유일한 손잡이는 NPW→PTW 링크 파라미터(ρ,δ 또는 ρ1)의 사전 확신도이지 NPW 데이터
  양 자체가 아니다.
  **Kennedy & O'Hagan (2000, Biometrika)의 원문 확보 실패** — 저자 홈페이지·
  academia.edu·sci-hub 계열 미러(sci-hub.se, sci.bban.top) 전부 막힘. AR(1) 모형은
  Perdikaris2015가 원 표기 그대로 재도출한 것을 2차 경유로만 확인했다(노트의
  "정직성 표지" 참조).

## 구현 요청

(이번 단원도 `sim/`에 코드를 넣지 않았다. 향후 계층 베이지안 NPW→PTW 전이를
실제로 구현할 때 참고할 사항:
1. Bachoc2013 p.14–15가 보고한 "CV로 상관길이를 추정하면 과대추정되는 경향"과 예측분산이
   수치적으로 깨지는 문제를 고려해, 하이퍼파라미터를 순수 CV 점추정으로 고르는 방식은
   피하고 물리 사전지식으로 상관길이 범위를 제약하거나 완전 베이지안으로 불확실성을
   전파하는 쪽을 권장한다.
2. NPW→PTW 링크 파라미터(척도 ρ, 위치 δ)의 사전분포 폭(vρ, vδ)을 어떻게 정할지가
   구현의 핵심 설계 변수다 — QW2008(식 유도, `knowledge/calibration/
   hierarchical-bayesian-npw-ptw-transfer.md` §2)은 경험적 베이즈로 처리하지만
   그 하이퍼파라미터 자체를 고르는 일반 원칙은 이번 조사에서 확인하지 못했다
   (Lv2-2 불확실성 정량화 단원에서 이어서 확인 필요).
3. FabSim에 패턴밀도·단차별로 NPW-PTW 괴리가 달라지는 경우, `series_scale.py`의
   상수 배율보다 QW2008 식(7)의 "x에 따라 변하는 GP 링크"가 원칙적으로 더 적합할
   수 있으나, 그만큼 더 많은 PTW 데이터가 필요하다는 트레이드오프가 있다.
   우선순위는 낮음 — Lv3-2(sim/calibration 구현) 착수 시점에 재확인 필요.)
