# FabSim — 온프레미스 배포 이미지
#
# 고객 환경에서 실행한다(ORG.md §7.5: 고객 데이터는 고객 망을 떠나지 않는다).
# 연구 노트(knowledge/*.md)·에이전트·논문 PDF는 넣지 않는다 — 물성 팩만 따라간다.
#
#   docker build -t fabsim:0.3.0 .
#   docker run --rm -p 8790:8790 fabsim:0.3.0
#   docker run --rm fabsim:0.3.0 fabsim --pack cu_h2o2_bta --json   # CLI만
#
# 고객 팩 주입:
#   docker run -v /path/to/packs:/packs -e FABSIM_PACK_DIR=/packs -p 8790:8790 fabsim:0.3.0

FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FABSIM_HOST=0.0.0.0 \
    FABSIM_PORT=8790 \
    FABSIM_NO_BROWSER=1

WORKDIR /app

# 의존성 먼저 — 레이어 캐시
COPY pyproject.toml README.md ./
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# 코드 + 런타임 데이터(물성 팩)만
COPY sim/ ./sim/
COPY knowledge/params/ ./sim/params/

RUN pip install --no-cache-dir ".[ui]" && \
    python -c "import sim.models; from sim.engine import available_models; \
               assert len(available_models()) >= 4, available_models(); \
               print('모델', available_models())"

# 비루트 실행
RUN useradd -m -u 10001 fabsim && chown -R fabsim:fabsim /app
USER fabsim

EXPOSE 8790
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s \
    CMD python -c "import urllib.request,sys; \
        sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8790/_stcore/health',timeout=3).status==200 else 1)"

CMD ["fabsim-studio"]
