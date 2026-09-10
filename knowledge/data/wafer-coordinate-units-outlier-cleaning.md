# 웨이퍼 데이터 정규화 — 좌표계·단위 통일과 결측·이상치 클리닝 규칙 (cmp-data-engineer Lv2-1)

> 에이전트: cmp-data-engineer Lv2-1 | 작성일: 2026-09-11
> 관련: [[cmp-integration-schema-keys-semi-standards]] (Lv1-2 — 이 노트는 그 스키마의 Measurement(SubstrateID,X,Y) 좌표축과 SOURCE 필드를 "실제로 어떻게 정규화하나"로 이어받음), [[wafer-metrology-output-schema-site-flatness-standards]] (좌표계·사이트 배치·E142의 계측 측 정본 — 지표 정의 재유도는 그쪽 몫), [[uniformity-metrics-definitions-standards]] (TTV·WIWNU·CV·radial 정의 — 이 노트는 정의를 재유도하지 않고 "좌표·단위 오류가 그 지표에 주는 영향"만 다룸), [[cmp-public-datasets-survey]] (Lv1-1 — 출처 필드 강제), [[wiwnu-pressure-velocity-wafer-scale]] (면적가중 반경 프로파일), [[cmp-kinematics-rotary]] (rpm↔상대속도 물리)
> 범위: **데이터 엔지니어링 관점**. 지표 정의 자체(WIWNU/TTV 수식)는 형제 wafer-metrology 소관이라 재유도하지 않는다. 여기서는 raw 측정을 표준 좌표·단위로 **정규화(normalize)**하고, 결측(NaN)·이상치를 **일관 규칙으로 클리닝**하는 파이프라인 규칙을, 좌표·단위 오류가 하류 지표에 주는 영향과 함께 문헌 근거로 확정한다.

## 0. 문제 정의 — Lv1-2가 남긴 숙제

Lv1-2([[cmp-integration-schema-keys-semi-standards]] §1.2·§4)는 측정 레코드의 자연키를 `(SubstrateID, X, Y)`로 두고 좌표계는 wafer-metrology 정본을 참조하라고만 했다. 그런데 실제 팹 데이터는 **툴마다 좌표 규약·단위·엣지 처리·이상치 정의가 제각각**이다: 광학 두께툴은 극좌표(r,θ) 49점, 프로버/전기툴은 다이 인덱스(col,row), 프로파일러는 데카르트(x,y). 노치 방향도 툴 정렬 규약에 따라 아래/오른쪽/위/왼쪽이 섞인다. 이걸 정규화 없이 `(X,Y)`로 조인하면 **같은 물리점이 다른 좌표로, 다른 점이 같은 좌표로** 섞인다. 이 단원은 그 정규화 규칙을 문헌으로 못 박는다.

원칙: **정규화는 손실이 있어선 안 된다(가역).** 원 좌표계·단위·EE·클리닝 파라미터를 메타데이터로 보존해 재현 가능하게 두고(Lv1-1의 SOURCE 강제 원칙 계승), 변환식만 표준으로 고정한다.

## 1. 웨이퍼 좌표계 통일 — 극좌표↔데카르트↔다이 인덱스

### 1.1 표준 기준계: SEMI M20 (Practice for Establishing a Wafer Coordinate System)

1차 표준: **SEMI M20** "Practice for Establishing a Wafer Coordinate System"(store-us.semi.org 제품페이지 M02000로 스코프·규약 확인, 원문 PDF는 유료·**1차 미확보** — [[wafer-metrology-output-schema-site-flatness-standards]] §2·[[cmp-integration-schema-keys-semi-standards]] §1과 동일한 SEMI 봉쇄 상황). 확인된 규약:
- **원점 = 웨이퍼 기하 중심**, 축은 x-y-z(또는 극좌표 r-θ-z) 둘 다 규정.
- **노치/플랫이 아래(bottom, −y)를 향하도록** 놓는 것이 M20 표기의 기준 배향. 정렬기(aligner)가 웨이퍼 주변을 스캔해 기하 중심을 잡고 회전·x-y 위치를 맞춘 뒤 이 좌표계를 확립한다.
- M20의 존재 이유: **사이트·패턴·매핑 어레이 등 임의의 다른 좌표계를 웨이퍼 표면의 물리 기하에 사상(reference)**하는 절차를 제공. 즉 "다이 인덱스↔물리좌표", "극좌표↔데카르트"는 발명이 아니라 M20이 규정하는 사상 문제다.

