"""라벨에는 적혀 있는데 모델에 전달되지 않는 변수를 찾는다.

발견 경위 (2026-09-15)
─────────────────────
us20110186542a1 이 C4(배율 두 무리)로 잡혔다. 라벨을 보니 낮은 배율 5점이
전부 "H2O2 0%" 였다. 그런데 분할 진단기는 "어떤 물리 좌표도 가르지 못한다"고
답했다. 둘 중 하나가 틀린 것이다.

확인 결과 **둘 다 맞았다**: H2O2 는 라벨 문자열에만 있고 overrides 에는
없었다. 즉 세 조건이 모델 입장에서 **완전히 동일한 입력**이다.
같은 입력에 다른 실측값이 오니 배율이 갈릴 수밖에 없다.

이것은 모델 결함이 아니라 **데이터셋 결함**이다. 그리고 가장 위험한 종류다:
  · 모델은 조용히 같은 값을 세 번 예측한다 (오류 없음)
  · 검증은 "모델이 산화제를 못 맞춘다"고 읽는다 (원인 오진)
  · 물리를 고치려 들면 있지도 않은 결함을 쫓는다

왜 기계가 찾아야 하는가
──────────────────────
라벨은 사람이 읽는 문자열이고 overrides 는 기계가 읽는 값이다. 둘이
어긋나도 아무도 예외를 던지지 않는다. 사람이 20개 파일을 눈으로 대조하는
것은 신뢰할 수 없다.

판정 규칙
─────────
라벨에서 "이름 + 숫자 + 단위" 패턴을 뽑고, 그 이름에 대응하는 키가
조건에 전달되는지 본다. 라벨 안에서 값이 **변하는데** 전달되지 않으면
그 축은 검증에 쓰이지 못하고 있다.
"""

from __future__ import annotations

import pathlib
import re
import sys
from typing import Dict, List, Optional, Set, Tuple

ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import yaml                                            # noqa: E402

DATASET_DIR = ROOT / "validation" / "datasets"

# 라벨에 쓰이는 표기 → 실제 파라미터 키
# ⚠ 물질명이 아니라 **축 이름**으로 맞춘다.
LABEL_TO_KEY: Dict[str, str] = {
    "h2o2": "oxidizer_wt_pct",
    "과산화수소": "oxidizer_wt_pct",
    "산화제": "oxidizer_wt_pct",
    "ph": "slurry_ph",
    "bta": "inhibitor_mM",
    "억제제": "inhibitor_mM",
    "연마제": "abrasive_wt_pct",
    "입경": "abrasive_size_nm",
    "분산제": "dispersant_wt_pct",
    "압력": "pressure_psi",
    "유량": "sfr_ml_min",
}

# 라벨에서 "이름 숫자(단위)" 를 뽑는다. 이름은 한글·영숫자 모두 허용.
_TOKEN = re.compile(
    r"([A-Za-z가-힣][A-Za-z0-9가-힣_]*)\s*[:=]?\s*([0-9]+(?:\.[0-9]+)?)\s*"
    r"(wt%|%|mM|mL/min|ml/min|mL|ml|L|nm|µm|um|psi|kPa)?",
    re.IGNORECASE,
)

# 키가 요구하는 차원. 라벨의 단위가 여기와 **양립 불가**하면 그 토큰은 이 키의
# 값이 아니다 — 신고하면 거짓 경보가 되고, 거짓 경보가 나면 감사기는 곧 무시당한다.
# (실측: "분산제 2mL/500mL" 라는 부피 서술이 dispersant_wt_pct 미전달로 신고됐다.
#  원문이 밀도를 안 줘서 wt% 로 환산할 수 없는 값이고, 지어내면 안 되는 값이다.)
KEY_UNITS: Dict[str, Set[str]] = {
    "oxidizer_wt_pct": {"wt%", "%"},
    "dispersant_wt_pct": {"wt%", "%"},
    "abrasive_wt_pct": {"wt%", "%"},
    "inhibitor_mM": {"mm"},
    "abrasive_size_nm": {"nm", "µm", "um"},
    "pressure_psi": {"psi", "kpa"},
    "sfr_ml_min": {"ml/min"},
    "slurry_ph": set(),          # pH 는 단위가 없다 — 어떤 단위 토큰도 붙지 않는다
}


