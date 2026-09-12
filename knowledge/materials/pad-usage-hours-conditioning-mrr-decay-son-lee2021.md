<!-- V2-SECTION: R3-pad | 작성 2026-09-12 | 정본: ARCHITECTURE-V2.md §3 -->
# 패드 사용시간(pad_usage_hours) 축 — 다시간 컨디셔닝 MRR 드리프트 정량화 (Son & Lee 2021)

> 에이전트: pad-mechanic Lv3 완료 후 상시 트랙 | 작성일: 2026-09-12
> [[pad-glazing-mechanism-mrr-decay]] [[pad-wear-glazing-mrr-decay]] [[../cmp/lpc-scratch-density-tail-correlation]]
> 정확도루프 갭: `sim/factors.py::_f_stab` PARTIAL(S 시간 안정성) — drivers=['pad_usage_hours',
> 'pad_wafer_count', 'disk_usage_hours']이지만 실제로 반응하는 항은 `time_s`(단발 연마 내 1~10분
> 로그감쇠, Jeong et al. 2024)뿐이다. 이 노트는 **패드 누적 사용시간(수십 시간 스케일)**이 MRR을
> 얼마나 감소시키는지 1차 문헌으로 확보한다 — Jeong 2024와는 시간축의 자릿수가 3자리 다르다
> (분 vs 시간).

## 1. 1차 문헌
**Son, J.; Lee, H. "Contact-Area-Changeable CMP Conditioning for Enhancing Pad Lifetime."
Applied Sciences 2021, 11(8), 3521. DOI: 10.3390/app11083521.** MDPI 오픈액세스(CC-BY),
Crossref로 저자·소속·발행일 실존 확인(Son: Tongmyong University, Lee: Dong-A University, Busan,
Korea, 2021-04-14 등록). MDPI 원문 사이트는 이 세션에서 봇 차단(Access Denied, Akamai edge)에
걸려 PDF 직접 저장은 실패했으나, **논문 요약·기술 스펙 표를 그대로 옮긴 제3자 기술문서**
(6ccvd.com, MPCVD 다이아몬드 컨디셔너 판매사의 "Original Source" 인용 페이지)에서 수치를
확보했다 — ⚠ **원문 PDF 직접 확인 아님, 초록·스펙표 수준의 재인용**으로 표기한다. DOI는
Crossref API로 실존 확인(2026-09-12), Semantic Scholar로 openAccessPdf(GOLD, CC-BY) 상태도
확인됐다.

## 2. 핵심 정량 데이터 (재인용 표 그대로)
실험: 200mm Si 웨이퍼(SiO2 1.5µm), Hard 폴리우레탄 KONI 패드, TSO-12 실리카 슬러리
150 mL/min, platen 93 rpm/conditioner 101 rpm, 컨디셔닝 하중 4 kgf, 연마시간 60초/회
(POLI-762, G&P Technology). 두 조건 비교:

| 조건 | 컨디셔너 구조 | 패드 수명(파손/불안정 전까지) | MRR 변화 | WIWNU |
|---|---|---|---|---|
| Case I (기존 swing-arm, 468 grit 단일디스크) | 전면 접촉 | **<16시간**(웨이퍼 파손) | 401.3 → 221.0 nm/min = **44.9% 감소**(16시간에 걸쳐) | 증가(수치 미확보) |
| Case II (분할형, 내부200/외부268 grit) | 5구역 독립하중 | **>20시간** 안정 | 387.7 → 359.0 nm/min = **7.4% 감소**(20시간에 걸쳐) | <3% 유지(20시간 내내) |

**핵심 관측**: 같은 초기 MRR 부근(401 vs 388 nm/min)에서 시작해 패드 마모 패턴(균일 vs
불균일)만 다르게 하면, 20시간 시점 MRR 감소폭이 **6.1배**(44.9%/7.4%) 차이 난다. 즉 시간 자체가
아니라 **컨디셔닝 구역별 마모 균일성**이 MRR 드리프트의 지배 인자라는 것이 이 논문의 핵심
주장이다 — 순수 "시간에 따른 감쇠"가 아니라 "불균일 마모 누적에 따른 감쇠"로 원인이 분해된다.

