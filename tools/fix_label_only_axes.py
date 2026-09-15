"""라벨에만 있던 축을 overrides 로 옮긴다.

⚠ 라벨 문자열에서 숫자를 뽑아 넣는다. 이것이 정당한 이유:
  라벨은 원 특허/논문 표를 옮길 때 사람이 적은 것이고, 그 숫자는 원표의
  조성값이다. 추정이 아니다.

⚠ 반드시 확인할 것: 옮긴 뒤 모델 예측이 **실제로 달라지는지**.
  달라지지 않으면 축이 여전히 죽어 있다는 뜻이다(기준점 부재 등).
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

DS = ROOT / "validation" / "datasets"

TARGETS = {
    "us20110186542a1_w_diamond_h2o2_ph.yaml": [
        (r"H2O2\s*([0-9.]+)%", "oxidizer_wt_pct"),
        (r"pH\s*([0-9.]+)", "slurry_ph"),
    ],
    "mo2026_double_sided_L16.yaml": [
        (r"H2O2\s*([0-9.]+)%", "oxidizer_wt_pct"),
        (r"pH\s*([0-9.]+)", "slurry_ph"),
    ],
    "carbide2023_slurry_composition_L9.yaml": [
        (r"분산제\s*([0-9.]+)", "dispersant_wt_pct"),
    ],
}


def fix(path: pathlib.Path, rules) -> int:
    lines = path.read_text(encoding="utf-8").split("\n")
    out, n, cur = [], 0, None
    for ln in lines:
        m = re.match(r"^(\s*)-\s+label:\s*\"(.+)\"\s*$", ln)
        if m:
            cur = m.group(2)
        # overrides 줄에 값을 끼워 넣는다
        mo = re.match(r"^(\s*)overrides:\s*\{(.*)\}\s*$", ln)
        if mo and cur:
            indent, body = mo.group(1), mo.group(2)
            adds = []
            for pat, key in rules:
                if key in body:
                    continue
                mm = re.search(pat, cur, re.IGNORECASE)
                if mm:
                    adds.append(f"{key}: {float(mm.group(1))}")
            if adds:
                body = (body.strip().rstrip(",") + ", " if body.strip() else "")
                ln = f"{indent}overrides: {{{body}{', '.join(adds)}}}"
                n += len(adds)
        out.append(ln)
    if n:
        path.write_text("\n".join(out), encoding="utf-8")
    return n


def main() -> int:
    total = 0
    for name, rules in TARGETS.items():
        p = DS / name
        if not p.exists():
            print(f"⚠ 없음: {name}")
            continue
        k = fix(p, rules)
        total += k
        print(f"{name}: {k}개 값 전달 추가")
    print(f"\n합계 {total}개")
    return 0


if __name__ == "__main__":
    sys.exit(main())
