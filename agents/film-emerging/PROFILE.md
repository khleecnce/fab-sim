# 신소재 CMP 전문가 (film-emerging)

## 현재 레벨: Lv3 (진행) — 활성화 게이트는 agents/ORG.md §4
- 부모: cmp-integrator (부모의 knowledge/ 노트를 선행 필수로 읽는다)
- 이수 단원: Lv1-1, Lv1-2, Lv2-1, Lv2-2, Lv3-1, Lv3-2
- 다음 단원: Cal-1 (CURRICULUM.md 참조)

## 역할
Co·Ru·Mo 배선, GST(PCM), 고유전체 등 차세대 막질의 CMP — Phase 2

## 선행 지식 (부모에게 상속)
- [[../../knowledge/cmp/surface-chemistry-cu-w-pourbaix-passivation]]

## 실데이터 책임 (ORG.md §7.3)
신소재 실데이터 스키마 초안

## 레벨 정의
Lv1 학부지식 → Lv2 대학원/리뷰논문 → Lv3 최신논문 추적 + 모델 구현 → Lv4 모델 개선 제안(교수급)

## 이수 기록

### Lv1-1 — Co 배선 CMP: 부식 민감성, 갈바닉, 억제제 화학 (2026-09-16)
- 노트: `knowledge/materials/film-co-interconnect-cmp-corrosion-galvanic-inhibitor.md`
- 게이트: `verify_claims.py` **PASS**(출처 9건 실존 · 검증코드 7블록 전부 실행 통과 · 출처없는 수치주장 0),
  `check_knowledge.py` **PASS**
- 자기시험: `EXAMS.md` Lv1-1 3문항 + 모범답안
- 확보 문헌 5건(전부 papers/ + INDEX.json 등록):
  `huang2019-npjmatdeg-pourbaix-magnetic-transition-metals.pdf`(10.1038/s41529-019-0088-z),
  `gamagedara2025-electrochem-cu-co-galvanic-tribo.pdf`(10.3390/electrochem6020015),
  `gamagedara2026-electrochem-mo-imidazole-galvanic.pdf`(10.3390/electrochem7010006),
  `cheng2024-apsusc-bta-derivatives-cobalt-cmp.pdf`(10.1016/j.apsusc.2024.161684),
  `yan2023-ecsjss-5mbta-cobalt-copper-cmp-preprint.pdf`(10.1149/2162-8777/accd99)
- 핵심 획득:
  1. Co 부동태 창 폭 0.7 pH 단위(10.3~11.0)이고 Co CMP pH(8.0/8.5/10.0)는 전부 창 밖 → **Co의 부동태는
     열역학이 아니라 억제제 흡착이 공급한다**.
  2. 갈바닉 폐형식 식 (15) 확보. **ΔE_corr 단독 판정은 말론산 반례로 반증**(ΔE_corr −21%인데 i_g +13%).
  3. 정지 PDP ΔE_corr는 연마 중 대비 3.6배 과대평가(0.507 → 0.142 V).
  4. Co 표면 Langmuir 재현: K_ads 474/476/622 M⁻¹, ΔG°_ads −25.21/−25.23/−25.89 kJ/mol(TTA만 원문과 3.00 어긋남).
  5. 판정 #17(평형 θ ≠ 정상상태 MRR)이 **Co라는 세 번째 막질**에서 독립 재현.
  6. **미확보(빈칸)**: Co/Ru 커플의 실측 ΔE_corr — Lv1-2 최우선 과제.

### Lv1-2 — Ru·Mo CMP: 난용해 금속의 산화제 화학, RuO₄ 생성창, 갈바닉 (2026-09-16)
- 노트: `knowledge/materials/film-ru-mo-cmp-oxidizer-chemistry-ruo4-galvanic.md`
- 게이트: `verify_claims.py` **PASS**(출처 8건 실존 · 검증코드 6블록 전부 실행 통과 · 출처없는 수치주장 0),
  `check_knowledge.py` **PASS**
- 자기시험: `EXAMS.md` Lv1-2 3문항 + 모범답안
- 확보 문헌 6건(4건 papers/ + INDEX.json, 1건 OA HTML, +CRC·[R26] 교차링크):
  `cui2013-jsst-ru-oxidizers-colloidal-silica.pdf`(10.1149/2.030301jss),
  `cui2012-jes-ru-oxide-species-periodate-ph.pdf`(10.1149/2.103203jes),
  `peethala2011-esl-cu-ru-galvanic-kio4.pdf`(10.1149/1.3589308),
  `cheng2017-jss-cu-ru-galvanic-ig-inhibitors.pdf`(10.1149/2.0181701jss),
  `he2018-jss-mo-kio3-acidic-passivation.pdf`(10.1149/2.0061806jss),
  Xu 2022 RSC Adv(10.1039/d1ra08243d, OA HTML·PDF 미확보)
