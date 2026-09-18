# 슬러리 입자 전문가 (slurry-abrasive)

## 현재 레벨: [대기] — 활성화 게이트는 agents/ORG.md §4
- 부모: slurry-chemist (부모의 knowledge/ 노트를 선행 필수로 읽는다)
- 이수 단원: Lv1-1, Lv1-2, Lv2-1, Lv2-2, Lv3-1, Lv3-2 (CURRICULUM.md 정본)
- 다음 단원: Cal-1 스펙시트 → 모델 입력 변환 규칙 (G2 이후 활성)

## 역할
실리카(콜로이달/퓸드)·세리아·알루미나 입자의 크기·형상·농도·경도가 MRR·결함에 미치는 영향

## 선행 지식 (부모에게 상속)
- [[../../knowledge/cmp/slurry-components-overview]]
- [[../../knowledge/cmp/colloid-zeta-dlvo-slurry-stability]]

## 실데이터 책임 (ORG.md §7.3)
스펙시트(입도·농도·제타) → 모델 입력 변환 규칙 정의 + 공개 데이터로 검증

## 레벨 정의
Lv1 학부지식 → Lv2 대학원/리뷰논문 → Lv3 최신논문 추적 + 모델 구현 → Lv4 모델 개선 제안(교수급)

## 이수 기록
(크론이 갱신)

## 이수 기록
- Lv1-1 (2026-09-10): 입자 종류별 제조법과 물성(콜로이달/퓸드 실리카, 세리아 소성/습식) —
  knowledge/cmp/abrasive-manufacturing-colloidal-fumed-silica-ceria.md
  (Son et al. 2021 Sci. Rep. 11:17736, doi:10.1038/s41598-021-97122-9 — 전문 PDF 확보·fitz
  대조; US 8,211,193 B2 Fujifilm Planar Solutions; US 2015/0104939 A1 Cabot Microelectronics;
  Kim 2018 IntechOpen 리뷰 doi:10.5772/intechopen.75408). 콜로이달=액상 이온교환(구형),
  퓸드=기상 화염가수분해(응집), 세리아 소성=분쇄(facet)/습식=침전(구형)의 제조공정-형상 인과를
  확립. Son 2021 정량 재현: 슬러리 pH 5.0→6.0에서 2차입자 223→130nm 감소·연마율
  263→524 nm/min 증가(역상관), 초미세 습식세리아 대 facet 습식세리아 연마율 비 ~52배(문헌
  ~50배와 일치). 절대 경도(GPa)는 1차 문헌에서 확보 못 함 — Lv2-1 잔여(Hertz 압입) 과제로 이월.
- Lv1-2 (2026-09-09): 입도 분포·LPC와 스크래치 상관 — knowledge/cmp/lpc-scratch-density-tail-correlation.md
  (Remsen et al. 2006, JES 153(5) G453-G461, doi:10.1149/1.2184036 — 미러 사이트 확보·전문 대조).
  임계 직경 0.68 µm(실리카 등가) 확정, 스크래치-LPC는 선형(r²=0.987~0.991) — 현재
  sim/factors.py `_f_delta`의 거듭제곱(n=3.0) 가정은 이 문헌이 지지하지 않음을 확인.
- Lv2-1 부분 (2026-09-09): D99 실측값 확보 —
  knowledge/cmp/abrasive-d99-composite-particle-versum2019.md
  (US 2019/0127607 A1, Versum Materials — 무료 공개 특허출원공보, Table I·II 실측).
  D99 158.5~316.7 nm(세리아코팅 실리카 복합입자), D99-HDP oxide RR 완전 단조 증가(n=4)
  확인했으나 구간별 기울기 13.7배 차이로 선형 근사는 성립하지 않음. **팩에 값 이식 안 함**
  (조성 오귀속 방지 — 이 특허 실시예 값이지 5개 팩의 실제 슬러리 값이 아님).
  경도·형상·Hertz 압입은 미착수 — Lv2-1 잔여.
  다음 단원: Lv1-1(입자 종류별 제조법) 또는 Lv2-1 나머지(경도·Hertz).

- Lv2-1 계속 (2026-09-09): D99-스크래치 정량 함수형 확보 —
  knowledge/cmp/abrasive-d99-scratch-hitachi-us8439995.md
  (US8439995B2, Hitachi Chemical — 세리아 D50/D99/스크래치 4점 실측, 원문 PDF 확보).
  거듭제곱 회귀 n≈1.44(R²=0.997) — 현재 sim/factors.py `_f_delta` 기본값 n=3.0보다
  약 2배 가파름. lpc-scratch-density-tail-correlation(선형)과 방향 일치(교차확증).
  factors.py docstring에 근거 기록(코드 로직·기본값은 표본 부족으로 유지, 지수 교체는
  구현 요청으로 남김).

