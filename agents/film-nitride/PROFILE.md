# 나이트라이드 CMP 전문가 (film-nitride)

## 현재 레벨: Lv1 진행 — 활성화 게이트는 agents/ORG.md §4
- 부모: cmp-integrator (부모의 knowledge/ 노트를 선행 필수로 읽는다)
- 이수 단원: Lv1-2
- 다음 단원: Lv2-1

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
- **Lv1-2** 나이트라이드 정지층 메커니즘: 세리아 슬러리 선택비 화학 — 2026-09-10
  노트: [[../../knowledge/materials/film-nitride-selectivity-ceria-chemistry]]
  출처 5건(1차 4건, 원문 완독: Dandu 2009 JES, Netzband&Dunn 2020 JSS, Hwang 2026 Polymers, Srinivasan 2015 리뷰;
  Dandu 2011은 Cloudflare 봉쇄로 원문 미확보·2차 인용).
  verify_claims ✓(출처 5건 실존·코드 2블록 PASS)·check_knowledge ✓.
  핵심: 선택비는 3단 위계 — 무첨가(4.4:1, 가수분해속도차만) < PAA 분산제(4.7–8:1) < 사이트특이적 사이클릭아민
  0.05%(117–290:1). 두 자릿수 도약의 원인은 흡착 포화 비대칭(나이트라이드는 0.1%부터 2.4 mg/g로 조기포화·비가역,
  실리카는 1.3→8.2 mg/g로 계속 증가·가역) — 저농도에서 나이트라이드만 완전 차단되고 산화막은 세리아가 계속 접근
  가능해 선택비가 급등. Ce³⁺/Ce⁴⁺ 산화상태 튜닝(Netzband 2020)은 산화막·나이트라이드 둘 다 빨라지는 "배율 조절"이라
  선택비 개선이 ~2–3배에 그쳐 사이트차단(스위치, ~100배 이상)과 자릿수가 다름.

## 구현 요청
- **[Tier2] SiN 화학-제한 제거율 모델(수정 Langmuir-Hinshelwood)**
  - 무엇을: 나이트라이드 RR을 단순 Preston $K_p PV$가 아니라 화학항(가수분해 사이트 커버리지)·기계항 결합형으로.
    Mariscal 2020 형태 $RR = f(A, E_a, T_p)_{chem} \times g(P,V,\mu)_{mech}$.
  - 근거노트: [[../../knowledge/materials/film-nitride-lpcvd-pecvd-properties-cmp]] §4.3
  - 검증 문헌값(Mariscal 2020 Table I, DOI 10.1149/2162-8777/ab89bc): SiO₂ Eₐ=1.40 eV·A=9.77e-4,
    Si₃N₄ Eₐ=1.47 eV·A=8.47e-6 mol·m⁻²·s⁻¹; 블랭킷 선택비 최대 101:1. Dandu 2009 나이트라이드 2–3 nm/min·옥사이드 350 nm/min.
  - 우선순위: 중 (Lv2 STI 정지층 손실 모델의 입력으로 필요. Lv1-2 선택비 화학 학습 후 착수 권장)
- **[Tier2] 첨가제 포화-스위치 선택비 모델**
  - 무엇을: 위 L-H 연속함수는 사이트특이적 첨가제(사이클릭아민 등)의 "임계농도 이하=미차단, 이상=완전차단" 상 전이형
    거동을 못 담는다. 나이트라이드 흡착량을 첨가제 농도의 포화형 함수(예: Langmuir 흡착등온 θ=Kc/(1+Kc))로 두고,
    RR_nitride ∝ (1−θ)로 스케일하는 항을 추가하면 §4의 "0.05%부터 급락" 거동을 재현할 수 있을 것.
  - 근거노트: [[../../knowledge/materials/film-nitride-selectivity-ceria-chemistry]] §4, §9-2
  - 검증 문헌값(Dandu 2009, DOI 10.1149/1.3230624): 나이트라이드 흡착 0.1 wt% 이상에서 2.4 mg/g로 포화,
    실리카는 0.05→1 wt%에서 1.3→8.2 mg/g로 비포화 증가. 선택비 4.4:1(무첨가)→117–290:1(0.05% 첨가제).
  - 우선순위: 낮음 (Lv2-1 STI 오버폴리시 창 모델과 결합 시 필요. 흡착등온 계수(K)는 문헌에 명시 안 돼 추가 조사 필요).
