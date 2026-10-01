# OCR SDK

SDK Python pour interagir avec l'API OCR. Supporte les clients synchrones et asynchrones avec des modèles Pydantic pour les entrées et sorties.

## Installation

### Depuis le dépôt Git (méthode recommandée pour un projet tiers)

`sdk/` vit dans un sous-dossier de ce monorepo, pas dans son propre dépôt : il faut le
fragment `#subdirectory=` pour que `pip`/`uv` trouve `sdk/pyproject.toml`.

```bash
pip install "git+https://github.com/IA-Generative/ocr.git#subdirectory=sdk"
# ou avec uv
uv add "git+https://github.com/IA-Generative/ocr.git#subdirectory=sdk"
```

### En local (développement du SDK lui-même)

Avec `uv` (recommandé):

```bash
# Depuis le répertoire sdk
uv pip install -e .
```

Ou avec `pip`:

```bash
pip install -e .
```

## Fonctionnalités

- ✅ Client **asynchrone** (`AsyncOCRClient`) avec httpx
- ✅ Client **synchrone** (`SyncOCRClient`) avec httpx
- ✅ Modèles **Pydantic** pour toutes les entrées/sorties
- ✅ Gestion des erreurs avec exceptions personnalisées
- ✅ Support de l'authentification par token
- ✅ Context managers pour une gestion automatique des connexions
- ✅ Méthodes utilitaires (wait_for_task, process_document)

## Utilisation

### Client Synchrone

```python
from ocr_sdk import SyncOCRClient, TaskOperation

# Utiliser le context manager pour gérer automatiquement la connexion
with SyncOCRClient("http://localhost:5000") as client:
    # Vérifier l'état de santé de l'API
    health = client.get_health()
    print(f"API Status: {health.status}")

    # Créer un job OCR
    task = client.create_job(
        "path/to/document.pdf",
        task_operation=TaskOperation.DEFAULT
    )
    print(f"Task created: {task.id}")

    # Attendre la fin du traitement
    completed_task = client.wait_for_task(task.id)

    # Récupérer le texte extrait
    if completed_task.status == "completed":
        text = client.get_task_text(task.id)
        print(f"Extracted text: {text}")
```

### Client Asynchrone

```python
import asyncio
from ocr_sdk import AsyncOCRClient, TaskOperation

async def main():
    # Utiliser le context manager async
    async with AsyncOCRClient("http://localhost:5000") as client:
        # Vérifier l'état de santé
        health = await client.get_health()
        print(f"API Status: {health.status}")

        # Créer un job OCR
        task = await client.create_job(
            "path/to/document.pdf",
            task_operation=TaskOperation.DEFAULT
        )
        print(f"Task created: {task.id}")

        # Attendre la fin du traitement
        completed_task = await client.wait_for_task(task.id)

        # Récupérer le texte extrait
        if completed_task.status == "completed":
            text = await client.get_task_text(task.id)
            print(f"Extracted text: {text}")

# Exécuter la fonction async
asyncio.run(main())
```

### Traitement Direct avec process_document

Pour une utilisation simplifiée, utilisez la méthode `process_document` qui upload et attend le résultat automatiquement:

```python
from ocr_sdk import SyncOCRClient

with SyncOCRClient("http://localhost:5000") as client:
    # Traite le document et attend les résultats
    results = client.process_document("path/to/document.pdf")

    for result in results:
        print(f"Page content: {result.page_content}")
        print(f"Metadata: {result.metadata}")
```

### Avec Authentification

```python
from ocr_sdk import SyncOCRClient

# Fournir un token API
with SyncOCRClient(
    "http://localhost:5000",
    api_key="your-api-token"
) as client:
    health = client.get_health()
    print(health)
```

### Récupérer les Tâches de l'Utilisateur

```python
from ocr_sdk import SyncOCRClient

with SyncOCRClient("http://localhost:5000") as client:
    # Récupérer les tâches (pagination) - retourne un objet paginé, pas une liste brute
    tasks = client.get_user_tasks(page=1, page_size=10)

    print(f"{tasks.total} tâche(s) au total")
    for task in tasks.items:
        print(f"Task {task.id}: {task.status}")
```

### Authentification par identifiants Keycloak (username/password)

