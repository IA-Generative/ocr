## Environment Variables

Ce projet utilise plusieurs variables d'environnement pour configurer les modèles OCR, Celery, les connecteurs de stockage (RustFS / S3), Redis, la base de données, ainsi que le monitoring des ressources.

Les variables sont chargées automatiquement grâce à [`pydantic-settings`](https://docs.pydantic.dev/latest/concepts/pydantic_settings/), sauf mention contraire (certaines sont lues directement via `os.environ`).

Légende : ✅ = obligatoire (le service plante/refuse de démarrer si absente) — ❌ = optionnelle (valeur par défaut fournie par le code).

---

### Variables liées à PaddleOCR

| Variable | Obligatoire | Description | Default | Utilisation |
|:---|:---:|:---|:---|:---|
| `PADDLE_OCR_BASE_DIR` | ❌ | Chemin de base où sont stockés les modèles OCR. | `models/` | `PaddleSetting` |
| `PADDLE_PDX_CACHE_HOME` | ❌ | Cache PaddleX (téléchargement/chargement des modèles). | `models/paddle_pdx_cache/` | `PaddleSetting` |
| `DETECTION_FOLDER` | ❌ | Sous-dossier du modèle de détection. | `detection` | `PaddleSetting` |
| `RECOGNITION_FOLDER` | ❌ | Sous-dossier du modèle de reconnaissance. | `recognition` | `PaddleSetting` |
| `CLASSIFICATION_FOLDER` | ❌ | Sous-dossier du modèle de classification. | `classification` | `PaddleSetting` |
| `DETECTION_BATCH_SIZE` | ❌ | Batch size pour la détection. | `2` | `PaddleSetting` |
| `RECOGNITION_BATCH_SIZE` | ❌ | Batch size pour la reconnaissance. | `8` | `PaddleSetting` |
| `CPU_THREADS` | ❌ | Nombre de threads CPU pour l'inférence PaddleOCR. | `2` | `PaddleSetting` |
| `ENABLE_MKLDNN` | ❌ | Active l'accélération MKL-DNN. | `False` | `PaddleSetting` |
| `OCR_VERSION` | ❌ | Version du modèle PaddleOCR. | `PP-OCRv3` | `PaddleSetting` |
| `DEVICE` | ❌ | Device d'inférence (`cpu`/`gpu`). | `cpu` | `PaddleSetting` |
| `OCR_LANG` | ❌ | Langue forcée pour l'OCR. | `None` | `PaddleSetting` |

---

### Variable liée au choix du modèle OCR

| Variable | Obligatoire | Description | Default | Utilisation |
|:---|:---:|:---|:---|:---|
| `MODEL_NAME` | ❌ | Choix du modèle OCR (`paddle` ou `surya`). | `paddle` | `OCRModelSettings` |
| `USE_VISION_LLM_EXTRACT_KIE` | ❌ | Active l'extraction KIE via un LLM de vision. | `False` | `OCRModelSettings` |

---

### Variables pour la configuration Celery

| Variable | Obligatoire | Description | Default | Utilisation |
|:---|:---:|:---|:---|:---|
| `CELERY_APP_NAME` | ❌ | Nom de l'application Celery. | `default` | `CelerySettings` |
| `WORKER_NAME` | ✅ | Nom du worker (identifie le pod/process dans les logs). | - | lu via `os.environ` dans `services/main.py` |
| `PROCESS_NAME` | ✅ | Nom du pipeline OCR à charger dans ce worker. | - | lu via `os.environ` dans `services/main.py` |

---

### Variables pour la purge périodique des tâches (Celery Beat)

Purge automatique des tâches terminales (`completed`, `failed`, `canceled`, `timeout`) et de leurs fichiers S3/RustFS associés, une fois qu'elles dépassent la rétention configurée. Planifiée via Celery Beat (service `beat` de `docker-compose.yaml`, tâche `ocr_backend.purge_old_tasks` dans `ocr_backend/purge.py`). Le process beat consomme une file Celery dédiée (`purge`) : sur la file par défaut, partagée avec les workers OCR, chacun jetterait les messages de l'autre comme tâches inconnues.

| Variable | Obligatoire | Description | Default | Utilisation |
|:---|:---:|:---|:---|:---|
| `PURGE_ENABLED` | ❌ | Active/désactive l'enregistrement de la tâche planifiée. | `true` | `PurgeSettings` (`src/config/purge.py`) |
| `TASK_RETENTION_DAYS` | ❌ | Âge (en jours, basé sur `created_at`) à partir duquel une tâche terminale est purgée. | `365` | `PurgeSettings` |
| `PURGE_BATCH_SIZE` | ❌ | Taille des lots de suppression en base (évite une transaction unique sur un gros volume). | `100` | `PurgeSettings` |
| `PURGE_CRON_MINUTE` | ❌ | Champ `minute` du [crontab Celery](https://docs.celeryq.dev/en/4.0/userguide/periodic-tasks.html#crontab-schedules). | `0` | `PurgeSettings` |
| `PURGE_CRON_HOUR` | ❌ | Champ `hour` du crontab Celery. | `2` | `PurgeSettings` |
| `PURGE_CRON_DAY_OF_WEEK` | ❌ | Champ `day_of_week` du crontab Celery. | `*` | `PurgeSettings` |
| `PURGE_CRON_DAY_OF_MONTH` | ❌ | Champ `day_of_month` du crontab Celery. | `*` | `PurgeSettings` |
| `PURGE_CRON_MONTH_OF_YEAR` | ❌ | Champ `month_of_year` du crontab Celery. | `*` | `PurgeSettings` |

---

### Variables pour la configuration du connecteur de stockage (S3 / RustFS)

> ⚠️ **Corrigé** : la documentation précédente mentionnait `S3_AVAILABLE`/`MINIO_AVAILABLE` et des classes `ConnectorSettings`/`MinioSettings` — **elles n'existent plus dans le code** (vérifié par recherche exhaustive, aucune occurrence). Il n'y a qu'un seul connecteur de stockage (`S3Connector`, `src/connector/s3_connector.py`), utilisé aussi bien pour un vrai bucket AWS S3 que pour une instance RustFS locale (en pointant `AWS_ENDPOINT_URL` vers RustFS, service S3-compatible qui a remplacé MinIO) — pas de bascule applicative entre les deux.

Seuls deux réglages sont propres à l'application (`S3Settings`, `src/config/s3.py`) :

| Variable | Obligatoire | Description | Default | Utilisation |
|:---|:---:|:---|:---|:---|
| `AWS_BUCKET_NAME` | ❌ | Nom du bucket S3/RustFS utilisé. | `test` | `S3Settings` |
| `VERIFY_SSL` | ❌ | Vérifie le certificat SSL du endpoint S3. | `False` | `S3Settings` |

Le reste des identifiants/endpoint est **lu nativement par boto3/botocore** (jamais par une classe `pydantic-settings` de ce repo) — ce sont les variables standard du SDK AWS :

| Variable | Obligatoire | Description | Default | Utilisation |
|:---|:---:|:---|:---|:---|
| `AWS_ACCESS_KEY_ID` | ❌ (✅ si pas de rôle IAM) | Clé d'accès. | - | résolu nativement par `boto3` |
| `AWS_SECRET_ACCESS_KEY` | ❌ (✅ si pas de rôle IAM) | Clé secrète. | - | résolu nativement par `boto3` |
| `AWS_ENDPOINT_URL` | ❌ | Endpoint custom (utilisé en dev pour pointer vers RustFS au lieu d'AWS). | - (AWS par défaut) | résolu nativement par `boto3` |
| `AWS_DEFAULT_REGION` | ❌ | Région AWS. | - | résolu nativement par `boto3` |

> 💡 **Renommé** : `S3_BUCKET_NAME` s'appelait auparavant différemment du préfixe `AWS_` des quatre autres variables de stockage (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_ENDPOINT_URL`, `AWS_DEFAULT_REGION`). Renommé en `AWS_BUCKET_NAME` dans le code pour cohérence (`S3Settings.AWS_BUCKET_NAME`, `src/config/s3.py`). ⚠️ **C'est un breaking change** : il faut mettre à jour Vault (et tout `.env`) avec `AWS_BUCKET_NAME` avant/au moment du déploiement de cette version, sans quoi le connecteur retombera sur la valeur par défaut `test`.

---

### Variables pour la configuration Redis

Redis est utilisé comme broker Celery (`RedisSettings`, `src/config/redis.py` + `src/connector/broker_connector.py`) et pour le health-check applicatif.

| Variable | Obligatoire | Description | Default | Utilisation |
|:---|:---:|:---|:---|:---|
| `REDIS_HOST` | ❌ | Adresse du serveur Redis (ignorée si le mode Sentinel est activé). | `localhost` | `RedisSettings` |
| `REDIS_PORT` | ❌ | Port Redis (ignoré si le mode Sentinel est activé). | `6379` | `RedisSettings` |
| `REDIS_DB` | ❌ | Index de la base logique Redis. | `0` | `RedisSettings` |
| `REDIS_PASSWORD` | ❌ | Mot de passe Redis (recommandé en prod). | `None` | `RedisSettings` |
| `REDIS_USE_TLS` | ❌ | Active TLS (`rediss://`) pour la connexion Redis. | `False` | `RedisSettings` |
| `REDIS_SENTINEL_ENABLED` | ❌ | Active la résolution du master via Redis Sentinel. | `False` | `RedisSettings` |
| `REDIS_SENTINEL_HOSTS` | ❌ (✅ si Sentinel activé) | Liste `host:port` séparée par des virgules des sentinels. | `None` | `RedisSettings` |
| `REDIS_SENTINEL_MASTER_NAME` | ❌ | Nom du master surveillé par les sentinels. | `mymaster` | `RedisSettings` |
| `REDIS_SENTINEL_PASSWORD` | ❌ | Mot de passe pour l'authentification auprès des sentinels (retombe sur `REDIS_PASSWORD` si absent pour le broker). | `None` | `RedisSettings` |

> ℹ️ `REDIS_QUEUE_NAME` a été retiré de cette documentation : la variable n'est référencée nulle part dans le code (documentation obsolète).
>
> Si Redis est géré par un chart (ex: Bitnami) avec réplication + Sentinel, préférez laisser le chart exposer un unique service Sentinel et ne renseignez que `REDIS_SENTINEL_ENABLED`/`REDIS_SENTINEL_HOSTS`/`REDIS_SENTINEL_MASTER_NAME` — le master courant sera résolu dynamiquement à chaque connexion.

---

### Variables pour la configuration du tracing Langfuse

| Variable | Obligatoire | Description | Default | Utilisation |
|:---|:---:|:---|:---|:---|
| `TRACING_SERVICE` | ❌ | Service de tracing à utiliser (`langfuse` ou `logging`). | `logging` | lu via `os.environ` |
| `LANGFUSE_PUBLIC_KEY` | ❌ | Clé publique Langfuse pour l'authentification. | - | `LangFuseTracingService` |
| `LANGFUSE_SECRET_KEY` | ❌ | Clé secrète Langfuse pour l'authentification. | - | `LangFuseTracingService` |
| `LANGFUSE_HOST` | ❌ | URL du serveur Langfuse (ex: https://cloud.langfuse.com). | - | `LangFuseTracingService` |
| `LANGFUSE_DEBUG` | ❌ | Active le mode debug Langfuse (`true` ou `false`). | `false` | `LangFuseTracingService` |
| `LANGFUSE_TRACING_ENVIRONMENT` | ❌ | Environnement de tracing (ex: `dev`, `preprod`, `prod`). | `dev` | `LangFuseTracingService` |

---

### Variables pour l'authentification Keycloak (BFF)

Le frontend ne parle plus jamais directement à Keycloak : c'est le backend qui possède tout le
flow OAuth2 Authorization Code + PKCE, via `/api/auth/{login,callback,logout,me}`
(`ocr_backend/routers/auth.py`). Le navigateur ne reçoit qu'un cookie de session opaque
(`httpOnly`) ; les jetons Keycloak eux-mêmes restent côté backend, dans Redis
(`ocr_backend/core/security/session.py`).

> 📘 Pour la configuration côté console d'administration Keycloak (créer le client, les
> redirect URIs, les rôles, le mapper `groups`...), voir
> [`docs/keycloak-setup.md`](./keycloak-setup.md).

| Variable | Obligatoire | Description | Default | Utilisation |
|:---|:---:|:---|:---|:---|
| `KEYCLOAK_URL` | ❌ | URL de Keycloak jointe **par le backend** (échange de code, refresh, introspection, logout). | `http://localhost:8080` | `ocr_backend/core/security/keycloak_client.py` |
| `KEYCLOAK_PUBLIC_URL` | ❌ | URL de Keycloak vue **par le navigateur** lors de la redirection `/api/auth/login`. Retombe sur `KEYCLOAK_URL` si absente — à renseigner uniquement si le backend et le navigateur ne résolvent pas Keycloak de la même façon (ex : docker compose local, où c'est un nom de service interne côté backend mais un port exposé sur l'hôte côté navigateur). | `KEYCLOAK_URL` | `ocr_backend/routers/auth.py` |
| `KEYCLOAK_REALM` | ❌ | Realm Keycloak utilisé. | `master` | `ocr_backend/core/security/keycloak_client.py` |
| `KEYCLOAK_CLIENT_ID` | ❌ | Client OpenID Connect **confidentiel** utilisé par le backend (le client ne doit pas être public : seul le backend échange le code d'autorisation). | `your-client-id` | `ocr_backend/core/security/keycloak_client.py` |
| `KEYCLOAK_CLIENT_SECRET` | ✅ (hors dev local) | Secret du client confidentiel. | - | `ocr_backend/core/security/keycloak_client.py` |
| `BACKEND_PUBLIC_URL` | ✅ (hors défaut local) | URL publique de cette API, utilisée pour construire le `redirect_uri` fixe envoyé à Keycloak (`{BACKEND_PUBLIC_URL}/api/auth/callback`) — doit correspondre exactement à une redirect URI enregistrée sur le client Keycloak. | `http://localhost:5000` | `src/config/keycloak.py` |
| `FRONTEND_URL` | ✅ (hors défaut local) | URL publique du frontend : origine CORS autorisée (`allow_credentials: true` + `allow_origins: ["*"]` est rejeté par les navigateurs, l'origine doit être explicite) et cible de redirection après `/callback`. | `http://localhost:8081` | `ocr_backend/main.py`, `ocr_backend/routers/auth.py` |
| `SESSION_COOKIE_NAME` | ❌ | Nom du cookie de session BFF. | `ocr_session` | `ocr_backend/routers/auth.py` |
| `SESSION_COOKIE_SECURE` | ❌ | Marque le cookie `Secure` (HTTPS uniquement). À désactiver **uniquement** en dev local HTTP (voir `docker-compose.yaml`) — jamais en production. | `True` | `ocr_backend/routers/auth.py` |
| `SESSION_COOKIE_SAMESITE` | ❌ | Attribut `SameSite` du cookie de session. | `lax` | `ocr_backend/routers/auth.py` |
| `SESSION_TTL_SECONDS` | ❌ | Durée de vie max. de la session côté Redis ; l'expiration réelle reste bornée par celle du refresh token Keycloak. | `604800` (7 jours) | `ocr_backend/core/security/session.py` |

---

### Variables diverses

| Variable | Obligatoire | Description | Default | Utilisation |
|:---|:---:|:---|:---|:---|
| `MONITOR_RESSOURCE_EVERY` | ❌ | Fréquence (en secondes) pour monitorer la consommation de ressources d'une tâche. | `5` (exemple) | `resource_monitor` dans les tâches |
| `DATABASE_URL` | ✅ | URL de connexion à la base de données PostgreSQL. Obligatoire pour le job de migration (`migration/env.py`, plante sans fallback) ; l'application applicative retombe silencieusement sur SQLite local si absente (log `WARNING`) — **ne pas compter sur ce fallback en prod, uniquement pour du dev/test local**. | - (fallback SQLite local en dehors de la migration) | `migration/env.py`, `src/connector/db_connector.py` |
| `ENVIRONMENT` | ❌ | Environnement d'exécution (`development`, `production`, ...). | - | `services/main.py`, `src/logger.py`, `ocr_backend/main.py` |
| `SERVICE_NAME` | ❌ | Nom du service pour les logs structurés. | - | `src/logger.py` |
| `API_KEYS` | ❌ | Clés API acceptées par l'API backend. | - | `ocr_backend/core/security/factory.py` |
| `VERIFY_TOKEN_MODEL` | ❌ | Sélectionne le vérificateur d'auth des routes API (`keycloak` = cookie de session BFF ci-dessus, ou `full-access`/`dev`). | `keycloak` | `ocr_backend/core/security/factory.py` |
| `MODEL_FEATURE_NAME` | ❌ | Nom du modèle de features utilisé par les collections. | - | `ocr_backend/routers/collections.py` |

> ℹ️ **Vues dans Vault, vérifiées contre le code** :
> - `API_KEYS` ✅ utilisée — clés API acceptées par **cette** API (`ocr_backend/core/security/factory.py:47`, défaut `default-api-key` si absente).
> - `VERIFY_TOKEN_MODEL` ✅ utilisée — sélectionne le vérificateur d'auth (`keycloak` par défaut, ou `full-access`) (`ocr_backend/core/security/factory.py:112`).
> - `SERVER_BASE_URL` ❌ **aucune occurrence dans ce repo** (code, tests, SDK). Vraisemblablement une variable côté *consommateur* de cette API (un autre service qui appelle l'OCR API et a besoin de savoir où elle vit), pas une variable lue par ce backend.
> - `SERVER_API_KEY` ❌ **idem, aucune occurrence** — probablement le pendant côté client de `API_KEYS` (la clé que le consommateur envoie), pas une variable lue par ce backend.
> - `EMBEDDINGS_MODEL` ❌ **totalement absente du code** (recherche sur tout le repo : `apps/server`, `apps/client`, `sdk` — zéro résultat, y compris variantes `EMBEDDING_MODEL`). Aucune fonctionnalité d'embeddings n'existe dans ce repo actuellement. Soit c'est une variable morte à nettoyer côté Vault, soit elle appartient à un autre service (pas dans ce repo) — vaut le coup de vérifier avant de la renommer en `OPENAI_EMBEDDINGS_MODEL`, puisqu'il n'y a rien à raccorder ici pour l'instant.

---

## Volumes

| Volume | Type | Point de montage | Usage |
|:---|:---|:---|:---|
| `postgres_data` | volume nommé (PVC en cluster) | `/var/lib/postgresql/data` | Données PostgreSQL — **doit être persistant**. |
| `rustfs_data` | volume nommé (PVC en cluster) | `/data` | Stockage objet RustFS (dev-only, remplacé par du vrai S3 en prod). |

> ⚠️ **Pas de volume dédié pour le cache de modèles PaddleOCR** (`PADDLE_OCR_BASE_DIR` / `PADDLE_PDX_CACHE_HOME`) : les modèles sont téléchargés et intégrés à l'image Docker au build (`business/paddleocr2/Dockerfile`), pas montés en volume à l'exécution. Chaque rebuild d'image retélécharge les modèles, et il n'y a pas de cache partagé entre replicas/pods. À considérer côté infra si la taille d'image ou le temps de démarrage posent problème.
>
> Les autres montages (`docker-compose.yaml`) sont des bind-mounts de code source pour le hot-reload en dev — non pertinents pour un déploiement en cluster.

---

## Exemple de fichier `.env`

```dotenv
# PaddleOCR
PADDLE_OCR_BASE_DIR=models/
DETECTION_FOLDER=detection
RECOGNITION_FOLDER=recognition
CLASSIFICATION_FOLDER=classification
DETECTION_BATCH_SIZE=2
RECOGNITION_BATCH_SIZE=8

# OCR Model
MODEL_NAME=paddle

# Celery (WORKER_NAME/PROCESS_NAME sont injectés par worker dans docker-compose.yaml)
CELERY_APP_NAME=my-celery-app

# Purge périodique (Celery Beat, service `beat`)
PURGE_ENABLED=true
TASK_RETENTION_DAYS=365
PURGE_BATCH_SIZE=100
PURGE_CRON_MINUTE=0
PURGE_CRON_HOUR=2
PURGE_CRON_DAY_OF_WEEK=*
PURGE_CRON_DAY_OF_MONTH=*
PURGE_CRON_MONTH_OF_YEAR=*

# Connecteurs de stockage (S3 / RustFS, lu nativement par boto3)
AWS_BUCKET_NAME=test
AWS_ACCESS_KEY_ID=rustfsadmin
AWS_SECRET_ACCESS_KEY=rustfsadmin
AWS_ENDPOINT_URL=http://localhost:9000
AWS_DEFAULT_REGION=us-east-1

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
REDIS_USE_TLS=False
# Sentinel (optionnel, prioritaire sur REDIS_HOST/REDIS_PORT si activé)
REDIS_SENTINEL_ENABLED=False
REDIS_SENTINEL_HOSTS=sentinel-0:26379,sentinel-1:26379,sentinel-2:26379
REDIS_SENTINEL_MASTER_NAME=mymaster
REDIS_SENTINEL_PASSWORD=

# Tracing Langfuse
TRACING_SERVICE=langfuse
LANGFUSE_PUBLIC_KEY=pk-lf-xxxxxxxxxxxxxxxxxxxxxxx
LANGFUSE_SECRET_KEY=sk-lf-xxxxxxxxxxxxxxxxxxxx
LANGFUSE_HOST=https://cloud.langfuse.com
LANGFUSE_DEBUG=true
LANGFUSE_TRACING_ENVIRONMENT=preprod

# Monitoring
MONITOR_RESSOURCE_EVERY=5

# Database (obligatoire)
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Keycloak (BFF - voir "Variables pour l'authentification Keycloak" ci-dessus)
KEYCLOAK_URL=http://localhost:8080
KEYCLOAK_REALM=mon-realm
KEYCLOAK_CLIENT_ID=mon-client
KEYCLOAK_CLIENT_SECRET=mon-secret
BACKEND_PUBLIC_URL=http://localhost:5000
FRONTEND_URL=http://localhost:8081
```
