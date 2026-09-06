"""공개 논문 표 → validation/datasets/*.yaml 생성기.

숫자는 전부 논문에 **인쇄된 표**에서 그대로 옮긴 것이다(read_method: table).
kPa→psi 변환만 코드가 한다(계산 실수 방지). 그 외 어떤 값도 추정/보간하지 않는다.
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent / "datasets"
KPA_TO_PSI = 1.0 / 6.894757


def psi(kpa):
    return round(kpa * KPA_TO_PSI, 4)


def emit(name, header, conds, notes):
    lines = [header.rstrip(), "", "conditions:"]
    for c in conds:
        lines.append(f'  - label: "{c["label"]}"')
        lines.append(f'    pressure_psi: {c["pressure_psi"]}')
        lines.append(f'    rpm_wafer: {c["rpm_wafer"]}')
        lines.append(f'    rpm_platen: {c["rpm_platen"]}')
        lines.append(f'    mrr_nm_per_min: {c["mrr"]}')
        lines.append("    read_method: table")
    lines.append("")
    lines.append("notes: >")
    for ln in notes.strip().split("\n"):
        lines.append("  " + ln.strip())
    (OUT / f"{name}.yaml").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(name, len(conds))


# ─────────────────────────────────────────────────────────────── 1
# Yang et al., Materials 16(3) 1148 (2023) — 석영유리 CeO2-LaOF 슬러리 L25 직교배열
# doi:10.3390/ma16031148  PMC9920658  (Table 1 인자수준 + Table 3 결과)
L25_P = {1: 20, 2: 25, 3: 30, 4: 35, 5: 40}          # kPa  (Table 1 factor D)
L25_V = {1: 60, 2: 80, 3: 100, 4: 120, 5: 140}       # rpm  (Table 1 factor E)
# (No, A, B, C, D, E, F, MRR) — Table 3 그대로
L25_ROWS = [
    (1, 1, 1, 1, 1, 1, 1, 273.30), (2, 1, 2, 3, 4, 5, 2, 138.26),
    (3, 1, 3, 5, 2, 4, 3, 118.96), (4, 1, 4, 2, 5, 3, 4, 168.80),
    (5, 1, 5, 4, 3, 2, 5, 62.70), (6, 2, 1, 5, 4, 3, 5, 112.53),
    (7, 2, 2, 2, 2, 2, 1, 155.94), (8, 2, 3, 4, 5, 1, 2, 262.04),
    (9, 2, 4, 1, 3, 5, 3, 67.52), (10, 2, 5, 3, 1, 4, 4, 308.66),
    (11, 3, 1, 4, 2, 5, 4, 186.48), (12, 3, 2, 1, 5, 4, 5, 250.79),
    (13, 3, 3, 3, 3, 3, 1, 226.67), (14, 3, 4, 5, 1, 2, 2, 109.32),
    (15, 3, 5, 2, 4, 1, 3, 122.18), (16, 4, 1, 3, 5, 2, 3, 229.89),
    (17, 4, 2, 5, 3, 1, 4, 122.18), (18, 4, 3, 2, 1, 5, 5, 223.46),
    (19, 4, 4, 4, 4, 4, 1, 127.00), (20, 4, 5, 1, 2, 3, 2, 181.66),
    (21, 5, 1, 2, 3, 4, 2, 138.26), (22, 5, 2, 4, 1, 3, 3, 303.84),
    (23, 5, 3, 1, 4, 2, 4, 78.77), (24, 5, 4, 3, 2, 1, 5, 139.86),
    (25, 5, 5, 5, 5, 5, 1, 271.69),
]
emit(
    "yang2023_quartz_ceria_L25",
    """# 석영유리 CeO2-LaOF 슬러리 CMP — L25 직교배열 (압력 5수준 x 회전수 5수준 x 조성)
source: >
  Y. Yang et al., "Dispersion and Polishing Mechanism of a Novel CeO2-LaOF-Based
  Chemical Mechanical Polishing Slurry for Quartz Glass", Materials 16(3), 1148 (2023).
  doi:10.3390/ma16031148 — MDPI 오픈액세스, PMC9920658 전문 XML에서 Table 1(인자수준표)과
  Table 3(직교실험 결과)을 그대로 옮겼다. MRR 단위는 본문(“MRR was 194.20 nm/min”) 기준 nm/min.

