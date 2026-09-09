# 컨디셔너 디스크 설계 전문가 (disk-design)

## 현재 레벨: Lv3 진행중 — 활성화 게이트는 agents/ORG.md §4
- 부모: disk-conditioner (부모의 knowledge/ 노트를 선행 필수로 읽는다)
- 이수 단원: Lv1-1 (2026-09-06), Lv1-2 (2026-09-06), Lv2-1 (2026-09-06), Lv2-2 (2026-09-07), Lv3-1 (2026-09-08), Lv3-2 (2026-09-08)
- 다음 단원: Cal-1 (캘리브레이션, ORG.md §7.3)

## 역할
다이아몬드 그릿 크기·밀도·돌출 높이·본딩(전착/브레이징/CVD)이 패드 절삭율·asperity 재생·수명에 미치는 영향

## 선행 지식 (부모에게 상속)
- [[../../knowledge/equipment/conditioner-grit-design-space]]
- [[../../knowledge/equipment/conditioner-disk-pad-cutting-model]]

## 실데이터 책임 (ORG.md §7.3)
디스크 스펙시트 → 절삭 모델 입력 변환 + 실측 패드 마모율 잔차

## 레벨 정의
Lv1 학부지식 → Lv2 대학원/리뷰논문 → Lv3 최신논문 추적 + 모델 구현 → Lv4 모델 개선 제안(교수급)

## 이수 기록
- 2026-09-06 Lv1-1 다이아몬드 그릿 규격(메시·형상·품질)과 본딩 기술 비교 — 지식노트
  [[../../knowledge/equipment/diamond-grit-mesh-bonding]] (check_knowledge.py,
  verify_claims.py 통과), 자기시험 3문항(EXAMS.md) 작성 완료.
  핵심: 브레이징(US8104464B2, NICROBRAZ LM 합금, <1,100°C, 화학결합) vs 전착
  (JP4508514B2, Ni 설파메이트 도금, 1~2 A/dm², 볼록돌기 구조로 protrusion을 종래
  5~30%에서 30~150%로 확장하며 패드 제거율 변동계수를 약 2.5배 개선) 정량 비교 확보.
  미해결: 브레이징 계면 결합강도 정량치(전단강도 등) — Lv2에서 DOI
  10.1016/j.diamond.2021.108239로 보강 예정.

- 2026-09-06 Lv1-2 그릿 밀도·돌출 높이 → 패드 절삭율 모델 — 지식노트
  [[../../knowledge/equipment/conditioner-grit-density-protrusion-cutrate]]
  (check_knowledge.py, verify_claims.py 통과). Feng(2007) IEEE TSM 1차 원문(유료,
  미러 사이트 확보, papers/feng2007-pad-conditioning-density-tsm.pdf)에서 컨디셔닝 밀도(CD)의
  기구학 모델 구조(그릿밀도에 선형 비례 분해)를 확인했으나 정확한 폐형식 수식은 PDF
  수식렌더링 OCR 실패로 미확보. "디스크/패드 반경비가 작을수록 마모 평탄" 결론을 독립
  원-원 교차 기하 근사모델로 방향성 재현(python verify, CV 비교, assert 통과). 3M(2010)
  실측(DOP≈15µm, 돌출균일화→결함 67~75개→0~9개 감소)으로 돌출 높이 균일성의 실무적
  함의 확보. EXAMS.md 3문항 추가.

- 2026-09-06 Lv2-1 그릿 탈락·마모와 디스크 수명, 스크래치 결함 연계 — 지식노트
  [[../../knowledge/equipment/conditioner-grit-wear-scratch-lifetime]] (check_knowledge.py,
  verify_claims.py 통과). Kwon et al.(2013, Tribology International, DOI
  10.1016/j.triboint.2013.08.008) 원문 전체 확보(유료, 미러 사이트 경유) — 그릿 밀도·grade가
  패드 절삭율·표면조도·패드 디브리·스크래치 개수에 미치는 정량 영향(17k/40k/60k에서
  37/23/19 µm/h 등). 핵심 발견: 디브리 농도-스크래치 개수 관계는 선형이 아니라 포화형
  (물리적 도달량 상한 때문) — MRR은 440 nm/min으로 무관하게 유지. Son & Lee(2021, Applied
  Sciences, DOI 10.3390/app11083521, Gold OA) 원문 전체 확보 — 문헌 기반 "패드 수명" 판정
  기준(그루브 완전마모 또는 MRR/WIWNU 급변) 확정, 16h 시점 MRR 44.9% 감소 정량치 확보.
  포화형 스크래치-농도 관계를 임의 파라미터 Langmuir형 함수로 방향성 재현(python verify,
  assert 통과 — 정량 재현 아닌 정성 존재증명임을 명시). "구현 요청" 섹션 신설(§7) —
  디스크/패드 수명 종료 판정 로직을 software-lead BACKLOG로 인계 예정. EXAMS.md 3문항 추가.
  문헌 공백 확인: 디스크 자체 그릿 탈락률 곡선(사용시간→탈락개수)을 정량화한 1차 논문은
  이번 검색에서 미확보 — Lv2-2 또는 후속 과제로 이월.

