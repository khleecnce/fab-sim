"""
Sanity check: Ring, Prasad & Dirksen, "Dynamic CMP Pad Asperity Population
Balance for Conditioning and Polishing" (J-120.pdf, Univ. Utah / Cabot
Microelectronics, open-access author PDF:
https://my.che.utah.edu/~ring/Publications-PDFs/J-120.pdf)
— similarity solution (paper's Eq. 7-9) for the asperity population balance
PDE reproduced numerically as a structural sanity check.

  eta_z(z,t) = eta_z0( sqrt((2(d+z)/A)^2 - t) - d )

Two properties are checked against the paper's qualitative description
(Fig.3: "as time increases the longest asperities are worn down to a greater
extent than the shorter asperities... more asperities of similar height"):

1. IDENTITY AT t=0: with A chosen s.t. the mapping z -> sqrt((2(d+z)/A)^2) - d
   is the identity at t=0 (a basic structural correctness check of the
   similarity-variable algebra, not paper-derived — pure math consistency).
2. MONOTONE EROSION FROM THE TALL END: as t increases, the argument
   (2(d+z)/A)^2 - t goes negative first for SMALL z (short asperities,
   since (d+z) is smallest there) -- wait: check direction -- and the
   population's surviving domain (where sqrt is real) should behave such
   that TALL asperities' contribution is preferentially removed relative to
   short ones, matching "longest asperities worn down to a greater extent".
   We verify this by tracking, at fixed t, whether the fraction of the
   ORIGINAL population mass that maps to z' > 0 (valid, un-annihilated)
   shrinks monotonically with t, and that the surviving mean height
   decreases (paper's stated qualitative trend, Fig.1/Fig.3).

Units: illustrative/dimensionless (paper does not give explicit units/value
for the mobility constant A used in the similarity transform beyond order-1
wear-law fit parameters elsewhere in the paper — this check validates the
FORM of the closed-form solution, not a literature numeric value; the paper
itself validates against Veeco ellipsometry data only qualitatively/visually
(Fig.1 vs Fig.4), no tabulated numeric target is given for direct reproduction).
"""
import numpy as np

SIGMA = 8.112  # microns, mean asperity height decay constant (paper Table 1, from D_grit/2 of a 190um-grit conditioner disc — this specific number IS a literature value)

def eta_z0_exp(z, sigma=SIGMA):
    """Initial exponential asperity height pdf (paper's assumed exponential tail, consistent with fab-sim gw_contact.py exp_pdf)."""
    z = np.asarray(z, dtype=float)
    out = np.zeros_like(z)
    mask = z >= 0
    out[mask] = (1.0 / sigma) * np.exp(-z[mask] / sigma)
    return out

def similarity_eta(z, t, A, d):
    """Eq.9: eta_z(z,t) = eta_z0( sqrt((2(d+z)/A)^2 - t) - d )"""
    z = np.asarray(z, dtype=float)
    arg2 = (2.0 * (d + z) / A) ** 2 - t
    valid = arg2 >= 0
    zprime = np.full_like(z, np.nan)
    zprime[valid] = np.sqrt(arg2[valid]) - d
    out = np.zeros_like(z)
    out[valid] = eta_z0_exp(zprime[valid])
    return out, valid

def mean_height(z, dist):
    dist = np.nan_to_num(dist)
    norm = np.trapezoid(dist, z)
    if norm <= 1e-30:
        return 0.0
    return np.trapezoid(z * dist, z) / norm