## 3. `_f_stab`에 대한 시사점 — 자릿수 분리, 이식 조건
1. **시간축 분리 확인**: Jeong 2024(§4, `_f_stab` 기존 근거)는 1~10분 범위의 **로그형** 드리프트
   (컨디셔닝 없는 단발 연마 내부), 이 논문은 **16~20시간** 범위의 **컨디셔닝 사이클 간** 드리프트다.
   두 축은 물리적으로 다른 메커니즘(단발 asperity 소성변형 vs 다회 컨디셔닝의 누적 불균일마모)이며
   `_f_stab` docstring이 이미 "이 회귀는 무-컨디셔닝 단발 연마의 초기 드리프트만 담는다"고 명시한
   경계와 정확히 일치 — 이 노트는 그 옆에 **별도 시간축**(pad_usage_hours)을 놓는다.
2. **팩에 이식 가능한 것은 절대 nm/min 값이 아니라 "시간당 감소율"뿐**: Case I 기준 44.9%/16h ≈
   시간당 2.8%(단순 선형 근사, 원문은 비선형일 가능성 있으나 원문 미확보라 곡률 확인 불가),
   Case II 기준 7.4%/20h ≈ 시간당 0.37%. 이 두 수치를 팩에 넣으려면 **컨디셔너 종류
   (구형 swing-arm 단일디스크 vs 분할형)가 팩의 실제 장비와 일치**해야 하는데, FabSim 팩
   (cu_h2o2_bta 등 5팩)은 컨디셔너 종류를 파라미터로 갖지 않는다 — **조건 불일치로 즉시 이식하지
   않는다**. 대신 "패드 사용시간이 길어지면 MRR이 시간당 0.4~3% 오더로 감소할 수 있다"는
   **오더(order-of-magnitude) 참고치**로만 기록한다.
3. **원문 미확보의 한계**: 이 데이터는 MDPI 사이트가 아니라 제3자 마케팅 기술문서에서 재인용했다.
   숫자 자체(401.3→221.0 등)는 소수점까지 구체적이라 지어낸 값이 아닐 가능성이 높지만(전형적인
   실측 보고 형식), **원문 그래프의 형태(선형 vs 로그 vs 계단)는 확인 못 했다** — 시간당 %만
   선형으로 가정한 것은 이 노트의 근사이지 문헌의 직접 서술이 아니다. **미검증**.

## 4. Δ와의 교차 참고 (오귀속 방지)
이 논문은 스크래치나 D99를 다루지 않는다 — 손상 유발도(Δ) 갭과는 무관하다. 다만 "불균일 마모 →
패드 국소 접촉압 변화 → MRR 드리프트" 메커니즘은 `_f_tau`(슬러리 전달, groove/porosity)나
κ(접촉강도)와 개념적으로 인접하지만, 이 논문은 컨디셔너 설계 비교 실험이라 조성 변수가 전혀
없어 그쪽 갭에도 직접 이식할 정량값은 없다.

## 5. 수식 재현 (sanity check — 원문 재인용 수치 산술 검증)

```python verify
# Son & Lee 2021, Applied Sciences 11(8) 3521, DOI:10.3390/app11083521
# 값은 6ccvd.com 기술문서(제3자 재인용, "Original Source" 표기)에서 확보 -- 원문 PDF 직접 미확인.

mrr_case1_start, mrr_case1_end, hours_case1 = 401.3, 221.0, 16.0   # nm/min, 컨디셔닝 시간
mrr_case2_start, mrr_case2_end, hours_case2 = 387.7, 359.0, 20.0

reduction_pct_case1 = (mrr_case1_start - mrr_case1_end) / mrr_case1_start * 100.0
reduction_pct_case2 = (mrr_case2_start - mrr_case2_end) / mrr_case2_start * 100.0

# 재인용 문서가 명시한 44.9% / 7.4%와 대조 (1% 이내 재현)
assert abs(reduction_pct_case1 - 44.9) < 1.0, f"Case I 감소율 재계산 불일치: {reduction_pct_case1:.2f}%"
assert abs(reduction_pct_case2 - 7.4) < 1.0, f"Case II 감소율 재계산 불일치: {reduction_pct_case2:.2f}%"

ratio = reduction_pct_case1 / reduction_pct_case2
print(f"Case I 감소율={reduction_pct_case1:.2f}%, Case II 감소율={reduction_pct_case2:.2f}%, 비율={ratio:.2f}배")
assert 5.0 < ratio < 7.0, f"두 조건 감소율 비율이 예상 오더(6배 근방)를 벗어남: {ratio:.2f}"

# 시간당 단순 선형 감소율 근사 (원문 곡률 미확인 -- 근사 표기)
rate_per_hour_case1 = reduction_pct_case1 / hours_case1
rate_per_hour_case2 = reduction_pct_case2 / hours_case2
print(f"시간당 감소율(선형 근사): Case I={rate_per_hour_case1:.2f}%/h, Case II={rate_per_hour_case2:.2f}%/h")
assert 2.0 < rate_per_hour_case1 < 3.5, rate_per_hour_case1
assert 0.2 < rate_per_hour_case2 < 0.6, rate_per_hour_case2
```

