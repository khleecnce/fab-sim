# 슬러리 안정성 전문가 (slurry-colloid)

## 현재 레벨: [활성, G3 개방 2026-09-12] — Lv1 2/6, Lv2 1/2
- 부모: slurry-chemist (부모의 knowledge/ 노트를 선행 필수로 읽는다)
- 이수 단원: Lv1-1, Lv1-2 (2026-09-12), Lv2-1 (2026-09-13)
- 다음 단원: Lv2-2

## 역할
분산 안정성·응집·POU 필터·쉘프라이프·희석/혼합이 대입자(LPC)와 스크래치에 미치는 영향

## 선행 지식 (부모에게 상속)
- [[../../knowledge/cmp/colloid-zeta-dlvo-slurry-stability]]

## 실데이터 책임 (ORG.md §7.3)
슬러리 로트·보관 이력 데이터 → LPC·결함 예측 잔차 정의

## 레벨 정의
Lv1 학부지식 → Lv2 대학원/리뷰논문 → Lv3 최신논문 추적 + 모델 구현 → Lv4 모델 개선 제안(교수급)

## 이수 기록
- 2026-09-12 Lv1-1 DLVO 심화(이온강도·pH·온도별 응집속도, Smoluchowski) —
  [[../../knowledge/slurry/dlvo-ionic-strength-ph-aggregation-kinetics]].
  핵심: perikinetic 실측/이론 20~45% 범위(Holthoff 1996), CMP 세리아 실측 이온강도 임계전이
  4→10mM(Kwon 2023), 온도의존성은 점도(η(T)) 경로가 지배. check_knowledge/verify_claims 통과.
- 2026-09-12 Lv1-2§9 추가: 실리카 염응집 시리즈로 damage_exponent 화학종 교차확증(세리아 n≈1.44 vs 실리카 n≈0.40, 방향일치·절대값불일치). check_knowledge/verify_claims 통과.
- 2026-09-12 Lv1-2 LPC 측정과 스크래치 상관관계(콜로이드 불안정화 메커니즘 관점) —
  [[../../knowledge/slurry/colloidal-destabilization-lpc-defect-mechanism]].
  핵심: Basim & Moudgil(2002) 실측 — NaCl 0.2M(CCC 미달)에서 벌크 입도분포 불변인데도
  Rmax 25→50nm 증가(DLVO 장벽 720→167kT, 여전히 통상 안정문턱보다 높음) → 벌크 광산란
  입도계는 LPC 꼬리에 본질적으로 둔감함을 시사. 입경-Rmax Pearson r≈0.33(약한 상관,
  강성이 입경보다 중요). Remsen2006(0.68µm)·Kwon2023(0.7µm) 임계직경 독립 수렴(<5% 차이,
  n=2라 미검증 표기). check_knowledge/verify_claims 통과.

- 2026-09-13 Lv2-1 POU 필터·재순환·펌프 전단이 입자에 미치는 영향 —
  [[../../knowledge/slurry/pou-filtration-recirculation-pump-shear-lpc]].
  핵심: ① 전단 응집은 **AND 조건**(G≥G_th AND G·t≥Camp_th) — Khanna 2018/2019가 pH10 실리카에서
  G=1000/s×2500s(Camp 2.5e6 > 임계 1.5e6)인데 응집 없음을 직접 보고. 임계 전단률 1000~1500 s⁻¹,
  임계 Camp는 pH2 1e5 / pH7 1.5e5 / pH10 1.5e6(IEP 근처가 15배 취약). ② 팹 루프 100 turnovers
  (=1.06e4 s)에서 G=1500/s면 Camp는 임계의 10.6배 → 설계 레버는 노출시간이 아니라 전단률.
  ③ 필터 포집은 체가 아니라 DLVO 지배 — 세리아 IEP(pH6.5) 횡단 시 단일섬유 효율 0.142→0.025
  (5.7배 급락, Rastegar 2017). 안정성과 여과성은 상충. ④ 리텐션↔beta ratio는 β=1/(1−E) 항등식;
  Entegris 실측 단일통과 리텐션 56~90 %(세리아 β=2.27 vs 실리카 β=4.55). PSL 비드는 양방향으로
  빗나가 보수적 대리시험이 아니다. ⑤ 재순환 실측이 CSTR 이상 제거모델을 1/4.8~1/14.4로 밑돎
  (Wood 2019) → 생성항 존재가 요구됨(인과는 미확정, 3가설 병렬 보존).
  check_knowledge/verify_claims 통과(코드 6블록, 출처 5건 실존).

## 구현 요청
- 무엇을: `sim/factors.py`의 `_f_delta`(Δ 손상 유발도)가 `aggregate_ratio`를 드라이버 후보
  키로 이미 받아두지만(현재 코드 L1022) 실제 계산식(L1034-1041)에는 안 쓰고 `abrasive_d99_nm`
  경로만 작동한다. 이걸 "d99 경로와 독립적인 손상 가중치"로 연결하는 항 추가를 검토해 달라
  — 예: `val = (d99/d99_ref)^n * (1 + w * aggregate_ratio)` 같은 곱셈 가중(형태는 미정,
  폐형식 문헌 없음 — 방향성만 제안).