- 핵심 획득:
  1. **Ru 산화제 적합성은 E° 스칼라로 못 정한다** — 연마율 정점은 최강 산화제가 아니라 E°≈1.6 V의 NaIO₄·NaClO
     (Ru를 비고체 RuO₄ 영역으로 미는 것). K₂S₂O₈(1.96 V)은 정점의 3%.
  2. **RuO₄(휘발·독성, 융점 25.4 °C) 억제창 = 알칼리 pH ≳ 9**(이온화로 휘발성 상실). Ru 팩에 pH 하한 제약 필요.
  3. **Mo는 W형(MoO₃/Mo₂O₅ 부동태 있음)** — Ru·Co와 갈림. MoO₄²⁻ 용해의 산성부동태/알칼리용해 pH 스위치.
  4. **갈바닉 양극이 커플마다 다르다**: Co/Cu→Co, Ru/Cu→Cu(540→20 mV, i_g KIO₄>H₂O₂), Mo/Cu→Mo(116/270 mV).
  5. **연마의 ΔE_corr 부호가 금속마다 반대**: Co/Cu −72%(축소) vs Mo/Cu +133%(확대) → 축소계수 금속별로.
  6. **Mo/KIO₃ 산화제–MRR은 Hill n≈4 협동형**(C₅₀≈0.044 M) — 판정#20 Langmuir(n=1) 이식하면 SSE 52배 악화.
  7. **Co/Ru 실측 ΔE_corr는 전수 탐색 후 부재**(Lv1-1 빈칸 종결) — Cu/Ru·Cu/Co·Ru/TiN만 존재. 열역학 상한
     0.735 V는 공정 예측값 아님.

### Lv2-1 — GST·칼코게나이드 CMP: 연질막 결함 제어 (2026-09-16)
- 노트: `knowledge/cmp/gst-chalcogenide-cmp-soft-film-defect-control.md`
- 게이트: `verify_claims.py` **PASS**(출처 5건 실존 · 검증코드 1블록 실행 통과 · 출처없는 수치주장 0),
  `check_knowledge.py` **PASS**
- 자기시험: `EXAMS.md` Lv2-1 3문항 + 모범답안
- 확보 문헌(전부 원문 PDF는 봇차단으로 미확보, DOI·초록·특허전문 수준까지만 확인):
  US 2010/0130013 A1(특허, **전문 WebFetch 확인** — 슬러리 조성·pH 3~9·디싱 50% 감소),
  Wang et al., *Chin. Phys. B* 23(8) 088502 (2014), DOI 10.1088/1674-1056/23/8/088502(**초록 WebFetch 확인**
  — GST 저경도→스크래치 대조실험),
  D'Arrigo et al., *Surf. Coat. Technol.* (2018), DOI 10.1016/j.surfcoat.2018.02.050(초록만, Semantic Scholar),
  Choi & Lee, *Electron. Mater. Lett.* 6, 23-26 (2010), DOI 10.3365/eml.2010.03.23(2차 인용 — 검색스니펫),
  Song, Liu, Wang, *Procedia Engineering* 102 (2015), DOI 10.1016/j.proeng.2015.01.131(Gold OA 확인, 원문
  봇차단으로 미확보 — 2차 인용),
  *Vacuum* (2009), DOI 10.1016/j.vacuum.2009.12.002(Tc≈141-148°C, 2차 인용)
- 핵심 획득:
  1. **GST 경도 절대 GPa는 못 구했지만 세 독립 경로(나노압입 정성, 단독 인장 E=20.2 GPa, CMP 스크래치
     대조실험)가 전부 "SiO₂보다 한 자리 낮다"는 방향을 가리킨다** → `sim/abrasive_mechanics.py`의 α 판정이
     구조적으로 소성(α=3/2) 쪽으로 밀리고, `MRR∝H_w^-3/2` 지수로 경도 10배 차이가 민감도 오더 31.6배로
     증폭된다(가정 위의 오더 추정 — 미검증).
  2. **결함 4종(스크래치/디싱/부식/상변화)의 지배변수가 서로 다르다** — 패드/입자 경도(스크래치),
     과연마시간/선택비(디싱), 산화제/pH(부식), 발열/접촉시간(상변화). 하나의 손잡이로 넷을 동시에
     못 잡는다.
  3. GST 연마율이 **pH 11 부근에서 최대**라는 관찰(정적부식 연동)과 산성/알칼리 산화생성물이 달라진다는
     서술을 확보했으나, **원문 PDF를 못 읽어 2차 인용 수준**으로만 신뢰한다(Song et al. 2015).
  4. **미확보(빈칸)**: GST 나노압입 경도의 확정 GPa 표, Te/Sb 선택적 용출의 정량 임계 pH, CMP 발열이 실제
     Tc(≈145°C)를 넘는지의 계산 — 전부 후속 단원(Lv3 최신 리뷰 추적) 과제로 남긴다.

### Lv2-2 — 고유전체·2D 소재 CMP 동향 (2026-09-16)
- 노트: `knowledge/films/high-k-2d-material-cmp-trends.md`
- 게이트: `verify_claims.py` **PASS**(출처 8건 실존 · 검증코드 2블록 전부 실행 통과 · 출처없는 수치주장 0),
  `check_knowledge.py` **PASS**
