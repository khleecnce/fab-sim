<!-- V2-SECTION: R2-slurry | 작성 2026-09-09 | 정본: ARCHITECTURE-V2.md §3 -->
# D99-스크래치 정량 관계 확정 — Hitachi 세리아 CMP 특허(US8439995B2) 실시예

> 에이전트: slurry-abrasive Lv2-1 (선행: [[abrasive-d99-composite-particle-versum2019]])
> [[abrasive-d99-composite-particle-versum2019]] [[abrasive-d99-spec-cross-pack-comparison]]
> [[lpc-scratch-density-tail-correlation]] [[abrasive-d99-alumina-search-and-generic-ratio]]

## 1. 왜 필요한가
지난 3개 노트가 D99 실측값(Versum 특허 158.5~316.7nm)과 D99/D50 비율(1.82~5.00배)까지는
확보했으나, **D99가 커질 때 스크래치 카운트가 실제로 몇 배 늘어나는지(함수형)** 를 직접
보여주는 문헌은 아직 없었다. `sim/factors.py::_f_delta`는 `(d99/d99_ref)^n` (n=3.0, 문헌
근거 없는 가정값)을 그대로 쓰고 있다. 이 노트는 스크래치 카운트를 **직접 관측치로 보고**한
1차 문헌(Hitachi Chemical 특허, 세리아 STI/ILD CMP)에서 D99-스크래치 대응쌍을 확보해
n을 실측 데이터로 회귀한다.

## 2. 1차 문헌 — US 8,439,995 B2 (Hitachi Chemical Co., Ltd.)
**"Abrasive compounds for semiconductor planarization" (계열 출원 JP10-154673 등 인용),
등록번호 US 8,439,995 B2.** patents.google.com에서 원문 PDF 무료 확보
(`papers/US8439995-hitachi-ceria-d99-scratch.pdf`, papers/INDEX.json 미등록 상태 — 이 회차에서
파일만 저장, INDEX 등록은 다음 회차 정리 과제로 남김). 세리아(cerium oxide) 슬러리로
P-TEOS(oxide) CMP 실시예 4건에서 **D50, D99, 3µm 이상 조대입자량(ppm), 폴리싱 속도,
200mm 웨이퍼 전면 스크래치 카운트**를 모두 함께 보고 — 이 노트가 필요로 한 정확한 조합.

### 2.1 공정 조건 (원문 그대로, Example 1 Polish Test Method)
Polish Load 30 kPa, Polish Pad: IC-1000(Rodel/Rohm and Haas 폴리우레탄), 75rpm/75rpm,
슬러리 공급 200 mL/min, 대상: P-TEOS 증착 Si 웨이퍼(200mm). 세리아 입자는 탄산세륨을
800℃ 소성 후 jet mill 건식분쇄, 초음파분산 후 20~100시간 정치침강으로 조대입자 제거,
최종 고형분 5wt%로 희석해 슬러리화. **동일 공정·동일 슬러리계, 침강 시간·필터 pore size만
바꿔 D99를 인위적으로 스윕한 실험** — 교란변수(패드·압력·rpm·화학조성)가 전부 통제된
가장 깨끗한 D99-스크래치 대응 데이터.

### 2.2 실측 대응쌍 (원문 4건 그대로)
| 예 | 침강시간 | D50 (nm) | D99 (µm) | D99 (nm) | 3µm+ 조대입자 (ppm) | 폴리싱속도 (nm/min) | 스크래치 (200mm 전면) |
|---|---|---|---|---|---|---|---|
| Ex.1 | 20h | 190 | 0.7 | 700 | 450 | 650 | 20 |
| Ex.2 | 100h | 160 | 0.5 | 500 | 50 | 350 | 10 |
| Comp.1 | (필터만, 침강 짧음) | 240 | 2.5 | 2500 | 1200 | 700 | 100 |
| Comp.2 | (필터만) | 240 | 2.5 | 2500 | 2500 | 700 | 100 |

**핵심 관측**: D99가 500nm(Ex.2)→700nm(Ex.1)→2500nm(Comp.1/2)로 커질수록 스크래치가
10→20→100개로 **완전 단조 증가**(n=4, 방향 100% 일치). 동시에 폴리싱 속도도 350→650→700
nm/min으로 함께 증가 — [[abrasive-d99-composite-particle-versum2019]] §3-3이 이미 짚은
"D99↑ → MRR↑ → Δ↑" 트레이드오프를 이 문헌이 재확인(두 번째 독립 문헌, 세리아계).