Pour une clé API statique, passez `api_key=...` au constructeur. Pour s'authentifier
comme un vrai utilisateur Keycloak (les requêtes portent alors ses rôles/groupes réels),
appelez `login()` une fois dans le context manager :

```python
from ocr_sdk import SyncOCRClient

with SyncOCRClient("http://localhost:5000") as client:
    client.login("user@example.com", "hunter2")
    task = client.create_job("document.pdf")
```

`login()` appelle `POST /api/auth/token` sur cette API : c'est le backend qui échange
les identifiants avec Keycloak (Resource Owner Password Credentials grant), le secret
du client Keycloak ne quitte jamais le backend. Le jeton d'accès renvoyé expire (5
minutes par défaut côté Keycloak), mais un `refresh_token` est aussi renvoyé et stocké
automatiquement — dès qu'une requête reçoit un 401, le client rafraîchit tout seul
avant de rejouer la requête, sans rien à faire de votre côté :

```python
with SyncOCRClient("http://localhost:5000") as client:
    client.login("user@example.com", "hunter2")
    # ... même après 10 minutes d'inactivité, l'appel suivant se rafraîchit tout seul
    task = client.create_job("document.pdf")
```

Pour rafraîchir explicitement (par exemple avant une longue attente), appelez
`client.refresh()`. Si le refresh token lui-même a expiré (au-delà de sa propre durée
de vie côté Keycloak), `refresh()` lève `OCRAuthenticationError` — il faut alors
rappeler `login()`.

## Modèles

Le SDK expose tous les modèles Pydantic nécessaires:

```python
from ocr_sdk import (
    TaskModel,      # Modèle de tâche
    TaskStatus,     # Enum des statuts de tâche
    TaskOperation,  # Enum des types d'opération
    Health,         # Modèle de santé API
    OCRResult,      # Résultat OCR
    Page,           # Page de document
    Bbox,           # Boîte englobante
)
```

### Statuts de Tâche

```python
from ocr_sdk import TaskStatus

# Statuts disponibles
TaskStatus.CREATED       # Tâche créée
TaskStatus.QUEUED        # En file d'attente
TaskStatus.STARTED       # Démarrée
TaskStatus.IN_PROGRESS   # En cours
TaskStatus.COMPLETED     # Terminée
TaskStatus.FAILED        # Échouée
TaskStatus.RETRYING      # Nouvelle tentative
TaskStatus.CANCELED      # Annulée
TaskStatus.TIMEOUT       # Timeout
```

### Types d'Opération

```python
from ocr_sdk import TaskOperation

# Opérations disponibles
TaskOperation.DEFAULT         # Opération par défaut
TaskOperation.OCR            # OCR standard
TaskOperation.SAVE_TEMPLATE  # Sauvegarder comme template
TaskOperation.FORMS          # Extraction de formulaires
TaskOperation.VECTORIZE      # Vectorisation
TaskOperation.DOCLING        # Traitement Docling
```

## Gestion des Erreurs

```python
from ocr_sdk import SyncOCRClient
from ocr_sdk.exceptions import (
    OCRAPIError,
    OCRTimeoutError,
    OCRAuthenticationError,
)

try:
    with SyncOCRClient("http://localhost:5000") as client:
        task = client.create_job("document.pdf")
        result = client.wait_for_task(task.id, max_wait_time=60)

except OCRTimeoutError as e:
    print(f"Timeout: {e}")
except OCRAPIError as e:
    print(f"API Error {e.status_code}: {e.message}")
except OCRAuthenticationError as e:
    print(f"Authentication failed: {e}")
```

## Développement

### Installation en mode développement

```bash
cd sdk
uv pip install -e ".[dev]"
```

### Tests

```bash
pytest
```

## Structure du Package

```
sdk/
├── ocr_sdk/
│   ├── __init__.py           # Exports publics
│   ├── client_async.py       # Client asynchrone
│   ├── client_sync.py        # Client synchrone
│   ├── models.py             # Modèles Pydantic
│   └── exceptions.py         # Exceptions personnalisées
├── examples/
│   ├── sync_example.py       # Exemple synchrone
│   └── async_example.py      # Exemple asynchrone
├── pyproject.toml            # Configuration du package
└── README.md                 # Documentation
```

## Compatibilité

- Python >= 3.10
- httpx >= 0.28.1
- pydantic >= 2.11.5

## Licence

Voir le fichier LICENSE du projet parent.
