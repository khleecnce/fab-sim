"""이상치를 **규칙으로** 가른다 — 손으로 고르면 체리피킹이다.

왜 규칙을 먼저 고정하는가
────────────────────────
"안 맞는 점을 뺀다"를 사람이 하면, 빼는 기준이 결국 "빼면 지표가 오르는가"가
된다. 그 순간 지표는 모델의 실력이 아니라 선별의 결과가 된다.

그래서 순서를 뒤집는다: **판정 규칙을 먼저 적고, 그 규칙이 무엇을 빼는지는
나중에 본다.** 규칙이 지표를 보지 못하게 하는 것이 핵심이다.

판정 규칙 (이 순서로 적용, 위가 우선)
─────────────────────────────────────
  C1 물리 불가   : 실측값 자체가 물리적으로 불가능 (음수 MRR, 0 이하)
                   → **제거**. 원인: 데이터 전사 오류.
  C2 정의역 밖   : 입력이 모델이 선언한 게이트 밖
                   (예: pH 게이트 3~6 인데 조건이 10)
                   → **제거**하고 게이트를 기록. 외삽은 모델의 실패가 아니다.
  C3 미지 상수   : 그 조건을 계산하는 데 필요한 상수가 쌍 표에 없음
                   → **순위만 유지**, 절대값 집계에서 제외. R8 발행.
  C4 계열 혼재   : 한 계열 안에서 배율이 두 무리로 갈림 (bimodal)
                   → **계열 분할**. 제거가 아니다.
  C5 설명 불가   : 위 넷에 해당하지 않는데 잔차가 극단
                   → **남긴다.** 이것이 진짜 모델 갭이고, 지울 대상이 아니다.

⚠ C5 가 이 파일의 존재 이유다. 설명할 수 없는 이상치는 **제거 금지**다.
  제거하면 고칠 기회가 사라지고, 지표만 좋아진다.

판정에 쓰지 않는 것
──────────────────
  · "이 점을 빼면 ρ 가 오른다"  ← 절대 판정 근거로 쓰지 않는다
  · 잔차 크기 단독              ← 크다는 것은 증상이지 원인이 아니다
"""

from __future__ import annotations

import sys
import pathlib
import warnings
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

warnings.filterwarnings("ignore")
ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np                                     # noqa: E402

__all__ = ["Verdict", "classify_point", "bimodal_scale_split"]

# 모델이 선언한 게이트 — 팩·항이 스스로 밝힌 적용 한계
# ⚠ 이 표는 "맞추려고" 좁히는 것이 아니다. 각 항의 문헌 근거가 정의한 범위다.
GATES: Dict[str, Tuple[float, float, str]] = {
    # Cu 산성역 pH 항: V자 골(pH 6~6.5) 너머는 부호가 반대다.
    # knowledge/cmp/cu-cmp-ph-mechanism.md
    "cu_ph": (2.0, 6.0, "Cu pH 항은 산성 가지 전용 — pH 6 너머는 곡선이 재상승(부호 반대)"),
}


@dataclass
class Verdict:
    code: str                  # C1~C5
    action: str                # remove / rank_only / split / keep
    reason: str
    detail: str = ""
    notes: List[str] = field(default_factory=list)

    @property
    def removed(self) -> bool:
        return self.action == "remove"


