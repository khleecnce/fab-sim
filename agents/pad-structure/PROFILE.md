# 패드 구조 전문가 (pad-structure)

## 현재 레벨: Lv2 완료(4/6) — 활성화 게이트는 agents/ORG.md §4
- 부모: pad-mechanic (부모의 knowledge/ 노트를 선행 필수로 읽는다)
- 이수 단원: Lv1 (Lv1-1, Lv1-2 완료), Lv2 (Lv2-1, Lv2-2 완료)
- 다음 단원: Lv3-1 (최신 리뷰: 최적 그루브 설계, CFD 기반 유동 해석)

## 역할
그루브(동심원·XY·나선) 형상·피치·깊이와 서브패드 적층이 슬러리 유동·압력 분포·엣지 효과에 미치는 영향

## 선행 지식 (부모에게 상속)
- [[../../knowledge/materials/pad-structure-groove-subpad]]

## 실데이터 책임 (ORG.md §7.3)
패드 구조 스펙 → 엣지 효과 보정 파라미터 정의

## 레벨 정의
Lv1 학부지식 → Lv2 대학원/리뷰논문 → Lv3 최신논문 추적 + 모델 구현 → Lv4 모델 개선 제안(교수급)

## 이수 기록
(크론이 갱신)

| 단원 | 일자 | 노트 | 비고 |
|---|---|---|---|
| Lv1-1 | 2026-09-07 | `knowledge/materials/pad-groove-slurry-transport.md` | 1차 특허 2건(EP0806267A1, JP5767280B2), verify 블록 통과(GFQ 정합·면적비 재현) |
| Lv1-2 | 2026-09-07 | `knowledge/materials/pad-groove-geometry-contact-area-flow-resistance.md` | 1차 논문 2편(Mu 2016 DOI 10.1016/j.mee.2016.02.035 미러 사이트 확보, Cho 2022 DOI 10.3390/app12094339 CC-BY OA), verify 블록 통과(GFQ 실측 재현·η 비단조/수확체감 실측 대조 3계열) — **Lv1 완료** |
| Lv2-1 | 2026-09-07 | `knowledge/materials/pad-subpad-stiffness-edge-nonuniformity.md` | 1차 논문 1편(Lo & Lin 2005, DOI 10.1016/j.jmatprotec.2005.01.010, 미러 사이트 원문 전체 확보), verify 블록 통과(T0·E0 축 두 계열 문헌표 재현: T0 변화율 15.7%, E0 변화율 6.5%) |
| Lv2-2 | 2026-09-08 | `knowledge/materials/pad-groove-wear-flow-change-end-of-life.md` | 1차 논문 2편(Irfan 2025 DOI 10.3390/jmmp9030095 CC-BY 원문 전체; Liu 2024 DOI 10.1149/2162-8777/ad83ef 초록만—IOP 캡차) + 특허 2건(US8192257B2, US11938584B2 전문) + Mu 2016 재활용, Park 2008 초록. verify 5블록 통과(Micron×Cabot 수명 교차 800=800, Liu CSTR 외삽 98.7% vs 100%, Irfan SST 오차 1/2 재현·1/2 불일치 기록, Mu Table2 6/6, 컨덕턴스 D³급) — **Lv2 완료** |

## 구현 요청 (sim/ 담당자에게 — pad-structure는 직접 넣지 않음)

| 무엇을 | 근거 노트 | 검증 문헌값 | 우선순위 |
|---|---|---|---|
| `groove_wear_flow_state(D0, cut_rate, GFQ, h_land, q_actual, t)` — 깊이 D(t)=D0−cut_rate·t, 저류 부피 V_groove(D)∝D, τ(D)=(V_land+V_groove)/q_actual, 직사각 채널 컨덕턴스비 G(D)/G(D0), 잔존비 D/D0로 초기/중기/말기 플래그(말기 임계 0.20–0.35) | `knowledge/materials/pad-groove-wear-flow-change-end-of-life.md` §2, §4, §5 | Mu 2016 Table 2 V_land/V_groove(3 PSI: 0.38/2.66, 0.31/4.41, 0.27/5.64 cm³); Liu 2024 초록 신선분율 72.34%(850 μm)→100%(250 μm)@0.51 s; US8192257B2 250 μm·0.25 μm/wafer→600–800장; US11938584B2 잔존부피 20% 하한 | 중 (Lv3-2 sim/tier2 선행) |