def _unit_ok(key: str, unit: Optional[str]) -> bool:
    """라벨의 단위가 그 키의 차원과 양립하는가.

    단위가 아예 없으면 판정하지 않고 통과시킨다(라벨은 자주 단위를 생략한다).
    있는데 어긋나면 그 토큰은 그 키의 값이 아니다.
    """
    if not unit:
        return True
    u = unit.strip().lower()
    allowed = KEY_UNITS.get(key)
    if allowed is None:
        return True
    if key == "slurry_ph":
        return False             # pH 뒤에 단위가 붙었으면 그것은 pH 가 아니다
    return u in {a.lower() for a in allowed}


def _flat(cond: dict) -> dict:
    out = dict(cond)
    ov = out.get("overrides")
    if isinstance(ov, dict):
        out.update(ov)
    return out


def txt_lines_before_conditions(text: str) -> List[str]:
    """conditions: 이전의 주석·설명 줄만 돌려준다.

    조건 블록 안의 label 은 위에서 이미 처리했으므로 중복을 피한다.
    """
    out = []
    for ln in text.split("\n"):
        if ln.startswith("conditions:"):
            break
        out.append(ln)
    return out


def scan(path: pathlib.Path) -> List[str]:
    raw_text = path.read_text(encoding="utf-8")
    raw = yaml.safe_load(raw_text) or {}
    conds = raw.get("conditions") or []
    if len(conds) < 2:
        return []

    # 라벨에서 축별 값을 모은다
    label_axes: Dict[str, Set[float]] = {}
    for c in conds:
        lab = str(c.get("label", ""))
        for name, num, _unit in _TOKEN.findall(lab):
            key = LABEL_TO_KEY.get(name.lower())
            if key and _unit_ok(key, _unit):
                label_axes.setdefault(key, set()).add(float(num))

    # ⚠ 라벨만 보면 놓치는 결함이 있다: 축이 **헤더 주석**에만 적혀 있고
    #   라벨에도 조건에도 없는 경우다. 그러면 위 루프가 0건을 돌려주고
    #   감사기는 '깨끗함'을 보고한다 — 실제로 구리 4계열이 이렇게 침묵했다.
    #   주석에 그 축이 언급되는데 조건에 전혀 전달되지 않으면 신고한다.
    header_axes: Set[str] = set()
    for line in txt_lines_before_conditions(raw_text):
        for name, _num, _unit in _TOKEN.findall(line):
            key = LABEL_TO_KEY.get(name.lower())
            if key and key not in label_axes and _unit_ok(key, _unit):
                header_axes.add(key)

    problems = []
    for key, vals in sorted(label_axes.items()):
        if len(vals) < 2:
            continue                      # 라벨에서도 안 변한다 — 문제 아님
        passed = [k for c in conds for k in _flat(c) if k == key]
        if not passed:
            problems.append(
                f"🔴 {key}: 라벨에서 {sorted(vals)} 로 **변하는데** 조건에 "
                f"전달되지 않는다. 모델은 이 축을 보지 못한다."
            )
        else:
            # 전달은 되는데 값이 고정이면 그것도 문제다
            passed_vals = {float(_flat(c)[key]) for c in conds if key in _flat(c)
                           and isinstance(_flat(c)[key], (int, float))}
            if len(passed_vals) < 2:
                problems.append(
                    f"🟡 {key}: 라벨은 {sorted(vals)} 로 변하는데 전달값은 "
                    f"{sorted(passed_vals)} 로 고정이다."
                )

    # 헤더 주석에만 있고 조건에 전혀 없는 축
    for key in sorted(header_axes):
        passed = [k for c in conds for k in _flat(c) if k == key]
        if not passed:
            problems.append(
                f"🟠 {key}: 문서 상단 설명에는 나오는데 조건에 **전혀** 전달되지 "
                f"않는다. 라벨에도 없어 조용히 넘어간다 — 모델은 이 축을 "
                f"팩 기본값으로 계산한다."
            )
    return problems


def main() -> int:
    print("=" * 84)
    print("라벨에만 있고 모델에 전달되지 않는 축 — 데이터셋 결함")
    print("=" * 84)
    print("이 결함은 조용하다: 모델은 같은 입력에 같은 값을 예측하고(오류 없음),")
    print("검증은 '모델이 그 축을 못 맞춘다'고 오진한다.")
    print()
    total = 0
    for path in sorted(DATASET_DIR.glob("*.yaml")):
        probs = scan(path)
        if probs:
            print(f"■ {path.stem}")
            for p in probs:
                print(f"    {p}")
            total += len(probs)
    print()
    print("-" * 84)
    if total:
        print(f"결함 {total}건 — 고치기 전에는 그 축의 검증 결과를 믿을 수 없다.")
    else:
        print("✅ 라벨과 전달값이 일치한다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
