# 슬러리 안정성 전문가 (slurry-colloid)

## 현재 레벨: [활성, G3 개방 2026-09-12] — Lv1 2/6
- 부모: slurry-chemist (부모의 knowledge/ 노트를 선행 필수로 읽는다)
- 이수 단원: Lv1-1, Lv1-2 (2026-09-12)
- 다음 단원: Lv2-1

## 역할
분산 안정성·응집·POU 필터·쉘프라이프·희석/혼합이 대입자(LPC)와 스크래치에 미치는 영향

## 선행 지식 (부모에게 상속)
- [[../../knowledge/cmp/colloid-zeta-dlvo-slurry-stability]]

## 실데이터 책임 (ORG.md §7.3)
슬러리 로트·보관 이력 데이터 → LPC·결함 예측 잔차 정의

## 레벨 정의
Lv1 학부지식 → Lv2 대학원/리뷰논문 → Lv3 최신논문 추적 + 모델 구현 → Lv4 모델 개선 제안(교수급)

## 이수 기록
- 2026-09-12 Lv1-1 DLVO 심화(이온강도·pH·온도별 응집속도, Smoluchowski) —
  [[../../knowledge/slurry/dlvo-ionic-strength-ph-aggregation-kinetics]].
  핵심: perikinetic 실측/이론 20~45% 범위(Holthoff 1996), CMP 세리아 실측 이온강도 임계전이
  4→10mM(Kwon 2023), 온도의존성은 점도(η(T)) 경로가 지배. check_knowledge/verify_claims 통과.
- 2026-09-12 Lv1-2 LPC 측정과 스크래치 상관관계(콜로이드 불안정화 메커니즘 관점) —
  [[../../knowledge/slurry/colloidal-destabilization-lpc-defect-mechanism]].
  핵심: Basim & Moudgil(2002) 실측 — NaCl 0.2M(CCC 미달)에서 벌크 입도분포 불변인데도
  Rmax 25→50nm 증가(DLVO 장벽 720→167kT, 여전히 통상 안정문턱보다 높음) → 벌크 광산란
  입도계는 LPC 꼬리에 본질적으로 둔감함을 시사. 입경-Rmax Pearson r≈0.33(약한 상관,
  강성이 입경보다 중요). Remsen2006(0.68µm)·Kwon2023(0.7µm) 임계직경 독립 수렴(<5% 차이,
  n=2라 미검증 표기). check_knowledge/verify_claims 통과.

## 구현 요청
- 무엇을: `sim/factors.py`의 `_f_delta`(Δ 손상 유발도)가 `aggregate_ratio`를 드라이버 후보
  키로 이미 받아두지만(현재 코드 L1022) 실제 계산식(L1034-1041)에는 안 쓰고 `abrasive_d99_nm`
  경로만 작동한다. 이걸 "d99 경로와 독립적인 손상 가중치"로 연결하는 항 추가를 검토해 달라
  — 예: `val = (d99/d99_ref)^n * (1 + w * aggregate_ratio)` 같은 곱셈 가중(형태는 미정,
  폐형식 문헌 없음 — 방향성만 제안).
- 근거 노트: [[../../knowledge/slurry/colloidal-destabilization-lpc-defect-mechanism]] §3, §6.
  Basim & Moudgil(2002)의 NaCl 0.2M 사례(평균 입경 불변인데 Rmax 25→50nm, 2배) — d99가 전혀
  안 바뀌는 불안정화 경로로도 손상이 늘 수 있음을 보여주는 1차 실측.
- 검증에 쓸 문헌값: 같은 노트 §5 verify 블록(Pearson r≈0.33, 장벽비 720/167kT). 단, 이 비율을
  팩 전반에 그대로 이식할 정량 근거(계수 w)는 아직 없다 — **1차로는 방향(존재만)만 넣는 것이
  정직함**. 절대 계수를 지어내면 안 됨.
- 선행 필요: 팩에 `aggregate_ratio`를 실제로 채워줄 입력 경로(로트 보관이력·이온강도 추정 등)가
  아직 없음 — Cal-1(캘리브레이션 단원, G2 이후)에서 다룰 범위. 지금 당장은 no-op로 남아도
  구조만 마련해 두는 것을 제안.
- 우선순위: 낮음(입력 경로 부재로 즉시 발동 안 함 — slurry-abrasive의 `abrasive_d99_nm` 스펙
  확보 선행 요청과 동일한 병목 공유).
