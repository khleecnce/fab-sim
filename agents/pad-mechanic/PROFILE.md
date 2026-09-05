# 패드 역학자 (Pad Mechanic)

## 임무
폴리우레탄 패드의 점탄성, asperity 접촉, groove 설계, 마모가 압력분포·MRR·균일도에 미치는 영향을 모델링

## 현재 레벨: Lv3 완료 → 커리큘럼 전체 이수 (2026-09-04)
- 이수 단원: Lv1-1, Lv1-2, Lv2-1 접촉역학(Hertz/GW), Lv2-2 GW 역문제(명목압력→실접촉압력), Lv3-1 패드 마모·glazing,
  Lv3-2 GW-Preston 연결(Kp 물리적 분해 + 문헌값 재현)
- 다음 단원: 없음 — CURRICULUM.md 전 단원 [x] 완료. Lv4(교수급 확장)는 상시 트랙으로 전환 가능,
  단 Phase 0 우선순위상 disk-conditioner로 학습 자원 이동 예정
- 승급 근거: Lv2 단원 2/2 이수로 Lv2 승급(2026-09-04). Lv3 단원 2/2(Lv3-1+Lv3-2) 이수로 **Lv3 승급 완료(2026-09-04)**

## 이수 기록
| 날짜 | 단원 | 산출 노트 | 자기시험 |
|---|---|---|---|
| 2026-09-04 | Lv1-1 고분자 점탄성 기초 | knowledge/materials/pad-viscoelasticity-dma.md | EXAMS.md 3문항 |
| 2026-09-04 | Lv1-2 CMP 패드 구조 (발포체·groove·subpad) | knowledge/materials/pad-structure-groove-subpad.md | EXAMS.md 3문항 |
| 2026-09-04 | Lv2-1 접촉역학 (Hertz, Greenwood-Williamson) | knowledge/materials/hertz-gw-contact-mechanics.md | EXAMS.md 3문항 |
| 2026-09-04 | Lv2-2 GW 역문제 (명목압력→국소압력) | knowledge/materials/gw-nominal-vs-local-pressure.md | EXAMS.md 3문항 |
| 2026-09-04 | Lv3-1 패드 마모·glazing과 MRR 드리프트 | knowledge/materials/pad-wear-glazing-mrr-decay.md | EXAMS.md 3문항 |
| 2026-09-04 | Lv3-2 GW-Preston 연결 (Kp 물리적 분해) | (신규 지식노트 없음, gw_preston_link.py 코드+docstring이 지식 근거 겸함) | EXAMS.md 3문항 |

## 구현 기여
<!-- sim/ 모듈 기여 기록 -->
- 2026-09-04: sim/tier2_physics/viscoelastic_maxwell.py — Maxwell 점탄성 모델(저장/손실탄성률) self-test 5/5 PASS. Lv1 sanity check용, MRR/WIWNU 계산엔 아직 미사용.
- 2026-09-04: sim/tier2_physics/gw_contact.py — Hertz(F~delta^1.5) + GW 지수분포 접촉모델 수치적분 구현, self-test 5/5 PASS (지수분포 A_r/W 비율이 분리거리 d와 무관함을 폐형식 vs 수치적분으로 확인, max_dev=8.6e-6). 아직 preston.py/MRR과 미연결(Lv2-2에서 K_p 물리적 분해 예정) — Lv3-2 최종구현의 사전 sanity-check 모듈.
- 2026-09-04: sim/tier2_physics/gw_pressure_solve.py — GW 힘평형 역문제(명목압력→분리거리 d, Brent법) 구현, self-test 5/5 PASS. 핵심 검증: 14→96kPa(6.9배) 압력변화에도 평균 실접촉압력 p_r=W/A_r이 <0.1% 편차로 불변(GW 지수분포 이론의 정성 결론을 수치 재현), 대신 접촉점수 n은 W에 거의 선형 비례(n/W 변동 1.78e-15). preston.py/MRR과는 아직 미연결(Lv3-2에서 정식 연결 예정).

- 2026-09-04: sim/tier2_physics/pad_wear_glazing.py — Shi&Ring(2010) population balance의 Borucki 극한(유체 없음)을
  이산 Monte-Carlo asperity 집단(2만~20만개)으로 근사 구현, Archard 마모법칙 오일러 시간적분. self-test 5/5 PASS:
  (1) 무컨디셔닝 시 평균 asperity 높이 단조 비증가(glazing, Oliver 실측 정성적 일치), (2) MRR(t) 단조 감소(30스텝
  2.66% 감쇠), (3) 감쇠 수확체감(초반 감쇠>후반 감쇠, 큰 asperity 우선 마모 - Eq.10 sqrt(delta) 특성 재현),
  (4) 이산모델 t=0 결과가 연속 gw_numeric()과 1.18% 오차로 교차검증, (5) 마모에 따른 p_r 변화(2.66%)가
  Lv2-2에서 확인한 "정적압력변화 시 p_r 불변(<0.1%)"과 다른 레짐임을 대비 확인. Preston K_p가 상수가 아니라
  "패드 컨디셔닝 상태의 함수"라는 지식노트 결론을 코드로 뒷받침. gw_contact.py의 hertz_force/hertz_contact_area
  재사용(중복 재구현 없음). 아직 유체결합(Reynolds)·컨디셔닝 B/D항·preston.py 정식 연결은 미구현(Lv3-2 범위).

- 2026-09-04: sim/tier2_physics/gw_preston_link.py — GW 접촉점수 n(P)를 매개로 Preston Kp의 미시적
  기원을 분해(MRR = alpha_removal * n_contacts(P) * V). self-test 4/4 PASS: (1) n(P) 선형적합 잔차
  2.46e-13(사실상 완전선형, Lv2-2 결론 재확인), (2) 문헌 캘리브레이션점(P=20.7kPa, Kp=1e-13, V=0.8m/s)에서
  GW-link/Preston-direct 항등 확인, MRR=99.36 nm/min(문헌범위 50-1000 nm/min 안, STI 254.05 nm/min과
  같은 자릿수 — Kp=1e-13 자체가 preston.py에서 이미 "다소 낮은 편"으로 명시된 값이라 정확 일치는 기대치 아님),
  (3) 14/48/96kPa 세 압력점 모두 GW-link vs Preston-direct 편차 <5e-12(n(P) 완전선형성 덕분 정의상 일치에
  가까움), (4) 역산된 Kp_physical(=alpha_removal*dn/dP)이 문헌 Kp=1e-13과 정확히 일치(항등식 검증,
  독립적 예측 아님을 docstring에 명시). **Phase 0 "패드: GW 접촉모델" 항목 완전 완료 처리** — 순방향
  (gw_contact)+역문제(gw_pressure_solve)+마모시계열(pad_wear_glazing)+Preston 정식연결(gw_preston_link)
  4개 모듈 체인 완성. pytest 전체 40/40 PASS.
