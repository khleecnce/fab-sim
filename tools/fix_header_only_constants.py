"""헤더 주석에만 있던 조건 상수를 conditions 로 전달한다.

무엇을 하는가
────────────
데이터셋 상단 설명에 "pH 8.5~9.5", "slurry 200 mL/min" 처럼 적혀 있는데
conditions 에 전혀 전달되지 않는 축을 찾아, **전 조건 공통 상수**로 넣는다.

⚠ 정당성: 이 값들은 원 특허·논문이 명시한 실험 조건이고, 그 계열 안에서
  고정이다. 추정이 아니다. 전 조건 동일값이므로 **순위에는 영향이 없고**
  절대 배수와 게이트 판정만 바뀐다 — 그리고 그 게이트 판정이 목적이다
  (pH 10 조건을 모델이 pH 4 로 계산하고 있었다).

⚠ 범위가 적힌 경우(pH 8.5~9.5)는 중앙값을 쓰고 노트에 폭을 남긴다.
  단일값으로 확정된 것처럼 적지 않는다.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

DS = ROOT / "validation" / "datasets"

# (파일, 키, 값, 근거) — 전부 그 데이터셋 상단이 명시한 값이다.
FIXES = [
    # 구리 알칼리 계열 — pH 게이트 판정에 반드시 필요하다
    ("us9200180b2_cu_abrasive_series.yaml", "slurry_ph", 9.5,
     "상단 설명 'pH 9~10 알칼리' 의 중앙값"),
    ("us9200180b2_cu_h2o2_series.yaml", "slurry_ph", 9.0,
     "상단 설명 'pH 8.5~9.5 알칼리' 의 중앙값"),
    ("us20110165777a1_cu_h2o2_series.yaml", "slurry_ph", 11.1,
     "상단 설명 'pH 11.1'"),
    ("tw202115224a_cu_abrasive_size_pressure.yaml", "slurry_ph", 7.2,
     "상단 설명 'pH 7.20'"),
]


def add_const(path: pathlib.Path, key: str, val: float) -> int:
    lines = path.read_text(encoding="utf-8").split("\n")
    out, n = [], 0
    for ln in lines:
        mo = re.match(r"^(\s*)overrides:\s*\{(.*)\}\s*$", ln)
        if mo and key not in mo.group(2):
            indent, body = mo.group(1), mo.group(2).strip().rstrip(",")
            body = (body + ", ") if body else ""
            ln = f"{indent}overrides: {{{body}{key}: {val}}}"
            n += 1
        out.append(ln)
    if n:
        path.write_text("\n".join(out), encoding="utf-8")
    return n


def main() -> int:
    total = 0
    for fname, key, val, why in FIXES:
        p = DS / fname
        if not p.exists():
            print(f"⚠ 없음: {fname}")
            continue
        n = add_const(p, key, val)
        total += n
        print(f"{fname[:48]:48s} {key}={val:<6g} {n:2d}개 조건  ({why})")
    print(f"\n합계 {total}개 조건에 전달 추가")
    return 0


if __name__ == "__main__":
    sys.exit(main())
