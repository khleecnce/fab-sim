담당 에이전트: **wafer-metrology**
학습 단원: **Lv2-2 패턴 지표 — step height·dishing·erosion·잔막(residual)·엣지 롤오프의 측정 구조물과 판정 기준**
- agents/wafer-metrology/CURRICULUM.md Lv2-2 항목만 학습하라.
- **먼저 읽어라(선행)**: knowledge/cmp/uniformity-metrics-definitions-standards.md, knowledge/cmp/wafer-metrology-thickness-methods.md, knowledge/cmp/pattern-dependent-dishing-erosion.md, knowledge/cmp/wafer-surface-roughness-afm-scan-scale-dependence.md
- ⚠ 이 에이전트 최우선 원칙: **지표 정의는 문헌·표준(SEMI/JEDEC·장비사 매뉴얼·논문)에서 확정하라. 사용자 회사 관행 정의를 그대로 옮기지 마라.** 정의가 갈리면 병기.
- 조사 범위: `.venv/bin/python tools/scope.py --agent wafer-metrology --queries`. SEMI 표준·장비사 매뉴얼이 논문보다 중요. focus는 지표 정의·측정 구조물.
- 목표: dishing(금속 오목)·erosion(유전체 침식)·step height·residual film·edge roll-off의 표준 정의, 측정에 쓰는 테스트 구조(패턴밀도 배열·라인/스페이스·comb structure), 프로파일러/AFM 측정법, 판정 스펙 예시(nm 단위). 패턴밀도·라인폭 의존성.
- python verify: dishing/erosion 정의식(예: erosion = 필드 대비 어레이 유전체 두께 감소, dishing = 금속선 중앙 함몰)을 문헌 수치로 상수 박고 관계 재현/대조. 패턴밀도-dishing 경향이라도 가능. 못 재현하면 정직히 기록.
- 상호링크 최소 3개: [[uniformity-metrics-definitions-standards]], [[pattern-dependent-dishing-erosion]], [[wafer-metrology-thickness-methods]] 등 실존 파일.
- 노트: knowledge/cmp/pattern-metrics-dishing-erosion-stepheight.md
