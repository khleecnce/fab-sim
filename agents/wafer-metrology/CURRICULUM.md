# 커리큘럼 — 웨이퍼 계측·판정 전문가 (wafer-metrology)

> 규칙: 순서대로 학습. 단원마다 ①출처 있는 지식노트(knowledge/) ②자기시험 3문항+답(EXAMS.md) ③가능하면 수식의 코드 재현.
> 유료 논문은 미러 사이트 활용(사용자 지시 9/5). 출처 없는 수치는 '미검증' 표기.

- [x] Lv1-1 두께 계측 원리와 오차: 엘립소미터(투명막)·4점탐침/와전류(금속)·XRF·프로파일러·AFM — 막질별 적합성 (2026-09-05, knowledge/cmp/wafer-metrology-thickness-methods.md)
- [x] Lv1-2 균일도 지표 정의를 **문헌에서** 확정: SEMI 표준(MF1530 등)·Lee & Boning 1999·장비사 매뉴얼에서 TTV·WIWNU(half-range/σ/3σ)·CV·radial 지표의 정의와 측정 포인트 체계(49/81pt·엣지 제외·다이 맵)를 조사. 정의가 갈리면 병기. **결과로 `sim/metrics/uniformity.py`의 잠정 정의를 교체하고 근거 노트를 docstring에 링크** (2026-09-06, knowledge/cmp/uniformity-metrics-definitions-standards.md — uniformity.py 교체는 PROFILE.md 구현요청[High]으로 소프트웨어 부문 인계)
- [x] Lv2-1 표면 조도(Ra·Rq·Rz)와 AFM 스캔 크기 의존성, 막질·슬러리별 문헌값 범위, 조도가 후속 공정(리소·증착)에 미치는 영향 (2026-09-06, knowledge/cmp/wafer-surface-roughness-afm-scan-scale-dependence.md — SiC 정량값 확보(Wang 2026), SiO2/Cu/W 대표값·리소 영향은 원문 미확보로 다음 재시도 대상)
- [x] Lv2-2 패턴 지표: step height·dishing·erosion·잔막(residual)·엣지 롤오프 — 측정 구조물과 판정 기준(스펙 예시) (2026-09-07, knowledge/cmp/pattern-metrics-dishing-erosion-stepheight.md — dishing/erosion 기준면 3종 병기·ISO 5436-1형 스텝 LS·SEMI M77 ROA 규약의존성·ITRS 2007 스펙 재현; ISO/SEMI 원문 미확보는 2차 확인)
- [x] Lv3-1 최신 리뷰: 인라인 계측·가상 계측(virtual metrology)·계측 샘플링 최적화 (2026-09-08, knowledge/cmp/inline-virtual-metrology-sampling-optimization.md — 계측 3층위(in-situ/통합/오프라인=W2W vs L2L 루프, US6645780)·PHM 2016 CMP VM 벤치마크 표 재현(Di 2017 MSE 7.07)·FSCA 50→7점 NMSE 0.96 % + 동적 공간 샘플링 MSSI/WOI 재현(McLoone 2018)·static/adaptive/dynamic 로트 샘플링(Nduhura-Munga 2013); 미확보: Rao 2000·Jebri 2017·Breidung 2025 원문, 통합 계측기 정밀도/처리량 1차 비교)
- [x] Lv3-2 출력 스키마 확정 + 지표 계산 라이브러리 구현 (sim/metrics/) — 반경 프로파일·다이 맵 입력 → 전 지표 동시 산출, 테스트 포함 (2026-09-08, knowledge/cmp/wafer-metrology-output-schema-site-flatness-standards.md — ASTM F1530 GBIR/GF3R/GF3D/GFLR/GFLD/SBIR/SBID/SF3R/SF3D/SFQR/SFQD 11종 + Bow/Warp 확정, GBIR=TTV 항등식 재현; sim/ 구현은 트랙B 인계, PROFILE.md 구현요청 등록. 49점 산업관행의 SEMI 표준 근거는 3편 연속 미확보로 남김)

## 캘리브레이션 단원 (ORG.md §7.3 — Lv2 완료 후, G2 이후 활성)
- [x] Cal-1 고객 계측 데이터(포인트 좌표·두께·조도) 스키마 소유. 지표 정의 불일치(고객마다 다른 WIWNU 정의)를 매핑하는 규칙 (2026-09-19, knowledge/cmp/wafer-metrology-customer-data-schema-metric-definition-mapping.md — 원 데이터 형식 3+편(US6922603B1 49점·Bibby&Harwood 52점·MF1618 점수표준·US7539552B2 다이·NIST Griesmann 2007 EE 3→1.5mm/SFQR 26×8mm 전문확보) + WIWNU 정의 5종 각 1차(3σ/σ/half-range/full-range/range-over-sum, Kumar2019·Doko2026·Burwell2023·Zhu2022) + 매핑규칙(원점→D1~D5 재계산→정본 3σ/mean, 스칼라→σ계열 무손실·range 불가플래그, measured_quantity 축) + 샘플링편향 verify(정의만 2.78배 스프레드·49vs81 range 노이즈+4.6%/최외곽반경+23.5%) + 스키마개정 제안표는 cmp-data-engineer 인계. check_knowledge·verify_claims 통과)

## 확장 (Lv4 — 교수급)
- 최신 논문 상시 추적, 기존 모델의 한계 지적 및 개선 제안
- 부모·형제 에이전트와의 결합 모델 설계 리뷰
