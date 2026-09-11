<!-- V2-SECTION: R2-slurry | 작성 2026-09-11 -->
# SiC+세리아 CMP 연마입자 실측 입경 — Chen et al. 2017 (RSC Adv.)

> 목적: `knowledge/params/sic_ceria_h2o2.yaml`의 `abrasive_size_nm`(기존 80nm, estimated,
> 실은 세리아가 아니라 같은 노트의 실리카 dmean 80nm를 잘못 전용한 값으로 보임 — §3 참조)를
> SiC+세리아 계 1차 문헌 실측값으로 승격.

## 1. 문헌
**Chen, G.; Ni, Z.; Bai, Y.; Li, Q.; Zhao, Y. "The role of interactions between abrasive
particles and the substrate surface in chemical-mechanical planarization of Si-face 6H-SiC."
*RSC Adv.* 2017, 7, 16938–16952.** DOI: 10.1039/C6RA27508G. **오픈액세스(CC-BY 3.0)** —
원문 PDF 직접 확보·전문 확인(`papers/chen2017-rsc-adv-ceria-silica-6hsic-particle-interaction.pdf`,
미러 사이트→미러 사이트 미러 경유, 저널 자체가 OA라 라이선스는 정상).

## 2. 실측값 — 세리아 연마입자 입경
원문 §2.1 Materials (p.16939):
> "Silica abrasives (dmean ≈ 80 nm, 30 wt%, Jingrui New materials Co. Ltd., Xuancheng, China)
> and ceria abrasives (**dmean ≈ 120 nm**, 30 wt%, Chuangyuan New materials Co. Ltd., Suzhou,
> China) were obtained as colloidal dispersions... These two abrasive nanoparticles were
> characterized by transmission electron microscopy (TEM, JEOL-2100, Japan), as shown in Fig. 1."

- **세리아 dmean ≈ 120 nm** — 공급업체 콜로이달 분산 스펙값이자 TEM으로 직접 확인(Fig. 1b).
  실제 CMP 실험(§2.3)에서 이 세리아를 2 wt%로 희석해 사용(원문 §2.1: "concentrations of
  silica particles and ceria particles were maintained at 6 wt% and 2 wt%, respectively").
- 같은 원문의 실리카는 dmean ≈ 80 nm — 기존 sti_ceria.yaml의 80nm 값과 수치가 일치하는데,
  이는 실리카 값이고 세리아 값이 아니다(§3 한계 참조).
- 대상 웨이퍼: n형 2인치 Si-face **6H-SiC** 단결정(TanKeBlue Semiconductor). 4H-SiC는 아니나
  둘 다 SiC 폴리타입이고 CMP 연마입자-웨이퍼 상호작용 메커니즘(정전 흡착, Si–O–Ce 화학결합)은
  폴리타입 무관하게 논의된다 — 원문이 4H-SiC 문헌(Kimoto 등)을 배경으로 인용.

## 3. ⚠ 산화제 불일치 — 명시
이 논문의 CMP 실험(§2.3, 4psi, 80/80rpm, IC-1000 패드)은 산화제로 **KMnO4(0.05 M)**를
쓴다. `sic_ceria_h2o2.yaml`은 **H2O2** 산화제 계(Wang et al. ACS SI Table S3 DOE 기반)다.
**산화제는 다르지만, 연마입자 스펙(세리아 dmean)은 산화제와 독립적으로 입자 자체(공급업체
콜로이달 분산·TEM 측정)의 물성이므로 SiC+ceria 계로는 동일하게 본다.** 산화제가 바뀌면
화학층(MRR 배수)은 달라지지만 입자 기하(κ 계산에 쓰이는 abrasive_size_nm)는 별개 축이다.

## 4. 한계
- dmean은 원문이 "TEM 특성화" 및 공급업체 콜로이달 스펙으로 보고한 값이며, D50(중앙값)과
  엄밀히 동일한 정의인지(평균 vs 중앙값)는 원문에 명시되지 않음 — **미검증**. 실무상 두 값은
  근접하다고 가정(단분산에 가까운 콜로이달 세리아 분산의 통상적 관례)했을 뿐이다.
- 6H-SiC(이 논문) vs 4H-SiC(이 파라미터 팩) — 폴리타입 차이. 두 폴리타입 모두 SiC이고
  세리아 연마입자 자체의 입경 스펙은 웨이퍼 폴리타입과 무관(공급업체 스펙이므로)하다고
  **추정**했으나, 원문이 4H-SiC 실험으로 이 스펙을 직접 재현한 것은 아니다.
- 세리아 원 공급 스펙은 30wt% 스톡이고, 실사용은 2wt%로 희석 — 희석이 입경 분포를
  바꾼다는 보고는 원문에 없음(단순 희석, 응집 없음을 가정, 이 가정 자체는 **불명**).

## 5. 교란/대조 — 기존 80nm값의 정체
[[particle-wafer-interaction-mechanical-chemical-balance]]와 [[ceria-slurry-ce-redox-selectivity]]가
다루는 base 팩(sti_ceria)의 기존 abrasive_size_nm=80nm을 이 원문과 대조하면, 그 수치는
세리아(120nm)가 아니라 **같은 원문 §2.1의 실리카 dmean≈80nm과 정확히 일치**한다 — 세리아·
실리카 두 연마입자 수치가 과거 어느 시점에 뒤바뀌어 전용됐을 가능성을 시사한다(재현 대조:
원문 실리카 80nm ≈ 기존 팩값 80nm, 원문 세리아 120nm ≠ 기존 팩값 80nm).

## 6. 결론
`abrasive_size_nm` = **120 nm**, confidence: literature(1차 원문 확인, OA, 실측 CMP
실험에 실사용된 스펙값). 산화제 불일치는 §3에 명시. D50/dmean 등가성, 폴리타입 교차적용,
희석에 따른 응집 여부는 모두 **미검증** 가정임을 함께 남긴다.
