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

## 이수 기록 (계속)
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
