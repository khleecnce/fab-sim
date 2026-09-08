#!/usr/bin/env python3
"""PHM 2016 Data Challenge CMP 데이터를 받아 공정조건-MRR 쌍으로 조인한다.

⚠ 이 데이터의 한계는 `validation/raw/phm2016/README.md`에 적혀 있다.
   요약: 컬럼이 스케일링돼 물리 단위가 아니고, 슬러리 조성이 없고,
   압력이 사실상 고정(96%가 257~270)이라 Preston 검증에 쓸 수 없다.
   쓸 수 있는 건 **소모품 열화 → MRR 감소** 하나다.

사용:
    python3 validation/fetch_phm2016.py            # 기본 40파일
    python3 validation/fetch_phm2016.py --files 186  # 전체(187MB)
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
import subprocess
import sys
import urllib.parse
from collections import defaultdict
from pathlib import Path

BASE = "https://raw.githubusercontent.com/akangel0307/PHM-Data-Challenge/master/"
SET = "data/2016 PHM Data Challenge/2016 PHM DATA CHALLENGE CMP DATA SET/"
ANS = "data/2016 PHM Data Challenge/PHM16TestValidationAnswers/PHM16TestValidationAnswers/"
ROOT = Path(__file__).resolve().parent / "raw" / "phm2016"

LABELS = {
    "training-removalrate.csv": SET + "CMP-training-removalrate.csv",
    "validation-answers.csv": ANS + "orig_CMP-validation-removalrate.csv",
    "test-answers.csv": ANS + "orig_CMP-test-removalrate.csv",
}


def fetch(remote: str, dest: Path, min_bytes: int = 1000) -> bool:
    if dest.exists() and dest.stat().st_size > min_bytes:
        return True
    dest.parent.mkdir(parents=True, exist_ok=True)
    r = subprocess.run(
        ["curl", "-sL", "--max-time", "90", BASE + urllib.parse.quote(remote),
         "-o", str(dest), "-w", "%{http_code}"],
        capture_output=True, text=True)
    ok = r.stdout.strip() == "200" and dest.exists() and dest.stat().st_size > min_bytes
    if not ok:
        dest.unlink(missing_ok=True)
    return ok


def spearman(xs: list[float], ys: list[float]) -> float:
    def rank(v):
        s = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(s):
            j = i
            while j + 1 < len(s) and v[s[j + 1]] == v[s[i]]:
                j += 1
            avg = (i + j) / 2 + 1
            for k in range(i, j + 1):
                r[s[k]] = avg
            i = j + 1
        return r
    if len(xs) < 3:
        return float("nan")
    rx, ry = rank(xs), rank(ys)
    n = len(xs)
    mx, my = sum(rx) / n, sum(ry) / n
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))
    return num / den if den else float("nan")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--files", type=int, default=40, help="받을 시계열 파일 수 (최대 186)")
    a = ap.parse_args()

    print("[1/3] 정답(MRR) 파일")
    for name, remote in LABELS.items():
        ok = fetch(remote, ROOT / name)
        print(f"   {'✓' if ok else '✗'} {name}")

    mrr: dict[tuple[str, str], float] = {}
    for name in LABELS:
        p = ROOT / name
        if not p.exists():
            continue
        for r in csv.DictReader(open(p)):
            mrr[(r["WAFER_ID"], r["STAGE"])] = float(r["AVG_REMOVAL_RATE"])
    print(f"   MRR 라벨 {len(mrr)}건")

    print(f"[2/3] 시계열 {a.files}파일")
    ts_dir = ROOT / "timeseries"
    got = 0
    for i in range(a.files):
        name = f"CMP-training-{i:03d}.csv"
        if fetch(SET + f"CMP-data/training/{name}", ts_dir / name, min_bytes=10000):
            got += 1
    print(f"   {got}파일 수집")

    print("[3/3] 조인")
    agg: dict = defaultdict(lambda: defaultdict(list))
    cols = {"pressure": "MAIN_OUTER_AIR_BAG_PRESSURE",
            "stage_rot": "STAGE_ROTATION", "head_rot": "HEAD_ROTATION",
            "slurry_a": "SLURRY_FLOW_LINE_A",
            "pad_usage": "USAGE_OF_POLISHING_TABLE", "dresser": "USAGE_OF_DRESSER"}
    for f in sorted(ts_dir.glob("*.csv")):
        for r in csv.DictReader(open(f)):
            key = (r.get("WAFER_ID"), r.get("STAGE"))
            if key not in mrr:
                continue
            try:
                # 압력 0 = 비연마 구간. 포함하면 중앙값이 무너진다.
                if float(r[cols["pressure"]] or 0) <= 0:
                    continue
                for k, c in cols.items():
                    agg[key][k].append(float(r[c] or 0))
            except (ValueError, KeyError):
                continue

    rows = []
    for key, d in agg.items():
        if len(d["pressure"]) < 20:
            continue
        row = {"wafer": key[0], "stage": key[1], "mrr": mrr[key]}
        row.update({k: statistics.median(v) for k, v in d.items()})
        rows.append(row)

    out = ROOT / "joined.json"
    json.dump(rows, open(out, "w"), indent=1)
    print(f"   조건+MRR {len(rows)} 웨이퍼 → {out}")

    if rows:
        ys = [r["mrr"] for r in rows]
        print("\n검증 가능한 관계 (Spearman):")
        for f in ("dresser", "pad_usage", "pressure"):
            note = ""
            if f == "pressure":
                note = "  ⚠ 양산 레시피라 고정 — 인과 해석 금지"
            print(f"   {f:10s} ρ = {spearman([r[f] for r in rows], ys):+.3f}{note}")
        lo = [r for r in rows if r["mrr"] < 120]
        if len(lo) > 20:
            print(f"   dresser(저속군 {len(lo)}건) ρ = "
                  f"{spearman([r['dresser'] for r in lo], [r['mrr'] for r in lo]):+.3f}")
    print("\n⚠ 한계는 validation/raw/phm2016/README.md 를 읽어라.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