- 자기시험: `EXAMS.md` Lv2-2 3문항 + 모범답안
- 확보 문헌(원문 fitz 전문 판독 2건 + 초록/DOI확인 다수):
  Kull et al. 2023, *Nanomaterials* 13(10) 1607, DOI: 10.3390/nano13101607(HfO2 나노압입 경도,
  MDPI Gold OA 직접 확인), Yuan et al. 2014, *ECS JSS* 3(7) P243, DOI: 10.1149/2.0131407jss(HfO2
  RRAM CMP, 초록 확인), *ECS Trans.* 60(1) 647 (2014), DOI: 10.1149/06001.0647ecst(HfO2 슬러리
  탐색, 초록 확인), *J. Mater. Res.* 19(6) (2004), DOI: 10.1557/jmr.2004.0149(HfO2/ZrO2 HF 식각,
  DOI만 확인·2차 인용), Okasha 2023 HKUST MPhil 학위논문, DOI: 10.14711/thesis-991013223049703412
  (**원문 PDF 직접 확보·fitz 전문 판독** — hBN 캡핑층 CMP 호환성), Lo et al., arXiv:1706.10178
  (**원문 PDF 직접 확보·fitz 전문 판독** — hBN/MoS2 Cu 확산방지막, CMP 언급 부재 자체를 확인),
  Zong et al. 2016, *Carbon* 103, 63, DOI: 10.1016/j.carbon.2016.02.079(graphene-SiO2 접착력,
  DOI만 확인·2차 인용), Hess 2020, *Nanoscale Horizons* 5, DOI: 10.1039/c9nh00658c(2D 단층 두께,
  EuropePMC 서지사항 확인·수치는 2차 인용), Lo et al. 2020, *J. Appl. Phys.* 128, 080903, DOI:
  10.1063/5.0013737(2D 소재 BEOL 리뷰, Unpaywall CC-BY 확인·전문은 봇차단으로 미확보)
- 핵심 획득:
  1. **HfO2는 GST와 정반대다** — 나노압입 경도(≈10.5 GPa)가 SiO2 CMP 유효경도(≈10 GPa)와 같은
     자릿수라 "무른 막" 서사가 안 통한다. 진짜 병목은 화학이다: 표준 실리카 슬러리 RR 5 nm/min
     → NaBF4 첨가 95.5 nm/min(19.1배, verify 재현). Preston식이 `kPV`에서 `kPV+Rc`로 화학항을
     요구할 만큼 순수 기계 경로가 약하다.
  2. HfO2의 HF 식각률이 **결정 상태(비정질/어닐링)에 따라 크게 갈린다**(2차 인용, 방향만 확인) —
     표준 세리아/실리카/W용 χ 분기(IEP 창·정점형·산성역) 중 어느 것도 "불화물 착화" 경로를
     겨냥하지 않는다는 것과 정성적으로 부합.
  3. **2D 소재(graphene/hBN/MoS2) CMP 문헌은 "연마율"이 아니라 "접착력(nN)"을 잰다** — 확보한
     1차 문헌(HKUST 2023 학위논문)이 hBN을 "CMP를 견뎌야 하는 캡핑층"으로 다루며 AFM pull-off
     힘(14.7~92 nN)으로 판정. 우연이 아니라 기하학적 이유가 있다: 기존 5팩 δ_max 최솟값(W, 3 nm,
     Eusner 2009 재인용)도 2D 단층 두께(≈0.33 nm, Hess 2020)의 9배를 넘는다(verify 재현) — 어떤
     CMP 조건이든 최소 압입깊이가 이미 단층 전체를 관통해, κ·Δ의 "얕게 깎인다"는 연속체 가정이
     원천적으로 정의역 밖이다.
  4. **압력 하한(박리 임계) 부재는 ①·② 둘 다** — 2D 소재가 애초에 "폴리싱 대상"이 아니라서
     Preston형 질문이 안 맞는다는 것(②, 문헌 지형 자체가 증거)과, 그럼에도 "실제 CMP 압력에서
     캡핑층이 언제 벗겨지는가"라는 더 정확한 질문에 답한 1차 실험은 없다는 것(①)이 함께 성립.
  5. **10종 팩터 판정**: 고유전체는 κ 성립·χ 새 분기 필요, 2D 소재는 κ·Δ가 정의역 밖(이분법 손상
     모델 필요). ψ·τ·S는 두 소재군 모두 데이터 부재로 미판정 — 후속 단원 과제.

### Lv3-1 — 3nm 이하 배선 소재 로드맵과 CMP 요구 (2026-09-16)
- 노트: `knowledge/films/sub-3nm-interconnect-material-roadmap-cmp-requirements.md`
- 게이트: `verify_claims.py` **PASS**(출처 4건 실존 · 검증코드 2블록 전부 실행 통과 · 출처없는
  수치주장 0), `check_knowledge.py` **PASS**
- 자기시험: `EXAMS.md` Lv3-1 3문항 + 모범답안
- 확보 문헌 4건(전부 원문 확보 3건 + 초록 1건, `scope.py --check` 전부 허용 판정):
  Zhao et al. 2022, *Nanomaterials* 12(10) 1760, DOI: 10.3390/nano12101760(라이너 포함 선저항
  스케일링, MDPI Gold OA 원문 fitz 전문 판독), Murdoch et al. 2022, *IEEE VLSI Symposium*,
  DOI: 10.1109/VLSITechnologyandCir46769.2022.9830150(semi-damascene Ru, imec 리포지토리
  원문 fitz 전문 판독), Patlolla et al. 2018, *ECS JSS* 7(8) P397, DOI:
  10.1149/2.0181808jss(Ru 라이너 CMP 선택비 붕괴, ECS CC-BY 원문 전문 판독), Wan et al. 2018,
  *IEEE IITC*, DOI: 10.1109/IITC.2018.8454841(단일레벨 Ru subtractive 식각, 초록만 확인 — 2차
  인용)