- Lv2-1 완성 (2026-09-11): 입자 경도·Hertz(소성)압입·입자당 제거체적 —
  knowledge/cmp/abrasive-hardness-hertz-indentation-removal-volume.md
  (Luo & Dornfeld, "Material Removal Regions in CMP...Part 1", UC Berkeley/escholarship 2002,
  전문 확보·통독, 도서챕터 DOI 10.1007/978-3-662-07928-7_5 — 원 논문 Luo&Dornfeld 2001 IEEE TSM
  doi:10.1109/66.920723은 유료·OA 없음, 재인용만 확인). [[../../knowledge/materials/hertz-gw-contact-mechanics]]
  (탄성 Hertz·GW)를 계승해 소성압입 단일입자 모델로 확장: 제거체적(율) ∝ x²·(P/H_w)^(3/2)·V
  (원문 Eq.11), 경도 지수 -3/2를 코드로 재현(대수적 검증). 입자경도 비교표 확보: 알루미나
  Mohs9·E≈500GPa(doi:10.3390/ma17030679 PMC10856169; 500GPa는 Luo2002 원문이 직접 인용),
  세리아(벌크) H=6.44±0.72GPa/E=167.6±12.5GPa(doi:10.3390/ma19102134 PMC13208460, 원자로
  대체연료 펠릿 측정 — CMP 슬러리 나노입자 아님, 오더 참고만), 실리카(용융) Vickers
  H=7.3±0.3GPa(doi:10.1016/j.jnoncrysol.2006.02.113, 초록 수준만 확인·원문 미접근).
  **핵심 발견**: (1) 실리카 경도(7.3GPa)가 SiO2 웨이퍼 벌크 경도(≈10GPa, 문헌 재인용)보다
  낮거나 비슷 — "입자가 웨이퍼보다 훨씬 단단하다"는 리지드 인덴터 가정이 실리카/SiO2에서
  깨짐, Cook(1990) 수화층 모델이 왜 필요한지 정량적으로 뒷받침. (2) 벌크경도 3/2제곱 법칙
  단독으로 예측한 W/산화막 상대제거율(≈31.6배)이 실측 대표값비(≈0.51배)와 62배 오더
  불일치 — 화학(WO3 passivation 순환 등)이 지배적임을 재확인(재현 실패를 숨기지 않고 그대로
  기록). Lv1-1이 이월한 "절대 경도 미확보" 과제를 이걸로 해소. verify_claims/check_knowledge
  둘 다 통과. abrasive-manufacturing-colloidal-fumed-silica-ceria.md Lv1-1 잔여과제 해소.

## 구현 요청
0. **세리아 톱니 항·세리아 팩 농도 기준 정정** (우선순위: 상, 2026-09-13 Lv3-1에서 제기)
   - 무엇을: (a) `knowledge/params/sti_ceria.yaml`의 `ce3_fraction`·`ce3_fraction_ref` 주석에
     **정의를 "표면 Ce 중 Ce³⁺ 분율"로 명시**. 지금은 정의가 없어 "입자 전체 Ce 대비"로 읽으면
     60 nm 입자의 기하 상한 3.09%의 4.9배로 물리적으로 불가능한 값이 된다(껍질 모델
     f=1−(1−2t/d)³, t=a/√3=0.312 nm). (b) 같은 팩이 base(oxide_silica)에서 상속하는
     `abrasive_wt_pct=20.0`을 **0.25 wt%로 오버라이드**(`abrasive_ref_wt_pct`도 동일) — 이 팩의
     `abrasive_size_nm=60`·`kp_m_per_pa`가 Dandu 2009(doi:10.1149/1.3230624) 0.25 wt% 조건에서
     온 값이라 기준 농도가 80배 어긋나 있다. (c) `sim/chemistry.py::_ceria_term`의 선형 가정에
     **국소 선형화·외삽 금지 경고**를 notes에 추가.
   - 근거 노트: knowledge/cmp/ceria-chemical-tooth-particle-site-density-facet.md §7·§8·§9
   - 검증 문헌값: Ce 면밀도 (111) 7.89 / (100) 6.83 nm⁻²(Brugnoli 2023 보고 7.9/6.8과 일치),
     XPS Ce³⁺ ≈5%(Chakarova 2025) vs 단일층 기하 상한 6.25%, 세리아 0.25 wt% → 350 nm/min(4 psi).
   - 하지 말 것: §6의 "입자당 23배"는 교차연구(E4) 비교라 **팩 계수로 이식 금지**(오더 표지만).
     세리아 농도 지수는 실리카의 +1/3 상속 금지 — Dandu 2009은 60 nm 세리아에서 0.25>0.5>1 wt%로
     MRR이 **감소**한다고 서술한다(별도 단원 필요).

