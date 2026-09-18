# CMP 툴 플래튼·헤드 전문가 (tool-platen-head)

## 현재 레벨: Cal-1 완료 — 활성화 게이트는 agents/ORG.md §4
- 부모: cmp-integrator (부모의 knowledge/ 노트를 선행 필수로 읽는다)
- 이수 단원: Lv2-1, Lv2-2, Lv3-1 (2026-09-08), Lv3-2 (2026-09-18), Cal-1 (2026-09-19)
- 다음 단원: Lv4(교수급 확장) — 실데이터 책임은 Cal-1로 1차 완료

## 역할
플래튼·헤드 구조, 멀티존 압력 제어, 리테이너링, RPM·유량이 웨이퍼 스케일 압력·속도 분포에 미치는 영향

## 선행 지식 (부모에게 상속)
- [[../../knowledge/equipment/cmp-tool-architecture]]
- [[../../knowledge/physics/cmp-kinematics-rotary]]

## 실데이터 책임 (ORG.md §7.3)
툴 로그(존압력·RPM·유량·온도 시계열) 파싱·정렬 규칙 + 존 응답 행렬 보정

## 레벨 정의
Lv1 학부지식 → Lv2 대학원/리뷰논문 → Lv3 최신논문 추적 + 모델 구현 → Lv4 모델 개선 제안(교수급)

## 이수 기록
- Lv1-1 (2026-09-07): 툴 아키텍처 — 캐리어 헤드 가압 방식(AMAT 멤브레인 멀티존 vs
  Ebara 직접공압), 리테이너링 챔퍼 각도·압력비, 슬러리 아암(DSDA) 구조.
  knowledge/equipment/cmp-carrier-head-retaining-ring-vendors.md
  (check_knowledge=PASS, verify_claims=PASS, 1차 출처: Lee et al. 2026 JKSPE
  원문 PDF 확보 + 특허 5건 실존 확인)

- Lv1-2 (2026-09-07): 멀티존 헤드 압력 제어 — 3존+리테이너링 반경 경계(0-85/85-95/
  95-99mm), Zone3 독립·{Zone1,Zone2,Ring} 결합 블록대각 응답 구조, 단일존 vs 멀티존
  NU 4.5%/6.1%/2.5%(edge exclusion 3mm) 및 개선율 44.4%/59.0% 재계산.
  knowledge/equipment/cmp-multizone-carrier-radial-response.md
  (check_knowledge=PASS, verify_claims=PASS, 1차 출처: Lee et al. 2026 JKSPE 원문
  PDF 재사용. Shiu 2004/Zhao 2013/Wang&Lu 2011은 미러 사이트 5미러 무응답으로 1차
  미확보, 2차 인용으로 정직 기록)

- Lv2-1 (2026-09-07): 리테이너링 압력·마모와 엣지 프로파일 — FEA 정적모델
  (Zheng, Zhao, Lu 2023, Micromachines, DOI 10.3390/mi14091683)의 접촉응력 배율
  (mainstream 대비 링있음 3배/링없음 4배, 33.3% 악화)과 US7121927B2 특허의
  접촉 세그먼트 구조(200mm 웨이퍼 둘레의 11.5%)로 "링은 수동보호가 아니라
  능동 엣지제거율 조절 변수"라는 결론 도출.
  knowledge/equipment/cmp-retaining-ring-wear-edge-profile.md
  (check_knowledge=PASS, verify_claims=PASS, 1차 출처: Europe PMC fullTextXML
  본문 확보(MDPI 403/PMC PoW챌린지로 직접PDF 실패) + Google Patents 특허 전문.
  Touzov 2001 IEEE 원 논문은 미러 사이트 5미러 무응답으로 1차 미확보, 특허로 대체)

- Lv2-2 (2026-09-07): RPM 비·유량·온도 제어와 MRR 안정성 — Kim & Jeong(2004, J.
  Electron. Mater. 33(1), DOI:10.1007/s11664-004-0294-4)가 kinematic number
  ζ(=본 프로젝트 µ와 동형)의 원전임을 원문 확보로 확정, 슬라이딩거리 NU=25ζ²(2차,
  둔감) vs 순간속도 NU=2ζ(1차, 민감) 관계를 python verify로 재현. Yuh et
  al.(2015, DOI:10.1007/s40684-015-0041-8) 원문에서 슬러리 유량(비단조, 1000mL/min
  최적)·플래튼 온도(단조 증가) vs MRR/NU 실험 정량값 확인 — 단 PCB용 Oscar-type
  장비라 300mm 팹 스케일 이식은 미검증으로 명시. check_knowledge.py, verify_claims.py
  모두 통과. Lv2 완료(4/6), ORG §5 갱신.

