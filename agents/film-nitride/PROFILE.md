# 나이트라이드 CMP 전문가 (film-nitride)

## 현재 레벨: Lv3 진행 — 활성화 게이트는 agents/ORG.md §4
- 부모: cmp-integrator (부모의 knowledge/ 노트를 선행 필수로 읽는다)
- 이수 단원: Lv3-1
- 다음 단원: Lv3-2

## 역할
SiN 막의 CMP 및 정지층 역할 — STI 선택비, 하드마스크 제거

## 선행 지식 (부모에게 상속)
- [[../../knowledge/cmp/slurry-components-overview]]

## 실데이터 책임 (ORG.md §7.3)
나이트라이드 실데이터 스키마 + 정지층 손실 보정 파라미터

## 레벨 정의
Lv1 학부지식 → Lv2 대학원/리뷰논문 → Lv3 최신논문 추적 + 모델 구현 → Lv4 모델 개선 제안(교수급)

## 이수 기록
- **Lv1-1** SiN 막 종류(LPCVD/PECVD)와 물성, CMP 제거 난이도 — 2026-09-10
  노트: [[../../knowledge/materials/film-nitride-lpcvd-pecvd-properties-cmp]]
  출처 7건(1차 5건, 원문 완독 4건: Dandu 2009 JES, Srinivasan 2015 리뷰, Mariscal 2020 JSS, Gan 2018 Surfaces; +Nejadriahi 2020 OE OA).
  verify_claims ✓(출처 7건 실존·코드 3블록 PASS)·check_knowledge ✓.
  핵심: LPCVD Si₃N₄(무수소·고밀도·22.5 GPa) > PECVD SiNₓ:H(수소 10–19 at%·13.6 GPa) 경도서열,
  제거는 가수분해→SiO₂→기계제거(chemically-limited), 선택비는 Eₐ 아닌 전지수인자 A(~115배)가 지배.
- **Lv1-2** 나이트라이드 정지층 메커니즘: 세리아 슬러리 선택비 화학 — 2026-09-10
  노트: [[../../knowledge/materials/film-nitride-selectivity-ceria-chemistry]]
  출처 5건(1차 4건, 원문 완독: Dandu 2009 JES, Netzband&Dunn 2020 JSS, Hwang 2026 Polymers, Srinivasan 2015 리뷰;
  Dandu 2011은 Cloudflare 봉쇄로 원문 미확보·2차 인용).
  verify_claims ✓(출처 5건 실존·코드 2블록 PASS)·check_knowledge ✓.
  핵심: 선택비는 3단 위계 — 무첨가(4.4:1, 가수분해속도차만) < PAA 분산제(4.7–8:1) < 사이트특이적 사이클릭아민
  0.05%(117–290:1). 두 자릿수 도약의 원인은 흡착 포화 비대칭(나이트라이드는 0.1%부터 2.4 mg/g로 조기포화·비가역,
  실리카는 1.3→8.2 mg/g로 계속 증가·가역) — 저농도에서 나이트라이드만 완전 차단되고 산화막은 세리아가 계속 접근
  가능해 선택비가 급등. Ce³⁺/Ce⁴⁺ 산화상태 튜닝(Netzband 2020)은 산화막·나이트라이드 둘 다 빨라지는 "배율 조절"이라
  선택비 개선이 ~2–3배에 그쳐 사이트차단(스위치, ~100배 이상)과 자릿수가 다름.

