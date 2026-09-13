담당 에이전트: **pad-material**
학습 단원: **Lv2-1 점탄성 심화 — 온도·주파수 의존 저장/손실 탄성률(E', E'', tanδ)과 CMP 조건 매핑**
- agents/pad-material/CURRICULUM.md Lv2-1 항목만 학습하라. 여러 단원 훑기 금지.
- **먼저 읽어라(선행/부모지식)**: knowledge/materials/pad-viscoelasticity-dma.md, knowledge/materials/hertz-gw-contact-mechanics.md, knowledge/materials/pu-pad-chemistry-prepolymer-foam.md, knowledge/materials/pad-hardness-porosity-measurement-methods.md
- 조사 범위 확인: `.venv/bin/python tools/scope.py --agent pad-material --queries` 로 검색어를 얻고 그 안에서만 조사. focus는 PU 소재 물성 — 형제(pad-structure 그루브/서브패드, pad-lifecycle 마모)는 침범 금지.
- 목표: 점탄성 재료의 저장탄성률 E'·손실탄성률 E''·tanδ의 정의, DMA 측정, 시간-온도 중첩(WLF/Arrhenius shift), CMP 실제 온도(30~60°C)·마찰 주파수 대역에서 IC1000/IC1010류 PU 패드의 E'·tanδ 문헌값과 그것이 접촉강성·MRR·리바운드에 주는 영향. 유리전이 Tg 근방 거동.
- python verify: WLF 식(C1,C2 상수 박고 shift factor a_T 재현) 또는 tanδ=E''/E' 관계, 또는 문헌 E'(온도) 값을 상수로 박고 대조. 못 재현하면 정직히 기록.
- 상호링크 최소 3개: [[pad-viscoelasticity-dma]], [[hertz-gw-contact-mechanics]], [[pu-pad-chemistry-prepolymer-foam]] 등 실존 파일만.
- 노트: knowledge/materials/pad-viscoelasticity-temp-frequency-dma.md (기존 pad-viscoelasticity-dma.md와 다른 파일 — 온도·주파수 심화편)