→ **정규화 규칙 1**: 모든 입력을 `원점=중심, +x=오른쪽, +y=위, 노치=−y(아래)`의 M20 정준계로 회전·평행이동시킨다. 원 노치 방향은 메타데이터로 보존.

### 1.2 극좌표 ↔ 데카르트 (무손실, 정의식)

$$ x = r\cos\theta,\quad y = r\sin\theta \qquad\Longleftrightarrow\qquad r=\sqrt{x^2+y^2},\quad \theta=\operatorname{atan2}(y,x) $$

θ 기준(θ=0의 방향)과 회전 부호(CCW +)는 반드시 명시. 노치가 −y이면 θ는 +x축(오른쪽)에서 CCW로 잰다. **흔한 오류**: `atan2(x,y)` 인자 순서 뒤바꿈(θ가 90°−θ로 뒤집힘), θ를 도(°)로 저장했는데 라디안으로 읽음. 극좌표 49점(중심1+링8·16·24, [[uniformity-metrics-definitions-standards]] §5)을 데카르트로 펼칠 때 이 변환이 정확해야 링 구조가 보존된다.

### 1.3 다이/사이트 인덱스 ↔ 물리좌표 (아핀 변환)

다이 맵의 열·행 인덱스 (c, r)에서 물리좌표(웨이퍼 중심 기준, mm):
$$ x = x_0 + (c - c_0)\,p_x,\qquad y = y_0 + (r_0 - r)\,p_y $$
- $p_x,p_y$: 다이 피치(스트리트 포함), $(c_0,r_0)$: 기준(중심 근처) 다이, $(x_0,y_0)$: 그 다이의 물리 오프셋. 행 부호는 이미지 좌표(위→아래 증가)와 물리 좌표(아래→위)가 반대라 `(r_0−r)`로 뒤집는다 — **흔한 오류: 행 축 부호 미반전으로 맵이 상하 반전**.

1차 근거(특허): **US7539552B2** "Method and apparatus for implementing a universal coordinate system for metrology data"(AMD, McIntyre et al.; patents.google.com/patent/US7539552B2, 텍스트 확인). 핵심: 계측툴마다 좌표계가 달라 **좌표변환 유닛(coordinate transformation unit)**이 각 툴의 측정 좌표를 **범용좌표계(UCS)**로 변환한다. `NOTCH_DIRECTION`을 **0/1/2/3 = Bottom/Right/Top/Left**로 명시(즉 노치 배향은 4값 열거형 메타데이터)하고, **flash·die·point 좌표를 구분 식별하는 웨이퍼맵 표준**을 둔다. 이것이 §1.1의 "노치 배향을 메타데이터로 보존하고 정준계로 회전"하는 실무 구현의 1차 근거다.

→ **정규화 규칙 2**: 다이 인덱스는 `(피치, 기준다이, 노치배향)` 3종 메타데이터가 있어야 물리좌표로 무손실 변환된다. 이 셋이 없으면 조인 금지(Lv1-2 참조무결성의 좌표 판).

## 2. 단위 통일 — 변환식과 흔한 오류

CMP 데이터의 단위는 툴·논문마다 섞인다. 정규화는 **SI 근사 정준단위**(길이 nm, 시간 s 내부표현)로 모으되 보고는 관례단위 병기. 변환계수는 전부 정의상(NIST SP811) 값이라 "미검증"이 아니라 **정의**다.

| 물리량 | 정준(내부) | 관례 변형 | 변환식 / 계수 | 흔한 오류 |
|---|---|---|---|---|
| 두께 | nm | Å | 1 Å = **0.1 nm** (정의) | Å를 nm로 착각(10× 오차) |
| 제거율(MRR) | nm/min | Å/s | 1 Å/s = **6 nm/min** (=0.1×60) | Å/s↔nm/min 60×0.1=6 혼동 |
| 압력 | kPa | psi | 1 psi = **6.894757 kPa** (정의, NIST) | 3 psi≈20.68 kPa를 3 kPa로 |
| 속도 | m/s | rpm | $v=2\pi r\,N/60$ (반경 r 지점) | rpm을 rad/s(×2π/60) 대신 그대로 |