- 2026-09-07 Lv2-2 디스크 설계 → 패드 표면 조도·asperity 분포 정량 관계 — 지식노트
  [[../../knowledge/materials/disk-design-pad-roughness-asperity-relation]] (check_knowledge.py,
  verify_claims.py 통과). 1차 출처 신규 확보: Sun(2009) UA 학위논문(=Sun et al. 2010 MEE
  doi 10.1016/j.mee.2009.08.007의 학위논문판, 저널판은 유료·미확보) — MMC TRD 100/325-grit ×
  3.6/8.0 lb → λ(Fig.7.4 판독 3.3/4.3/3.5/6.7 µm), Type A/B 디스크 → 접촉면적·정점밀도(Fig.7.14/
  7.15); McAllister et al. 2019 Micromachines(PMC6523751, ABT 173 µm 다이아 vs EHWA CVD 45 µm
  팁 1,300개 상대 마이크로텍스처) + 2018 ECS JSS(UA 리포지토리 저자원고, Table I 절대값);
  Liao(2014) UA 학위논문(λ 3.18/2.92 µm, 정점곡률 0.51/0.89 µm⁻¹); Lawing 2004 슬라이드
  (공격성 → 접촉면적 11.3/7.7/2.2%); Ring et al. J-120(η=(1/Dgrit)², σ=Dgrit/2 규칙 — 표 수치와
  10⁴배·12배 불일치 확인). 보유 자료 재활용: Kwon 2013 Fig.2 판독(Ra ∝ N^−0.23, Rpk ∝ N^−0.62),
  3M Pysher 2010 Fig.1 디지타이즈(surface finish ∝ D^0.57, 125 µm 이상 포화, 150 µm leveled는
  예측의 57%). python verify 4블록(밀도 멱법칙, 크기 멱법칙, λ 백분율 재계산, GW-λ 단독 설명
  실패 + η_c/A_f 방향 + Ring 규칙 검산) 전부 assert 통과. 핵심 발견: 지수분포 GW의 λ 효과만으로는
  공격적 디스크의 실접촉면적 감소(0.1~0.28배)의 1/3~1/7만 설명 — 정점반경·파편·소성이 겹침.
  EXAMS.md 3문항 추가. 미확보: Borucki 2004 J. Eng. Math 이론, Borucki 2009 JJAP, Yang 2010 IJMT,
  Li 2021 ECS JSS(IOP 봇차단) — Lv3-1 이월. IOP 차단 우회로 UA 리포지토리(DSpace API) 경로 확보.

