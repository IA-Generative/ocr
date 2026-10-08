# OCR API

Cette API fournit un service d’extraction de texte à partir de fichiers PDF ou d’images. Elle repose sur un pipeline de traitement asynchrone utilisant Redis (queue), S3 (stockage), et PaddleOCR pour effectuer la reconnaissance de texte.

## Démo

![DEMO](docs/images/demo-ocr.gif)

## SDKs

Deux SDKs sont disponibles pour faciliter l'intégration de l'API OCR dans vos projets, un par langage, dans `sdk/<langage>/`.

### SDK Python

Supporte les clients synchrones et asynchrones avec des modèles Pydantic pour une validation stricte des données.

📦 **[Voir le SDK](sdk/python/README.md)** - Client Python avec support async/sync

```bash
cd sdk/python
uv pip install -e .
# ou
pip install -e .
```

```python
from ocr_sdk import SyncOCRClient

with SyncOCRClient("http://localhost:5000") as client:
    task = client.create_job("document.pdf")
    result = client.wait_for_task(task.id)
    text = client.get_task_text(task.id)
    print(text)
```

Pour plus de détails, consultez la [documentation du SDK Python](sdk/python/README.md).

### SDK JS/TypeScript

Client Node.js (≥ 18, `fetch` natif) avec des types TypeScript pour toutes les entrées/sorties.

📦 **[Voir le SDK](sdk/js/README.md)** - Client TypeScript pour Node.js

```bash
npm install "git+https://github.com/IA-Generative/ocr.git#path:sdk/js"
```

```ts
import { OCRClient } from 'ocr-sdk'

const client = new OCRClient('http://localhost:5000')
const task = await client.createJob('document.pdf')
const result = await client.waitForTask(task.id)
const text = await client.getTaskText(task.id)
console.log(text)
```

Pour plus de détails, consultez la [documentation du SDK JS](sdk/js/README.md).

## [Fonctionnement](docs/server/asyncronus.md)

Dans cette section vous trouverez le fonctionnement de cette application [docs/server/asyncronus.md](docs/server/asyncronus.md)

## Prérequis

