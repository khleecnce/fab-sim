#!/usr/bin/env python3
"""학습 진도 대시보드 + 완주 예측 + 게이트 판정.

크론이 매 실행 첫 단계로 부른다:
  python3 tools/progress.py              # 요약 (다음 학습 대상 1명 포함)
  python3 tools/progress.py --next       # 다음 학습 대상 id만 출력 (크론이 파싱)
  python3 tools/progress.py --gates      # 게이트 충족 여부만
  python3 tools/progress.py --full       # 28명 전체 표
"""
import argparse
import json
import re
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AGENTS = ROOT / "agents"
ORG = AGENTS / "ORG.md"
STATE = ROOT / "agents" / ".progress.json"

# 별칭: ORG.md 트리 이름 → 실제 디렉토리
ALIAS = {"cmp-integrator": "process-integrator"}

# 게이트 정의 (ORG.md §4의 기계 판독본). 조건은 함수로 평가한다.
GATES = {
    "G1": {
        "opens": ["wafer-metrology", "surface-contamination", "wafer-type",
                  "film-oxide", "film-cu"],
        "need": "활성 5명 전원 Lv2 이상 (=각 3/6 이상)",
        "test": lambda p: all(p[a]["done"] >= 3 for a in p if p[a]["state"] == "활성"),
    },
    "G2": {
        "opens": ["slurry-abrasive", "slurry-chemistry", "pad-material",
                  "film-w", "tool-platen-head", "cmp-data-engineer"],
        "need": "1세대 5명 전원 6/6 + G1 개방자 전원 Lv1 이상(1/6)",
        "test": lambda p: all(p[a]["done"] >= 6 for a in GEN1 if a in p)
        and all(p[a]["done"] >= 1 for a in GATES["G1"]["opens"] if a in p),
    },
    "G3": {
        "opens": ["slurry-colloid", "pad-structure", "pad-lifecycle",
                  "disk-design", "film-nitride", "film-poly-si",
                  "tool-endpoint", "defect-scientist"],
        "need": "MILESTONES M2 달성 + G2 개방자 전원 Lv2 이상(3/6)",
        "test": lambda p: milestone_done("M2")
        and all(p[a]["done"] >= 3 for a in GATES["G2"]["opens"] if a in p),
    },
    "G4": {
        "opens": ["disk-kinematics", "film-emerging", "tool-post-clean",
                  "cmp-calibrator"],
        "need": "MILESTONES M3(결합 모델 v1 + 캘리브레이션 골격) 달성",
        "test": lambda p: milestone_done("M3"),
    },
    "G5": {
        "opens": ["etch-integrator", "depo-integrator", "litho-integrator",
                  "diffusion-integrator", "metrology-integrator"],
        "need": "MILESTONES M6(데모·백서) 달성 — Phase 2 타공정 진입",
        "test": lambda p: milestone_done("M6"),
    },
}
GEN1 = ["process-integrator", "pad-mechanic", "disk-conditioner",
        "slurry-chemist", "tribologist"]
PREREQ_F = AGENTS / "PREREQ.json"
ALIAS_REV = {"cmp-integrator": "process-integrator"}

MAX_ACTIVE = 12   # ORG.md: 동시 활성 상한


def load_prereq() -> dict:
    if not PREREQ_F.exists():
        return {}
    raw = json.loads(PREREQ_F.read_text())
    return {k: v for k, v in raw.items() if not k.startswith("_")}


def prereq_status(aid: str, p: dict, pre: dict) -> tuple:
    """(충족여부, 미충족 목록[(선수, 필요, 현재)])"""
    spec = pre.get(aid, {}).get("prereq", [])
    miss = []
    for dep, need in spec:
        dep = ALIAS_REV.get(dep, dep)
        have = p.get(dep, {}).get("done", 0)
        if have < need:
            miss.append((dep, need, have))
    return (not miss, miss)