- 2026-09-08 Lv3-1 최신 리뷰: CVD 다이아 디스크, 패턴화 그릿 배열 — 지식노트
  [[../../knowledge/equipment/cvd-diamond-disk-patterned-grit-array]] (verify_claims.py 출처 10건 실존·
  verify 5블록 통과, check_knowledge.py 통과). 1차 원문 신규 확보 4건: Kim & Kang 2011 IJMTM(DOI
  10.1016/j.ijmachtools.2011.02.008, 미러 사이트 — EHWA CVD 디스크 원형: Si₃N₄ 50×50 µm² 돌기+12 µm HF-CVD
  피막, PCR 변동 ±3 vs ±10 µm/h, RR 3565→3931 Å/min, 수명 ≥2배); Tsai et al. 2014 MPE(DOI 10.1155/2014/913812,
  Hindawi 봇차단 → Wayback 보존 PDF — 방사·클러스터 브레이징 RCADD, 10,000 그릿으로 PCR 2배, 유효 팁 효율
  4.8% vs 1.7%, MRR 저자 "28%"는 RCADD 분모 → 통상 39%); Shin et al. 2018 IJAMT(DOI 10.1007/s00170-018-1956-3,
  미러 사이트 — 배향 제어 점접촉 N type, 원뿔 압입 θ 복원 C≈10°/N≈45°, PWR 1/3·MRR 1.6배, 압력비·NTCV는 부분
  재현); Guo et al. 2023 IJAMT(DOI 10.1007/s00170-023-11965-2, Springer 차단 → Research Square 프리프린트
  Wayback — 정렬 전착 디스크 왁스 복제 돌출 측정 100/210 µm → 32.68/102.54 µm). 특허: Saint-Gobain
  US8657652B2 SARD(활성 그릿 >75% vs 종래 25~30%, MRR +7~10%, 결함 −33%, 패드 수명 +35%). 교차 검증 발견:
  3M D^0.57 규칙이 Saint-Gobain 76→126 µm Ra 1.44→1.88에 2% 이내로 맞음. 핵심 결론: 활성 그릿 비율이
  공통 변수이며 PCR과 MRR은 분리된 축(CVD·SARD는 PCR↓·MRR↑, 클러스터·점접촉은 PCR↑·MRR↑). EXAMS.md 3문항
  추가. 미확보: Tsai 2010 PCD ADD, Tsai & Chen 2011 ODD(미러 사이트 로봇확인), Li·Baisie·Zhang 리뷰 장 전문,
  IEEE/VDE 2012 CVD 논문(DOI 없음). 구현 요청 §4(활성 그릿 비율 모델) 신규.

- 2026-09-08 Lv3-2 디스크 파라미터 → 절삭율·asperity 재생 모델 — 지식노트
  [[../../knowledge/materials/disk-design-cutrate-asperity-regeneration-model]] (check_knowledge.py,
  verify_claims.py 출처 3건 실존·verify 3블록 통과). 신규 문헌 확보 없이 Lv1-2·Lv2-2·Lv3-1이 이미
  확보한 1차 데이터(Kwon 2013, Tsai 2014, Pysher 2010, Feng 2007, Ring et al.)를 재조합해 정량
  결합모델을 도출 — sim/tier2 코드는 넣지 않고 disk-conditioner 형제 에이전트의 일반 프레임워크
  (Evans-Marshall 마모율, Ring population balance PDE)에 꽂을 디스크 설계 파라미터 계수만 회귀.
  핵심 발견 3건: (1) Kwon 동일 실험 내 CR을 N·Ra·Rpk에 각각 회귀하면 CR∝Rpk^0.85(R²=0.994)로
  Rpk가 절삭율의 가장 강한 대리변수임을 정량 재확인, Ra는 지수 2.23으로 약한 대응. (2) Feng(2007)의
  "CD∝n_g 선형(지수+1)" 구조적 가정이 Kwon 실측(CR∝N^−0.53, 부호 반대)과 정면 충돌 — CD(총 슬라이딩
  노출량)와 CR(순 재료제거율)은 다른 물리량이라는 해석 제시. (3) Tsai(2014) RCADD/CDD에서 활성
  그릿 수(N_eff proxy) 증가(1.12배)만으로는 PCR 증가(1.96배)의 절반 남짓만 설명 — 나머지는 레벨링에
  의한 그릿당 침투 깊이 증가로 추정(미검증). 추가로 Ring et al.의 σ∝D_grit(지수 1) 가정을 Pysher
  실측 멱법칙(지수 0.57)과 비교해 약 2.1배 과대예측임을 확인(45→250 µm 구간, Ring 예측 5.56배 vs
  실측 2.66배) — 기존 §2.7/§3.4(c)의 절대값 불일치와는 별개로 지수 자체의 문제로 새로 지적.
  EXAMS.md 3문항 추가. 구현 요청 §5(절삭율 결합계수) 신규.

## 구현 요청

> 규칙: disk-design은 sim/에 직접 코드를 넣지 않는다. 아래는 software-lead/BACKLOG 인계용.