1. **Δ 팩터 형태 재검토** (우선순위: 중, 선행조건: 팩에 abrasive_d99_nm 확보 필요)
   - 무엇을: `sim/factors.py::_f_delta`를 거듭제곱 `(d99/d99_ref)^n` 대신 임계 초과 선형
     근사로 재설계 검토. 최소: 임계 직경(680 nm, fumed silica 한정) 초과 여부 불리언 게이트.
   - 근거 노트: knowledge/cmp/lpc-scratch-density-tail-correlation.md §2.2, §3
   - 검증 문헌값: Table V slope 2.99e-5~21.2e-5 counts/(particles/g_slurry), r²=0.987~0.991
     (절대 slope은 이 슬러리 시스템 특유 — 방향성만 이식 가능, 값 자체는 이식 금지)
   - 선행 필요: 5개 팩(cu_h2o2_bta, oxide_silica, sic_ceria_h2o2, sti_ceria, w_fe_oxidizer)
     모두 abrasive_d99_nm 부재 — 제조사 스펙시트/특허 조성표에서 D99 확보가 먼저다.

2. **팩별 D99 확보 진행 상황** (2026-09-09 갱신)
   - 세리아 계열(sic_ceria_h2o2, sti_ceria): US10669449B2 특허 실시예에서 D99 실측 확보했으나,
     팩 화학종과 동일 제품이라는 근거가 없어 이식 보류(오귀속 방지). 참고치: D99/D50 비율
     1.82~3.82배 (근거: knowledge/cmp/abrasive-d99-spec-cross-pack-comparison.md §2.2 Table3).
   - 콜로이달실리카(oxide_silica): Evonik IDISIL 기술문서 확인 — Z-average 평균 입경(50~125nm)만
     공개, D99 비공개. 상업 스펙시트는 D50만 노출하는 경향(정성, 미검증 일반화).
   - 알루미나 계열(cu_h2o2_bta, w_fe_oxidizer): **4회차 연속 D99 미확보(2026-09-10 종결 판단)**.
     추가 시도: Guo&Subramanian(2004, doi:10.1149/1.1640632, Cu+알루미나 화학종 정확 일치)은
     평균 응집입경 220nm만 보고, 분포 데이터 전무. US6258137B1(나노알루미나 CMP 특허)은
     "D90≤50nm, 상위10%<100nm 초과" 경계조건만 있어 D99 유일값 역산 불가(논리적으로 증명,
     knowledge/cmp/abrasive-d99-alumina-fourth-attempt-guo-nanoalumina.md §5 verify 블록).
     **알루미나 D99 절대값 탐색은 이 경로로는 종결 — accuracy_gaps.py --skip 처리(2026-09-10)**.
     대안 경로 권고: (a) 세리아 팩에 이미 확보된 D99(Versum/Hitachi)를 이식 재검토,
     (b) LPC 임계 직경(0.68µm, lpc-scratch-density-tail-correlation.md §2.2)을
     scratch_threshold_nm 축으로 전환.

   - **2026-09-10 실행됨**: 대안 (a) 이식 완료 — sti_ceria(및 상속 sic_ceria_h2o2)에
     `abrasive_d99_nm`=700nm(Hitachi US8439995B2 Ex.1 baseline, confidence=estimated)와
     `damage_exponent`=1.44(동 특허 4점 회귀, confidence=literature)를 배선.
     `_f_delta`가 처음으로 발동(knowledge/params/sti_ceria.yaml, tests/test_factors.py
     신규 3건, qa_loop --strict PASS, ρ=0.9349 불변). 잔여: cu_h2o2_bta·w_fe_oxidizer
     (알루미나)·oxide_silica(콜로이달실리카)는 여전히 D99 미확보 — 대안 (b) LPC 임계
     전환이 다음 시도 대상.
   - **2026-09-14 해소됨**: 알루미나 D99 절대값은 여전히 미확보이나, sti_ceria와 동일한
     "화학종+용도 일치 1차 특허 baseline 이식" 논거로 3팩 전부 literature 승격
     완료(knowledge/cmp/abrasive-particle-size-distribution-d99-tail.md). 알루미나 2팩은
     US7344988B2(DuPont, 알루미나 CMP 특허)의 D99.9/D50 상한(more preferred ≤5x)이 기존
     유도값(비율 5.00)과 정확히 일치해 값은 그대로 두고 근거만 교체, oxide_silica는
     US10894906B2(Versum, 실리카 코어 CMP 복합입자) 실측 절대값(287.5nm)으로 교체.

3. **Δ damage_exponent 하향 조정 검토** (우선순위: 중, 신규 2026-09-09)
   - 무엇을: `sim/factors.py::_f_delta`의 `damage_exponent` 기본값 3.0 → 1.4~1.5 범위 검토.
   - 근거 노트: knowledge/cmp/abrasive-d99-scratch-hitachi-us8439995.md §3
     (US8439995B2 4점 회귀, n=1.444, R²=0.997) + lpc-scratch-density-tail-correlation.md
     (Remsen 2006, fumed silica, 선형=n≈1 근방) — 두 독립 문헌·화학종이 n=3.0보다
     훨씬 완만한 지수를 지지.
   - 검증에 쓸 문헌값: US8439995B2 Example1(D99=700nm,scratch=20), Example2(500nm,10),
     Comparative1/2(2500nm,100).
   - 선행 필요: 여전히 abrasive_d99_nm이 5개 팩 어디에도 없어 no-op — 지수를 먼저
     바꿔도 예측 변화 없음. D99 팩 스펙 확보(특히 알루미나 계열)가 여전히 최우선.