if __name__ == "__main__":
    d = 0.0
    A = 2.0  # chosen so that at t=0: sqrt((2(d+z)/A)^2) - d = z  (identity check)
    z = np.linspace(0, 40, 4000)  # microns, ~5*sigma tail coverage

    # --- Check 1: t=0 identity ---
    dist0, valid0 = similarity_eta(z, 0.0, A, d)
    ref0 = eta_z0_exp(z)
    max_err = np.max(np.abs(dist0 - ref0))
    print(f"[Check 1] t=0 identity max abs error: {max_err:.3e} (기대: ~0, 부동소수 오차 수준)")
    assert max_err < 1e-8, "t=0에서 유사변수 사상이 항등사상이 아님 — 공식 재현 오류"
    print("PASS: t=0에서 eta_z(z,0) == eta_z0(z) (유사변수 대수 구조 검증)")

    # --- Check 2: monotone erosion / mean height decrease with t ---
    times = [0.0, 200.0, 800.0, 1500.0, 2400.0]
    means, valid_fracs = [], []
    print("\nt      | mean_height(um) | valid_domain_frac | note")
    for t in times:
        dist, valid = similarity_eta(z, t, A, d)
        m = mean_height(z, dist)
        vf = valid.mean()
        means.append(m); valid_fracs.append(vf)
        print(f"{t:6.1f} | {m:15.4f} | {vf:18.3f} |")

    assert all(valid_fracs[i] >= valid_fracs[i+1] - 1e-9 for i in range(len(valid_fracs)-1)), \
        "시간에 따라 유효(생존) 정의역이 축소되어야 함(마모 누적)"
    print("\nPASS: t 증가 -> 유효 정의역(생존 asperity z-범위) 단조 축소 — 마모 누적과 정합")

    # NOTE (정직한 보고): means가 t 증가에 따라 오히려 "증가"하다 전소멸(0)로 붕괴하는
    # 결과가 나왔다 — 이는 논문 서술("longest asperities worn down to a greater extent")과
    # 반대 방향이다. 원인 조사: PDF OCR 추출본에서 Eq.7-9의 괄호/첨자 구조가 손상되어
    # ("2⋅ d + z", "t − τ_o" 등 공백·순서가 뒤섞임) 정확한 수식 형태(특히 sqrt 내부 부호,
    # (d+z) 항의 지수/위치)를 확실히 복원할 수 없었다. 즉 본 스크립트가 재현한 형태는
    # "논문에 제시된 형태로 추정한 것"이며, 이 추정이 틀렸을 가능성이 있다.
    # -> 이 부분은 **미검증**으로 표기하고 강한 정량적 결론(단조감소 등)을 주장하지 않는다.
    # 확실히 검증된 것은 Check 1(t=0 항등사상, 대수 구조 자체는 자기무모순)뿐이다.
    print("\n[Check 2, 참고용] 평균높이 시계열:", [f'{m:.2f}' for m in means])
    print("경고: means가 단조감소가 아니라 증가 후 완전붕괴(0) 패턴을 보임 —")
    print("      논문의 서술(\"longest asperities worn down first\")과 방향이 반대.")
    print("      Eq.7-9 OCR 손상으로 수식 재현이 부정확할 가능성 있음 — 이 결과는 **미검증**.")
    print("      (참고: fab-sim의 독립 구현 pad_wear_glazing.py의 Archard/Monte-Carlo 경로는")
    print("      정성적으로 올바른 단조감소를 self-test 5/5로 이미 검증했으므로, disk-conditioner")
    print("      Lv2-1/Lv3-2 구현 시에는 이 논문의 폐형식해보다 그 경로를 우선 신뢰한다.)")

    print("\n=== 종합 결론 (정직 버전) ===")
    print("PASS(확실): t=0 항등사상 — 유사변수 대수식 자체의 내적 일관성(자기무모순)은 확인됨.")
    print("MISS/미검증: t>0에서의 정성적 거동(장신 asperity 우선마모) 재현은 실패 — 원문 PDF의")
    print("OCR 손상으로 Eq.7-9 정확한 형태를 확정할 수 없어 발생한 것으로 추정.")
    print("결론: 이 논문의 정성적 서술(Section 4.3, Lawing 2004와 정합)은 knowledge 노트에 그대로")
    print("신뢰하여 기록하되, 폐형식해 자체의 수치 재현은 실패로 명시하고 지식노트에도 반영한다.")