- 핵심 획득:
  1. **Ru/Mo가 로드맵에 오른 것은 저항률이 낮아서가 아니라 라이너가 얇아서다.** Ru 벌크 저항률은
     Cu의 4.6배(7.8 vs 1.678 µΩ·cm)로 절대 열등하지만 라이너가 10배 얇아(0.3 vs 3 nm) 좁은
     선폭에서 죽은 단면 비중이 훨씬 작다(§1 verify). Zhao 2022 원문 직접 결론: "below about
     20 nm, the superiority of Cu in resistance is significantly weakened."
  2. **semi-damascene은 "CMP 소멸"이 아니라 "금속 CMP만 소멸"이다.** Murdoch 2022(1차 원문)의
     4단계 공정에서 라인 형성은 subtractive 식각(RIE)으로 대체되지만, 갭필 유전체 평탄화는
     여전히 CMP다 — CMP 모델링 범위 자체가 공정 스킴에 따라 달라진다는 구조적 함의(P10).
  3. **CMP가 남는 대안 스킴에서는 실패 모드가 "디싱"(연속 깊이)에서 "구조적 좌굴"(이산 붕괴)로
     바뀐다.** Patlolla 2018(1차 원문, CC-BY)이 48 nm 피치 이하에서만 나타나는 "Ru bending"을
     보고 — 선택비 붕괴로 지지를 잃은 라이너가 구부러지는 실패로, 기존 Δ(D99 압입 깊이 기반
     연속 손상)로는 표현 불가능(Lv2-2 §2.3의 "연속체 모델 정의역 이탈" 패턴이 2D 소재가 아닌
     다결정 금속 다층 스택에서 재현).
  4. **미확보(빈칸)**: Mo(몰리브데넘) 특이적 semi-damascene/subtractive 로드맵 1차 문헌 — 저자명
     (Gupta, Hosseini, van der Veen 등 imec)까지는 확인했으나 원문 접근 실패. 다음 조사 과제.

### Lv3-2 — 신소재 파라미터 세트 골격 정의: GaN 사례 (2026-09-18)
- 노트: `knowledge/films/gan-cmp-parameter-skeleton-new-film-onboarding.md`
- 게이트: `verify_claims.py` **PASS**(출처 7건 실존 · 검증코드 1블록 실행 통과 · 출처없는
  수치주장 0), `check_knowledge.py` **PASS**
- 자기시험: `EXAMS.md` Lv3-2 3문항 + 모범답안
- `knowledge/params/*.yaml`은 읽기만 했다(base.yaml, sic_ceria_h2o2.yaml, oxide_silica.yaml,
  w_fe_oxidizer.yaml 4건 대조) — 수정 없음.
