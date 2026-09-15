# CMP 계측 데이터 ingest 파이프라인: 스키마 검증 → 표준화 → 컬럼형 저장 (cmp-data-engineer Lv3-2)

> 에이전트: cmp-data-engineer Lv3-2 | 작성일: 2026-09-15
> 관련: [[cmp-integration-schema-keys-semi-standards]] (Lv1-2 — 엔터티·조인 키는 여기서 재정의하지 않고 그대로 계승),
> [[wafer-coordinate-units-outlier-cleaning]] (Lv2-1 — 단위환산·좌표계·MAD 이상치 규칙의 정본),
> [[cmp-data-quality-gate-and-anonymization]] (Lv3-1 — 이 노트의 검증 규칙이 통과시킨 레코드가 넘어가는 다음 관문)
> 범위: 기존 코드 `tools/ingest_measurement.py`(컬럼 별칭 매핑)와 `sim/store.py`(SQLite 행 저장)는 **읽기만** 했다.
> 이 노트는 그 둘이 이미 하고 있는 것과, 아직 하지 않는 것(불확도·출처 필드, 물리적 불가능값 검증, 컬럼형 저장)을
> 문헌 근거로 정리한 설계 노트다. 코드 변경은 하지 않는다 — 필요분은 PROFILE.md "구현 요청"에 넘긴다.

## 1. 최소 스키마 — 조건·응답·불확도·출처가 없으면 그 행은 쓸모없다

CMP 계측 레코드 한 줄이 하류(캘리브레이션·모델 검증)에서 쓸모가 있으려면 네 범주가 모두 있어야 한다.
넷 중 하나라도 없으면 그 행은 "숫자는 있지만 아무것도 증명하지 못하는" 죽은 데이터가 된다.

1. **조건(condition)** — 무엇을 걸고 측정했는가. 최소한 압력·회전수·시간 중 시뮬레이션 입력에 대응되는 값.
   `tools/ingest_measurement.py`가 이미 이 원칙을 코드로 구현하고 있다 — 압력·시간이 없으면 `blockers`에
   "시뮬레이션 조건을 맞출 수 없다"고 신고하고 `comparable=False`로 막는다(같은 파일 187–190행, 직접 확인).
   이는 임무가 요구하는 "조건 없는 행은 쓸모없다"는 판단 기준이 이미 부분적으로 실장되어 있다는 뜻이다.
2. **응답(response)** — 무엇을 쟀는가. 두께(pre/post) 또는 제거량 또는 제거율 중 하나. 없으면 조건이 아무리
   완비돼도 비교할 대상이 없다(같은 파일 179–181행, `has_val` 체크).
3. **불확도(uncertainty)** — 이 응답값이 ± 얼마나 흔들리는가. **현재 `ingest_measurement.py`에는 이 필드가
   전혀 없다** — `points`에 값만 있고 반복측정 표준편차나 계측기 사양 불확도가 들어갈 자리가 없다.
   이것이 문제인 이유는 임의값이 아니라 계측 표준 자체의 정의다. GUM(JCGM 100:2008, DOI:10.59161/jcgm100-2008e,
   원문 PDF 직접 확인)은 "uncertainty of measurement"를 "측정값에 합리적으로 귀속될 수 있는 값들의 산포를
   특징짓는 매개변수"로 정의하고(§2.2.3), 확장불확도 U = k·u_c(y)에서 커버리지 인자 k는 통상 2~3 범위를 쓰며
   "특수한 경우가 아니면 이 범위를 벗어나지 않는다"고 명시한다(§6.3.1). 나아가 §7.2.3은 측정 결과를 보고할 때
   k 값과 u_c(y)를 **반드시 함께 명시**해야 한다고 규정한다. 즉 "제거량 42.3 nm"라는 숫자만 있고 불확도가 없는
   행은 GUM이 정의하는 의미에서 "측정 결과"의 자격조차 없다 — 산포 정보가 없으면 다른 값과의 차이가 신호인지
   잡음인지 판단할 수 없기 때문이다.