4. **농도 항을 멱함수 → 포화형(점유확률) 함수로 교체** (우선순위: 중, 신규 2026-09-12)
   - 무엇을: `sim/factors.py` 농도 항 `(C/C_ref)^n`을 `[C/(C_h(P)+C)] / [C_ref/(C_h(P)+C_ref)]`
     (또는 포아송형 `1−e^(−C/C0(P))`)로 교체. 신규 팩 파라미터 `abrasive_conc_half_wt_pct`
     (기준압력에서의 반포화 농도), `abrasive_conc_half_pressure_exponent`(기본 1.0, GW A_r∝P 근거,
     미검증). `abrasive_conc_exponent<0`인 팩(sic_ceria_h2o2 −0.406)은 감소 레짐이라 기존
     멱함수 유지(게이트).
   - 근거 노트: knowledge/cmp/abrasive-concentration-mrr-saturation-contact-probability.md
     §4(점유확률 유도·극한), §5(포화형 SSE ≈255/≈135 vs 멱함수 ≈926), §6(C_h 압력 단조증가).
   - 검증에 쓸 문헌값: US9499721B2 TABLE 18(validation/datasets/us9499721b2_teos_colloidal_silica_pressure_conc.yaml,
     22점) — 3 psi 행 140/207/226/229/243/248 nm/min(0.5~3.0 wt%), 압력별 C_h ≈0.2/0.3/0.9 wt%
     (1.5/3/5 psi). 농도 순위 유지 + 고농도 평탄부 재현이 합격 기준.
   - 주의: oxide_silica 팩의 캘리브레이션 출처(Li 2021, 20~30 wt%·음전하·pH 11)와 계가 달라
     C_h 값을 그대로 이식하지 말 것(confidence=estimated로만). 현재 `abrasive_saturation_wt_pct`
     상수 경고는 압력 의존을 못 담으므로 이 항으로 대체.

## 이수 기록 (계속)
- Lv3-1 (2026-09-13, **자가검사 통과**): 세리아 화학적 톱니(chemical tooth) 메커니즘과 옥사이드 선택비 —
  knowledge/cmp/ceria-chemical-tooth-particle-site-density-facet.md
  (`verify_claims.py` 출처 11건 실존·코드 5블록 전부 통과, `check_knowledge.py` 통과).
  형제(slurry-chemist/film-oxide/film-nitride)가 이미 다룬 Ce³⁺ 산화환원·첨가제 선택비는 반복하지 않고
  **"톱니가 몇 개이고 몇 개가 물리는가"**라는 입자 기하·개수 축만 다뤘다. 1차 출처: Brugnoli et al. 2023
  Langmuir 39(15) 5527, doi:10.1021/acs.langmuir.3c00304(PMC10116594, 전문 XML 확보);
  Dandu Veera et al. 2009 JES 156(12) H936, doi:10.1149/1.3230624(전문 PDF); US9499721B2 TABLE 18;
  Chakarova et al. 2025 Molecules 30(15) 3100, doi:10.3390/molecules30153100(PMC12348644);
  Bellahsene et al. 2025 Nanomaterials 15(17) 1366, doi:10.3390/nano15171366(리뷰, 2차 인용).
  핵심: (1) 형석 격자에서 패싯별 Ce 면밀도 (111) 7.89 / (100) 6.83 nm⁻²를 유도해 원자모사 보고값
  7.9/6.8과 일치시키고, 밀도 7.216 g/cm³·(111) 수산기 피복 33.2%까지 같은 기하로 재현.
  (2) 세리아 경도 6.44 GPa는 SiO₂ 막(≈10 GPa)의 0.64배 — 리지드 인덴터 가정이 깨지며, Luo-Dornfeld는
  입자 재질항이 없어 세리아/실리카 입자당 비를 1.23배로만 예측한다. (3) 실측(4 psi 정합)은 질량당 5.19배,
  **입자당 23.3배** → 톱니 배수 ≈19(단 교차연구 E4, 오더 표지). (4) 350 nm/min을 Cook 24회/개·
  Si–O–Ce 0.7 nm⁻²로 역산하면 필요 활성 입자는 단층의 0.06~1.06% — 실접촉 면적률과 같은 자릿수로
  톱니 모델이 물리적으로 충분함을 확인. (5) 껍질 모델로 팩 `ce3_fraction=0.15`의 정의 오류와
  `sti_ceria`의 `abrasive_wt_pct=20.0` 상속 오류를 발견(구현 요청 0번). (6) 근거 충돌: Ln³⁺ 도핑에서
  Ce³⁺가 가장 많은 Yb가 RR 증가는 4.3%로 최저(리뷰 2차 인용) → Ce³⁺ 선형 가정은 국소 선형화로 제한,
  패싯은 "밀도축 vs 활성축" 두 개로 분해(스칼라 형상계수 금지).
  미확보: Ma et al. 2022 doi:10.1021/acsaelm.2c01553(단원 정중앙 주제, SSRN 403·미러 사이트 미러 3종 전부 실패)
  — 다음 회차 최우선. 상용 세리아의 실제 노출 패싯 비율(HRTEM 통계)도 미확보.