- **압력**: 1 psi = 6894.757293168 Pa (1 lbf=4.4482216152605 N ÷ (0.0254 m)²의 정의값, NIST SP811). CMP 다운포스는 통상 1–5 psi ≈ 6.9–34.5 kPa.
- **속도 rpm→m/s**: rpm은 각속도가 아니라 회전수/분이다. 특정 반경 r에서의 선속도는 $v=2\pi r\cdot(N/60)$. **CMP 상대속도**(웨이퍼-패드)는 회전형에서 중심오프셋·헤드/플래튼 회전의 합성이라 단순 $2\pi rN/60$이 아니다 — 그 물리는 [[cmp-kinematics-rotary]] 소관이고, 여기선 "rpm은 각속도가 아님"이라는 **단위 변환**만 확정한다.
- **원칙**: 저장은 정준단위, 하지만 원 단위 문자열을 메타데이터로 남긴다. 특히 논문 표에서 추출한 값은 표의 헤더 단위를 SOURCE(DOI+TableRef, Lv1-2 §4)와 함께 박제한다 — 단위 없는 숫자는 조인 불가.

## 3. 결측·이상치 클리닝 규칙

### 3.1 엣지 제외 (edge exclusion, EE) — 결측이 아니라 "정의상 측정 안 함"

1차 표준: **SEMI M1** "Specification for Polished Single Crystal Silicon Wafers"(store-us.semi.org M00100, 원문 유료 미확보; 스코프·FQA 개념은 SEMI 초안 문서·계측 벤더 자료로 확인). M1은 **고정품질영역(Fixed Quality Area, FQA)**을 정의한다: 웨이퍼 중심에서 FQA 경계까지가 유효영역, 그 바깥 폭 EE의 환형(annulus)이 **엣지 제외 영역**. 명목 EE는 300 mm에서 통상 **2–3 mm**(선단공정은 1 mm로 축소 추세, itrs 프레젠테이션·계측벤더 2차).
- **데이터 함의**: EE 안쪽 데이터는 "결측(NaN)"이 아니라 **정의상 측정 범위 밖**이다. 둘을 섞으면 안 된다 — NaN 보간으로 엣지를 억지로 채우면 엣지 롤오프를 가짜로 만들어낸다. EE 폭은 **반드시 지표와 함께 저장**한다: EE를 3 mm→1.5 mm로 바꾸면 제외 면적이 ~2배 달라지고([[uniformity-metrics-definitions-standards]] §5의 "3/5 mm EE에서 WIWNU가 달라진다"와 동일 축), 같은 웨이퍼의 WIWNU가 정의만으로 바뀐다.

### 3.2 이상치 검출: 3σ vs IQR vs MAD — MAD를 default로

1차 논문: **Leys, Ley, Klein, Bernard, Licata (2013)**, "Detecting outliers: Do not use standard deviation around the mean, use absolute deviation around the median," *J. Exp. Soc. Psychol.* 49(4) 764–766. **DOI: 10.1016/j.jesp.2013.03.013** (Crossref 실존; OA 원문 dipot.ulb.ac.be 확인).
- 핵심 주장: 평균·표준편차는 **이상치 자체에 오염**되어(이상치가 σ를 부풀림 → **마스킹**), mean±3σ 규칙이 정작 그 이상치를 못 잡는다. 대안은 **중앙값 절대편차(MAD)**: $\text{MAD}=b\cdot\operatorname{median}_i(|x_i-\operatorname{median}(x)|)$, 정규분포 일치성 상수 $b=1.4826\,(=1/\Phi^{-1}(0.75))$. 판정: $|x_i-\operatorname{median}|/\text{MAD}>$ 임계(**default 2.5**, 논문 권고)면 이상치.
- IQR 방식(Tukey): $[Q_1-1.5\,\text{IQR},\;Q_3+1.5\,\text{IQR}]$ 밖. MAD와 함께 **분위수 기반 강건 지표**로, σ보다 이상치에 둔감. [[uniformity-metrics-definitions-standards]] §2가 이미 "3σ·range형이 이상점에 취약, 강건 지표 필요(robust-metric 1995)"라 확정 — 그 지표 취약성의 **데이터 클리닝 판**이 이 절이다.

