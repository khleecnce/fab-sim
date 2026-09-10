# 텅스텐 CMP 전문가 (film-w)

## 현재 레벨: Lv2 (진행) — 활성화 게이트는 agents/ORG.md §4
- 부모: cmp-integrator (부모의 knowledge/ 노트를 선행 필수로 읽는다)
- 이수 단원: Lv1-1, Lv1-2, Lv2-1
- 다음 단원: Lv2-2 (Ti/TiN 배리어 CMP와 W:배리어:옥사이드 선택비)

## 역할
W 플러그·contact CMP — 산화제(H2O2/Fe) 화학, 리세스·코어링, 배리어(Ti/TiN)

## 선행 지식 (부모에게 상속)
- [[../../knowledge/cmp/surface-chemistry-cu-w-pourbaix-passivation]]

## 실데이터 책임 (ORG.md §7.3)
W 실데이터 스키마 + 산화제 농도 의존 보정 파라미터

## 레벨 정의
Lv1 학부지식 → Lv2 대학원/리뷰논문 → Lv3 최신논문 추적 + 모델 구현 → Lv4 모델 개선 제안(교수급)

## 이수 기록
- Lv1-1 (2026-09-10): W CMP 메커니즘 — WO₃ passivation 막 형성-제거 순환, 산화제 종류별 차이.
  노트 `knowledge/cmp/w-cmp-wo3-passivation-oxidizer-kaufman.md`. 1차 논문 2건(Kaufman 1991
  DOI 10.1149/1.2085434 원문 확보 · Lim 2013 DOI 10.1016/j.apsusc.2013.06.003 원문 확보) + 보조 1건
  (Tamboli 1999 초록). verify_claims ✓(출처 3/코드 3블록) · check_knowledge ✓. EXAMS Lv1-1 3문항.
- Lv1-2 (2026-09-10): Fe 촉매 H₂O₂의 Fenton 화학 + 알루미나/실리카 입자 선택.
  노트 `knowledge/cmp/w-cmp-fenton-catalyst-abrasive-alumina-silica.md`. 1차 논문/원전 3건 —
  Buxton 1988 DOI 10.1063/1.555805(•OH 속도상수 원전, 원문 확보: •OH+Fe²⁺ 4.3×10⁸, •OH+H₂O₂
  2.7×10⁷ M⁻¹s⁻¹) · Egan & Kim 2019 DOI 10.1149/2.0311905jss(W contact 입자크기/스크래치, OA 원문
  확보) · Lim 2013(재인용) — + 보조 De Laat & Gallard 1999 DOI 10.1021/es981171v(Fenton 개시/재생
  속도상수, 2차 인용) · Wei 2026 DOI 10.3390/cryst16030179(Fenton CMP, 정성). 핵심 정량: Fe²⁺가
  •OH를 H₂O₂보다 ~16배 빨리 소거 → 과잉 Fe 자기소거 → 촉매 최적점 존재(Lim region I/II 정성
  재현). verify_claims ✓(출처 4/코드 3블록) · check_knowledge ✓. EXAMS Lv1-2 3문항.

## 구현 요청 (software-lead용, 우선순위 순)
- (P2) **Fe 촉매 농도 → W MRR 종형(포화) 모델**: MRR ∝ 생성률(Fe↑ 증가) × 활용률(Fe↑ 자기소거로
  감소). 근거노트 `w-cmp-fenton-catalyst-abrasive-alumina-silica.md` §2.2·§3. 검증 문헌값: Lim 2013
  region I 급증(0.01 wt% 923 Å/min) → region II 완만(>0.1 wt%); Buxton 1988 속도상수비 16. 현재
  sim/에 Fe 농도 의존 W MRR 항 없음 → Cal-1(실데이터 보정)에서 이 함수형이 필요.
- (P2) **산화막 버프 토포그래피 모델(Yu 2009 식 1·2)**: 버프 후 최종 침식 `E_f = E_i − m·L_oxide`,
  프로트루전 `P = n·L_oxide − R`. 입력: 버프 전 침식 E_i·리세스 R(=W CMP 단계 출력), 버프 제거량
  L_oxide. 출력: 프로트루전 P(결함 판정: P가 스펙 초과 시 입자결함 플래그)·최종 침식 E_f. 근거노트
  `w-cmp-plug-recess-coring-keyhole-overpolish-window.md` §4·§7[A]. 검증 문헌값(상대단위, 캘리브레이션
  필요): m=2.64, n=2.58, E_i=3.6, R=1.54(Yu 2009 Fig.9). 결함 급감 임계: 프로트루전 POR 대비 −20%,
  소멸 −50%. m·n은 패턴밀도 의존 → Cal-1에서 밀도별 추출.
- (P3) **심-코어링 정적식각 항 + 키홀 종횡비 위험 플래그**: 플러그에 심/키홀이 있으면(증착 이력 입력)
  코어링 깊이 ≈ SER × t_overpolish(자기제한 안 됨, 추정 모델). SER은 Lv1-1 노트의 정적식각률(억제제로
  하향). 비아 종횡비 AR = 깊이/직경 > ~3이면 키홀 위험 플래그. 근거노트 동일 §3·§7[B][C]. 검증값:
  AR(0.18µm 비아, 0.65µm ILD)=3.6, EM TTF 키홀무/저압키홀 = 46/24 h(Kim 2005). **추정 모델이므로
  코어링률은 캘리브레이션 전까지 정성 플래그로만 사용** — 절대 nm 예측 금지.