- [Docker](https://docs.docker.com/get-docker/) installé
- [Docker Compose](https://docs.docker.com/compose/) (version 2+ recommandée)
- [make](https://www.gnu.org/software/make/) — point d'entrée unique du dépôt
- [uv](https://docs.astral.sh/uv/) pour le backend Python
- [Node](https://nodejs.org/) 24 (LTS) et [pnpm](https://pnpm.io/) 11 pour le frontend
- Un fichier `.env` configuré à la racine du projet (voir exemple ci-dessous)

`make doctor` indique quels outils sont présents sur la machine.

---

## Images et chart Helm

Les images sont publiées sous `ghcr.io/ia-generative/ocr/{api,worker,frontend,migration}`. Le chart `oci://ghcr.io/ia-generative/ocr/ocr` pointe sur ces images par défaut depuis sa version `0.4.0` (application `0.22.0`).

Les versions `0.2.0-rc` à `0.3.1` du chart utilisent par défaut les anciens noms `ghcr.io/ia-generative/ocr-api/{api,worker,frontend}` (le job de migration utilise `ocr-api/api`). Tous les tags de version ont été copiés sous le nouvel emplacement avec les mêmes digests : si les anciens paquets ne sont plus disponibles, surchargez les dépôts d'images, les tags restent les mêmes.

```yaml
api:
  image:
    repository: ia-generative/ocr/api
worker:
  image:
    repository: ia-generative/ocr/worker
frontend:
  image:
    repository: ia-generative/ocr/frontend
jobs:
  migration:
    image:
      repository: ia-generative/ocr/migration
```

---

## Développement

Toutes les commandes passent par le `Makefile`. `make` (ou `make help`) affiche la
liste complète, groupée par thème.

```bash
# Installation complète : backend (uv), frontend (pnpm), hooks git
make install

# Démarrer la stack conteneurisée
make up

# Vérifier le dépôt : lint + types + tests unitaires
make check
```

Les vérifications sont également disponibles séparément :

| Commande            | Effet                                                  |
| ------------------- | ------------------------------------------------------ |
| `make lint`         | ruff (`apps/server`) + ESLint (`apps/client` et racine) |
| `make format`       | Corrige automatiquement ce qui peut l'être              |
| `make type-check`   | `vue-tsc` sur le frontend                               |
| `make test`         | pytest (backend) + vitest (frontend)                    |
| `make test-e2e`     | Playwright                                              |

Les mêmes hooks tournent avant chaque commit (`pre-commit` pour Python, ESLint
pour le frontend et les fichiers de la racine).

---

## Configuration du fichier `.env`

Crée un fichier `.env` à la racine avec les variables suivantes (à adapter si besoin) :

```env
# Redis configuration
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_QUEUE_NAME=redis-queue

# Database connection string (PostgreSQL)
DATABASE_URL=postgresql://postgres:secret@db:5432/example_db

# Monitoring interval (seconds)
MONITOR_RESSOURCE_EVERY=5

# S3 (RustFS) configuration
AWS_BUCKET_NAME=test
AWS_ACCESS_KEY_ID=rustfsadmin
AWS_SECRET_ACCESS_KEY=rustfsadmin
AWS_ENDPOINT_URL=http://rustfs:9000
AWS_DEFAULT_REGION=us-east-1

# Terminal settings
TERM=xterm-256color
no_proxy=rustfs

# OCR worker settings
PROCESS_NAME="mixed-classic-and-vlm"
WORKER_NAME=worker.tasks.ocr
DEVICE=cpu
```

Liste complète des variables (obligatoires/optionnelles, description, valeur par défaut) : [`docs/variables.md`](docs/variables.md).

---

## Authentification

L'API accepte deux modes d'authentification, sur les mêmes routes :

- **Clé API statique** — `Authorization: Bearer <clé>`, la clé venant de la variable `API_KEYS`.
- **Identité Keycloak réelle** — via le flow BFF du frontend (cookie de session), ou via `POST /api/auth/token` (username/password) pour un script/SDK, avec renouvellement automatique du jeton (`POST /api/auth/refresh`).

Pour configurer un client Keycloak côté console d'administration (redirect URIs, rôles, mapper `groups`...) : [`docs/keycloak-setup.md`](docs/keycloak-setup.md).

---

## Lancer l’application (Backend)

Depuis la racine du projet, lance la commande :

```bash
docker compose up --build -d
```

Cette commande construit les images si nécessaire et démarre tous les containers en arrière-plan.

---

## Accès aux services

- API OCR (FastAPI) : [http://localhost:5000](http://localhost:5000)
  — Documentation Swagger : [http://localhost:5000/api/docs](http://localhost:5000/api/docs)
- Frontend (Vue) : [http://localhost:8081](http://localhost:8081)
- Keycloak (dev, realm auto-provisionné) : [http://localhost:8080](http://localhost:8080)
  — Admin : `admin` / `admin`
- Interface RustFS : [http://localhost:9001](http://localhost:9001)
  — Identifiant : `rustfsadmin`
  — Mot de passe : `rustfsadmin`

---

## Arrêter l’application

Pour stopper et supprimer les containers, exécute :

```bash
docker compose down
```

Pour supprimer aussi les volumes persistants (base de données, RustFS), ajoute l’option `-v` :

```bash
docker compose down -v
```

---

## Tester l’API

📖 **Documentation interactive (Swagger)** : [http://localhost:5000/api/docs](http://localhost:5000/api/docs) — toutes les routes, leurs paramètres et leurs réponses, testables directement depuis le navigateur. Version ReDoc : [http://localhost:5000/api/redocs](http://localhost:5000/api/redocs).

Les routes nécessitent une authentification, soit une clé API statique (`Authorization: Bearer <clé>`, voir `API_KEYS` dans [`docs/variables.md`](docs/variables.md)), soit un utilisateur Keycloak (voir [Authentification](#authentification) ci-dessus).

Envoyer un fichier à traiter :

```bash
curl -X POST "http://localhost:5000/api/jobs/" \
  -H "Authorization: Bearer <ta_clé_api>" \
  -F "file=@/chemin/vers/ton/fichier.pdf"
```

Obtenir l'état de la tâche (l'`id` renvoyé par l'appel précédent) :

```bash
curl -X GET "http://localhost:5000/api/tasks/<task_id>" \
  -H "Authorization: Bearer <ta_clé_api>"
```

Tu peux aussi passer par l'ui dédiée [Frontend](#frontend), ou par l'un des [SDKs](#sdks) ci-dessus.

---

## Support et dépannage

- Assure-toi que Docker et Docker Compose sont correctement installés
- Vérifie que le fichier `.env` est présent et bien configuré

## Frontend

```sh
# Installer les dépendances
make install-frontend

# Serveur de développement Vite sur la machine hôte
make dev-frontend

# ... ou dans un conteneur
make up-frontend

# Régénérer les types depuis l'OpenAPI de l'API
make generate-openapi
```