## 구현 요청 (2) — 2026-09-12 추가, damage_exponent 화학종 분리
- 무엇을: `damage_exponent`(현재 전 팩 공통 n=3.0)를 화학종별로 분리 검토.
  세리아계(sti_ceria, sic_ceria_h2o2): n≈1.44(Hitachi 특허 US8439995B2, 스크래치 카운트, R²=0.997).
  실리카계(oxide_silica): n≈0.40(Basim & Moudgil 2002, RMS 거칠기, R²=0.99, 단 Rmax 지표로는
  n≈0.60/R²=0.80으로 갈림). 두 화학종 모두 n=3.0보다 훨씬 완만하다는 **방향**은 교차확증되나
  절대값은 3.6배 차이로 수렴하지 않음 — 즉시 상수 교체는 보류, 표본 확충 후 재시도.
- 근거 노트: [[../../knowledge/slurry/colloidal-destabilization-lpc-defect-mechanism]] §9.
- 검증에 쓸 문헌값: §9 verify 블록(n_rms≈0.40, n_hitachi_ceria=1.444).
- 우선순위: 낮음(표본 3~4점, 화학종별 분리의 실익이 확정되지 않음).
- 근거 노트: [[../../knowledge/slurry/colloidal-destabilization-lpc-defect-mechanism]] §3, §6.
  Basim & Moudgil(2002)의 NaCl 0.2M 사례(평균 입경 불변인데 Rmax 25→50nm, 2배) — d99가 전혀
  안 바뀌는 불안정화 경로로도 손상이 늘 수 있음을 보여주는 1차 실측.
- 검증에 쓸 문헌값: 같은 노트 §5 verify 블록(Pearson r≈0.33, 장벽비 720/167kT). 단, 이 비율을
  팩 전반에 그대로 이식할 정량 근거(계수 w)는 아직 없다 — **1차로는 방향(존재만)만 넣는 것이
  정직함**. 절대 계수를 지어내면 안 됨.
- 선행 필요: 팩에 `aggregate_ratio`를 실제로 채워줄 입력 경로(로트 보관이력·이온강도 추정 등)가
  아직 없음 — Cal-1(캘리브레이션 단원, G2 이후)에서 다룰 범위. 지금 당장은 no-op로 남아도
  구조만 마련해 두는 것을 제안.
- 우선순위: 낮음(입력 경로 부재로 즉시 발동 안 함 — slurry-abrasive의 `abrasive_d99_nm` 스펙
  확보 선행 요청과 동일한 병목 공유).

## 구현 요청 (3) — 2026-09-13 추가, 슬러리 이력(전단·여과) → LPC 상태량
- 무엇을: 현재 슬러리 팩의 `abrasive_d99_nm` / `aggregate_ratio`는 "제조 시 값"으로 고정 입력된다.
  이를 **루프 이력을 통과한 상태량**으로 바꾸는 구조를 검토해 달라. 최소 형태 3가지:
  1. **전단 응집 게이트(AND 조건)**: `agglomerate = (G >= G_th) and (G*t >= Camp_th)`.
     Camp 수 단일 스칼라 게이트로 만들면 문헌 반례(G=1000/s × 2500 s, Camp 2.5e6 > 임계 1.5e6인데
     응집 없음)에서 틀린다. **두 조건을 하나로 합치지 말 것.**
  2. **필터 제거항**: 단일통과 리텐션 E 또는 beta ratio β(=1/(1−E))를 팩 파라미터로.
     등급(µm)만으로 정하면 안 됨 — 같은 0.5 µm 등급 필터가 세리아 56 %, 실리카 78~90 %,
     알루미나 83~88 %로 갈린다(화학종·pH 의존).
  3. **재순환 수지**: `LPC(n) = 생성항(n) − 제거항(n)`. 단, 제거만 있는 CSTR 모델
     `R(n)=1−exp(−E·n)`은 실측을 4.8~14.4배 과대예측하므로 **그대로 쓰면 안 된다**.
- 근거 노트: [[../../knowledge/slurry/pou-filtration-recirculation-pump-shear-lpc]] §2.4, §4, §7.
- 검증에 쓸 문헌값: 같은 노트 verify 블록 6개.
  G_th(pH10 실리카)=1000~1500 s⁻¹; Camp_th = {pH2: 1e5, pH7: 1.5e5, pH10: 1.5e6};
  β(0.5 µm 등급) = {ceria: 2.27, silica: 4.55~10.0, alumina: 5.88~8.33, PSL: 2.63};
  Wood 2019 CDS 5 µm: E(단일통과, ≥0.3 µm)=0.10, 실측 R(25턴)=0.405.
- 선행 필요: 팩에 펌프 전단률 G와 루프 turnover 수를 넣을 입력 경로가 없다(Cal-1 범위).
  구조만 먼저 마련하고 기본값은 no-op(=응집 게이트 off, β=∞)로 두는 것을 제안.
- ⚠ 넘기면 안 되는 수치: Seo 2003의 유량-카운트 거듭제곱 지수(≈0.71, R²≈0.77)는 그래프 판독
  4점이라 **sim/ 상수로 옮기지 말 것**. 방향(유량↑ → 여과효율↓)만 쓸 것.
- 우선순위: 중간. 입력 경로가 없어 즉시 발동하지는 않지만, 위 1번(AND 게이트)은 폐형식이
  단순하고 문헌 반례로 직접 검증되므로 구조를 잘못 잡으면 나중에 되돌리기 어렵다.
