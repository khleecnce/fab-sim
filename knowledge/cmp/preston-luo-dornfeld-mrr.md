# Preston 방정식 & Luo-Dornfeld 입자스케일 모델 — MRR 이론 정밀분석

> process-integrator Lv2-1. 관련: [[../physics/cmp-kinematics-rotary]] (v_R 항의 출처), [[../equipment/cmp-tool-architecture]]

## 1. Preston 방정식 (1927, 유리 연마 기원)

$$ \dot{h} = K_p \cdot P \cdot V $$

- $\dot h$: 재료제거율(선형, 두께/시간), $P$: 압력, $V$: 상대속도, $K_p$: Preston 계수(경험적 lumped 상수).
- 출처: F.W. Preston, "The theory and design of plate glass polishing machines," *J. Soc. Glass Technol.*, 11, 214–256 (1927). (원문은 유료/희귀 — 2차 인용으로 검증. 아래 재인용 다수 확인됨)
- 재인용 확인 소스:
  - S. Chen (Iowa State Univ. PhD thesis), "A study on material detachment mechanism in CMP process" (2000s), 5–8쪽 문헌리뷰 — https://dr.lib.iastate.edu/bitstreams/a946712d-5717-441d-87f7-61c66c27ca57/download (무료 공개, 원문 확인함)
  - DuPont US Patent Application 2026/0091462 "Pad for chemical mechanical polishing" — "Rate = Kp·P·V ... Kp is the so-called Preston Coefficient, a lumped sum constant characteristic of the consumable set" — https://www.freepatentsonline.com/y2026/0091462.html (특허 공개, 요지만 확인)
- **물리적 의미**: $K_p$는 화학·기계 효과를 전부 뭉뚱그린 현상론적 상수 — 압력·속도 외 슬러리 입자크기/농도, 패드 물성, 화학반응 속도의 영향은 전혀 분리하지 못함. 이것이 이후 모델들(Brown, Tseng-Wang, Luo-Dornfeld 등)의 동기.
- **전형적 $K_p$ 값 (SiO2/콜로이달실리카)**: 문헌 재인용상 ~$10^{-13}$–$10^{-12}$ m²/N (novasolver.jp 공학 계산기 FAQ가 "~1e-13 m²/N for SiO2 w/ colloidal silica"로 명시 — *미검증*, 1차 논문 대조 못함. 방향성(오더)만 참고용으로 채택, 절대값은 재료·슬러리마다 실측 캘리브레이션 필요).

## 2. Preston 이후 확장 모델 계보 (Chen 논문 문헌리뷰, 5–8쪽 요약)

| 저자(연도) | 모델 형태 | 가정 |
|---|---|---|
| Preston (1927) | $\dot h = K_p PV$ | 선형, 상수 lump |
| Brown (1981) | $\dot h = \frac{1}{2E}PV$ | 완전 고체-고체 접촉, 광학연마 |
| Tseng & Wang (1997) | $\dot h \sim P^{5/6}V^{1/2}$ | Runnels-Eyman(1994) 유체역학 기반, 슬러리막 40–65µm 가정, 열산화막 실험과 부합 |
| Bulsara et al. (1997) | 활성입자 모델 | 힘은 활성입자(전체의 <0.5%, 입도분포 꼬리)로만 전달 — 경질 패드/저압·고농도에 적합 |
| **Luo & Dornfeld (2001)** | $\dot h = C \cdot P^{1/2} \cdot V$ | 완전 소성접촉(웨이퍼-입자-패드), $C$가 압력에 종속(입도분포가 압력의 함수) |
| Fu et al. (2001) | 비접촉: $\dot h\sim P^{3/2}V$ / 접촉: $\dot h\sim P^{9/8}V$ | 소성 빔모델, 두 접촉모드 전이조건 해석해 유도 |
| Shi & Zhao (1998) | $\dot h \sim P^{2/3}V$ | 연질 패드, 압력의존성이 경질패드와 근본적으로 다름 |
| Zhao & Shi (2000) | $\dot h \sim (P^{2/3}-P_{th}^{2/3})\cdot V$ | 문턱압력 $P_{th}$ 도입 — 이 압력 이하는 제거 없음 |
| Bastawros et al. (2002) | 현상론적, 수치기반 | 비접촉/부분접촉/완전접촉 3모드, 압력·패드탄성·슬러리농도로 결정 |

