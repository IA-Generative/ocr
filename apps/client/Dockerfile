ARG PNPM_VERSION=11.28.9

# dev
FROM docker.io/node:24.22.1-slim AS dev

# pnpm's native binary (@pnpm/exe) needs libatomic, which the slim base image doesn't
# ship - without it the binary fails at runtime with "libatomic.so.1: cannot open
# shared object file", not at install time.
RUN apt-get update \
    && apt-get install -y --no-install-recommends libatomic1 \
    && rm -rf /var/lib/apt/lists/*

RUN npm install --ignore-scripts --location=global pnpm@${PNPM_VERSION}

WORKDIR /app
# Single, non-recursive chown of the empty directory: switching to `node` before
# installing anything means `node_modules` and the copied source are owned by
# `node` from the moment they're created, instead of a slow `chown -R` afterwards.
RUN chown node:node /app

USER node

# The lockfile and pnpm-workspace.yaml have to land *before* the install, not
# with the rest of the sources: installing from package.json alone re-resolves
# every range, so the image ignored the committed lockfile entirely. It also
# left node_modules out of sync with the lockfile that `COPY . .` then brought
# in, which pnpm's verify-deps-before-run check turns into a hard failure
# (it wants to reinstall, that needs to remove node_modules, and there is no
# TTY in a build to confirm it).
# Build scripts are restricted by `allowBuilds` in pnpm-workspace.yaml.
COPY --chown=node:node ./package.json ./pnpm-lock.yaml ./pnpm-workspace.yaml ./
RUN pnpm install --frozen-lockfile
COPY --chown=node:node . .

CMD ["pnpm", "run", "dev"]


# build
FROM dev AS build

RUN pnpm run build


# prod
FROM docker.io/nginxinc/nginx-unprivileged:1.31.6-alpine AS prod

# The base image's CA bundle still trusts the eMudhra emSign ECC Root CA - G3, whose
# intermediates have publicly recoverable private keys. Alpine's ca-certificates
# 20261020-r0 removes it; both packages are upgraded because the `ca-certificates` trigger
# regenerates the bundle from its own copy. `USER 101` restores the numeric user the base
# image ends on.
USER root
RUN apk upgrade --no-cache ca-certificates ca-certificates-bundle
USER 101

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx/50x.html /usr/share/nginx/html
COPY nginx/40x.html /usr/share/nginx/html
COPY nginx/default.conf /etc/nginx/conf.d/default.conf

# Deliberately no `USER` here. nginx-unprivileged already ends on `USER 101`, and the
# numeric form is what `runAsNonRoot: true` needs to verify - re-declaring it as `USER
# nginx` would replace a verifiable user with an unverifiable name. The base image also
# already owns /var/cache/nginx and /etc/nginx by group root for arbitrary UIDs, and
# these assets are only ever read, never written.

EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://127.0.0.1:8080/ || exit 1
CMD ["nginx", "-g", "daemon off;"]