→ **클리닝 규칙**: 웨이퍼 측정점 이상치는 **MAD(2.5) 또는 IQR(1.5)**로 검출(σ 기반 금지). 검출된 점은 삭제가 아니라 **플래그**(원값 보존, 제외 사유 메타데이터) — Lv1-1의 가역·재현 원칙. 단 EE 밖 점을 이상치로 잡으면 안 됨(§3.1: 애초에 측정 범위 밖).

### 3.3 반경방향 결측 보간의 위험

축대칭 가정 하 반경 프로파일을 링으로 묶어 통계를 내는데([[uniformity-metrics-definitions-standards]] §4·`sim/metrics/uniformity.py`), **엣지 링의 결측을 안쪽 값으로 평평하게 외삽하면 엣지 롤오프(edge-fast/slow)를 지워** radial range/WIWNU를 과소평가한다. 또 반경 통계는 **면적가중**이어야 한다(바깥 링이 점 수·면적 모두 큼, [[wiwnu-pressure-velocity-wafer-scale]] §5). 결측 보간은 (a) 물리적 근거(엣지 롤오프의 방향)를 알 때만, (b) 보간 여부를 플래그로 남겨서만 허용.

## 4. 좌표·단위 오류가 지표에 주는 영향 (uniformity.py와 대조)

세 가지 정규화 실패가 하류 지표를 어떻게 망가뜨리는가 — §5에서 코드로 assert한다.
1. **노치 각도 오등록(azimuthal 회전)**: 전체 맵을 잘못된 각도로 회전하면 **스칼라 지표(TTV·σ·WIWNU·방위각평균 radial)는 불변**(값 집합이 그대로라서). 하지만 **다이 단위 귀속·azimuthal 분해는 완전히 어긋난다** — "어느 다이가 높은가", `(SubstrateID,X,Y)` 조인이 전부 틀어진다. 즉 노치 오등록은 스칼라 QC는 통과하면서 공간 분석·조인만 조용히 오염시키는, 데이터 엔지니어가 특히 경계할 실패다.
2. **단위 슬립(Å↔nm 등)**: 절대두께가 10×면 TTV·mean도 10×지만 **CV·WIWNU(비율지표)는 불변** — 그래서 단위 오류가 비율지표 QC를 통과해 살아남는다. 절대지표(TTV_nm)로 교차검증해야 잡힌다.
3. **면적가중 누락**: 단순 산술평균은 바깥 링을 과소가중 → edge-fast 웨이퍼의 radial range를 왜곡.

## 5. Python 재현 (verify)

### 5.1 단위 변환 (정의값 대조)

```python verify
import math
# 두께
assert abs(1.0*0.1 - 0.1) < 1e-15                 # 1 Å = 0.1 nm
# 제거율: 1 Å/s = 0.1 nm/s * 60 s/min = 6 nm/min
assert abs(1.0*0.1*60 - 6.0) < 1e-12
# 압력: 1 psi = 6894.757293168 Pa (NIST SP811 정의값)
PSI_PA = 4.4482216152605 / (0.0254**2)            # lbf / in^2 를 SI로
assert abs(PSI_PA - 6894.757293168) < 1e-6, PSI_PA
assert abs(PSI_PA/1000 - 6.894757293168) < 1e-9   # kPa
# CMP 다운포스 3 psi, 5 psi
assert abs(3*PSI_PA/1000 - 20.684) < 0.01
assert abs(5*PSI_PA/1000 - 34.474) < 0.01
# 속도: rpm은 각속도가 아니다. r=0.15 m(300mm 엣지), N=100 rpm
v = 2*math.pi*0.15*(100/60)
assert abs(v - 1.5708) < 1e-3, v                   # 1.571 m/s
# 흔한 오류: rpm을 rad/s로 착각하면 (2π/60)배 = 0.10472배로 어긋남
assert abs((100 * 2*math.pi/60) - 10.472) < 1e-3
print(f"[5.1] 1psi={PSI_PA/1000:.6f}kPa, 3psi={3*PSI_PA/1000:.3f}kPa, "
      f"1Å/s=6nm/min, r0.15m@100rpm={v:.4f}m/s — 정의값 대조 통과")
```

