## 0.3.1 (2025-05-01)

### Feat

- :sparkles: add submodule infra
- :zap: add tests in containers
- add first client for ocr (#20)
- add input form
- add output format
- output integration
- add output around all
- :tada: add new arch for queueing ocr

### Fix

- **health**: :bug: add all deps for healthcheck
- use right env var
- input for task
- same id for task
- version
- write integration
- :bug: change runner type

### Refactor

- :lipstick: refactor s3
- base and s3
- clean code
- code clean
- :art: change minio vars

## [0.22.0](https://github.com/IA-Generative/ocr/compare/v0.21.1...v0.22.0) (2026-10-07)


### Features

* **docker:** add a dedicated migration image ([038f606](https://github.com/IA-Generative/ocr/commit/038f606700445f8f2290cd46a38b93961bfbf5ec))


### Bug Fixes

* **deps:** declare pyyaml, imported by the shared logger ([938e5a0](https://github.com/IA-Generative/ocr/commit/938e5a054da3e92c22aa46d17c9b4f2f320ff2a3))


### Code Refactoring

* **chart:** default to the ocr repository's ghcr.io images, migrate with the migration image ([6d2b06e](https://github.com/IA-Generative/ocr/commit/6d2b06e41da1dedd74b7b37fd107e6ba0770a572))


### Dependencies

* use the ocr-worker and ocr-migration images locally ([2cd0d3d](https://github.com/IA-Generative/ocr/commit/2cd0d3d16c0de7f60b6ba5dfc9a2cce24bf1ebcc))

## [0.21.1](https://github.com/IA-Generative/ocr-api/compare/v0.21.0...v0.21.1) (2026-09-30)


### Bug Fixes

* **ci:** drop the YouTube SDK methods and make the paddle opencv install deterministic ([65f64ac](https://github.com/IA-Generative/ocr-api/commit/65f64ac19cb02aa217165742f1ec553ddd414e05))
* **client:** upgrade libexpat in the nginx image (CVE-2026-93990) ([5641a9d](https://github.com/IA-Generative/ocr-api/commit/5641a9dfa3bf3588dd6869f5cf4e5bac1021cebd))
* **docker:** drop the removed media group and directory from the paddle image ([933002c](https://github.com/IA-Generative/ocr-api/commit/933002c33e3d6df5f2c06c99fd82ce9f16d7ab17))

## [0.21.1-rc](https://github.com/IA-Generative/ocr-api/compare/v0.21.0...v0.21.1-rc) (2026-09-30)


### Bug Fixes

* **ci:** drop the YouTube SDK methods and make the paddle opencv install deterministic ([7042087](https://github.com/IA-Generative/ocr-api/commit/7042087d6459be524f3015757e9f35d478babfd2))
* **client:** upgrade libexpat in the nginx image (CVE-2026-93990) ([cc7c170](https://github.com/IA-Generative/ocr-api/commit/cc7c1709aecaffa982cb41932b27b53403afee35))
* **docker:** drop the removed media group and directory from the paddle image ([38a875e](https://github.com/IA-Generative/ocr-api/commit/38a875e3d6ada314e7f1f3d9109366668bd89696))

## [0.21.0](https://github.com/IA-Generative/ocr-api/compare/v0.20.2...v0.21.0) (2026-09-30)


### Features

* **purge:** periodic purge of old tasks via Celery Beat ([3ac5dee](https://github.com/IA-Generative/ocr-api/commit/3ac5dee726bc6c3dc20a224e5cee759177f67996))


### Bug Fixes

* **pipeline:** remove LLM-based OCR/form extraction entirely ([8f4d8c4](https://github.com/IA-Generative/ocr-api/commit/8f4d8c412ba2ef6be3ff2ff357fb3eed8b15e28f))


### Code Refactoring

* **purge:** schedule purge with a Celery crontab instead of a plain interval ([90b53f1](https://github.com/IA-Generative/ocr-api/commit/90b53f1d672067fdd64e54d8cb4bc3243a57a181))

## [0.21.0-rc](https://github.com/IA-Generative/ocr-api/compare/v0.20.2...v0.21.0-rc) (2026-09-28)


### Features

* **purge:** periodic purge of old tasks via Celery Beat ([e0f17e0](https://github.com/IA-Generative/ocr-api/commit/e0f17e0f47296c09612429385bf7a968561f9a4d))


### Bug Fixes

* **pipeline:** remove LLM-based OCR/form extraction entirely ([55a2357](https://github.com/IA-Generative/ocr-api/commit/55a23578e57766109c3d15a474467f7b18bb78fa))


### Code Refactoring

* **purge:** schedule purge with a Celery crontab instead of a plain interval ([1e2213c](https://github.com/IA-Generative/ocr-api/commit/1e2213c96703f7c4e333c2fba7b8d72c25a951a8))

## [0.20.2](https://github.com/IA-Generative/ocr-api/compare/v0.20.1...v0.20.2) (2026-09-16)


### Bug Fixes

* **compose:** replace defunct minio/minio image with rustfs/rustfs ([2554c76](https://github.com/IA-Generative/ocr-api/commit/2554c76d812ec899c483382974177a79f61f79c9))

## [0.20.1](https://github.com/IA-Generative/ocr-api/compare/v0.20.0...v0.20.1) (2026-09-16)


### Bug Fixes

* **dso:** fall back to full chart package when before-SHA is unreachable ([c331ae7](https://github.com/IA-Generative/ocr-api/commit/c331ae7e0937a7b5c08248942352e857279cdf1f))

## [0.20.1-rc](https://github.com/IA-Generative/ocr-api/compare/v0.20.0...v0.20.1-rc) (2026-09-16)


### Bug Fixes

* **dso:** fall back to full chart package when before-SHA is unreachable ([57d5eea](https://github.com/IA-Generative/ocr-api/commit/57d5eea9f1d9dca5d4c779453a6590123b569309))

## [0.20.0](https://github.com/IA-Generative/ocr-api/compare/v0.19.11...v0.20.0) (2026-09-16)


### Features

* **auth,sdk:** add refresh token support end-to-end ([9a474ae](https://github.com/IA-Generative/ocr-api/commit/9a474ae5911a1abca7c256a710b700193e1dacc9))
* **auth:** add a password-grant token endpoint for non-browser clients ([8777993](https://github.com/IA-Generative/ocr-api/commit/87779932ac7150515b97154c7d0357a1105b9764))
* **bakend:** add auth other backend only ([d355acf](https://github.com/IA-Generative/ocr-api/commit/d355acf2793da7c4d45359a3fb9da75a99533010))
* **client:** add GitHub and API docs links to the footer ([c84e780](https://github.com/IA-Generative/ocr-api/commit/c84e7809285726f4505e6d60a8f9eb653746b7bb))
* **client:** display tasks as a tile grid instead of a table ([ec15ade](https://github.com/IA-Generative/ocr-api/commit/ec15ade25c921f90b2c4df203d9854430751a888))
* gpu available ([7effe35](https://github.com/IA-Generative/ocr-api/commit/7effe355a90d3c72f7b213d4cd624b163872a4c2))
* **sdk:** add a TypeScript/Node.js SDK (sdk/js) ([c3b5db2](https://github.com/IA-Generative/ocr-api/commit/c3b5db2b45c9212e88ee6979cf3b922fbd8b8c39))
* **sdk:** sync client routes/schemas with the API, add login() ([56b9d29](https://github.com/IA-Generative/ocr-api/commit/56b9d29ae2af36c188ee257439e8027dcd4c6375))


### Bug Fixes

* **auth:** add API_KEYS for machine-to-machine authentication ([96e9c4e](https://github.com/IA-Generative/ocr-api/commit/96e9c4e3515de54b010af38729ee9ba8e4479dac))
* **auth:** end the Keycloak SSO session on logout ([b4f16a2](https://github.com/IA-Generative/ocr-api/commit/b4f16a229b083a1c17e660f19684c08e6ec9cf4d))
* **auth:** rate-limit /api/auth/login per client IP ([0905ab9](https://github.com/IA-Generative/ocr-api/commit/0905ab97a68d5b6bd919880f8cd7da91c63c9284))
* **auth:** reject cross-site logout requests as CSRF defense in depth ([0d3bf39](https://github.com/IA-Generative/ocr-api/commit/0d3bf390f741610dc2cf76a3695eaac703ebf98a))
* **auth:** remove the VITE_SSO_BYPASS frontend auth-guard bypass ([ae03b43](https://github.com/IA-Generative/ocr-api/commit/ae03b43292b49a53d4cc89228d9edd2aab288f33))
* **auth:** route login through keycloak-js and pin the redirect_uri ([9ce9d3e](https://github.com/IA-Generative/ocr-api/commit/9ce9d3e125852fde748ad53e21581845f595ed3d))
* **auth:** stop trusting empty-subject/introspection claims and freeze roles ([ac1f26d](https://github.com/IA-Generative/ocr-api/commit/ac1f26db833dc25158409770a6ab9b39eab9cde5))
* **auth:** strip OIDC response params before Keycloak check-sso ([fed37aa](https://github.com/IA-Generative/ocr-api/commit/fed37aa29de52755d5ba3d25553a9e7737e52c50))
* **auth:** strip trailing slash from BACKEND_PUBLIC_URL too ([0d3cf18](https://github.com/IA-Generative/ocr-api/commit/0d3cf183ceb625e030811053d739120cfc1952db))
* **ci:** tag Harbor images with the chart appVersion ([1b51ed5](https://github.com/IA-Generative/ocr-api/commit/1b51ed5104d8ef4cb5f17b87cc1bcb2d169afa13))
* **client:** correct pagination cursor and default bounding boxes display ([55c8d3c](https://github.com/IA-Generative/ocr-api/commit/55c8d3c574ae7b2e31299fda18286aee9e9ea7b8))
* **client:** install from the committed lockfile in the Docker image ([c69e3c0](https://github.com/IA-Generative/ocr-api/commit/c69e3c09b5803a7ee048a59bd6da7af9fbb24e19))
* **client:** install libatomic1 for pnpm's native binary in the slim image ([1142d8e](https://github.com/IA-Generative/ocr-api/commit/1142d8e22f8cd8eca20d4666cde151348ab77282))
* **client:** keep the tasks tab up to date, add a manual refresh button ([f048142](https://github.com/IA-Generative/ocr-api/commit/f048142c6b6ab1ea457811a0ce3434ae18cad0db))
* delete commitizen ([3d9fdb6](https://github.com/IA-Generative/ocr-api/commit/3d9fdb6c6543cf8403a26bd493008b8c3522e378))
* **deps:** bump aiohttp, h2, tornado and transformers (darwin) to patched versions ([06cbb4e](https://github.com/IA-Generative/ocr-api/commit/06cbb4eb7f32081cfb3508a690e659ebba1b0db6))
* **deps:** pin transitive npm packages to patched versions via pnpm overrides ([bff9a87](https://github.com/IA-Generative/ocr-api/commit/bff9a87c9ad1d1e67b0625aa3cbbbea4d14059ba))
* **frontend:** handle nullable percentage in the task sort comparator ([27c3db6](https://github.com/IA-Generative/ocr-api/commit/27c3db6c7c63a3bc0ed1bf503fc9e00ab6cf73c0))
* **frontend:** paginate the user tasks list correctly ([ef3737b](https://github.com/IA-Generative/ocr-api/commit/ef3737b4bda22deee93a603d52d0665010466699))
* gitleak disbale false postif ([626bd6f](https://github.com/IA-Generative/ocr-api/commit/626bd6f61b38bf6d8dabec832a9cf82249bc20b3))
* linting helm ([9d1aac4](https://github.com/IA-Generative/ocr-api/commit/9d1aac499031bc9bbba0e3e8daf8c4f0f69baf5b))
* non root user into container ([8fb66d5](https://github.com/IA-Generative/ocr-api/commit/8fb66d5fc3016cc0a5ad038d5c3912297eeb5806))
* refresh gitleaksignore fingerprint after history rewrite ([773e764](https://github.com/IA-Generative/ocr-api/commit/773e764636bfcd02aa5938812046fd2a1a32361e))
* **release:** bump pyproject.toml/package.json on prerelease too ([ff85715](https://github.com/IA-Generative/ocr-api/commit/ff85715d5761eafa4d3d2dbda3f28e02295e333d))
* **security:** apt upgrade the api image's base packages ([#469](https://github.com/IA-Generative/ocr-api/issues/469)) ([a1f7fc7](https://github.com/IA-Generative/ocr-api/commit/a1f7fc7fc3eb0a414b32b7f4cd1d40ea84196b89))
* **security:** apt upgrade the worker image's base packages ([#469](https://github.com/IA-Generative/ocr-api/issues/469)) ([4c9ce58](https://github.com/IA-Generative/ocr-api/commit/4c9ce58a45e2fcb875e59038fae1c03884b07606))
* **security:** make the images usable under an arbitrary UID ([f9e2807](https://github.com/IA-Generative/ocr-api/commit/f9e2807b16adc7296cc62a994cd1feb1500521e5))
* **security:** stop leaking secrets into the keycloak container and drop an unread test env var ([2daf830](https://github.com/IA-Generative/ocr-api/commit/2daf8303403abb3b336ee99c0951fe7a79d8886a))
* sync gitleaksignore fingerprints onto this branch ([f297d13](https://github.com/IA-Generative/ocr-api/commit/f297d138475da259a5885b7d130f384fdf7467d9))
* **version:** correct path to pyproject.toml for version detection ([07f1122](https://github.com/IA-Generative/ocr-api/commit/07f112205c3f3438692e44716c30b157277f3ff2))
* **worker:** stop dropping pages 2+ of multi-page DOCX/PPTX/etc results ([d8ce56a](https://github.com/IA-Generative/ocr-api/commit/d8ce56a30a239eccce1e63e15da91927ba0aaf4d))


### Performance Improvements

* **client:** short-circuit the auth guard on an already-confirmed session ([6c9c5b4](https://github.com/IA-Generative/ocr-api/commit/6c9c5b4ce5b2dcfce91e989359005716aa49228d))
* **client:** stop copying node_modules into the docker build context ([627c743](https://github.com/IA-Generative/ocr-api/commit/627c74361418ad4b3815e86ea5b64a8cbfbdae60))
* update with latest package ([ba49a8f](https://github.com/IA-Generative/ocr-api/commit/ba49a8f1488d33fd44ba57c12aa8783b8e1d5c7c))


### Code Refactoring

* **frontend:** tighten task list types, drop any ([7ee64d9](https://github.com/IA-Generative/ocr-api/commit/7ee64d938e286471fa2ab42a84445682d9c23aab))
* **sdk:** move the Python SDK into sdk/python ([7cb0bd8](https://github.com/IA-Generative/ocr-api/commit/7cb0bd8230dd9a3ba0c267d4df80104a584ad488))


### Dependencies

* **deps:** bump Node to 24 LTS and upgrade the JS dependencies ([b76539a](https://github.com/IA-Generative/ocr-api/commit/b76539af8b8d0ca3634be857fc263cc796e17fc8))
* **deps:** migrate to pnpm 11 and refresh the container base images ([f8ab00c](https://github.com/IA-Generative/ocr-api/commit/f8ab00cc9ce07b60f2b3a656fa81bf6a0e3e5ed3))

## [0.20.0-rc.13](https://github.com/IA-Generative/ocr-api/compare/v0.20.0-rc.12...v0.20.0-rc.13) (2026-09-11)


### Bug Fixes

* **client:** keep the tasks tab up to date, add a manual refresh button ([5e9982c](https://github.com/IA-Generative/ocr-api/commit/5e9982cafeca3b46dbcf1a792e278b125ecca682))
* **worker:** stop dropping pages 2+ of multi-page DOCX/PPTX/etc results ([883b987](https://github.com/IA-Generative/ocr-api/commit/883b987d58bae1a8b5ed13cf4fb86b5504bdac14))

## [0.20.0-rc.12](https://github.com/IA-Generative/ocr-api/compare/v0.20.0-rc.11...v0.20.0-rc.12) (2026-09-11)


### Features

* **auth,sdk:** add refresh token support end-to-end ([afb61ca](https://github.com/IA-Generative/ocr-api/commit/afb61cac45e03fe7964046cc014259ed9d69f536))
* **auth:** add a password-grant token endpoint for non-browser clients ([bfdb8e4](https://github.com/IA-Generative/ocr-api/commit/bfdb8e41d66e6044679d135bc8b03fd1ad9b6c83))
* **sdk:** add a TypeScript/Node.js SDK (sdk/js) ([b5bbf1d](https://github.com/IA-Generative/ocr-api/commit/b5bbf1d247e7fcaa0eaba4c10a2919bf6f7e98a9))
* **sdk:** sync client routes/schemas with the API, add login() ([5bfb43b](https://github.com/IA-Generative/ocr-api/commit/5bfb43b3a66e28d441e58e5ac53a29840d581be0))


### Code Refactoring

* **sdk:** move the Python SDK into sdk/python ([8f0ac21](https://github.com/IA-Generative/ocr-api/commit/8f0ac21417fdd27d8f7bbaa91407b8e377ad5682))

## [0.20.0-rc.11](https://github.com/IA-Generative/ocr-api/compare/v0.20.0-rc.10...v0.20.0-rc.11) (2026-09-10)


### Features

* **client:** add GitHub and API docs links to the footer ([20984c6](https://github.com/IA-Generative/ocr-api/commit/20984c6fafa6f2596aae606e38413bd72e911c2a))

## [0.20.0-rc.10](https://github.com/IA-Generative/ocr-api/compare/v0.20.0-rc.9...v0.20.0-rc.10) (2026-09-10)


### Bug Fixes

* **frontend:** handle nullable percentage in the task sort comparator ([38f5f9e](https://github.com/IA-Generative/ocr-api/commit/38f5f9eec19bae0b3f473d207ff4166433d01ecb))
* **frontend:** paginate the user tasks list correctly ([1c76ab0](https://github.com/IA-Generative/ocr-api/commit/1c76ab050d1656ec72d72b562dd85a44addf99d1))


### Code Refactoring

* **frontend:** tighten task list types, drop any ([944d8c9](https://github.com/IA-Generative/ocr-api/commit/944d8c91125559e32d40ec5198b2851ecc3ad007))

## [0.20.0-rc.9](https://github.com/IA-Generative/ocr-api/compare/v0.20.0-rc.8...v0.20.0-rc.9) (2026-09-10)


### Bug Fixes

* **release:** bump pyproject.toml/package.json on prerelease too ([138b0f0](https://github.com/IA-Generative/ocr-api/commit/138b0f03c678ccd79596341169c2e2dae3abb21d))
* **version:** correct path to pyproject.toml for version detection ([42cf336](https://github.com/IA-Generative/ocr-api/commit/42cf3367e199341a8ef589e2114f57d53342a510))

## [0.20.0-rc.8](https://github.com/IA-Generative/ocr-api/compare/v0.20.0-rc.7...v0.20.0-rc.8) (2026-09-07)


### Features

* **bakend:** add auth other backend only ([b5acaee](https://github.com/IA-Generative/ocr-api/commit/b5acaee3870d4fcc00281d1454fe52ffff850ec1))


### Bug Fixes

* **auth:** add API_KEYS for machine-to-machine authentication ([5474913](https://github.com/IA-Generative/ocr-api/commit/5474913a7d3bd8ff73c60716b510e01aa0972471))
* **auth:** end the Keycloak SSO session on logout ([fb09c99](https://github.com/IA-Generative/ocr-api/commit/fb09c998fc120017037d8983c8d58e1ca1f40a25))
* **auth:** rate-limit /api/auth/login per client IP ([f531b66](https://github.com/IA-Generative/ocr-api/commit/f531b66465b5eefb9f470a6fb67996cbee7207d2))
* **auth:** reject cross-site logout requests as CSRF defense in depth ([d4faef6](https://github.com/IA-Generative/ocr-api/commit/d4faef63dc3f4d985e2b6534b58194e7c1a73bcf))
* **auth:** remove the VITE_SSO_BYPASS frontend auth-guard bypass ([5ca919c](https://github.com/IA-Generative/ocr-api/commit/5ca919c1496a5e4507cd5bd5d89322771ff4432d))
* **auth:** route login through keycloak-js and pin the redirect_uri ([5e7e835](https://github.com/IA-Generative/ocr-api/commit/5e7e8355d46f0814bb84acb8db4a6bb686198085))
* **auth:** stop trusting empty-subject/introspection claims and freeze roles ([b5522e6](https://github.com/IA-Generative/ocr-api/commit/b5522e66c6707361e69696692655b67981873fde))
* **auth:** strip trailing slash from BACKEND_PUBLIC_URL too ([449ae94](https://github.com/IA-Generative/ocr-api/commit/449ae94e7a37aeffbeb1ed2095364d6bc7484268))
* **client:** install libatomic1 for pnpm's native binary in the slim image ([b6e7a66](https://github.com/IA-Generative/ocr-api/commit/b6e7a66e3d0940b6a96131292e50addab3c39f6f))
* **security:** stop leaking secrets into the keycloak container and drop an unread test env var ([b8474b2](https://github.com/IA-Generative/ocr-api/commit/b8474b2850d6594405db4c21a9886ada6cd84698))


### Performance Improvements

* **client:** short-circuit the auth guard on an already-confirmed session ([43d5aa7](https://github.com/IA-Generative/ocr-api/commit/43d5aa7dd938aa4ebbfb2cdb19cd20d7606b8e78))
* **client:** stop copying node_modules into the docker build context ([ab81a23](https://github.com/IA-Generative/ocr-api/commit/ab81a23303059a7a284d764e86368ef2fe263307))

## [0.20.0-rc.7](https://github.com/IA-Generative/ocr-api/compare/v0.20.0-rc.6...v0.20.0-rc.7) (2026-09-04)


### Features

* **client:** display tasks as a tile grid instead of a table ([a30e898](https://github.com/IA-Generative/ocr-api/commit/a30e898101c1c8cf9ea6942671bbe02dbf912779))

## [0.20.0-rc.6](https://github.com/IA-Generative/ocr-api/compare/v0.20.0-rc.5...v0.20.0-rc.6) (2026-09-04)


### Bug Fixes

* **client:** correct pagination cursor and default bounding boxes display ([b6183ba](https://github.com/IA-Generative/ocr-api/commit/b6183ba99e9f1afa922a1f88d307dd4f0511487c))

## [0.20.0-rc.5](https://github.com/IA-Generative/ocr-api/compare/v0.20.0-rc.4...v0.20.0-rc.5) (2026-09-04)


### Bug Fixes

* **deps:** bump aiohttp, h2, tornado and transformers (darwin) to patched versions ([c516d88](https://github.com/IA-Generative/ocr-api/commit/c516d88cb33417cdb384dcaf08eba85e5e480d28))
* **deps:** pin transitive npm packages to patched versions via pnpm overrides ([9add913](https://github.com/IA-Generative/ocr-api/commit/9add9139a15a6c616e340d75e54efd0983405aa9))
* **security:** apt upgrade the api image's base packages ([#469](https://github.com/IA-Generative/ocr-api/issues/469)) ([b3f3788](https://github.com/IA-Generative/ocr-api/commit/b3f3788272d3c1be6aa37caf9e4495ff8c153b9a))
* **security:** apt upgrade the worker image's base packages ([#469](https://github.com/IA-Generative/ocr-api/issues/469)) ([915d2d8](https://github.com/IA-Generative/ocr-api/commit/915d2d8b7d0eb70c32a659074aa2d9d4e22ff29e))

## [0.20.0-rc.4](https://github.com/IA-Generative/ocr-api/compare/v0.20.0-rc.3...v0.20.0-rc.4) (2026-08-31)


### Bug Fixes

* **ci:** tag Harbor images with the chart appVersion ([ce88a38](https://github.com/IA-Generative/ocr-api/commit/ce88a38207a05d2fc018a9d08455c85dd82ba9a0))

## [0.20.0-rc.3](https://github.com/IA-Generative/ocr-api/compare/v0.20.0-rc.2...v0.20.0-rc.3) (2026-08-31)


### Bug Fixes

* **auth:** strip OIDC response params before Keycloak check-sso ([366269b](https://github.com/IA-Generative/ocr-api/commit/366269bc9af05c6da11c3aca971ebc4bc54687ce))
* **client:** install from the committed lockfile in the Docker image ([0e00ce2](https://github.com/IA-Generative/ocr-api/commit/0e00ce2e81921f16d02726ac8db14fa0f86660b7))


### Dependencies

* **deps:** bump Node to 24 LTS and upgrade the JS dependencies ([0d2df77](https://github.com/IA-Generative/ocr-api/commit/0d2df7722576046bcfa7f3af60ae598111b8bfb0))
* **deps:** migrate to pnpm 11 and refresh the container base images ([f5bc195](https://github.com/IA-Generative/ocr-api/commit/f5bc1957e3e902b5322942673defc8d5af861fad))

## [0.20.0-rc.2](https://github.com/IA-Generative/ocr-api/compare/v0.20.0-rc.1...v0.20.0-rc.2) (2026-08-25)


### Bug Fixes

* non root user into container ([13a3504](https://github.com/IA-Generative/ocr-api/commit/13a350430f0f44bec9100b52aeceb26116eefef6))
* **security:** make the images usable under an arbitrary UID ([ad4609f](https://github.com/IA-Generative/ocr-api/commit/ad4609f251df57312d7b78aff2cc53caff0a7abe))

## [0.20.0-rc.1](https://github.com/IA-Generative/ocr-api/compare/v0.20.0-rc...v0.20.0-rc.1) (2026-08-25)


### Bug Fixes

* sync gitleaksignore fingerprints onto this branch ([7c15ce7](https://github.com/IA-Generative/ocr-api/commit/7c15ce7b8c643c1d46716a959b834b8b06cc2876))

## [0.20.0-rc](https://github.com/IA-Generative/ocr-api/compare/v0.19.12-rc...v0.20.0-rc) (2026-08-25)


### Features

* gpu available ([7bb22c4](https://github.com/IA-Generative/ocr-api/commit/7bb22c457399da376ef68194b9c5a58c91167068))


### Bug Fixes

* delete commitizen ([539b022](https://github.com/IA-Generative/ocr-api/commit/539b022f12ba09444665c4052310800aa8f408f5))
* linting helm ([5453e69](https://github.com/IA-Generative/ocr-api/commit/5453e691fb6d435f0ca0effb548b721cb311a334))
* refresh gitleaksignore fingerprint after history rewrite ([ec5c09f](https://github.com/IA-Generative/ocr-api/commit/ec5c09fcee517d497c06cd031fcf570ff21e9e68))

## [0.19.12-rc](https://github.com/IA-Generative/ocr-api/compare/v0.19.11...v0.19.12-rc) (2026-08-24)


### Bug Fixes

* gitleak disbale false postif ([a9b9984](https://github.com/IA-Generative/ocr-api/commit/a9b99842ed5ba4d615e30284f14367c9a7731abf))


### Performance Improvements

* update with latest package ([d0c1084](https://github.com/IA-Generative/ocr-api/commit/d0c1084ac0213272bcf4b1d2377fbeb9264972dc))

## [0.19.11](https://github.com/IA-Generative/ocr-api/compare/v0.19.10...v0.19.11) (2026-08-14)


### Bug Fixes

* **tracing:** open a real langfuse observation for each task ([c2b9637](https://github.com/IA-Generative/ocr-api/commit/c2b9637a0ee7946e2fba9b513cd56b42b7ae560b))
* **tracing:** shut down the langfuse client when auth fails ([157ba89](https://github.com/IA-Generative/ocr-api/commit/157ba89a4fc5c21794744c92214872d4008665b3))

## [0.19.10](https://github.com/IA-Generative/ocr-api/compare/v0.19.9...v0.19.10) (2026-07-29)


### Bug Fixes

* llm ([24b582f](https://github.com/IA-Generative/ocr-api/commit/24b582f3d05e83f32d0ce93ea14c09f127a18015))

## [0.19.9](https://github.com/IA-Generative/ocr-api/compare/v0.19.8...v0.19.9) (2026-07-29)


### Bug Fixes

* **api:** api keys ([a195a0f](https://github.com/IA-Generative/ocr-api/commit/a195a0f1c8d2a12ee83e7cd509b54ddbc999a610))

## [0.19.8](https://github.com/IA-Generative/ocr-api/compare/v0.19.7...v0.19.8) (2026-07-29)


### Bug Fixes

* **vision:** fix vision ([01d5c8c](https://github.com/IA-Generative/ocr-api/commit/01d5c8c9a09764cdb604663a6ebbd1a92d208d19))

## [0.19.7](https://github.com/IA-Generative/ocr-api/compare/v0.19.6...v0.19.7) (2026-07-29)


### Bug Fixes

* **database:** fix fallback ([9a82db8](https://github.com/IA-Generative/ocr-api/commit/9a82db811c5d4549ef688e56b033b10514b3bd7b))

## [0.19.6](https://github.com/IA-Generative/ocr-api/compare/v0.19.5...v0.19.6) (2026-07-29)


### Bug Fixes

* **logging:** fix logging and var ([b0c06f4](https://github.com/IA-Generative/ocr-api/commit/b0c06f4e89bd141610e86a3e110a7866034b842d))

## [0.19.5](https://github.com/IA-Generative/ocr-api/compare/v0.19.4...v0.19.5) (2026-07-17)


### Bug Fixes

* kwargs add sentinel ([ef37e1b](https://github.com/IA-Generative/ocr-api/commit/ef37e1bbcd604505663c9d7e663200ef926c7310))

## [0.19.4](https://github.com/IA-Generative/ocr-api/compare/v0.19.3...v0.19.4) (2026-07-17)


### Bug Fixes

* **redis:** log redis pwd ([3d3aa65](https://github.com/IA-Generative/ocr-api/commit/3d3aa6518878a2387a25ab8e86e3647a5b9638a9))

## [0.19.3](https://github.com/IA-Generative/ocr-api/compare/v0.19.2...v0.19.3) (2026-07-17)


### Bug Fixes

* **logs:** add logs ([11b7c45](https://github.com/IA-Generative/ocr-api/commit/11b7c4533761c62922655cd840a2a6c409aec016))

## [0.19.2](https://github.com/IA-Generative/ocr-api/compare/v0.19.1...v0.19.2) (2026-07-17)


### Bug Fixes

* sentinel password ([84ea469](https://github.com/IA-Generative/ocr-api/commit/84ea469db132c663ea432349c82ac612005f4bb6))

## [0.19.1](https://github.com/IA-Generative/ocr-api/compare/v0.19.0...v0.19.1) (2026-07-17)


### Bug Fixes

* sentinel scheme ([4c4175f](https://github.com/IA-Generative/ocr-api/commit/4c4175fc3e05dd382c9ce0820f2ada92244f0c69))

## [0.19.0](https://github.com/IA-Generative/ocr-api/compare/v0.18.0...v0.19.0) (2026-07-15)


### Features

* **yt:** add youtube transcription ([940c57c](https://github.com/IA-Generative/ocr-api/commit/940c57ccd4c1c0d2e619ba88c0cb03d61c20b11c))

## [0.18.0](https://github.com/IA-Generative/ocr-api/compare/v0.17.0...v0.18.0) (2026-07-15)


### Features

* **eml+zip:** add eml and zip consideration ([92b20a3](https://github.com/IA-Generative/ocr-api/commit/92b20a334abe389f1b530bc228bf5d2173aca447))


### Bug Fixes

* **openwebui:** delete task and associated file after processing ([580ec7f](https://github.com/IA-Generative/ocr-api/commit/580ec7fee6132b37953b13fcc49615a93d1e50f0))
* url presigned ([8f4b45c](https://github.com/IA-Generative/ocr-api/commit/8f4b45cbf509bad5972d5254d50b5d8e4b1ec233))

## [0.17.0](https://github.com/IA-Generative/ocr-api/compare/v0.16.0...v0.17.0) (2026-07-09)


### Features

* add OpenWebUI router and endpoint for document processing ([a60c11b](https://github.com/IA-Generative/ocr-api/commit/a60c11becf3a7321a8a91274d64277c70973db1a))

## [0.16.0](https://github.com/IA-Generative/ocr-api/compare/v0.15.1...v0.16.0) (2026-07-09)


### Features

* add ZoneSelectionModal component and integrate with OcrViewer for enhanced zone selection functionality ([25219cb](https://github.com/IA-Generative/ocr-api/commit/25219cb504e4a49dc134431bca712e3759b95aee))
* enhance OcrViewer with search functionality and zone selection features ([47d400e](https://github.com/IA-Generative/ocr-api/commit/47d400ece50dca24ae4385531d6036e49ee419df))

## [0.15.1](https://github.com/IA-Generative/ocr-api/compare/v0.15.0...v0.15.1) (2026-07-09)


### Bug Fixes

* update langfuse dependency handling and versioning in configuration files ([5eaf7d1](https://github.com/IA-Generative/ocr-api/commit/5eaf7d136cfcc208ab44655214b83332558b00df))

## [0.15.0](https://github.com/IA-Generative/ocr-api/compare/v0.14.0...v0.15.0) (2026-07-09)


### Features

* add TaskDetail view and routing, enhance TasksTab with detail navigation ([218ac04](https://github.com/IA-Generative/ocr-api/commit/218ac0412d89a608913687a1aef6b3d45363c139))
* rename S3_BUCKET_NAME to AWS_BUCKET_NAME for consistency and update related documentation ([1c95b85](https://github.com/IA-Generative/ocr-api/commit/1c95b8593e836ddc785f979602d2842561753b22))

## [0.14.0](https://github.com/IA-Generative/ocr-api/compare/v0.13.0...v0.14.0) (2026-07-09)


### Features

* enhance Redis configuration with Sentinel support and improve database URL handling ([0c62b4b](https://github.com/IA-Generative/ocr-api/commit/0c62b4b7dac5829112a9ff4572612e85bccac03e))

## [0.13.0](https://github.com/IA-Generative/ocr-api/compare/v0.12.6...v0.13.0) (2026-07-09)


### Features

* add support for additional file formats in OCR upload and update hints ([61379a6](https://github.com/IA-Generative/ocr-api/commit/61379a602cfdd2f6ab2ee5c99e39baf8d6c6bd5f))
* integrate liteparse library and add liteparse worker ([bdc189e](https://github.com/IA-Generative/ocr-api/commit/bdc189e80d67c62b7a5c30a72b4b7446f92d085e))
* set multiprocessing start method to 'spawn' for PaddleOCR stability and initialize OCR pipeline in worker process ([2276ba3](https://github.com/IA-Generative/ocr-api/commit/2276ba3bf49518859e985d9408c7490795970b7b))

## [0.12.6](https://github.com/IA-Generative/ocr-api/compare/v0.12.5...v0.12.6) (2026-07-05)


### Bug Fixes

* **paddleocr:** remove enable_mkldnn parameter from PaddleOCR initialization ([f272783](https://github.com/IA-Generative/ocr-api/commit/f2727835d5033cf55d00d7ae6960048bfa11a559))
* **tracing:** update trace generation method in LangFuseTracingService ([f272783](https://github.com/IA-Generative/ocr-api/commit/f2727835d5033cf55d00d7ae6960048bfa11a559))

## [0.12.5](https://github.com/IA-Generative/ocr-api/compare/v0.12.4...v0.12.5) (2026-07-05)


### Bug Fixes

* **paddleocr:** update PaddleOCR model initialization and enhance inference tests ([bc9c870](https://github.com/IA-Generative/ocr-api/commit/bc9c870f9a1a46e648de6370ec1bb6cc69d9d342))

## [0.12.4](https://github.com/IA-Generative/ocr-api/compare/v0.12.3...v0.12.4) (2026-07-05)


### Bug Fixes

* **docker:** add TORCHINDUCTOR_CACHE_DIR environment variable to Dockerfiles ([61dd89a](https://github.com/IA-Generative/ocr-api/commit/61dd89a7a8e54ff93340bf02abe10efddcd31781))

## [0.12.3](https://github.com/IA-Generative/ocr-api/compare/v0.12.2...v0.12.3) (2026-07-01)


### Bug Fixes

* **security:** security fixed ([27d799c](https://github.com/IA-Generative/ocr-api/commit/27d799ced960c469c9a24cc29668b39afb6878d8))

## [0.12.2](https://github.com/IA-Generative/ocr-api/compare/v0.12.1...v0.12.2) (2026-07-01)


### Bug Fixes

* **dso:** ci for dso ([6e13d1c](https://github.com/IA-Generative/ocr-api/commit/6e13d1c28434b9a90b111e7ed810937f8d38f963))

## [0.12.1](https://github.com/IA-Generative/ocr-api/compare/v0.12.0...v0.12.1) (2026-06-30)


### Bug Fixes

* **ci:** fix release for dso ([54ca48c](https://github.com/IA-Generative/ocr-api/commit/54ca48c5eada21c37f42cb5ce9cca7fa43aef143))

## [0.12.0](https://github.com/IA-Generative/ocr-api/compare/v0.11.2...v0.12.0) (2026-06-30)


### Features

* **mark:** add markdown ([68facd7](https://github.com/IA-Generative/ocr-api/commit/68facd7a65c88f145d421ba921acea534a73e880))

## [0.11.2](https://github.com/IA-Generative/ocr-api/compare/v0.11.1...v0.11.2) (2026-06-30)


### Bug Fixes

* **ocr:** add newer version ([4fa3ba3](https://github.com/IA-Generative/ocr-api/commit/4fa3ba3fab444ea6751b0715b13f047e625cadbd))

## [0.11.1](https://github.com/IA-Generative/ocr-api/compare/v0.11.0...v0.11.1) (2026-06-30)


### Bug Fixes

* **security:** fix security depandabot ([f476009](https://github.com/IA-Generative/ocr-api/commit/f476009b133d21b69d50350efb07db48f8cdd671))

## [0.11.0](https://github.com/IA-Generative/ocr-api/compare/v0.10.1...v0.11.0) (2026-06-30)


### Features

* add NoCacheMiddleware to prevent caching of responses ([d87f098](https://github.com/IA-Generative/ocr-api/commit/d87f098f97bd94069cd486e37a45f5e80812d6fc))
* add unit tests for QdrantVectorStore and collection management functionality ([bc02737](https://github.com/IA-Generative/ocr-api/commit/bc027370b9c04bc0f42605b017efe1b8895548f5))
* enhance error handling and logging in BaseWorker, update storage file path in tests ([c14a428](https://github.com/IA-Generative/ocr-api/commit/c14a428da2399551fa1cb85a4ca834663fc73515))
* enhance S3 file handling with download functionality and filename management ([ffdc3a4](https://github.com/IA-Generative/ocr-api/commit/ffdc3a4032e3b85ca0484219b278cbfb520f9cfd))
* **ocr:** aligne with abrege ([9959e24](https://github.com/IA-Generative/ocr-api/commit/9959e240ece10b62103ad05fe583097d9ad63d88))
* report errors to Sentry for api, worker and frontend ([#398](https://github.com/IA-Generative/ocr-api/issues/398)) ([12df704](https://github.com/IA-Generative/ocr-api/commit/12df704f5c0b781d7322e453c9b12d5258eef977))


### Bug Fixes

* **ci:** correct tracing test assertion and stabilize SDK tests ([#399](https://github.com/IA-Generative/ocr-api/issues/399)) ([50bb1fb](https://github.com/IA-Generative/ocr-api/commit/50bb1fb1ea9f96367ffd7236af39df562d69a605))
* **ci:** release ([abf4236](https://github.com/IA-Generative/ocr-api/commit/abf4236eec3ab1a705e96a41907b3a3b0cf938e5))
* improve cache handling in TaskCache and streamline NoCacheMiddleware response headers ([0274dcc](https://github.com/IA-Generative/ocr-api/commit/0274dccdaa3917f0bd8ef53e9dda74184c79b85a))
* vulne ([b544f56](https://github.com/IA-Generative/ocr-api/commit/b544f56d620ba3bdb2b5817ebb59702ba871fe62))

## [0.10.1](https://github.com/IA-Generative/ocr-api/compare/v0.10.0...v0.10.1) (2026-04-07)


### Bug Fixes

* enable SSL verification for S3 client and improve code formatting ([#254](https://github.com/IA-Generative/ocr-api/issues/254)) ([33d197f](https://github.com/IA-Generative/ocr-api/commit/33d197f8fa8590a8de6c53fb1a8b68809e8bb7d0))

## [0.10.0](https://github.com/IA-Generative/ocr-api/compare/v0.9.0...v0.10.0) (2026-03-05)


### Features

* add OPENAI_API_KEY to environment configuration ([95de513](https://github.com/IA-Generative/ocr-api/commit/95de5131a084d84f35d1287df07fd518b2a659bc))


### Bug Fixes

* add missing version and tag_name outputs to release workflow ([9f69eeb](https://github.com/IA-Generative/ocr-api/commit/9f69eeb00da51d0beda9e90bfac4173983f7a5fe))
* **release:** unify release ([#246](https://github.com/IA-Generative/ocr-api/issues/246)) ([80c044c](https://github.com/IA-Generative/ocr-api/commit/80c044c545ffc92ef25df156aed7ff5645a19adb))
* update SDK test cases and improve Makefile for testing ([#242](https://github.com/IA-Generative/ocr-api/issues/242)) ([e00afd8](https://github.com/IA-Generative/ocr-api/commit/e00afd832068a76b072ddc3cb9a363a9a92a31b9))

## [0.9.0](https://github.com/IA-Generative/ocr-api/compare/v0.8.4...v0.9.0) (2026-02-17)


### Features

* add OPENAI_API_KEY to environment configuration ([95de513](https://github.com/IA-Generative/ocr-api/commit/95de5131a084d84f35d1287df07fd518b2a659bc))


### Bug Fixes

* add missing version and tag_name outputs to release workflow ([9f69eeb](https://github.com/IA-Generative/ocr-api/commit/9f69eeb00da51d0beda9e90bfac4173983f7a5fe))

## [0.8.4](https://github.com/IA-Generative/ocr-api/compare/v0.8.3...v0.8.4) (2026-02-16)


### Bug Fixes

* update SDK test cases and improve Makefile for testing ([#242](https://github.com/IA-Generative/ocr-api/issues/242)) ([e00afd8](https://github.com/IA-Generative/ocr-api/commit/e00afd832068a76b072ddc3cb9a363a9a92a31b9))

## [0.8.3](https://github.com/IA-Generative/ocr-api/compare/v0.8.2...v0.8.3) (2026-02-16)


### Bug Fixes

* update package names and include-component-in-tag settings in re… ([#238](https://github.com/IA-Generative/ocr-api/issues/238)) ([e41e106](https://github.com/IA-Generative/ocr-api/commit/e41e10695e4839e525cd5afccc1f675032a1c21e))

## [0.8.2](https://github.com/IA-Generative/ocr-api/compare/v0.8.1...v0.8.2) (2025-11-21)


### Bug Fixes

* add missing extraction files to Dockerfile ([0f3be43](https://github.com/IA-Generative/ocr-api/commit/0f3be43371cc68e2759d7b8ba70ab5661d365164))
* update package name in release-please manifest ([2786f37](https://github.com/IA-Generative/ocr-api/commit/2786f37b1ecd64607f0f34b579a56d28aecdaf4e))

## [0.8.1](https://github.com/IA-Generative/ocr-api/compare/v0.8.0...v0.8.1) (2025-10-27)


### Bug Fixes

* mettre à jour les chemins des liens dans la barre latérale ([78c54ea](https://github.com/IA-Generative/ocr-api/commit/78c54eaa3c94d030cb73deef41588911173b45a6))
* mettre à jour les liens des conditions d'utilisation et de la FAQ dans la barre latérale ([88e73de](https://github.com/IA-Generative/ocr-api/commit/88e73decd3986bb9dedbfe8c49cccc1368876300))

## [0.8.0](https://github.com/IA-Generative/ocr-api/compare/v0.7.0...v0.8.0) (2025-10-25)


### Features

* add document extraction support for multiple file formats ([026088c](https://github.com/IA-Generative/ocr-api/commit/026088cab3efb9cd2719fbb4039d70812e551612))
* add process router for document processing and related tests ([9f2473e](https://github.com/IA-Generative/ocr-api/commit/9f2473e8156fbafcc8d606f056b1acf199ae22bf))
* add set_page_text method to OCRResult for page text extraction ([3522ca4](https://github.com/IA-Generative/ocr-api/commit/3522ca4f3b849f5d0904d353c9bc320870146b2c))
* add test.csv file for validation in tests/data/valid ([69cfc75](https://github.com/IA-Generative/ocr-api/commit/69cfc755e6a7a84ffd45988f589503b466b7ee4a))

## [0.7.0](https://github.com/IA-Generative/ocr-api/compare/v0.6.0...v0.7.0) (2025-10-01)


### Features

* :art: add auth with backend ([8d5b74c](https://github.com/IA-Generative/ocr-api/commit/8d5b74cf18eedf7b0c4f9a1c73eee71404f8d120))
* :art: add headers to api ([ca4e425](https://github.com/IA-Generative/ocr-api/commit/ca4e425fd2d9f1a134d7ce5ee5491b22643f09ba))
* :chart_with_upwards_trend: add matomo tracking ([e0cbb46](https://github.com/IA-Generative/ocr-api/commit/e0cbb46d1487386dbca7ff3b35b7aa094a389fa6))
* :sparkles: add husky, pre-commit and commitlint ([5b77743](https://github.com/IA-Generative/ocr-api/commit/5b77743f85c7d229d33360347556121c213aef6b))
* :sparkles: update environment variables and improve sidebar links ([4a3f1e6](https://github.com/IA-Generative/ocr-api/commit/4a3f1e67158313ef84c757e05cb85ab68d95666f))
* add all text from pdf ([0ed2c8d](https://github.com/IA-Generative/ocr-api/commit/0ed2c8dfc5643272bbfe0f7d5eafc174da631d68))
* add configs directory copy to Dockerfile ([d54236b](https://github.com/IA-Generative/ocr-api/commit/d54236b08fed9727205591a1a810c438376a0adb))
* add delete routers ([701ed7d](https://github.com/IA-Generative/ocr-api/commit/701ed7d9573ecb9063848d3e6534034354707f06))
* add docling process ([96f7828](https://github.com/IA-Generative/ocr-api/commit/96f782802b6726e2ec6b34733978bdd1006a0262))
* add example curl commands for OCR API usage ([c3cc714](https://github.com/IA-Generative/ocr-api/commit/c3cc714a6e94f5b0deb42aeb0d1e88ec7633da1a))
* add Keycloak configuration details and OpenAI API variables to documentation ([ff217ac](https://github.com/IA-Generative/ocr-api/commit/ff217ac84f988c7da8e3193f5675f1eb5180150e))
* add ocr-docling group to Dockerfile build process ([96f7828](https://github.com/IA-Generative/ocr-api/commit/96f782802b6726e2ec6b34733978bdd1006a0262))
* add parameters column to tasks and update migration script ([a1f092a](https://github.com/IA-Generative/ocr-api/commit/a1f092ae75ae27dd3fe92e1f65e680f22f8feec9))
* add PDF forms extraction worker and related tests ([d1392d9](https://github.com/IA-Generative/ocr-api/commit/d1392d9f2bdd605f01d6e966a390575d4a0b46d4))
* add purge script for task deletion with Keycloak authentication ([b9197ca](https://github.com/IA-Generative/ocr-api/commit/b9197ca4192ecfe671f73d1bcd18d03682bce948))
* add workflow for testing services related to forms ([d5647b9](https://github.com/IA-Generative/ocr-api/commit/d5647b98afe4cec88e80c95275c071fc1cae12b9))
* **docs:** add Langfuse tracing configuration variables ([88ee3b5](https://github.com/IA-Generative/ocr-api/commit/88ee3b5172da4e43a3f8459c8d12542af8bf4d85))
* enhance Keycloak token verification and update dependencies ([af64177](https://github.com/IA-Generative/ocr-api/commit/af64177631d952c02da1a0cf77f40ca8b540f1d1))
* enhance task management with admin checks and update request context ([701ed7d](https://github.com/IA-Generative/ocr-api/commit/701ed7d9573ecb9063848d3e6534034354707f06))
* extract text and bounding boxes from PDF pages for improved data processing ([0ed2c8d](https://github.com/IA-Generative/ocr-api/commit/0ed2c8dfc5643272bbfe0f7d5eafc174da631d68))
* implement centralized logging configuration system ([d54236b](https://github.com/IA-Generative/ocr-api/commit/d54236b08fed9727205591a1a810c438376a0adb))
* integrate Keycloak authentication and update dependencies ([af64177](https://github.com/IA-Generative/ocr-api/commit/af64177631d952c02da1a0cf77f40ca8b540f1d1))
* integrate Keycloak for authentication and user management ([521a930](https://github.com/IA-Generative/ocr-api/commit/521a930719010e44b6ae39b4c4e5fb6d48a0354a))
* merge staging to preprod ([#144](https://github.com/IA-Generative/ocr-api/issues/144)) ([59cb5a8](https://github.com/IA-Generative/ocr-api/commit/59cb5a89691b75fa200af457c59b1b7e2896b5fc))
* refactor PDF form extraction, add vector and template management, and improve feature extraction ([cda4e3d](https://github.com/IA-Generative/ocr-api/commit/cda4e3d73c515ce5a0f20827c4d61fd59ecc3808))
* **security:** improve Keycloak token verification, logging, and documentation ([15c3b87](https://github.com/IA-Generative/ocr-api/commit/15c3b871a5d4ef77d339e1f3f0bf6555a8de1de8))
* update environment variables and refactor job and task routers for improved functionality ([af64177](https://github.com/IA-Generative/ocr-api/commit/af64177631d952c02da1a0cf77f40ca8b540f1d1))


### Bug Fixes

* :label: fix error types ts ([c3d1a13](https://github.com/IA-Generative/ocr-api/commit/c3d1a1377f0899cccb8696499abd3c4addcbebce))
* :passport_control: fixing keycloak infinity loop on sign in ([0bc8db0](https://github.com/IA-Generative/ocr-api/commit/0bc8db07a79b770b2e765fa607f4d5f240493217))
* :rocket: don't open twice file ([1ae8f31](https://github.com/IA-Generative/ocr-api/commit/1ae8f31ff1d34e822d07795411af3564bf688c3d))
* :white_check_mark: fix ocr e2e test ([f225d2f](https://github.com/IA-Generative/ocr-api/commit/f225d2f2e7fdbe5ac28b99fe34542c5d13d546e7))
* add clearToken when keycloak logout ([1fabd51](https://github.com/IA-Generative/ocr-api/commit/1fabd51be72115d858eb204512adacbf92e4340b))
* add docling_inference directory to Dockerfile ([3707056](https://github.com/IA-Generative/ocr-api/commit/37070567d0ad9f5aa77fe3d1b955b3c9df102a1d))
* add more log using user_id ([9b310c9](https://github.com/IA-Generative/ocr-api/commit/9b310c9a25ad8fdc73e15ffff17e3a3c82e5adb5))
* async routes ([#7](https://github.com/IA-Generative/ocr-api/issues/7)) ([525dddd](https://github.com/IA-Generative/ocr-api/commit/525dddd4ca418c396ced33c29953f4ac9a87f6e9))
* correct attribut href to in DsfrTile component ([43f670a](https://github.com/IA-Generative/ocr-api/commit/43f670a4171cbc6fe67a37bd00b87bda0ed97a6c))
* delete role in headers (not necessary) ([098d6a6](https://github.com/IA-Generative/ocr-api/commit/098d6a68f8ff74f0a3ff607f1e7c26b371395265))
* ensure task output pages are cleared for non-completed tasks and format delete function parameters ([edb41af](https://github.com/IA-Generative/ocr-api/commit/edb41afa9e0f4dd8b2117909cc168fa5b6a586a6))
* fix keycloak client id ([c5e932e](https://github.com/IA-Generative/ocr-api/commit/c5e932ea1e662d624c6816a6113e090f9660b209))
* hot fix lock ([2e93413](https://github.com/IA-Generative/ocr-api/commit/2e93413ed1802fa711a78a549b36d522fe013273))
* improve logging format and enhance trace context in launch_task ([084fc56](https://github.com/IA-Generative/ocr-api/commit/084fc56e6c5326a491c4e0a02a62f3312dcdd028))
* Refactor batch_predict method to improve handling of predictions and ensure non-null checks for better stability ([#55](https://github.com/IA-Generative/ocr-api/issues/55)) ([2ffdcfc](https://github.com/IA-Generative/ocr-api/commit/2ffdcfc07f2ff12b2cb399066e28a05bbd385de8))
* remove docling from dependencies and add ocr-docling group ([96f7828](https://github.com/IA-Generative/ocr-api/commit/96f782802b6726e2ec6b34733978bdd1006a0262))
* remove unused 'tags' parameter from LangFuseTracingService ([084fc56](https://github.com/IA-Generative/ocr-api/commit/084fc56e6c5326a491c4e0a02a62f3312dcdd028))
* simplify metadata handling in LangFuseTracingService ([084fc56](https://github.com/IA-Generative/ocr-api/commit/084fc56e6c5326a491c4e0a02a62f3312dcdd028))
* update apps/client/src/api/http-client.ts ([7012539](https://github.com/IA-Generative/ocr-api/commit/70125395a3408a92004ab257e178714f9d53f020))
* update apps/client/src/api/http-client.ts ([2d0704f](https://github.com/IA-Generative/ocr-api/commit/2d0704f6d0f7815c4e0a501990aa9ba80701b5eb))
* update apps/client/src/api/http-client.ts ([453edc0](https://github.com/IA-Generative/ocr-api/commit/453edc0c6203c9bfee29402161a96409e9b2f377))
* update apps/client/src/utils/keycloak.ts ([9bca0e0](https://github.com/IA-Generative/ocr-api/commit/9bca0e03a7c67386a9a1e87c17716943310ab5dc))
* update apps/client/src/utils/keycloak.ts ([cdfb2f9](https://github.com/IA-Generative/ocr-api/commit/cdfb2f9c1b9443ae4aff82e9c45e4397453d1574))
* update apps/client/src/utils/keycloak.ts ([12b3614](https://github.com/IA-Generative/ocr-api/commit/12b3614a3bb2aef2669ca0bebde8d43d8b20092d))
* update apps/client/src/utils/keycloak.ts ([655e2ee](https://github.com/IA-Generative/ocr-api/commit/655e2eeda630b3d6fce788d6c8f06a217c154915))
* update apps/client/src/utils/keycloak.ts ([cb674a4](https://github.com/IA-Generative/ocr-api/commit/cb674a44d5cc705345242179cc5d66b40620004b))
* update apps/client/src/utils/keycloak.ts ([cb0a6c0](https://github.com/IA-Generative/ocr-api/commit/cb0a6c096f9b1736ebf4f9aa10b978e3c1c11a04))
* update apps/client/src/utils/keycloak.ts ([0a5e16b](https://github.com/IA-Generative/ocr-api/commit/0a5e16bd52602d0618e1882cdd2e0619b45dcedd))
* update default task operation to use DEFAULT value in upload_file function ([e5b8162](https://github.com/IA-Generative/ocr-api/commit/e5b8162ea60664dad5e3b774d3d145bff6bec1f3))
* update maxfail option in test commands to allow all tests to run ([00616f0](https://github.com/IA-Generative/ocr-api/commit/00616f004ae19bee5a587ed5fd71c963091f79b4))
* update release workflow to correct manifest and config file paths ([93de8cc](https://github.com/IA-Generative/ocr-api/commit/93de8cc4636c41e568bec0a069972c37dc020388))
* use resource_access and client_id to get roles ([d22ac16](https://github.com/IA-Generative/ocr-api/commit/d22ac162de5acddd0700e8c45482c56bb9b0cb3c))

## [0.6.0](https://github.com/IA-Generative/ocr-api/compare/v0.5.0...v0.6.0) (2025-10-01)


### Features

* add purge script for task deletion with Keycloak authentication ([68b5ebb](https://github.com/IA-Generative/ocr-api/commit/68b5ebbfd960cc4e933a11a5aa3d0a8a8707f0e5))


### Bug Fixes

* use resource_access and client_id to get roles ([c1a26d7](https://github.com/IA-Generative/ocr-api/commit/c1a26d70274b5c5fd85d916c184cfb232594cd73))

## [0.5.0](https://github.com/IA-Generative/ocr-api/compare/v0.4.0...v0.5.0) (2025-09-29)


### Features

* :art: add auth with backend ([8d5b74c](https://github.com/IA-Generative/ocr-api/commit/8d5b74cf18eedf7b0c4f9a1c73eee71404f8d120))
* :art: add headers to api ([ca4e425](https://github.com/IA-Generative/ocr-api/commit/ca4e425fd2d9f1a134d7ce5ee5491b22643f09ba))
* :chart_with_upwards_trend: add matomo tracking ([e0cbb46](https://github.com/IA-Generative/ocr-api/commit/e0cbb46d1487386dbca7ff3b35b7aa094a389fa6))
* :sparkles: add husky, pre-commit and commitlint ([5b77743](https://github.com/IA-Generative/ocr-api/commit/5b77743f85c7d229d33360347556121c213aef6b))
* :sparkles: update environment variables and improve sidebar links ([4a3f1e6](https://github.com/IA-Generative/ocr-api/commit/4a3f1e67158313ef84c757e05cb85ab68d95666f))
* add all text from pdf ([0ed2c8d](https://github.com/IA-Generative/ocr-api/commit/0ed2c8dfc5643272bbfe0f7d5eafc174da631d68))
* add configs directory copy to Dockerfile ([d54236b](https://github.com/IA-Generative/ocr-api/commit/d54236b08fed9727205591a1a810c438376a0adb))
* add delete routers ([701ed7d](https://github.com/IA-Generative/ocr-api/commit/701ed7d9573ecb9063848d3e6534034354707f06))
* add docling process ([96f7828](https://github.com/IA-Generative/ocr-api/commit/96f782802b6726e2ec6b34733978bdd1006a0262))
* add example curl commands for OCR API usage ([c3cc714](https://github.com/IA-Generative/ocr-api/commit/c3cc714a6e94f5b0deb42aeb0d1e88ec7633da1a))
* add Keycloak configuration details and OpenAI API variables to documentation ([ff217ac](https://github.com/IA-Generative/ocr-api/commit/ff217ac84f988c7da8e3193f5675f1eb5180150e))
* add ocr-docling group to Dockerfile build process ([96f7828](https://github.com/IA-Generative/ocr-api/commit/96f782802b6726e2ec6b34733978bdd1006a0262))
* add parameters column to tasks and update migration script ([a1f092a](https://github.com/IA-Generative/ocr-api/commit/a1f092ae75ae27dd3fe92e1f65e680f22f8feec9))
* add PDF forms extraction worker and related tests ([d1392d9](https://github.com/IA-Generative/ocr-api/commit/d1392d9f2bdd605f01d6e966a390575d4a0b46d4))
* add workflow for testing services related to forms ([d5647b9](https://github.com/IA-Generative/ocr-api/commit/d5647b98afe4cec88e80c95275c071fc1cae12b9))
* **docs:** add Langfuse tracing configuration variables ([88ee3b5](https://github.com/IA-Generative/ocr-api/commit/88ee3b5172da4e43a3f8459c8d12542af8bf4d85))
* enhance Keycloak token verification and update dependencies ([af64177](https://github.com/IA-Generative/ocr-api/commit/af64177631d952c02da1a0cf77f40ca8b540f1d1))
* enhance task management with admin checks and update request context ([701ed7d](https://github.com/IA-Generative/ocr-api/commit/701ed7d9573ecb9063848d3e6534034354707f06))
* extract text and bounding boxes from PDF pages for improved data processing ([0ed2c8d](https://github.com/IA-Generative/ocr-api/commit/0ed2c8dfc5643272bbfe0f7d5eafc174da631d68))
* implement centralized logging configuration system ([d54236b](https://github.com/IA-Generative/ocr-api/commit/d54236b08fed9727205591a1a810c438376a0adb))
* integrate Keycloak authentication and update dependencies ([af64177](https://github.com/IA-Generative/ocr-api/commit/af64177631d952c02da1a0cf77f40ca8b540f1d1))
* integrate Keycloak for authentication and user management ([521a930](https://github.com/IA-Generative/ocr-api/commit/521a930719010e44b6ae39b4c4e5fb6d48a0354a))
* merge staging to preprod ([#144](https://github.com/IA-Generative/ocr-api/issues/144)) ([59cb5a8](https://github.com/IA-Generative/ocr-api/commit/59cb5a89691b75fa200af457c59b1b7e2896b5fc))
* refactor PDF form extraction, add vector and template management, and improve feature extraction ([cda4e3d](https://github.com/IA-Generative/ocr-api/commit/cda4e3d73c515ce5a0f20827c4d61fd59ecc3808))
* **security:** improve Keycloak token verification, logging, and documentation ([15c3b87](https://github.com/IA-Generative/ocr-api/commit/15c3b871a5d4ef77d339e1f3f0bf6555a8de1de8))
* update environment variables and refactor job and task routers for improved functionality ([af64177](https://github.com/IA-Generative/ocr-api/commit/af64177631d952c02da1a0cf77f40ca8b540f1d1))


### Bug Fixes

* :label: fix error types ts ([c3d1a13](https://github.com/IA-Generative/ocr-api/commit/c3d1a1377f0899cccb8696499abd3c4addcbebce))
* :passport_control: fixing keycloak infinity loop on sign in ([0bc8db0](https://github.com/IA-Generative/ocr-api/commit/0bc8db07a79b770b2e765fa607f4d5f240493217))
* :rocket: don't open twice file ([1ae8f31](https://github.com/IA-Generative/ocr-api/commit/1ae8f31ff1d34e822d07795411af3564bf688c3d))
* :white_check_mark: fix ocr e2e test ([f225d2f](https://github.com/IA-Generative/ocr-api/commit/f225d2f2e7fdbe5ac28b99fe34542c5d13d546e7))
* add clearToken when keycloak logout ([1fabd51](https://github.com/IA-Generative/ocr-api/commit/1fabd51be72115d858eb204512adacbf92e4340b))
* add docling_inference directory to Dockerfile ([3707056](https://github.com/IA-Generative/ocr-api/commit/37070567d0ad9f5aa77fe3d1b955b3c9df102a1d))
* add more log using user_id ([9b310c9](https://github.com/IA-Generative/ocr-api/commit/9b310c9a25ad8fdc73e15ffff17e3a3c82e5adb5))
* async routes ([#7](https://github.com/IA-Generative/ocr-api/issues/7)) ([525dddd](https://github.com/IA-Generative/ocr-api/commit/525dddd4ca418c396ced33c29953f4ac9a87f6e9))
* correct attribut href to in DsfrTile component ([43f670a](https://github.com/IA-Generative/ocr-api/commit/43f670a4171cbc6fe67a37bd00b87bda0ed97a6c))
* delete role in headers (not necessary) ([098d6a6](https://github.com/IA-Generative/ocr-api/commit/098d6a68f8ff74f0a3ff607f1e7c26b371395265))
* ensure task output pages are cleared for non-completed tasks and format delete function parameters ([edb41af](https://github.com/IA-Generative/ocr-api/commit/edb41afa9e0f4dd8b2117909cc168fa5b6a586a6))
* fix keycloak client id ([c5e932e](https://github.com/IA-Generative/ocr-api/commit/c5e932ea1e662d624c6816a6113e090f9660b209))
* hot fix lock ([2e93413](https://github.com/IA-Generative/ocr-api/commit/2e93413ed1802fa711a78a549b36d522fe013273))
* improve logging format and enhance trace context in launch_task ([084fc56](https://github.com/IA-Generative/ocr-api/commit/084fc56e6c5326a491c4e0a02a62f3312dcdd028))
* Refactor batch_predict method to improve handling of predictions and ensure non-null checks for better stability ([#55](https://github.com/IA-Generative/ocr-api/issues/55)) ([2ffdcfc](https://github.com/IA-Generative/ocr-api/commit/2ffdcfc07f2ff12b2cb399066e28a05bbd385de8))
* remove docling from dependencies and add ocr-docling group ([96f7828](https://github.com/IA-Generative/ocr-api/commit/96f782802b6726e2ec6b34733978bdd1006a0262))
* remove unused 'tags' parameter from LangFuseTracingService ([084fc56](https://github.com/IA-Generative/ocr-api/commit/084fc56e6c5326a491c4e0a02a62f3312dcdd028))
* simplify metadata handling in LangFuseTracingService ([084fc56](https://github.com/IA-Generative/ocr-api/commit/084fc56e6c5326a491c4e0a02a62f3312dcdd028))
* update apps/client/src/api/http-client.ts ([7012539](https://github.com/IA-Generative/ocr-api/commit/70125395a3408a92004ab257e178714f9d53f020))
* update apps/client/src/api/http-client.ts ([2d0704f](https://github.com/IA-Generative/ocr-api/commit/2d0704f6d0f7815c4e0a501990aa9ba80701b5eb))
* update apps/client/src/api/http-client.ts ([453edc0](https://github.com/IA-Generative/ocr-api/commit/453edc0c6203c9bfee29402161a96409e9b2f377))
* update apps/client/src/utils/keycloak.ts ([9bca0e0](https://github.com/IA-Generative/ocr-api/commit/9bca0e03a7c67386a9a1e87c17716943310ab5dc))
* update apps/client/src/utils/keycloak.ts ([cdfb2f9](https://github.com/IA-Generative/ocr-api/commit/cdfb2f9c1b9443ae4aff82e9c45e4397453d1574))
* update apps/client/src/utils/keycloak.ts ([12b3614](https://github.com/IA-Generative/ocr-api/commit/12b3614a3bb2aef2669ca0bebde8d43d8b20092d))
* update apps/client/src/utils/keycloak.ts ([655e2ee](https://github.com/IA-Generative/ocr-api/commit/655e2eeda630b3d6fce788d6c8f06a217c154915))
* update apps/client/src/utils/keycloak.ts ([cb674a4](https://github.com/IA-Generative/ocr-api/commit/cb674a44d5cc705345242179cc5d66b40620004b))
* update apps/client/src/utils/keycloak.ts ([cb0a6c0](https://github.com/IA-Generative/ocr-api/commit/cb0a6c096f9b1736ebf4f9aa10b978e3c1c11a04))
* update apps/client/src/utils/keycloak.ts ([0a5e16b](https://github.com/IA-Generative/ocr-api/commit/0a5e16bd52602d0618e1882cdd2e0619b45dcedd))
* update default task operation to use DEFAULT value in upload_file function ([e5b8162](https://github.com/IA-Generative/ocr-api/commit/e5b8162ea60664dad5e3b774d3d145bff6bec1f3))
* update maxfail option in test commands to allow all tests to run ([00616f0](https://github.com/IA-Generative/ocr-api/commit/00616f004ae19bee5a587ed5fd71c963091f79b4))
* update release workflow to correct manifest and config file paths ([93de8cc](https://github.com/IA-Generative/ocr-api/commit/93de8cc4636c41e568bec0a069972c37dc020388))

## [0.4.0](https://github.com/IA-Generative/ocr-api/compare/v0.3.0...v0.4.0) (2025-09-29)


### Features

* **docs:** add Langfuse tracing configuration variables ([56fe229](https://github.com/IA-Generative/ocr-api/commit/56fe22991c1c72c20dfa792af08486896cc99abb))


### Bug Fixes

* improve logging format and enhance trace context in launch_task ([8fc774f](https://github.com/IA-Generative/ocr-api/commit/8fc774f4392eaf677f7c9619dd89d9ea69202123))
* remove unused 'tags' parameter from LangFuseTracingService ([8fc774f](https://github.com/IA-Generative/ocr-api/commit/8fc774f4392eaf677f7c9619dd89d9ea69202123))
* simplify metadata handling in LangFuseTracingService ([8fc774f](https://github.com/IA-Generative/ocr-api/commit/8fc774f4392eaf677f7c9619dd89d9ea69202123))

## [0.3.0](https://github.com/IA-Generative/ocr-api/compare/v0.2.0...v0.3.0) (2025-09-27)


### Features

* :art: add auth with backend ([8d5b74c](https://github.com/IA-Generative/ocr-api/commit/8d5b74cf18eedf7b0c4f9a1c73eee71404f8d120))
* :art: add headers to api ([ca4e425](https://github.com/IA-Generative/ocr-api/commit/ca4e425fd2d9f1a134d7ce5ee5491b22643f09ba))
* :chart_with_upwards_trend: add matomo tracking ([e0cbb46](https://github.com/IA-Generative/ocr-api/commit/e0cbb46d1487386dbca7ff3b35b7aa094a389fa6))
* :sparkles: add husky, pre-commit and commitlint ([5b77743](https://github.com/IA-Generative/ocr-api/commit/5b77743f85c7d229d33360347556121c213aef6b))
* :sparkles: update environment variables and improve sidebar links ([4a3f1e6](https://github.com/IA-Generative/ocr-api/commit/4a3f1e67158313ef84c757e05cb85ab68d95666f))
* add all text from pdf ([0ed2c8d](https://github.com/IA-Generative/ocr-api/commit/0ed2c8dfc5643272bbfe0f7d5eafc174da631d68))
* add configs directory copy to Dockerfile ([d54236b](https://github.com/IA-Generative/ocr-api/commit/d54236b08fed9727205591a1a810c438376a0adb))
* add delete routers ([701ed7d](https://github.com/IA-Generative/ocr-api/commit/701ed7d9573ecb9063848d3e6534034354707f06))
* add docling process ([96f7828](https://github.com/IA-Generative/ocr-api/commit/96f782802b6726e2ec6b34733978bdd1006a0262))
* add example curl commands for OCR API usage ([c3cc714](https://github.com/IA-Generative/ocr-api/commit/c3cc714a6e94f5b0deb42aeb0d1e88ec7633da1a))
* add Keycloak configuration details and OpenAI API variables to documentation ([ff217ac](https://github.com/IA-Generative/ocr-api/commit/ff217ac84f988c7da8e3193f5675f1eb5180150e))
* add ocr-docling group to Dockerfile build process ([96f7828](https://github.com/IA-Generative/ocr-api/commit/96f782802b6726e2ec6b34733978bdd1006a0262))
* add parameters column to tasks and update migration script ([a1f092a](https://github.com/IA-Generative/ocr-api/commit/a1f092ae75ae27dd3fe92e1f65e680f22f8feec9))
* add PDF forms extraction worker and related tests ([d1392d9](https://github.com/IA-Generative/ocr-api/commit/d1392d9f2bdd605f01d6e966a390575d4a0b46d4))
* add workflow for testing services related to forms ([d5647b9](https://github.com/IA-Generative/ocr-api/commit/d5647b98afe4cec88e80c95275c071fc1cae12b9))
* enhance Keycloak token verification and update dependencies ([af64177](https://github.com/IA-Generative/ocr-api/commit/af64177631d952c02da1a0cf77f40ca8b540f1d1))
* enhance task management with admin checks and update request context ([701ed7d](https://github.com/IA-Generative/ocr-api/commit/701ed7d9573ecb9063848d3e6534034354707f06))
* extract text and bounding boxes from PDF pages for improved data processing ([0ed2c8d](https://github.com/IA-Generative/ocr-api/commit/0ed2c8dfc5643272bbfe0f7d5eafc174da631d68))
* implement centralized logging configuration system ([d54236b](https://github.com/IA-Generative/ocr-api/commit/d54236b08fed9727205591a1a810c438376a0adb))
* integrate Keycloak authentication and update dependencies ([af64177](https://github.com/IA-Generative/ocr-api/commit/af64177631d952c02da1a0cf77f40ca8b540f1d1))
* integrate Keycloak for authentication and user management ([521a930](https://github.com/IA-Generative/ocr-api/commit/521a930719010e44b6ae39b4c4e5fb6d48a0354a))
* merge staging to preprod ([#144](https://github.com/IA-Generative/ocr-api/issues/144)) ([59cb5a8](https://github.com/IA-Generative/ocr-api/commit/59cb5a89691b75fa200af457c59b1b7e2896b5fc))
* refactor PDF form extraction, add vector and template management, and improve feature extraction ([cda4e3d](https://github.com/IA-Generative/ocr-api/commit/cda4e3d73c515ce5a0f20827c4d61fd59ecc3808))
* **security:** improve Keycloak token verification, logging, and documentation ([15c3b87](https://github.com/IA-Generative/ocr-api/commit/15c3b871a5d4ef77d339e1f3f0bf6555a8de1de8))
* update environment variables and refactor job and task routers for improved functionality ([af64177](https://github.com/IA-Generative/ocr-api/commit/af64177631d952c02da1a0cf77f40ca8b540f1d1))


### Bug Fixes

* :label: fix error types ts ([c3d1a13](https://github.com/IA-Generative/ocr-api/commit/c3d1a1377f0899cccb8696499abd3c4addcbebce))
* :passport_control: fixing keycloak infinity loop on sign in ([0bc8db0](https://github.com/IA-Generative/ocr-api/commit/0bc8db07a79b770b2e765fa607f4d5f240493217))
* :rocket: don't open twice file ([1ae8f31](https://github.com/IA-Generative/ocr-api/commit/1ae8f31ff1d34e822d07795411af3564bf688c3d))
* :white_check_mark: fix ocr e2e test ([f225d2f](https://github.com/IA-Generative/ocr-api/commit/f225d2f2e7fdbe5ac28b99fe34542c5d13d546e7))
* add clearToken when keycloak logout ([1fabd51](https://github.com/IA-Generative/ocr-api/commit/1fabd51be72115d858eb204512adacbf92e4340b))
* add docling_inference directory to Dockerfile ([3707056](https://github.com/IA-Generative/ocr-api/commit/37070567d0ad9f5aa77fe3d1b955b3c9df102a1d))
* add more log using user_id ([9b310c9](https://github.com/IA-Generative/ocr-api/commit/9b310c9a25ad8fdc73e15ffff17e3a3c82e5adb5))
* async routes ([#7](https://github.com/IA-Generative/ocr-api/issues/7)) ([525dddd](https://github.com/IA-Generative/ocr-api/commit/525dddd4ca418c396ced33c29953f4ac9a87f6e9))
* correct attribut href to in DsfrTile component ([43f670a](https://github.com/IA-Generative/ocr-api/commit/43f670a4171cbc6fe67a37bd00b87bda0ed97a6c))
* delete role in headers (not necessary) ([098d6a6](https://github.com/IA-Generative/ocr-api/commit/098d6a68f8ff74f0a3ff607f1e7c26b371395265))
* ensure task output pages are cleared for non-completed tasks and format delete function parameters ([edb41af](https://github.com/IA-Generative/ocr-api/commit/edb41afa9e0f4dd8b2117909cc168fa5b6a586a6))
* fix keycloak client id ([c5e932e](https://github.com/IA-Generative/ocr-api/commit/c5e932ea1e662d624c6816a6113e090f9660b209))
* hot fix lock ([2e93413](https://github.com/IA-Generative/ocr-api/commit/2e93413ed1802fa711a78a549b36d522fe013273))
* Refactor batch_predict method to improve handling of predictions and ensure non-null checks for better stability ([#55](https://github.com/IA-Generative/ocr-api/issues/55)) ([2ffdcfc](https://github.com/IA-Generative/ocr-api/commit/2ffdcfc07f2ff12b2cb399066e28a05bbd385de8))
* remove docling from dependencies and add ocr-docling group ([96f7828](https://github.com/IA-Generative/ocr-api/commit/96f782802b6726e2ec6b34733978bdd1006a0262))
* update apps/client/src/api/http-client.ts ([7012539](https://github.com/IA-Generative/ocr-api/commit/70125395a3408a92004ab257e178714f9d53f020))
* update apps/client/src/api/http-client.ts ([2d0704f](https://github.com/IA-Generative/ocr-api/commit/2d0704f6d0f7815c4e0a501990aa9ba80701b5eb))
* update apps/client/src/api/http-client.ts ([453edc0](https://github.com/IA-Generative/ocr-api/commit/453edc0c6203c9bfee29402161a96409e9b2f377))
* update apps/client/src/utils/keycloak.ts ([9bca0e0](https://github.com/IA-Generative/ocr-api/commit/9bca0e03a7c67386a9a1e87c17716943310ab5dc))
* update apps/client/src/utils/keycloak.ts ([cdfb2f9](https://github.com/IA-Generative/ocr-api/commit/cdfb2f9c1b9443ae4aff82e9c45e4397453d1574))
* update apps/client/src/utils/keycloak.ts ([12b3614](https://github.com/IA-Generative/ocr-api/commit/12b3614a3bb2aef2669ca0bebde8d43d8b20092d))
* update apps/client/src/utils/keycloak.ts ([655e2ee](https://github.com/IA-Generative/ocr-api/commit/655e2eeda630b3d6fce788d6c8f06a217c154915))
* update apps/client/src/utils/keycloak.ts ([cb674a4](https://github.com/IA-Generative/ocr-api/commit/cb674a44d5cc705345242179cc5d66b40620004b))
* update apps/client/src/utils/keycloak.ts ([cb0a6c0](https://github.com/IA-Generative/ocr-api/commit/cb0a6c096f9b1736ebf4f9aa10b978e3c1c11a04))
* update apps/client/src/utils/keycloak.ts ([0a5e16b](https://github.com/IA-Generative/ocr-api/commit/0a5e16bd52602d0618e1882cdd2e0619b45dcedd))
* update default task operation to use DEFAULT value in upload_file function ([e5b8162](https://github.com/IA-Generative/ocr-api/commit/e5b8162ea60664dad5e3b774d3d145bff6bec1f3))
* update maxfail option in test commands to allow all tests to run ([00616f0](https://github.com/IA-Generative/ocr-api/commit/00616f004ae19bee5a587ed5fd71c963091f79b4))
* update release workflow to correct manifest and config file paths ([93de8cc](https://github.com/IA-Generative/ocr-api/commit/93de8cc4636c41e568bec0a069972c37dc020388))

## [0.2.0](https://github.com/IA-Generative/ocr-api/compare/v0.1.0...v0.2.0) (2025-09-27)


### Features

* :art: add auth with backend ([8d5b74c](https://github.com/IA-Generative/ocr-api/commit/8d5b74cf18eedf7b0c4f9a1c73eee71404f8d120))
* :art: add headers to api ([ca4e425](https://github.com/IA-Generative/ocr-api/commit/ca4e425fd2d9f1a134d7ce5ee5491b22643f09ba))
* :chart_with_upwards_trend: add matomo tracking ([e0cbb46](https://github.com/IA-Generative/ocr-api/commit/e0cbb46d1487386dbca7ff3b35b7aa094a389fa6))
* :sparkles: add husky, pre-commit and commitlint ([92b152b](https://github.com/IA-Generative/ocr-api/commit/92b152b21947314961b53ef6e236b108ce0a9b03))
* :sparkles: update environment variables and improve sidebar links ([4a3f1e6](https://github.com/IA-Generative/ocr-api/commit/4a3f1e67158313ef84c757e05cb85ab68d95666f))
* add all text from pdf ([0ed2c8d](https://github.com/IA-Generative/ocr-api/commit/0ed2c8dfc5643272bbfe0f7d5eafc174da631d68))
* add configs directory copy to Dockerfile ([d54236b](https://github.com/IA-Generative/ocr-api/commit/d54236b08fed9727205591a1a810c438376a0adb))
* add delete routers ([701ed7d](https://github.com/IA-Generative/ocr-api/commit/701ed7d9573ecb9063848d3e6534034354707f06))
* add docling process ([96f7828](https://github.com/IA-Generative/ocr-api/commit/96f782802b6726e2ec6b34733978bdd1006a0262))
* add example curl commands for OCR API usage ([c3cc714](https://github.com/IA-Generative/ocr-api/commit/c3cc714a6e94f5b0deb42aeb0d1e88ec7633da1a))
* add Keycloak configuration details and OpenAI API variables to documentation ([ff217ac](https://github.com/IA-Generative/ocr-api/commit/ff217ac84f988c7da8e3193f5675f1eb5180150e))
* add ocr-docling group to Dockerfile build process ([96f7828](https://github.com/IA-Generative/ocr-api/commit/96f782802b6726e2ec6b34733978bdd1006a0262))
* add parameters column to tasks and update migration script ([a1f092a](https://github.com/IA-Generative/ocr-api/commit/a1f092ae75ae27dd3fe92e1f65e680f22f8feec9))
* add PDF forms extraction worker and related tests ([d1392d9](https://github.com/IA-Generative/ocr-api/commit/d1392d9f2bdd605f01d6e966a390575d4a0b46d4))
* add workflow for testing services related to forms ([d5647b9](https://github.com/IA-Generative/ocr-api/commit/d5647b98afe4cec88e80c95275c071fc1cae12b9))
* enhance Keycloak token verification and update dependencies ([af64177](https://github.com/IA-Generative/ocr-api/commit/af64177631d952c02da1a0cf77f40ca8b540f1d1))
* enhance task management with admin checks and update request context ([701ed7d](https://github.com/IA-Generative/ocr-api/commit/701ed7d9573ecb9063848d3e6534034354707f06))
* extract text and bounding boxes from PDF pages for improved data processing ([0ed2c8d](https://github.com/IA-Generative/ocr-api/commit/0ed2c8dfc5643272bbfe0f7d5eafc174da631d68))
* implement centralized logging configuration system ([d54236b](https://github.com/IA-Generative/ocr-api/commit/d54236b08fed9727205591a1a810c438376a0adb))
* integrate Keycloak authentication and update dependencies ([af64177](https://github.com/IA-Generative/ocr-api/commit/af64177631d952c02da1a0cf77f40ca8b540f1d1))
* integrate Keycloak for authentication and user management ([521a930](https://github.com/IA-Generative/ocr-api/commit/521a930719010e44b6ae39b4c4e5fb6d48a0354a))
* merge staging to preprod ([#144](https://github.com/IA-Generative/ocr-api/issues/144)) ([59cb5a8](https://github.com/IA-Generative/ocr-api/commit/59cb5a89691b75fa200af457c59b1b7e2896b5fc))
* refactor PDF form extraction, add vector and template management, and improve feature extraction ([cda4e3d](https://github.com/IA-Generative/ocr-api/commit/cda4e3d73c515ce5a0f20827c4d61fd59ecc3808))
* **security:** improve Keycloak token verification, logging, and documentation ([15c3b87](https://github.com/IA-Generative/ocr-api/commit/15c3b871a5d4ef77d339e1f3f0bf6555a8de1de8))
* update environment variables and refactor job and task routers for improved functionality ([af64177](https://github.com/IA-Generative/ocr-api/commit/af64177631d952c02da1a0cf77f40ca8b540f1d1))


### Bug Fixes

* :label: fix error types ts ([c3d1a13](https://github.com/IA-Generative/ocr-api/commit/c3d1a1377f0899cccb8696499abd3c4addcbebce))
* :passport_control: fixing keycloak infinity loop on sign in ([0bc8db0](https://github.com/IA-Generative/ocr-api/commit/0bc8db07a79b770b2e765fa607f4d5f240493217))
* :rocket: don't open twice file ([1ae8f31](https://github.com/IA-Generative/ocr-api/commit/1ae8f31ff1d34e822d07795411af3564bf688c3d))
* :white_check_mark: fix ocr e2e test ([f225d2f](https://github.com/IA-Generative/ocr-api/commit/f225d2f2e7fdbe5ac28b99fe34542c5d13d546e7))
* add clearToken when keycloak logout ([1fabd51](https://github.com/IA-Generative/ocr-api/commit/1fabd51be72115d858eb204512adacbf92e4340b))
* add docling_inference directory to Dockerfile ([3707056](https://github.com/IA-Generative/ocr-api/commit/37070567d0ad9f5aa77fe3d1b955b3c9df102a1d))
* add more log using user_id ([9b310c9](https://github.com/IA-Generative/ocr-api/commit/9b310c9a25ad8fdc73e15ffff17e3a3c82e5adb5))
* async routes ([#7](https://github.com/IA-Generative/ocr-api/issues/7)) ([525dddd](https://github.com/IA-Generative/ocr-api/commit/525dddd4ca418c396ced33c29953f4ac9a87f6e9))
* correct attribut href to in DsfrTile component ([43f670a](https://github.com/IA-Generative/ocr-api/commit/43f670a4171cbc6fe67a37bd00b87bda0ed97a6c))
* delete role in headers (not necessary) ([098d6a6](https://github.com/IA-Generative/ocr-api/commit/098d6a68f8ff74f0a3ff607f1e7c26b371395265))
* ensure task output pages are cleared for non-completed tasks and format delete function parameters ([edb41af](https://github.com/IA-Generative/ocr-api/commit/edb41afa9e0f4dd8b2117909cc168fa5b6a586a6))
* fix keycloak client id ([c5e932e](https://github.com/IA-Generative/ocr-api/commit/c5e932ea1e662d624c6816a6113e090f9660b209))
* hot fix lock ([2e93413](https://github.com/IA-Generative/ocr-api/commit/2e93413ed1802fa711a78a549b36d522fe013273))
* Refactor batch_predict method to improve handling of predictions and ensure non-null checks for better stability ([#55](https://github.com/IA-Generative/ocr-api/issues/55)) ([2ffdcfc](https://github.com/IA-Generative/ocr-api/commit/2ffdcfc07f2ff12b2cb399066e28a05bbd385de8))
* remove docling from dependencies and add ocr-docling group ([96f7828](https://github.com/IA-Generative/ocr-api/commit/96f782802b6726e2ec6b34733978bdd1006a0262))
* update apps/client/src/api/http-client.ts ([7012539](https://github.com/IA-Generative/ocr-api/commit/70125395a3408a92004ab257e178714f9d53f020))
* update apps/client/src/api/http-client.ts ([2d0704f](https://github.com/IA-Generative/ocr-api/commit/2d0704f6d0f7815c4e0a501990aa9ba80701b5eb))
* update apps/client/src/api/http-client.ts ([453edc0](https://github.com/IA-Generative/ocr-api/commit/453edc0c6203c9bfee29402161a96409e9b2f377))
* update apps/client/src/utils/keycloak.ts ([9bca0e0](https://github.com/IA-Generative/ocr-api/commit/9bca0e03a7c67386a9a1e87c17716943310ab5dc))
* update apps/client/src/utils/keycloak.ts ([cdfb2f9](https://github.com/IA-Generative/ocr-api/commit/cdfb2f9c1b9443ae4aff82e9c45e4397453d1574))
* update apps/client/src/utils/keycloak.ts ([12b3614](https://github.com/IA-Generative/ocr-api/commit/12b3614a3bb2aef2669ca0bebde8d43d8b20092d))
* update apps/client/src/utils/keycloak.ts ([655e2ee](https://github.com/IA-Generative/ocr-api/commit/655e2eeda630b3d6fce788d6c8f06a217c154915))
* update apps/client/src/utils/keycloak.ts ([cb674a4](https://github.com/IA-Generative/ocr-api/commit/cb674a44d5cc705345242179cc5d66b40620004b))
* update apps/client/src/utils/keycloak.ts ([cb0a6c0](https://github.com/IA-Generative/ocr-api/commit/cb0a6c096f9b1736ebf4f9aa10b978e3c1c11a04))
* update apps/client/src/utils/keycloak.ts ([0a5e16b](https://github.com/IA-Generative/ocr-api/commit/0a5e16bd52602d0618e1882cdd2e0619b45dcedd))
* update default task operation to use DEFAULT value in upload_file function ([e5b8162](https://github.com/IA-Generative/ocr-api/commit/e5b8162ea60664dad5e3b774d3d145bff6bec1f3))
* update maxfail option in test commands to allow all tests to run ([00616f0](https://github.com/IA-Generative/ocr-api/commit/00616f004ae19bee5a587ed5fd71c963091f79b4))
* update release workflow to correct manifest and config file paths ([7769665](https://github.com/IA-Generative/ocr-api/commit/77696658f14eaa8952f895ee97fd8dde7d9deb15))

## [0.1.0](https://github.com/IA-Generative/ocr-api/compare/v0.0.1...v0.1.0) (2025-07-30)


### Features

* :chart_with_upwards_trend: add matomo tracking ([f73aacb](https://github.com/IA-Generative/ocr-api/commit/f73aacbf8bc4898b20b8632bb516fd612d968510))
* add PDF forms extraction worker and related tests ([98bcdf1](https://github.com/IA-Generative/ocr-api/commit/98bcdf1daa580b934de3e68db89b591b81259487))
* add workflow for testing services related to forms ([eecc67b](https://github.com/IA-Generative/ocr-api/commit/eecc67ba7103cec7b6b32b3bcad11e11a4d7057b))


### Bug Fixes

* :rocket: don't open twice file ([eb6464c](https://github.com/IA-Generative/ocr-api/commit/eb6464c6f08bc5a4b6725f5fadbbbb14d12d29c4))
* add more log using user_id ([9b310c9](https://github.com/IA-Generative/ocr-api/commit/9b310c9a25ad8fdc73e15ffff17e3a3c82e5adb5))
* async routes ([#7](https://github.com/IA-Generative/ocr-api/issues/7)) ([525dddd](https://github.com/IA-Generative/ocr-api/commit/525dddd4ca418c396ced33c29953f4ac9a87f6e9))
* hot fix lock ([2e93413](https://github.com/IA-Generative/ocr-api/commit/2e93413ed1802fa711a78a549b36d522fe013273))
* Refactor batch_predict method to improve handling of predictions and ensure non-null checks for better stability ([#55](https://github.com/IA-Generative/ocr-api/issues/55)) ([2ffdcfc](https://github.com/IA-Generative/ocr-api/commit/2ffdcfc07f2ff12b2cb399066e28a05bbd385de8))

## [1.7.0](https://github.com/IA-Generative/ocr-api/compare/v1.6.0...v1.7.0) (2025-07-15)


### Features

* ❇️ add queue arch ([#21](https://github.com/IA-Generative/ocr-api/issues/21)) ([0243aaf](https://github.com/IA-Generative/ocr-api/commit/0243aafead55914213fd21d2b86255dfd29db746))
* add checkbox drawing functionality and update tests with new images and JSON data ([f3e9df8](https://github.com/IA-Generative/ocr-api/commit/f3e9df8dcd928d347f342d07aaa7a8b18871f6b5))


### Bug Fixes

* add cache package ([92044ca](https://github.com/IA-Generative/ocr-api/commit/92044cacdb3e6a060e10061cc45bf3549f143af9))
* add checkbox_service directory to Dockerfile ([3fadb80](https://github.com/IA-Generative/ocr-api/commit/3fadb80026abc7dd848056d0bad2ca8ad182913a))
* add llm folder ([aa06510](https://github.com/IA-Generative/ocr-api/commit/aa0651016023609dea2514caab45d87e22c7d7af))
* add logging to BoxDetection class and improve batch_predict method performance ([43edf1c](https://github.com/IA-Generative/ocr-api/commit/43edf1cf17520790c7ff65278073c460b1199fc9))
* async routes ([#7](https://github.com/IA-Generative/ocr-api/issues/7)) ([525dddd](https://github.com/IA-Generative/ocr-api/commit/525dddd4ca418c396ced33c29953f4ac9a87f6e9))
* comment out text_det_limit_type and format batch_predict method signature ([195606d](https://github.com/IA-Generative/ocr-api/commit/195606d812567f749113f490de0d6173a6e90e22))
* comment out unused GPU build configurations for paddleocr ([fbe9447](https://github.com/IA-Generative/ocr-api/commit/fbe9447d174f88bd042fc257f9360527ceffb183))
* download using cpu ([2eb5f5b](https://github.com/IA-Generative/ocr-api/commit/2eb5f5bdbda4f4aacbc8532928124cd45f07e715))
* enhance error logging in TemplateLLMDetector and improve code formatting ([7b93841](https://github.com/IA-Generative/ocr-api/commit/7b93841b10c5abec8957ce6c4d9378409a7c3c01))
* format code for better readability and ensure models are appended correctly ([2ac03f4](https://github.com/IA-Generative/ocr-api/commit/2ac03f43237abefdd2c61da493edb7127629002d))
* improve code readability by formatting and adding debug logs in BaseWorker ([7b22719](https://github.com/IA-Generative/ocr-api/commit/7b227196a3f62ebeded8c1d3366a034aabd02fe9))
* improve readability of batch_predict method in BoxDetection class ([3d9806a](https://github.com/IA-Generative/ocr-api/commit/3d9806ad436e8709c33fbb27052ff0bbf71c9ae5))
* model instances ([9c8e355](https://github.com/IA-Generative/ocr-api/commit/9c8e355f138aa6c73c3293c6c9837965bbaa7670))
* Refactor model initialization to move warmup logging after model creation ([20a55dd](https://github.com/IA-Generative/ocr-api/commit/20a55dd11af9f428fe310c676f9b183a5cf48628))
* refactor PaddleInferOCR initialization to use settings from PaddleSetting ([ea6b3d8](https://github.com/IA-Generative/ocr-api/commit/ea6b3d87a3a9da4ea3e0170a33f71b5c5a7a3241))
* remove migration service from dependencies in multiple services ([8d31689](https://github.com/IA-Generative/ocr-api/commit/8d31689d53a028f4a2b2b90261d8e0191f00bc9a))
* remove redundant uv sync command in Dockerfile ([3471b14](https://github.com/IA-Generative/ocr-api/commit/3471b14513868ba7efd259fb284ef0b8e91f20f4))
* rename PaddleFormulaPredcition to PaddleFormulaRecognizer for consistency ([130c6d9](https://github.com/IA-Generative/ocr-api/commit/130c6d98bebeb2fa5604200137477aa61ee5f99d))
* result ([6fc2872](https://github.com/IA-Generative/ocr-api/commit/6fc287235ccea9b3e8fe986e5344817ceaf4ef16))
* revert OCR_VERSION to PP-OCRv4 and set default OCR_LANG to 'en' ([e1df499](https://github.com/IA-Generative/ocr-api/commit/e1df499b0e4892c56decfa91b8be1aa774f9ce58))
* update Dockerfile to include 'services' group in uv sync command ([681d174](https://github.com/IA-Generative/ocr-api/commit/681d17458aaa86e46cb33e3d6acb8bd32f25bedb))
* update image names for paddleocr services to include version ([4221e84](https://github.com/IA-Generative/ocr-api/commit/4221e84759a486ac227b565706761c7d546d1e13))
* use gpu ([82455e3](https://github.com/IA-Generative/ocr-api/commit/82455e38b13af7d9b0c617328c58ec588e4dc663))
* use uv instead of vu ([4598d93](https://github.com/IA-Generative/ocr-api/commit/4598d93cea4680670124cd3d9816fed4c1fb1f26))

## [1.6.0](https://github.com/IA-Generative/ocr-api/compare/v1.5.0...v1.6.0) (2025-07-08)


### Features

* ❇️ add queue arch ([#21](https://github.com/IA-Generative/ocr-api/issues/21)) ([0243aaf](https://github.com/IA-Generative/ocr-api/commit/0243aafead55914213fd21d2b86255dfd29db746))
* add checkbox drawing functionality and update tests with new images and JSON data ([f3e9df8](https://github.com/IA-Generative/ocr-api/commit/f3e9df8dcd928d347f342d07aaa7a8b18871f6b5))


### Bug Fixes

* add checkbox_service directory to Dockerfile ([3fadb80](https://github.com/IA-Generative/ocr-api/commit/3fadb80026abc7dd848056d0bad2ca8ad182913a))
* add logging to BoxDetection class and improve batch_predict method performance ([43edf1c](https://github.com/IA-Generative/ocr-api/commit/43edf1cf17520790c7ff65278073c460b1199fc9))
* async routes ([#7](https://github.com/IA-Generative/ocr-api/issues/7)) ([525dddd](https://github.com/IA-Generative/ocr-api/commit/525dddd4ca418c396ced33c29953f4ac9a87f6e9))
* comment out text_det_limit_type and format batch_predict method signature ([195606d](https://github.com/IA-Generative/ocr-api/commit/195606d812567f749113f490de0d6173a6e90e22))
* comment out unused GPU build configurations for paddleocr ([fbe9447](https://github.com/IA-Generative/ocr-api/commit/fbe9447d174f88bd042fc257f9360527ceffb183))
* download using cpu ([2eb5f5b](https://github.com/IA-Generative/ocr-api/commit/2eb5f5bdbda4f4aacbc8532928124cd45f07e715))
* enhance error logging in TemplateLLMDetector and improve code formatting ([7b93841](https://github.com/IA-Generative/ocr-api/commit/7b93841b10c5abec8957ce6c4d9378409a7c3c01))
* format code for better readability and ensure models are appended correctly ([2ac03f4](https://github.com/IA-Generative/ocr-api/commit/2ac03f43237abefdd2c61da493edb7127629002d))
* improve code readability by formatting and adding debug logs in BaseWorker ([7b22719](https://github.com/IA-Generative/ocr-api/commit/7b227196a3f62ebeded8c1d3366a034aabd02fe9))
* improve readability of batch_predict method in BoxDetection class ([3d9806a](https://github.com/IA-Generative/ocr-api/commit/3d9806ad436e8709c33fbb27052ff0bbf71c9ae5))
* Refactor model initialization to move warmup logging after model creation ([20a55dd](https://github.com/IA-Generative/ocr-api/commit/20a55dd11af9f428fe310c676f9b183a5cf48628))
* refactor PaddleInferOCR initialization to use settings from PaddleSetting ([ea6b3d8](https://github.com/IA-Generative/ocr-api/commit/ea6b3d87a3a9da4ea3e0170a33f71b5c5a7a3241))
* remove migration service from dependencies in multiple services ([8d31689](https://github.com/IA-Generative/ocr-api/commit/8d31689d53a028f4a2b2b90261d8e0191f00bc9a))
* remove redundant uv sync command in Dockerfile ([3471b14](https://github.com/IA-Generative/ocr-api/commit/3471b14513868ba7efd259fb284ef0b8e91f20f4))
* rename PaddleFormulaPredcition to PaddleFormulaRecognizer for consistency ([130c6d9](https://github.com/IA-Generative/ocr-api/commit/130c6d98bebeb2fa5604200137477aa61ee5f99d))
* revert OCR_VERSION to PP-OCRv4 and set default OCR_LANG to 'en' ([e1df499](https://github.com/IA-Generative/ocr-api/commit/e1df499b0e4892c56decfa91b8be1aa774f9ce58))
* update Dockerfile to include 'services' group in uv sync command ([681d174](https://github.com/IA-Generative/ocr-api/commit/681d17458aaa86e46cb33e3d6acb8bd32f25bedb))
* update image names for paddleocr services to include version ([4221e84](https://github.com/IA-Generative/ocr-api/commit/4221e84759a486ac227b565706761c7d546d1e13))
* use uv instead of vu ([4598d93](https://github.com/IA-Generative/ocr-api/commit/4598d93cea4680670124cd3d9816fed4c1fb1f26))

## [1.5.0](https://github.com/IA-Generative/ocr-api/compare/v1.4.0...v1.5.0) (2025-07-08)


### Features

* ❇️ add queue arch ([#21](https://github.com/IA-Generative/ocr-api/issues/21)) ([0243aaf](https://github.com/IA-Generative/ocr-api/commit/0243aafead55914213fd21d2b86255dfd29db746))
* add checkbox drawing functionality and update tests with new images and JSON data ([f3e9df8](https://github.com/IA-Generative/ocr-api/commit/f3e9df8dcd928d347f342d07aaa7a8b18871f6b5))


### Bug Fixes

* add checkbox_service directory to Dockerfile ([3fadb80](https://github.com/IA-Generative/ocr-api/commit/3fadb80026abc7dd848056d0bad2ca8ad182913a))
* add logging to BoxDetection class and improve batch_predict method performance ([43edf1c](https://github.com/IA-Generative/ocr-api/commit/43edf1cf17520790c7ff65278073c460b1199fc9))
* async routes ([#7](https://github.com/IA-Generative/ocr-api/issues/7)) ([525dddd](https://github.com/IA-Generative/ocr-api/commit/525dddd4ca418c396ced33c29953f4ac9a87f6e9))
* comment out text_det_limit_type and format batch_predict method signature ([195606d](https://github.com/IA-Generative/ocr-api/commit/195606d812567f749113f490de0d6173a6e90e22))
* comment out unused GPU build configurations for paddleocr ([fbe9447](https://github.com/IA-Generative/ocr-api/commit/fbe9447d174f88bd042fc257f9360527ceffb183))
* download using cpu ([2eb5f5b](https://github.com/IA-Generative/ocr-api/commit/2eb5f5bdbda4f4aacbc8532928124cd45f07e715))
* format code for better readability and ensure models are appended correctly ([2ac03f4](https://github.com/IA-Generative/ocr-api/commit/2ac03f43237abefdd2c61da493edb7127629002d))
* improve code readability by formatting and adding debug logs in BaseWorker ([7b22719](https://github.com/IA-Generative/ocr-api/commit/7b227196a3f62ebeded8c1d3366a034aabd02fe9))
* improve readability of batch_predict method in BoxDetection class ([3d9806a](https://github.com/IA-Generative/ocr-api/commit/3d9806ad436e8709c33fbb27052ff0bbf71c9ae5))
* Refactor model initialization to move warmup logging after model creation ([20a55dd](https://github.com/IA-Generative/ocr-api/commit/20a55dd11af9f428fe310c676f9b183a5cf48628))
* refactor PaddleInferOCR initialization to use settings from PaddleSetting ([ea6b3d8](https://github.com/IA-Generative/ocr-api/commit/ea6b3d87a3a9da4ea3e0170a33f71b5c5a7a3241))
* remove migration service from dependencies in multiple services ([8d31689](https://github.com/IA-Generative/ocr-api/commit/8d31689d53a028f4a2b2b90261d8e0191f00bc9a))
* remove redundant uv sync command in Dockerfile ([3471b14](https://github.com/IA-Generative/ocr-api/commit/3471b14513868ba7efd259fb284ef0b8e91f20f4))
* rename PaddleFormulaPredcition to PaddleFormulaRecognizer for consistency ([130c6d9](https://github.com/IA-Generative/ocr-api/commit/130c6d98bebeb2fa5604200137477aa61ee5f99d))
* revert OCR_VERSION to PP-OCRv4 and set default OCR_LANG to 'en' ([e1df499](https://github.com/IA-Generative/ocr-api/commit/e1df499b0e4892c56decfa91b8be1aa774f9ce58))
* update Dockerfile to include 'services' group in uv sync command ([681d174](https://github.com/IA-Generative/ocr-api/commit/681d17458aaa86e46cb33e3d6acb8bd32f25bedb))
* update image names for paddleocr services to include version ([4221e84](https://github.com/IA-Generative/ocr-api/commit/4221e84759a486ac227b565706761c7d546d1e13))
* use uv instead of vu ([4598d93](https://github.com/IA-Generative/ocr-api/commit/4598d93cea4680670124cd3d9816fed4c1fb1f26))

## [1.5.0](https://github.com/IA-Generative/ocr-api/compare/v1.4.0...v1.5.0) (2025-07-07)


### Features

* ❇️ add queue arch ([#21](https://github.com/IA-Generative/ocr-api/issues/21)) ([0243aaf](https://github.com/IA-Generative/ocr-api/commit/0243aafead55914213fd21d2b86255dfd29db746))
* add checkbox drawing functionality and update tests with new images and JSON data ([f3e9df8](https://github.com/IA-Generative/ocr-api/commit/f3e9df8dcd928d347f342d07aaa7a8b18871f6b5))


### Bug Fixes

* add checkbox_service directory to Dockerfile ([3fadb80](https://github.com/IA-Generative/ocr-api/commit/3fadb80026abc7dd848056d0bad2ca8ad182913a))
* add logging to BoxDetection class and improve batch_predict method performance ([43edf1c](https://github.com/IA-Generative/ocr-api/commit/43edf1cf17520790c7ff65278073c460b1199fc9))
* async routes ([#7](https://github.com/IA-Generative/ocr-api/issues/7)) ([525dddd](https://github.com/IA-Generative/ocr-api/commit/525dddd4ca418c396ced33c29953f4ac9a87f6e9))
* comment out text_det_limit_type and format batch_predict method signature ([195606d](https://github.com/IA-Generative/ocr-api/commit/195606d812567f749113f490de0d6173a6e90e22))
* download using cpu ([2eb5f5b](https://github.com/IA-Generative/ocr-api/commit/2eb5f5bdbda4f4aacbc8532928124cd45f07e715))
* improve readability of batch_predict method in BoxDetection class ([3d9806a](https://github.com/IA-Generative/ocr-api/commit/3d9806ad436e8709c33fbb27052ff0bbf71c9ae5))
* Refactor model initialization to move warmup logging after model creation ([20a55dd](https://github.com/IA-Generative/ocr-api/commit/20a55dd11af9f428fe310c676f9b183a5cf48628))
* refactor PaddleInferOCR initialization to use settings from PaddleSetting ([ea6b3d8](https://github.com/IA-Generative/ocr-api/commit/ea6b3d87a3a9da4ea3e0170a33f71b5c5a7a3241))
* rename PaddleFormulaPredcition to PaddleFormulaRecognizer for consistency ([130c6d9](https://github.com/IA-Generative/ocr-api/commit/130c6d98bebeb2fa5604200137477aa61ee5f99d))
* revert OCR_VERSION to PP-OCRv4 and set default OCR_LANG to 'en' ([e1df499](https://github.com/IA-Generative/ocr-api/commit/e1df499b0e4892c56decfa91b8be1aa774f9ce58))
* update image names for paddleocr services to include version ([4221e84](https://github.com/IA-Generative/ocr-api/commit/4221e84759a486ac227b565706761c7d546d1e13))
* use uv instead of vu ([4598d93](https://github.com/IA-Generative/ocr-api/commit/4598d93cea4680670124cd3d9816fed4c1fb1f26))

## [0.1.0](https://github.com/IA-Generative/ocr-api/compare/v0.0.1...v0.1.0) (2025-06-18)


### Features

* ❇️ add queue arch ([#21](https://github.com/IA-Generative/ocr-api/issues/21)) ([0243aaf](https://github.com/IA-Generative/ocr-api/commit/0243aafead55914213fd21d2b86255dfd29db746))
* Add BoxDetection model and update configuration parameters ([#53](https://github.com/IA-Generative/ocr-api/issues/53)) ([ea8b33c](https://github.com/IA-Generative/ocr-api/commit/ea8b33c0ddfdf31a89fedba932fb2c3bba0d1cdf))


### Bug Fixes

* async routes ([#7](https://github.com/IA-Generative/ocr-api/issues/7)) ([525dddd](https://github.com/IA-Generative/ocr-api/commit/525dddd4ca418c396ced33c29953f4ac9a87f6e9))
* Correct Dockerfile path for ocr-service-paddle build ([e3f59e8](https://github.com/IA-Generative/ocr-api/commit/e3f59e812c0d997a2b88b56f914ea4d4571b5b1f))
* Improve checkbox confidence calculation and refactor code for readability ([262e57f](https://github.com/IA-Generative/ocr-api/commit/262e57fc25ef1918ad4f6236b86bb2c114ad68b7))
* Refactor model initialization to move warmup logging after model creation ([20a55dd](https://github.com/IA-Generative/ocr-api/commit/20a55dd11af9f428fe310c676f9b183a5cf48628))
* Remove unused GPU build configuration for ocr-service-paddle ([a1fc6c3](https://github.com/IA-Generative/ocr-api/commit/a1fc6c3b00e754db6f9a297d40f5ab5b03f1a027))
* Update target_size type to tuple and enhance image resizing logic ([9b92d3f](https://github.com/IA-Generative/ocr-api/commit/9b92d3fb20610b4fbdb88506f0814b5d466eadee))

## [1.3.0](https://github.com/IA-Generative/ocr-api/compare/v1.2.1...v1.3.0) (2025-05-21)


### Features

* ❇️ add position in queue ([#42](https://github.com/IA-Generative/ocr-api/issues/42)) ([cce48e9](https://github.com/IA-Generative/ocr-api/commit/cce48e9863003416762c03a4da3bdc3c38f62e23))


## [1.2.1](https://github.com/IA-Generative/ocr-api/compare/v1.2.0...v1.2.1) (2025-05-20)


### Bug Fixes

* donwload text ([#40](https://github.com/IA-Generative/ocr-api/issues/40)) ([55818ae](https://github.com/IA-Generative/ocr-api/commit/55818ae9384c9497e389279619016e141a4f2005))

## [1.2.0](https://github.com/IA-Generative/ocr-api/compare/v1.1.0...v1.2.0) (2025-05-20)


### Features

* add route to download text ([#37](https://github.com/IA-Generative/ocr-api/issues/37)) ([764806b](https://github.com/IA-Generative/ocr-api/commit/764806b05d656eec6e128d194a5ac05f99df40d5))


### Bug Fixes

* donwload text ([#39](https://github.com/IA-Generative/ocr-api/issues/39)) ([d02c155](https://github.com/IA-Generative/ocr-api/commit/d02c155771c7de4c3cfcaffe3cfe65d8466f3b57))

## [1.1.0](https://github.com/IA-Generative/ocr-api/compare/v1.0.0...v1.1.0) (2025-05-19)


### Features

* ❇️ add queue arch ([#21](https://github.com/IA-Generative/ocr-api/issues/21)) ([0243aaf](https://github.com/IA-Generative/ocr-api/commit/0243aafead55914213fd21d2b86255dfd29db746))

## [1.0.0](https://github.com/IA-Generative/ocr-api/compare/v0.0.1...v1.0.0) (2025-05-16)


### ⚠ BREAKING CHANGES

* :tada: add new arch for queueing ocr

### Features

* :rocket: add stress tests ([066d878](https://github.com/IA-Generative/ocr-api/commit/066d878582f997452605036d1527f8f526db9aef))
* :sparkles: add output input form ([#19](https://github.com/IA-Generative/ocr-api/issues/19)) ([66f16ab](https://github.com/IA-Generative/ocr-api/commit/66f16ab77afcdd1f5e18d1a48fd2088fcbff9e9f))
* :tada: add new arch for queueing ocr ([bb8f9c2](https://github.com/IA-Generative/ocr-api/commit/bb8f9c2f64454638751ebb8a53f8f7f29b9245f0))
* add release ([#28](https://github.com/IA-Generative/ocr-api/issues/28)) ([5cf7390](https://github.com/IA-Generative/ocr-api/commit/5cf7390d24d39a96697e916a728da516eacee99f))
* add signe url ([#24](https://github.com/IA-Generative/ocr-api/issues/24)) ([61b2bb0](https://github.com/IA-Generative/ocr-api/commit/61b2bb01d93aa4ade5f8e25d4bd0909fbe6aa0d9))


### Bug Fixes

* :bug: change runner type ([77d7c7f](https://github.com/IA-Generative/ocr-api/commit/77d7c7f7b663eac1b782dc4f35747f2d190452b1))
* raise error ([8ce8ad6](https://github.com/IA-Generative/ocr-api/commit/8ce8ad65b2f306d86b1905fac9e7e7d10e8bfb21))

## 0.2.0 (2025-04-24)

### Feat

- add paddle
- add task_stats
- :zap: add flower monitoring queue
- :beers: concurrency works for celery
- :zap: add celery queue
- add some celery for titi
- reduce main and add abtract to wrker
- add workers
- use surya ocr
- add surya ocr
- add surya ocr

### Fix

- :bug: run worker with good model
- rid off ignore folder ignore
- don't use user_id
- add failure process
- use pg
- add pg in docker compose
- add psycopg
- global variable and unittest
- task_data not found
- don't use ressource
- cean code
- typo
- stress test
- install
- installation poppler-utils
- correct dockerfile
- service
- don't use paddle ocr
- add unittest for utils
- hope that create directory
- dwnload model
- installation ocr-service
- add pillow

## [0.3.0](https://github.com/IA-Generative/ocr-api/compare/v0.2.0...v0.3.0) (2025-04-25)


### Features

* :beers: concurrency works for celery ([7b7466b](https://github.com/IA-Generative/ocr-api/commit/7b7466b38f845cd81a1c8ae666534405482cda63))
* :zap: add celery queue ([6aff3db](https://github.com/IA-Generative/ocr-api/commit/6aff3dbca81c4b8d89a030966e044978b7b649d3))
* :zap: add flower monitoring queue ([398f9a9](https://github.com/IA-Generative/ocr-api/commit/398f9a92b74cb830d1279a60fba71371c38b9d1c))
* add ci-cd ([c9a1e56](https://github.com/IA-Generative/ocr-api/commit/c9a1e5607cd8f74316c7bad374e936e23eec3d52))
* add docekrfiles ([1f21b0f](https://github.com/IA-Generative/ocr-api/commit/1f21b0fd4705f06bd5db2e7614c628066e28fd17))
* add documentation ([6116038](https://github.com/IA-Generative/ocr-api/commit/61160382b88afc57c863c194fa04d524f6c5fe83))
* add github action for release ([ed761f4](https://github.com/IA-Generative/ocr-api/commit/ed761f47e86d6d169d340ff5ce7a77facccc1c80))
* add more extras ([3921c99](https://github.com/IA-Generative/ocr-api/commit/3921c998cfaba1c1682af55dc229ba8c1f3beb07))
* add ocr service ([e2f2ace](https://github.com/IA-Generative/ocr-api/commit/e2f2ace131e48cdb4c85a4282cd23a2fc13e6d45))
* add paddle ([f96a942](https://github.com/IA-Generative/ocr-api/commit/f96a9421ebcf20c23c1e3694e43fd5cb9818b0bc))
* add redis broker ([fb0db99](https://github.com/IA-Generative/ocr-api/commit/fb0db99ba9f9779afed4c71f2e6e70482004436f))
* add some celery for titi ([28a14df](https://github.com/IA-Generative/ocr-api/commit/28a14dfd086986922621b08e299515b90cde99b5))
* add surya ocr ([3a74515](https://github.com/IA-Generative/ocr-api/commit/3a745153cd3b8181b5bd86ca6d602945e5991767))
* add surya ocr ([134ffbc](https://github.com/IA-Generative/ocr-api/commit/134ffbce6cb3e01057ef74bffd5d8ca0e60b9838))
* add task_stats ([ebe50c5](https://github.com/IA-Generative/ocr-api/commit/ebe50c5af825940c3febf18c2893ce87823f718c))
* add workers ([800d3f2](https://github.com/IA-Generative/ocr-api/commit/800d3f2b185d91c1e782156b56198875e9dbce15))
* minio connection ([573bd91](https://github.com/IA-Generative/ocr-api/commit/573bd919f3dad80ba098ee22db4ca7af262756ff))
* move route health ([9a017a5](https://github.com/IA-Generative/ocr-api/commit/9a017a59e71420125296f7b6d1b3a77b6a7170c4))
* reduce main and add abtract to wrker ([91dd9cb](https://github.com/IA-Generative/ocr-api/commit/91dd9cbc0768e5e9ff0eeb81ee78a5e5cf999449))
* route jobs ([340c35c](https://github.com/IA-Generative/ocr-api/commit/340c35cf463dda683a14dca5d5bfbd059278123e))
* use surya ocr ([2512889](https://github.com/IA-Generative/ocr-api/commit/251288995689102d66ecbf8f530c507d2a407907))


### Bug Fixes

* :bug: run worker with good model ([5b87298](https://github.com/IA-Generative/ocr-api/commit/5b872985d8331c2da713b098689e6ff774ef9467))
* :fire: correct models dockerfiles ([5113288](https://github.com/IA-Generative/ocr-api/commit/511328894abf84e5b0eb2450011f6e5a619fe2cb))
* add database url ([fa44788](https://github.com/IA-Generative/ocr-api/commit/fa44788887eaeb83c9ce1bc08556d34e901c1d2d))
* add docerfile ([e57814f](https://github.com/IA-Generative/ocr-api/commit/e57814f7a4b2af3f05f2b2806eb2119aece3c6dd))
* add failure process ([c802064](https://github.com/IA-Generative/ocr-api/commit/c8020644392385e3785d817edea914e86a008770))
* add pg in docker compose ([e30b15a](https://github.com/IA-Generative/ocr-api/commit/e30b15a80667d743707c3691977950d92a3298d6))
* add pillow ([d448ced](https://github.com/IA-Generative/ocr-api/commit/d448ced367919799064c34041c7235f891a1b15d))
* add psycopg ([5256eea](https://github.com/IA-Generative/ocr-api/commit/5256eea205a802acaebeb64851cc0a8b3f6f6148))
* add unittest for utils ([eecee0e](https://github.com/IA-Generative/ocr-api/commit/eecee0e8d6a9887906a5d0e324bf148df17f28d3))
* async routes ([7289ffd](https://github.com/IA-Generative/ocr-api/commit/7289ffd247ebc7b1e50f4f61dcb348a2759848ef))
* async routes ([#7](https://github.com/IA-Generative/ocr-api/issues/7)) ([525dddd](https://github.com/IA-Generative/ocr-api/commit/525dddd4ca418c396ced33c29953f4ac9a87f6e9))
* branch name ([c431d38](https://github.com/IA-Generative/ocr-api/commit/c431d382ddcc2c259733bdf14ef4188889a3fb24))
* cean code ([14935da](https://github.com/IA-Generative/ocr-api/commit/14935da7f82539e4bb6dca402c547d316112b6a5))
* clean code ([c06e8fe](https://github.com/IA-Generative/ocr-api/commit/c06e8fe5ae7fb5fa32aa41d8f31d8e61f4e672f7))
* clean code with ruff ([b41e781](https://github.com/IA-Generative/ocr-api/commit/b41e781c54cec6fbf63afb45456acf1a6da10a40))
* correct dockerfile ([937cde7](https://github.com/IA-Generative/ocr-api/commit/937cde75379d46df75d0a2786f2fd0e10706624d))
* db ([82fe96d](https://github.com/IA-Generative/ocr-api/commit/82fe96dfacff9d671fa87ebfe7b37e8a5a7176dc))
* db creator ([5b5dee7](https://github.com/IA-Generative/ocr-api/commit/5b5dee7bfe26341748cd5d70d6876167b34b5bd2))
* don't use paddle ocr ([65824e5](https://github.com/IA-Generative/ocr-api/commit/65824e5134f651574d44af0e103703823c842773))
* don't use ressource ([6551382](https://github.com/IA-Generative/ocr-api/commit/655138273a8d9a0adf95fcbce0bfa797a56389bd))
* don't use user_id ([97150b5](https://github.com/IA-Generative/ocr-api/commit/97150b5729b5bea9e52c9641ba63f2235444de4b))
* dwnload model ([2d1e76e](https://github.com/IA-Generative/ocr-api/commit/2d1e76ecb79b59c58cd422f4f974a067f2c47417))
* en down ([ddca026](https://github.com/IA-Generative/ocr-api/commit/ddca026ecbaa430d3adcb0901be4ad7d24d98667))
* env file ([d43caff](https://github.com/IA-Generative/ocr-api/commit/d43caff3721172441adbc9163f0a715168bb0225))
* extras allow ([6310008](https://github.com/IA-Generative/ocr-api/commit/63100084fb0fe46e82169632b489c3f3227a92a2))
* fastdeploy dir ([c933c14](https://github.com/IA-Generative/ocr-api/commit/c933c148b1f8eaad7a6b702f3587eee877fb62f4))
* global variable and unittest ([0f9d31f](https://github.com/IA-Generative/ocr-api/commit/0f9d31f585a66ef6a5a92a6744906b7012f16819))
* hope that create directory ([98b3b58](https://github.com/IA-Generative/ocr-api/commit/98b3b5835c64075144f209797d822a39d7ca4789))
* ingore .db ([5b4e934](https://github.com/IA-Generative/ocr-api/commit/5b4e934e08e0757873357664bfe8586ff7b2fed9))
* install ([d598c18](https://github.com/IA-Generative/ocr-api/commit/d598c188a3e1274f14268ef6d9b176c271156241))
* installation ocr-service ([0656729](https://github.com/IA-Generative/ocr-api/commit/06567291f12395680fbe5282272415ad7468c4ed))
* installation poppler-utils ([b170d7c](https://github.com/IA-Generative/ocr-api/commit/b170d7cae0f566e63446360b79c5ee11f2f8db28))
* launch anytime ([394a598](https://github.com/IA-Generative/ocr-api/commit/394a5980e0461bcb0603863e1af95c4011769549))
* let user id ([66ea277](https://github.com/IA-Generative/ocr-api/commit/66ea277cec93361dd9aac70cede46044e8554f08))
* multi worker and thread ([e2d47ae](https://github.com/IA-Generative/ocr-api/commit/e2d47aec7204fe01da055fa3029199340ab2551b))
* non root cache dir ([1d05402](https://github.com/IA-Generative/ocr-api/commit/1d054027a07ead0d04a0b30e847c177b047a7b2a))
* pythonpath ([b268746](https://github.com/IA-Generative/ocr-api/commit/b26874660a22a545185c51863e7754fc203b82ec))
* pythonpath using export ([0eef252](https://github.com/IA-Generative/ocr-api/commit/0eef252c6fe9158f23175c5662d39bb6f1e1fa34))
* redis and minio sender ([ba1d283](https://github.com/IA-Generative/ocr-api/commit/ba1d283fd9c96cf87eef4461b75dc9d32994e6cc))
* remove clean cache ([edaa149](https://github.com/IA-Generative/ocr-api/commit/edaa14929c0efafc3da369d20014e57c04df93e9))
* rid off ignore folder ignore ([4f94b77](https://github.com/IA-Generative/ocr-api/commit/4f94b77e04b776b7c962aace2cbaac7ea04a0e68))
* service ([9bdd164](https://github.com/IA-Generative/ocr-api/commit/9bdd1642ecdaa855a532a4cf7f2246dcb666c35a))
* size to send ([1f5ef6e](https://github.com/IA-Generative/ocr-api/commit/1f5ef6e00d4ced199b11bd61b9271752faf6ac0a))
* stress test ([fd8c204](https://github.com/IA-Generative/ocr-api/commit/fd8c2048a460a1b29ba9c2430d5a74a054d497a8))
* tag for routes ([c5dfc77](https://github.com/IA-Generative/ocr-api/commit/c5dfc773d8f62c92fd103ffd9d177962958533aa))
* task_data not found ([f3f2173](https://github.com/IA-Generative/ocr-api/commit/f3f217374bbeaa190b5a8dcb1ca7a4560e40f616))
* tests ([1f79eec](https://github.com/IA-Generative/ocr-api/commit/1f79eec4d132ad833dc0037de32718523cc0603b))
* typo ([0db6fc3](https://github.com/IA-Generative/ocr-api/commit/0db6fc3d506ff3201ebd8b9771e065044275b0ec))
* up coverage ([5b21740](https://github.com/IA-Generative/ocr-api/commit/5b21740acf0cea2900a9c30c2950b63612a27709))
* up readme ([1105cc1](https://github.com/IA-Generative/ocr-api/commit/1105cc1b2265360da78ea77883a9ee667917af01))
* use define task type and status ([9d998c8](https://github.com/IA-Generative/ocr-api/commit/9d998c8b05cff1795cadd9e289c2c6338a0ea051))
* use dso pipeline ([d1f2617](https://github.com/IA-Generative/ocr-api/commit/d1f2617226bd2b96a7c1ada5f28a1133dac1639c))
* use file instead of memory ([8a6ab55](https://github.com/IA-Generative/ocr-api/commit/8a6ab5547d69b914566c6e575b408a2995fc8d23))
* use global config ([4c17b5f](https://github.com/IA-Generative/ocr-api/commit/4c17b5f22a1928770c3b06f20804e080bf228e9c))
* use minio ([3d1484d](https://github.com/IA-Generative/ocr-api/commit/3d1484d9e0b98895148dd2e537e2e1b839b12d3d))
* use pg ([2126d86](https://github.com/IA-Generative/ocr-api/commit/2126d8609bd5ab7c84e7d40c60e286dfe237734c))
* use real files ([92e76ce](https://github.com/IA-Generative/ocr-api/commit/92e76cee3afa75c3ce266ef098f08f8dfd91131c))
* uv ([a45191d](https://github.com/IA-Generative/ocr-api/commit/a45191dc5e9a84a7bee240dc31cc4cadea2d7698))
* version ([377b32d](https://github.com/IA-Generative/ocr-api/commit/377b32dc4f797f924e4a4f846130e1893e1de29c))
* warning ([d0a29b1](https://github.com/IA-Generative/ocr-api/commit/d0a29b1f160c2dbdd6e56eeb1ea99b9f10a1cc60))


### Documentation

* clean readme ([1d5e92d](https://github.com/IA-Generative/ocr-api/commit/1d5e92ddb6e65d5128edd405f3fc7cb3a59b60b5))

## 0.1.5 (2025-04-13)

### Feat

- add documentation
- add ci-cd

### Fix

- let user id
- add database url
- use define task type and status
- use dso pipeline
- en down
- up coverage
- pythonpath using export
- pythonpath
- launch anytime
- tests
- env file
- extras allow

## 0.1.4 (2025-04-13)

### Fix

- version

## v0.1.1 (2025-04-13)

### Feat

- add docekrfiles
- add ocr service
- add more extras
- add redis broker
- minio connection
- route jobs
- move route health

### Fix

- clean code with ruff
- use real files
- clean code
- ingore .db
- redis and minio sender
- size to send
- use minio
- use global config
- db
- use file instead of memory
- db creator
- tag for routes
- warning
- uv
- fastdeploy dir
- non root cache dir
- remove clean cache
- up readme
- async routes (#7)
- multi worker and thread
- async routes
