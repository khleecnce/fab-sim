# 구성요소 스키마 — CMP를 이루는 모든 것의 분해도

> 2026-09-06 사용자 지시: "슬러리: 1)입자 2)R/R booster 3)R/R inhibitor 4)oxidizer
> 5)chelator 6)biocide 7)pH조절제 8)분산제 9)Defect저감제 10)roughness·TTV 개선 외 …
> 장비, 패드, disk 등 다른 요소들도 이런식으로 구성해줘. 어떤 구성이 필요할지는
> 내가 슬러리 경험밖에 없어서 잘 모르니까 research ai agent 통해서 조사해서 만들어."
>
> 이어서: **"내가 말했다고 그게 전체는 아니야. 필요한게 있으면 포함시켜."**
> → 사용자 목록은 **씨앗**이지 명세가 아니다. 각 계열의 담당 에이전트가 문헌으로
> 빠진 항목을 찾아 추가한다. 추가할 때는 `origin: researched` 와 근거를 반드시 단다.

## 왜 이 층이 필요한가

지금 물성 팩(`knowledge/params/*.yaml`)은 **시뮬레이터가 당장 쓰는 숫자**만 담는다
(kp_m_per_pa, slurry_ph …). 그런데 실무자가 다루는 단위는 그게 아니다 —
"세리아 입자 1차 60nm, 2차 120nm, 함량 1.5wt%, Nit booster 300ppm, 분산제 X"처럼
**배합 단위**로 생각한다.

이 층(`knowledge/components/`)이 그 간극을 메운다:

```
구성요소 스키마 (사람이 다루는 단위)      →  물성 팩 (시뮬레이터가 쓰는 숫자)
abrasive.secondary_size_nm = 120            →  abrasive_size_nm = 120
booster.nit.concentration_ppm = 300         →  (연결식) → kp_m_per_pa 보정
inhibitor.bta_mM = 5                        →  inhibitor_mM = 5
```

연결식(`maps_to`)이 없는 항목은 **아직 시뮬레이터에 반영 안 된다**. 그걸 숨기지 않고
`status: not_wired` 로 표시한다 — UI에 회색으로 뜬다. 무엇이 비어 있는지 보이는 게
목적이다.

## 파일 배치

```
knowledge/components/
  _SCHEMA.md          ← 이 파일 (형식 정의)
  slurry.yaml         담당: slurry-chemist (+ 분화 3명)
  pad.yaml            담당: pad-mechanic (+ 분화 3명)
  conditioner.yaml    담당: disk-conditioner (+ 분화 2명)
  tool.yaml           담당: tool-platen-head, tool-endpoint
  wafer.yaml          담당: wafer-type, film-*
  process.yaml        담당: cmp-integrator (레시피·시퀀스·환경)
  post_cmp.yaml       담당: tool-post-clean, surface-contamination
  metrology.yaml      담당: wafer-metrology
```

## 항목 형식

```yaml
version: 1
component: slurry
owner: slurry-chemist              # 이 파일의 책임 에이전트
description: "..."

groups:
  - id: abrasive
    label: "입자 (연마입자)"
    origin: user                   # user | researched
    owner: slurry-abrasive         # 이 그룹의 담당 (분화 에이전트)
    why: "제거의 기계적 주체. 종류·크기·형상·함량이 MRR과 스크래치를 동시에 결정"
    fields:
      - key: type
        label: 종류
        type: enum
        options: [silica_colloidal, silica_fumed, ceria, alumina, zirconia, diamond, mixed]
        origin: user
        maps_to: abrasive          # 물성 팩 키. 없으면 생략
        status: wired              # wired | not_wired | partial
        source: knowledge/cmp/slurry-components-overview.md
        confidence: literature     # verified | literature | estimated | unverified
        note: "..."
      - key: primary_size_nm
        label: 1차 입도
        type: number
        unit: nm
        typical: [10, 200]         # 실무 범위 (문헌 근거 필요)
        origin: user
        maps_to: abrasive_size_nm
        status: wired
```

### 필드 규칙

- `origin: user` — 사용자가 직접 지시한 항목. **삭제 금지.** 이름을 바꾸려면 사용자 확인.
- `origin: researched` — 에이전트가 문헌에서 찾아 추가. `source` 필수.
- `status: not_wired` — 스키마에는 있으나 시뮬레이터 연결 없음. **지어내서 연결하지 마라.**
  연결하려면 물리 근거(노트 + verify 블록)가 먼저다.
- `confidence` — 물성 팩과 같은 4단계. `typical` 범위도 출처가 필요하다.
- `maps_to` 는 물성 팩 키 또는 `slots:` 구현 파라미터를 가리킨다.

## 담당 에이전트가 할 일

1. `SCOPE.yaml`의 자기 조사 범위를 확인한다 (`tools/scope.py --agent <id>`).
2. **그 계열의 논문·특허·교과서를 조사**해 빠진 그룹/필드를 찾는다.
3. 추가할 때 `origin: researched` + `source` + `confidence`를 단다.
4. 물리적 연결식이 성립하면 노트를 쓰고 `maps_to`를 채운 뒤 `status: wired`로 올린다.
   **연결식 없이 status를 올리는 것은 할루시네이션이다.**
5. `tools/components.py --check` 로 스키마 유효성을 확인하고 커밋한다.

## 사용자 목록을 넘어서라

사용자는 슬러리 실무자다. 나머지 계열(장비·패드·디스크·후공정·계측)은 **문헌이
사용자보다 많이 안다.** 사용자가 언급하지 않은 항목이라도 그 계열에서 중요하면
반드시 넣어라. 반대로 사용자가 지시한 항목은 문헌에 드물어도 남긴다 — 실무에서
쓰이는 축이라는 뜻이다.