- Lv2-2 (2026-09-12, **자가검사 미실행 — 조건부 이수**): 입자 농도-MRR 포화 곡선과 접촉 확률 모델 —
  knowledge/cmp/abrasive-concentration-mrr-saturation-contact-probability.md.
  이 회차는 실행 환경에서 파이썬·curl·웹검색·웹페치가 승인 대기로 전부 차단되어
  `tools/verify_claims.py`·`tools/check_knowledge.py`를 실행하지 못했고 신규 문헌 확보·PDF 재판독
  (pdftoppm 부재)도 불가했다. 저장소 내 기확보 1차 자료만 사용: US9499721B2(Cabot, 특허 실시예
  TABLE 18 — 콜로이달 실리카 54 nm 0.5~3 wt% × 1.5/3/4/5 psi TEOS, 22점, E1),
  Luo & Dornfeld 2003 doi:10.1109/tsm.2003.815199(캐시 실존확인, Region 1 C 선형식 형제노트 재인용),
  Li 2021 doi:10.1149/2162-8777/ac3e44(캐시 전문), Bai 2007 doi:10.1016/j.apsusc.2007.04.027(형제노트 재인용),
  US20220315802A1(감소 레짐 교차참조). 핵심: (1) 3 psi 한계기울기 1340→100 Å/min/wt%(13.4배 붕괴)
  = 포화 실측, 저자도 "1.5 wt% 이상은 12.5 wt% 대조군과 동등" 서술. (2) 활성입자를 접촉 자리
  점유확률 N=n_s(1−e^(−λ)), λ∝C/A_r로 정식화 — 저농도 선형(Luo-Dornfeld Region 1)·고농도 포화
  (n_s∝A_r∝P)·반포화 농도 C_h∝P가 한 식에서 나옴. (3) 전역 멱지수 n≈0.30은 sim 기본 1/3과
  일치하나 국소 지수 0.56→0.11로 붕괴, 포화형 SSE가 멱함수의 1/3.6~1/6.9. (4) C_h가 1.5/3/5 psi
  에서 ≈0.2/0.3/0.9 wt%로 단조증가 — 모델 예측(C_h∝P) 방향 확인, 지수(≈1.25)는 미검증.
  EVIDENCE-RULES: Li 2021 "선형"(E3) vs Cabot 포화(E1)는 레짐 분리로 판정(계·전하·pH 다름).
  verify 블록 4개(순수 파이썬)는 손계산으로 밴드를 잡았으며 **총괄이 verify_claims/check_knowledge
  실행 후 통과 시 CURRICULUM [x] 확정** — 그 전까지 체크박스는 비워 둠.
- Lv2-1 계속 (2026-09-10): 텅스텐 벌크 CMP 실양산 데이터 확보 —
  knowledge/cmp/w-cmp-abrasive-agglomeration-scratch-multiplier-egan-kim2019.md
  (Egan and Kim 2019, ECS J. Solid State Sci. Technol. 8(5) P3206, doi:10.1149/2.0311905jss --
  GLOBALFOUNDRIES 300mm 양산 데이터, Unpaywall OA PDF 확보 fitz 대조). 핵심: 입자크기 3배
  응집(온도유도) -> 스크래치 60배(n_temp약3.73 역산), 입자크기 3배(교반유도) -> 스크래치
  6.67배(n_agit약1.73 역산) -- 텅스텐계 damage_exponent가 세리아(Hitachi n=1.44)보다 가파를
  가능성. 결정적 발견: **텅스텐 벌크 CMP는 입자크기가 MRR에 통계적으로 무관**(원문 직접
  실측) -- 카파 팩터 화학종별 예외 처리 필요성 시사(구현요청 참조). D99 절대 nm 값은 여전히
  미확보(PSD 그래프가 정규화 축) -- 델타 갭은 이번 회차도 no-op 유지, damage_exponent
  화학종별 분화 근거만 축적(n=1.44 세리아 vs n=1.73~3.73 텅스텐, 3번째 독립 문헌).

