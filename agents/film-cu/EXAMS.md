# 자기시험 — 구리 CMP 전문가 (film-cu)

> 단원 이수 시 3문항 + 모범답안을 여기에 추가한다. 답안에는 출처를 단다.

## Lv1-1 Cu CMP 3단계(벌크·소프트랜딩·배리어)와 슬러리 요구 (2026-09-08)

**Q1.** Cu damascene CMP가 왜 한 가지 압력·슬러리로 한 번에 밀지 않고 여러 단계(벌크→소프트랜딩→
배리어)로 나뉘는가?
**A1.** 벌크 제거는 처리량을 위해 고압·고MRR이 필요하지만, 배리어 근접부에서는 얇아진 Cu가
과도한 압력·화학적 용해에 노출되면 dishing이 급격히 커진다 — 두 요구가 상충한다. 특허
US2009/0057264A1(Applied Materials)은 벌크(~1.8 psi, ~9000 Å/min) → rate quench 전이
(~0.5 psi) → 소프트랜딩(~1.3 psi, ~1800 Å/min) → 잔류제거(≤0.3 psi)로 다운포스·제거속도를
계단식으로 낮춘다. 소프트랜딩/벌크 제거속도 비는 약 20%(0.15~0.25 범위, verify 재현).

**Q2.** "Rate quench" 전이 스텝의 목적은 무엇이며, 왜 순수 기계적 변수(압력)만의 문제가 아닌가?
**A2.** 벌크 단계에서 패드 위에 누적된 Cu²⁺ 부산물이 BTA 등 억제제의 부동태(passivation) 효과를
떨어뜨린다([[../../knowledge/cmp/surface-chemistry-cu-w-pourbaix-passivation]] 참조). Rate
quench는 슬러리·린스 유량을 늘려 이 Cu 이온 농도를 씻어내 억제제 효과를 회복시키는 스텝 —
특허 원문 "reduce the copper ion concentration on the polishing pad... preserving passivation
agent effectiveness". 즉 국소 전기화학 평형을 재설정하는 것이지 다운포스 조절만이 아니다.

**Q3.** Pan(1999)의 실측에서, 광폭(100µm) 트렌치의 "최적 오버폴리시" 조건과 5µm pitch 90%
밀도 라인/스페이스 어레이(40% 오버폴리시)의 Cu 두께손실 비율은 각각 얼마이며 어느 쪽이 더 큰가?
**A3.** 광폭 트렌치 최적OP: 500Å 디싱 / 5000Å 목표두께 = 약 10%. 고밀도 어레이 40%OP: 목표두께의
약 70%(erosion이 주 원인). 후자가 훨씬 크다 — erosion 지배(고밀도)가 dishing 지배(광폭
트렌치·최적OP)보다 두께손실 비율이 크다는 것이 이 논문의 핵심 관찰
([[../../knowledge/cmp/cu-cmp-three-step-process-slurry-requirements]] §6 verify 블록 재현,
[[../../knowledge/cmp/pattern-dependent-dishing-erosion]]과 연결).

출처: [[../../knowledge/cmp/cu-cmp-three-step-process-slurry-requirements]] (US2009/0057264A1,
Pan et al. 1999 CMP-MIC, Park et al. 1998 VMIC)
