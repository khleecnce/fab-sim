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
| 패드 유효 탄성률의 온도 의존 모델 `E_pad(T)` — Tg 근방 전이를 표현하는 구간 함수(예: 유리질 평탄부–전이–고무질 평탄부를 tanh 또는 로그-시그모이드로 보간). GW/Hertz 접촉모듈의 E* 입력을 상수에서 T의 함수로 교체 | knowledge/materials/pad-viscoelasticity-temp-frequency-dma.md §3.1, §4 | Cabot US20170087688A1 Table 1B: Epic D100 E'(25/50/80 °C)=1000/141/19 MPa, tanδ 피크 56 °C; 발명패드 1D 1590/317/5 MPa, Tg(DSC) 43.6 °C — 6종 모두 25→50 °C 3~10배 감소 재현 | 높음 (Khanna 2019: E' 온도민감도가 MRR 시간드리프트의 직접 원인) |
| WLF shift factor 유틸 `wlf_shift(T, Tr, C1, C2)` + 기준온도 재매개화 함수 — E'(ω,T) 마스터커브 이동용. 기본 상수는 보편값(17.44, 51.6 K @Tg)로 두되 "CMP PU 미피팅" 플래그를 상수에 명시 | 같은 노트 §2, §6 verify (1) | WLF 1955 doi:10.1021/ja01619a008; 17.44/51.6 → Tr+50 K 시 8.86/101.6 K 재현(0.03% 이내) | 중간 (Tg 이상 구간 전용, 30 °C 이하 유리질엔 Arrhenius 필요) |
| Preston K_p 온도 보정 훅: `K_p_eff(T) = K_p0 · (E*(T0)/E*(T))^m` 형태로 GW A_r∝1/E* 함의(m=1)를 옵션화. 실측 대조 전까지 기본 OFF | 같은 노트 §4 | Khanna 2019 doi:10.1149/2.0121905jss: E'25/E'90 비 188/21/4 ↔ R90s/R15s ≈2/1.45/1 순서 일치(3점, 방향성만) | 낮음 (실측 대조값 부족 — 순서 재현 이상은 미검증) |