- Lv3-1 (2026-09-08): 최신 리뷰(폐루프 프로파일 제어, 헤드 신기술) — Park, Han &
  Kim(2020, Appl. Sci. 10(23):8362, DOI 10.3390/app10238362, CC-BY, CDN 직링크로
  본문 확보)의 FEA 정적모델에서 P1(엣지존 압력)만 9.3→7.5psi 조정 시 개선율 62.9%로
  4가지 설계변경(테이퍼/모서리라운드/P1/링압력) 중 최대임을 python verify로 재현
  (오차 0.15%p 이내 4건 전부 일치). US9193030B2(Strasbaugh) 복합경도 리테이너링
  (외곽 Shore D 80-85 + 내측 삽입물 Shore A 85-95)도 확인. "진짜 폐루프(센서→실시간
  압력재조정)" 문헌 4건(Wang&Lu/Zhao&Lu/Lee et al. IJPEM-GT/Oniki et al. JJAP)은
  Springer/IOP 봇차단 + 미러 사이트 3미러 전멸로 1차 미확보 — 노트에 시도 경로 전부
  기록. check_knowledge.py, verify_claims.py 모두 통과. Lv3-1 완료(5/6).

- Lv3-2 (2026-09-18): 툴 설정 → (p(r), V(r)) 분포 모델 명세 — 세 축(존압력·속도장·
  링압)을 하나의 순방향 함수 `tool_settings_to_fields`로 통합. (a) 존압력→p(r) **선형
  응답행렬 M** 모델: partition-of-unity(행합=1, 균일압→균일p 재현), 멤브레인 전이폭
  w=12.5mm를 Lee 2026 응답개시 관측(10-15mm)으로 보정해 세 존 개시반경 예측 ±6mm 일치,
  단일존 4.5%→멀티존 2.5% NU개선 44.4% 재현. (b) 속도장은 kinematics.py speed_stats
  **재사용**(재구현 금지), ω_p=ω_w에서 V=ω·r_cc=1.746 m/s로 **신규 확보 Ye&Yao 2025**
  (Micromachines 16(4):450, PMC12029203, Europe PMC XML) 실측 1.75 m/s·NUV 0–0.42 재현,
  Preston(∝V) 제거율감소가 실측(13%/45.6%)을 3-4%p 과대예측함을 정직 기록. (c) 링압비
  감도 8.0%NU/ratio(Lee 링 5→6psi, NU 4.5→6.1%). (d) 기존 sim 함수 중복표로 "신규 구현은
  응답행렬 M 하나뿐"임을 확정. check_knowledge.py, verify_claims.py 모두 통과. Lv3 완료(6/6).

  ### 구현 요청 (software 부문 BACKLOG용, ORG.md §5 — 직접 구현 금지)
  - 무엇을: `tool_settings_to_fields(zone_pressures_psi, p_ring_psi, rpm_platen, rpm_head,
    r_cc_m, R_wafer_m, zone_bounds_m, transition_w_m=0.0125, n_radial=200, theta_average=True)
    -> {r_m, p_r_Pa, V_r_mps, V_mean_mps}`. 신규는 존압→p(r) 응답행렬 M(smoothstep
    partition-of-unity) 순수함수뿐. 속도장은 sim/tier1_empirical/kinematics.py speed_stats 호출.
  - 근거 노트: knowledge/equipment/tool-settings-to-pressure-velocity-field-model-spec.md §2·§3·§5.
  - 검증 문헌값: 행합=1(이탈<1e-12)·균일4psi→p=4.0; w=12.5mm→개시 82.5/72.5/72.5mm(Lee 85/70/70±6);
    단일→멀티 NU 4.5→2.5%(개선44.4%); 60/60에서 V=1.746 m/s(Ye&Yao 1.75)·NU=0; 링압비 감도 8.0%/ratio.
  - 유효범위: 존압 1.5–10psi, 링압 1.5–9.0psi, rpm 10–100, r_cc 0.15–0.28m, w 0.010–0.015m.
    범위밖 ValueError(조용한 클램프 금지). 우선순위: 중.