def check_dag(pre: dict) -> list:
    """순환 의존 검출. 있으면 설계 오류다."""
    graph = {k: [ALIAS_REV.get(d, d) for d, _ in v.get("prereq", [])]
             for k, v in pre.items()}
    seen, stack, bad = set(), set(), []

    def walk(n, path):
        if n in stack:
            bad.append(" → ".join(path + [n]))
            return
        if n in seen:
            return
        seen.add(n)
        stack.add(n)
        for m in graph.get(n, []):
            walk(m, path + [n])
        stack.discard(n)

    for n in graph:
        walk(n, [])
    return bad


def milestone_done(mid: str) -> bool:
    f = ROOT / "MILESTONES.md"
    if not f.exists():
        return False
    for line in f.read_text().splitlines():
        if re.match(rf"^\|\s*{mid}\s*\|", line) and "✅" in line:
            return True
    return False


def org_states() -> dict:
    if not ORG.exists():
        return {}
    m = re.search(r"## 2\. 조직도(.*?)## 3\.", ORG.read_text(), re.S)
    block = m.group(1) if m else ORG.read_text()
    out = {}
    for line in block.splitlines():
        s = re.search(r"\[(활성|대기|자리|미활성)", line)
        if not s:
            continue
        ids = [i for i in re.findall(r"\b([a-z][a-z0-9]*(?:-[a-z0-9]+)*)\b",
                                     line.split("[")[0])
               if len(i) > 3 and i != "cmp"]
        if ids:
            out[ALIAS.get(ids[0], ids[0])] = s.group(1)
    return out


def scan() -> dict:
    states = org_states()
    p = {}
    for d in sorted(AGENTS.iterdir()):
        if not d.is_dir() or not (d / "PROFILE.md").exists():
            continue
        c = d / "CURRICULUM.md"
        units = re.findall(r"^- \[( |x)\] (Lv\d-\d|Cal-\d) (.+)$",
                           c.read_text(), re.M) if c.exists() else []
        core = [u for u in units if not u[1].startswith("Cal")]
        cal = [u for u in units if u[1].startswith("Cal")]
        nxt = next((f"{u[1]} {u[2][:44]}" for u in core if u[0] == " "), "")
        p[d.name] = {
            "state": states.get(d.name, "대기"),
            "done": sum(1 for u in core if u[0] == "x"),
            "total": len(core) or 6,
            "cal_done": sum(1 for u in cal if u[0] == "x"),
            "cal_total": len(cal),
            "next": nxt,
        }
    return p


def gates(p: dict) -> list:
    opened = {a for a in p if p[a]["state"] == "활성"}
    pre = load_prereq()
    out = []
    for gid, g in GATES.items():
        present = [a for a in g["opens"] if a in p]
        # 디렉토리조차 없는 게이트(Phase 2 자리)는 "개방됨"이 아니라 "미생성"
        already = bool(present) and all(a in opened for a in present)
        try:
            ok = g["test"](p)
        except Exception:
            ok = False
        # 게이트 숫자 조건을 넘어도, 선수과목 미충족자는 열 수 없다
        # ⚠ 이미 [활성]인 에이전트는 "열 것" 목록에 넣지 않는다 — 넣으면 총괄 크론이
        #   매 회차 같은 이름을 "지금 열 것"으로 받아 개방 작업을 반복한다(2026-09-14 실측:
        #   disk-kinematics(09-07 개방)·tool-post-clean(09-13 개방)이 계속 재출력됐다).
        eligible, blocked = [], []
        for a in present:
            if a in opened:
                continue
            fine, miss = prereq_status(a, p, pre)
            (eligible if fine else blocked).append(
                a if fine else (a, miss))
        out.append({"id": gid, "opened": already, "ready": ok,
                    "need": g["need"], "opens": present,
                    "eligible": eligible, "blocked": blocked})
    return out


