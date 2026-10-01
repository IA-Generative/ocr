ARG HARBOR_PROXY_URL

FROM ${HARBOR_PROXY_URL:-docker.io}/python:3.13-slim

# Same refresh as the api image: picks up the fixable HIGHs that only trail the base
# image's own package snapshot, nothing this Dockerfile installs.
RUN apt-get update -qy \
    && apt-get upgrade -qy \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

# Only alembic on top of the project's own dependencies: env.py needs the SQLAlchemy
# models from src/, not the API or OCR stacks.
COPY apps/server/pyproject.toml /app/pyproject.toml
COPY apps/server/uv.lock /app/uv.lock
RUN uv sync --no-cache --no-default-groups --group migration \
    && uv cache clean

# src/ reads /app/pyproject.toml for its version and configs/logging.yaml for the logger.
COPY apps/server/src /app/src
COPY apps/server/configs /app/configs
COPY alembic.ini /app/
COPY apps/server/migration /app/migration

ENV PATH=$PATH:/app/.venv/bin/
ENV PYTHONPATH=/app/
ENV PYTHONDONTWRITEBYTECODE=1
ENV HOME=/app

# OpenShift's restricted-v2 SCC ignores the image's USER and runs the container as an
# arbitrary UID from the namespace's range, always with GID 0. Owning the tree by group
# root and mirroring the owner bits onto the group is what lets one image work both as
# 10001 on the current cluster and as that arbitrary UID later.
RUN groupadd --gid 10001 appuser \
    && useradd --uid 10001 --gid appuser --no-create-home --home-dir /app --shell /usr/sbin/nologin appuser \
    && chown -R 10001:0 /app \
    && chmod -R g=u /app

# Numeric, not `appuser`: with `runAsNonRoot: true` and no explicit `runAsUser`, the
# kubelet cannot resolve a named user and refuses to start the container.
USER 10001:10001

CMD ["alembic", "upgrade", "head"]
