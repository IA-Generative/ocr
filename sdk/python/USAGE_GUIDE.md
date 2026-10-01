# Guide d'utilisation du SDK OCR

Ce document fournit des exemples d'utilisation pratiques du SDK OCR dans différents scénarios.

## Table des matières

1. [Installation](#installation)
2. [Utilisation de base](#utilisation-de-base)
3. [Cas d'usage avancés](#cas-dusage-avancés)
4. [Gestion des erreurs](#gestion-des-erreurs)
5. [Intégration dans un projet](#intégration-dans-un-projet)

## Installation

### Dans un nouveau projet avec uv

```bash
# Créer un nouveau projet
mkdir mon-projet-ocr
cd mon-projet-ocr

# Initialiser avec uv
uv init

# Ajouter le SDK comme dépendance locale
uv pip install -e /path/to/ocr/sdk
```

### Dans un projet existant avec pip

```bash
# Depuis votre projet
pip install -e /path/to/ocr/sdk
```

## Utilisation de base

### 1. Vérifier la santé de l'API

```python
from ocr_sdk import SyncOCRClient

with SyncOCRClient("http://localhost:5000") as client:
    health = client.get_health()
    print(f"API Status: {health.status}")
    print(f"Version: {health.version}")
```

### 2. Traiter un document simple

```python
from ocr_sdk import SyncOCRClient

with SyncOCRClient("http://localhost:5000") as client:
    # Upload et créer la tâche
    task = client.create_job("facture.pdf")
    print(f"Tâche créée: {task.id}")

    # Attendre la fin du traitement
    result = client.wait_for_task(task.id)

    # Récupérer le texte
    text = client.get_task_text(task.id)
    print(text)
```

### 3. Traitement avec un seul appel

```python
from ocr_sdk import SyncOCRClient

with SyncOCRClient("http://localhost:5000") as client:
    # Tout en un seul appel
    results = client.process_document("document.pdf")

    for result in results:
        print(f"Contenu: {result.page_content}")
        print(f"Metadata: {result.metadata}")
```

## Cas d'usage avancés

### 1. Traitement de plusieurs fichiers en parallèle (Async)

```python
import asyncio
from pathlib import Path
from ocr_sdk import AsyncOCRClient

async def process_multiple_files(files):
    async with AsyncOCRClient("http://localhost:5000") as client:
        # Créer toutes les tâches
        tasks = []
        for file in files:
            task = await client.create_job(file)
            tasks.append(task)

        # Attendre toutes les tâches en parallèle
        results = await asyncio.gather(
            *[client.wait_for_task(t.id) for t in tasks]
        )

        return results

# Utilisation
files = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]
results = asyncio.run(process_multiple_files(files))
```

### 2. Surveillance en temps réel

```python
from ocr_sdk import SyncOCRClient, TaskStatus

with SyncOCRClient("http://localhost:5000") as client:
    task = client.create_job("large_document.pdf")

    # Surveiller la progression
    while True:
        current_task = client.get_task(task.id)
        print(f"Status: {current_task.status}")
        print(f"Progression: {current_task.percentage}%")

        if current_task.status == TaskStatus.COMPLETED.value:
            print("Traitement terminé!")
            break
        elif current_task.status == TaskStatus.FAILED.value:
            print("Traitement échoué!")
            break

        time.sleep(2)
```

### 3. Traitement avec zones d'intérêt

```python
import json
from ocr_sdk import SyncOCRClient, TaskOperation

# Définir les zones d'intérêt
interest_zones = [
    {
        "interest_zone": [
            {"x": 0.1, "y": 0.1, "width": 0.8, "height": 0.3, "text": ""}
        ],
        "labels": "header"
    }
]

with SyncOCRClient("http://localhost:5000") as client:
    task = client.create_job(
        "document.pdf",
        interest_zone=json.dumps(interest_zones),
        task_operation=TaskOperation.OCR
    )

    result = client.wait_for_task(task.id)
```

### 4. Extraction de formulaires

```python
from ocr_sdk import SyncOCRClient, TaskOperation

with SyncOCRClient("http://localhost:5000") as client:
    task = client.create_job(
        "formulaire.pdf",
        task_operation=TaskOperation.FORMS
    )

    result = client.wait_for_task(task.id)

    # Accéder aux champs du formulaire
    if result.output and result.output.pages:
        for page in result.output.pages:
            for entry in page.form_entries:
                print(f"{entry.field_name}: {entry.field_value}")
```

## Gestion des erreurs

### Gestion robuste des erreurs

```python
from ocr_sdk import SyncOCRClient
from ocr_sdk.exceptions import (
    OCRAPIError,
    OCRTimeoutError,
    OCRAuthenticationError,
)
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_with_error_handling(file_path):
    try:
        with SyncOCRClient("http://localhost:5000") as client:
            task = client.create_job(file_path)
            result = client.wait_for_task(task.id, max_wait_time=300)
            return client.get_task_text(task.id)

    except FileNotFoundError as e:
        logger.error(f"Fichier introuvable: {e}")
        return None

    except OCRTimeoutError as e:
        logger.error(f"Timeout lors du traitement: {e}")
        return None

    except OCRAPIError as e:
        logger.error(f"Erreur API {e.status_code}: {e.message}")
        return None

    except Exception as e:
        logger.error(f"Erreur inattendue: {e}")
        return None

# Utilisation
text = process_with_error_handling("document.pdf")
if text:
    print(f"Texte extrait: {text}")
```

### Retry avec backoff exponentiel

```python
import time
from ocr_sdk import SyncOCRClient
from ocr_sdk.exceptions import OCRAPIError

def process_with_retry(file_path, max_retries=3):
    with SyncOCRClient("http://localhost:5000") as client:
        for attempt in range(max_retries):
            try:
                task = client.create_job(file_path)
                return client.wait_for_task(task.id)

            except OCRAPIError as e:
                if e.status_code >= 500 and attempt < max_retries - 1:
                    # Erreur serveur, retry avec backoff
                    wait_time = 2 ** attempt
                    print(f"Tentative {attempt + 1} échouée, retry dans {wait_time}s")
                    time.sleep(wait_time)
                else:
                    raise
```

## Intégration dans un projet

### Exemple de classe wrapper

```python
from pathlib import Path
from typing import Optional, List
from ocr_sdk import SyncOCRClient, TaskModel, TaskStatus
from ocr_sdk.exceptions import OCRAPIError, OCRTimeoutError

class OCRService:
    """Service wrapper pour l'API OCR."""

    def __init__(self, api_url: str, api_key: Optional[str] = None):
        self.api_url = api_url
        self.api_key = api_key

    def extract_text(self, file_path: str, timeout: int = 300) -> Optional[str]:
        """Extrait le texte d'un document.

        Args:
            file_path: Chemin vers le fichier
            timeout: Timeout en secondes

        Returns:
            Texte extrait ou None en cas d'erreur
        """
        try:
            with SyncOCRClient(self.api_url, self.api_key) as client:
                task = client.create_job(file_path)
                result = client.wait_for_task(task.id, max_wait_time=timeout)
                return client.get_task_text(task.id)
        except (OCRAPIError, OCRTimeoutError) as e:
            print(f"Erreur lors de l'extraction: {e}")
            return None

    def batch_extract(self, file_paths: List[str]) -> dict:
        """Extrait le texte de plusieurs documents.

        Args:
            file_paths: Liste des chemins de fichiers

        Returns:
            Dictionnaire {file_path: texte_extrait}
        """
        results = {}
        with SyncOCRClient(self.api_url, self.api_key) as client:
            # Créer toutes les tâches
            tasks = {}
            for file_path in file_paths:
                try:
                    task = client.create_job(file_path)
                    tasks[task.id] = file_path
                except Exception as e:
                    results[file_path] = f"Erreur: {e}"

            # Attendre et récupérer les résultats
            for task_id, file_path in tasks.items():
                try:
                    result = client.wait_for_task(task_id)
                    if result.status == TaskStatus.COMPLETED.value:
                        text = client.get_task_text(task_id)
                        results[file_path] = text
                    else:
                        results[file_path] = f"Échec: {result.status}"
                except Exception as e:
                    results[file_path] = f"Erreur: {e}"

        return results

    def get_recent_tasks(self, page: int = 1, page_size: int = 10) -> List[TaskModel]:
        """Récupère les tâches récentes.

        Args:
            page: Numéro de page
            page_size: Nombre de tâches par page

        Returns:
            Liste des tâches
        """
        with SyncOCRClient(self.api_url, self.api_key) as client:
            return client.get_user_tasks(page, page_size)

# Utilisation
if __name__ == "__main__":
    service = OCRService("http://localhost:5000")

    # Extraire un seul document
    text = service.extract_text("document.pdf")
    if text:
        print(text)

    # Extraire plusieurs documents
    files = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]
    results = service.batch_extract(files)
    for file, text in results.items():
        print(f"{file}: {len(text)} caractères extraits")
```

### Intégration FastAPI

```python
from fastapi import FastAPI, UploadFile, HTTPException
from ocr_sdk import SyncOCRClient
from ocr_sdk.exceptions import OCRAPIError
import tempfile
import os

app = FastAPI()
OCR_API_URL = "http://localhost:5000"

@app.post("/process-document")
async def process_document(file: UploadFile):
    """Endpoint pour traiter un document."""

    # Sauvegarder temporairement le fichier
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        with SyncOCRClient(OCR_API_URL) as client:
            task = client.create_job(tmp_path)
            result = client.wait_for_task(task.id)
            text = client.get_task_text(task.id)

            return {
                "task_id": task.id,
                "status": result.status,
                "text": text,
                "pages": result.output.total_pages if result.output else 0
            }
    except OCRAPIError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    finally:
        # Nettoyer le fichier temporaire
        os.unlink(tmp_path)
```

## Bonnes pratiques

1. **Toujours utiliser les context managers** pour garantir la fermeture des connexions
2. **Gérer les timeouts** en fonction de la taille de vos documents
3. **Implémenter des retries** pour les erreurs temporaires
4. **Logger les erreurs** pour faciliter le débogage
5. **Utiliser le client async** pour les traitements en parallèle
6. **Valider les fichiers** avant de les envoyer à l'API
7. **Monitorer les quotas** si vous avez des limites d'utilisation

## Support

Pour plus d'informations:
- [README complet](README.md)
- [Guide de démarrage rapide](QUICKSTART.md)
- [Exemples](examples/)
