# 시험 웨이퍼 전문가 (wafer-type)

## 현재 레벨: [활성] (G1 개방 2026-09-06)
- 부모: cmp-integrator (부모의 knowledge/ 노트를 선행 필수로 읽는다)
- 이수 단원: Lv1-1, Lv1-2, Lv2-1 (2026-09-06), Lv2-2 (2026-09-07)
- 다음 단원: Lv3-1

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


## 이수 기록 (크론 갱신, 2026-09-07)
- 2026-09-07: Lv2-2 완료. knowledge/cmp/wafer-type-metrology-techniques-suitability.md
  (check_knowledge ✓, verify_claims ✓ — 출처 10건 실존확인(DOI 4·arXiv 2·특허 4), python verify 1블록
  (A)~(E) 통과). 핵심: NPW에서 유효한 기법이 PTW에서 제약되는 세 물리 — ①스팟 vs 패드(US7095511:
  피처 0.1–10 µm, 패드 100 µm; 70° 입사 타원 스팟 50→146 µm), ②혼입광·회절(US9574992 40 µm 타깃),
  ③투과깊이(Cu d_p=14.8 nm, Johnson&Christy 1972 → SE 금속 두께 불가). 스타일러스 팁 R=1.52 µm(NIST) →
  w<3 µm 트렌치 미도달·Table 3 불확도 계수; AFM 4픽셀 규칙(Ahn et al. 2019 arXiv 재현, 높이 2% 이내);
  XRF 지수법칙(US9644956)·NIST XCOM μ/ρ로 Cu 1 µm 비선형 2.3% 확인. 막질×기법×NPW/PTW 적합성 표 작성.
  미검증: SiO₂/Si Ψ·Δ 실측 대조값(Fresnel 자기일관만), Stenzel 2019 본문, 기업자료(스팟·반복도) 전부 2차.
  4/6 완료. 다음 단원: Lv3-1.

## 구현 요청 (2026-09-07, wafer-type Lv2-2)
1. **PTW/NPW 메타데이터 스키마 필수 필드 추가** — `spot_size_um`, `pad_size_um`, `local_density`,
   `probe_radius_um`(스타일러스/AFM), `pixel_pitch_nm`(AFM), `technique`(SE/SR/EC/4PP/XRF/stylus/AFM).
   근거: knowledge/cmp/wafer-type-metrology-techniques-suitability.md §6.2. 검증값: 스팟 장축 = 빔/cos θ
   (50 µm@70° → 146 µm), 패드 100 µm(US7095511). 우선순위: 높음(Cal-1 선행).
2. **측정 적합성 검사 함수** `metrology_suitability(film, wafer_type, technique, spot_um, pad_um, aoi_deg,
   feature_w_um, probe_r_um)` → 경고 리스트. 규칙: 금속+SE→불가(Cu d_p 14.8 nm 기준 50 nm 문턱), SE 타원
   장축>패드→불가, 스타일러스 w<2R→깊이 과소평가 경고, AFM 픽셀 피치>폭/4→폭 신뢰불가 경고, XRF+PTW→
   면적가중 평균 경고. 검증 문헌값: 위 노트 §7 verify (A)~(E) 상수. 우선순위: 중.
3. **XRF 강도-두께 함수** `xrf_intensity_fraction(mu_rho_cm2_g, rho_g_cm3, t_um, geometry_factor=1)` =
   1−exp(−μ̄ρt). 검증값: Cu 52.55 cm²/g·8.96 g/cm³에서 1 µm → 4.60%(비선형 2.3%), 15 µm → 51%. 우선순위: 낮음.
