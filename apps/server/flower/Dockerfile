ARG HARBOR_PROXY_URL

FROM ${HARBOR_PROXY_URL:-docker.io}/python:3.13-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
	build-essential \
	gcc \
	&& rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir flower redis celery

# OpenShift's restricted-v2 SCC ignores the image's USER and runs the container as an
# arbitrary UID from the namespace's range, always with GID 0. Owning the tree by group
# root and mirroring the owner bits onto the group is what lets one image work both as
# 10001 on the current cluster and as that arbitrary UID later.
RUN groupadd --gid 10001 appuser \
    && useradd --uid 10001 --gid appuser --no-create-home --home-dir /home/appuser --shell /usr/sbin/nologin appuser \
    && mkdir -p /home/appuser \
    && chown -R 10001:0 /home/appuser \
    && chmod -R g=u /home/appuser
ENV HOME=/home/appuser
ENV PYTHONDONTWRITEBYTECODE=1

# Numeric, not `appuser`: with `runAsNonRoot: true` and no explicit `runAsUser`, the
# kubelet cannot resolve a named user and refuses to start the container.
USER 10001:10001

EXPOSE 5555
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD python3 -c "import urllib.request as u; u.urlopen('http://127.0.0.1:5555/', timeout=2)" || exit 1
