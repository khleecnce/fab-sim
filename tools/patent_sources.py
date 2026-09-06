"""신뢰 출원인 화이트리스트 + 물리 기반 이상치 기준.

사용자 지시(2026-09-06):
  "특허는 1. 대학교수, 2. 믿을만한 기업 (삼성하이닉스 마이크론, cabot, entegris,
   fujimi, fujifilm, MERCK 등 슬러리나 CMP쪽에서 메이저 기업) 것만 반영하도록해"
  "벗어나는 수치는 제외시키고"

왜 출원인 필터가 이상치 제거보다 강한가:
  특허 실시예의 숫자는 검증 절차가 없다. 출원인이 유리하게 쓴 값일 수 있고, 실험
  조건이 불명확한 경우도 많다. 통계적 이상치 제거는 "튀는 값"만 걸러낼 뿐,
  **일관되게 부정확한 출처**는 못 거른다.

  반면 CMP 소재를 실제로 양산하는 기업과 이 분야 학계는 자기 실시예가 재현되지
  않으면 잃을 것이 크다. 데이터 품질의 사전 확률 자체가 다르다.

  → 1차 게이트 = 출원인, 2차 게이트 = 물리 범위. 순서가 중요하다.
"""
from __future__ import annotations

import re
from typing import Dict, List, Optional, Tuple

# ── 1차 게이트: 신뢰 출원인 ─────────────────────────────────
# 소문자 부분일치로 검사한다. 사명 변경·자회사·표기 흔들림을 흡수하기 위해
# 짧은 핵심 토큰을 쓰되, 오탐이 날 만큼 짧은 것은 피한다.

SLURRY_CONSUMABLE = {
    # CMP 소모재 메이저 (슬러리·패드)
    "cabot": "Cabot Microelectronics (현 Entegris)",
    "cmc materials": "CMC Materials (구 Cabot Micro, 현 Entegris)",
    "entegris": "Entegris",
    "fujimi": "Fujimi Incorporated",
    "fujifilm": "FUJIFILM",
    "merck": "Merck KGaA (구 Versum/Air Products 계열 포함)",
    "versum": "Versum Materials (현 Merck)",
    "air products": "Air Products (CMP 사업 → Versum)",
    "dupont": "DuPont (구 Rohm and Haas CMP 패드)",
    "rohm and haas": "Rohm and Haas Electronic Materials",
    "rodel": "Rodel (CMP 패드·슬러리 선구자, → Rohm and Haas → DuPont)",
    "eternal materials": "Eternal Materials (CMP 슬러리)",
    "ace nanochem": "ACE NanoChem",
    "anji microelectronic": "Anji Microelectronics (安集)",
    "hubei dinglong": "Hubei Dinglong (鼎龙)",
    "sinmat": "SinMat (SiC/GaN CMP 슬러리)",
    "planar solutions": "Planar Solutions",
    "epoch material": "Epoch Material (長興)",
    "jiangsu": "Jiangsu 계열 CMP 소재사",
    "asahi kasei": "Asahi Kasei",
    "tokuyama": "Tokuyama Corporation (실리카)",
    "denka": "Denka Company",
    "admatechs": "Admatechs (실리카)",
    "nippon chemical": "Nippon Chemical Industrial",
    "dow global": "Dow (CMP 패드)",
    "jsr corp": "JSR Corporation",
    "hitachi chemical": "Hitachi Chemical (현 Showa Denko Materials)",
    "showa denko": "Showa Denko Materials / Resonac",
    "resonac": "Resonac (구 Showa Denko)",
    "asahi glass": "AGC / Asahi Glass",
    "nitta haas": "Nitta Haas (CMP 패드·슬러리)",
    "3m innovative": "3M (CMP 소모재)",
    "ferro corp": "Ferro Corporation",
    "nissan chemical": "Nissan Chemical (콜로이달 실리카)",
    "kao corp": "Kao Corporation (연마 조성물)",
    "wacker": "Wacker Chemie (실리카)",
    "evonik": "Evonik (실리카·세리아)",
    "solvay": "Solvay",
    "basf": "BASF",
    # 국내 소재사
    "dongjin": "동진쎄미켐",
    "soulbrain": "솔브레인",
    "kctech": "케이씨텍",
    "k.c.tech": "케이씨텍",
    "ltc co": "엘티씨",
    "sk hynix": "SK하이닉스",
    "samsung electronics": "삼성전자",
    "sk siltron": "SK실트론",
}

