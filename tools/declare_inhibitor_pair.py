"""cu_h2o2_bta 팩이 (억제제 × 기질) 쌍을 선언하게 한다.

지금까지 팩에는 inhibitor_dG_ads_kJ = -35.4 하나뿐이었다(등급 unverified,
폐형식 근거 없음). 억제제를 바꿔도 같은 값을 쓰므로, 니코틴산 데이터에
BTA 용 상수가 적용돼 흡착상수가 5,700 배 어긋났다.

쌍을 선언하면:
  · BTA × Cu  → 문헌 쌍값(-30.02, literature)을 조회한다
  · 다른 억제제 → 쌍이 없으므로 **거부**하고 R8 측정 명세를 발행한다
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent  # tools/ 의 부모
sys.path.insert(0, str(ROOT))

PACK = ROOT / "knowledge" / "params" / "cu_h2o2_bta.yaml"

ADD = """
# ── 억제제-기질 쌍 (2026-09-15) ───────────────────────────────
# ΔG_ads 는 억제제 단독의 성질이 아니라 **쌍**의 성질이다.
# 근거: 같은 논문·같은 방법인데 BTA/Cu -30.02 vs BTA/Fe -21.89 (8.13 kJ/mol 차)
#       10.2320/matertrans.m2016310
# 이 두 키를 선언하면 엔진이 쌍 표에서 ΔG 를 조회하고, 쌍이 없으면
# 유사 값으로 대체하지 않고 측정 명세(R8)를 발행한다.
inhibitor_species:
  value: bta
  confidence: verified
  source: 팩 정의 자체 (이 팩은 BTA 계 구리 슬러리다)
  note: >
    이 키는 수치가 아니라 **조회 키**다. 다른 억제제를 쓰려면 이 값을 바꿔야
    하고, 그러면 엔진이 그 쌍의 ΔG 를 요구한다 - 조용히 BTA 값을 재사용하지
    않는다. 그것이 5,700배 오차의 원인이었다.
substrate_species:
  value: cu
  confidence: verified
  source: 팩 정의 자체
  note: >
    기질을 명시해야 하는 이유는 같은 억제제라도 기질이 바뀌면 ΔG 가 바뀌기
    때문이다. 순금속과 합금도 다른 쌍이다(BTA/Cu-Ni = -22.093).
"""


def main() -> int:
    txt = PACK.read_text(encoding="utf-8")
    if "inhibitor_species" in txt:
        print("이미 선언됨 — 건너뜀")
        return 0
    PACK.write_text(txt.rstrip() + "\n" + ADD, encoding="utf-8")
    print(f"추가: inhibitor_species=bta, substrate_species=cu → {PACK.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
