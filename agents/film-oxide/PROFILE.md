# 옥사이드 CMP 전문가 (film-oxide)

## 현재 레벨: Lv2 완료 (4/6) — 활성화 게이트는 agents/ORG.md §4
- 부모: cmp-integrator (부모의 knowledge/ 노트를 선행 필수로 읽는다)
- 이수 단원: Lv1-1, Lv1-2 (2026-09-08), Lv2-1, Lv2-2 (2026-09-09)
- 다음 단원: Lv3-1 최신 리뷰: 세리아 첨가제 선택비 제어, 저결함 옥사이드 CMP

## 역할
TEOS·HDP·SOD 등 SiO2 막의 CMP — ILD 평탄화·STI. 기계 제거 지배, 실리카/세리아 슬러리

## 선행 지식 (부모에게 상속)
- [[../../knowledge/cmp/preston-luo-dornfeld-mrr]]
- [[../../knowledge/cmp/slurry-components-overview]]

## 실데이터 책임 (ORG.md §7.3)
옥사이드 실데이터(막종류·MRR·WIWNU·디싱) 스키마 + 보정 파라미터(Kp_oxide, 선택비) 정의

## 레벨 정의
Lv1 학부지식 → Lv2 대학원/리뷰논문 → Lv3 최신논문 추적 + 모델 구현 → Lv4 모델 개선 제안(교수급)

## 이수 기록
- 2026-09-08 Lv1-1 이수: knowledge/materials/film-oxide-teos-hdp-bpsg-sod-density-hardness.md
  (Wei 2010 IEEE WMED DOI 10.1109/wmed.2010.5453755, Cook 1990 J.Non-Cryst.Solids DOI
  10.1016/0022-3093(90)90200-6, Zantye 2004 Mater.Sci.Eng.R DOI 10.1016/j.mser.2004.06.002)
  check_knowledge.py ✓ / verify_claims.py ✓
- 2026-09-08 Lv1-2 이수: knowledge/materials/film-oxide-hydration-layer-mechanism-cook-suratwala.md
  (Cook 1990 J.Non-Cryst.Solids DOI 10.1016/0022-3093(90)90200-6 §3.1 전체 완독,
  Suratwala et al. 2015 J.Am.Ceram.Soc DOI 10.1111/jace.13659 — Cook 이론모델의 25년 뒤
  SIMS 실측 검증. 핵심: Cook 확산깊이 계산(0.5-12nm)과 실측 폴리싱층(1-20nm) 오더 일치,
  Suratwala Bielby층(Ce기준 50nm)이 Cook 계산치보다 두꺼움 — 두 메커니즘 동일성 미검증.
  K/Ce 침투가 제거속도에 반대로 반응(확산 vs 화학반응 지배) 확인)
  check_knowledge.py ✓ / verify_claims.py ✓
- 2026-09-09 Lv2-1 이수: knowledge/cmp/ild-cmp-planarization-global-local-density.md
  (Ouma 1999 MIT Ph.D. thesis hdl.handle.net/1721.1/9704 — DSpace에서 원문 PDF 229쪽 확보,
  스캔본이라 1.4절·5장·7.1-7.2절을 페이지 이미지로 직접 읽음; 저널판 Ouma et al. 2002 IEEE TSM
  DOI 10.1109/66.999598, Stine et al. 1998 DOI 10.1109/66.661292는 Crossref 확인·본문 미확보;
  Xie & Boning MRS 2003 원문 PDF 확보. 핵심: 국소 단차는 선형 소멸(t=ρ·z1/K), 전역 단차
  TIR=Δρ·z1(Fig.7.1 6000Å 재현), PL은 타원 가중함수가 2/π로 떨어지는 폭(식 5.13/5.14 적분
  재현, IC1000 최대처짐 약 6µm 재현), PL은 서브패드 강성이 지배(표 7.2 속도 +4% vs 서브패드
  제거 +50%). 과제 문구의 exp(-x/PL) 단차감쇠는 원문에 없음을 명기)
  check_knowledge.py ✓ / verify_claims.py ✓

- 2026-09-09 Lv2-2 이수: knowledge/cmp/sti-cmp-ceria-high-selectivity-nitride-stop-dishing.md
  (Lee 2002 MIT Ph.D. thesis hdl.handle.net/1721.1/29907 — DSpace API로 원문 201쪽 확보, 2장·3.7절 완독, 수식 쪽은
  이미지 판독; Dandu Veera et al. 2009 JES DOI 10.1149/1.3230624·Mariscal et al. 2020 ECS JSS DOI 10.1149/2162-8777/ab89bc
  원문(papers/ 기확보분) 완독; Srinivasan et al. 2015 리뷰 DOI 10.1149/2.0071511jss CC-BY 원문; Urban 2016 Ferro CMPUG
  슬라이드; Hwang et al. 2026 Polymers DOI 10.3390/polym18151899. 핵심: STI = Phase 1(ILD 밀도모델) + Phase 2(2물질
  removal-rate diagram) 폐형해 — D_ss = d_max·ρ(s−1)/(1+ρ(s−1)), K_ss = K/(1+ρ(s−1)), τ_nit = τ₂/(1+(s−1)ρ); 선택비↑는 디싱을
  줄이지 않고(→d_max) 침식률을 줄여 오버폴리시 창을 넓힌다(s 10→100 창 9배). 세리아 HSS: 억제제(환형 아민 0.05 %)로
  nitride 80→2 nm/min·선택비 4.4→175-290, 노출 후 3 nm 과도 제거 뒤 정지; 선택비는 P·V·패턴 의존(32-101). 원문 식 2.36
  상수항 부호 오기 발견(ODE 적분으로 확인), 식 3.46 K1 상수 불일치 정직 기록. 미확보: Lee 2007 MEE·Hwee 2001 JEM·Chang 2005 MEE)
  check_knowledge.py ✓ / verify_claims.py ✓ (출처 7건 실존, verify 4블록 PASS)