출처: Chen thesis 5–8쪽 (위 링크), 문헌 원저는 IEEE Trans. Semicond. Manuf. 등에 산재 — 1차 논문 전문은 유료(미러 사이트 등 무료 우회는 원칙상 배제), **2차 인용 기반 정리이며 지수·계수는 리뷰서 표기를 그대로 채택**.

## 3. Luo & Dornfeld (2001) 핵심 아이디어 상세

원 논문: J. Luo, D.A. Dornfeld, "Material removal mechanism in chemical mechanical polishing: theory and modeling," *IEEE Trans. Semicond. Manuf.*, 14(2), 112–133 (2001). (유료 게재, 원문 미확보 — 아래는 2차 인용 종합)

- 가정: 웨이퍼-입자, 입자-패드 계면 모두 **완전 소성접촉**. 입자 크기는 **정규분포**, 패드 표면은 **주기적 거칠기**로 근사.
- 확장판(Effects of Abrasive Size Distribution in CMP: Modeling and Verification, IEEE Trans. Semicond. Manuf. 16(3), 2003 — Luo&Dornfeld 후속): 입도분포가 압력에 따라 "활성" 입자 집단을 바꾼다는 게 골자. 압력이 오르면 더 많은(더 작은) 입자가 활성화되어 $C$가 압력의 함수가 됨 → $\dot h = C(P)\cdot P^{1/2}\cdot V$ 형태가 곧 $\dot h \propto P^{n}V$ ($n>1/2$)로 실효 편차 발생 설명.
- Chen thesis 평가(7쪽 인용, *미검증이지만 다수 2차 문헌이 공유하는 비판*): "매우 단단한 패드를 가정하면서 동시에 연질 패드 논의와 상충 — ambiguity 존재. 그럼에도 재료물성·패드 표면물성·입자 형상/크기분포를 폭넓게 고려한 최초의 입자스케일 모델이라는 의의는 유효."
- **공통 한계** (Chen thesis 8쪽): 초기 입자스케일 모델들은 예측 MRR이 실측보다 수 배~수십 배 높게 나옴 — trench 내 재료가 입자 이동과 함께 전부 제거된다고 가정하기 때문("ploughing vs cutting" 구분 결여).

## 4. 공정통합 관점 종합 (이 에이전트의 결론)

1. **v0 구현 전략**: 위 계보 중 실무적으로 가장 널리 쓰이고 파라미터가 적은 **Preston 선형식**을 Tier1 베이스로 채택한다. $\dot h = K_p \cdot P(r,\theta) \cdot V(r,\theta)$ — $V$는 이미 구현된 [[../physics/cmp-kinematics-rotary]]의 $v_R(r,\theta)$를 그대로 사용.
2. **P^{1/2} 계열 확장은 Tier2**로 남긴다: Luo-Dornfeld형 $\dot h\propto P^{1/2}V$나 Fu et al.의 이중모드는 슬러리-패드 접촉역학(GW 모델, tribologist 영역)이 성숙한 뒤 결합.
3. **$K_p$의 물리적 위치**: 운동학(Lv1-2)에서 이미 $V(r,\theta)$의 공간분포를 얻었으므로, Preston v0에서 남는 자유도는 (a) $K_p$ (재료·슬러리 종속 상수, 캘리브레이션 필요) (b) $P(r,\theta)$ (멤브레인 존압 분포, pad-mechanic 영역과 결합 필요) 뿐이다.
4. **WIWNU 재확인**: Lv1-2에서 이미 "속도 비균일도는 자전평균으로 상쇄, WIWNU 주범은 압력분포"라 결론지었음. Preston식이 $P\cdot V$의 곱이므로 이번 정리로 이 결론이 재확인됨 — $V$가 균일해지는 조건($\omega_w=\omega_p$)에서 Preston MRR의 반경 프로파일은 순수하게 $P(r)$ 프로파일을 따른다.

## 5. 자기시험

→ [[../../agents/process-integrator/EXAMS.md]] Lv2-1 문항 참조.
