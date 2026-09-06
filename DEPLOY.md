# FabSim 배포

산출물 3종. 대상이 다르다.

| 형태 | 대상 | 명령 |
|---|---|---|
| **Mac 앱** | 사용자 본인·데모 | `open "dist/FabSim Studio.app"` |
| **웹(Docker)** | 고객사 온프레미스 | `docker run -p 8790:8790 fabsim:0.3.0` |
| **wheel** | 고객 파이썬 환경·CI | `pip install fabsim-0.3.0-py3-none-any.whl` |

## 빌드

```bash
./packaging/build.sh            # 앱 + wheel → dist/
./packaging/build.sh --wheel    # wheel만
docker build -t fabsim:0.3.0 .  # 컨테이너
```

## 실행

```bash
fabsim --pack cu_h2o2_bta --profile     # CLI
fabsim-studio                           # Streamlit UI (단일 사용자)
fabsim-web                              # HTTP API + 웹 UI (다중 사용자, :8080)
```

## 배포본에 무엇이 들어가고 무엇이 빠지나

**들어간다**: `sim/` 코드, `knowledge/params/*.yaml`(물성 팩), 내장 웹 UI

**빠진다** — 의도적이다:
- `papers/` — 논문 PDF. 저작권상 재배포 불가
- `knowledge/*.md` — 연구 노트. 우리 자산이지 제품이 아니다
- `agents/` — 에이전트 조직·조사 범위(SCOPE.yaml). 영업비밀
- `tests/`, `tools/`

`tests/test_deploy.py`가 이 경계를 강제한다. Dockerfile에 `COPY papers`를 넣으면 테스트가 깨진다.

## 고객 환경 설정

```bash
# 고객이 자기 물성 팩을 쓴다
docker run -v /opt/mypacks:/packs -e FABSIM_PACK_DIR=/packs -p 8790:8790 fabsim:0.3.0

# 포트 변경
FABSIM_PORT=9000 fabsim-web
```

**데이터는 고객 망을 떠나지 않는다** (ORG.md §7.5). 외부 호출 없음, 텔레메트리 없음, 웹 UI는 CDN 의존 0.

## 아직 아닌 것

- 코드 서명 없음(ad-hoc). 배포 시 Gatekeeper 경고 → 정식 배포 전 Apple Developer ID 필요
- 라이선스 키 없음 — M6(12월) 데모 후
- 다중 사용자 인증 없음. 사내망 전제. 외부 노출 시 리버스 프록시로 감쌀 것
