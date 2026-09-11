#!/usr/bin/env python3
"""UX 자가 감사 — 사용자가 지적하기 전에 기계가 먼저 찾는다.

왜 만들었나 (2026-09-11 사용자 지시):
  "이런 부분 너 스스로 개선하고 고쳐서 시뮬레이터까지 수정하고 나한테 보고할수는
   없어? 루프돌리듯이 최선의 결과 완성을 향해서."

배경: 크론 7개가 물리·문헌·정확도를 돌리는데, **UI/제품 품질을 보는 눈은 하나도
없었다.** 그래서 2026-09-11 하루에만 결함 6건이 전부 사용자 입에서 나왔다:
  ① 내부 팩 ID(`sic_ceria_h2o2`)를 선택 목록에 그대로 노출
  ② 패널·P&ID는 만들고 3D 씬에 실물 유닛이 없음 (SDS)
  ③ 캐시 헤더 부재 → 폰이 며칠 전 HTML을 계속 렌더 ("구현이 안 돼있다")
  ④ 캔버스 width 고정 → 폰에서 9px 글자가 5px로 축소
  ⑤ 엔진 연결 1개뿐인 축을 독립 탭으로 분리 (누를 이유 없는 화면)
  ⑥ 감독 포트에 수동 서버 기동 → 알림 40초마다 폭주

여섯 건 모두 **기계로 검출 가능한 클래스**다. 여기 규칙으로 박아 재발을 막는다.

한계를 정직히: 이 감사기는 "아름다운가"를 판정하지 못한다. 판정하는 것은
'정직성 위반'과 '과거에 실제로 터진 결함 패턴'뿐이다. 심미·정보구조는 여전히
렌더 스크린샷 + 사람(또는 vision) 판단이 필요하다.

출력: 사람이 읽는 표(기본) / `--json` / `--backlog`(수정 대상 파일에 기록)
종료코드: 심각(error) 1건 이상이면 1 — CI·크론 게이트로 쓸 수 있다.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parent.parent
WEB = ROOT / "sim" / "web" / "studio3d.html"
API = ROOT / "sim" / "api.py"
BACKLOG = ROOT / "UX-BACKLOG.md"

SEV_ORDER = {"error": 0, "warn": 1, "info": 2}


@dataclass
class Finding:
    rule: str
    severity: str          # error | warn | info
    title: str
    detail: str
    fix: str               # 무엇을 하면 닫히는가 — 크론이 이걸 읽고 고친다
    where: str = ""
    evidence: List[str] = field(default_factory=list)


def _html() -> str:
    return WEB.read_text() if WEB.exists() else ""


def _js_block(html: str) -> str:
    """가장 큰 <script> 블록 = 앱 코드."""
    blocks = re.findall(r"<script[^>]*>(.*?)</script>", html, re.S)
    return max(blocks, key=len) if blocks else ""


# ── R1. 내부 식별자 노출 ────────────────────────────────────────────
def r_internal_ids(html: str, js: str) -> List[Finding]:
    """팩 id·엔진 키를 사용자에게 그대로 보여주지 않는다.

    사용자 정정 원문: "sic_ceria_h2o2 이러면 보기도안좋고 너무 국부적이야",
    "무슨 소린지 모르겠어"(팩 이름으로 설명했을 때).
    """
    out: List[Finding] = []
    pack_ids = sorted(p.stem for p in (ROOT / "knowledge" / "params").glob("*.yaml"))
    # 표시 문자열 안에 팩 id가 박혀 있는가 (option 텍스트·배지·힌트)
    for pid in pack_ids:
        if pid == "base":
            continue
        # `>...sic_ceria_h2o2...<` 형태로 화면에 찍히는 경우
        for m in re.finditer(r">([^<>{}]*\b" + re.escape(pid) + r"\b[^<>{}]*)<", html):
            frag = m.group(1).strip()
            if "pack id" in frag.lower():        # 추적용으로 작게 남긴 것은 허용
                continue
            out.append(Finding(
                "R1-internal-id", "error",
                "내부 팩 ID가 화면에 노출됨",
                f"표시 문자열에 `{pid}` 가 그대로 들어 있습니다: {frag[:80]!r}",
                "sim/pack_meta.py 의 label/short 를 쓰도록 바꾸십시오.",
                where="sim/web/studio3d.html",
            ))
    return out


# ── R2. 패널만 있고 3D 실물이 없는 파트 ─────────────────────────────
def r_panel_without_geometry(js: str) -> List[Finding]:
    """탭(PARTS)이 있으면 3D 씬에 클릭 가능한 실물이 있어야 한다.

    2026-09-11: ② Slurry Delivery 탭과 P&ID는 만들었는데 씬에는 노즐뿐이었다.
    사용자에겐 "3D모델로 공급장치가 없다고"로 돌아왔다.
    """
    out: List[Finding] = []
    parts = re.findall(r"^  (\w+):\s*\{\s*name:", js, re.M)
    hot = set(re.findall(r"hot\.(\w+)\s*=", js))
    station_part = set(re.findall(r'STATION_PART\s*=\s*\{([^}]*)\}', js))
    mapped = set()
    for blob in station_part:
        mapped |= set(re.findall(r'["\']?\w+["\']?\s*:\s*["\'](\w+)["\']', blob))
    # data 탭은 3D 대응물이 없는 게 정상
    exempt = {"data"}
    for p in parts:
        if p in exempt:
            continue
        if p not in hot and p not in mapped:
            out.append(Finding(
                "R2-no-geometry", "error",
                f"파트 '{p}' 에 대응하는 3D 실물이 없음",
                f"PARTS 에 '{p}' 탭이 있지만 hot.{p} 도 STATION_PART 매핑도 없습니다. "
                "패널은 장비를 설명할 뿐이고, 씬은 장비를 보여줘야 합니다.",
                f"씬에 '{p}' 지오메트리를 만들고 hot.{p} 또는 proxy()+STATION_PART 로 연결하십시오.",
                where="sim/web/studio3d.html",
            ))
    return out


# ── R3. 캐시 헤더 ───────────────────────────────────────────────────
def r_cache_headers() -> List[Finding]:
    """개발 중 바뀌는 HTML 라우트는 no-store + 빌드 식별자를 띄운다.

    2026-09-11: 캐시 헤더가 없어 폰이 구버전을 계속 렌더 → "구현이 안 돼있다".
    서버 파일에는 멀쩡히 있었다.
    """
    out: List[Finding] = []
    if not API.exists():
        return out
    src = API.read_text()
    m = re.search(r'@app\.get\("/3d".*?(?=\n@app\.|\Z)', src, re.S)
    if not m:
        return out
    body = m.group(0)
    if "no-store" not in body:
        out.append(Finding(
            "R3-cache", "error", "/3d 에 캐시 금지 헤더가 없음",
            "폰 브라우저가 이전 사본을 계속 렌더할 수 있습니다.",
            "HTMLResponse(headers={'Cache-Control':'no-store, ...'}) 를 붙이십시오.",
            where="sim/api.py",
        ))
    if "data-build" not in body:
        out.append(Finding(
            "R3-buildtag", "warn", "화면에 빌드 식별자를 주입하지 않음",
            "'지금 보는 게 최신인가'를 사용자와 말다툼 없이 판별할 방법이 없습니다.",
            "파일 mtime 을 data-build 로 주입해 화면에 띄우십시오.",
            where="sim/api.py",
        ))
    return out


# ── R4. 캔버스 반응형 ───────────────────────────────────────────────
def r_canvas_responsive(html: str, js: str) -> List[Finding]:
    """캔버스를 고정 width 로 만들고 CSS 로 늘리면 폰에서 글자가 못 읽힌다."""
    out: List[Finding] = []
    for m in re.finditer(r'<canvas id="(cv-[\w-]+)"([^>]*)>', html):
        cid, attrs = m.group(1), m.group(2)
        if re.search(r'\bwidth="\d+"', attrs):
            out.append(Finding(
                "R4-canvas-fixed", "error",
                f"캔버스 {cid} 가 고정 폭",
                "폰(342px)에서 축소돼 9px 글자가 5px이 됩니다.",
                "width 속성을 빼고 data-h 만 두어 JS(cv())가 clientWidth+DPR 로 잡게 하십시오.",
                where="sim/web/studio3d.html",
            ))
    if "cv-" in html and "devicePixelRatio" not in js:
        out.append(Finding(
            "R4-no-dpr", "warn", "캔버스가 DPR 을 반영하지 않음",
            "레티나 화면에서 뿌옇게 보입니다.",
            "setTransform(dpr,0,0,dpr,0,0) 으로 비트맵만 확대하십시오.",
            where="sim/web/studio3d.html",
        ))
    # 회전/리사이즈 재렌더
    if "drawViz" in js:
        rs = re.search(r"function resize\(\)\s*\{(.*?)\n\}", js, re.S)
        if rs and "drawViz" not in rs.group(1):
            out.append(Finding(
                "R4-no-redraw", "warn", "resize 시 캔버스를 다시 그리지 않음",
                "화면 회전 후 폭이 어긋난 그림이 남습니다.",
                "resize() 안에서 drawViz() 를 호출하십시오.",
                where="sim/web/studio3d.html",
            ))
    return out


# ── R5. 탭 존재 이유 (엔진 연결 필드 수) ────────────────────────────
def r_tab_worth_existing(js: str) -> List[Finding]:
    """필드가 거의 전부 기록 전용인 탭은 존재 이유가 없다.

    사용자 정정: "슬러리 공급은 어차피 수정할거 없으니까 … 한번에 나올수있게해"
    """
    out: List[Finding] = []
    for m in re.finditer(r'^  (\w+):\s*\{\s*name:"([^"]+)"(.*?)\n  \]\},', js, re.S | re.M):
        pid, name, body = m.group(1), m.group(2), m.group(3)
        if pid == "data":
            continue
        wired = len(re.findall(r'pk:"', body))
        dead = len(re.findall(r"pk:null", body))
        viz = len(re.findall(r"special:", body))
        if wired <= 1 and dead >= 4 and viz <= 1:
            out.append(Finding(
                "R5-thin-tab", "warn",
                f"탭 '{name}' 은 엔진 연결이 {wired}개뿐",
                f"기록 전용 {dead}개 / 연결 {wired}개. 사용자가 누를 뿐 볼 것이 없는 화면입니다.",
                "인접 탭의 섹션으로 합치십시오. 나중에 연결이 늘면 그때 분리하면 됩니다.",
                where="sim/web/studio3d.html",
            ))
    return out


# ── R6. 새 어셈블리에 경계 테스트가 있는가 ──────────────────────────
def r_assembly_tested(js: str) -> List[Finding]:
    """씬에 등록된 스테이션은 렌더 검증 테스트로 잠겨 있어야 한다."""
    out: List[Finding] = []
    stations = set(re.findall(r'^\s*(\w+):\{label:"', js, re.M))
    tools_dir = ROOT / "tools"
    tested = ""
    for f in tools_dir.glob("test_*3d*.py"):
        tested += f.read_text()
    for st in sorted(stations):
        if st in {"TOOL"}:
            continue
        if f"'{st}'" not in tested and f'"{st}"' not in tested:
            out.append(Finding(
                "R6-untested-assembly", "info",
                f"스테이션 {st} 에 렌더 검증 테스트가 없음",
                "코드 존재는 증거가 아닙니다 — 첫 렌더에서 부품이 바닥에 깔리거나 "
                "케이스 밖으로 새는 사고가 실제로 있었습니다.",
                "tools/test_sds_3d.py 형태로 프록시·내부 메시 수·높이 이탈 0 을 잠그십시오.",
                where="tools/",
            ))
    return out


# ── R7. dead 배지 정직성 ────────────────────────────────────────────
def r_dead_honesty(js: str) -> List[Finding]:
    """pk:null 인데 dead/weak 설명이 없으면 '연결된 척'하는 거짓 UI."""
    out: List[Finding] = []
    for m in re.finditer(r"\{k:\"(\w+)\"[^}]*?pk:null[^}]*?\}", js, re.S):
        blob = m.group(0)
        key = m.group(1)
        if "dead:" not in blob and "weak:" not in blob and "hint:" not in blob:
            out.append(Finding(
                "R7-silent-dead", "error",
                f"'{key}' 는 엔진 미연결인데 아무 표시가 없음",
                "사용자는 값을 바꿔도 결과가 안 변하는 이유를 알 수 없습니다.",
                "dead:\"왜 연결 안 됐는지\" 를 추가하십시오.",
                where="sim/web/studio3d.html",
            ))
    return out


# ── R8. 상시 서비스 안전장치 ────────────────────────────────────────
def r_service_guard() -> List[Finding]:
    """감독 서비스 4종 안전장치 — 알림 폭주가 실제로 발생했다."""
    out: List[Finding] = []
    sf = ROOT / "tools" / "serve_forever.sh"
    if not sf.exists():
        return out
    src = sf.read_text()
    checks = [
        ("포트 소유자 판정", "PORT_OWNER", "기동 전 lsof 로 포트 주인을 확인하고 헬스체크 통과 시 얹히십시오."),
        ("본체 실패 시 터널 금지", "no tunnel", "API 가 못 뜨면 터널·알림을 만들지 마십시오."),
        ("알림 시간당 상한", "rate limit", "notify() 에 시간당 상한을 거십시오."),
        ("이상 감지 후 대기", "restarting in", "즉시 exit 하면 launchd 가 곧바로 재기동해 폭주합니다."),
    ]
    for label, needle, fix in checks:
        if needle not in src:
            out.append(Finding(
                "R8-service-guard", "error", f"상시 서비스에 '{label}' 안전장치 없음",
                "2026-09-11 포트 충돌로 40초마다 새 주소가 텔레그램 발송된 사고가 있었습니다.",
                fix, where="tools/serve_forever.sh",
            ))
    return out


# ── R9. 표시 메타 커버리지 ──────────────────────────────────────────
def r_pack_meta_coverage() -> List[Finding]:
    """새 팩이 추가되면 표시 메타도 같이 있어야 한다."""
    out: List[Finding] = []
    try:
        sys.path.insert(0, str(ROOT))
        from sim.pack_meta import PACK_META, NON_SLURRY  # type: ignore
    except Exception as e:
        return [Finding("R9-import", "warn", "pack_meta 를 읽지 못함", str(e), "임포트 오류를 고치십시오.")]
    for p in (ROOT / "knowledge" / "params").glob("*.yaml"):
        pid = p.stem
        if pid in NON_SLURRY or pid in PACK_META:
            continue
        out.append(Finding(
            "R9-meta-missing", "error",
            f"팩 '{pid}' 에 표시 메타가 없음",
            "선택 목록에 내부 ID 가 그대로 뜹니다.",
            "sim/pack_meta.py 의 PACK_META 에 family/label/short/film/film_label/mechanism/chem/note 를 추가하십시오.",
            where="sim/pack_meta.py",
        ))
    return out


RULES = [
    ("R1", lambda h, j: r_internal_ids(h, j)),
    ("R2", lambda h, j: r_panel_without_geometry(j)),
    ("R3", lambda h, j: r_cache_headers()),
    ("R4", lambda h, j: r_canvas_responsive(h, j)),
    ("R5", lambda h, j: r_tab_worth_existing(j)),
    ("R6", lambda h, j: r_assembly_tested(j)),
    ("R7", lambda h, j: r_dead_honesty(j)),
    ("R8", lambda h, j: r_service_guard()),
    ("R9", lambda h, j: r_pack_meta_coverage()),
]


def audit() -> List[Finding]:
    html = _html()
    js = _js_block(html)
    found: List[Finding] = []
    for _, fn in RULES:
        try:
            found += fn(html, js)
        except Exception as e:                      # 규칙 하나가 죽어도 나머지는 돈다
            found.append(Finding("AUDIT-ERROR", "warn", "감사 규칙 실행 실패", repr(e), "규칙 코드를 고치십시오."))
    found.sort(key=lambda f: (SEV_ORDER.get(f.severity, 9), f.rule))
    return found


def write_backlog(found: List[Finding]) -> None:
    lines = [
        "# UX 백로그 — 기계 감사 결과",
        "",
        "`tools/ux_audit.py` 가 자동 생성합니다. **손으로 고치지 마십시오** — 다음 실행에 덮어씁니다.",
        "고칠 것은 이 파일이 아니라 `where` 에 적힌 소스입니다.",
        "",
        f"발견 {len(found)}건 "
        f"(심각 {sum(1 for f in found if f.severity=='error')} · "
        f"경고 {sum(1 for f in found if f.severity=='warn')} · "
        f"정보 {sum(1 for f in found if f.severity=='info')})",
        "",
    ]
    if not found:
        lines.append("현재 위반 없음. 새 결함 클래스가 생기면 규칙을 추가하십시오.")
    for f in found:
        mark = {"error": "🔴", "warn": "🟡", "info": "⚪"}[f.severity]
        lines += [
            f"## {mark} [{f.rule}] {f.title}",
            f"- **위치**: `{f.where}`",
            f"- **내용**: {f.detail}",
            f"- **조치**: {f.fix}",
            "",
        ]
    BACKLOG.write_text("\n".join(lines))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--backlog", action="store_true", help="UX-BACKLOG.md 갱신")
    ap.add_argument("--top", type=int, default=0, help="가장 심각한 N건만 출력 (크론 배차용)")
    a = ap.parse_args()

    found = audit()
    if a.top:
        found = found[: a.top]

    if a.json:
        print(json.dumps([asdict(f) for f in found], ensure_ascii=False, indent=2))
    else:
        if not found:
            print("✅ UX 감사 위반 없음")
        for f in found:
            mark = {"error": "🔴", "warn": "🟡", "info": "⚪"}[f.severity]
            print(f"{mark} [{f.rule}] {f.title}")
            print(f"     위치: {f.where}")
            print(f"     내용: {f.detail}")
            print(f"     조치: {f.fix}")
        n_err = sum(1 for f in found if f.severity == "error")
        print(f"\n총 {len(found)}건 (심각 {n_err})")

    if a.backlog:
        write_backlog(audit())
        print(f"\n→ {BACKLOG.relative_to(ROOT)} 갱신")

    return 1 if any(f.severity == "error" for f in found) else 0


if __name__ == "__main__":
    sys.exit(main())