used_for_calibration: false
pack: sti_ceria""",
    [dict(label=f"No.{n}: {L25_P[d]}kPa, {L25_V[e]}rpm (A{a} B{b} C{c} F{f})",
          pressure_psi=psi(L25_P[d]), rpm_wafer=L25_V[e], rpm_platen=L25_V[e], mrr=m)
     for (n, a, b, c, d, e, f, m) in L25_ROWS],
    """압력(D: 20~40 kPa)과 회전수(E: 60~140 rpm)가 5수준씩 변하지만 연마제 농도(A)·pH(B)·
    분산제 농도(C)·유량(F)도 동시에 변하는 직교배열이다. 즉 순수 Preston 스윕이 아니라
    화학 변수가 섞여 있다. 우리 모델은 P·V만 반응하므로, 화학 기여가 크면 순위가 깨진다 —
    그것을 재는 것이 이 데이터셋의 목적이다.
    UNIPOL-1200S 단면 연마기로 "polishing speed"만 주어져 웨이퍼/플래튼 회전수를 구분할 수 없다.
    동일 회전(co-rotation, 상대속도 = ω·r_cc)으로 가정해 rpm_wafer = rpm_platen 으로 넣었다.
    이 가정은 절대 MRR에는 영향을 주지만 조건 간 순위에는 단조 변환만 준다.
    팩은 세리아 슬러리이므로 sti_ceria. 피연마재는 석영유리(SiO2)로 STI 산화막과 다르며,
    절대값 비교는 무의미하고 순위 비교용이다.""")

# ─────────────────────────────────────────────────────────────── 2
# Yao et al., Micromachines 2026 — Mo 양면 CMP L16 직교배열. PMC12942839
L16_P = {1: 64, 2: 77, 3: 90, 4: 115}   # kPa (Table 2 factor A)
L16_ADD = {1: "no additive", 2: "H2O2", 3: "H2O2 0.5%+Gly", 4: "H2O2 1%+Gly"}
L16_PH = {1: 4, 2: 7, 3: 9, 4: 11}
L16_ABR = {1: 0.6, 2: 1.7}
L16_ROWS = [  # (No, A, B, C, D, MRR nm/min)  — Table 3 그대로
    (1, 1, 1, 1, 1, 11), (2, 1, 2, 2, 1, 94), (3, 1, 3, 3, 2, 18),
    (4, 1, 4, 4, 2, 20), (5, 2, 1, 2, 2, 125), (6, 2, 2, 1, 2, 43),
    (7, 2, 3, 4, 1, 50), (8, 2, 4, 3, 1, 57), (9, 3, 1, 3, 1, 41),
    (10, 3, 2, 4, 1, 18), (11, 3, 3, 1, 2, 61), (12, 3, 4, 2, 2, 144),
    (13, 4, 1, 4, 2, 131), (14, 4, 2, 3, 2, 88), (15, 4, 3, 2, 1, 156),
    (16, 4, 4, 1, 1, 51),
]
emit(
    "mo2026_double_sided_L16",
    """# 몰리브덴 기판 양면 CMP — L16 직교배열 (압력 4수준 x pH 4수준 x 첨가제 4수준 x 입도 2수준)
source: >
  "Experimental Study on Double-Sided Chemical Mechanical Polishing of Molybdenum
  Substrates for LED Devices", Micromachines (2026). PMC12942839 (MDPI 오픈액세스).
  https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12942839/
  Table 2(인자수준표)와 Table 3(L16 결과, MRR[nm/min])을 그대로 옮겼다.
  회전수: 본문 §2.1 "the upper plane and lower plane rotated at 3.3 rpm and 10 rpm".

used_for_calibration: false
pack: oxide_silica""",
    [dict(label=f"No.{n}: {L16_P[a]}kPa, pH{L16_PH[b]}, {L16_ADD[c]}, {L16_ABR[d]}um",
          pressure_psi=psi(L16_P[a]), rpm_wafer=3.3, rpm_platen=10, mrr=m)
     for (n, a, b, c, d, m) in L16_ROWS],
    """압력만 우리 모델의 입력이고 pH·첨가제·입도는 반영되지 않는다(팩에 Mo 화학이 없다).
    논문 자신의 극차분석에서도 지배 인자는 첨가제(R=88.25) > 압력(R=70.75) 순이므로,
    압력만 보는 모델의 순위 상한이 낮을 수밖에 없다. **이것이 이 데이터셋의 핵심 정보다** —
    화학층이 없는 조건에서 우리 예측이 얼마나 무력한지의 정량치.
    피연마재가 Mo(금속)라 전용 팩이 없다. 순위는 Kp 스케일에 불변이므로 oxide_silica 팩의
    기계 모델만 쓰되, 절대 MRR·MAPE는 의미 없다.
    양면 연마기(상/하 정반 3.3/10 rpm)를 회전형 CMP 기구학으로 근사했다 — 모든 조건에서
    동일하므로 순위에는 영향이 없다.""")

# ─────────────────────────────────────────────────────────────── 3
# Chen et al., Micromachines 14(4) 900 (2023) — 4H-SiC 전단유동 연마 L9. PMC10143364
L9_ROWS = [  # (No, 입도um, 농도wt%, 회전수 r/min, 압력 kPa, MRR nm/min) — Table 2+3
    (1, 0.5, 3, 70, 9.05, 6.5), (2, 0.5, 6, 80, 10.19, 7.8),
    (3, 0.5, 9, 90, 11.32, 13.3), (4, 1.0, 3, 80, 11.32, 43.4),
    (5, 1.0, 6, 90, 9.05, 34.7), (6, 1.0, 9, 70, 10.19, 30.3),
    (7, 1.5, 3, 90, 10.19, 22.4), (8, 1.5, 6, 70, 11.32, 21.9),
    (9, 1.5, 9, 80, 9.05, 28.7),
]
emit(
    "sic2023_shear_rheological_L9",
    """# 4H-SiC 전단유동(SRP) 연마 — L9 직교배열 (압력 3수준 x 회전수 3수준 x 입도/농도)