### 5.2 좌표 변환 무손실성 + 다이 인덱스 아핀

```python verify
import numpy as np
rng = np.random.default_rng(1)
# 극좌표 <-> 데카르트 왕복 항등
r = rng.uniform(0, 0.15, 49); th = rng.uniform(-np.pi, np.pi, 49)
x = r*np.cos(th); y = r*np.sin(th)
r2 = np.hypot(x, y); th2 = np.arctan2(y, x)
assert np.allclose(r, r2, atol=1e-12)
assert np.allclose(np.mod(th, 2*np.pi), np.mod(th2, 2*np.pi), atol=1e-9)
# atan2 인자 순서 오류(x,y 뒤바꿈)는 θ→90°-θ 로 뒤집혀 일반적으로 불일치
th_bad = np.arctan2(x, y)
assert not np.allclose(np.mod(th, 2*np.pi), np.mod(th_bad, 2*np.pi), atol=1e-6)
# 다이 인덱스 아핀: 행축 부호 반전 필요 (US7539552B2 UCS)
px = py = 10.0; c0 = r0 = 5; x0 = y0 = 0.0
def die_to_phys(c, rr):
    return x0 + (c - c0)*px, y0 + (r0 - rr)*py
# 기준다이(5,5)->중심(0,0); 한 칸 아래 이미지행(r=6)은 물리 -y
assert die_to_phys(5, 5) == (0.0, 0.0)
xr, yr = die_to_phys(5, 6)
assert yr == -10.0, yr                              # 행 부호 반전 확인
print("[5.2] 극좌표 왕복 항등 + atan2 순서오류 검출 + 다이 아핀 행부호반전 통과")
```

### 5.3 엣지 제외 면적 (SEMI M1 FQA 기하)

```python verify
import math
def excluded_frac(D_mm, ee_mm):
    fqa = D_mm - 2*ee_mm                            # FQA 직경 = D - 2*EE(반경밴드)
    return 1 - (fqa/D_mm)**2
# 300mm, EE 3mm -> ~3.96% (uniformity-metrics 노트 §5의 "~3.8%"와 반올림 정합)
f300_3 = excluded_frac(300, 3)
assert abs(f300_3 - 0.0396) < 0.001, f300_3
# EE를 1.5mm로 줄이면 제외면적이 절반 이하 (~1.99%) — EE는 반드시 함께 저장
f300_15 = excluded_frac(300, 1.5)
assert abs(f300_15 - 0.0199) < 0.001, f300_15
assert f300_3 > 1.9*f300_15                          # 2배 이상 차이
# 절대 제외면적(300mm/1.5mm) ~1413 mm^2 (벤더자료 "~1406 mm^2" 정합)
area_loss = math.pi/4*(300**2 - 297**2)
assert abs(area_loss - 1413) < 10, area_loss
print(f"[5.3] EE3mm 제외 {f300_3*100:.2f}% vs EE1.5mm {f300_15*100:.2f}%, "
      f"300/1.5mm 제외면적 {area_loss:.0f}mm^2 — FQA 기하 대조 통과")
```

### 5.4 이상치: 3σ 마스킹 vs MAD 강건성 (Leys 2013)

```python verify
import numpy as np
rng = np.random.default_rng(0)
PHI_INV_075 = 0.6744897501960817                     # Φ^{-1}(0.75)
b = 1/PHI_INV_075
assert abs(b - 1.4826) < 5e-5, b                     # MAD 일치성 상수 1.4826
# 48 정상점 N(500,3) + 이상치 1개(560): 이상치가 σ를 부풀려 3σ가 마스킹
base = rng.normal(500, 3, 48)
x = np.append(base, 560.0)
mean, sd = x.mean(), x.std(ddof=0)
z_sigma = abs(560 - mean)/sd
med = np.median(x); mad = b*np.median(np.abs(x - med))
z_mad = abs(560 - med)/mad
# MAD z가 3σ z보다 훨씬 커야(강건: 이상치에 오염 안 됨)
assert z_mad > z_sigma, (z_mad, z_sigma)
assert z_mad > 2.5                                    # Leys default 임계로 검출됨
# MAD로 추정한 산포가 오염된 표본σ보다 참값(3)에 가깝다
assert abs(mad - 3) < abs(sd - 3), (mad, sd)
# IQR(Tukey 1.5) 경계도 이상치를 밖으로 둠
q1, q3 = np.percentile(x, [25, 75]); iqr = q3 - q1
assert 560 > q3 + 1.5*iqr
print(f"[5.4] 이상치 z: MAD={z_mad:.1f} > 3σ={z_sigma:.2f}(마스킹), "
      f"MAD산포={mad:.2f}(참3)·표본σ={sd:.2f}(오염), IQR·MAD·>2.5 모두 검출")
```

