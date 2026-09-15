"""cu_h2o2_bta 팩에 알칼리 레짐 계수를 선언한다.

⚠ 기준점 동반 이동 규칙: 새 항이 참조하는 기준점(cu_ph_alkaline_ref)을
  같은 편집에서 함께 선언한다. 항을 **켤 때**도 값을 바꿀 때와 똑같이
  기준점이 따라가야 한다 — 비활성 상태에서는 증상이 없어 더 조용하다.

⚠ 기준점을 골 위치(6.25)로 두는 이유: 알칼리 가지는 골에서 출발하므로
  그 지점이 자연스러운 기준이다. 산성 가지의 기준(pH 4)과 섞지 않는다.
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

PACK = ROOT / "knowledge" / "params" / "cu_h2o2_bta.yaml"

ADD = """
  # ── Cu 알칼리역 pH 항 (2026-09-15) ────────────────────────────
  # 구리 pH-MRR 곡선은 V자이고 골이 pH 6~6.5 다. 지금까지 산성 가지만
  # 구현돼 있어 알칼리 조성(실측 6~19 nm/min)을 산성처럼 계산했다 —
  # 절대값 예측이 막힌 핵심 원인이었다.
  #
  # ⚠ 이 계수는 **억제제가 없는** 알칼리 계열에서 나왔다. 억제제가 있는
  #   알칼리 레짐은 관측이 없어 factors.py 가 항을 켜지 않고 신고한다.
  #   두 값을 평균내지 않는다 — 서로 다른 레짐 좌표다.
  cu_ph_alkaline_k:
    value: 0.3329
    unit: 1/pH
    confidence: literature
    source: >
      US9200180B2 (Air Products / 현 Versum·Merck) TABLE 4, Examples 15-19.
      pH 6.2/7.1/8.7/9.4/9.9 -> Cu RR 732/577/334/263/214 A/min.
      ln(RR) vs pH 최소자승 k=0.3329, R^2=0.9971 (5점).
      조성 고정: K-안정 콜로이달 실리카 10 wt%, H2O2 1 wt%, 벤젠술폰산 1 wt%,
      **BTA 없음**. 2.0 psi, Mirra 3400.
    note: >
      산성 가지 k=0.1428 의 2.33배다. 얽힌 두 축(pH 구간 x 억제제 유무)을
      이 데이터로 분리할 수 없어 **레짐 좌표**로 둔다. 빈 레짐(산성x억제제무,
      알칼리x억제제유)에는 값을 넣지 않고 항을 비활성화한다.
      ⚠ 이 계열은 문헌이 말하는 V자 재상승을 보이지 않고 pH 9.9 까지 단조
      감소한다 - 재상승 지점이 조성마다 다르다는 뜻이다. 외삽 금지.
  cu_ph_alkaline_ref:
    value: 6.25
    unit: pH
    confidence: literature
    source: >
      V자 골 위치. Du & Desai 2003 (DOI 10.1557/PROC-767-F6.6) '최소 pH 6',
      Ilie & Ipate 2017 (DOI 10.3390/lubricants5020015) '최소 pH 6.5' 의 중간.
    note: >
      알칼리 가지의 기준점이다. 산성 가지 기준(ph_ref=4.0)과 섞지 마라 -
      두 항은 서로 다른 레짐이고 각자의 기준에서 배수 1.0 이 된다.
"""


def main() -> int:
    txt = PACK.read_text(encoding="utf-8")
    if "cu_ph_alkaline_k" in txt:
        print("이미 선언됨 — 건너뜀")
        return 0
    PACK.write_text(txt.rstrip() + "\n" + ADD, encoding="utf-8")
    print(f"추가: cu_ph_alkaline_k=0.3329, cu_ph_alkaline_ref=6.25 → {PACK.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