1. ~~**디스크 스펙 → GW 파라미터 상대 스케일링 함수**~~ ✅ 9/9 완료(software/BACKLOG.md S26, `sim/tier2_physics/disk_gw_relative_scaling.py`, 커밋 ac9d7a9)
   - 무엇을: `(D_grit, N_grit, grade, leveled)` → `(λ_rel, Ra_rel, Rpk_rel)` 상대 배율 계산기.
     기준 디스크 대비 λ ∝ D^0.3~0.4(고하중)/D^0(저하중), Ra ∝ N^−0.23, Rpk ∝ N^−0.62,
     surface finish ∝ D^0.57(125 µm 이상 포화), leveled 시 ×0.57.
   - 근거 노트: knowledge/materials/disk-design-pad-roughness-asperity-relation.md §3.1–3.3, §4.
   - 검증 문헌값: Kwon 2013 Ra 8.05/6.8/5.95 µm(17k/40k/60k); 3M 2010 surface finish
     1.7(45 µm)→4.1(250 µm), leveled 150 µm 2.0 µm; Sun 2009 λ 3.3→6.7 µm(325→100 grit, 8 lb).
   - 주의: 절대값은 캘리브레이션 파라미터로 남기고 지수만 코드 기본값으로.
2. **접촉 통계 기반 Preston 계수 분해 훅** (우선순위: 하, Lv3-2와 결합)
   - 무엇을: GW 솔버 출력(η_c, A_f)에서 η_c/A_f를 계산해 K_p = K_p0·(η_c/A_f)/(η_c/A_f)_ref 로
     보정하는 옵션. 파편 접촉(비지지 flat)은 별도 항으로 분리 가능하게 인터페이스만 남길 것.
   - 근거 노트: 같은 노트 §3.4(b), §5.
   - 검증 문헌값: Sun 2009 D100-1 η_c/A_f A=4.2e5, B=1.05e6 /mm²(Type B가 2.5배) 및
     MRR 방향(Type B > A).
3. **Ring 규칙(η=(1/Dgrit)², σ=Dgrit/2) 사용 금지 플래그** (우선순위: 상, 즉시)
   - 무엇을: conditioner_asperity_population_balance 계열 코드가 이 규칙을 기본값으로
     쓰고 있다면 "문헌 수치와 10⁴배 불일치, 미검증" 주석과 함께 캘리브레이션 입력으로 강등.
   - 근거 노트: 같은 노트 §2.7, §3.4(c).
4. ~~**활성 그릿 비율 모델 `f_active(protrusion_pdf, engage_depth)`**~~ ✅ 9/9 완료(software/BACKLOG.md S29, `sim/tier2_physics/disk_active_grit_fraction.py`, 커밋 cb2db15)
   - 무엇을: 디스크 돌출 높이 PDF(균일 40–90 µm / 단일 높이 / 측정 히스토그램)와 최고 그릿 기준 침투
     깊이 δ → f_a = P(h > h_max − δ), N_eff = f_a·N_total을 conditioner-disk-pad-cutting-model의 그릿 밀도
     항에 곱하는 훅. δ는 캘리브레이션 파라미터.
   - 근거 노트: knowledge/equipment/cvd-diamond-disk-patterned-grit-array.md §2 verify, §3.2, §6.1, §8.
   - 검증 문헌값: 종래 f_a 25~30%(US8657652 Fig.6), "<10%"(Tsai 2014), CVD 단일 높이 → 1.0(Kim & Kang 2011),
     RCADD/CDD 유효 팁 비 2.8배(484/10,000 vs 432/25,000).
5. **절삭율 결합계수 `CR(N, N_eff, Rpk)`** (우선순위: 중, Cal-1 입력)
   - 무엇을: `CR = CR_ref·(N/N_ref)^(-0.53)·(Rpk/Rpk_ref)^0.85` 를 밀도/봉우리높이 기반 절삭율
     1차 근사로 채택. 활성 그릿 수(N_eff, 항목4의 f_active 출력)와 Rpk는 절삭율에 독립적으로
     기여하는 두 축이므로(§3의 잔차 1.75배), 단일 스칼라로 축약하지 말고 두 입력을 모두 받는
     인터페이스로 설계할 것.
   - 근거 노트: knowledge/materials/disk-design-cutrate-asperity-regeneration-model.md §2–3.
   - 검증 문헌값: Kwon 2013 CR 37/23/19 µm/h(17k/40k/60k, 2h); Tsai 2014 N_eff proxy 비 1.12배
     vs PCR 비 1.96배(24→47 µm/h, 1h).
   - 추가: population balance(disk-conditioner 형제 코드)의 그릿크기 입력에 Ring σ∝D_grit(지수1)
     대신 D^0.57(surface finish 대리, 지수 오더만 차용)을 기본값 후보로 고려 — 같은 노트 §4.