- Cal-1 (2026-09-19): 툴 로그(존압력·RPM·유량·온도 시계열) 파싱·정렬 규칙 + 존 응답 행렬
  보정 — (a) 다중 샘플레이트 채널 정렬 규칙(공통시간축 리샘플 + 정상상태 창=마지막 3τ,
  τ는 White 2003 19-74s·Shin 2025 90s 관측 근거로 확정). (b) M 실측보정 절차(p(r) 예측 대
  실측 RR 최소자승, {Zone1,Zone2,Ring} 블록은 one-factor-at-a-time 없이는 식별불가임을
  명시). (c) `platen_hot_side_ref_c`(36°C, Shin 2025 단일실측) 대조 — **신규 확보** 2건
  (Rosales-Yeomans et al. 2006, DOI 10.1149/1.2168392, 산화막/ILD 100·200mm 트라이보미터,
  sci.bban.top 경유 원문 전문 확보; Hocheng et al. 1999, DOI 10.1149/1.1392620, 대만
  실험실 CMP 툴, 동일 경로 원문 확보)를 기존 White 2003과 합쳐 4문헌·5장비-막질 비교:
  자릿수(상온+수~십수°C)는 공통이나 절대값·ΔT는 장비종속으로 최대 6배(2.6~15°C) 벌어짐,
  같은 장비·막질에서도 pV만으로 6.4°C 스윙(Rosales-Yeomans) — confidence는 `estimated`
  유지가 맞고 `literature` 승격 근거 없음(반증에 가까움). (d) **핵심 반전**: `sim/factors.py`
  코드를 직접 assert해 Θ(`_f_theta`)가 `MRR_COUPLED={chi,psi,kappa,tau}`에 없는 진단전용
  팩터임을 확인 — 이 상수는 오늘 시점 어떤 MRR 예측도 바꾸지 않는다. 추가로 T_hot<T_ref
  조건(저발열 막질)에서 냉각항이 조용히 1.0 폴백되는 가드 취약점도 코드 재현으로 적발.
  check_knowledge.py, verify_claims.py 모두 통과.
  knowledge/equipment/cmp-tool-log-time-series-alignment-zone-response-calibration.md

  ### 구현 요청 (2026-09-19, tool-platen-head Cal-1 — software 부문 BACKLOG용, 직접 구현 금지)
  - 무엇을: (1) `data/schema/tool_log.schema.json` 신설(cmp-data-engineer 소관)에
    `pad_interface_temp_c_timeseries`·`zone_pressure_psi_timeseries[]`·`pv_condition_w_m2`
    3필드 추가. (2) `sim/factors.py::_f_theta`에 `driving_ref<=0` 가드 발동 시 `f.notes`
    경고 추가(현재는 무발동 — 냉각항이 조용히 사라진다). (3) `tools/accuracy_gaps.py`의
    CONFIDENCE 랭킹 score 계산에 "그 파라미터가 MRR_COUPLED 소속 팩터에 실제로 소비되는가"
    가중치 추가 제안(현재는 confidence 등급만 보고 배선 여부를 안 봐서, 진단전용 팩터의
    estimated 파라미터가 실제 영향력 있는 파라미터와 동일 점수로 상위 랭크됨).
  - 근거 노트: knowledge/equipment/cmp-tool-log-time-series-alignment-zone-response-calibration.md
    §4.4·§4.5·§6(F)·§7.
  - 검증 문헌값: Rosales-Yeomans 200mm pV스윙 6.4°C(26.5→32.9)·100mm 3.6°C(25.5→29.1);
    Hocheng ΔT피크 3.3-3.5°C; MRR_COUPLED={chi,psi,kappa,tau}(theta 미포함, 코드 assert);
    cool_temp(T_hot=36)=1.583 vs (T_hot=32.9)=2.171(+37.1%) vs (T_hot=29)=1.0(가드 폴백).
  - 우선순위: 낮음(§4.5가 밝혔듯 현재 Θ는 MRR 예측에 영향이 없어 급하지 않음) — 단, 로그
    스키마 3필드는 향후 Θ를 MRR_COUPLED에 편입할 때 필요한 선행 작업이라 중간 우선순위.