- 갭 보강 (2026-09-14): 입도분포 대입자 꼬리(D99/D95/D90) 측정법·상관 —
  knowledge/materials/abrasive-psd-large-particle-tail-d99.md
  (Kim, Yang, Kim 2010, Electrochem. Solid-State Lett. 13(4) H137, doi:10.1149/1.3299254 —
  SLS vs SMPS 직접 비교, 미러 사이트 미러 경유 전문 확보·fitz 대조; Yang, Kim, Kim 2010,
  J. Electrochem. Soc. 157(3) H235, doi:10.1149/1.3273079 — 단분산 세리아 30~300nm 통제실험,
  동일 경로 확보). abrasive-d99-scratch-hitachi-us8439995.md §9.4가 이미 3팩(oxide_silica,
  cu_h2o2_bta, w_fe_oxidizer) D99 confidence를 estimated로 판정 완료했고, 알루미나 D99
  절대값 탐색은 선행 4회차가 "공개 1차 문헌 경로 소진"으로 종결한 상태라 이번 회차는 같은
  절대값 탐색을 반복하지 않았다. 대신 **측정법 자체의 구조적 한계**를 새 1차 문헌으로
  확정: (1) SLS(강도가중 광산란)는 산란강도가 10⁴배 낮은 소입자를 검출 못 하고, SMPS(단일
  입자 개수계수)는 15~550nm(세리아 한정 최대 1µm)까지만 정밀 — D99가 수 µm급이면 SMPS도
  못 본다는 것이 원문 명시. 제조사 QC 표준장비(DLS/SLS)가 D99를 비공개하는 구조적 이유를
  설명(선행 Evonik 관찰과 정합). (2) 세리아 계열 안에서만도 D99/D50 비율이 1.82~10.42배
  (5.7배 폭)라는 것을 기존 확보 문헌(Versum/Hitachi 특허, 재채굴 없음)으로 재확인. (3) 단분산
  세리아(30~300nm, 화학 배제 DI수 연마) 통제실험에서 Ra∝x^0.3346, 300nm에서만 비정질
  손상층 관찰(200nm는 결정질 유지) — 손상 문턱이 200~300nm 사이에 있음을 TEM으로 직접
  관찰. 이 지수(0.3346)는 Hitachi n=1.44와 물리량이 달라 합산 불가하지만, 둘 다
  damage_exponent 기본값 3.0보다 훨씬 완만하다는 방향성을 세 번째 독립 문헌·측정법으로
  교차확증. **3팩 confidence 판정은 바꾸지 않음**(새 절대 D99값도 새 구현 요청도 없음 —
  기존 §9.4 판정 유지가 이 노트의 발견과 모순되지 않음). verify_claims/check_knowledge
  둘 다 통과.

- 갭 해소 (2026-09-14): 알루미나 2팩 + 콜로이달실리카 1팩 abrasive_d99_nm estimated→literature —
  knowledge/cmp/abrasive-particle-size-distribution-d99-tail.md
  (US7344988B2, DuPont Air Products Nanomaterials LLC, "Alumina abrasive for chemical
  mechanical polishing" — freepatentsonline.com 2회 독립 fetch로 claim/명세 수치 교차 확인;
  US10894906B2, Versum Materials US, LLC, "Composite particles, method of refining and use
  thereof" — 동일 방법으로 Table 1 교차 확인). 6회차에 걸친 선행 탐색(알루미나 D99 4연속
  실패 + 일반비 대체)이 소진한 자리에서, **화학종+용도가 정확히 일치하는 신규 1차 특허 2건**을
  찾아 sti_ceria(§9, Hitachi Ex.1 baseline 이식)와 동일한 E2 논거를 적용했다. (1)
  `cu_h2o2_bta`·`w_fe_oxidizer`(둘 다 알루미나): 기존 D99=D50×5.00 유도값을 **바꾸지 않고**
  근거만 교체 — US7344988B2가 Cu/Al/W CMP 알루미나에 "post-milled D99.9 more preferably
  <5x D50" 상한을 명시하는데, 이 팩들의 비율(정확히 5.00)이 그 상한과 정확히 일치한다.
  (2) `oxide_silica`(콜로이달 실리카): 같은 5.00 비율이 실리카 코어 실측(US10894906B2 Table1
  "No Treatment", D50=152.3/D99=287.5nm, 비율 1.887)과 100% 넘게 벌어짐을 확인하고 폐기,
  대신 이 실측 절대값(287.5nm)을 baseline으로 채택(250→287.5, `abrasive_ref_d99_nm` 동반
  이동). 세 팩 모두 confidence=literature. tests/test_factors.py의 대응 regression test
  (`test_delta_synthesis_derived_d99_matches_d50_times_generic_ratio`)를 새 근거에 맞춰
  갱신(estimated 고정 assert → literature 확인 + oxide_silica 실측값 assert로 교체) —
  같은 날 판정#16이 이 테스트를 작성했으므로 후속 갱신으로 간주. ⚠ D99.9≠D99(안전한 방향의
  상한 근사), damage_exponent는 이 회차 범위 밖(변경 없음). verify_claims/check_knowledge/
  pytest tests/test_factors.py 셋 다 통과.

