# FabSim — AI-Native Semiconductor Process Simulation Platform

> **CMP(Chemical Mechanical Planarization) 통합 시뮬레이터에서 출발해 가상 fab으로 확장하는, "공정을 이해하는 AI + 모델 라이브러리" 플랫폼.**
> 수치해석 엔진이 아니라, 소재·장비·공정의 과학을 스스로 학습해 *왜 결함이 났고 무엇을 바꿔야 하는지* 답하는 도메인 전문가 에이전트 시스템을 목표로 합니다.

**Owner:** Keehwan Lee — CMP slurry materials engineer (3.7 yr), M.S.  ·  **Started:** 2026-08-31  ·  **Status:** Phase 0 → 1 진행 중

---

## 왜 이 프로젝트인가

| 영역 | 기존 강자 | 공백 |
|---|---|---|
| TCAD (device) | Synopsys Sentaurus, Silvaco | 정면승부 불가 — 장기 북극성으로만 |
| 공정 3D 모델링 | Coventor SEMulator3D (Lam) | 기하학 중심, **소재 화학이 약함** |
| **CMP 시뮬레이션** | **통합 상용툴 부재** — 학계 모델 산재 | ★ 슬러리+패드+디스크+공정변수 통합은 공백 |
| AI 공정 전문가 | 없음 | ★ 지식 학습 → 모델 설계 → 해석 루프 |

CMP는 수십억 달러 규모 소모품 시장(슬러리·패드·컨디셔너)에 통합 시뮬레이터가 없는 드문 공정입니다. 현직 슬러리 개발자로서 "무엇을 모델링해야 실무에 쓰이는가"를 압니다.

## 아키텍처 (4층)

```
L4  Fab Director Agent        공정 플로우 설계 · 에이전트 협업 · 통합 해석
L3  도메인 전문가 에이전트 ×5   각자 커리큘럼 + 지식베이스 + 검증시험 보유 (Lv1→Lv4 성장)
    slurry-chemist · pad-mechanic · disk-conditioner · tribologist · process-integrator
L2  시뮬레이션 엔진 (Python)    Tier1 경험식 → Tier2 물리모델 → Tier3 ML 서로게이트
L1  지식베이스 (knowledge/)     논문·교과서 요약을 상호링크된 md로 축적. 모든 주장에 출처.
```

**핵심 메커니즘 — 에이전트가 스스로 성장합니다.** 각 에이전트는 `agents/<name>/CURRICULUM.md`(학부→대학원→최신논문)를 따라 단원을 학습하고, `knowledge/`에 출처가 명시된 노트를 쓰고, `EXAMS.md`에 자기시험을 만들어 풀고, 수식은 Python으로 재현해 문헌값과 대조합니다. 지식이 쌓인 도메인만 `sim/`에 구현합니다 — **지식이 코드보다 앞선다.**

## 현재 상태 (2026-09-05)

| 지표 | 값 |
|---|---|
| 지식 노트 (출처 명시) | 21편 — `knowledge/{cmp,materials,physics,equipment}` |
| 시뮬레이션 모듈 | 24개 — `sim/{tier1_empirical,tier2_physics,integration}` |
| 회귀 테스트 | 83 passed (`pytest tests/`) |
| 에이전트 진도 | disk-conditioner 6/6 · pad-mechanic 6/6 · process-integrator 6/6 · slurry-chemist 3/6 · tribologist 2/6 |
| Phase 0 체크리스트 | 7/14 |

### 구현된 모델 (발췌)

- **Tier 1** — Preston MRR (`preston.py`), 회전식 CMP 운동학 상대속도장 (`kinematics.py`, Lai MIT 2001), 시간축 공정 (`process_time.py`), WIWNU (`wiwnu.py`)
- **Tier 2** — Greenwood-Williamson 접촉역학 순방향/역문제 (`gw_contact.py`, `gw_pressure_solve.py`), GW→Preston 계수 물리적 분해 (`gw_preston_link.py`), 패드 점탄성 Maxwell (`viscoelastic_maxwell.py`), 패드 마모·glazing 시계열 (`pad_wear_glazing.py`), 컨디셔너 sweep 운동학·PCR 감쇠·asperity 분포 (`conditioner_*.py`), Stribeck 윤활 영역 (`cmp_lubrication_regime.py`), DLVO 콜로이드 안정성 (`dlvo_colloid.py`), Pourbaix/Nernst (`pourbaix_nernst_slope.py`)
- **Integration** — 시공간 제거율 통합 (`spatiotemporal_removal*.py`), 마모 인지 종말점 (`wear_aware_endpoint.py`)
- **Demo** — Streamlit UI (`sim/demo_app.py`): 압력·RPM·존압력 슬라이더 → MRR/프로파일 실시간 플롯

모든 모듈은 문헌 재현값 테스트를 동반합니다. 안 맞으면 노트에 "안 맞는다"고 적습니다.

## 실행

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m pytest tests/ -v                 # 회귀 테스트
streamlit run sim/demo_app.py              # 데모 UI
python tools/check_knowledge.py --all      # 지식노트 품질 게이트
```

## 로드맵

| Phase | 기간 | 목표 |
|---|---|---|
| **0 — CMP 코어 모델** | ~2026-11 | 5개 도메인 에이전트 Lv2+, Tier1/2 핵심 모듈, 데모 UI |
| **1 — CMP 통합 시뮬레이터** | ~2027-01 | 슬러리+패드+디스크+공정변수 통합, 결함 진단 에이전트, **예비창업패키지 증빙 데모** |
| 2 — 인접 공정 확장 | 2027 | Litho / Etch / Deposition 에이전트 |
| 3 — 가상 fab | 2028+ | Fab Director가 공정 플로우 설계·해석 |

상세: [`MASTER-PLAN.md`](MASTER-PLAN.md) · 마일스톤: [`MILESTONES.md`](MILESTONES.md)

## 운영 방식

이 저장소는 사람 1명 + AI 에이전트 크론 4개가 함께 키웁니다. 상시 성장엔진(2시간 간격)이 학습·구현을 번갈아 하고, 심야 병렬 크론이 서브에이전트 3명을 동시에 띄워 지식 축적 속도를 높이며, 품질 게이트(`tools/check_knowledge.py`)를 통과하지 못한 노트는 미완으로 되돌립니다. 진행 기록은 `MASTER-PLAN.md` 하단 진행 로그에 남습니다.

## 원칙

- **출처 없는 주장은 "미검증"으로 표기한다.** 확신하는 척하지 않는 것이 지식베이스의 신뢰도다.
- **공개 문헌·합성 데이터만 사용한다.** 재직 회사의 실험 데이터·배합 정보는 어떤 형태로도 포함하지 않는다.
- 코드는 실행해서 확인한 것만 보고한다.

## License

All rights reserved (사업화 검토 중). 문의: khleecnce@gmail.com
