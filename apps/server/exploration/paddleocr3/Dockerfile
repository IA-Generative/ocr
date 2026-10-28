ARG HARBOR_PROXY_URL

FROM ${HARBOR_PROXY_URL:-docker.io}/paddlepaddle/paddle:3.0.0 AS paddle_model

COPY --from=ghcr.io/astral-sh/uv:0.13.5 /uv /uvx /bin/
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update -qy && \
	apt-get install -qy --no-install-recommends \
	ccache \
	ffmpeg \
	libgl1 \
	libglib2.0-0 \
	libsm6 \
	libxext6 \
	poppler-utils \
	&& apt-get clean \
	&& rm -rf /var/lib/apt/lists/*

# Distrust the eMudhra emSign ECC Root CA - G3 (its intermediates have publicly recoverable
# private keys) explicitly: the Ubuntu-based paddle images ship it in their CA bundle and no
# package upgrade removes it.
RUN sed -i 's|^mozilla/emSign_ECC_Root_CA_-_G3.crt|!mozilla/emSign_ECC_Root_CA_-_G3.crt|' /etc/ca-certificates.conf \
	&& update-ca-certificates --fresh

ENV MKLDNN_VERBOSE=1
ENV UV_CACHE_DIR=/app/.cache
ENV PADDLE_OCR_BASE_DIR=/app/.cache/paddle/
ENV PADDLE_PDX_CACHE_HOME=/app/.tmp/paddlex/
ARG PADDLE_OCR_VERSION="PP-OCRv4"
ENV PADDLE_OCR_VERSION=${PADDLE_OCR_VERSION}

WORKDIR /app

COPY apps/server/pyproject.toml apps/server/uv.lock /app/

RUN uv sync --no-cache --group ocr-service-paddle

ENV PYTHONPATH=/app
COPY apps/server/services /app/services
COPY apps/server/src /app/src
COPY apps/server/business/__init__.py /app/business/__init__.py
COPY apps/server/business/paddleocr3 /app/business/paddleocr3
COPY apps/server/business/cache /app/business/cache
COPY apps/server/business/checkbox_service /app/business/checkbox_service

RUN uv run /app/business/paddleocr3/utils/download_paddle_models.py
ENV PATH=$PATH:/app/.venv/bin/
ENV PYTHONDONTWRITEBYTECODE=1
ENV HOME=/app

# No HTTP server here (Celery worker started by `services/main.py`) - `inspect ping` is Celery's
# own liveness check instead. Long start-period: model loading + broker registration can take a
# while on cold start.
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD celery -A services.main inspect ping || exit 1

# OpenShift's restricted-v2 SCC ignores the image's USER and runs the container as an
# arbitrary UID from the namespace's range, always with GID 0. Owning the tree by group
# root and mirroring the owner bits onto the group is what lets one image work both as
# 10001 on the current cluster and as that arbitrary UID later.
RUN groupadd --gid 10001 appuser \
  && useradd --uid 10001 --gid appuser --no-create-home --home-dir /app --shell /usr/sbin/nologin appuser \
  && mkdir -p /app/.tmp/paddlex \
  && chown -R 10001:0 /app \
  && chmod -R g=u /app

# Numeric, not `appuser`: with `runAsNonRoot: true` and no explicit `runAsUser`, the
# kubelet cannot resolve a named user and refuses to start the container.
USER 10001:10001

CMD ["uv", "run", "services/main.py"]

FROM paddle_model AS test
RUN uv sync --group test --group ocr-service-paddle
COPY --chown=10001:0 apps/server/tests /app/tests
CMD ["uv", "run", "services/main.py"]