- **Lv2-1** STI 나이트라이드 손실·디싱과 공정 윈도우 — 2026-09-11
  노트: [[../../knowledge/cmp/sti-nitride-loss-erosion-overpolish-window]]
  출처 6건(1차 4건: Lee 2002·Johnson 2009 MIT 학위논문 원문, Dandu 2009·Mariscal 2020; +Srinivasan 2015 리뷰·Urban 2016 벤더).
  verify_claims ✓(DOI 3건 실존·코드 4블록 PASS)·check_knowledge ✓.
  핵심: 형제 film-oxide 노트가 디싱(D_ss)으로 푼 Lee 2002를 **나이트라이드 침식 E(t)** 각도로 상보. 정지의 실체 = 나이트라이드
  손실 예산(200 Å, Lee p.185). 정상상태 손실률 K_ss = K/(1+ρ(s−1))는 블랭킷율 K/s보다 큼(압력집중). 선택비의 값어치는 디싱
  감소가 아니라(D_ss↑) 예산 대비 오버폴리시 창 확대 — s=10→100에서 창 37.8→304 s(8배). 블랭킷 선택비 100+여도 패턴 유효선택비
  s_eff≈3(Lee p.121 "세리아 HSS도 통상공정 수준 침식"). 저밀도서 K_ss→K_nit/ρ("좁은 나이트라이드가 손실 급소"). 자기정지
  슬러리(Dandu Fig.14: 30 Å 포화)는 선형 K_ss 누적을 깨 창 무한 — 선택비보다 근본적 보호.

- **Lv2-2** 나이트라이드 직접 CMP: 하드마스크·게이트 응용 — 2026-09-11
  노트: [[../../knowledge/materials/film-nitride-direct-cmp-hardmask-gate]]
  출처 4건(1차 3건: Alety 2017 ECS JSS 원문 완독, US8895444B2·US9558959B2 특허 명세서 확인; Dandu 2010 JCIS는 DOI만
  확인·원문 미확보 2차 인용). verify_claims ✓(출처 4건 실존·코드 2블록 PASS)·check_knowledge ✓.
  핵심: Lv1/Lv2-1이 "SiN이 멈추는 막"이었다면 이 단원은 정반대 — SAC(Reverse STI)·FinFET 핀캡 하드마스크에서
  나이트라이드를 실제로 깎아 없앤다. Ce³⁺ 첨가(양이온 산화촉매, 산화질화물 경유)로 나이트라이드 RR을 10→300
  nm/min(30배)까지 올리고 선택비 방향을 옥사이드 우위→나이트라이드 우위로 뒤집을 수 있음(Alety 2017). 카르복실기
  첨가제+음이온 연마재(전하반발, US9558959B2)로도 SiN:TEOS 최대 97:1 역선택비 달성 가능하나 관능기 구조에 따라
  역효과(말론산)도 있음. FinFET 핀캡 제거는 웨트/드라이 에치 대신 3단계 CMP(옥사이드씨닝→stop-on-nitride→
  stop-on-silicon)로 대체(US8895444B2) — 한 공정 체인 안에서 나이트라이드가 "정지 목표"에서 "제거 목표"로 역할이
  바뀜. 저속(첨가제 없는) 레짐은 화학-제한·비-Prestonian(Lv1-1 Mariscal)이지만 Ce³⁺ 고속 레짐은 압력에 선형
  (Prestonian)으로 반응 — 레짐이 Kp의 압력의존성 자체를 바꿈.

- **Lv3-1** 최신 리뷰: 나이트라이드 선택비 첨가제, 3D NAND 응용 — 2026-09-14
  노트: [[../../knowledge/materials/film-nitride-additive-selectivity-3dnand-review]]
  출처 5건(1차 4건, 원문 완독 3건: America 2004 ESSL·Penta 2013 Colloids Surf A·Praveen 2014 MEE; Zhao 2025 Appl. Surf. Sci.는
  2025-11 게재 유료·미러 사이트 미등재로 초록 기반 E5; 아미노산 리뷰 2025 Surf. Sci. Technol.은 Springer 챌린지로 전문 미확보·정성 프레이밍만).
  verify_claims ✓(출처 5건 실존·코드 5블록 PASS)·check_knowledge ✓.
  핵심: 첨가제 SiN 억제는 (농도)×(pH 창) **이중 스위치** — 억제는 첨가제 아민이 양성자화된 pH에서만 켜짐(f=1/(1+10^(pH−pKa))).
  이것이 피콜린산 겉모순 해소(pH5 pKa5.3 ON→SiN~1 nm/min vs pH9.6 OFF→65 nm/min)이자 Lv1-2 흡착포화(농도스위치)의 pH축 보완.
  America 2004 Table I: 프롤린이 SiN 2·옥사이드 456 nm/min로 선택비 228:1 최고(아르기닌·라이신은 옥사이드까지 억제→STI 부적합).
  Praveen 2014: 억제는 첨가제×연마재 조합 성질 — L-proline은 La-무함유 세리아에서만 sel 3→40, L-glutamic은 세리아 3종 모두 견고.
  (b) 역선택비/촉진: 고pH(America pH11서 최소대비 ~10배)·La-세리아+프롤린 무력화; 적극적 역선택비 화학은 Lv2-2 참조(중복 회피).
  (c) 3D NAND: 요구 SiO₂:Si₃N₄ ≈30:1(STI 블랭킷 100–290보다 낮음), Zhao 2025 초록 SiO₂ 3606.1·Si₃N₄ 101.6 Å/min→35.49 —
  적층당 두꺼운 SiN이 큰 손실예산을 줘 자기정지 아닌 "예산관리형" 레짐.

