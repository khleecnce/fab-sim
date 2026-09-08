# 옥사이드 CMP 전문가 (film-oxide)

## 현재 레벨: Lv2 진행 중 (3/6) — 활성화 게이트는 agents/ORG.md §4
- 부모: cmp-integrator (부모의 knowledge/ 노트를 선행 필수로 읽는다)
- 이수 단원: Lv1-1, Lv1-2 (2026-09-08), Lv2-1 (2026-09-09)
- 다음 단원: Lv2-2 STI CMP: 세리아 슬러리 고선택비, 나이트라이드 정지, 디싱

## 역할
TEOS·HDP·SOD 등 SiO2 막의 CMP — ILD 평탄화·STI. 기계 제거 지배, 실리카/세리아 슬러리

## 선행 지식 (부모에게 상속)
- [[../../knowledge/cmp/preston-luo-dornfeld-mrr]]
- [[../../knowledge/cmp/slurry-components-overview]]

## 실데이터 책임 (ORG.md §7.3)
옥사이드 실데이터(막종류·MRR·WIWNU·디싱) 스키마 + 보정 파라미터(Kp_oxide, 선택비) 정의

## 레벨 정의
Lv1 학부지식 → Lv2 대학원/리뷰논문 → Lv3 최신논문 추적 + 모델 구현 → Lv4 모델 개선 제안(교수급)

## 이수 기록
- 2026-09-08 Lv1-1 이수: knowledge/materials/film-oxide-teos-hdp-bpsg-sod-density-hardness.md
  (Wei 2010 IEEE WMED DOI 10.1109/wmed.2010.5453755, Cook 1990 J.Non-Cryst.Solids DOI
  10.1016/0022-3093(90)90200-6, Zantye 2004 Mater.Sci.Eng.R DOI 10.1016/j.mser.2004.06.002)
  check_knowledge.py ✓ / verify_claims.py ✓
- 2026-09-08 Lv1-2 이수: knowledge/materials/film-oxide-hydration-layer-mechanism-cook-suratwala.md
  (Cook 1990 J.Non-Cryst.Solids DOI 10.1016/0022-3093(90)90200-6 §3.1 전체 완독,
  Suratwala et al. 2015 J.Am.Ceram.Soc DOI 10.1111/jace.13659 — Cook 이론모델의 25년 뒤
  SIMS 실측 검증. 핵심: Cook 확산깊이 계산(0.5-12nm)과 실측 폴리싱층(1-20nm) 오더 일치,
  Suratwala Bielby층(Ce기준 50nm)이 Cook 계산치보다 두꺼움 — 두 메커니즘 동일성 미검증.
  K/Ce 침투가 제거속도에 반대로 반응(확산 vs 화학반응 지배) 확인)
  check_knowledge.py ✓ / verify_claims.py ✓
- 2026-09-09 Lv2-1 이수: knowledge/cmp/ild-cmp-planarization-global-local-density.md
  (Ouma 1999 MIT Ph.D. thesis hdl.handle.net/1721.1/9704 — DSpace에서 원문 PDF 229쪽 확보,
  스캔본이라 1.4절·5장·7.1-7.2절을 페이지 이미지로 직접 읽음; 저널판 Ouma et al. 2002 IEEE TSM
  DOI 10.1109/66.999598, Stine et al. 1998 DOI 10.1109/66.661292는 Crossref 확인·본문 미확보;
  Xie & Boning MRS 2003 원문 PDF 확보. 핵심: 국소 단차는 선형 소멸(t=ρ·z1/K), 전역 단차
  TIR=Δρ·z1(Fig.7.1 6000Å 재현), PL은 타원 가중함수가 2/π로 떨어지는 폭(식 5.13/5.14 적분
  재현, IC1000 최대처짐 약 6µm 재현), PL은 서브패드 강성이 지배(표 7.2 속도 +4% vs 서브패드
  제거 +50%). 과제 문구의 exp(-x/PL) 단차감쇠는 원문에 없음을 명기)
  check_knowledge.py ✓ / verify_claims.py ✓

## 구현 요청
- **[P1] elliptic 가중커널 + Ouma 폐형해** — 무엇: `sim/tier1_empirical/pattern_density.py`에
  Ouma 식 5.11/5.12(반경 a=PL/2 원형하중 탄성변형, 완전 타원적분)를 2D 가중커널로 추가하고
  (`scipy.special.ellipe/ellipk` 사용 가능, 정규화 후 FFT 컨볼루션), 식 5.3 폐형해
  z(t)=z0−Kt/ρ0 (t<ρ0z1/K) / z0−z1−Kt+ρ0z1 를 up-area 두께 함수로 제공. 현재는 가우시안
  커널만 있음. 근거노트: knowledge/cmp/ild-cmp-planarization-global-local-density.md §5, §9[C].
  검증문헌값: w(a)/w(0)=2/π 정확히; IC1000(E=2.9e7 Pa, ν=1/3, a=2mm, q=7psi) w_max≈6µm
  (Ouma 1999 p.126); 표 5.3 타원필터 RMS 42Å@7.35mm는 데이터 없어 재현 불가(성질만).
- **[P2] TIR·최적 증착량 설계식** — 무엇: 레이아웃 밀도맵+PL → Δρ=ρmax−ρmin, TIR=Δρ·z1,
  t_lp=ρmax·z1/K, H0=H_ILD+z1(1+Δρ), t_opt=(ρmax+0.1)z1/K (Ouma 식 7.1-7.5) 유틸.
  근거노트: 같은 노트 §7. 검증문헌값: Δρ=0.8, z1=7500Å → TIR=6000Å (Fig.7.1);
  z1=0.7µm, H_ILD=0.8µm, Δρ=0.8 → H0=2.06µm(각주 범위 1.6-2.0µm 상단).
- **[P3] 서브패드 강성 → PL 매핑(경향만)** — 무엇: PL ∝ E_pad(Xie 2003) 경향과 표 7.2
  (적층 6.35 / 서브패드 없음 9.50 mm) 비율을 pad-mechanic 쪽 서브패드 강성 파라미터에 연결하는
  훅. 절대값 캘리브레이션은 특성화 마스크 실측 필요 — 미검증 표기 유지. 우선순위 낮음.
