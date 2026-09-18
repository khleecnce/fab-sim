# 종말점 검출 전문가 (tool-endpoint)

## 현재 레벨: [대기] — 활성화 게이트는 agents/ORG.md §4
- 부모: cmp-integrator (부모의 knowledge/ 노트를 선행 필수로 읽는다)
- 이수 단원: Lv3-2
- 다음 단원: Lv4 (모델 개선 제안)

## 역할
광학·모터전류·와전류 EPD 원리와 신호 해석, 종말점 → 제거량 역산

## 선행 지식 (부모에게 상속)
- [[../../knowledge/equipment/cmp-tool-architecture]]

## 실데이터 책임 (ORG.md §7.3)
EPD 트레이스 실데이터 스키마 + 역산 보정

## 레벨 정의
Lv1 학부지식 → Lv2 대학원/리뷰논문 → Lv3 최신논문 추적 + 모델 구현 → Lv4 모델 개선 제안(교수급)

## 이수 기록
- Lv1-1 EPD 원리별 비교(광학/모터전류/와전류) — 2026-09-10. 지식노트
  [[../../knowledge/equipment/epd-optical-motor-friction-eddy-current-comparison]]
  (check_knowledge.py / verify_claims.py 통과). EXAMS.md 3문항 추가.
- Lv1-2 신호 처리: 노이즈·필터·알고리즘·오버폴리시 제어 — 2026-09-10. 지식노트
  [[../../knowledge/equipment/epd-signal-processing-filtering-overpolish]]
  (check_knowledge.py / verify_claims.py 통과). EXAMS.md 3문항 추가.
- Lv2-1 막질별 EPD 적합성과 한계(투명막·다층) — 2026-09-11. 지식노트
  [[../../knowledge/equipment/epd-film-type-suitability-transparent-multilayer-limits]]
  (check_knowledge.py / verify_claims.py 통과). EXAMS.md 3문항 추가. 신규 출처:
  Lai 2001 MIT thesis Ch.6(eq6.10 면적분율 반사율), US4293224(λ/2n 간섭 모호성),
  An NCCAVS 와전류(측정범위 550–7000Å). 구현요청 없음(모델 아닌 한계 분석).
- Lv2-2 EPD 트레이스 → 제거량·잔막 역산 방법 — 2026-09-12. 지식노트
  [[../../knowledge/equipment/epd-trace-removal-remaining-thickness-inversion]]
  (check_knowledge.py / verify_claims.py 통과). EXAMS.md 3문항 추가. 핵심: 간섭 프린지
  카운팅은 절대두께는 몰라도 "변화량(제거량)"은 무모호(US4293224 서론 재해석) — Lai(2001)의
  면적분율 반사(단조함수)는 원리상 카운팅 불가. 모터전류/마찰/반사는 "시각"만 주므로
  Preston $RR$을 곱해야 제거량이 나옴([[../../knowledge/cmp/preston-luo-dornfeld-mrr]] 연결).
  오버폴리시 예산은 필터지연분(~19nm, Lv1-2 재사용)보다 저다운포스 잔막마진(Tian 2023,
  100~200nm)이 5~11배 커서 지배적임을 수치로 확인. 와전류 정량 교정식은 문헌 미확보로
  솔직하게 미검증 처리(IEEE TIM 2022 논문 발견했으나 OA/미러 사이트 모두 실패).
- Lv3-1 최신 리뷰: ML 기반 EPD, 인시츄 계측 통합 — 2026-09-15. 지식노트
  [[../../knowledge/equipment/epd-ml-statistical-insitu-metrology-integration]]
  (check_knowledge.py / verify_claims.py 통과, 출처 8건 DOI/특허 실존검증). EXAMS.md 3문항 추가.
  신규 출처: BenZakour&Taleb 2012(DWT+SPRT, var vs CV 231/202검출점), BenZakour 2012(PCA-웨이블릿
  T² 378s 정확검출), Rothe 2025(fPCA+커널릿지 5-zone 압력 대리모델, ms급), Nabil 2021(하이브리드
  특징선택 VM), Helu-Chien-Dornfeld 2014(AE EPD, 마찰보다 10s조기·5%오버폴리시 방지·FFT
  endpoint frequency), US10478937B2(Applied Materials AE 도파관+FFT+삼각측량 다중센서 특허).
  핵심: ML/통계는 필터·임계의 최적화·자동화일 뿐 물리 실패모드(투명막·패턴밀도·드리프트)는
  못 넘음. 정량 재현 4블록(CV>분산 민감도, PCA 5성분 99%+T²타이밍, 10s/5% 자기일관성+Preston
  환산 38nm, fPCA 5성분 재구성 상대오차<2%) 전부 통과. 말미에 모델 후보 표(입력→출력→문헌성능
  →적용조건) 작성 — Lv3-2 설계 입력.

## 구현 요청
- (Lv3-1) wear_aware_endpoint의 `t_detect` 보정: 센서별 검출지연이 다르므로(AE는 마찰보다
  ~10s 조기, Helu 2014) 센서 종류를 인자로 받아 `t_detect += sensor_lead[sensor]` 형태의
  보정항을 두기를 제안. 근거노트 §5 Block C, 검증 문헌값: AE 조기검출 10s ≈ 38nm(RR=229nm/min).
  우선순위 중(Lv3-2 EPD→제거량 모델과 함께 설계).