def classify_point(pred: float, obs: float,
                   inputs: Optional[Dict[str, float]] = None,
                   pack: str = "",
                   note_text: str = "") -> Verdict:
    """한 점을 규칙으로 판정한다. 지표는 보지 않는다.

    note_text 는 엔진이 그 조건에서 낸 경고 문구다 — 모델이 스스로
    "이 값은 모른다"고 말한 경우를 잡는다(C3).
    """
    inputs = inputs or {}

    # C1 — 실측값 자체가 물리적으로 불가능
    if not np.isfinite(obs) or obs <= 0:
        return Verdict("C1", "remove",
                       "실측 MRR 이 0 이하이거나 비유한 — 물리적으로 불가능",
                       f"obs={obs}",
                       ["원인은 모델이 아니라 데이터 전사다. 원표를 다시 읽어야 한다."])

    if not np.isfinite(pred) or pred <= 0:
        return Verdict("C1", "remove",
                       "예측이 0 이하이거나 비유한 — 계산 경로가 깨졌다",
                       f"pred={pred}",
                       ["이것은 이상치가 아니라 **버그**다. 제거하고 끝내면 안 된다."])

    # C2 — 입력이 모델이 선언한 게이트 밖 (외삽)
    ph = inputs.get("slurry_ph")
    if ph is not None and pack.startswith("cu"):
        lo, hi, why = GATES["cu_ph"]
        if not (lo <= ph <= hi):
            return Verdict("C2", "remove",
                           f"pH {ph:g} 가 선언된 게이트 [{lo:g}, {hi:g}] 밖",
                           why,
                           ["외삽에서 틀리는 것은 모델의 실패가 아니다 — "
                            "게이트를 밝히는 것이 정직한 처리다.",
                            "⚠ 단, 이 데이터가 필요하면 그 영역의 항을 "
                            "**새로 유도**해야 한다(게이트를 넓히는 게 아니라)."])

    # C3 — 계산에 필요한 상수가 없다 (모델이 스스로 신고한 경우)
    if "쌍의 ΔG 가 표에 없다" in note_text or "[R8 측정 명세]" in note_text:
        return Verdict("C3", "rank_only",
                       "그 조건의 재료쌍 상수가 없다 — 절대값을 계산할 근거가 없다",
                       "",
                       ["순위는 유지한다(농도가 오르면 내린다는 방향은 물리에서 나온다).",
                        "절대값 집계에서만 뺀다. R8 측정 명세가 발행돼 있다."])

    # C5 — 설명할 수 없다. **남긴다.**
    return Verdict("C5", "keep",
                   "위 규칙에 해당하지 않는다 — 설명 가능한 사유가 없다",
                   "",
                   ["이것이 진짜 모델 갭이다. 제거하면 고칠 기회가 사라진다."])


def bimodal_scale_split(pred: Sequence[float], obs: Sequence[float],
                        min_gap: float = 3.0) -> Optional[Tuple[List[int], List[int], str]]:
    """C4 — 한 계열의 배율이 두 무리로 갈리는지 본다.

    배율이 bimodal 이면 그 계열 안에 서로 다른 물리(또는 다른 장비)가
    섞여 있다는 뜻이다. 제거가 아니라 **분할**이 답이다.

    min_gap: 두 무리의 배율 비가 이보다 크면 갈린 것으로 본다.
             기본 3배 — 측정 재현성으로 설명되지 않는 크기다.
    """
    p = np.asarray(pred, dtype=float)
    o = np.asarray(obs, dtype=float)
    m = np.isfinite(p) & np.isfinite(o) & (p > 0) & (o > 0)
    if m.sum() < 4:
        return None
    logr = np.log(o[m] / p[m])
    order = np.argsort(logr)
    s = logr[order]

    # 가장 큰 간극에서 자른다 — 그 간극이 min_gap 배 이상이면 분할
    gaps = np.diff(s)
    if gaps.size == 0:
        return None
    k = int(np.argmax(gaps))
    if float(np.exp(gaps[k])) < min_gap:
        return None

    idx = np.flatnonzero(m)
    lo = [int(idx[order[i]]) for i in range(k + 1)]
    hi = [int(idx[order[i]]) for i in range(k + 1, s.size)]
    msg = (f"배율이 두 무리로 갈린다 — 낮은 무리 ×{np.exp(np.mean(s[:k+1])):.3g} "
           f"({len(lo)}점) vs 높은 무리 ×{np.exp(np.mean(s[k+1:])):.3g} ({len(hi)}점), "
           f"간극 {np.exp(gaps[k]):.1f}배. 계열을 갈라야 한다.")
    return lo, hi, msg
