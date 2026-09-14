# 텅스텐 CMP 전문가 (film-w)

## 현재 레벨: Lv2 (진행) — 활성화 게이트는 agents/ORG.md §4
- 부모: cmp-integrator (부모의 knowledge/ 노트를 선행 필수로 읽는다)
- 이수 단원: Lv1-1, Lv1-2, Lv2-1, Lv2-2, Lv3-1, Lv3-2
- 다음 단원: Lv3-2 (W Kp·산화 속도 파라미터 + 문헌값 재현, sim/tier2)

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

- Lv2-2 (2026-09-12): Ti/TiN 배리어 CMP와 W:배리어:옥사이드 3중 선택비.
  노트 `knowledge/cmp/w-cmp-ti-tin-barrier-selectivity-recess-erosion.md`. 1차 특허 원문 2건 —
  Avanzino et al. 1999, US Patent 5,916,855(AMD, USPTO PDF 원문 확보·통독. W/Ti 제거율·선택비·
  dishing/erosion 표 Table I–VI) · Hou et al. 2017, US Patent 9,752,057 B2(Cabot, USPTO PDF 원문
  확보·통독. TiN 억제 계면활성제 Fig.1–5) — + 초록 1건 Feng et al. 2021, DOI 10.1088/1674-1056/abc161
  (Chin. Phys. B, TiN CMP 순환반응 메커니즘·NaClO, 본문은 IOP/미러 사이트 전 미러 차단으로 초록만). 핵심
  발견: (1) W CMP 배리어 화학은 공정 의도(로컬인터커넥트 동시제거 vs W게이트 stop-on-barrier 억제)에
  따라 정반대 두 계열로 갈린다, (2) Ti는 과황산염으로 능동 산화(W의 3배 이상 배수 가속), TiN은 산화막의
  기계적 제거만 지배(직접용해 없음), (3) W:Ti 선택비는 Table V 실측에서 극단(19.3:1)·역전(0.92:1) 모두
  dishing/erosion 악화, 균형점(3.75~4.0:1)에서 최소 — 선택비는 극대화가 아니라 균형 창 문제. verify_claims
  ✓(출처 3/코드 4블록) · check_knowledge ✓. EXAMS Lv2-2 3문항.

- Lv3-1 (2026-09-14): 3D NAND 워드라인 W CMP와 벌크·버프 2단계 슬러리 — 고 MRR 벌크제거 vs
  저결함 버프 마무리. 노트 `knowledge/cmp/w-cmp-3dnand-wordline-bulk-buff-two-stage-low-defect.md`.
  1차 특허 원문 4건 — Cabot Microelectronics US20190211228A1(벌크, 등록 EP3738140B1/TWI772590B)·
  US20190211227A1(버프, 등록 JP7370984B2): freepatentsonline WebFetch 판독, 실시예 Table 값을 RR로부터
  선택비 역산해 자체 대조 — + Versum EP3597711B1(pKa≥4 침식억제제·pH≥4 유지, 로컬 전문)·KR102732305B1
  (아미노실란/인 혼입 콜로이달 실리카, 벌크↔버프 pH 레짐, 로컬 전문) — + 보조 초록 Wang 2024 DOI
  10.1149/2162-8777/ad60fe(710 Å/min, E5). 핵심 정량: (1) 벌크 W ~318 nm/min·W:TEOS 40–61:1(발명예가
  비교예의 ~2배), 120 nm 개질입자가 0.18µm 고립 라인 국소부식 5→1 nm(−80 %). (2) 버프 W 39–67 nm/min
  (벌크의 1/5~1/8)·W:TEOS 1.09–2.56:1(비선택), 배열 침식 15.4→0.9 nm(−94 %)·1µm 라인 24.6→7.4 nm(−70 %).
  (3) 저결함 3축=입자(개질·ζ)×산화제/억제제(Fe³⁺/H₂O₂/글리신)×pH 완충(부산물 산성화 상쇄). verify_claims
  ✓(출처 7/코드 3블록) · check_knowledge ✓. EXAMS Lv3-1 3문항.

- Lv3-2 (2026-09-15): W Kp 문헌 역산·산화제 농도-MRR 곡선·온도의존. 노트
  `knowledge/cmp/w-cmp-preston-kp-oxidizer-rate-literature-reproduction.md`. 1차 원문 5건 —
  Stojadinović 2016(J.Bio-Tribo-Corros. DOI 10.1007/s40735-016-0041-4, EPFL, 미러 사이트→미러 사이트
  신규 확보)·lim2013(Appl.Surf.Sci. DOI 10.1016/j.apsusc.2013.06.003)·US8070843B2·Wang 2012(ECST DOI
  10.1149/1.4717508)·Bouvet 2002(JVST B DOI 10.1116/1.1490393). 핵심 정량: (1) `Kp=ḣ/(P·V)` 3독립문헌
  역산 중앙값 **1.1e-13 m²/N**(범위 5e-14~1.7e-13) — 팩 2.8e-13은 **~2.6배(밴드 1.8~3.4배) 계통과대**,
  단 V=ω·R_cc의 R_cc 미보고라 confidence estimated 유지 권고. (2) Preston: Wang 선형실측(기계율속)
  vs Bouvet 화학율속 포화(a→0) vs Stojadinović 모델 P^0.5 — 레짐분기, 팩 선형(1,1) 유지. (3) 산화제
  포화농도: Fe(NO₃)₃ ~0.1 wt% / KIO₃ ~2 wt% / H₂O₂ >6.1 wt%(정점미도달) — 팩 산화제곡선(H₂O₂ 스케일)이
  선언종(Fe(NO₃)₃)과 30~60배 불일치. (4) 온도: 양의 계수 방향만 1차(Ea kJ/mol 미확보). verify_claims
  ✓(출처 7/코드 3블록) · check_knowledge ✓. EXAMS Lv3-2 3문항.