DEVICE_EQUIPMENT = {
    # 칩 제조사 (CMP 공정 당사자)
    "micron technology": "Micron Technology",
    "intel corp": "Intel",
    "taiwan semiconductor": "TSMC",
    "globalfoundries": "GlobalFoundries",
    "international business machines": "IBM",
    "texas instruments": "Texas Instruments",
    "infineon": "Infineon",
    "toshiba": "Toshiba / Kioxia",
    "kioxia": "Kioxia",
    "renesas": "Renesas",
    "united microelectronics": "UMC",
    "semiconductor manufacturing international": "SMIC",
    # 장비사 (CMP 툴·공정)
    "applied materials": "Applied Materials",
    "ebara": "Ebara Corporation",
    "lam research": "Lam Research",
    "tokyo electron": "Tokyo Electron",
    "revasum": "Revasum",
    "axus technology": "Axus Technology",
}

ACADEMIC_MARKERS = (
    "university", "universite", "universität", "universidad", "univ ",
    "institute of technology", "college", "research institute",
    "academy of sciences", "학교", "대학", "kaist", "postech", "unist",
    "national laboratory", "cnrs", "fraunhofer", "imec", "sematech",
    "industry-academic", "산학협력단", "research foundation",
)

TRUSTED = {**SLURRY_CONSUMABLE, **DEVICE_EQUIPMENT}


def classify_assignee(names: List[str]) -> Tuple[bool, str, str]:
    """(신뢰 여부, 분류, 매칭된 기관명)

    분류: consumable | device_equipment | academic | untrusted
    """
    for raw in names:
        low = (raw or "").lower().strip()
        if not low:
            continue
        for key, label in SLURRY_CONSUMABLE.items():
            if key in low:
                return True, "consumable", label
        for key, label in DEVICE_EQUIPMENT.items():
            if key in low:
                return True, "device_equipment", label
        for mark in ACADEMIC_MARKERS:
            if mark in low:
                return True, "academic", raw.strip()
    return False, "untrusted", (names[0].strip() if names else "")


# ── 단위 환산 → nm/min ─────────────────────────────────────
# 특허마다 단위가 제각각이다. 2026-09-06에 μm/h를 빠뜨려 Entegris 특허
# (표9·실시예8 보유)를 "단위 없음"으로 놓칠 뻔했다. 놓친 단위 = 놓친 데이터다.
RATE_UNITS_FULL = {
    "nm/min": 1.0, "nm/minute": 1.0, "nm min": 1.0,
    "a/min": 0.1, "å/min": 0.1, "angstrom/min": 0.1, "a/minute": 0.1,
    "angstroms/min": 0.1, "å/minute": 0.1,
    "um/min": 1000.0, "µm/min": 1000.0, "μm/min": 1000.0, "micron/min": 1000.0,
    "um/h": 1000.0 / 60.0, "µm/h": 1000.0 / 60.0, "μm/h": 1000.0 / 60.0,
    "um/hr": 1000.0 / 60.0, "µm/hr": 1000.0 / 60.0, "μm/hr": 1000.0 / 60.0,
    "micron/hour": 1000.0 / 60.0, "um/hour": 1000.0 / 60.0,
    "nm/h": 1.0 / 60.0, "nm/hr": 1.0 / 60.0,
    "mm/min": 1e6,
}


def find_rate_unit(text: str):
    """텍스트에서 제거율 단위를 찾는다. (표기, nm/min 환산계수) 또는 None.

    긴 것부터 검사한다 — 'um/min'이 'um/m'에 먼저 걸리면 안 된다.
    """
    low = text.lower()
    for u in sorted(RATE_UNITS_FULL, key=len, reverse=True):
        if u in low:
            return u, RATE_UNITS_FULL[u]
    return None


