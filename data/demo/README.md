# ⛔ SYNTHETIC — 실측 아님

이 폴더의 CSV 3개는 모두 `tools/make_demo_csv.py`가 생성한 **합성** 데이터다.
실제 fab 측정값이 아니다. 각 CSV의 `data_source` 열도 모든 행에 `"SYNTHETIC"`을
담고 있다(이중 표기 — 파일 자체를 봐도, 이 README를 봐도 실측이 아님을 알 수 있게).

CSV 첫 줄에 `#` 주석을 넣지 않은 이유: `sim/demo_app.py` 탭3의 업로더가
`pd.read_csv(csv_file)`을 `comment=` 옵션 없이 그대로 호출한다. 주석 줄을 넣으면
그 줄이 헤더로 읽혀 탭3 데모가 깨진다. 그래서 SYNTHETIC 표기는 (a) 이 README와
(b) `data_source` 열, 둘로 남긴다.

재생성:

```
./.venv/bin/python tools/make_demo_csv.py [--seed 20260919]
```

같은 시드 → 비트 동일 CSV(결정적, `numpy.random.default_rng(seed)` 고정 시드).

## 생성 방식 (재현 가능하도록 그대로 적음)

물리 기준선은 지어낸 값이 아니라 **`sim.engine.simulate()`가 그 팩에 대해 실제로
내는 `WaferResult.removed_nm`**에서 그대로 가져온다(`tools/make_synthetic_wafer.py`와
동일한 서브샘플 방식 — 반경 격자에서 9점을 뽑고, 각도 4개(0/90/180/270°)에
동일하게 복제해 36행을 만든다).

```
recipe = Recipe(pack="oxide_silica", wafer=<"NPW"|"PTW">, time_s=60.0)
res = simulate(recipe)
r_mm, removed_nm = res.radius_m[idx]*1000, res.removed_nm[idx]   # idx = 9점 서브샘플
```

그 위에 **의도적으로 주입한** 결정론적 편차와 가우시안 노이즈만 더한다:

```
deviation(r_mm) = DEV_AMP_NM * sin(r_mm / DEV_L_MM) + offset
                = 8.0 * sin(r_mm / 40.0) + offset          # nm
noise ~ N(0, NOISE_SIGMA_NM)  =  N(0, 0.5)                  # nm, 측정 반복성 모사

measured_nm = removed_nm(r_mm)  +  deviation(r_mm)  +  noise
```

파일별 계수(`tools/make_demo_csv.py`의 상수 그대로):

| 파일 | wafer | seed | offset (nm) | 의미 |
|---|---|---|---|---|
| `npw_oxide_silica.csv` | NPW | 20260919 (기본 `--seed`) | 0.0 | 정상 로트 — NPW GP 보정 학습용 |
| `ptw_oxide_silica.csv` | PTW | 20260920 (`--seed`+1) | 0.0 | 같은 팩 PTW 측정 |
| `npw_oxide_silica_drifted.csv` | NPW | 20260921 (`--seed`+2) | **+30.0** | 드리프트 시연용 — 학습 때 없던 상수 오프셋 주입 |

`DEV_AMP_NM=8.0`, `DEV_L_MM=40.0`, `NOISE_SIGMA_NM=0.5`, `DRIFT_OFFSET_NM=30.0`은
전부 임의로 고른 숫자다(문헌값 아님) — 목적은 "GP가 학습 가능한 정도의 반경방향
구조"와 "기존 GP가 못 잡아낼 정도로 큰 새 편차"를 만드는 것뿐이다.

## 실제 확인 결과 (2026-09-19, `--seed 20260919` 기본값)

`npw_oxide_silica.csv`로 `run_calibration("oxide_silica", npw_record)`:

```
verdict: calibrated
fit_npw: improved=True, loo_rmse_gp=0.561, loo_rmse_baseline=5.029
```

그 run에 `evaluate_new_lot(run, drifted_record)` (drifted CSV):

```
verdict: alarm
n_points=36, rmse_new=30.36, rmse_reference=0.561, ratio=54.1
frac_outside_90ci=1.000 (기대 0.10) — 이항검정 p≈1e-36 < 0.05
```

같은 run에 정상 `npw_oxide_silica.csv`를 다시 새 로트로 넣으면(대조):

```
verdict: ok
frac_outside_90ci=0.111 (≈ 기대 0.10), rmse_new=0.500
```

→ +30nm 상수 오프셋은 이 GP 보정 하에서 1회 시도로 즉시 잡혔다(`DRIFT_OFFSET_NM`을
키우지 않았다).

## CSV 열 (탭3 `_csv_to_record`가 기대하는 polar 좌표계 매핑)

| 열 | 단위 | 의미 | `_csv_to_record` 매핑 |
|---|---|---|---|
| `r_mm` | mm | 웨이퍼 중심에서의 반경 | 반경 열(`r_col`, `r_unit="mm"`) |
| `theta_deg` | deg | 각도 | 각도 열(`theta_col`, `theta_unit="deg"`) |
| `thickness_nm` | nm | 60초 연마 후 제거두께 | 측정값 열(`value_col`, `value_unit="nm"`) |
| `data_source` | — | 항상 `"SYNTHETIC"` — 실측 아님 표기 | 사용하지 않음(무시되는 여분 열) |

`wafer_id`/`wafer_diameter_mm`(300)/`notch_direction`(`"Bottom"`)/`edge_exclusion_mm`(0.0)은
CSV 열이 아니라 탭3 업로더에서 사용자가 직접 입력하는 메타데이터다(측정기 출력이
아니라는 원칙 — `sim/demo_app.py` 참고).
