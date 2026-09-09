# 나이트라이드 CMP 전문가 (film-nitride)

## 현재 레벨: Lv1 진행 — 활성화 게이트는 agents/ORG.md §4
- 부모: cmp-integrator (부모의 knowledge/ 노트를 선행 필수로 읽는다)
- 이수 단원: Lv1-1
- 다음 단원: Lv1-2

## 역할
SiN 막의 CMP 및 정지층 역할 — STI 선택비, 하드마스크 제거

## 선행 지식 (부모에게 상속)
- [[../../knowledge/cmp/slurry-components-overview]]

## 실데이터 책임 (ORG.md §7.3)
나이트라이드 실데이터 스키마 + 정지층 손실 보정 파라미터

## 레벨 정의
Lv1 학부지식 → Lv2 대학원/리뷰논문 → Lv3 최신논문 추적 + 모델 구현 → Lv4 모델 개선 제안(교수급)

## 이수 기록
- **Lv1-1** SiN 막 종류(LPCVD/PECVD)와 물성, CMP 제거 난이도 — 2026-09-10
  노트: [[../../knowledge/materials/film-nitride-lpcvd-pecvd-properties-cmp]]
  출처 7건(1차 5건, 원문 완독 4건: Dandu 2009 JES, Srinivasan 2015 리뷰, Mariscal 2020 JSS, Gan 2018 Surfaces; +Nejadriahi 2020 OE OA).
  verify_claims ✓(출처 7건 실존·코드 3블록 PASS)·check_knowledge ✓.
  핵심: LPCVD Si₃N₄(무수소·고밀도·22.5 GPa) > PECVD SiNₓ:H(수소 10–19 at%·13.6 GPa) 경도서열,
  제거는 가수분해→SiO₂→기계제거(chemically-limited), 선택비는 Eₐ 아닌 전지수인자 A(~115배)가 지배.

## 구현 요청
- **[Tier2] SiN 화학-제한 제거율 모델(수정 Langmuir-Hinshelwood)**
  - 무엇을: 나이트라이드 RR을 단순 Preston $K_p PV$가 아니라 화학항(가수분해 사이트 커버리지)·기계항 결합형으로.
    Mariscal 2020 형태 $RR = f(A, E_a, T_p)_{chem} \times g(P,V,\mu)_{mech}$.
  - 근거노트: [[../../knowledge/materials/film-nitride-lpcvd-pecvd-properties-cmp]] §4.3
  - 검증 문헌값(Mariscal 2020 Table I, DOI 10.1149/2162-8777/ab89bc): SiO₂ Eₐ=1.40 eV·A=9.77e-4,
    Si₃N₄ Eₐ=1.47 eV·A=8.47e-6 mol·m⁻²·s⁻¹; 블랭킷 선택비 최대 101:1. Dandu 2009 나이트라이드 2–3 nm/min·옥사이드 350 nm/min.
  - 우선순위: 중 (Lv2 STI 정지층 손실 모델의 입력으로 필요. Lv1-2 선택비 화학 학습 후 착수 권장)
