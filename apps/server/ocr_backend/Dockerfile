ARG HARBOR_PROXY_URL

FROM ${HARBOR_PROXY_URL:-docker.io}/python:3.13-slim AS builder

# Trivy triage (#469): closes out the util-linux/openssl family of fixable HIGHs that
# just trail the base image's own package snapshot - not pulled in by anything this
# Dockerfile installs.
RUN apt-get update -qy \
    && apt-get upgrade -qy \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.13.5 /uv /uvx /bin/
ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

COPY apps/server/pyproject.toml /app/pyproject.toml
COPY apps/server/uv.lock /app/uv.lock
RUN uv sync --no-cache --group ocr-backend --group migration \
    && uv cache clean

COPY apps/server/ocr_backend /app/ocr_backend
COPY apps/server/src /app/src
COPY alembic.ini /app/
COPY apps/server/migration /app/migration
COPY apps/server/scripts /app/scripts
COPY apps/server/configs /app/configs

ENV PATH=$PATH:/app/.venv/bin/
ENV HOST=0.0.0.0
ENV PYTHONPATH=/app/
ENV PORT=5000
ENV TORCHINDUCTOR_CACHE_DIR=/app/.cache/torchinductor/
ENV PYTHONDONTWRITEBYTECODE=1
ENV HOME=/app

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD python3 -c "import urllib.request as u; u.urlopen('http://127.0.0.1:${PORT}/api/health', timeout=2)" || exit 1

# OpenShift's restricted-v2 SCC ignores the image's USER and runs the container as an
# arbitrary UID from the namespace's range, always with GID 0. Owning the tree by group
# root and mirroring the owner bits onto the group is what lets one image work both as
# 10001 on the current cluster and as that arbitrary UID later.
RUN groupadd --gid 10001 appuser \
    && useradd --uid 10001 --gid appuser --no-create-home --home-dir /app --shell /usr/sbin/nologin appuser \
    && mkdir -p /app/.cache/torchinductor \
    && chown -R 10001:0 /app \
    && chmod -R g=u /app

# Numeric, not `appuser`: with `runAsNonRoot: true` and no explicit `runAsUser`, the
# kubelet cannot resolve a named user and refuses to start the container.
USER 10001:10001

CMD ["./scripts/run.sh"]

FROM builder AS test
WORKDIR /app
RUN uv sync --no-cache --group test --group ocr-backend --group migration
COPY --chown=10001:0 apps/server/tests tests
CMD ["./scripts/run.sh"]