# ── 2차 게이트: 물리 범위 ───────────────────────────────────
# "벗어나는 수치는 제외" — 다만 통계적 이상치(±3σ)가 아니라 **물리적으로 불가능한
# 값**을 기준으로 자른다. 통계 기준은 데이터가 편중돼 있으면 정상값을 버리고
# 편중된 값을 남긴다. 물리 기준은 데이터 분포와 무관하게 옳다.
#
# 근거: knowledge/cmp/preston-luo-dornfeld-mrr.md (STI 254 nm/min @ 3psi),
#       knowledge/cmp/cmp-tool-architecture.md (문헌 표준 공정조건)

PHYSICAL_RANGE: Dict[str, Tuple[float, float, str]] = {
    # 키: (하한, 상한, 근거)
    "mrr_nm_per_min": (
        0.1, 20000.0,
        "CMP 제거율. 산화막 수십~수백, Cu 수백~2000 nm/min이 통상. "
        "20000 초과는 CMP가 아니라 grinding/lapping 영역이거나 단위 오독이다. "
        "0.1 미만은 정지막(stop layer) 수치라 스크리닝 비교 대상이 아니다."),
    "pressure_psi": (
        0.1, 15.0,
        "다운포스. 통상 1~6 psi, 특수 공정 포함해도 15 psi 초과는 웨이퍼 파손 영역."),
    "rpm_wafer": (1.0, 500.0, "웨이퍼 회전수"),
    "rpm_platen": (1.0, 500.0, "플래튼 회전수"),
    "slurry_ph": (0.5, 13.5, "수용액 pH. 이 밖은 측정 오류이거나 비수계"),
    "oxidizer_wt_pct": (0.0, 30.0, "산화제 농도. 30wt% 초과 H2O2는 취급 불가 영역"),
    "abrasive_wt_pct": (0.01, 50.0, "연마입자 농도"),
    "abrasive_size_nm": (1.0, 2000.0, "1차 입경. 2000nm 초과는 슬러리가 아니라 페이스트"),
    "inhibitor_mM": (0.0, 500.0, "억제제 농도"),
    "time_s": (1.0, 7200.0, "연마 시간"),
}


def check_physical(key: str, value: float) -> Optional[str]:
    """물리 범위 위반이면 사유 문자열, 정상이면 None."""
    rng = PHYSICAL_RANGE.get(key)
    if rng is None:
        return None
    lo, hi, why = rng
    if value < lo or value > hi:
        return f"{key}={value:g}이 물리 범위 [{lo:g}, {hi:g}] 밖 — {why}"
    return None


def screen_condition(cond: Dict) -> Tuple[bool, List[str]]:
    """조건 하나를 물리 범위로 검사한다. (통과, 사유들)"""
    reasons = []
    for k, v in cond.items():
        if isinstance(v, (int, float)):
            r = check_physical(k, float(v))
            if r:
                reasons.append(r)
    for k, v in (cond.get("overrides") or {}).items():
        if isinstance(v, (int, float)):
            r = check_physical(k, float(v))
            if r:
                reasons.append(r)
    return (not reasons), reasons


def internal_consistency(conds: List[Dict]) -> List[str]:
    """데이터셋 내부 정합성 — 개별 값은 정상인데 묶어놓으면 이상한 경우.

    통계적 이상치를 여기서 다루되, 버리지 않고 **표시만** 한다.
    특허 실시예에는 의도적으로 극단 조건이 들어가므로(비교예) 튄다고 틀린 게 아니다.
    """
    warns = []
    rates = [float(c["mrr_nm_per_min"]) for c in conds if "mrr_nm_per_min" in c]
    if len(rates) >= 4:
        srt = sorted(rates)
        q1 = srt[len(srt) // 4]
        q3 = srt[(3 * len(srt)) // 4]
        iqr = q3 - q1
        if iqr > 0:
            out = [r for r in rates if r < q1 - 3 * iqr or r > q3 + 3 * iqr]
            if out:
                warns.append(
                    f"IQR 3배 밖 값 {len(out)}개: {[round(o,1) for o in out][:5]} "
                    "— 비교예(의도적 극단 조건)일 수 있으니 원문 확인 후 판단. "
                    "자동 제거하지 않았다.")
    if rates and min(rates) > 0:
        span = max(rates) / min(rates)
        if span > 1000:
            warns.append(f"최대/최소 비가 {span:.0f}배 — 서로 다른 막질(예: Cu vs 정지막)이 "
                         "한 표에 섞였을 수 있다. 같은 막질끼리 분리하라.")
    return warns
