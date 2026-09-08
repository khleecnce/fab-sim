# 옥사이드 CMP 전문가 (film-oxide)

## 현재 레벨: Lv1 (2/6) — 활성화 게이트는 agents/ORG.md §4
- 부모: cmp-integrator (부모의 knowledge/ 노트를 선행 필수로 읽는다)
- 이수 단원: Lv1-1, Lv1-2 (2026-09-08)
- 다음 단원: Lv2-1 ILD CMP: 다층 배선 평탄화, 글로벌/로컬 평탄도

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
