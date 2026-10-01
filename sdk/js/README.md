# ocr-sdk (JS/TypeScript)

Client TypeScript/Node.js pour l'API OCR MIrAI. Équivalent JS du [SDK Python](../README.md), même couverture de routes.

Cible Node.js uniquement (≥ 18, `fetch` natif) — pas prévu pour tourner dans un navigateur (pas de bundler/polyfill fourni).

## Installation

Ce SDK vit dans un sous-dossier de ce monorepo, pas dans son propre dépôt :

```bash
npm install "git+https://github.com/IA-Generative/ocr.git#path:sdk/js"
# ou avec pnpm
pnpm add "git+https://github.com/IA-Generative/ocr.git#path:sdk/js"
```

npm/pnpm exécutent automatiquement le script `prepare` (compilation TypeScript) après un install depuis Git.

### En local (développement du SDK lui-même)

```bash
cd sdk/js
npm install
npm run build
```

## Utilisation

### Avec une clé API statique

```ts
import { OCRClient } from 'ocr-sdk'

const client = new OCRClient('http://localhost:5000', { apiKey: 'your-api-key' })

const task = await client.createJob('path/to/document.pdf')
const result = await client.waitForTask(task.id)

if (result.status === 'completed') {
  const text = await client.getTaskText(task.id)
  console.log(text)
}
```

### Authentification par identifiants Keycloak (username/password)

```ts
import { OCRClient } from 'ocr-sdk'

const client = new OCRClient('http://localhost:5000')
await client.login('user@example.com', 'hunter2')

const task = await client.createJob('path/to/document.pdf')
```

`login()` appelle `POST /api/auth/token` sur cette API : c'est le backend qui échange les identifiants avec Keycloak, le secret du client Keycloak ne quitte jamais le backend. Le jeton d'accès expire (5 minutes par défaut côté Keycloak), mais un refresh token est aussi stocké automatiquement — dès qu'une requête reçoit un 401, le client se rafraîchit tout seul avant de rejouer la requête. Pour rafraîchir explicitement, appelez `await client.refresh()` ; si le refresh token lui-même a expiré, `refresh()` lève `OCRAuthenticationError` et il faut rappeler `login()`.

### Traitement direct avec `processDocument`

```ts
const results = await client.processDocument('path/to/document.pdf')
for (const result of results) {
  console.log(result.page_content)
}
```

### Récupérer les tâches de l'utilisateur

```ts
const tasks = await client.getUserTasks(1, 10) // paginé : { total, page, page_size, items }
for (const task of tasks.items ?? []) {
  console.log(task.id, task.status)
}
```

## Gestion des erreurs

```ts
import { OCRAPIError, OCRAuthenticationError, OCRTimeoutError } from 'ocr-sdk'

try {
  const task = await client.createJob('document.pdf')
  await client.waitForTask(task.id, { maxWaitTimeMs: 60_000 })
}
catch (err) {
  if (err instanceof OCRTimeoutError) {
    console.error('Timeout:', err.message)
  }
  else if (err instanceof OCRAPIError) {
    console.error(`API error ${err.statusCode}:`, err.body)
  }
  else if (err instanceof OCRAuthenticationError) {
    console.error('Auth failed:', err.message)
  }
}
```

## Référence API

`OCRClient` (constructeur : `new OCRClient(baseUrl, { apiKey?, timeoutMs? })`) :

- `login(username, password)` — authentification Keycloak
- `refresh()` — renouvelle le jeton d'accès de façon proactive (appelé automatiquement sur un 401)
- `getHealth()`
- `createJob(filePath, { groupId?, interestZone?, taskOperation? })`
- `getTask(taskId)`
- `getTaskPageImage(taskId, pageNumber)` — retourne un `Buffer`
- `getUserTasks(page?, pageSize?)`
- `getTaskStats(page?, pageSize?)`
- `getUsersCountToday()`
- `deleteTask(taskId)`
- `deleteTasksByDateAndStatus(startDate, endDate, status)` — admin uniquement
- `getTaskText(taskId)`
- `getTaskValue(taskId, transform?)` — `"text" | "form" | "form-csv" | "only-result"`
- `processDocument(filePath, { mimeType?, maxWaitTimeSeconds?, pollIntervalSeconds? })`
- `waitForTask(taskId, { pollIntervalMs?, maxWaitTimeMs? })`

Les routes `template`/`collections` existent côté backend mais ne sont pas montées (`ocr_backend/main.py`) — aucune méthode ne les appelle, elles renverraient 404.

## Développement

```bash
npm install
npm run build        # compile src/ -> dist/
npm run test         # vitest, mock de fetch
npm run lint
npm run type-check
```

## Compatibilité

- Node.js >= 18
- TypeScript >= 5.9 (pour le développement du SDK — les consommateurs n'ont besoin que du JS compilé)