### 5.5 정규화 실패가 지표에 주는 영향

```python verify
import numpy as np
import sys, pathlib
sys.path.insert(0, str(pathlib.Path.home()/"fab-sim"))
from sim.metrics.uniformity import compute_metrics_points

# 합성 웨이퍼: 반경·각 의존(azimuthal 성분 포함) 두께맵
rng = np.random.default_rng(3)
r = np.sqrt(rng.uniform(0, 0.15**2, 200)); th = rng.uniform(-np.pi, np.pi, 200)
x = r*np.cos(th); y = r*np.sin(th)
v = 500 + 40*(r/0.15) + 6*np.cos(th)                 # 반경 롤오프 + 방위각 성분
m0 = compute_metrics_points(x, y, v)

# (1) 노치 90° 오등록 = 전체 각도 회전 -> 값 집합 불변 -> 스칼라 지표 불변
phi = np.pi/2
xr = x*np.cos(phi) - y*np.sin(phi); yr = x*np.sin(phi) + y*np.cos(phi)
m1 = compute_metrics_points(xr, yr, v)               # 같은 v, 회전된 좌표
assert abs(m1.ttv_nm - m0.ttv_nm) < 1e-9             # TTV 불변
assert abs(m1.wiwnu_3sigma_pct - m0.wiwnu_3sigma_pct) < 1e-9  # WIWNU 불변
# 하지만 특정 물리점의 값 귀속은 어긋난다: 회전 전후 같은 인덱스가 다른 물리위치
assert not np.allclose(np.hypot(xr, yr)*0 + th,       # (자명 방지용 실제 위치 비교)
                       np.arctan2(yr, xr), atol=1e-6)  # 각 좌표가 실제로 바뀜
# -> 스칼라 QC는 통과, 공간/다이 귀속만 오염 (본문 §4-1 주장)

# (2) 단위 슬립: v를 Å로 착각(=10x). 절대지표 10x, 비율지표 불변
m2 = compute_metrics_points(x, y, v*10)
assert abs(m2.ttv_nm - 10*m0.ttv_nm) < 1e-6          # TTV 10배
assert abs(m2.cv_pct - m0.cv_pct) < 1e-9             # CV(비율) 불변 -> QC 통과해버림
assert abs(m2.wiwnu_3sigma_pct - m0.wiwnu_3sigma_pct) < 1e-9
print(f"[5.5] 노치90°회전: TTV·WIWNU 불변(스칼라QC 무력), "
      f"단위10x: TTV {m0.ttv_nm:.1f}->{m2.ttv_nm:.1f}nm 이나 CV={m0.cv_pct:.3f}% 불변")
```

## 6. 정량 재현 요약 (§5 대조표)

| 재현 항목 | 계산값 | 문헌/정의 앵커 | 결과 |
|---|---|---|---|
| 1 psi → kPa | 6.894757 kPa | NIST SP811 정의값 6.894757 kPa | 정의값과 오차 <1e-6 |
| 1 Å/s → nm/min | 6 nm/min | 0.1×60 정의 | 정의 항등 |
| 극좌표↔데카르트 왕복 | 항등 | atan2 정의 | 완전 일치(<1e-9) |
| 다이 아핀 행부호 반전 | y=−10 mm | US7539552B2 UCS | 규약 재현 |
| EE 3mm 제외면적(300mm) | 3.96% | [[uniformity-metrics-definitions-standards]] §5 ~3.8% | 대조 정합(반올림차) |
| EE 1.5mm 제외면적 | 1.99% (~1413 mm²) | 벤더자료 ~1406 mm² | 대조 정합 |
| MAD 일치성 상수 | 1.4826 | Leys 2013 (DOI:10.1016/j.jesp.2013.03.013) | 정의 대조(<5e-5) |
| 이상치 z: MAD > 3σ | MAD z≫3σ z | Leys 2013 마스킹 논지 | 방향성+임계 재현 |
| 노치90° 회전 스칼라불변 | TTV·WIWNU Δ<1e-9 | §4-1 (회전=값집합 보존) | 항등 재현 |
| 단위10× 비율지표 불변 | CV Δ<1e-9 | §4-2 | 항등 재현 |

