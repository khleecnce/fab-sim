"""특허 전문에서 "조성 → 제거율" 짝을 뽑아낸다.

특허 실시예의 실제 구조
──────────────────────
특허는 조성과 결과를 **한 표에 싣지 않는다.** 보통 이렇게 나뉜다:

    Table 1 : 예시번호별 조성      (C1  실리카 1.0  KIO3 0.6  pH 2.2 …)
    Table 2 : 공정 조건            (하중 20.7 kPa  회전 133 rpm …)
    Table 3 : 예시번호별 제거율    (C1  2580 Å/min …)

즉 **예시번호가 외래키**다. 이 키로 조성과 결과를 join 해야 비로소
"조성을 이만큼 바꿨더니 제거율이 이렇게 변했다"는 한 줄이 나온다.

수집기가 표를 하나씩만 보던 때에는 조성표에 제거율이 없다는 이유로
버리거나, 결과표만 주워 조성을 모르는 숫자를 얻었다. 둘 다 쓸모없다.

⚠ 이 모듈은 **읽기만** 한다. 값을 보정하거나 채워 넣지 않는다.
  표에 없는 것은 없는 채로 둔다 — 빈칸을 추정으로 메우면 그 순간
  데이터가 아니라 창작이 된다.
"""

from __future__ import annotations

import re
from typing import Dict, List, Optional, Tuple

__all__ = ["parse_patent", "ExampleRow"]

RATE_RE = re.compile(r"(Å|A|nm|µm|um)\s*/\s*min", re.I)
# 예시 라벨 — 특허마다 표기가 제각각이다. 실측으로 확인된 형태:
#   C1  CE-1  PC1  Ex 3  PS-1  CS-1  S-1  Sample 2  Slurry 4  1  12
# ⚠ 처음에 C/CE/PC/Ex/숫자만 잡았더니 108건 중 91건이 "라벨 없음"으로
#   버려졌다. 접두사를 열거하지 말고 **모양**으로 잡는다:
#   "알파벳 1~4자 + 선택적 구분자 + 숫자" 또는 "순수 숫자".
LABEL_RE = re.compile(
    r"^(?:[A-Z]{1,4}[-–_ ]?\d{1,3}[A-Z]?|\d{1,3})$", re.I)

# 라벨로 오인하기 쉬운 단어 — 단위·화학식·표 머리글에 흔한 토큰
_NOT_LABEL = {
    "H2O2", "H2O", "KIO3", "SIO2", "CEO2", "AL2O3", "NH4", "KOH", "HNO3",
    "NO3", "PEG", "PSS", "PH", "RPM", "KPA", "PSI", "WT", "PPM", "MIN",
    "FIG", "NO", "MW", "DI", "UV", "ND", "NA", "CMP", "CMPC", "TEOS",
}


class ExampleRow(dict):
    """예시 하나 = 조성 + 공정 + 결과."""


def _sections(text: str) -> List[Tuple[int, str, str]]:
    """TABLE 헤더 위치로 구간을 자른다. (시작, 표이름, 본문)"""
    marks = [(m.start(), m.group(0)) for m in
             re.finditer(r"TABLE\s+[\dIVX]+", text, re.I)]
    if not marks:
        return []
    # 같은 위치 근처의 중복 헤더(본문에서 표를 '언급'만 한 것)를 접는다
    dedup = []
    for pos, name in marks:
        if dedup and pos - dedup[-1][0] < 120:
            continue
        dedup.append((pos, name))
    out = []
    for i, (pos, name) in enumerate(dedup):
        end = dedup[i + 1][0] if i + 1 < len(dedup) else min(len(text), pos + 4000)
        out.append((pos, name, text[pos:end]))
    return out