source: >
  "Experimental Study on Shear Rheological Polishing of Si Surface of 4H-SiC Wafer",
  Micromachines 14(4), 900 (2023). doi:10.3390/mi14040900 — MDPI 오픈액세스, PMC10143364.
  Table 2(L9 배치)와 Table 3(결과, MRR nm/min)을 그대로 옮겼다.
  워크피스 회전수 20 r/min은 Table 1(SRP parameters)에서.

used_for_calibration: false
pack: oxide_silica""",
    [dict(label=f"No.{n}: {p}kPa, {v}r/min, {sz}um {cc}wt%",
          pressure_psi=psi(p), rpm_wafer=20, rpm_platen=v, mrr=m)
     for (n, sz, cc, v, p, m) in L9_ROWS],
    """압력(9.05/10.19/11.32 kPa)과 회전수(70/80/90 r/min)가 3수준씩 변하는 Preston형 스윕이지만
    다이아몬드 입도(0.5/1.0/1.5 um)와 농도(3/6/9 wt%)가 동시에 변한다.
    논문 자신의 S/N 분석에서 입도가 지배 인자이며 MRR이 입도에 대해 단봉(1.0um 최대)이다 —
    우리 모델에는 입도 항이 없으므로 이 데이터셋은 "기계항만으로 어디까지 가나"의 하한을 준다.
    CMP가 아니라 전단유동 연마(SRP)라 패드 접촉 기구가 다르다. 절대값 비교 부적합.""")

# ─────────────────────────────────────────────────────────────── 4
# Xu et al., Materials 16(?) (2023) — 초경합금 인서트 CMP 조성 L9. PMC11154297
CHEM_ROWS = [  # (No, 연마제wt%, 산화제wt%, 분산제wt%, pH, MRR nm/min) — Table 1+5
    (1, 10, 6, 4, 11, 66.85), (2, 10, 8, 3, 9.5, 74.81), (3, 10, 10, 2, 8, 79.58),
    (4, 8, 6, 3, 8, 39.79), (5, 8, 8, 2, 11, 55.71), (6, 8, 10, 4, 9.5, 57.30),
    (7, 6, 6, 2, 9.5, 41.38), (8, 6, 8, 4, 8, 50.93), (9, 6, 10, 3, 11, 30.24),
]
emit(
    "carbide2023_slurry_composition_L9",
    """# 초경합금 인서트 CMP — 슬러리 조성만 바꾼 L9 (압력·회전수 완전 고정)
source: >
  "Experimental Study on Chemical-Mechanical Synergistic Preparation for Cemented
  Carbide Insert Cutting Edge", Micromachines/Materials (2023). PMC11154297 (오픈액세스).
  https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11154297/
  Table 1(조성 직교표), Table 2(고정 공정조건: 94.99 kPa, 70 rpm, 30 min),
  Table 5(MRR nm/min, Ra) 인쇄값 그대로.

used_for_calibration: false
pack: oxide_silica""",
    [dict(label=f"No.{n}: 연마제{a}wt% 산화제{o}wt% 분산제{d}wt% pH{ph}",
          pressure_psi=psi(94.99), rpm_wafer=70, rpm_platen=70, mrr=m)
     for (n, a, o, d, ph, m) in CHEM_ROWS],
    """**의도적 대조군(negative control)이다.** 압력 94.99 kPa·회전수 70 rpm이 9조건 모두 동일하고
    연마제 농도(6/8/10 wt%)·산화제 농도(6/8/10 wt%)·분산제·pH만 바뀐다. 실측 MRR은 30.24~79.58
    nm/min로 2.6배 퍼져 있다.
    우리 모델은 팩 단위로만 화학을 보고 조건별 조성을 입력받지 못하므로 9조건 예측이 전부 동일하다
    → Spearman ρ가 판정불가(NaN)로 나오는 것이 정상이며, 그것이 곧 "sim/chemistry.py가 아직
    조건별 조성에 배선되어 있지 않다"는 정량적 증거다. 이 데이터셋은 그 공백을 기록하려고 넣었다.""")
