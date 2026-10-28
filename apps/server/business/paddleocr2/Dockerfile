ARG HARBOR_PROXY_URL

FROM ${HARBOR_PROXY_URL:-docker.io}/python:3.13-slim AS builder

# Selects which PaddlePaddle wheel gets installed below: "cpu" (default) keeps the
# CPU-only package already pinned in pyproject.toml; "gpu" additionally installs the
# CUDA-enabled wheel from PaddlePaddle's own package index, built with
# `--build-arg PADDLE_DEVICE=gpu`. The wheel bundles its own CUDA runtime, so the base
# image doesn't need to change. This only decides what's installed in the image - the
# actual device used at inference time is still selected at runtime via the `DEVICE`
# env var read by `PaddleSetting` (business/paddleocr2/configs/paddle.py).
ARG PADDLE_DEVICE=cpu
ENV PADDLE_DEVICE=${PADDLE_DEVICE}
ARG PADDLE_CUDA_INDEX=cu126
ENV PADDLE_CUDA_INDEX=${PADDLE_CUDA_INDEX}

RUN pip install --no-cache-dir uv==0.13.5
ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

# Trivy triage (#469): `apt upgrade` before installing anything closes out the
# util-linux/openssl family of fixable HIGHs that just trail the base image's own
# package snapshot, on top of the packages this Dockerfile adds below.
RUN apt update -qy && apt upgrade -qy && apt install -qy \
  curl \
  ffmpeg \
  libsm6 \
  libxext6 \
  poppler-utils \
  libreoffice-core \
  libreoffice-writer \
  libreoffice-calc \
  libreoffice-impress \
  && apt autoremove && rm -rf /var/lib/apt/lists/*
ENV UV_CACHE_DIR=/app/.cache
ENV PADDLE_OCR_BASE_DIR=/app/.cache/paddle/
ENV PADDLE_PDX_CACHE_HOME=$PADDLE_OCR_BASE_DIR
ENV PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK=True
ENV TORCH_HOME=/app/.cache/torch/
ENV HF_HOME=/app/.cache/huggingface/
ENV TORCHINDUCTOR_CACHE_DIR=/app/.cache/torchinductor/
# Limite le parallélisme interne PaddlePaddle/OpenBLAS/PaddleX DataLoader.
# Évite les deadlocks de threads dans un worker Celery solo.
ENV OMP_NUM_THREADS=1
ENV MKL_NUM_THREADS=1
ENV PADDLE_NUM_THREADS=1
ENV OPENBLAS_NUM_THREADS=1
ENV FLAGS_paddle_num_threads=1

COPY apps/server/pyproject.toml apps/server/uv.lock apps/server/.python-version  /app/
RUN uv sync --no-cache --group business-forms \
  --group checkbox_service \
  --group client \
  --group liteparse \
  --group ocr-service-paddle \
  --group ocr-docling \
  --group services \
  && uv cache clean

RUN uv pip install --no-cache --reinstall --no-deps "opencv-contrib-python==4.10.0.84"

RUN if [ "$PADDLE_DEVICE" = "gpu" ]; then \
  uv pip install --no-cache "paddlepaddle-gpu==3.1.1" \
  -i "https://www.paddlepaddle.org.cn/packages/stable/${PADDLE_CUDA_INDEX}/" \
  ; fi

ENV PYTHONPATH=/app
# Download PaddleOCR models
COPY apps/server/business/paddleocr2 /app/business/paddleocr2
RUN uv run business/paddleocr2/utils/download_paddle_models.py \
  --folder $PADDLE_OCR_BASE_DIR

# Copy application code
COPY apps/server/business/__init__.py /app/business/__init__.py
COPY apps/server/business/cache /app/business/cache
COPY apps/server/business/checkbox_service /app/business/checkbox_service
COPY apps/server/business/forms /app/business/forms
COPY apps/server/business/features /app/business/features
COPY apps/server/business/docling_inference /app/business/docling_inference
COPY apps/server/business/extractions /app/business/extractions
COPY apps/server/business/liteparse /app/business/liteparse

# Copy common code
COPY apps/server/src /app/src
COPY apps/server/services /app/services/
COPY apps/server/configs /app/configs/

ENV PATH=$PATH:/app/.venv/bin/
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

# No HTTP server here (Celery worker, started via `celery -A services.main worker ...` in
# docker-compose/helm's command override) - `inspect ping` is Celery's own liveness check
# instead. Long start-period: model loading + broker registration can take a while on cold start.
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD celery -A services.main inspect ping || exit 1

FROM builder AS test
RUN uv sync --no-cache --group business-forms \
  --group checkbox_service \
  --group client \
  --group liteparse \
  --group ocr-service-paddle \
  --group ocr-docling \
  --group services \
  --group test \
  && uv cache clean

# uv sync above re-resolves strictly from the lockfile, which would drop the GPU wheel
# installed outside of it - reinstall it here so GPU test images keep it too.
RUN if [ "$PADDLE_DEVICE" = "gpu" ]; then \
  uv pip install --no-cache "paddlepaddle-gpu==3.1.1" \
  -i "https://www.paddlepaddle.org.cn/packages/stable/${PADDLE_CUDA_INDEX}/" \
  ; fi