- Lv3-2 (2026-09-16, **자가검사 통과**): 입자 파라미터 → Kp 기여 정량모델 (종합·감사 단원) —
  knowledge/cmp/abrasive-parameters-to-kp-contribution-quantitative-model.md
  (`verify_claims.py` 출처 14건 실존·코드 6블록 전부 통과, `check_knowledge.py` 통과).
  '구현'이라 적혀 있으나 sim/은 소프트웨어 부문 소관이므로 산출물은 **함수형+재현노트+구현
  요청서**로 낸다(sim/·YAML 미수정). 내용: (a) `_f_kappa` 3항 감사 — **농도항만** P·V 고정
  1차 회귀(US9499721B2 3psi n≈0.30)로 팩 0.3333을 직접 뒷받침, 입경항은 수치회귀 null(Cu
  판정#1)+정점유도(실리카80/세리아163 레짐분할), 입자경도는 κ 독립항이 아님(코드 H^-1.5=패드,
  Luo-Dornfeld H_w^-3/2=웨이퍼) — 입자경도는 승수가 아니라 리지드 인덴터 게이트. (b) 함수형
  비교 — 같은 E1 데이터에서 멱함수 SSE≈926 vs 포화형(Langmuir≈255/포아송≈135) ΔAIC>10, 국소
  지수 0.56→0.11 붕괴를 레짐 분할(평균 금지). (c) 3입자 배율표(기준 실리카 1.0): 세리아 입자당
  ≈23배(E4 오더표지, 팩계수 이식 금지), 알루미나 미확보(head-to-head 실측 없음). (d) D99→Δ
  귀속을 형제 인용으로 정리(d50→Kp, D99→Δ 분리; 이중계상 금지). 1차 출처(전부 형제 노트에서
  도구 실존확인·재사용): US9499721B2, Cooper 2002(doi:10.1149/1.1517772), Wang 2012, Li 2021
  (doi:10.1149/2162-8777/ac3e44), TW202115224A, Dandu 2009(doi:10.1149/1.3230624), Oh 2010
  (doi:10.1016/j.mee.2010.07.040), Luo-Dornfeld/Bai 2007. EVIDENCE-RULES 판정#1(입경 null) 종합
  재확인. **새 근거 충돌 없음**(형제 판정 종합).

- Cal-1 (2026-09-19, **자가검사 통과**): 스펙시트(입도·농도·제타) → 모델 입력 변환 규칙 정의 + 공개 데이터 검증 —
  knowledge/cmp/slurry-abrasive-specsheet-to-model-input-conversion-rules.md
  (`verify_claims.py` 출처 4건 실존·코드 5블록 전부 통과, `check_knowledge.py` 통과).
  1차 스펙 조사(상용 TDS·특허 실시예): **Evonik IDISIL TDS**(papers/evonik-idisil-cmp-colloidal-silica-datasheet.pdf,
  입경="Average Particle Size Z avg"=DLS 강도가중, Silica Content wt.%, pH(20°C), Peanut 형상)·**US9499721B2**
  (avg 54nm 측정법 미기재, 15wt% 농축→희석, pH 4.7)·**US20190127607A1/US10894906B2**(Versum, D99="99 wt.%",
  disc centrifuge 질량가중, Table1 D50 152.3/D75 189.8/D99 287.5)·**Seo 2021**(doi:10.1149/2162-8777/ac2c56,
  ζ=−63mV @pH 8.1 — 제타 측정 pH 명시 예). 핵심 발견: (1) **스펙시트마다 입경 측정 가중이 다르다** —
  상용 TDS는 Z-average(강도), 특허는 disc centrifuge(질량). (2) **Hatch–Choate median 변환**(1929,
  doi:10.1016/s0016-0032(29)91451-4) $D_{med,k}=D_g\exp(k\ln^2\sigma_g)$로만 통일 가능; disc centrifuge
  D99/D50=1.887→σ_g=1.314 역산, 역산에 안 쓴 D75로 3.6% 이내 교차검증(로그정규 정합). (3) **wt%→vol%**는
  입자밀도 필수(slurry-colloid F_vol 인용, 실리카 2.2로 30wt%→16.3vol%, 밀도 혼동만으로 15%+ 편차). (4)
  팩 abrasive_size_nm=50이 Evonik Z-avg 50과 **우연 일치**하나 size_basis 미명시로 정점모델 입력에 최대 35%
  잠재 편차 — 값은 유지, 필드 신설 제안. (5) **식별가능성**: Kp=κ_size·κ_conc 곱 구조라 단일조건 잔차는
  입도/농도 어느 단독으로도 완벽 설명(비식별) → 스펙 축 스윕이 귀속의 전제(prior.py/fit_npw.py 잔차층 설계와 정합).
  형제 경계 준수: 제타 화학·pH·산화제(slurry-chemistry)·이력/응집(slurry-colloid)·스키마 파일(cmp-data-engineer)은
  인용만. sim/·data/schema/·YAML 미수정 — 스키마 개정은 §6 제안표로 인계.