- (Lv3-1) 검출 임계는 고정상수가 아니라 **이동블록 데이터에서 갱신**하는 구조를 제안(드리프트
  대응). 근거노트 §1(BenZakour SPRT 블록별 임계갱신)·§4(드리프트 실패모드). 임계 민감도가
  under-polish(조기)↔over-polish(지연)를 가르는 튜닝 파라미터임을 §5 Block B가 규모로 보임.
  우선순위 중.
- (Lv3-1) 구역별 계면압력 VM(fPCA+회귀, Rothe 2025)을 Preston $P$ 항의 구역별 실시간 공급원으로
  두면 wear_aware_endpoint를 균일도-인식으로 확장 가능. 근거노트 §2·§5 Block D(5구역 하중은
  5 fPCA 성분으로 99.9%+ 재구성). 단 문헌 RMSE 구체값 미확보 — 구현 시 자체 캘리브레이션 필요.
  우선순위 하(장기).
- sim/tier2 wear_aware_endpoint(향후 Lv3-2 대상)가 "검출시각→제거량" 환산을 붙일 때
  `removed = RR*(t_detect + t_overpolish)` 골격을 쓰고, `t_overpolish`를 (i) 필터지연항
  (Lv1-2 §3 공식 재사용)과 (ii) 공정 안전마진항(막질별 상수, 이 노트 §5)으로 분리해서
  넣기를 제안한다 — 두 항의 물리적 기원이 다르므로 하나의 튜닝 상수로 뭉치면 안 된다.
- Lv3-2 EPD 신호 → 제거량 모델 명세 — 2026-09-19. 지식노트
  [[../../knowledge/equipment/epd-trace-to-removal-model-spec]]
  (verify_claims 4블록 통과·출처 9건 실존, check_knowledge 통과). EXAMS.md Lv3-2 3문항 추가.
  신규 출처: Xu et al.(2010, J.Semicond, μ 0.4–0.7 실측·Cu→Ta innovation<0·Chebyshev 3S 임계·검출오차
  식17 ΔT=|T/d̄|), Headley et al.(2019, ECS JSS, W/ILD COF 실측·boundary vs mixed lubrication·oxide RR∝COF
  선형), US7078894(Ebara 특허, 저항성분 1000Å→0 substantially linear·Cu 7MHz/Ta 180MHz·교정곡선 룩업),
  Wang et al.(2023, IEEE TIE, 선형범위 24–2095nm·종점 100–180nm — 초록 E5). 핵심: 마찰/모터전류는 시각만
  주어 검출오차 ΔT가 잔막오차 δh=RR·ΔT로 직결(불확실성 지배), 간섭은 λ/2n 두께직접, 와전류는 저항성분
  극박막 선형+룩업. Fresnel 단층 무흡수 R(d,λ,n) 폐형식으로 633nm·SiO2 λ/2n=216.8nm 재현.

## 구현 요청 (Lv3-2 — sim/tier2, wear_aware_endpoint 확장; 구현은 소프트웨어 부문)

- **`epd_trace_to_removal(trace, sensor, h0, RR, calib=None) → (t_ep, removed, h_remain, sigma_h)`**
  신규 함수. process_time.py/wear_aware_endpoint.py의 제거량 적분은 **재구현 금지, 그대로 호출**하고
  앞단(트레이스→t_ep)과 불확실성 전파만 얹는다. 근거노트 §1·§5.
  - friction/motor_current 경로: (i) 안정구간 표본표준편차 S로 임계 T=3S(단측, 하강방향), (ii) trailing
    이동평균이 임계 이탈하는 t2 검출, (iii) t_ep=t2−|T/d̄| (Xu 식17, d̄=전이 하강기울기), (iv)
    removed=RR·t_ep, **sigma_h=RR·ΔT**. 검증문헌값: μ대역 0.4–0.7(Xu Fig6b), Cu→Ta 방향 음(식16).
  - optical_interf 경로: 프린지 카운트 N → removed=N·λ/2n+δ (Lv2-2 §2). 검증: 633nm·SiO2 주기 216.8nm.
  - eddy 경로: 참조 교정곡선 룩업 d=g⁻¹(signal). 유효범위 24–2095nm(Wang2023) / ≤1000Å 저항성분 선형
    (US7078894). 하한 수십 nm(An 55nm).
  - **우선순위 상** — Lv3-1의 t_detect 센서리드타임 보정(AE +10s)·블록별 임계갱신 요청과 함께 설계.
- 오버폴리시 추가제거량은 `removed += RR·t_op`로 EPD 후단에 붙이되, 디싱 증가 정량은 형제(film-cu)
  소관이므로 이 함수는 계산하지 않는다(근거노트 §4). 우선순위 중.
- sigma_h(검출오차 전파)는 wear_aware_endpoint의 optimism_pct(드리프트 낙관도)와 **별개 불확실성원**이므로
  따로 리턴한다 — 하나로 합치지 마라. 근거노트 §5 표. 우선순위 중.