def _numbers_after_label(seg: str) -> Dict[str, List[float]]:
    """'라벨 숫자 숫자 …' 패턴을 훑어 예시별 숫자열을 만든다."""
    toks = seg.split()
    rows: Dict[str, List[float]] = {}
    cur: Optional[str] = None
    for tok in toks:
        t = tok.strip(",;:()")
        norm = t.upper().replace("-", "").replace("–", "").replace("_", "").replace(".", "")
        if norm in _NOT_LABEL:
            continue
        # 순수 숫자는 라벨이 아니라 값일 확률이 훨씬 높다.
        # 앞에 이미 라벨이 있으면 값으로 취급한다.
        if LABEL_RE.match(t) and not _is_float(t.replace(",", "")):
            cur = norm
            rows.setdefault(cur, [])
            continue
        if cur is not None:
            v = _to_float(t)
            if v is not None:
                rows[cur].append(v)
            elif t in ("—", "-", "–", "NA", "N/A"):
                rows[cur].append(float("nan"))
    return {k: v for k, v in rows.items() if v}


def _is_float(s: str) -> bool:
    return _to_float(s) is not None


def _to_float(s: str) -> Optional[float]:
    s = s.replace(",", "").strip()
    if not s or not re.match(r"^-?\d*\.?\d+$", s):
        return None
    try:
        return float(s)
    except ValueError:
        return None


def _header_terms(seg: str) -> List[str]:
    """표 머리글에서 열 이름 후보를 뽑는다(순서 보존)."""
    head = seg[:400]
    terms = re.findall(
        r"(pH|wt\s*%|ppm|Å/min|A/min|nm/min|RPM|kPa|ml/min|"
        r"removal rate|particle size|abrasive|oxidizer|inhibitor|"
        r"H\s*2\s*O\s*2|KIO\s*3|glycine|silica|ceria|alumina)",
        head, re.I)
    return [t.strip() for t in dict.fromkeys(t.lower() for t in terms)]


def parse_patent(text: str) -> Dict[str, object]:
    """전문 텍스트 → 예시별 조성·결과 묶음.

    반환:
        {
          "tables":  [{"name","kind","terms","rows"}...],
          "examples": {"C1": {"composition":[...], "rate":[...]}, ...},
          "joinable": 조성과 결과가 **같은 라벨로 이어진** 예시 수
        }
    """
    secs = _sections(text)
    tables = []
    comp_rows: Dict[str, List[float]] = {}
    rate_rows: Dict[str, List[float]] = {}

    for pos, name, seg in secs:
        # ⚠ 표 종류 판정은 **머리글에서만** 한다.
        #   본문 어딘가에 "removal rate"가 한 번 스쳐도 구간 전체를 결과표로
        #   오판하면 조성표와 결과표가 뒤바뀐다(실측으로 겪음: 조성 자리에
        #   유량·하중·RPM 이 들어오고 결과 자리에 wt% 가 들어왔다).
        #   결과표는 머리글에 단위(Å/min 등) 또는 'removal rate'가 있다.
        head = seg[:300].lower()
        has_rate = bool(RATE_RE.search(seg[:300])) or "removal rate" in head
        rows = _numbers_after_label(seg)
        if not rows:
            continue
        kind = "result" if has_rate else "composition"
        tables.append({"name": name, "kind": kind,
                       "terms": _header_terms(seg), "n_rows": len(rows)})
        target = rate_rows if kind == "result" else comp_rows
        for k, v in rows.items():
            # 같은 라벨이 여러 표에 나오면 더 긴 쪽(정보가 많은 쪽)을 쓴다
            if len(v) > len(target.get(k, [])):
                target[k] = v

    labels = sorted(set(comp_rows) | set(rate_rows))
    examples = {}
    for lab in labels:
        examples[lab] = {"composition": comp_rows.get(lab, []),
                         "rate": rate_rows.get(lab, [])}
    joinable = sum(1 for lab in labels
                   if comp_rows.get(lab) and rate_rows.get(lab))

    return {"tables": tables, "examples": examples,
            "n_examples": len(labels), "joinable": joinable}