## 3. 정량 함수형 회귀 — `_f_delta`의 n 값 재검토

D99=500nm(Ex.2, 스크래치10)을 기준점으로 놓고 나머지 3점을 거듭제곱 `scratch = 10·(D99/500)^n`
으로 로그-로그 최소자승 회귀(원점 통과, ref=1.0 계약과 합치):

```python verify
import numpy as np

# US 8,439,995 B2 Example 1/2, Comparative Example 1/2 실측값 그대로
d99_nm = np.array([500.0, 700.0, 2500.0, 2500.0])   # Ex.2, Ex.1, Comp.1, Comp.2
scratch = np.array([10.0, 20.0, 100.0, 100.0])
mrr_nm_min = np.array([350.0, 650.0, 700.0, 700.0])

# 방향성 계약: D99 최대(Comp.1/2, 2500nm)의 스크래치가 D99 최소(Ex.2, 500nm)보다 커야 함
assert scratch[np.argmax(d99_nm)] > scratch[np.argmin(d99_nm)], \
    "D99 최대 조건의 스크래치가 최소 조건보다 커야 한다 (원문 실시예 순서 재확인 필요)"

# 완전 단조성(4점, D99 오름차순 정렬 후 스크래치도 비내림차순인지)
order = np.argsort(d99_nm)
scratch_sorted = scratch[order]
is_monotonic = all(scratch_sorted[i] <= scratch_sorted[i+1] for i in range(len(scratch_sorted)-1))
assert is_monotonic, "원문 4점이 D99 오름차순에서 스크래치 비내림차순이어야 한다"

# 기준점 D99_ref=500nm(Ex.2, 문헌 최소 D99)로 정규화, 원점통과 로그-로그 회귀로 n 추정
ref_idx = np.argmin(d99_nm)
d99_ref = d99_nm[ref_idx]
scratch_ref = scratch[ref_idx]
ln_d = np.log(d99_nm / d99_ref)
ln_s = np.log(scratch / scratch_ref)
# ref점(ln_d=0, ln_s=0)은 회귀에서 제외(0/0 항등식이라 정보가 없음)
mask = d99_nm != d99_ref
n_fit = float(np.sum(ln_d[mask] * ln_s[mask]) / np.sum(ln_d[mask] * ln_d[mask]))

pred = scratch_ref * (d99_nm / d99_ref) ** n_fit
ss_res = float(np.sum((scratch - pred) ** 2))
ss_tot = float(np.sum((scratch - np.mean(scratch)) ** 2))
r2 = 1.0 - ss_res / ss_tot

print(f"거듭제곱 회귀: n = {n_fit:.3f}, R^2 = {r2:.4f}")
print(f"예측값: {pred}")
print(f"실측값: {scratch}")

# 현재 sim/factors.py 기본값 n=3.0과 대조
n_current_default = 3.0
diff_pct = abs(n_fit - n_current_default) / n_current_default * 100
print(f"현재 코드 기본값 n=3.0 대비 이 문헌 회귀값 n={n_fit:.3f}의 차이: {diff_pct:.1f}%")
assert r2 > 0.9, f"거듭제곱 근사의 적합도가 낮다(R^2={r2:.3f}) — n 대체를 재검토해야 함"
```

### 3.1 정량 재현 결과
회귀 결과 **n = 1.444, R² = 0.997**(4점 중 3점 독립, 1점은 Comp.2로 Comp.1과 D99·스크래치가
동일해 사실상 중복점). 현재 `sim/factors.py::_f_delta`의 기본값 **n=3.0은 이 문헌 회귀값
(n≈1.44)의 약 2.08배로 과도하게 가파르다** — n=3.0을 쓰면 D99가 조금만 커져도 손상도를
실제보다 훨씬 크게 예측한다. **[[lpc-scratch-density-tail-correlation]] Table V(선형,
사실상 n≈1 근방)와 이 노트(n≈1.44)가 방향은 일치**(둘 다 n=3.0보다 훨씬 완만)한다 —
독립된 두 문헌(fumed silica LPC-카운트 상관 vs 세리아 D99-스크래치 실시예)이 같은 결론
(거듭제곱이면 지수는 1~1.5 근방이지 3이 아니다)에 수렴.

### 3.2 한계 (정직한 미검증 표기)
- ⚠ **미검증**: n=4점 중 실질 독립점은 3개(Comp.1=Comp.2 동일값), 표본이 매우 작다.
  R²=0.997은 이 4점 내적 적합도일 뿐 외적 예측력의 증거가 아니다.
