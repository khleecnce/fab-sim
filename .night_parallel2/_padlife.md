담당 에이전트: **pad-lifecycle**
학습 단원: **Lv2-1 glazing(글레이징) 메커니즘 — asperity 소성변형·슬러리 잔류물 축적·MRR 감소**
- agents/pad-lifecycle/CURRICULUM.md Lv2-1 항목만 학습하라. (이전 회차에서 max-turns로 실패 — 이번엔 단원 1개에만 집중해 완료하라.)
- **먼저 읽어라(선행/부모지식)**: knowledge/materials/pad-wear-glazing-mrr-decay.md, knowledge/equipment/conditioning-mechanism-asperity-regeneration.md, knowledge/materials/pad-breakin-asperity-mrr-runup.md, knowledge/materials/pad-conditioning-wear-regeneration-balance.md
- 조사 범위: `.venv/bin/python tools/scope.py --agent pad-lifecycle --queries`. focus는 패드 사용이력→시간의존 MRR/결함. 형제(pad-material 소재물성, disk-conditioner 디스크설계) 침범 금지.
- 목표: glazing의 물리적 정의(asperity 끝의 소성변형·평탄화, 기공 막힘, 슬러리 부산물/마모입자 응착), glazing이 표면 asperity 밀도·접촉면적·마찰계수·MRR에 주는 정량 영향, 컨디셔닝으로의 회복. 문헌의 MRR 감소율·표면조도 변화 수치.
- python verify: glazing에 따른 MRR 감소를 문헌 수치(예: N시간 후 MRR X% 감소)로 상수 박고 재현/대조. asperity 접촉면적-압력 관계라도 가능. 못 재현하면 정직히 기록.
- 상호링크 최소 3개: [[pad-wear-glazing-mrr-decay]], [[conditioning-mechanism-asperity-regeneration]], [[pad-conditioning-wear-regeneration-balance]] 등 실존 파일.
- 노트: knowledge/materials/pad-glazing-mechanism-mrr-decay.md
