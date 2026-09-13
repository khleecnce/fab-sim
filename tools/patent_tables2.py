"""특허 실시예 표를 **열 이름과 함께** 읽는다.

앞선 파서가 실패한 이유
──────────────────────
숫자를 위치로만 주웠다. 특허 표는 열 구성이 제각각이라(금속이온 ppm,
Mc/Mm 비, 균일도, 여러 막질의 제거율…) 위치가 의미를 보장하지 않는다.
정답을 아는 특허로 검증했더니 제거율 자리에 남의 숫자가 들어왔다.

그래서 이 파서는 **머리글을 먼저 읽는다.**

특허 표의 실제 모양 (HTML 태그를 지운 뒤)
────────────────────────────────────────
    TABLE 1 Polishing Solution Parameters and Tungsten Removal Results
    Metal Ion   Removal
    Conc.   H 2 O 2 Conc.   Rate   % Non-
    Example (ppm)   (Mc/Mm)   (wt %)   (Å/min.)   Uniformity
    1   1180   1.6   4.07   2,410   3.9
    2   5   1.6   4.06   2,396   17.9

머리글이 여러 줄로 쪼개져 있고(Metal Ion / Conc. / (ppm)), 단위가 괄호로
따로 붙는다. 그래서 "이름 줄"과 "단위 줄"을 합쳐 열을 복원해야 한다.

전략
────
1) 데이터 행을 먼저 찾는다 — "라벨 + 숫자 n개"가 **연속으로 반복**되는 구간.
   행마다 숫자 개수가 같아야 진짜 표다(이게 강력한 신호다).
2) 데이터 행 직전 텍스트가 머리글이다. 거기서 단위 토큰을 순서대로 뽑는다.
3) 단위 개수와 열 개수가 맞으면 짝짓는다. 안 맞으면 **버린다** —
   억지로 맞추면 조용히 틀린 값이 들어온다.

⚠ 원칙: 확신이 없으면 버린다. 검증용 데이터가 오염되는 것이
  데이터가 적은 것보다 훨씬 나쁘다.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

__all__ = ["Table", "parse_tables", "find_rate_columns", "find_axis_columns"]


NUM = r"-?\d[\d,]*\.?\d*"
NUM_RE = re.compile(NUM)
BLANK = {"—", "-", "–", "NA", "N/A", "ND", "nil", "none"}

LABEL_RE = re.compile(r"^(?:[A-Z]{1,5}[-–_ ]?\d{1,3}[A-Z]?|\d{1,3})$", re.I)
_NOT_LABEL = {
    "H2O2", "H2O", "KIO3", "SIO2", "CEO2", "AL2O3", "NH4", "KOH", "HNO3",
    "NO3", "PEG", "PSS", "PH", "RPM", "KPA", "PSI", "WT", "PPM", "MIN",
    "FIG", "NO", "MW", "DI", "UV", "ND", "NA", "CMP", "CMPC", "TEOS",
    "TABLE", "EX", "CE", "PS", "CS", "PC",
}

# 열 역할 — 이름만 보고 무엇인지 판정한다 (물질명 아님, 물리량 이름)
ROLE_PATTERNS: List[Tuple[str, str]] = [
    ("rate",        r"(Å|A|nm|µm|um)\s*/\s*min|removal\s*rate|polish(?:ing)?\s*rate|RR\b"),
    ("ph",          r"^\s*pH\s*$|\bpH\b"),
    ("wt_pct",      r"wt\.?\s*%|weight\s*%|%\s*by\s*weight"),
    ("ppm",         r"\bppm\b"),
    ("size_nm",     r"(particle\s*size|mean\s*size|d50|diameter).{0,20}(nm|µm|um)|(nm|µm|um).{0,10}(size|diameter)"),
    ("pressure",    r"\bkPa\b|\bpsi\b|down\s*force|down\s*pressure"),
    ("rpm",         r"\bRPM\b|\brpm\b|platen\s*speed|carrier\s*speed"),
    ("flow",        r"m[lL]\s*/\s*min|flow\s*rate"),
    ("ratio",       r"selectivit|ratio|Mc\s*/\s*Mm"),
    ("uniformity",  r"non-?\s*uniformit|NU\b|WIWNU"),
    ("time_s",      r"\b\d+\s*s(ec)?\b|time\s*\("),
]


@dataclass
class Table:
    name: str
    header_text: str
    columns: List[str]                      # 열 이름 (머리글에서 복원)
    roles: List[str]                        # 각 열의 역할 판정
    rows: Dict[str, List[float]]            # 라벨 → 값들
    n_cols: int = 0
    confident: bool = False                 # 열 수와 이름 수가 맞는가
    notes: List[str] = field(default_factory=list)

    def col(self, role: str) -> List[int]:
        return [i for i, r in enumerate(self.roles) if r == role]


def _to_float(s: str) -> Optional[float]:
    s = s.replace(",", "").strip()
    if s in BLANK:
        return math.nan
    if not re.fullmatch(NUM, s):
        return None
    try:
        return float(s)
    except ValueError:
        return None


def _data_rows(seg: str) -> Tuple[List[Tuple[str, List[float]]], int, int]:
    """라벨+숫자 행을 찾는다.

    반환: (행 목록, 열 개수, 데이터 시작 위치)
    열 개수는 **최빈값**으로 정한다 — 일부 행은 빈칸 때문에 짧다.
    """
    toks = seg.split()
    rows: List[Tuple[str, List[float]]] = []
    starts: List[int] = []
    cur_lab: Optional[str] = None
    cur_vals: List[float] = []
    cur_start = 0

    # 순수 숫자 라벨(Example 1, 2, 3 …)을 값과 구분하는 법
    # ───────────────────────────────────────────────────
    # 토큰만 보면 라벨 "1" 과 값 "1" 이 똑같다. 구분 단서는 **위치**다:
    # 표는 열 수가 일정하므로, 직전 행이 n_cols 개를 채웠으면 다음 토큰은
    # 새 행의 라벨이다. 그래서 1차로 문자 라벨만 잡아 열 수를 확정한 뒤,
    # 2차로 그 열 수를 이용해 숫자 라벨 행을 회수한다.
    # (이 처리를 안 하면 Example 1~4 행이 통째로 사라진다 — 실제로 겪었다.)
    for i, tok in enumerate(toks):
        t = tok.strip(",;:()")
        norm = t.upper().replace("-", "").replace("–", "").replace("_", "").replace(".", "")
        is_lab = (LABEL_RE.match(t) and norm not in _NOT_LABEL
                  and _to_float(t) is None)
        if is_lab:
            if cur_lab is not None and cur_vals:
                rows.append((cur_lab, cur_vals))
                starts.append(cur_start)
            cur_lab, cur_vals, cur_start = norm, [], i
            continue
        if cur_lab is None:
            continue
        v = _to_float(t)
        if v is not None:
            cur_vals.append(v)
        elif t in BLANK:
            cur_vals.append(math.nan)
        # 단어가 나오면 행이 끝났을 수 있으나, 표 안 주석일 수도 있어 계속 둔다

    if cur_lab is not None and cur_vals:
        rows.append((cur_lab, cur_vals))
        starts.append(cur_start)

    if not rows:
        return [], 0, 0

    # ── 표 맨 앞의 숫자 라벨 행 회수 ────────────────────────
    # 머리글이 끝나는 지점 뒤부터 첫 문자 라벨(CE-1 등)까지 사이에
    # "1 1180 1.6 4.07 2410 3.9  2 5 1.6 ..." 처럼 숫자 라벨 행이 먼저
    # 나오는 표가 흔하다. 첫 문자 라벨만 찾던 로직은 이 구간을 통째로
    # 머리글로 오인해 버렸다(Example 1~4 가 사라졌다).
    from collections import Counter as _C
    _n = _C(len(v) for _, v in rows).most_common(1)[0][0]
    first_start = starts[0] if starts else len(toks)
    # 머리글 끝 = 마지막 괄호 단위 뒤 또는 마지막 알파벳 낱말 뒤
    head_end = 0
    for j in range(first_start - 1, -1, -1):
        tk = toks[j].strip(",;:()")
        if re.search(r"[A-Za-z]", tk) and _to_float(tk) is None:
            head_end = j + 1
            break
    lead = toks[head_end:first_start]
    lead_vals: List[float] = []
    for tk in lead:
        t2 = tk.strip(",;:()")
        v = _to_float(t2)
        lead_vals.append(v if v is not None else math.nan)
    # (라벨 1 + 값 _n) 단위로 끊어 되살린다
    pre_rows: List[Tuple[str, List[float]]] = []
    k = 0
    while k + _n + 1 <= len(lead_vals):
        lab_v = lead_vals[k]
        if not (isinstance(lab_v, float) and not math.isnan(lab_v)
                and float(lab_v).is_integer() and 0 < lab_v < 200):
            break
        pre_rows.append((str(int(lab_v)), lead_vals[k + 1:k + 1 + _n]))
        k += _n + 1
    if pre_rows:
        rows = pre_rows + rows

    from collections import Counter
    n_cols = Counter(len(v) for _, v in rows).most_common(1)[0][0]

    # ── 2차: 숫자 라벨 행 회수 ──────────────────────────────
    # 값이 n_cols 를 **초과**해 흘러넘친 행은, 그 안에 숫자 라벨로 시작하는
    # 다음 행들이 붙어 있다는 뜻이다. n_cols+1 개씩(라벨 1 + 값 n_cols)
    # 끊어 되살린다.
    fixed: List[Tuple[str, List[float]]] = []
    for lab, vals in rows:
        if len(vals) <= n_cols:
            fixed.append((lab, vals))
            continue
        fixed.append((lab, vals[:n_cols]))
        rest = vals[n_cols:]
        while len(rest) >= n_cols + 1:
            sub_lab = rest[0]
            # 라벨은 작은 정수여야 한다(Example 번호). 아니면 중단.
            if not (float(sub_lab).is_integer() and 0 < sub_lab < 200):
                break
            fixed.append((str(int(sub_lab)), rest[1:1 + n_cols]))
            rest = rest[1 + n_cols:]
    rows = fixed
    return rows, n_cols, (starts[0] if starts else 0)


def _header_columns(head: str, n_cols: int) -> Tuple[List[str], bool]:
    """머리글에서 열 이름 n_cols 개를 복원한다.

    실제 특허 머리글의 모양(HTML 태그 제거 후):

        ... Metal Ion Removal Conc. H 2 O 2 Conc. Rate % Non-
        Example (ppm) Mc/Mm (wt %) (Å/min.) Uniformity  1 1180 1.6 ...
                ^^^^^ ^^^^^ ^^^^^^ ^^^^^^^^ ^^^^^^^^^^
                열1   열2   열3    열4      열5

    핵심: 행 라벨 열 이름(Example/Sample/Slurry/Ex/CMPC…) **뒤부터**
    데이터 시작 전까지가 열 머리글이고, 각 열은
      · 괄호 단위  `(ppm)` `(wt %)` `(Å/min.)`   또는
      · 괄호 없는 낱말 `Mc/Mm` `Uniformity` `pH`
    로 나타난다. 둘을 **같은 자격의 토큰**으로 순서대로 세어야 한다.
    (괄호만 세면 `Mc/Mm`·`Uniformity` 가 빠져 개수가 안 맞는다.)
    """
    # 1) 라벨 열 이름을 찾아 그 뒤만 본다
    m = re.search(r"\b(Example|Sample|Slurry|Ex\.?|CMPC|Composition|Formulation|No\.?)\b",
                  head, re.I)
    tail = head[m.end():] if m else head

    # 2) 괄호 단위와 괄호 밖 낱말을 **등장 순서대로** 수집
    toks: List[str] = []
    pos = 0
    for mm in re.finditer(r"\(([^)]{1,24})\)", tail):
        between = tail[pos:mm.start()]
        for w in re.findall(r"[A-Za-z%][A-Za-z0-9%/\.\-]{1,20}", between):
            if w.lower() in ("the", "and", "with", "of", "in", "for", "to"):
                continue
            toks.append(w)
        u = mm.group(1).strip()
        if not re.fullmatch(r"\d+", u):
            toks.append(f"({u})")
        pos = mm.end()
    for w in re.findall(r"[A-Za-z%][A-Za-z0-9%/\.\-]{1,20}", tail[pos:]):
        if w.lower() in ("the", "and", "with", "of", "in", "for", "to"):
            continue
        toks.append(w)

    if len(toks) == n_cols:
        return toks, True

    # 3) 괄호만으로 맞는 경우 (모든 열에 단위가 붙은 표)
    units = [f"({u.strip()})" for u in re.findall(r"\(([^)]{1,24})\)", tail)
             if not re.fullmatch(r"\d+", u.strip())]
    if len(units) == n_cols:
        return units, True

    # 4) 머리글이 여러 줄로 쪼개진 표
    #    "Slurry PVD Co RR TiN RR Selectivity # (Å/min) (Å/min) Co:TiN"
    #    처럼 이름 줄과 단위 줄이 따로 있고, 라벨 열 이름(#)이 중간에 낀다.
    #    이때는 **단위 줄만** 열 앵커로 쓰고, 그 앞 이름을 가까운 순서로
    #    붙인다. 단위 개수가 열 수보다 적으면 남는 열은 이름만으로 채운다.
    if 0 < len(units) < n_cols:
        names = [w for w in re.findall(r"[A-Za-z%][A-Za-z0-9%/\.\-:]{1,20}", tail)
                 if w.lower() not in ("the", "and", "with", "of", "in", "for",
                                      "to", "table", "results")]
        merged: List[str] = []
        # 단위가 붙은 열을 뒤에서부터 배치하고 앞쪽은 이름으로 메운다
        n_name = n_cols - len(units)
        merged.extend(names[:n_name])
        merged.extend(units)
        if len(merged) == n_cols:
            return merged, True

    return toks or units, False


def _role_of(colname: str) -> str:
    for role, pat in ROLE_PATTERNS:
        if re.search(pat, colname, re.I):
            return role
    return "unknown"


def parse_tables(text: str) -> List[Table]:
    """전문에서 표를 추출한다."""
    marks = [(m.start(), m.group(0)) for m in
             re.finditer(r"TABLE\s+[\dIVX]+", text, re.I)]
    dedup: List[Tuple[int, str]] = []
    for pos, name in marks:
        if dedup and pos - dedup[-1][0] < 100:
            continue
        dedup.append((pos, name))

    out: List[Table] = []
    for i, (pos, name) in enumerate(dedup):
        end = dedup[i + 1][0] if i + 1 < len(dedup) else min(len(text), pos + 5000)
        seg = text[pos:end]
        rows, n_cols, dstart = _data_rows(seg)
        if not rows or n_cols < 2:
            continue
        toks = seg.split()
        head = " ".join(toks[:dstart]) if dstart else seg[:300]
        cols, ok = _header_columns(head, n_cols)
        roles = [_role_of(c) for c in cols] if ok else []
        t = Table(
            name=name, header_text=head[:400], columns=cols, roles=roles,
            rows={lab: vals for lab, vals in rows if len(vals) == n_cols},
            n_cols=n_cols, confident=ok,
        )
        if not ok:
            t.notes.append(
                f"열 이름 복원 실패: 단위 {len(cols)}개 vs 열 {n_cols}개 "
                "— 위치로 추측하지 않고 버린다")
        out.append(t)
    return out


def find_rate_columns(t: Table) -> List[int]:
    return t.col("rate")


def find_axis_columns(t: Table) -> Dict[str, List[int]]:
    """조성/공정 축 열."""
    axes = {}
    for role in ("wt_pct", "ppm", "ph", "size_nm", "pressure", "rpm", "flow"):
        idx = t.col(role)
        if idx:
            axes[role] = idx
    return axes