### 5.1 재현 결과
Case I: 44.9%/16h → 시간당 약 2.81%. Case II: 7.4%/20h → 시간당 약 0.37%. 두 조건 비율 약
6.07배 — assert 통과. 원문(재인용) 수치와 일치.

## 6. 정직한 미검증 목록
- ⚠ **원문 PDF 미확보**: MDPI 사이트 봇 차단으로 이번 회차엔 논문 본문을 직접 읽지 못했다.
  제3자 재인용(6ccvd.com)의 수치를 사용했으며, Crossref/Semantic Scholar로 DOI·저자·OA 상태만
  독립 검증했다. 다음 회차에 미러 사이트나 다른 경로로 원문을 재시도할 것.
- ⚠ **팩 파라미터 미이식**: 컨디셔너 설계(swing-arm vs 분할형)가 FabSim 팩에 없는 변수라 이 두
  수치(2.81%/h, 0.37%/h)를 `sim/factors.py`에 직접 넣지 않는다 — 오더 참고치로만 노트에 기록.
- ⚠ **선형 가정**: 시간당 % 감소는 이 노트가 근사한 것이지 원문이 직접 보고한 형태가 아니다.
  Jeong 2024(§4)가 같은 계열 현상(MRR 드리프트)에서 로그형이 선형보다 우수함을 보였으므로,
  이 16~20시간 축도 로그형일 가능성이 있으나 확인 불가 — 미검증.
- ⚠ **화학종 특정**: TSO-12 실리카 슬러리, SiO2 CMP 계에서 얻은 값이다. 세리아·알루미나·구리 CMP로
  외삽 불가.

## 7. 구현 요청 (agents/pad-mechanic/PROFILE.md에 등록 — 소프트웨어 부문이 코딩)
- 무엇을: `_f_stab`에 `pad_usage_hours` 드라이버가 실제로 반응하도록 두 번째 시간축(시간 단위,
  로그 또는 선형)을 추가하는 것을 검토. 단, **컨디셔너 설계 변수(균일 마모 여부)가 팩에 없어
  값을 어느 쪽(2.81 %/h vs 0.37 %/h)으로 잡을지 근거가 없다** — 이게 선행 조건.
- 근거 노트: 본 노트 §5 verify 블록.
- 검증에 쓸 문헌값: Case I 44.9%/16h, Case II 7.4%/20h (Son & Lee 2021, 재인용).
- 우선순위: 낮음 — 컨디셔너 설계 변수를 팩에 추가하는 것이 선행 과제이고, 그 근거가 아직 없다.
  당장은 정성적 참고(패드 수명 관리가 균일 마모에 지배된다)로만 활용.

## 8. 출처
- Son, J.; Lee, H. (2021). "Contact-Area-Changeable CMP Conditioning for Enhancing Pad
  Lifetime." Applied Sciences 11(8), 3521. DOI: 10.3390/app11083521 (MDPI, CC-BY, OA).
- 재인용: https://6ccvd.com/research/literature-reviews/2021/04/contact-area-changeable-cmp-conditioning-for-enhancing-pad-lifetime-3156965014/
  ("Original Source" 섹션에 논문 인용 명시, 기술 스펙표가 원문 표 형식 그대로 재구성됨)
- Crossref API 조회(2026-09-12): DOI resolve 성공, 저자·소속·발행일 일치 확인.
