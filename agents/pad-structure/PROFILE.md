# 패드 구조 전문가 (pad-structure)

## 현재 레벨: Lv3 완료(6/6) — 활성화 게이트는 agents/ORG.md §4
- 부모: pad-mechanic (부모의 knowledge/ 노트를 선행 필수로 읽는다)
- 이수 단원: Lv1 (Lv1-1, Lv1-2 완료), Lv2 (Lv2-1, Lv2-2 완료), Lv3 (Lv3-1, Lv3-2 완료)
- 다음 단원: Cal-1 (패드 구조 스펙 → 엣지 효과 보정 파라미터, G2 이후 활성)

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

| Lv3-1 | 2026-09-08 | `knowledge/materials/pad-groove-cfd-micropattern-optimal-design.md` | 1차 논문 1편(Sadri Mofakham 2024, DOI:10.1149/2162-8777/ad8fd3, ECS JSS CC-BY 원문 전체 확보), verify 블록 통과(DCA/DICL 표 재현, Re<2300 층류 정합성 sanity, DICL-RR 단조증가 vs 압력강하-RR 비단조 재현). 리뷰 논문 2편(Physics of Fluids DOI:10.1063/5.0312258, SiC involute groove SSRN 5358338)은 미러 사이트·SSRN 접속 실패로 **원문 미확보**, 초록 수준만 기록 |
| Lv3-2 | 2026-09-18 | `knowledge/materials/pad-groove-stack-pressure-flow-model-spec.md` | 구현 명세 단원. 신규 1차 5편(Byrne 2011 DOI:10.1177/09544054JEM2187 리프린트 발췌; Choi&Dornfeld 2004 eScholarship OA 2층 회귀 DOI:10.1557/proc-816-k4.4; Bae 2022 DOI:10.1016/j.mssp.2022.106968; Rosales-Yeomans 2008 DOI:10.1149/1.2963268; Wang&Yang 2007 DOI:10.1149/1.2716558) + Lo&Lin·Mu·Cho 인용. verify 4블록 통과: (a) die-scale H/L 회귀 4.946–8.108+설계규칙 3부호, wafer-scale 엣지 피크비 3계열(Byrne 1.732/2.391<Wang 4.47, Lo&Lin 밴드), BOEF λ 6–9mm 준해석; (b) P_land=P/(1−GFQ) ×1.25/1.5/1.75+컨덕턴스 D³급 재사용; (c) 동심원 대비 방사 SST−25%·RR+24.6%, 나선 RR+24% 교차수렴; (d) sim/tier2 중복·부재 점검. **Lv3 완료** |

## 구현 결과 (소프트웨어 부문 회신)
- `groove_wear_flow_state` 등 9함수 구현 완료 — `sim/tier2_physics/pad_groove_wear_flow.py`(S25, 커밋 236e5b6, 2026-09-08). 노트 §5 verify A/D/E 정량값 그대로 재현 테스트 18건. engine 미등록(Recipe 스키마 부채, S24 이하와 동일 지위). `pattern_dicl_mrr_factor`는 데이터점 3개뿐이라 이번 회차 범위 밖(미착수).

## 구현 요청 (sim/ 담당자에게 — pad-structure는 직접 넣지 않음)

| 무엇을 | 근거 노트 | 검증 문헌값 | 우선순위 |
|---|---|---|---|
| `groove_wear_flow_state(D0, cut_rate, GFQ, h_land, q_actual, t)` — 깊이 D(t)=D0−cut_rate·t, 저류 부피 V_groove(D)∝D, τ(D)=(V_land+V_groove)/q_actual, 직사각 채널 컨덕턴스비 G(D)/G(D0), 잔존비 D/D0로 초기/중기/말기 플래그(말기 임계 0.20–0.35) | `knowledge/materials/pad-groove-wear-flow-change-end-of-life.md` §2, §4, §5 | Mu 2016 Table 2 V_land/V_groove(3 PSI: 0.38/2.66, 0.31/4.41, 0.27/5.64 cm³); Liu 2024 초록 신선분율 72.34%(850 μm)→100%(250 μm)@0.51 s; US8192257B2 250 μm·0.25 μm/wafer→600–800장; US11938584B2 잔존부피 20% 하한 | 중 (Lv3-2 sim/tier2 선행) |
| `pattern_dicl_mrr_factor(dca, dicl)` — DICL 증가에 따른 정성적 MRR 보정 계수(단조 증가, GFQ 기반 land 모델과는 별도 축). 사각-원 DICL=3.7→기준 원 DICL=2.0 대비 MRR 약 1.34배(300 g/cm² 조건). 정량 함수형은 미정(3점 데이터만 존재) — 형태 제안은 소프트웨어 부문 결정 | `knowledge/materials/pad-groove-cfd-micropattern-optimal-design.md` §1.3 | Sadri Mofakham 2024 Fig.14: 원 745, 타원 751, 사각-원 ~1000 Å/min @300 g/cm² | 낮음 (데이터점 3개뿐, GFQ 모델과 통합 필요성 §4 미해결 먼저 정리) |
| `land_pressure_amplification(P_nom, GFQ) -> P_land = P_nom/(1-GFQ)` — 그루브 면적분율만큼 줄어든 land 접촉면에 하중이 몰려 국소 접촉응력이 증배. **주의: GW/3체마모 레이어의 국소압 입력이지 Preston 면적평균 MRR에 곱하지 말 것**(접촉면적 감소가 지배하면 net MRR은 오히려 낮아짐, Wang&Yang 2007). engine 미등록(Recipe에 GFQ 필드 필요) | `knowledge/materials/pad-groove-stack-pressure-flow-model-spec.md` §2 | GFQ 0.20/0.333/0.429 → ×1.25/1.5/1.75 (Mu 2016 3종); 하중평형 항등식 | 중 (Lv3-2 핵심, GW 레이어 결합 선행) |
| `edge_pressure_profile(E1,t1,E2,t2,h_w; load_path)` — 2층 직렬스프링 기초 k_eff=1/(t1/E1+t2/E2), 엣지롤오프 폭 스케일 λ=(4·D_w/k_eff)^¼(오더·방향만 신뢰), 엣지 피크비는 **하중경로 인자**로 [1.7(리테이너링 분담)–4.5(캐리어필름 단독)]. 절대값 하드코딩 금지 — E_pad 유효압축률은 pad-material 캘리브레이션 대상. Lv2-1 단일층 R을 2층으로 확장 | `knowledge/materials/pad-groove-stack-pressure-flow-model-spec.md` §1 | Byrne 2011 피크비 1.732/2.391, Wang 4.47, Lo&Lin 1.68–2.08; λ 6–9 mm 오더; 서브패드 뻣뻣↑→λ↓(Xin 방향) | 중 |
| `groove_type_factor(type)` — 그루브 유형(동심원=1 기준/방사/나선)별 상대 SST·MRR 계수. 방사·나선이 동심원 대비 ~+24% MRR·SST 단축으로 수렴. 정량은 유형별 단일 앵커(본문 미확보 다수)라 순위·방향 우선 | `knowledge/materials/pad-groove-stack-pressure-flow-model-spec.md` §3 | Cho 2022 SST 21.52→16.06 s(−25%); Bae 2022 Cu RR 4051→5047 Å/min(+24.6%); Rosales-Yeomans 2008 RR +24%/COF +28% | 낮음 (유형별 정량 앵커 단일, 통합 전 근거 보강 권장) |