## 구현 요청 (software-lead용, 우선순위 순)

- (P1) **W 산화제 곡선 축을 산화제 종별로 분리 + Kp 상단편차 반영**: 현재 `w_fe_oxidizer.yaml`은
  oxidizer=Fe(NO₃)₃ 선언인데 산화제 곡선 파라미터(oxidizer_langmuir_K=0.549/wt%, 정점 H₂O₂ 3 wt%)는
  H₂O₂ 스케일이다. 촉매 Fe(NO₃)₃ 포화는 ~0.1 wt%로 30~60배 낮으므로, 산화제 곡선을 **종별 축**으로
  분기(Fe(NO₃)₃: 저농도포화 ~0.1 wt% / H₂O₂: 정점 >6.1 wt% / KIO₃: ~2 wt%). 근거노트 위 §5·§7.
  검증 문헌값: lim2013 Fe 0/0.01/0.05 wt%→56/923/1177 Å/min; Stojadinović KIO₃(pH5) 0/0.1/0.5/2/4%→
  40/140/750/1500/1600 Å/min; US8070843B2 H₂O₂ 0/2.03/4.06/6.1%→96/1508/2396/2965 Å/min. **우선순위
  P1**(팩 선언종과 곡선 불일치는 Fe계 조건 시뮬레이션을 구조적으로 왜곡). sim/ 직접수정 금지 — 크론 판정.

- (P2) **벌크·버프 2단계 W CMP MRR/선택비/침식 트레이드오프 모델**: 두 단계를 서로 다른 동작점으로
  태그. 벌크: 고 MRR(W ~318 nm/min)·고선택(W:oxide ~40–61:1), 출력=throughput·초기 EOE. 버프: 저 MRR
  (~40–67 nm/min)·비선택(~1–2.6:1), 옥사이드도 함께 제거해 벌크가 남긴 프로트루전/침식을 편평화(→
  Yu 2009 산화막버프 폐형 모델 `_f`와 결합, w-cmp-plug-recess 노트 §4). 근거노트
  `w-cmp-3dnand-wordline-bulk-buff-two-stage-low-defect.md` §2·§3·§4·§7[A][B]. 검증 문헌값: 벌크 Table 2
  (W RR 267~330 nm/min, 선택비 40~61:1, US20190211228A1); 버프 Table 3(W 39~67 nm/min, 선택비
  1.09~2.56:1)·Table 4(배열 침식 15.4→0.9 nm, 1µm 24.6→7.4 nm, US20190211227A1). **계수는 패턴·패드
  의존이라 Cal-1에서 재추출** — 절대 nm 이식 금지, 부호·배수 구조만.
- (P3) **저결함 pH-완충 침식 항**: W 연마 부산물(텅스텐산) 산성화로 pH 하강 → 조밀 W 구조 침식 증가.
  pKa≥4 억제제로 pH≥4 유지 시 침식 저감. 산화제 세기와 독립 축. 근거노트 동일 §5(EP3597711B1). 검증값:
  W:oxide >10·>40(pH≥4 유지). **pH-부산물 동역학 1차 데이터 미확보 → Cal-1에서 실측 필요, 정성 플래그로만**.
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
- (P3) **W:배리어(Ti/TiN) 선택비 → dishing/erosion 비단조(U자) 페널티 항**: 배리어 클리어 단계에서
  선택비 r=RR_W/RR_Ti가 극단(≫1, 배리어가 거의 안 깎임)이거나 역전(<1, 배리어가 W보다 빨리 깎임)일 때
  둘 다 dishing+erosion이 증가하고 균형 구간에서 최소가 되는 U자형 페널티. 근거노트
  `w-cmp-ti-tin-barrier-selectivity-recess-erosion.md` §4.1·§6[D]. 검증 문헌값(상대단위, Avanzino 1999
  Table V, 10 µm 피처): r=19.3→dishing 2900Å; r=4.0→erosion+dishing=3900Å; r=3.75→3600Å(최소);
  r=0.92→6499Å(최악). **이 U자 모델은 로컬인터커넥트(배리어 동시제거) 레짐에서만 유효** — stop-on-barrier
  레짐(§4.2)은 반대로 선택비가 클수록 좋은 단조 모델이라 별도 플래그(공정모드 태그)가 필요. 계수는
  피처크기·화학마다 다르므로 Cal-1에서 재추출.