def pick_next(p: dict) -> str:
    """활성 + 선수과목 충족 + 미완 중 진도 최저. 동률이면 GEN1 우선."""
    pre = load_prereq()
    cand = []
    for a, v in p.items():
        if v["state"] != "활성" or v["done"] >= v["total"]:
            continue
        if not prereq_status(a, p, pre)[0]:
            continue
        cand.append((v["done"], GEN1.index(a) if a in GEN1 else 99, a))
    return sorted(cand)[0][2] if cand else ""


def velocity() -> float:
    """최근 14일 커밋 로그에서 '단원 이수' 속도(단원/일)를 추정."""
    try:
        log = subprocess.run(
            ["git", "log", "--since=14 days ago", "--pretty=%s"],
            cwd=ROOT, capture_output=True, text=True, timeout=10).stdout
    except Exception:
        return 0.0
    n = len(re.findall(r"Lv\d-\d|Cal-\d", log))
    return n / 14 if n else 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--next", action="store_true")
    ap.add_argument("--gates", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    p = scan()

    if a.next:
        print(pick_next(p))
        return
    if a.json:
        print(json.dumps({"agents": p, "gates": gates(p),
                          "next": pick_next(p)}, ensure_ascii=False))
        return

    act = {k: v for k, v in p.items() if v["state"] == "활성"}
    done_u = sum(v["done"] for v in p.values())
    tot_u = sum(v["total"] for v in p.values())
    v = velocity()

    print(f"■ 학습 진도 — {date.today()}")
    print(f"  에이전트 {len(p)}명 (활성 {len(act)} / 대기 {len(p)-len(act)}) · "
          f"상한 {MAX_ACTIVE}")
    print(f"  단원 {done_u}/{tot_u} ({done_u/tot_u*100:.1f}%) · "
          f"최근 14일 속도 {v:.2f} 단원/일")
    if v > 0:
        eta = date.today() + timedelta(days=(tot_u - done_u) / v)
        print(f"  전원 완주 예상: {eta}  (현재 속도 유지 시)")
    else:
        print("  전원 완주 예상: 산출 불가 (최근 14일 이수 기록 없음)")

    print("\n■ 활성 에이전트")
    for k, x in sorted(act.items(), key=lambda i: i[1]["done"]):
        bar = "█" * x["done"] + "·" * (x["total"] - x["done"])
        cal = f" Cal {x['cal_done']}/{x['cal_total']}" if x["cal_total"] else ""
        print(f"  {k:<22} {bar} {x['done']}/{x['total']}{cal}"
              + (f"  → {x['next']}" if x["next"] else "  ✓ 완주"))

    if a.full:
        print("\n■ 대기 에이전트")
        for k, x in sorted(p.items()):
            if x["state"] != "활성":
                print(f"  {k:<22} {x['done']}/{x['total']}  [{x['state']}]")

    print("\n■ 게이트")
    for g in gates(p):
        mark = "✅ 개방됨" if g["opened"] else ("🟢 개방 조건 충족 — 지금 열어라"
                                             if g["ready"] else "⬜ 대기")
        if not g["opens"]:
            mark = "⬛ 미생성 (Phase 2 자리 — 디렉토리 없음)"
        print(f"  {g['id']} {mark}")
        print(f"     조건: {g['need']}")
        if not g["opened"] and g["opens"]:
            if g["eligible"]:
                print(f"     ✔ 선수충족 → 지금 열 것({len(g['eligible'])}): "
                      f"{', '.join(g['eligible'])}")
            for a, miss in g["blocked"]:
                m = ", ".join(f"{d} {h}/{n}" for d, n, h in miss)
                print(f"     ⏸ {a} — 선수 미충족: {m}")

    cyc = check_dag(load_prereq())
    if cyc:
        print("\n⚠ 선수관계 순환 감지 (설계 오류 — 즉시 수정):")
        for c in cyc:
            print(f"   {c}")

    nx = pick_next(p)
    print(f"\n▶ 이번 회차 학습 대상: {nx or '(선수 충족 + 미완인 활성자 없음 — 게이트 확인)'}")
    if nx:
        print(f"   다음 단원: {p[nx]['next']}")


if __name__ == "__main__":
    main()
