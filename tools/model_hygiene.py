#!/usr/bin/env python3
"""모델식 위생 검사 — 차원 · 극한 · 식별 가능성.

위치: 이 도구는 "어떤 슬러리든 넣으면 모델식이 나오는 절차"의 검증 장치다.
      특정 물질·특정 팩을 알지 못하며, 알아서도 안 된다.

    입력        판단 기준(물질명 없음)                    출력
    ─────────  ────────────────────────────────────   ──────────────
 D  단위 있는   키가 선언한 차원 == 단위의 차원           불일치 목록
    모든 수치
 L  MRR 결합    드라이버의 **극한 역할 선언**과            위반 + 미선언
    팩터의       실제 극한 거동의 일치
    모든 드라이버  (AGENT→0, MODULATOR→유한 양수)
 I  곱해지는     두 팩터가 같은 드라이버를 공유하지 않음    교락 목록
    팩터 집합

왜 이렇게 짰나 (2026-09-11 사용자 지적):
  첫 구현은 팩 하나("oxide_silica")와 드라이버 4개를 코드에 박았다. 그러면
  새 화학계가 들어올 때 검사기가 **아는 것만** 보고 침묵한다 — 절차가 아니라
  사례다. 지금은 팩을 전수 순회하고, 드라이버는 팩터가 신고한 것을 전부 돌며,
  극한의 옳고 그름은 검사기가 추측하지 않고 `factors.LIMIT_ROLE` 선언을 읽는다.
  **미선언은 통과가 아니라 결함이다** — 선언 없이는 옳은지 말할 수 없다.

무엇을 검사하지 못하나 (정직히):
  "이 수식이 옳은가"는 판정하지 못한다. 판정하는 것은 **명백히 틀린 것**뿐이다 —
  차원 불일치, 비물리적 극한, 구조적 이중 계상. 모델의 타당성은 문헌 대조
  (verify_claims.py)와 held-out 백테스트(qa_loop.py)의 몫이다.

실행:
    tools/model_hygiene.py              # 전 팩
    tools/model_hygiene.py --pack X     # 팩 하나만 (빠름)
    tools/model_hygiene.py --json
종료코드: 심각(error) 1건 이상이면 1
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parent.parent
PY = str(ROOT / ".venv" / "bin" / "python")
PACKS = ROOT / "knowledge" / "params"

sys.path.insert(0, str(ROOT))


@dataclass
class Issue:
    check: str            # D | L | I
    severity: str         # error | warn | info
    title: str
    detail: str
    fix: str = ""


# ══════════════════════════════════════════════════════════════════════
# [D] 차원 정합성
# 판단 기준: 키 접미사가 선언하는 차원과 unit 문자열의 차원이 같은가.
# 물질명이 아니라 **차원 기호**만 본다.
# ══════════════════════════════════════════════════════════════════════
SUFFIX_UNITS: Dict[str, List[str]] = {
    "_nm": ["nm"],
    "_um": ["µm", "um", "μm"],
    "_mm": ["mm"],
    "_m": ["m"],
    "_s": ["s", "sec"],
    "_pct": ["%", "wt%", "vol%", "pct"],
    "_wt_pct": ["wt%", "%"],
    "_vol_pct": ["vol%", "%"],
    "_psi": ["psi"],
    "_pa": ["Pa"],
    "_pa_s": ["Pa·s", "Pa*s", "Pa s", "Pa.s"],
    "_rpm": ["rpm"],
    "_cpm": ["cpm", "cycles/min"],
    "_lbf": ["lbf"],
    "_ml_min": ["mL/min", "ml/min"],
    "_per_m2": ["1/m²", "1/m^2", "m^-2", "m⁻²", "/m²", "/m^2"],
    "_density_m2": ["1/m²", "1/m^2", "m^-2", "m⁻²"],   # 면'밀도' = 역수 면적
    "_m2": ["m²", "m^2"],
    "_m_per_pa": ["m^2/N", "m²/N", "m/Pa"],            # Preston: m/Pa ≡ m²/N
    "_mm_per_hour": ["mm/h", "mm/hr"],
    "_hours": ["h", "hr", "hours"],
    "_c": ["°C", "C", "degC"],
    "_k": ["K"],
    "_mM": ["mM", "mmol/L"],
}

# 본래 무차원인 키 (지수·비율·분율·로그량)
DIMLESS_SUFFIX = ("_exponent", "_ratio", "_fraction", "_factor", "_index",
                  "_per_unit", "_coefficient", "_curve_n", "_strength_k",
                  "_ph", "_ph_ref", "_softening_ref")


def _norm(u: Optional[str]) -> str:
    return (u or "").strip().replace(" ", "")


def _exception_documented(pack_file: Path, key: str) -> bool:
    """키-단위 불일치의 예외는 **팩 YAML의 note 에 근거가 적혀 있을 때만** 인정한다.

    검사기 안에 예외 목록을 두면(첫 구현이 그랬다) 예외를 늘리는 것으로 검사를
    무력화할 수 있고, 그 목록 자체가 특정 팩:키를 아는 사례가 된다.
    근거를 데이터 쪽에 두면 어느 화학계든 같은 규칙이 적용된다.
    """
    if not pack_file.exists():
        return False
    t = pack_file.read_text()
    m = re.search(rf"^  {re.escape(key)}:\n((?:    .*\n|\s*\n)+)", t, re.M)
    if not m:
        return False
    block = m.group(1)
    # note/ note: > 블록 안에 '환산'과 '단위'가 함께 언급되면 의도된 표기로 본다
    return ("note" in block and "환산" in block) or "단위 불일치" in block


def check_dimensions() -> List[Issue]:
    from sim.params import available_packs, load_pack
    out: List[Issue] = []
    for name in available_packs():
        try:
            pk = load_pack(name)
        except Exception as e:
            out.append(Issue("D", "error", f"팩 {name} 로드 실패", repr(e)))
            continue
        pack_file = PACKS / f"{name}.yaml"
        for key, p in pk.params.items():
            if not isinstance(getattr(p, "value", None), (int, float)):
                continue                       # 식별자(문자열)는 단위 없음이 정상
            unit = _norm(getattr(p, "unit", None))

            if key.endswith(DIMLESS_SUFFIX):
                if unit and unit not in ("-", "1", "", "pH"):
                    out.append(Issue(
                        "D", "warn", f"{name}:{key} 는 무차원이어야 하는데 단위 '{unit}'",
                        "지수·비율·분율·로그량은 무차원입니다.",
                        "단위를 비우거나 '-' 로 두십시오."))
                continue

            if not unit:
                out.append(Issue(
                    "D", "warn", f"{name}:{key} 에 단위가 없음",
                    f"값 {p.value} 이 무슨 단위인지 코드 밖에서 알 수 없습니다.",
                    "팩 YAML 에 unit 을 추가하십시오."))
                continue

            # 접미사는 **긴 것부터** — 짧은 것부터 보면 _pa_s 가 _s 에 먼저 걸린다
            for suf in sorted(SUFFIX_UNITS, key=len, reverse=True):
                if not key.endswith(suf):
                    continue
                if any(_norm(a) == unit for a in SUFFIX_UNITS[suf]):
                    break
                if _exception_documented(pack_file, key):
                    break                      # 근거가 데이터에 적혀 있으면 인정
                out.append(Issue(
                    "D", "error",
                    f"{name}:{key} 단위 불일치 — '{unit}' (키는 {suf} 를 뜻함)",
                    f"허용: {SUFFIX_UNITS[suf]}. 키 이름과 단위가 어긋나면 다른 "
                    "모듈이 환산 없이 그대로 써서 자릿수 오류가 납니다.",
                    "단위를 고치거나, 의도된 표기라면 팩 YAML note 에 왜 환산하지 "
                    "않는지 적으십시오."))
                break
    return out


# ══════════════════════════════════════════════════════════════════════
# [L] 극한 거동
# 판단 기준: 드라이버의 역할 선언(AGENT/MODULATOR)과 실제 거동의 일치.
# 검사기는 변수의 뜻을 **모른다** — factors.LIMIT_ROLE 이 말해준다.
# ══════════════════════════════════════════════════════════════════════
PROBE = r'''
import sys, warnings, json
warnings.filterwarnings("ignore")
sys.path.insert(0, "{root}")
from sim.engine import Recipe, simulate
rr = simulate(Recipe(pack="{pack}"))
m = 1.0
for k, f in rr.factors.items():
    if f.mrr_coupled and f.value is not None:
        m *= f.value
print(json.dumps({{"mult": m}}))
'''


def _run(pack_dir: Path, pack: str) -> Tuple[Optional[float], Optional[str]]:
    env = dict(os.environ)
    env["FABSIM_PACK_DIR"] = str(pack_dir)
    try:
        r = subprocess.run([PY, "-c", PROBE.format(root=ROOT, pack=pack)],
                           capture_output=True, text=True, env=env,
                           cwd=str(ROOT), timeout=180)
    except subprocess.TimeoutExpired:
        return None, "타임아웃"
    if r.returncode != 0:
        return None, (r.stderr.strip().splitlines() or ["?"])[-1][:90]
    try:
        return json.loads(r.stdout.strip().splitlines()[-1])["mult"], None
    except Exception as e:
        return None, f"파싱 실패: {e}"


def _write_value(pack_dir: Path, pack: str, key: str, val: float) -> bool:
    """그 팩이 **실제로 읽게 될** 선언을 찾아 값을 바꾼다.

    ⚠ 순서가 물리적으로 중요하다. 상속 체인 밖의 팩을 고치면 대상 팩의 값은
    그대로이고, 검사기는 "0 으로 바꿨는데 배수가 안 변했다"를 **모델 결함**으로
    오판한다. 실제로는 검사기가 엉뚱한 파일을 건드린 것이다.
    그러므로 자식 → 부모 순(lineage 역순)으로만 훑고, 체인 밖은 보지 않는다.
    """
    # 상속 체인을 실제 로더에게 물어본다 (파일명 추측 금지)
    chain: List[str] = []
    try:
        env = dict(os.environ)
        env["FABSIM_PACK_DIR"] = str(pack_dir)
        r = subprocess.run(
            [PY, "-c",
             f"import sys;sys.path.insert(0,{str(ROOT)!r});"
             f"from sim.params import load_pack;"
             f"print(','.join(load_pack({pack!r}).lineage))"],
            capture_output=True, text=True, env=env, cwd=str(ROOT), timeout=60)
        if r.returncode == 0:
            chain = [s for s in r.stdout.strip().split(",") if s]
    except Exception:
        pass
    if not chain:
        chain = [pack]

    for name in reversed(chain):          # 자식이 부모를 덮으므로 자식부터
        cand = pack_dir / f"{name}.yaml"
        if not cand.exists():
            continue
        t = cand.read_text()
        pat = re.compile(rf"^(\s+{re.escape(key)}:\s*\n\s+value:\s*)([-\d.eE+]+)", re.M)
        if pat.search(t):
            cand.write_text(pat.sub(lambda m: f"{m.group(1)}{val!r}", t, count=1))
            return True
        pat2 = re.compile(rf"^(\s+{re.escape(key)}:\s+)([-\d.eE+]+)\s*$", re.M)
        if pat2.search(t):
            cand.write_text(pat2.sub(lambda m: f"{m.group(1)}{val!r}", t, count=1))
            return True
    return False


# 세기 변수(INTENSIVE)를 밀어볼 지점 — **정의역의 양 끝**이지 '0' 이 아니다.
#
# 고르는 기준(물질명 없이): 그 변수가 물리적으로 취할 수 있는 범위의 양 극단.
# 여기서 모델이 죽거나 비물리 값을 내면, 사용자가 슬라이더를 끝까지 밀었을 때
# 그대로 드러난다. 값 자체가 문헌 근거일 필요는 없다 — 이건 파라미터가 아니라
# **검사 지점**이고, 물어보는 것은 "그 조건에서 모델이 무너지는가"뿐이다.
_INTENSIVE_PROBES: Dict[str, List[float]] = {
    # 수용액에서 실질적으로 도달 가능한 양 끝
    "slurry_ph": [0.0, 14.0],
    # 폴리싱 패드 경도의 물리적 범위 (아주 무른 것 ~ 아주 단단한 것)
    "pad_hardness_shore_d": [1.0, 90.0],
    # 슬러리가 액상을 유지하는 범위
    "temperature_c": [0.0, 95.0],
}


def _ref_mismatch_hint(pack: str, pack_dir: Optional[Path] = None) -> str:
    """기준 조건 배수가 1이 아닐 때, 어긋난 본값/기준점 짝을 찾아 알려준다.

    판단 기준(물질명 없음): 이름이 `X` 와 `X_ref`(또는 `<접두>_ref_<나머지>`) 로
    짝을 이루는 수치 파라미터에서 두 값이 다르면 의심 대상이다.
    기준점은 "어느 조건에서 축척을 역산했는가"의 좌표이므로, 그 팩의 운전 조건과
    같아야 기준 배수가 1이 된다.

    ⚠ 추측을 단정으로 바꾸지 않는다 — 어긋남이 **정당한** 경우도 있으므로
    (의도적으로 다른 조건을 기준으로 삼은 설계) '의심 지점'으로만 말한다.
    """
    try:
        env = dict(os.environ)
        env["PYTHONWARNINGS"] = "ignore"
        env["FABSIM_PACK_DIR"] = str(pack_dir or PACKS)
        code = (
            f"import sys;sys.path.insert(0,{str(ROOT)!r});"
            "import json;from sim.params import load_pack;"
            f"pk=load_pack({pack!r});"
            "out=[]\n"
            "keys=list(pk.params)\n"
            "for k in keys:\n"
            "    if '_ref' not in k: continue\n"
            "    # 기준점 이름에서 _ref 를 떼면 본값 이름의 **일부**가 나온다.\n"
            "    # 접두사가 붙는 경우(예: 도메인 접두 + 축 이름)가 있으므로\n"
            "    # 완전 일치뿐 아니라 접미/접두 일치도 후보로 본다.\n"
            "    stem=k.replace('_ref_','_').replace('_ref','')\n"
            "    if not stem: continue\n"
            "    cands=[c for c in keys if c!=k and (c==stem or c.endswith('_'+stem) or stem.endswith('_'+c))]\n"
            "    # 가장 짧은(=가장 구체적으로 대응하는) 후보를 고른다\n"
            "    cands.sort(key=len)\n"
            "    for c in cands:\n"
            "        a,b=pk.get_or(c,None),pk.get_or(k,None)\n"
            "        try:\n"
            "            if a is not None and b is not None and float(a)!=float(b):\n"
            "                out.append((c,float(a),k,float(b),pk.has_own(k)))\n"
            "        except Exception: pass\n"
            "        break\n"
            "print(json.dumps(out))"
        )
        r = subprocess.run([PY, "-c", code], capture_output=True, text=True,
                           env=env, cwd=str(ROOT), timeout=60)
        if r.returncode != 0:
            return ""
        items = json.loads(r.stdout.strip().splitlines()[-1])
    except Exception:
        return ""
    if not items:
        return ""
    parts = []
    for base, a, ref, b, own in items[:3]:
        tag = "자기선언" if own else "**상속값**"
        parts.append(f"{base}={a:g} vs {ref}={b:g} ({tag})")
    return " · ".join(parts)


def check_limits(packs: List[str]) -> List[Issue]:
    import warnings
    warnings.filterwarnings("ignore")
    from sim.engine import Recipe, simulate
    from sim.factors import LIMIT_ROLE

    out: List[Issue] = []
    for pack in packs:
        # 기준 조건에서 배수 1.0 (Kp 이중 계상 방지 계약)
        d0 = Path(tempfile.mkdtemp(prefix="mh0_"))
        shutil.copytree(PACKS, d0 / "p")
        base, err = _run(d0 / "p", pack)
        shutil.rmtree(d0, ignore_errors=True)
        if base is None:
            out.append(Issue("L", "error", f"[{pack}] 기준 실행 실패", err or "?"))
            continue
        if abs(base - 1.0) > 1e-6:
            # 원인을 짚어 준다 — "배수가 1이 아니다"만으로는 어디를 볼지 모른다.
            # 이 위반은 거의 항상 **기준점이 본값과 어긋난** 것이고, 그 어긋남은
            # 두 경로로 생긴다: ① 본값을 바꾸며 _ref 를 안 옮겼다
            # ② 어떤 항을 **활성화**했는데 그 항이 쓰는 기준점이 상속값이다.
            # ②는 비활성 상태에서 증상이 없어 조용히 남는다.
            hint = _ref_mismatch_hint(pack)
            out.append(Issue(
                "L", "error", f"[{pack}] 기준 조건 MRR 배수가 1.0 이 아님 ({base:.6f})",
                "Kp 가 그 조건에서 역산된 값이므로 배수는 정확히 1.0 이어야 합니다."
                + (f"\n     의심 지점: {hint}" if hint else ""),
                "본값과 _ref 짝을 같은 편집에서 함께 옮기십시오. 항을 새로 "
                "활성화한 경우에도 그 항이 쓰는 기준점을 자기 팩에 선언해야 합니다."))

        # MRR 결합 팩터가 신고한 **모든** 드라이버를 순회한다
        try:
            rr = simulate(Recipe(pack=pack))
        except Exception as e:
            out.append(Issue("L", "error", f"[{pack}] simulate 실패", repr(e)))
            continue
        drivers: Dict[str, None] = {}
        for f in rr.factors.values():
            if f.mrr_coupled:
                for d in (f.drivers or {}):
                    drivers[d.split("(")[0]] = None    # 'x(note)' 형태 정리

        for key in sorted(drivers):
            role = LIMIT_ROLE.get(key)
            if role is None:
                out.append(Issue(
                    "L", "warn", f"[{pack}] 드라이버 '{key}' 의 극한 역할이 미선언",
                    "선언이 없으면 0 에서의 거동이 옳은지 판정할 수 없습니다. "
                    "미선언은 통과가 아닙니다.",
                    "sim/factors.py 의 LIMIT_ROLE 에 AGENT / MODULATOR / INTENSIVE "
                    "중 하나로 등록하십시오(어느 화학계에서도 성립하는 선언이어야 합니다)."))
                continue

            if role == "INTENSIVE":
                # 0 이 '없음'을 뜻하지 않는 세기 변수. "0 에서 어떻게 되는가"는
                # 물어볼 수 없는 질문이므로 0 극한을 적용하지 않는다. 대신 이런
                # 변수는 **유효 구간 밖에서 조용히 외삽되는 것**이 결함이다.
                #
                # 검사: 정의역 양 끝 근처로 밀었을 때 모델이 (a) 죽지 않고
                # (b) 음수·발산을 내지 않으며 (c) 유도 구간 밖임을 사용자에게
                # 알리는가. (c) 는 notes 에 경고가 실리는지로 본다 — 값이 조용히
                # 나오면 그 숫자가 어디서 왔는지 사용자가 알 길이 없다.
                probes = _INTENSIVE_PROBES.get(key)
                if not probes:
                    out.append(Issue(
                        "L", "warn",
                        f"[{pack}] 세기 변수 '{key}' 의 검사 구간이 없음",
                        "INTENSIVE 로 선언했으나 어느 범위를 밀어볼지 정의되지 "
                        "않아 외삽 검사를 건너뛰었습니다.",
                        "tools/model_hygiene.py 의 _INTENSIVE_PROBES 에 정의역 "
                        "양 끝 값을 등록하십시오."))
                    continue
                for probe in probes:
                    d = Path(tempfile.mkdtemp(prefix="mhi_"))
                    shutil.copytree(PACKS, d / "p")
                    if not _write_value(d / "p", pack, key, probe):
                        shutil.rmtree(d, ignore_errors=True)
                        continue
                    m, err = _run(d / "p", pack)
                    shutil.rmtree(d, ignore_errors=True)
                    if m is None:
                        out.append(Issue(
                            "L", "error", f"[{pack}] {key}={probe:g} 에서 예외",
                            err or "?",
                            "정의역 끝에서 죽지 않도록 방어하십시오."))
                    elif m != m or m in (float("inf"), float("-inf")) or m < 0:
                        out.append(Issue(
                            "L", "error",
                            f"[{pack}] {key}={probe:g} → MRR 배수 {m}",
                            "세기 변수를 정의역 끝으로 밀었을 때 비물리 값이 "
                            "나옵니다.", "항의 정의역과 clamp 를 확인하십시오."))
                continue

            d = Path(tempfile.mkdtemp(prefix="mh_"))
            shutil.copytree(PACKS, d / "p")
            ok = _write_value(d / "p", pack, key, 0.0)
            if not ok:
                shutil.rmtree(d, ignore_errors=True)
                out.append(Issue(
                    "L", "warn", f"[{pack}] 드라이버 '{key}' 를 극한값으로 바꾸지 못함",
                    "이 드라이버가 팩 YAML 의 예상 형식으로 선언돼 있지 않아 "
                    "극한 검사를 **수행하지 못했습니다**. 검사기가 조용히 건너뛰면 "
                    "'위반 없음'으로 잘못 읽힙니다.",
                    "팩에 이 키가 숫자 값으로 선언돼 있는지, 코드가 계산으로만 "
                    "만들어내는 값은 아닌지 확인하십시오."))
                continue
            m, err = _run(d / "p", pack)
            shutil.rmtree(d, ignore_errors=True)

            if m is None:
                out.append(Issue("L", "error", f"[{pack}] {key}=0 에서 예외", err or "?",
                                 "극한값에서 죽지 않도록 정의역을 방어하십시오."))
                continue
            if m != m or m in (float("inf"), float("-inf")):
                out.append(Issue("L", "error", f"[{pack}] {key}=0 → MRR 배수 {m}",
                                 "NaN/발산은 비물리입니다.", "항의 정의역을 확인하십시오."))
            elif m < 0:
                out.append(Issue("L", "error", f"[{pack}] {key}=0 → MRR 배수 음수 ({m:.4g})",
                                 "제거율은 음수가 될 수 없습니다.", "clamp 를 추가하십시오."))
            elif role == "AGENT" and m > 1e-9:
                out.append(Issue(
                    "L", "error",
                    f"[{pack}] {key}=0 인데 MRR 배수 {m:.4g} (AGENT 이므로 0 이어야)",
                    "제거를 수행하는 주체가 없는데 제거율이 남아 있습니다. 항이 아예 "
                    "만들어지지 않아 '효과 없음(=1.0)'으로 남았을 가능성이 큽니다.",
                    "0 케이스를 분기로 잡아 terms[...] = 0.0 으로 계상하십시오."))
            elif role == "MODULATOR" and m <= 0:
                out.append(Issue(
                    "L", "error",
                    f"[{pack}] {key}=0 인데 MRR 배수 {m:.4g} (MODULATOR 이므로 양수여야)",
                    "조절 변수가 0 이라고 메커니즘 전체가 멈추지는 않습니다.",
                    "역할 선언이 틀렸는지, 항의 형태가 틀렸는지 확인하십시오."))
    return out


# ══════════════════════════════════════════════════════════════════════
# [I] 식별 가능성 — 곱해지는 팩터끼리 드라이버를 공유하면 이중 계상
# ══════════════════════════════════════════════════════════════════════
# 팩터 정의 위반을 드러내는 탐침 — 드라이버를 기준점 **아래/위**로 민다.
# 특히 0(= 그 성분을 아예 빼는 조건)이 중요하다: 상대항의 기준점이 범위
# 중간에 있으면 0 에서 배수가 1을 크게 넘는다.
_RANGE_PROBE_DRIVERS = {
    "inhibitor_mM":     lambda x: [("zero", 0.0), ("hi", x * 10)],
    "surfactant_ppm":   lambda x: [("zero", 0.0), ("hi", x * 10)],
    "oxidizer_wt_pct":  lambda x: [("zero", 0.0), ("hi", x * 3)],
    "abrasive_wt_pct":  lambda x: [("lo", x * 0.1), ("hi", x * 5)],
    "shield_additive_wt_pct": lambda x: [("zero", 0.0), ("hi", x * 5)],
}


def check_factor_ranges(packs: List[str]) -> List[Issue]:
    """각 팩터가 **자기 정의가 허용하는 범위** 안에 있는가.

    왜 필요한가
    ───────────
    팩터는 이름에 정의가 박혀 있다. ψ 는 "표면 보호가 만드는 제거 **억제**
    배수"이므로 ≤ 1 이어야 한다. 그런데 실측에서 ψ = 18.15 가 나왔고
    (억제제 0 조건), 그 값이 MRR 을 18배 부풀려 예측 9085 vs 실측 19.2 라는
    형상오차 117.8 % 를 만들었다.

    이 종류의 결함은 조용하다 — 예외도 NaN 도 아니고 그냥 큰 수다.
    이름이 약속한 범위를 검사기가 들고 있어야 잡힌다.

    ⚠ 값을 자르지 않는다. clamp 는 물리를 숨기는 것이다.
      범위를 벗어났다는 **사실을 신고**하고, 왜 벗어났는지는 모델이 답한다.
    """
    # 팩터 이름 → (하한, 상한, 그 범위가 무슨 뜻인가)
    # 물질명 없음 — 팩터의 정의에서만 나온다.
    RANGES: Dict[str, Tuple[float, float, str]] = {
        "psi": (0.0, 1.0, "표면 보호는 제거를 억제한다 — 촉진할 수 없다"),
        "delta": (0.0, float("inf"), "결함 밀도는 음수일 수 없다"),
        "stab": (0.0, float("inf"), "안정도는 음수일 수 없다"),
        "chi": (0.0, float("inf"), "화학 반응성은 음수일 수 없다"),
        "kappa": (0.0, float("inf"), "접촉 강도는 음수일 수 없다"),
        "tau": (0.0, float("inf"), "전달 효율은 음수일 수 없다"),
        "theta": (0.0, float("inf"), "열 항은 음수일 수 없다"),
        "gamma": (0.0, float("inf"), "컨디셔닝 항은 음수일 수 없다"),
        "lambda": (0.0, float("inf"), "기계 부하는 음수일 수 없다"),
        "pi": (0.0, float("inf"), "하중 분포는 음수일 수 없다"),
    }

    import warnings
    warnings.filterwarnings("ignore")
    from sim.engine import Recipe, simulate
    from sim.params import load_pack
    import sim.models  # noqa: F401  (모델 등록)

    out: List[Issue] = []
    for pack in packs:
        # ⚠ 기본 조건만 보면 놓친다.
        #   상대항은 기준점에서 정확히 1.0 이므로 범위를 벗어날 수 없다.
        #   정의 위반은 **검증 조건**(기준점 밖)에서 드러난다 —
        #   실제로 ψ=18.15 는 억제제 0 조건에서만 나왔고 기본 조건에서는
        #   1.000 이었다. 기본 조건만 검사하면 검사기가 거짓 안심을 준다.
        #   그래서 각 드라이버를 기준점 아래/위로 밀어 보며 함께 본다.
        probes: List[Tuple[str, Dict[str, float]]] = [("기준", {})]
        try:
            pk = load_pack(pack)
        except Exception:
            pk = None
        if pk is not None:
            for key, lo_hi in _RANGE_PROBE_DRIVERS.items():
                if not pk.has(key):
                    continue
                try:
                    x0 = float(pk.get(key))
                except (TypeError, ValueError):
                    continue
                for tag, v in lo_hi(x0):
                    probes.append((f"{key}={v:g}", {key: v}))

        for tag, ov in probes:
            try:
                rr = simulate(Recipe(pack=pack, pack_overrides=ov))
            except Exception as e:  # noqa: BLE001
                if tag == "기준":
                    out.append(Issue("R", "error",
                                     f"[{pack}] 팩터 산출 실패: {e}",
                                     "엔진이 이 팩을 실행하지 못합니다."))
                continue
            for key, fac in rr.factors.items():
                val = getattr(fac, "value", None)
                if not isinstance(val, (int, float)) or key not in RANGES:
                    continue
                val = float(val)
                if val != val:          # NaN
                    continue
                lo, hi, why = RANGES[key]
                if not (lo - 1e-9 <= val <= hi + 1e-9):
                    out.append(Issue(
                        "R", "error",
                        f"[{pack}] {key} = {val:.4g} 가 정의 범위 "
                        f"[{lo:g}, {hi:g}] 밖 (조건: {tag})",
                        f"{why}. 값을 자르지 말고 **왜 벗어났는지**를 "
                        "고치십시오 — 보통 상대값의 기준점이 검증 조건 "
                        "범위의 하단이 아니라 중간에 있을 때 생깁니다."))
                    break          # 팩·팩터당 한 번만 신고
    return out


def check_identifiability(packs: List[str]) -> List[Issue]:
    import warnings
    warnings.filterwarnings("ignore")
    from sim.engine import Recipe, simulate
    out: List[Issue] = []
    seen: set = set()
    for pack in packs:
        try:
            rr = simulate(Recipe(pack=pack))
        except Exception:
            continue
        owner: Dict[str, List[str]] = {}
        for k, f in rr.factors.items():
            if not f.mrr_coupled:
                continue
            for d in (f.drivers or {}):
                owner.setdefault(d.split("(")[0], []).append(k)
            if f.status == "modeled" and f.terms and not f.sources:
                sig = ("src", pack, k)
                if sig not in seen:
                    seen.add(sig)
                    out.append(Issue(
                        "I", "warn", f"[{pack}] {f.symbol} {k} 가 modeled 인데 근거 경로 없음",
                        "완성 게이트는 f.sources 를 셉니다. 비어 있으면 다음 회차가 "
                        "같은 문헌을 다시 찾습니다.",
                        "f.sources 에 knowledge/ 노트 경로를 넣으십시오."))
        for d, ks in sorted(owner.items()):
            if len(ks) > 1:
                sig = ("dup", d, tuple(sorted(ks)))
                if sig in seen:
                    continue
                seen.add(sig)
                out.append(Issue(
                    "I", "error", f"드라이버 '{d}' 가 MRR 팩터 {sorted(ks)} 에 중복",
                    "같은 물리량이 두 번 곱해집니다(이중 계상). 데이터로도 분리할 수 "
                    "없습니다 — 식별 불가능.",
                    "한 팩터에만 남기고 다른 쪽은 그 팩터를 참조하게 하십시오."))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--pack", help="팩 하나만 검사 (기본: 전 팩)")
    ap.add_argument("--skip-limits", action="store_true",
                    help="극한 검사는 팩×드라이버마다 서브프로세스를 띄워 느립니다")
    a = ap.parse_args()

    from sim.params import available_packs
    from sim.pack_meta import NON_SLURRY
    packs = [a.pack] if a.pack else [p for p in available_packs() if p not in NON_SLURRY]

    issues: List[Issue] = []
    issues += check_dimensions()
    issues += check_factor_ranges(packs)
    issues += check_identifiability(packs)
    if not a.skip_limits:
        issues += check_limits(packs)

    order = {"error": 0, "warn": 1, "info": 2}
    issues.sort(key=lambda i: (order.get(i.severity, 9), i.check, i.title))

    if a.json:
        print(json.dumps([asdict(i) for i in issues], ensure_ascii=False, indent=2))
    else:
        names = {"D": "차원", "L": "극한", "I": "식별", "R": "범위"}
        if not issues:
            print(f"✅ 모델식 위생 검사 통과 — 팩 {len(packs)}개, "
                  "차원·범위·극한·식별 위반 없음")
        for i in issues:
            mark = {"error": "🔴", "warn": "🟡", "info": "⚪"}[i.severity]
            print(f"{mark} [{names[i.check]}] {i.title}")
            print(f"     {i.detail}")
            if i.fix:
                print(f"     조치: {i.fix}")
        n_err = sum(1 for i in issues if i.severity == "error")
        print(f"\n팩 {len(packs)}개 검사 · 총 {len(issues)}건 (심각 {n_err})")
    return 1 if any(i.severity == "error" for i in issues) else 0


if __name__ == "__main__":
    sys.exit(main())