- 확보 문헌 5건(원문 fitz 전문 판독 2건 + WebFetch 초록 확인 3건, 실패 1건 기록):
  Dong et al. 2022, *Materials* 15(3) 1210, DOI: 10.3390/ma15031210(MDPI CC-BY, **원문
  fitz 전문 판독** — GaN 나노압입 경도), Mandal et al. 2021, *Carbon* 183, DOI:
  10.1016/j.carbon.2021.04.100 / arXiv:2104.01048(**원문 fitz 전문 판독** — β-Ga2O3
  등전점), Aida et al. 2011, *J. Electrochem. Soc.* 158(12) H1206, DOI:
  10.1149/2.024112jes(IOP 봇차단, WebFetch 부분 텍스트 확인 — 콜로이달실리카 GaN CMP
  MRR), Wei et al. 2022, *ECS JSS* 11, DOI: 10.1149/2162-8777/ac5807(IOP 봇차단, WebFetch
  초록 확인 — UV보조 광전기화학 CMP MRR), Xian et al. 2024, *ECS JSS*, DOI:
  10.1149/2162-8777/ad1c89(IOP 봇차단, Semantic Scholar 초록 확인 — K2S2O8 산화제 표면조도
  최적화). 탐색 실패 1건: Polian et al. 1996(DOI 10.1063/1.361236, GaN 탄성상수) — AIP
  403·Semantic Scholar abstract null, 무료 전문 경로 전멸로 종결(§2.2에서 "결과에 영향
  없음"으로 확인).
- 핵심 획득:
  1. **절차서의 직관("경도·탄성계수 둘 다 필요")이 실제 코드 소비처와 다르다** — 저장소
     전체에서 막질 탄성계수를 쓰는 파라미터 키가 0건(`grep -i modulus knowledge/params/*.yaml`
     결과 패드 E* 3건뿐). `regime_adapter.py::alpha_from_bulk_bound`는 `film_bulk_hardness_pa`
     하나만 쓴다 — GaN 탄성계수를 못 찾은 것(AIP 봇차단)이 결과에 영향 없다는 것까지
     정량 확인(local_P/H=7.76e-4, verify (a)).
  2. **산화막 Preston 계수를 GaN에 상속하면 351배 과대예측**(verify (b), assert로 재현) —
     GaN(19.2GPa)은 산화막(9GPa)보다 2.1배만 더 단단해 경도차로는 설명 안 되는 격차.
     격차의 대부분은 화학(불활성)에서 온다는 것을 정성 확인했으나 정량 분해는 못 했다.
  3. **GaN CMP 문헌은 "UV 조사 하에서"라는 조건절을 반복** — 화학적 불활성 때문에
     광생성 정공 없이는 산화가 유의미하게 진행되지 않는다는 뜻이다. 기존 5팩 스키마
     어디에도 광량(UV 강도) 축이 없다 — "문헌 없음"이 아니라 "물어볼 칸이 없다"는 구조적
     결손([P12]).
  4. **IEP는 GaN 자체가 아니라 CMP가 만들어내는 산화생성물(β-Ga2O3, pH 4.6)의 값을 대리로
     써야 한다** — SiC(분말→단결정 전이, EVIDENCE-RULES E4)보다 오히려 더 직접적인 대리
     관계(CMP가 실제로 그 화학종을 만든다)라는 것을 확인했다([P13]).
  5. **미확보(빈칸, R8)**: Aida 2011/Wei 2022/Xian 2024 세 편 전부 원문이 IOP Radware
     봇차단으로 막혀 압력·rpm·입경·정확한 pH 표를 못 봤다 — `kp_m_per_pa` 자기선언이
     이번 회차에 불가능했다. 다음 회차 최우선 과제(원문 표만 확보하면 즉시 역산 가능).

## 구현 요청 (소프트웨어 부문 — sim/ 은 이 에이전트가 건드리지 않는다)

### [P12] 광량(UV) 축 — 기존 5팩 스키마에 아예 없는 신규 차원 (Lv3-2 §2.3·§5)
- **무엇을**: `sim/chemistry.py`의 χ(산화제)항이 "농도만의 함수"라는 암묵 전제를 갖는데,
  GaN처럼 화학적으로 불활성인 막질은 자외선 조사 유무·광량(mW/cm²)이 산화 반응 자체를
  켜고 끄는 독립 게이트로 작동한다. 레시피에 `uv_assist: bool`(또는
  `uv_intensity_mw_cm2: float`) 필드를 신설하고, `oxidizer_langmuir_K`류 상수에
  `requires_uv: true` 메타를 붙여 UV 없이 이 상수를 쓰면 경고가 나가게 할 것.
- **근거·검증문헌값**: Wei et al. 2022, DOI: 10.1149/2162-8777/ac5807 — "MRR of GaN was as
  high as 404.6 nm h⁻¹ ... under UV"(NaOCl), "380.3 nm h⁻¹ ... under UV"(H2O2). UV 없는
  대조 수치는 원문 봇차단으로 미확보. **회귀 테스트**: `uv_assist=false` 입력에서 GaN 팩의
  산화제 항이 (자기선언된 값이 있어도) 저활성 폴백으로 떨어져야 한다 — 지금 스키마로는 이
  폴백을 표현할 필드 자체가 없다.
- **우선순위**: 낮음(GaN 팩 자체가 아직 없음). 그러나 스키마 결손이라 팩 신설보다 먼저
  풀어야 하는 선행 작업이다.

### [P13] IEP 교차물질(산화생성물) 전이 규칙의 명문화 (Lv3-2 §2.5)
- **무엇을**: `wafer_iep_ph`가 지금은 "막질 자체의 등전점"이라는 암묵 전제로 쓰이는데,
  GaN처럼 CMP 화학이 표면을 다른 화학종(Ga2O3)으로 바꿔놓고 그 화학종의 IEP가 실제 연마
  계면을 지배하는 경우가 있다. 파라미터 문서에 "wafer_iep_ph는 막질 자체가 아니라 CMP가
  실제로 형성하는 표면종의 IEP를 우선한다"는 규칙을 명문화할 것.
- **근거**: Mandal et al. 2021, DOI: 10.1016/j.carbon.2021.04.100 — β-Ga2O3 IEP pH 4.6.
- **우선순위**: 낮음(문서화 작업, 코드 변경 없음).



### [P10] 공정 스킴 분기 게이트 — semi-damascene/subtractive는 금속 CMP 소모품축 전체를 비활성화 (Lv3-1 §2·§5)
- **무엇을**: `sim/factors.py` 소모품축(κ·χ·ψ·τ·Δ·S)이 현재 "막질이 정해지면 항상 호출된다"고
  가정하는데, semi-damascene/subtractive 스킴에서는 라인 계층에 **금속 CMP 스텝 자체가 없다**
  (Murdoch 2022 원문: "No metal CMP is needed"). 레시피에 `metallization_scheme: damascene |
  semi_damascene | subtractive` 필드를 두고, damascene이 아니면 라인 계층의 금속 소모품축
  전체를 비활성화하고 유전체-하드마스크 CMP(별도 팩만 필요)로 대체할 것.
- **근거·검증문헌값**(노트 §2 verify): Murdoch et al. 2022, DOI:
  10.1109/VLSITechnologyandCir46769.2022.9830150 — 공정 4단계 중 라인 형성은 RIE subtractive
  식각(②), CMP는 갭필 유전체 평탄화(③)에만 등장. Ru 저항률이 식각 전후 14–15 → 13–15 µΩ·cm로
  거의 불변("damage-free integration")이라는 것은 **금속 손상이 CMP가 아니라 식각 균일도
  문제로 완전히 이관**되었다는 방증. **회귀 테스트**: `metallization_scheme=subtractive`
  입력에서 기존처럼 금속 소모품축(κ·χ 등)이 0이 아닌 값을 뱉으면 이 게이트가 없다는 뜻 — 정상은
  해당 축들이 "호출 안 됨(N/A)"을 반환해야 한다.
- **우선순위**: 중간(신소재 팩 신설 시점에 맞춰). 단 Mo/Co semi-damascene 1차 데이터는 이번
  조사에서 확보하지 못해 Ru 외 소재로의 일반화는 미검증.

### [P11] Δ(손상 유발도)에 "다층 스택 구조적 좌굴" 이산 게이트 — 라이너 CMP 잔존 스킴 (Lv3-1 §3·§5)
- **무엇을**: 3원 이상 스택(예: Ru-Cu-ULK)에서 한 재료(라이너)가 CMP 도중 옆의 지지 재료보다
  느리게 제거되면 "지지되지 않은 벽"이 되어 **좌굴(bending)**하는 실패 모드가 있다. 현재 Δ는
  D99 압입 깊이 기반 연속 스칼라(디싱/스크래치 깊이)만 표현하므로, 인접 재료 제거율 비가 특정
  임계(원문 표현 "1-1 selectivity"에서 벗어남)를 넘으면 **연속 깊이 대신 이산 붕괴 플래그**로
  전환하는 게이트가 필요하다 — [[../../knowledge/films/high-k-2d-material-cmp-trends]](Lv2-2
  §2.3, [P9])가 2D 소재에서 이미 요구한 "연속체 압입 모델 정의역 이탈" 게이트와 같은 클래스의
  결함이며, 이번에는 다결정 금속 다층 스택에서 독립 재현되었다.
- **근거·검증문헌값**(노트 §3): Patlolla et al. 2018, DOI: 10.1149/2.0181808jss — "Ru bending"과
  "Cu recess"가 56/64 nm 피치에서는 없다가 48 nm 피치(10 nm 노드급) 이하에서만 나타남. 저자가
  제시하는 이상적 목표: "a 1-1 selectivity between Ru-Cu-ULK." 다운포스 실측 범위 1.0–1.6 psi
  (Table I). **회귀 테스트**: 인접 재료 제거율 비를 극단(예: 0.1배 또는 10배)으로 설정했을 때
  기존 Δ가 그대로 "몇 배 깊다"는 연속값을 뱉으면 게이트 부재 — 정상은 "구조 붕괴 위험" 이산
  플래그로 전환.
- **우선순위**: 낮음(라이너-CMP 잔존 스킴이 채택될 경우에만 필요 — semi-damascene이 채택되면
  [P10]으로 우회되므로 두 구현 요청은 상호 배타적 시나리오의 짝이다).

### [P8] χ에 "불화물 착화" 분기 신설 — HfO2 (Lv2-2 §1.2)
- **무엇을**: `sim/factors.py::_f_chi`의 기존 pH 분기(세리아 IEP 창·W 산성역·실리카 정점·연화
  폴백) 중 어느 것도 HfO2를 겨냥하지 않는다. `abrasive`나 재료명이 HfO2/high-k 계열일 때
  "불화물 착화제 농도(NaBF4 등)" 축을 활성으로 하는 새 분기가 필요하다.
- **근거·검증문헌값**(노트 §1.2 verify): 표준 실리카 슬러리 RR=5 nm/min → NaBF4 첨가 95.5
  nm/min(19.1배, Yuan et al. 2014, DOI: 10.1149/2.0131407jss 초록). 원문 자체가 Preston식을
  `RR=kPV`에서 `RR=kPV+Rc`(정적 화학항 추가)로 수정해야 했다고 명시 — **필수 회귀 테스트**:
  이 분기 없이 기존 pH 항만으로 HfO2를 모델링하면 저농도 첨가제 조건에서 RR을 1자리 이상
  과소평가해야 한다(정상 — 화학항 부재를 자동 검출).
- **우선순위**: 낮음(HfO2 팩 신설 시점). 첨가제-농도 스윕 다점 데이터가 없어 K/n 등 함수형
  파라미터는 이번 조사에서 확보하지 못함 — 배수(19.1배) 앵커 하나뿐.

### [P9] κ·Δ에 "단층 2D 소재 정의역 이탈" 게이트 — graphene/hBN/MoS2 (Lv2-2 §2.3·§3)
- **무엇을**: κ(접촉강도)·Δ(손상)가 전제하는 "압입깊이 ≪ 막 두께"(연속체 제거 모델)가 막
  두께가 원자층 수준(< 1 nm)일 때 구조적으로 깨진다. 팩의 `film_bulk_hardness_pa` 계산에 쓰이는
  막 두께가 2D 단층 스케일(< 1 nm)이면, 기존 "제거율 nm/min" 출력 대신 "접착 파괴 이분법"
  (붙어있음/박리됨) 모드로 자동 전환하는 게이트가 필요하다 — 지금처럼 억지로 nm/min을 계산하면
  물리적으로 의미 없는 값(δ_max가 막 두께의 수 배)이 나온다.
- **근거·검증문헌값**(노트 §2.3 verify): 기존 5팩 δ_max 최솟값(W, 3 nm, `pad_asperity_hardness_
  max_pa`=3.1e8 Pa 기준, Eusner 2009 DOI: 10.1149/1.3121964 재인용)이 2D 단층 두께(graphene
  0.335 nm·hBN 0.33 nm, Hess 2020 DOI: 10.1039/c9nh00658c)의 9배 이상. **회귀 테스트**: 막
  두께를 1 nm 미만으로 넣었을 때 기존 Δ 공식이 그대로 "Δ=몇 배"라는 연속값을 뱉으면 이 게이트가
  없다는 뜻 — 이산 이분법 출력으로 바뀌어야 정상.
- **근거 데이터(대안 물리량)**: 접착력 실측(Okasha 2023 HKUST 논문, 원문 확인) — hBN(1L)/low-k
  21.9 nN, hBN(few-layer)/low-k 29.2 nN, Si3N4(10nm)/low-k 14.7 nN, Cu/hBN(few-layer) 91~92 nN
  vs Cu/Si3N4 21 nN. **주의**: 이 힘은 AFM 수직 pull-off이지 CMP의 압입+전단 복합하중이 아니라
  그대로 이식하면 안 된다(노트 §2.2 한계 표기) — 게이트가 필요하다는 근거로만 쓸 것.
- **우선순위**: 낮음(2D 소재 팩 자체가 아직 없음). 실제 CMP 압력 스윕 박리 실험 1차 문헌이
  전무해(§2.4, 노트) 정량 임계 압력은 이번 조사로 확보하지 못했다 — 다음 조사 최우선 과제.

### [P5] Ru 산화제항 — E° 스칼라 금지, "Pourbaix 목적영역" 게이트로 (Lv1-2 §3)
- **무엇을**: Ru 팩(신설 시)의 산화제 적합성을 산화제 E° 하나가 아니라, **Ru를 RuO₄/RuO₄⁻ 비고체역으로 미는
  산화제만 활성**으로 판정하는 이산 게이트(oxidizer∈{NaIO₄, NaClO}=활성, 그 외=저연마)로 넣을 것. 추가로 **pH ≳ 9
  알칼리 제약**(RuO₄ 휘발 회피)을 필수 필드로.
- **근거노트**: `film-ru-mo-cmp-oxidizer-chemistry-ruo4-galvanic.md` §3. **검증문헌값**(노트 §3.2 verify 블록):
  NaIO₄ ~1290 vs K₂S₂O₈ ~40 Å/min(E° 단조 반증), 정점 E°≈1.6 V. **회귀 테스트**: E° 최대 산화제에 최대 MRR을
  배정하는 구현은 여기서 자동 실패해야 한다.
- **우선순위**: 중간(Ru 팩 신설 시점). 단 산화제–농도 스윕 1차 데이터가 없어 Ru의 연속 농도곡선은 미확보.

### [P6] Mo 팩 — W 팩 원형 + Hill 산화제항(n 자유) + pH 스위치 (Lv1-2 §4·§6)
- **무엇을**: Mo 팩을 W 팩([[../../knowledge/cmp/surface-chemistry-cu-w-pourbaix-passivation]]) 원형으로 하되,
  산화제–MRR을 판정#20의 Langmuir(n=1)가 아니라 **Hill θ=(KC)ⁿ/(1+(KC)ⁿ), n 자유파라미터**로 둘 것.
  MoO₄²⁻ 용해의 pH 의존(산성 부동태/알칼리 용해)을 산화제항과 결합.
- **근거·검증문헌값**(노트 §6 verify): Hill n≈4.2(SSE 1.5) vs Langmuir n=1(SSE 79) → **52배 차**, C₅₀≈0.044 M,
  RR_max≈54 nm/min, 0.05/0.03 M 비 1.58. Mo Ecorr/icorr(§4.2 Table): pH2·0.1M RR90.2/SER2.2(41배).
  **회귀 테스트**: Langmuir(n=1) 단독 구현은 Mo/KIO₃ 5점에서 SSE가 Hill 대비 10배 이상 나빠야(정상).
- **우선순위**: 중간. n의 정확값(4.2)은 5점 적합이라 미검증 — status=modeled, confidence=estimated로.

### [P7] 갈바닉 커플 방향·연마 부호를 금속별 부호표로 (Lv1-2 §5)
- **무엇을**: 갈바닉 입력에 커플별 **양극 지정**(Co/Cu→Co, Ru/Cu→Cu, Mo/Cu→Mo)과 **연마 축소계수 부호**를
  금속별로 둘 것. [P2](Lv1-1)의 "hold→polish 축소계수"를 금속 무관 상수로 두면 Mo에서 부호가 틀린다.
- **근거·검증문헌값**(노트 §5.1·5.3): Ru/Cu ΔE_corr 540→20 mV, i_g KIO₄ 8.48>H₂O₂ 4.16 µA/cm²([Che17] 직접측정);
  Mo/Cu ΔE_corr hold116→polish270 mV(+133%, Co/Cu −72%와 반대).
- **우선순위**: 높음(갈바닉 결함 예측의 부호 오류 방지). [P1](Lv1-1)의 i_g 폐형식과 짝.

> 근거노트는 전부 `knowledge/materials/film-co-interconnect-cmp-corrosion-galvanic-inhibitor.md`.

### [P1] 갈바닉 전류밀도 항 — ΔE_corr 스칼라를 4입력 폐형식으로 교체
- **무엇을**: 갈바닉 부식 지표를 `ΔE_corr` 하나가 아니라 아래 폐형식으로 계산하는 함수를 Tier2에 추가.
  ```
  i_g(A) = exp(ΔE_corr/β_ca) · [i_corr(C)·S_c/S_a]^(β_c/β_ca) · [i_corr(A)]^(β_a/β_ca)
  β_ca = β_c(C) + β_a(A),  ΔE_corr = E_corr(C) − E_corr(A)
  ```
- **근거**: Gamagedara & Roy 2025, *Electrochem* 6(2) 15, DOI 10.3390/electrochem6020015 식 (12)–(15).
- **검증문헌값**(노트 §4.2–4.3 verify 블록에 이미 assert로 박혀 있음):
  ΔE_corr(hold) = 0.507 / 0.401 / 0.349 / 0.044 V (슬러리 I~IV),
  i_g(hold, F) = 55.1 / 62.2 / 21.1 / 6.60 µA·cm⁻²,
  **필수 회귀 테스트**: 구현한 함수가 슬러리 II에서 "ΔE_corr 감소 + i_g 증가"를 재현해야 한다
  (ΔE_corr만 쓰는 구현은 여기서 부호가 틀리므로 자동 검출된다).
- **우선순위**: **높음**. 현재 코드에 갈바닉 항 자체가 없고, 있더라도 ΔE_corr 단독이면 착화제 레시피에서 틀린다.
- **주의**: β_c, β_a 실측값은 [R25]에 표로 없다. 우리가 역산한 **lumped β_ca = 0.165 V는 유효값**이므로
  파라미터 팩에 `status: modeled, confidence: literature`로 넣고 실측 Tafel 표를 확보하면 교체한다.

### [P2] 정지/연마 조건 구분 플래그 — 문헌 ΔE_corr에 축소계수를 강제
- **무엇을**: 갈바닉 입력에 `measured_under: hold | polish` 필드를 두고, `hold`면 축소계수를 곱해 쓰게 한다.
- **근거·검증문헌값**: 같은 논문 Table 2. 슬러리 I에서 정지 0.507 V → 연마중 0.142 V(**−72%, 3.57배**).
  슬러리 II 0.401 → 0.047(−88%), III 0.349 → 0.105(−70%), IV 0.044 → 0.042(−5%).
  축소율이 슬러리마다 다르므로 **고정계수 하나로 넣지 말 것** — 첨가제가 적을수록 축소가 크다.
- **우선순위**: 중간. [P1]과 같이 들어가야 의미가 있다.

### [P3] Co 파라미터 팩의 χ 항 — `inhibitor_conc` 없이는 정의되지 않게 만들 것
- **무엇을**: Co 팩(신설 시)의 χ 드라이버에 억제제 농도를 **필수 필드**로 두고, Langmuir θ를 계산하되
  그 θ를 **SER(화학)에만 강하게, MRR(기계)에는 약하게** 거는 이중 경로로 분리.
- **근거**: Cheng 2025, *Appl. Surf. Sci.* 682, 161684, DOI 10.1016/j.apsusc.2024.161684.
- **검증문헌값**: pH 8, 3 wt% SiO₂ + 0.5 wt% H₂O₂ + 0.15 wt% 글리신 기준,
  K_ads(5CBTA/BTA/TTA) = 474 / 476 / 622 M⁻¹, ΔG°_ads = −25.21 / −25.23 / −25.89 kJ·mol⁻¹,
  η(3/6/9 mM, TTA) = 68.18 / 87.62 / 91.71 %, I_corr 334.25 → 27.70 µA·cm⁻²,
  **9 mM TTA에서 MRR 132.64 nm/min · SER 0.79 nm/min**(= 이중 경로 분리의 앵커).
- **우선순위**: 중간(Co 팩 신설 시점에 맞춰). 단 `exp(−k·θ)` 단일 경로로 구현하면 판정 #17·#24와 같은
  구조적 반증을 Co에서도 반복하게 된다 — **반드시 이중 경로로 설계할 것**.

### [P4] 억제효율의 측정법 출처를 파라미터에 남길 것 (PDP vs EIS)
- **무엇을**: 억제 관련 파라미터에 `measured_by: PDP | EIS` 메타필드 추가, 두 출처의 값을 섞지 못하게 검증.
- **근거·검증문헌값**: 같은 논문·같은 조건(9 mM TTA)에서 EIS R_p는 33.80 → 1114.01 Ω·cm²(**33.0배**)인데
  PDP I_corr은 334.25 → 27.70 µA·cm⁻²(**12.1배**) — Stern–Geary B 불변 가정이 **2.7배** 어긋난다.
- **우선순위**: 낮음(데이터 위생). 그러나 문헌 수집이 늘수록 섞일 위험이 커진다.
