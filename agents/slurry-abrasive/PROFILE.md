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

## 구현 요청
1. **Δ 팩터 형태 재검토** (우선순위: 중, 선행조건: 팩에 abrasive_d99_nm 확보 필요)
   - 무엇을: `sim/factors.py::_f_delta`를 거듭제곱 `(d99/d99_ref)^n` 대신 임계 초과 선형
     근사로 재설계 검토. 최소: 임계 직경(680 nm, fumed silica 한정) 초과 여부 불리언 게이트.
   - 근거 노트: knowledge/cmp/lpc-scratch-density-tail-correlation.md §2.2, §3
   - 검증 문헌값: Table V slope 2.99e-5~21.2e-5 counts/(particles/g_slurry), r²=0.987~0.991
     (절대 slope은 이 슬러리 시스템 특유 — 방향성만 이식 가능, 값 자체는 이식 금지)
   - 선행 필요: 5개 팩(cu_h2o2_bta, oxide_silica, sic_ceria_h2o2, sti_ceria, w_fe_oxidizer)
     모두 abrasive_d99_nm 부재 — 제조사 스펙시트/특허 조성표에서 D99 확보가 먼저다.