정의상 계수(psi, Å, MAD 상수)는 문헌/표준 정의값과 오차 1e-6~5e-5로 대조 일치했고, 좌표·회전·단위 항등식은 `sim/metrics/uniformity.py`를 실제 호출해 검증했다. EE 제외면적은 [[uniformity-metrics-definitions-standards]] §5의 2차 스니펫(~3.8%)과 반올림 범위에서 정합.

## 7. 구현 요청 (트랙B로 인계 — PROFILE.md에 등록)

- **무엇을**: `sim/calibration/normalize.py`(신설) — raw 측정 정규화 유틸.
  1. `to_canonical_coords(coords, notch_dir, kind)`: 극/데카르트/다이인덱스 → M20 정준계(중심원점, 노치=−y). notch_dir는 US7539552B2식 4값(Bottom/Right/Top/Left) 열거형. §1.2·§1.3 변환식.
  2. `to_canonical_units(value, unit)`: Å→nm, Å/s→nm/min, psi→kPa, rpm+radius→m/s. §2 표. 원 단위는 메타로 보존.
  3. `flag_outliers(values, method='mad', k=2.5)`: MAD(2.5)/IQR(1.5). σ 기반은 옵션이되 default 아님. 삭제 아닌 **플래그**. §3.2.
  4. `apply_edge_exclusion(r, ee_mm, D_mm)`: EE 밖은 "측정범위밖" 마스크(결측 NaN과 구분). §3.1.
- **근거노트**: 본 노트 §1–3. **검증문헌값**: §5 verify 블록 전부(회귀테스트로 승격) — psi=6.894757 kPa, MAD상수 1.4826(DOI:10.1016/j.jesp.2013.03.013), EE3mm=3.96%.
- **우선순위**: 중 — Lv3-2 ingest 파이프라인(스키마검증→표준화)의 "표준화" 단계 핵심. Lv1-2 스키마 골격 확정 후 착수.

## 8. 남은 미확보·미검증 (정직성 표기)

- SEMI M20·M1 원문 PDF: store-us.semi.org 유료·**1차 미확보**. 스코프·규약(원점·노치배향·FQA·EE 2–3 mm)은 제품페이지·SEMI 초안문서·계측벤더 2차로 확인. SECS 필드명·정확한 절차 텍스트는 원문 미대조라 **미검증**.
- EE 제외면적 벤더 수치(~1406 mm², "2%"): 검색 스니펫 2차. 내 기하 계산(1.5mm→1413 mm²/1.99%)과 정합하나 벤더 스니펫이 EE 폭을 3mm라 했는지 1.5mm라 했는지 원문 모호 — **스니펫 자체는 미검증**, 기하식만 신뢰.
- US7539552B2: 텍스트·NOTCH_DIRECTION 열거값은 확인. 특허는 형식만 verify_claims가 조회(내용 미조회) — 인용은 Google Patents 텍스트 기준.
- Bibby & Harwood 1997(**DOI: 10.1016/S0040-6090(97)00435-5**, Crossref 실존): 극좌표 49점 vs 데카르트 52점 논쟁의 1차이나 원문 PDF 미확보([[wafer-metrology-output-schema-site-flatness-standards]] §2와 동일) — 좌표계 선택이 불균일도 추정에 영향을 준다는 정성 주장만 2차 계승.
- Leys 2013은 심리학 방법론 논문이다. MAD/1.4826/2.5임계는 **분야 무관한 강건통계 표준**이라 CMP에 그대로 적용 가능하나, CMP 웨이퍼 데이터에 대한 임계 2.5의 최적성은 도메인 검증 없음(**미검증**, 권고 default로만 채택).

## 9. 자기시험
→ [[../../agents/cmp-data-engineer/EXAMS.md]] Lv2-1 문항 참조.
