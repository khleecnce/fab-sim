# fab-sim 작업 규칙

## ⛔ CI / GitHub Actions 과금 규칙 (2026-09-15 사고 이후)

이 저장소는 **private**이다. private 저장소의 Actions 실행은 계정의
무료 2000분/월을 소모한다.

**실제로 터진 일:** 에이전트 크론들이 하루 수십 번 push 했고, 그 중
약 65%(30일간 292/454 커밋)는 `knowledge/`, `papers/`, `agents/`,
`*.md` 같은 **pytest 결과와 무관한 문서·데이터 변경**이었다. 그런데도
`on: [push]` 때문에 매번 전체 워크플로가 돌아 2000분을 모두 태웠고,
2026-09-14에 결제 차단이 걸리면서 이후 모든 run이
`The job was not started because recent account payments have failed`
로 죽었다. **테스트는 하나도 깨진 적이 없다** — 로컬 전체 스위트는
729 passed. 즉 쏟아진 실패 알림은 전부 과금 문제였다.

### 규칙

1. **워크플로 트리거를 넓히지 마라.** `.github/workflows/verify.yml`의
   `on.push.paths`는 `**.py`, `requirements.txt`, `.github/**` 로
   한정돼 있다. `on: [push]`로 되돌리면 같은 사고가 재발한다.
   전체 스위트를 수동으로 돌리고 싶으면 Actions 탭의
   `workflow_dispatch`를 쓴다.

2. **push 전 검증은 이미 자동이다.** `core.hooksPath = .githooks`로 설정돼
   있어 `.githooks/pre-push`가 **HEAD를 임시 디렉토리에 export해서**(=CI와
   같은 클린 트리) pytest를 돌린다. 워킹트리가 아니라 HEAD를 보는 이유는,
   크론이 `git add <명시 경로>`로 커밋할 때 동반 변경이 빠져 로컬만 녹색이
   되는 사고가 있었기 때문이다. 새 clone에서는
   `git config core.hooksPath .githooks`를 다시 걸어야 한다.
   우회는 `FABSIM_SKIP_PREPUSH=1 git push`(급할 때만).

3. **빨간 CI를 원격에 밀지 마라.** 실패하는 run도 분을 소모한다.

4. **분(minute) 절약 장치 두 가지가 더 걸려 있다. 되돌리지 마라.**
   - `concurrency: cancel-in-progress` — 크론이 몇 분 간격으로 연속
     push 할 때 중간 run들을 취소한다. 이전에는 push마다 ~8분짜리 run이
     끝까지 돌았다.
   - `knowledge-quality`는 별도 워크플로로 분리해 **주 1회**(월 12:00 KST)
     만 돈다. 모든 스텝이 `continue-on-error`라 아무것도 막지 못하면서
     push마다 한 벌씩 분을 태우고 있었다. 필요하면 Actions 탭에서
     수동 실행.

### 검증 명령

```bash
cd ~/fab-sim && ./.venv/bin/python -m pytest -q     # 729 passed / 약 200초
```

> 주의: `.venv`는 python 3.9다. 시스템 python이나 Hermes venv에는
> pytest가 없어서 `No module named pytest`가 난다 — 테스트가 없는 게
> 아니라 인터프리터를 잘못 고른 것이다.

### 결제 복구

무료 분이 리셋되거나(매월) 결제 수단을 고치기 전까지는 Actions가
전혀 돌지 않는다. 확인:
https://github.com/settings/billing
