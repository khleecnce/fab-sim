# 컨디셔닝 목적과 메커니즘: glazing 제거, asperity 재생

> disk-conditioner Lv1-1. [[hertz-gw-contact-mechanics]] [[pad-wear-glazing-mrr-decay]] [[cmp-tool-architecture]] [[pad-viscoelasticity-dma]] [[conditioner-grit-design-space]] 상호링크.

## 1. 왜 컨디셔닝이 필요한가 — 경쟁 메커니즘 (Lawing 2004)
**출처**: A. Scott Lawing (Rohm and Haas Electronic Materials CMP Technologies), "Pad Conditioning Effects in Chemical Mechanical Polishing", NCCAVS CMPUG 2004-05-05 발표자료(공개 PDF, AVS strategic-plan 아카이브 호스팅: https://strategic-plan.avs.org/wp-content/uploads/CMPUG2004/CMPUG_05_2004_Lawing.pdf). 산업 컨퍼런스 발표(피어리뷰 논문 아님, 실측 데이터 포함 1차 자료로 취급) — 이하 "Lawing 2004"로 인용.

- **패드 표면 구조는 두 경쟁 효과의 균형으로 결정된다**:
  1. **패드 마모(Pad Wear)**: 웨이퍼-패드 접촉에 의한 asperity 마모/평탄화 → glazing 진행. [[pad-wear-glazing-mrr-decay]]의 Shi&Ring 모델과 동일 현상.
  2. **컨디셔너 절삭(Conditioner Cut Rate)**: 다이아몬드 디스크가 패드 표면을 깎아 intrinsic(고유) asperity 구조를 복원.
  - Cut Rate = Wear Rate인 지점이 정상상태(steady state) — Cut Rate > Wear Rate면 "Above horizontal, more stable"(과소마모=고유구조 유지), Cut Rate < Wear Rate면 "Severe glazing"(과대마모=심한 유리화).
- **극단 사례 비교**: "Conditioning dominated" 표면(중간 공격성 컨디셔너로 유지되는 intrinsic 구조) vs "Wafer dominated" 표면(컨디셔닝 없이 다수 웨이퍼 연마 시 asperity tip이 절단된 truncated 구조, 높이분포 저단부에 별도 성분 형성). 즉 **컨디셔닝 부재는 단순 높이감소가 아니라 분포 형태 자체를 변형**(2차 피크 성장)시킨다 — [[pad-wear-glazing-mrr-decay]]의 population balance 이류(advection) 그림과 정합.

## 2. 컨디셔너 공격성(aggressiveness)이 정상상태 표면에 미치는 영향
- 동일 패드 마모율 조건에서, 컨디셔너 공격성이 증가할수록 정상상태 glazing 정도가 감소(더 거친 표면 유지).
- 정량 실측(Lawing 2004): 저/중/고 공격성 컨디셔너에서 추정 접촉면적이 각각 **11.3% / 7.7% / 2.2%** — 공격성이 낮을수록 asperity가 더 truncate되어 오히려 접촉면적(비율)이 커진다(뭉툭해진 다수의 얕은 접촉 vs 뾰족한 소수의 깊은 접촉).
- **다이아몬드 결정 크기/형상/밀도**가 절삭 특성과 고유 표면구조를 직접 결정: 더 공격적인 다이아몬드일수록 상호작용당 더 많은 패드를 제거하고 더 거친("rough") 표면을 만든다. Solid(비발포) 패드는 공격성이 곧 거칠기를 좌우(고유 텍스처 없음, 거의 가우시안 높이분포), void-filled(발포) 패드는 공격성이 표면 근처 영역에만 영향(필러 재료가 고유 거칠기를 결정, 컨디셔닝은 추가 주파수 성분을 중첩).

## 3. 공정변수 → 정상상태의 함의
- 컨디셔닝 하중(down-force)을 늘리면 제거되는 패드 재료가 늘어 마모-복원 균형이 이동. **임계 하중** 존재: 임계 이하에서는 하중 감소에 따라 연마율(polish rate)이 하락, 임계 이상에서는 하중 증가에도 연마율이 포화.
- **고유구조는 컨디셔너 하중에 크게 민감하지 않다** — 일단 마모성분이 상쇄되어 고유구조가 복원되면 추가 컨디셔닝은 표면구조를 더 바꾸지 않는다(과잉 컨디셔닝의 물리적 한계).
- Ex-situ(컨디셔닝 중단 후) 연마율 감쇠: 전형적 **로그(logarithmic) 감쇠** 관찰 — 시간에 따른 asperity 마모 증가가 연마율 감소와 대응. 콜로이달 슬러리는 fumed 실리카 슬러리보다 asperity 마모가 덜 심해 감쇠도 덜함(슬러리 화학과 기계적 마모의 상호작용, 미검증 정량 메커니즘).

## 4. 정량 모델: 다이나믹 Asperity Population Balance (Ring, Prasad & Dirksen)
**출처**: Terry A. Ring, Abaneshwar Prasad, James A. Dirksen (Univ. of Utah / Cabot Microelectronics), "Dynamic CMP Pad Asperity Population Balance for Conditioning and Polishing" — 저자 공개 PDF: https://my.che.utah.edu/~ring/Publications-PDFs/J-120.pdf (무료·공개, [[pad-wear-glazing-mrr-decay]]의 Shi&Ring 2010과 같은 저자군의 선행 연구로 추정).
이 논문은 [[pad-wear-glazing-mrr-decay]]에서 다룬 Shi&Ring(2010) population balance를 **컨디셔너-패드 접촉에도 명시적으로 적용**한 점에서 disk-conditioner 관점의 핵심 연결점이다.

### 4.1 마모율 모델 (Evans & Marshall 소성변형 마모법칙)
- Asperity 국소 마모율: `WearRate(P_n, Vel, Area) = (1/2)·P_n·Vel·cot(psi/2) / (H_pad^2·Area)` (Eq.2) — P_n=국소수직력, Vel=상대속도(패드-웨이퍼 또는 패드-컨디셔너), cot(psi/2)=압입자(indenter) 각도의 코탄젠트, H_pad=패드 경도. 비례상수(order-1)는 fit parameter.
- 국소 하중/접촉면적 비는 GW로부터: `L/A ~ 4E'*Vel*cot(psi/2) / (3*pi*H_pad*beta)` (Eq.3, E'=E_pad/(1-nu_pad^2), beta=asperity 곡률반경) — [[hertz-gw-contact-mechanics]]의 Hertz-GW 골격과 동일 재료상수 사용.

### 4.2 분리거리(compliance)의 해석적 형태 (지수분포 가정)
- `d = sigma*ln(P_applied / (pi*sigma*E'*rho*sqrt(beta)*A^2))` (Eq.4, sigma=평균 asperity 높이 감쇠상수, rho=asperity 밀도) — [[hertz-gw-contact-mechanics]]에서 사용한 지수분포 GW와 동일 가정, 로그 형태는 지수분포 특유의 해석해.

### 4.3 Population Balance PDE와 폐형식 해 (핵심 신규 내용)
- 지배방정식: `d(eta_z)/dt + A*d(z+d)/dz * d(eta_z)/dz = 0` (Eq.5, RHS 생성/소멸항은 컨디셔너-패드-웨이퍼 3자 동시접촉에서는 0으로 둠 — 컨디셔너 자체가 "asperity 재생성원"이므로 이 논문의 틀에서 컨디셔너 접촉은 "감소하는 asperity 개체군을 절삭해 새 분포로 재형성"으로 취급, [[pad-wear-glazing-mrr-decay]]의 B/D항과는 다른 접근).
- **특성곡선/유사변수(similarity variable) tau**로 폐형식 해 유도(Eq.7-9): `eta_z(z,t) = eta_z0(sqrt((2(d+z)/A)^2 - t) - d)` — 초기분포 eta_z0(z)가 시간에 따라 "형태를 유지한 채 변형"되는 자기유사(self-similar) 해. **이 폐형식 해는 fab-sim의 pad_wear_glazing.py(Lv3-1, Monte-Carlo 이산근사)와 달리 해석적으로 정확** — 다음 절에서 수치 재현·비교.
- **응용 1 (웨이퍼만 접촉, 컨디셔닝 없음)**: 지수분포 초기조건 → 시간에 따라 가장 긴 asperity부터 우선 마모, 남은 asperity들의 높이가 수렴(분포 폭이 좁아짐) → 웨이퍼 하중을 지지하는 asperity 수가 늘고 국소하중 편차가 줄어듦(정성적으로 [[pad-wear-glazing-mrr-decay]]의 "낮은 asperity 마모되어 사라지고 남은 것 뭉침"과 일치하나 이 논문은 반대 극단인 "긴 것부터 마모"를 강조 — **부드러운 마모(wafer, 낮은 P_n) vs 유리화 관찰(오래된 정성 관찰)의 뉘앙스 차이, 미검증 통합**).
- **응용 2 (컨디셔너만 접촉)**: 신품 패드는 정규분포(평균 0, sigma=8.112 µm, 컨디셔너 그릿 특성에서 역산: **Asperity 밀도 rho=1/D_grit^2, 평균 asperity 높이=D_grit/2** — Table 1, D_grit=190 µm 컨디셔너에서 sigma=8.112 µm는 미검증 산출과정이나 논문 표에 직접 명시) → 컨디셔닝 시간 증가에 따라 분포가 좁아지며 로그-선형(지수형) 꼬리로 수렴 — **AMAT Mirra 툴 + Epic D100 패드에서 Veeco 레이저 간섭계 실측과 정성적으로 일치**(실측 검증 있는 흔치 않은 사례).
- **응용 3 (웨이퍼+컨디셔너 동시접촉, in-situ)**: 컨디셔너의 절삭 효과가 지배적(웨이퍼 기여는 미미) — 컨디셔너 grit이 패드보다 훨씬 rough하기 때문(Eq.2의 마모율이 압입자 형상·하중에 의존, 다이아몬드 그릿의 곡률반경이 asperity보다 작아 국소응력이 훨씬 큼).

### 4.4 disk-conditioner 관점에서의 함의
- 컨디셔너 그릿 크기(D_grit)가 **직접** 생성되는 패드 asperity의 평균 높이·밀도·곡률반경을 결정한다(Table 1의 근사: 밀도∝1/D_grit^2, 높이∝D_grit/2, 곡률반경∝D_grit) — 이는 Lv1-2(다이아몬드 디스크 설계 변수: grit size/density/protrusion) 단원의 정량적 출발점이 된다.
- 컨디셔너 절삭이 지배적인 이유는 마모율 공식(Eq.2)의 압입자 형상항(cot(psi/2))과 곡률반경(beta)이 다이아몬드 그릿에서 훨씬 날카롭기(작은 beta) 때문 — 물리적으로 "더 날카로운 압입자가 같은 하중에서 더 큰 국소응력을 만든다"는 Hertz 접촉의 직접적 귀결.

## 5. 다음 단원과의 연결
- Lv1-2(그릿 크기/밀도/돌출)에서 Table 1/2의 D_grit-asperity 특성 매핑을 정량적으로 확장.
- Lv2-1(디스크-패드 절삭모델)에서 Eq.2(Evans-Marshall 마모율)를 직접 구현 대상으로 삼는다 — fab-sim pad_wear_glazing.py가 이미 유사한 Archard 마모 이산근사를 갖고 있으므로(Shi&Ring 경로), 이 논문의 **폐형식 해(Eq.9)로 수치해를 교차검증**하는 것이 Lv3-2(disk-conditioner 결합모델) 이전 정합성 확보에 유용.

## 6. 수치 재현 시도와 정직한 한계 (2026-09-04)
`agents/disk-conditioner/scripts/ring_similarity_check.py` 실행 결과:
- **PASS**: 유사변수(similarity variable) t=0 항등사상 — 대수식 자체의 내적 일관성(자기무모순)은 확인.
- **MISS/미검증**: t>0에서 논문 서술(장신 asperity 우선 마모 → 평균높이 단조감소)을 재현하려 했으나, 재현된 수치는 오히려 평균높이가 증가하다 전체 붕괴(0)하는 반대 방향 거동을 보임.
- **원인**: PDF 텍스트 추출(OCR) 과정에서 Eq.7-9의 괄호·첨자 구조가 손상되어("2⋅d+z", "t−τ_o" 등 순서·공백 뒤섞임) 정확한 수식 형태(특히 제곱근 내부 부호, (d+z) 항의 위치)를 확정하지 못함.
- **결론**: 이 절의 정성적 서술(§4.1-4.4)은 Lawing 2004의 독립적 실측 근거와도 정합하므로 지식으로서는 신뢰하여 기록하되, 폐형식해(Eq.9) 자체의 정량 재현은 **실패로 명시**한다. fab-sim의 향후 구현(Lv2-1/Lv3-2)에서는 이 논문의 폐형식해보다 이미 self-test 5/5 검증된 `pad_wear_glazing.py`(Monte-Carlo/Archard 경로)를 우선 신뢰하고, 원문 PDF(비-OCR, 원본 조판)를 구할 수 있으면 재시도한다.