## 구현 요청
- **[P1] elliptic 가중커널 + Ouma 폐형해** — 무엇: `sim/tier1_empirical/pattern_density.py`에
  Ouma 식 5.11/5.12(반경 a=PL/2 원형하중 탄성변형, 완전 타원적분)를 2D 가중커널로 추가하고
  (`scipy.special.ellipe/ellipk` 사용 가능, 정규화 후 FFT 컨볼루션), 식 5.3 폐형해
  z(t)=z0−Kt/ρ0 (t<ρ0z1/K) / z0−z1−Kt+ρ0z1 를 up-area 두께 함수로 제공. 현재는 가우시안
  커널만 있음. 근거노트: knowledge/cmp/ild-cmp-planarization-global-local-density.md §5, §9[C].
  검증문헌값: w(a)/w(0)=2/π 정확히; IC1000(E=2.9e7 Pa, ν=1/3, a=2mm, q=7psi) w_max≈6µm
  (Ouma 1999 p.126); 표 5.3 타원필터 RMS 42Å@7.35mm는 데이터 없어 재현 불가(성질만).
- **[P2] TIR·최적 증착량 설계식** — 무엇: 레이아웃 밀도맵+PL → Δρ=ρmax−ρmin, TIR=Δρ·z1,
  t_lp=ρmax·z1/K, H0=H_ILD+z1(1+Δρ), t_opt=(ρmax+0.1)z1/K (Ouma 식 7.1-7.5) 유틸.
  근거노트: 같은 노트 §7. 검증문헌값: Δρ=0.8, z1=7500Å → TIR=6000Å (Fig.7.1);
  z1=0.7µm, H_ILD=0.8µm, Δρ=0.8 → H0=2.06µm(각주 범위 1.6-2.0µm 상단).
- **[P3] 서브패드 강성 → PL 매핑(경향만)** — 무엇: PL ∝ E_pad(Xie 2003) 경향과 표 7.2
  (적층 6.35 / 서브패드 없음 9.50 mm) 비율을 pad-mechanic 쪽 서브패드 강성 파라미터에 연결하는
  훅. 절대값 캘리브레이션은 특성화 마스크 실측 필요 — 미검증 표기 유지. 우선순위 낮음.
- **[P1] STI Phase 2 폐형해 (Lee 2002 식 2.32-2.56)** — 무엇: `sim/tier1_empirical/pattern_density.py`(또는 신설
  `sim/tier1_empirical/sti_two_phase.py`)에 nitride-up/oxide-down 2물질 단계 추가. 입력 K, s, τ₂(또는 d_max), ρ_nit(PL_nit로 필터링한
  유효밀도), Phase 1 결과 h_n·t_n → D(t) = (h_n−D_ss)e^{−(t−t_n)/τ_nit}+D_ss, E(t) = K_ss(t−t_n)+(h_n−D_ss)(1−ρ)/(1+ρ(s−1))(1−e^{…}),
  K_ss·D_ss·τ_nit 유도량, touch-down 시각 t_n은 식 2.52/2.53 초월방정식 고정점 반복. 근거노트:
  knowledge/cmp/sti-cmp-ceria-high-selectivity-nitride-stop-dishing.md §4.2, §8 [A][B]. 검증문헌값: K 2000 Å/min·s 10·τ₂ 60 s·ρ 0.5 →
  d_max 400 Å, τ_nit 10.9 s, D_ss 327 Å, K_ss 364 Å/min(§8 [A] 재현치); ρ 0.1/0.9 → D_ss 947/198 Å; RR_a(D_ss)=RR_f(D_ss)=K_ss 항등.
  주의: 원문 식 2.36의 상수항 부호는 오기 — dH/dt = RR_f − RR_a 로 구현할 것. 우선순위 높음(Cal-1 디싱 스키마의 물리 스켈레톤).
- **[P2] 세리아 HSS 일반화 훅 (Lee 2002 3장·§3.7)** — 무엇: Phase 1/2에 활성화 지연 t' = t − t_off(세리아 28 s)와 밀도별
  파라미터 함수 D_ss(ρ)=A·e^{−ρ/B}, K_ss(ρ), K_n1(ρ) 옵션(표준 1/ρ 형 대신 사용자 정의 함수 주입). 검증문헌값: 표 3.10 (2862/1.51,
  4784/0.40, 11573/0.28)이 표 3.9 ρ 0.5/0.7/0.9 값을 ±8 %로 재현(§8 [C]). 우선순위 중.
- **[P3] 오버폴리시 창 유틸** — 무엇: 나이트라이드 손실 예산 E_max와 (K, s, ρ)에서 허용 오버폴리시 시간 ≈ (E_max − 과도항)/K_ss
  계산 + 다이 내 t_n 퍼짐(§2.12.2: 80→120 s)을 더해 최소 오버폴리시 시간을 산출. 검증값: 예산 300 Å·K 2000·ρ 0.5에서 s 10 →
  0.8 min, s 100 → 7.6 min(§8 [B]; 과도항 무시한 내 유도, 문헌 직접값 아님 — 미검증 표기 유지). 우선순위 중.
