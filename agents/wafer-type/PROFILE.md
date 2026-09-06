# 시험 웨이퍼 전문가 (wafer-type)

## 현재 레벨: [활성] (G1 개방 2026-09-06)
- 부모: cmp-integrator (부모의 knowledge/ 노트를 선행 필수로 읽는다)
- 이수 단원: Lv1-1, Lv1-2, Lv2-1 (2026-09-06)
- 다음 단원: Lv2-2

## 역할
NPW(블랭킷)와 PTW(패턴) 웨이퍼의 목적·구조·측정 체계·데이터 해석 차이. 두 유형 데이터를 잇는 전이 규칙의 소유자

## 선행 지식 (부모에게 상속)
- [[../../knowledge/cmp/wiwnu-pressure-velocity-wafer-scale]]
- [[../../knowledge/cmp/pattern-dependent-dishing-erosion]]

## 실데이터 책임 (ORG.md §7.3)
NPW/PTW 메타데이터 스키마 소유. 두 유형 실데이터 정렬·비교 규칙 정의 (§7.2 전이 규칙의 구현)

## 레벨 정의
Lv1 학부지식 → Lv2 대학원/리뷰논문 → Lv3 최신논문 추적 + 모델 구현 → Lv4 모델 개선 제안(교수급)

## 이수 기록
(크론이 갱신)


## 이수 기록 (크론 갱신, 2026-09-06)
- 2026-09-06: Lv1-1/Lv1-2 통합 학습 완료. knowledge/cmp/npw-ptw-test-wafer-fundamentals.md
  (check_knowledge ✓, verify_claims ✓ — 출처 1건 실존, python verify 1블록 통과).
  핵심: NPW 49점 polar 체계(US6922603B1), PTW MIT 854계열 마스크·effective density
  모델(Boning et al. 1999, RR=K/ρ_eff 반비례 관계 assert로 검증), Kim&Seo(2002)
  상관계수 r=0.71은 원문 미확보로 미검증 표기. 2/6 완료.


## 이수 기록 (크론 갱신, 2026-09-06 2차)
- 2026-09-06: Lv2-1 완료. knowledge/cmp/npw-ptw-pattern-effect-gw-physics.md
  (check_knowledge ✓, verify_claims ✓ — 출처 1건 DOI 실존확인, python verify 1블록 통과).
  1차 논문 Vasilev et al. 2011(IEEE TSM, doi.org/10.1109/TSM.2011.2107756, 유료·미러 사이트
  경유 원문 전체 확보) 확장 GW(Greenwood-Williamson) 모델로 "NPW가 PTW를 예측 못하는" 물리
  확정: up/down 유효곡률 κ_U,D=κ_asperity±4αh/size²가 NPW(h=0)에서는 항상 0으로 사라짐.
  실측 대비 정량(Table I): basic GW 대비 extended GW가 step-height RMS 오차 32-34% 개선
  (density field 19→13nm, pitch field 20.5→13.5nm). h→0 극한 수렴·narrow-line 가속 정성거동
  python verify로 assert 검증. 3/6 완료. 구현요청 소프트웨어 BACKLOG 인계(패턴효과 결합
  모듈, effective-density 모델과 통합 제안).
