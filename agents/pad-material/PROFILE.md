# 패드 소재 전문가 (pad-material)

## 현재 레벨: Lv2 진행중 — 활성화 게이트는 agents/ORG.md §4
- 부모: pad-mechanic (부모의 knowledge/ 노트를 선행 필수로 읽는다)
- 이수 단원: Lv2-1
- 다음 단원: Lv2-2

## 역할
폴리우레탄 조성·경도(Shore D)·기공률·점탄성(DMA)이 접촉역학·MRR·결함에 미치는 영향

## 선행 지식 (부모에게 상속)
- [[../../knowledge/materials/pad-viscoelasticity-dma]]
- [[../../knowledge/materials/hertz-gw-contact-mechanics]]
- [[../../knowledge/materials/pad-viscoelasticity-temp-frequency-dma]] (본인 Lv2-1 산출, 온도·주파수 심화)

## 실데이터 책임 (ORG.md §7.3)
패드 스펙시트(경도·밀도·기공) → 접촉모델 입력 변환 + 실측 프로파일 잔차

## 레벨 정의
Lv1 학부지식 → Lv2 대학원/리뷰논문 → Lv3 최신논문 추적 + 모델 구현 → Lv4 모델 개선 제안(교수급)

## 이수 기록
| 날짜 | 단원 | 산출 노트 | 자기시험 |
|---|---|---|---|
| 2026-09-06 | Lv1-1 PU 화학: 프리폴리머·경화제·발포 | knowledge/materials/pu-pad-chemistry-prepolymer-foam.md | EXAMS.md 3문항 |
| 2026-09-06 | Lv1-2 경도·탄성률·기공률 측정법과 문헌값 범위 | knowledge/materials/pad-hardness-porosity-measurement-methods.md | EXAMS.md 3문항 |
| 2026-09-07 | Lv2-1 점탄성 심화: 온도·주파수 의존 E'·E''·tanδ와 CMP 조건 매핑 | knowledge/materials/pad-viscoelasticity-temp-frequency-dma.md | EXAMS.md 3문항(Q7~Q9) |

(이후 크론이 갱신)

## 구현 요청 (sim/ 담당자에게 — 본인은 노트 verify만 수행)
| 무엇을 | 근거 노트 | 검증 문헌값 | 우선순위 |
|---|---|---|---|
| ~~패드 유효 탄성률의 온도 의존 모델 `E_pad(T)`~~ ✅ 2026-09-07 소프트웨어 부문 구현 완료(S21, `sim/tier2_physics/pad_viscoelastic_temperature.py`, 커밋 16d6147) — tanh 대신 로그-선형 구간보간(이산 앵커점만 있어 tanh 피팅파라미터를 지어낼 수 없었음), Cabot Table 1B 6패드x3앵커점 정확 재현 | knowledge/materials/pad-viscoelasticity-temp-frequency-dma.md §3.1, §4 | (재현 완료) | 높음 |
| ~~WLF shift factor 유틸~~ ✅ 2026-09-07 구현 완료(S21, `wlf_log_aT`/`wlf_reparametrize`, 같은 커밋) — 재매개화 8.86/101.6 재현(0.03%), "CMP PU 미피팅" docstring 명시 | 같은 노트 §2, §6 verify (1) | (재현 완료) | 중간 |
| Preston K_p 온도 보정 훅: `K_p_eff(T) = K_p0 · (E*(T0)/E*(T))^m` 형태로 GW A_r∝1/E* 함의(m=1)를 옵션화. 실측 대조 전까지 기본 OFF | 같은 노트 §4 | Khanna 2019 doi:10.1149/2.0121905jss: E'25/E'90 비 188/21/4 ↔ R90s/R15s ≈2/1.45/1 순서 일치(3점, 방향성만) | 낮음 (실측 대조값 부족 — 순서 재현 이상은 미검증) |