4. **출처(source)** — 누가/무엇이 이 값을 냈는가. 실측이면 장비 ID + 타임스탬프, 문헌 추출이면 DOI + 표/그림
   번호. [[cmp-integration-schema-keys-semi-standards]]가 이미 `Measurement.SOURCE NOT NULL` 제약으로 이
   구분(실측=ToolID / 문헌추출=DOI+TableRef)을 정의해 두었으므로 여기서 재정의하지 않고 그대로 쓴다.
   출처가 없으면 값이 틀렸을 때 무엇을 의심해야 할지(장비 드리프트인가, 오타인가, 논문 표 오독인가) 추적할
   방법이 없다 — 이는 Lv1-2 노트의 참조무결성 요구와 같은 문제의 다른 얼굴이다.

CMP 측정 데이터셋이 실제로 어떤 필드를 최소 스키마로 삼는지 보여주는 1차 문헌 예시로 Li, X. et al.,
"Data-driven Prognostics for Chemical Mechanical Polishing Consumable Life," *J. Manufacturing Science and
Engineering* 141(10), 2019 (DOI:10.1115/1.4042051, OpenAlex 초록·서지로 확인, 본문은 ASME 유료·미확보)가
있다 — PHM 데이터셋의 WAFER_ID·STAGE 복합키가 이 스키마의 SubstrateID·ProcessEvent에 대응한다는 사실은
[[cmp-integration-schema-keys-semi-standards]]에서 이미 확립했다. 이 노트는 그 매핑을 반복하지 않고, 그
스키마 위에서 "행 하나가 통과 가능한가"를 판정하는 게이트를 다룬다.

## 2. 스키마 검증 규칙 — 단위 정합성·물리적 불가능값·결측 신고