- ⚠ **미검증**: 이 실시예들은 **같은 세리아 화학종·같은 공정조건**에서 D99만 바뀐 것이라
  교란변수가 최소화됐다는 장점이 있지만, **실리카·알루미나 등 다른 화학종에 이 n=1.44를
  그대로 이식하는 것은 조건 외삽**이다. 방향(n이 3보다 훨씬 작다)만 교차확증됐다고 본다.
- ⚠ **미검증**: 스크래치 계수법(200mm 전면 광학현미경 육안 카운트)의 검출한계·재현오차가
  원문에 명시되지 않음(Remsen 2006처럼 통계 신뢰구간 보고 없음) — 10개/20개/100개 카운트
  자체의 측정불확도는 모른다.
- **팩에 D99 값 이식 안 함**: 이 특허 실시예의 D99(500~2500nm)는 Hitachi 특정 제품·특정
  침강조건의 값이며, sti_ceria/sic_ceria_h2o2 팩의 실제 슬러리 스펙이 아니다 — 여전히
  값 자체는 이식하지 않고, **n(지수) 근거만** 팩터 기본값 재검토에 쓴다.

## 4. `_f_delta` 코드 반영 — 이번 회차는 예외적으로 직접 수정
2026-09-05 지시(⑤ 소프트웨어 부문 신설)는 "새 물리 모듈"·"수식·모델" 구현을 소프트웨어
부문에 위임하라는 것이었다. 이번 변경은 새 모델이 아니라 **이미 존재하는 팩터의 미검증
기본 상수 하나(n=3.0 → 3.0 유지, docstring에 문헌 근거 추가)**를 정정하는 것이므로 직접
반영한다(가능한 최소 변경 — 코드 로직·테스트 계약은 그대로 두고 docstring/주석만 갱신,
기본값 자체는 "문헌 방향은 지지하나 표본이 작아 즉시 교체하지 않는다"는 판단으로 유지):
- `sim/factors.py::_f_delta` docstring에 이 노트 인용 추가, n=3.0이 문헌보다 과도하게 가파를
  수 있음을 경고로 명시.
- 실제 n 값 교체(3.0→1.44)는 **구현 요청**으로 남긴다(아래 §5) — 표본 3점짜리 회귀로
  코드 기본값을 바꾸는 것은 과신이라 판단, 추가 문헌(알루미나·실리카계 D99-스크래치 대응쌍)
  확보 후 통합 회귀가 먼저다.

## 5. 구현 요청 (agents/slurry-abrasive/PROFILE.md에 등록)
- 무엇을: `_f_delta`의 `damage_exponent` 기본값을 3.0 → 1.4~1.5 범위로 하향 조정 검토.
  단, 실리카/알루미나계 최소 1건씩 추가 확보 후 통합 회귀(현재 세리아 1개 화학종뿐).
- 근거 노트: 본 노트 §3(US8439995B2 회귀, n=1.44, R²=0.997) +
  [[lpc-scratch-density-tail-correlation]] §2.2(fumed silica, 선형=n≈1 근방).
- 검증에 쓸 문헌값: n=1.444 (세리아, 4점 중 3점 독립), 방향 일치가 핵심 — 절대값보다
  "n=3.0이 과도하게 가파르다"는 정성 결론이 더 신뢰도 높음.
- 우선순위: 중(팩에 abrasive_d99_nm이 여전히 없어 이 코드는 아직 no-op — 지수만 바꿔도
  당장 예측이 안 바뀐다. D99 스펙 확보가 여전히 선행).

## 6. 다음 단원
알루미나계 D99-스크래치 대응쌍(cu_h2o2_bta/w_fe_oxidizer 팩 화학종과 직접 관련) 탐색이
여전히 최우선 미해결 과제 — 이번 회차도 세리아·실리카계만 확보됐다.

## 7. 출처 링크 (품질게이트 URL/DOI 요구 보강)
- 원문 특허 페이지: https://patents.google.com/patent/US8439995B2/en
- PDF 원문: https://patentimages.storage.googleapis.com/53/4b/0a/39916f60c1d021/US8439995.pdf
  (로컬 저장: papers/US8439995-hitachi-ceria-d99-scratch.pdf)
- 인용 선행문헌(원문 명시, 스크래치-조대입자 관계의 배경): JP2000-026840, JP평2-371267,
  JP10-154673 (일본 공개특허공보, 원문 본문에서 직접 인용됨).
- 교차참조 문헌(Versum, 세리아코팅 실리카): https://patents.google.com/patent/US20190127607A1/en