## 구현 요청
- **[Tier2] 첨가제 억제항에 pKa 기반 pH 게이트 추가**
  - 무엇을: 기존 [Tier2] 첨가제 포화-스위치 모델(Langmuir θ=Kc/(1+Kc))에 **양성자화 게이트 f_prot=1/(1+10^(pH−pKa))** 를
    곱해 RR_nitride ∝ (1−θ·f_prot)로 둔다. 같은 첨가제(피콜린산)가 pH 5는 억제·pH 9.6은 무력이라 pH 무시 모델은 부호를 틀린다.
    또 선택비 파라미터에 **연마재 La/순도 태그**를 결합(L-proline은 La-세리아서 무력, L-glutamic은 견고).
  - 근거노트: [[../../knowledge/materials/film-nitride-additive-selectivity-3dnand-review]] §3·§4·§5
  - 검증 문헌값: 피콜린산 pKa≈5.3(pH창 ≤6)·프롤린 pKa≈10.6(pH창 ≤11)(Penta 2013, DOI 10.1016/j.colsurfa.2013.03.046);
    소요농도 피콜린 0.1 wt%·프롤린 2 wt%; America 2004(DOI 10.1149/1.1817870) Table I 프롤린 456/2=228; Praveen 2014
    (DOI 10.1016/j.mee.2013.10.004) La 24–31 wt% 상용세리아서 프롤린 무력·L-glutamic SiN<3 nm/min.
  - 우선순위: 중 (Lv1-2 포화-스위치 모델 확장. pH 축이 빠지면 억제 방향을 틀림).
- **[Tier2] 3D NAND ONON 정지 파라미터 세트(예산관리형)**
  - 무엇을: 3D NAND는 STI 자기정지(<1 nm/min)와 달리 요구선택비 ≈30:1·유한 SiN율(~100 Å/min)을 허용하는 별도 프리셋.
    Lv2-1 손실예산 모델을 두꺼운 ONON(적층당 큰 예산)에 재사용하되 목표선택비만 낮춘 파라미터.
  - 근거노트: [[../../knowledge/materials/film-nitride-additive-selectivity-3dnand-review]] §6
  - 검증 문헌값(Zhao 2025, DOI 10.1016/j.apsusc.2025.163978, 초록 E5): 요구 30:1, 실측 SiO₂ 3606.1·Si₃N₄ 101.6 Å/min·sel 35.49.
  - 우선순위: 낮음 (Zh25 원문 확보 후 입경·압력 조건 보강 필요).

- **[Tier2] STI Phase 2 나이트라이드 침식식 E(t) + 손실 예산 판정**
  - 무엇을: Lee 2002 Phase 2 폐형해에 **침식 E(t) = K_ss(t−t_n) + 과도항**(식 2.56)과 밀도의존 손실률 K_ss(ρ)=K/(1+ρ(s−1))·
    K_n1(ρ)를 출력하고, 소자 판정을 **E(t) < E_max(예: 200 Å)** 로 하는 판정기. 형제 film-oxide 구현요청(D_ss·touch-down)의
    나이트라이드측 짝. 오버폴리시 창 Δt_op = argmax{ E(t)<E_max } 도 함께.
  - 근거노트: [[../../knowledge/cmp/sti-nitride-loss-erosion-overpolish-window]] §4·§6
  - 검증 문헌값(Lee 2002, hdl 1721.1/29907): 표 3.10 세리아 HSS 지수적합 K_ss=4784·exp(−ρ/0.40)·K_n1=11573·exp(−ρ/0.28) Å/min,
    표 3.9 실측(ρ=0.5/0.7/0.9 → K_ss 1367/903/465, K_n1 1902/903/465 Å/min); 예산 200 Å에서 s=10 창 37.8 s·s=100 창 304 s.
  - 우선순위: 중 (형제 STI Phase 2 모듈과 동시 구현. 노트 §7 [A][B][C] verify가 계산식 원본).
