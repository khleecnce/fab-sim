# 슬러리 입자 전문가 (slurry-abrasive)

## 현재 레벨: [대기] — 활성화 게이트는 agents/ORG.md §4
- 부모: slurry-chemist (부모의 knowledge/ 노트를 선행 필수로 읽는다)
- 이수 단원: 없음
- 다음 단원: Lv1-1

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