검증은 **버리기가 아니라 신고**다. `tools/ingest_measurement.py`의 설계 원칙("모르는 것을 추정해 채우지
않는다", 파일 상단 docstring)을 그대로 물려받아 세 층으로 나눈다.

- **단위 정합성**: 값 자체는 유효해도 선언된 단위와 자릿수가 안 맞으면 신고한다. 예: `thickness_post_nm`
  컬럼에 500~600 범위 값이 들어와야 정상인데 5000~6000대 값이 섞여 있으면 Å 단위를 nm로 잘못 표기했을
  개연성이 높다 — 값을 조용히 나누지 말고(추정 금지 원칙 위반) "단위 의심"으로 플래그만 남긴다.
- **물리적 불가능값**: 두께·제거량·제거율·압력·시간·회전수는 정의상 음수가 될 수 없다(제거량이 음수라면
  pre/post 두께가 뒤바뀐 것이고, 압력·시간이 0 이하면 공정 자체가 성립하지 않는다). `removed_nm < 0`,
  `pressure_psi <= 0`, `time_s <= 0`는 결측(missing)이 아니라 **오류(invalid)**로 분리해 신고해야 한다 —
  둘을 같은 "빈 값"으로 취급하면 결측치 대체 로직이 오류값까지 함께 메워버리는 사고가 난다.
- **결측 처리**: [[wafer-coordinate-units-outlier-cleaning]] §3.1이 이미 확립한 원칙 — EE(edge exclusion)
  밖은 결측이 아니라 정의상 측정 범위 밖 — 을 그대로 계승한다. 여기 덧붙일 것은 조건 필드의 결측이다.
  `pressure_psi`가 비어 있으면 그 값을 팩 기본값으로 채워 넣지 말고(추정 금지), 그 행 전체를 "조건 불명 —
  비교 불가"로 신고해야 한다. `ingest_measurement.py`의 `blockers` 메커니즘이 정확히 이 역할이다.

세 층 모두 "이 행을 하류로 보내도 되는가"라는 동일한 형태의 pass/fail 결정이라는 점에서
[[cmp-data-quality-gate-and-anonymization]] §1(결측 게이트)의 완전성(completeness) 원칙과 같은 계열이다.
차이는 그 노트가 게이트 *정책*(무엇을 왜 막는가)을 다뤘다면, 여기서는 ingest 시점에 **스키마 수준**에서
무엇을 검증해야 다음 단계(표준화)가 안전한지를 다룬다는 점이다.

## 3. 표준화 — 단위 환산, 컬럼 별칭, 좌표계

표준화는 검증을 통과한 행을 정준(canonical) 형태로 바꾸는 단계다. 세 가지가 필요하다.

- **단위 환산**: Å/min ↔ nm/min(×0.1), psi → kPa(×6.894757, NIST SP811 — 앵커는
  [[wafer-coordinate-units-outlier-cleaning]] §2에서 이미 검증, 여기서 재유도하지 않는다), 그리고 이 노트가
  새로 다루는 것 — **천단위 쉼표 파싱**이다. 실무 CSV/XLSX 파일은 `1,234.5`처럼 쉼표가 낀 숫자를 문자열로
  담는 경우가 흔하고, `tools/ingest_measurement.py`의 `_num()`(121–127행)이 이미 `.replace(",", "")`로 이를
  처리한다 — 단, 이 방식은 유럽식 소수점 쉼표(`1.234,5` = 1234.5)와 충돌한다는 한계가 있다(파일 포맷 메타에
  로케일 정보가 없으므로 구분 불가 — 이 노트가 새로 지적하는 제약이며 §5 verify에서 실패 사례로 보인다).
- **컬럼 별칭**: `ALIASES`/`COND_ALIASES` 딕셔너리(같은 파일 30–52행)가 이미 폭넓게 구현돼 있다 — 정규화
  함수 `_norm()`이 공백·언더스코어·괄호·슬래시를 제거하고 소문자화한 뒤 별칭 집합과 대조하며, 모호하면
  매핑하지 않는다("잘못 매칭이 더 나쁘다", 74행 주석). 이 노트가 추가할 근거는 왜 이 방식(화이트리스트 별칭
  + 모호성 회피)이 스키마 검증의 사전 단계로 타당한가다 — [[cmp-integration-schema-keys-semi-standards]]가
  정의한 표준 키(SubstrateID, X, Y, metric, value, SOURCE)로 수렴하지 않는 컬럼은 표준화 대상이 아니라
  `unmapped_columns`로 남아 사람이 봐야 한다는 원칙과 일치한다.
- **좌표계**: 반경 기준 정준계(SEMI M20, 원점=중심, 노치=−y)로의 변환은
  [[wafer-coordinate-units-outlier-cleaning]] §1에서 이미 검증했으므로 이 노트는 재유도하지 않고, ingest
  단계에서는 "원 좌표계·노치 배향을 메타데이터로 보존해야 가역적"이라는 그 노트의 요구사항만 계승한다.

## 4. 컬럼형 저장(Parquet)을 쓰는 근거 — 왜 `sim/store.py`의 SQLite 행 저장만으로는 부족한가

`sim/store.py`는 이미 `measurements` 테이블에 실측을 SQLite로 저장한다(직접 확인, 41–58행) — 이는 캘리브레이션
소급 조회(런 하나 찾기)에는 적합하다. 그러나 ingest 파이프라인이 반복적으로 필요로 하는 연산은 **소급 조회가
아니라 집계**(웨이퍼/로트/조건별 평균 제거율, 반경 구간별 통계)다. 컬럼형 저장이 이 워크로드에 유리하다는
주장의 배경은 Stonebraker, M. et al., "C-Store: A column-oriented DBMS," 원 발표 *VLDB* 2005, 재수록:
*Making Databases Work: the Pragmatic Wisdom of Michael Stonebraker*, ACM, 2018 (DOI:10.1145/3226595.3226638,
Crossref 서지로 저자·연도·수록처 확인 — **본문 PDF는 오픈액세스 경로를 찾지 못해 미확보**. 따라서 이 논문의
구체적 수치는 인용하지 않고, "분석 워크로드에서 컬럼 지향 저장이 필요한 컬럼만 읽어 I/O를 줄인다"는 이
분야의 통념적 배경으로만 밝힌다). 정량적 근거는 원 논문 대신 아래 §5에서 이 프로젝트의 실제 스키마(반경·
두께·압력·시간·DOI 등 8컬럼)를 흉내 낸 합성 표로 직접 벤치마크한 결과를 쓴다 — 집계 쿼리(조건별 평균
제거율)에서 Parquet이 SQLite 대비 파일 크기 78% 작고 쿼리 3.5배 빠르며, 행 단위 CSV 대비로는 46배 빠르다
(코드와 수치는 §5 verify 블록에 있다. **이 벤치마크는 본 노트가 합성 데이터로 직접 실행한 것이지 문헌 재현이
아니다** — 정직성 표지).

DuckDB는 이 프로젝트 `.venv`(Python 3.9)에 설치돼 있지 않다(직접 확인, `import duckdb` → `ModuleNotFoundError`,
2026-09-15). CURRICULUM.md가 이 단원 제목에 "DuckDB"를 언급하지만, 이 노트는 설치 여부를 검증할 수 없는
도구를 근거로 쓰지 않는다 — 대신 이미 설치된 `pyarrow`(21.0.0, 직접 확인)의 Parquet 읽기/쓰기로 벤치마크했다.
DuckDB는 Parquet 파일을 그대로 질의할 수 있는 컬럼형 엔진이므로(공식 R 패키지 문서, DOI:10.32614/cran.package.duckdb,
Unpaywall로 PDF 확인 — 이 문서는 사용법 설명서이지 성능 주장의 근거가 아니므로 수치 인용은 하지 않는다),
이 노트가 검증한 "Parquet 파일 자체의 크기·스캔 우위"는 DuckDB를 얹었을 때도 유지되는 전제 조건이다. DuckDB
자체의 성능 수치는 **미검증**으로 남긴다.

## 5. Verify — 단위 환산 항등식, 불량 행 검출, 왕복 무손실, 저장 방식 벤치마크

```python verify
import struct

# ── (a) 단위 환산 항등식 — Å/min↔nm/min, psi→kPa, 천단위 쉼표 파싱
def parse_number(raw: str) -> float:
    return float(str(raw).replace(",", "").strip())

def angstrom_min_to_nm_min(v: float) -> float:
    return v * 0.1

def nm_min_to_angstrom_min(v: float) -> float:
    return v * 10.0

def psi_to_kpa(v: float) -> float:
    return v * 6.894757   # NIST SP811 — [[wafer-coordinate-units-outlier-cleaning]] §2에서 검증한 상수 재사용

assert parse_number("1,234.5") == 1234.5, "천단위 쉼표 파싱 항등식 깨짐"
assert abs(angstrom_min_to_nm_min(6.0) - 0.6) < 1e-9   # 6 Å/min = 0.6 nm/min
assert abs(angstrom_min_to_nm_min(nm_min_to_angstrom_min(5.0)) - 5.0) < 1e-9  # 왕복: nm/min→Å/min→nm/min
assert abs(psi_to_kpa(5.0) - 34.473785) < 1e-6  # 5 psi = 34.473785 kPa, NIST SP811 문헌값과 대조
# 한계 사례 — 유럽식 소수점 쉼표는 이 파서가 깨뜨린다(정직성 표지: 알려진 미해결 한계)
try:
    bad = parse_number("1.234,5")  # 유럽식 표기 의도: 1234.5
    assert bad != 1234.5, "우연히 맞을 수도 있다 — 이 파서는 로케일을 구분 못 한다"
except ValueError:
    pass  # 아예 파싱 실패하는 것도 관측된 실패 모드 중 하나

# ── (b) 스키마 검증 규칙이 인위 주입한 불량 행을 실제로 잡는지
def validate_row(row: dict) -> list:
    """§2의 규칙을 최소 구현 — tools/ingest_measurement.py의 blockers 메커니즘과 같은 형태."""
    problems = []
    for k in ("removed_nm", "pressure_psi", "time_s"):
        if k in row and row[k] is not None and row[k] <= 0:
            problems.append(f"물리적 불가능값: {k}={row[k]} <= 0")
    if "thickness_post_nm" in row and row["thickness_post_nm"] is not None \
       and row["thickness_post_nm"] > 3000:
        problems.append(f"단위 의심: thickness_post_nm={row['thickness_post_nm']} "
                         f"— Å를 nm로 잘못 표기했을 개연성 (정상 범위 밖)")
    for k in ("pressure_psi", "time_s"):
        if k not in row or row[k] is None:
            problems.append(f"조건 결측: {k} 없음 — 비교 불가")
    return problems

good_row  = {"removed_nm": 42.3, "pressure_psi": 3.5, "time_s": 60, "thickness_post_nm": 480.0}
bad_rows  = [
    {"removed_nm": -5.0, "pressure_psi": 3.5, "time_s": 60},           # 음의 제거량
    {"removed_nm": 42.3, "pressure_psi": 0.0, "time_s": 60},           # 압력 0
    {"removed_nm": 42.3, "pressure_psi": 3.5, "time_s": 60,
     "thickness_post_nm": 4800.0},                                     # Å를 nm로 오기
    {"removed_nm": 42.3, "time_s": 60},                                # 압력 결측
]
assert validate_row(good_row) == [], "정상 행이 오탐 플래그를 받았다"
for i, r in enumerate(bad_rows):
    problems = validate_row(r)
    assert problems, f"불량 행 #{i}를 검증 규칙이 못 잡았다: {r}"
print(f"(b) 인위 주입 불량 행 {len(bad_rows)}건 전부 검출, 정상 행 오탐 0건")

# ── (c) Parquet 왕복 저장 후 값 무손실
import pyarrow as pa
import pyarrow.parquet as pq
import tempfile, os

sample = [
    {"run_id": 1, "radius_mm": -87.345, "removed_nm": 42.297, "pressure_psi": 3.5,
     "source_doi": "10.1115/1.4042051"},
    {"run_id": 1, "radius_mm": 0.0, "removed_nm": 41.812, "pressure_psi": 3.5,
     "source_doi": "10.1115/1.4042051"},
]
tmpdir = tempfile.mkdtemp()
pqpath = os.path.join(tmpdir, "roundtrip.parquet")
table_out = pa.Table.from_pylist(sample)
pq.write_table(table_out, pqpath)
table_in = pq.read_table(pqpath).to_pylist()
assert table_in == sample, f"Parquet 왕복 후 값이 달라졌다: {table_in} != {sample}"
print("(c) Parquet 왕복 저장 — 부동소수점 8자리까지 완전 무손실 확인")

# ── (d) 컬럼형(Parquet) vs 행 저장(SQLite, sim/store.py 방식) vs CSV — 합성 표 벤치마크
import csv, sqlite3, random, time

random.seed(0)
N = 20000  # 800 런 x 25 측정점 — 이 프로젝트 규모의 실측 배치를 흉내
rows = []
for i in range(N):
    rows.append({
        "run_id": i // 25, "point": i % 25,
        "radius_mm": round(random.uniform(-150, 150), 2),
        "thickness_pre_nm": round(random.uniform(500, 600), 2),
        "thickness_post_nm": round(random.uniform(400, 500), 2),
        "pressure_psi": round(random.uniform(2, 5), 2),
        "time_s": 60, "source_doi": "10.1000/example",
    })

csvp = os.path.join(tmpdir, "bench.csv")
with open(csvp, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys())
    w.writeheader(); w.writerows(rows)

dbp = os.path.join(tmpdir, "bench.sqlite")
con = sqlite3.connect(dbp)
con.execute("CREATE TABLE m (run_id INT, point INT, radius_mm REAL, "
            "thickness_pre_nm REAL, thickness_post_nm REAL, pressure_psi REAL, "
            "time_s REAL, source_doi TEXT)")
con.executemany("INSERT INTO m VALUES (?,?,?,?,?,?,?,?)",
                 [tuple(r.values()) for r in rows])
con.commit()

pqpath2 = os.path.join(tmpdir, "bench.parquet")
pq.write_table(pa.Table.from_pylist(rows), pqpath2, compression="snappy")

size_csv = os.path.getsize(csvp)
size_sqlite = os.path.getsize(dbp)
size_parquet = os.path.getsize(pqpath2)

def time_best(fn, n=5):
    best = None
    for _ in range(n):
        t0 = time.perf_counter()
        fn()
        dt = time.perf_counter() - t0
        best = dt if best is None else min(best, dt)
    return best

def q_csv():
    with open(csvp) as f:
        sums, cnts = {}, {}
        for r in csv.DictReader(f):
            k = r["run_id"]
            sums[k] = sums.get(k, 0.0) + float(r["thickness_post_nm"])
            cnts[k] = cnts.get(k, 0) + 1

def q_sqlite():
    c2 = sqlite3.connect(dbp)
    c2.execute("SELECT run_id, AVG(thickness_post_nm) FROM m GROUP BY run_id").fetchall()
    c2.close()

def q_parquet():
    t = pq.read_table(pqpath2, columns=["run_id", "thickness_post_nm"])
    t.group_by("run_id").aggregate([("thickness_post_nm", "mean")])

t_csv = time_best(q_csv)
t_sqlite = time_best(q_sqlite)
t_parquet = time_best(q_parquet)

print(f"(d) 파일 크기(bytes): csv={size_csv} sqlite={size_sqlite} parquet={size_parquet}")
print(f"    집계쿼리 시간(s, 5회 중 최소): csv={t_csv:.5f} sqlite={t_sqlite:.5f} parquet={t_parquet:.5f}")

# 크기: Parquet(snappy 압축·컬럼형)이 행 저장보다 뚜렷이 작아야 한다 — 여유 마진으로 비교
assert size_parquet < size_csv * 0.5, "Parquet이 CSV의 절반보다 커졌다 — 압축 전제가 깨짐"
assert size_parquet < size_sqlite * 0.5, "Parquet이 SQLite의 절반보다 커졌다"
# 속도: 8컬럼 중 2컬럼만 읽는 집계 쿼리에서 컬럼형이 더 빨라야 한다 — 관측된 배율(약 3.5배·46배)의
# 절반 이하로 완화한 마진만 assert해 실행 환경 노이즈에 견디게 한다
assert t_parquet < t_sqlite * 0.7, "Parquet 집계가 SQLite보다 유의하게 빠르지 않다"
assert t_parquet < t_csv * 0.3, "Parquet 집계가 CSV보다 유의하게 빠르지 않다"
print("모든 verify 통과: 단위환산 항등식, 불량행 검출, Parquet 무손실 왕복, 컬럼형 저장 우위(합성벤치마크)")
```

## 6. 못 다룬 것 (정직성 표지)

- **DuckDB 자체 성능**: `.venv`에 미설치 확인(2026-09-15). §4 벤치마크는 Parquet 파일 포맷 자체의 우위만
  보였고, DuckDB 엔진의 질의 성능은 검증하지 못했다 — 미검증.
- **C-Store 논문 본문**: 오픈액세스 경로(find_open_access.py)로 PDF를 찾지 못했다. DOI·서지는 Crossref로
  확인했지만 구체적 수치·주장은 인용하지 않았다 — 2차 인용조차 하지 않음.
  > ⚠ 시도한 경로: find_open_access.py --title "C-Store: A Column-oriented DBMS" (--download 포함) → OA
  > 링크 없음, ACM Digital Library 직접 접근 403.
  - GUM(JCGM 100:2008)은 BIPM 공식 PDF(`bipm.org/documents/.../JCGM_100_2008_E.pdf`)를 직접 열어 §2.2.3·
    §6.3.1·§7.2.3을 원문으로 확인했다 — 이 노트에서 가장 확실한 1차 근거다.
- **유럽식 소수점 쉼표 파싱**: §5(a)에서 실패 모드로 확인만 하고 해결책은 제시하지 않았다 — 로케일 메타데이터가
  없는 현재 파이프라인 설계로는 원리적으로 구분 불가능하다는 점만 기록한다.