- **[Tier2] 자기정지(포화형) 침식항**
  - 무엇을: Lee의 선형 K_ss 누적은 자기정지 슬러리를 못 담는다. 침식을 E(t)=E_sat·(1−exp(−(t−t_n)/τ_stop)) 형태의 포화항으로
    두면 "노출 후 30 Å만 잃고 멈춤"(Dandu Fig.14)·임계압력형(Nojo)을 재현할 수 있다. 선택비 손잡이와 별개 모드로.
  - 근거노트: [[../../knowledge/cmp/sti-nitride-loss-erosion-overpolish-window]] §6 자기정지, §7 [D]
  - 검증 문헌값(Dandu 2009, DOI 10.1149/1.3230624): 나이트라이드 30 s에 ~3 nm(≈30 Å) 후 200 s까지 0 → E_sat≈30 Å·τ_stop~10 s.
    임계압력 P_th≈70 kPa(Nojo, Lee 2002 Fig.3.15, 2차).
  - 우선순위: 낮음 (E_sat·τ_stop·P_th 문헌값이 정성 서술 근사라 추가 조사 필요. 위 [Tier2] 판정기 완성 후 착수).

- **[Tier2] SiN 화학-제한 제거율 모델(수정 Langmuir-Hinshelwood)**
  - 무엇을: 나이트라이드 RR을 단순 Preston $K_p PV$가 아니라 화학항(가수분해 사이트 커버리지)·기계항 결합형으로.
    Mariscal 2020 형태 $RR = f(A, E_a, T_p)_{chem} \times g(P,V,\mu)_{mech}$.
  - 근거노트: [[../../knowledge/materials/film-nitride-lpcvd-pecvd-properties-cmp]] §4.3
  - 검증 문헌값(Mariscal 2020 Table I, DOI 10.1149/2162-8777/ab89bc): SiO₂ Eₐ=1.40 eV·A=9.77e-4,
    Si₃N₄ Eₐ=1.47 eV·A=8.47e-6 mol·m⁻²·s⁻¹; 블랭킷 선택비 최대 101:1. Dandu 2009 나이트라이드 2–3 nm/min·옥사이드 350 nm/min.
  - 우선순위: 중 (Lv2 STI 정지층 손실 모델의 입력으로 필요. Lv1-2 선택비 화학 학습 후 착수 권장)
- **[Tier2] 첨가제 포화-스위치 선택비 모델**
  - 무엇을: 위 L-H 연속함수는 사이트특이적 첨가제(사이클릭아민 등)의 "임계농도 이하=미차단, 이상=완전차단" 상 전이형
    거동을 못 담는다. 나이트라이드 흡착량을 첨가제 농도의 포화형 함수(예: Langmuir 흡착등온 θ=Kc/(1+Kc))로 두고,
    RR_nitride ∝ (1−θ)로 스케일하는 항을 추가하면 §4의 "0.05%부터 급락" 거동을 재현할 수 있을 것.
  - 근거노트: [[../../knowledge/materials/film-nitride-selectivity-ceria-chemistry]] §4, §9-2
  - 검증 문헌값(Dandu 2009, DOI 10.1149/1.3230624): 나이트라이드 흡착 0.1 wt% 이상에서 2.4 mg/g로 포화,
    실리카는 0.05→1 wt%에서 1.3→8.2 mg/g로 비포화 증가. 선택비 4.4:1(무첨가)→117–290:1(0.05% 첨가제).
  - 우선순위: 낮음 (Lv2-1 STI 오버폴리시 창 모델과 결합 시 필요. 흡착등온 계수(K)는 문헌에 명시 안 돼 추가 조사 필요).