## 구현 요청 (계속 — Cal-1 캘리브레이션 스키마)

8. **슬러리 스펙 스키마 필드 신설**(cmp-data-engineer 인계, 우선순위: 중, 신규 2026-09-19)
   - 무엇을: `data/schema/`에 슬러리 스펙 필드(또는 `slurry_spec` 객체) 신설 — 핵심은 값과 함께 **측정 규약**을
     메타로 받는 것: `abrasive_size_basis`(enum: intensity_zaverage/volume_median/mass_median/number_median/
     primary_bet/primary_tem/hydrodynamic, **필수**)·`abrasive_size_method`(dls/laser_diffraction/disc_centrifuge/
     spos/bet/tem)·`psd_sigma_g` 또는 (d50,d99)·`abrasive_conc_unit`(wt_pct/vol_pct/g_per_L)·
     `abrasive_density_kg_m3`(wt%면 필수)·`zeta_mv`+`zeta_ph`(제타 있으면 pH 필수)·`zeta_ionic_strength_mM`.
   - 근거 노트: knowledge/cmp/slurry-abrasive-specsheet-to-model-input-conversion-rules.md §1·§6.
   - 검증 문헌값: Evonik Z-avg vs disc centrifuge 가중 차이, Hatch-Choate σ_g=1.314(US10894906B2), Seo 2021 pH 8.1.
   - 하지 말 것: size_basis 없이 D50만 받기(가중 통일 불가). 제타를 측정 pH 없이 받기(귀속 불가).

9. **`abrasive_size_nm`에 size_basis 태그**(우선순위: 중, 신규 2026-09-19)
   - 무엇을: 팩 `abrasive_size_nm`(및 정점모델 기준)에 측정 가중을 명시하는 주석/키. 정점모델(Li 2021)이 어느
     가중의 크기를 가정했는지 원문이 밝히지 않아 현재 Evonik 50과의 일치가 규약상 모호하다 — 값은 유지하되
     basis를 못박아야 이 축의 잔차를 신뢰 귀속할 수 있다.
   - 근거 노트: 위 노트 §4·§5. 검증 문헌값: σ_g=1.31 가정 시 Z-avg 50→부피median 40·개수median 32(basis별 35% 편차).
   - 하지 말 것: 지어낸 σ_g로 상용 TDS(σ_g 비공개) 값을 강제 환산(그게 오염). σ_g 없는 소스는 표기 그대로+플래그.

## 구현 요청 (계속 — Lv3-2 sim/tier2)
5. **입자 경도 진단 인자(승수 아님, 게이트)** (우선순위: 낮음, 신규 2026-09-16)
   - 무엇을: 팩에 `abrasive_hardness_gpa`가 있고 웨이퍼(표면층) 유효경도보다 낮으면 "리지드
     인덴터 가정 위반 — 순수 기계 Kp 항 신뢰 저하" 경고를 `_f_kappa` notes에 남기는 **진단만**.
     **Kp를 곱셈 항으로 바꾸지 말 것**(입자 경도는 Luo-Dornfeld에서 소거되는 게이트이지 승수가
     아니다). 벌크 경도 단독 예측은 W/SiO2 제거율비를 60배 이상 틀리게 낸다.
   - 근거 노트: knowledge/cmp/abrasive-parameters-to-kp-contribution-quantitative-model.md §6.
   - 검증 문헌값: 실리카 7.3 GPa < SiO2막 유효경도 10 GPa(위반), 알루미나 E≈500 GPa(성립),
     Luo-Dornfeld H_w^-3/2 단독 예측 31.6배 vs 실측 0.5배(불일치 60배).
   - 하지 말 것: 입자 경도를 `(H_p/H_ref)^k` 승수로 넣기(근거 없는 부호·지수). 독립 스윕 미확보.
6. **농도 함수형 포화 교체 — AIC 근거 보강**(우선순위: 중, 편승 2026-09-16)
   - 구현요청 4번(농도항 멱함수→포화형)과 동일 항목. 이 단원 §4의 AIC 비교(멱함수 대비 포화형
     ΔAIC>10 결정적 우세)가 그 요청의 근거를 강화한다 — **새 요청이 아니라 근거 보강**.
   - 근거 노트: 위 노트 §4 + abrasive-concentration-mrr-saturation-contact-probability.md §5.
7. **입자 경도 축·알루미나 Kp 배율 데이터 확보**(우선순위: 낮음, 선행 조사)
   - 무엇을: 같은 입경·같은 화학에서 경도만 바꾼 P·V 고정 스윕(입자 경도 축), 그리고 콜로이달
     실리카와 나란히 잰 알루미나 Kp 실측(3입자 배율표 알루미나 칸). 확보 전까지 §7 알루미나 칸·
     §6 경도 게이트는 미확보 유지 — 지어내지 않는다.
   - 근거 노트: 위 노트 §6·§7·§12.
