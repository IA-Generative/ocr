#!/bin/bash

# Variables d'environnement (à définir dans votre système)
KEYCLOAK_URL="${KEYCLOAK_URL:-http://localhost/realms/mirai/protocol/openid-connect/token}"
CLIENT_ID="${CLIENT_ID:-api-preprod}"
CLIENT_SECRET="${CLIENT_SECRET}"
DELETE_URL="${DELETE_URL:-http://localhost/api/v1/tasks/}"

# Paramètres de date
END_DATE="${END_DATE:-$(date -u +"%Y-%m-%dT%H:%M:%S")}"  # Date actuelle par défaut
DAYS_BACK="${DAYS_BACK:-30}"  # 30 jours par défaut

# Liste de tous les statuts possibles (basé sur TaskStatus)
STATUSES=("completed" "failed")

# Vérification des variables obligatoires
if [ -z "$CLIENT_SECRET" ]; then
    echo "Erreur: CLIENT_SECRET doit être défini dans les variables d'environnement"
    exit 1
fi

# Calcul de la start_date
if command -v date >/dev/null 2>&1; then
    # Linux/GNU date
    START_DATE=$(date -u -d "$END_DATE - $DAYS_BACK days" +"%Y-%m-%dT%H:%M:%S" 2>/dev/null)
    if [ -z "$START_DATE" ]; then
        # Fallback si END_DATE n'est pas au bon format
        START_DATE=$(date -u -d "$(date -u +"%Y-%m-%d") - $DAYS_BACK days" +"%Y-%m-%dT00:00:00")
    fi
else
    echo "Erreur: commande 'date' non disponible"
    exit 1
fi

echo "=== Configuration ==="
echo "  Période: du $START_DATE au $END_DATE ($DAYS_BACK jours)"
echo "  Statuts: ${STATUSES[*]}"
echo "  URL: $DELETE_URL"
echo ""

# Récupération du token
echo "🔐 Récupération du token d'authentification..."
RETRIEVE_TOKEN_START=$(curl -s -X POST \
  "$KEYCLOAK_URL" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials" \
  -d "client_id=$CLIENT_ID" \
  -d "client_secret=$CLIENT_SECRET" )

ACCESS_TOKEN=$(echo "$RETRIEVE_TOKEN_START" | jq -r '.access_token')

# Vérification du token
if [ "$ACCESS_TOKEN" == "null" ] || [ -z "$ACCESS_TOKEN" ]; then
    echo "❌ Erreur: Impossible d'obtenir le token d'accès"
    echo "Réponse Keycloak: $RETRIEVE_TOKEN_START"
    exit 1
fi

echo "✅ Token obtenu avec succès"
echo ""

# Variables pour le résumé
TOTAL_DELETED=0
FAILED_STATUSES=()

# Traitement de chaque statut
for STATUS in "${STATUSES[@]}"; do
    echo "🔄 Traitement du statut: $STATUS"

    RESPONSE=$(curl -s -w "\n%{http_code}" -X DELETE "$DELETE_URL" \
      -H "Authorization: Bearer $ACCESS_TOKEN" \
      -H "Content-Type: application/json" \
      -G \
      --data-urlencode "start_date=$START_DATE" \
      --data-urlencode "end_date=$END_DATE" \
      --data-urlencode "status=$STATUS")

    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | sed '$d')

    if [ "$HTTP_CODE" -eq 200 ] || [ "$HTTP_CODE" -eq 204 ]; then
        # L'API répond 204 sans corps : il n'y a alors aucun décompte à relire.
        COUNT=0
        if [ -n "$BODY" ]; then
            COUNT=$(echo "$BODY" | jq '. | length' 2>/dev/null || echo "0")
        fi
        TOTAL_DELETED=$((TOTAL_DELETED + COUNT))

        if [ "$HTTP_CODE" -eq 204 ]; then
            echo "  ✅ Purge acceptée pour le statut '$STATUS' (204, pas de décompte renvoyé)"
        elif [ "$COUNT" -gt 0 ]; then
            echo "  ✅ $COUNT tâches supprimées avec le statut '$STATUS'"
        else
            echo "  ℹ️ Aucune tâche trouvée avec le statut '$STATUS'"
        fi
    else
        echo "  ❌ Erreur pour le statut '$STATUS' (Code HTTP: $HTTP_CODE)"
        echo "  Réponse: $BODY"
        FAILED_STATUSES+=("$STATUS")
    fi

    # Pause courte entre les requêtes
    sleep 1
done

echo ""
echo "=== Résumé ==="
echo "📊 Total de tâches supprimées: $TOTAL_DELETED"
echo "📅 Période: du $START_DATE au $END_DATE"

if [ ${#FAILED_STATUSES[@]} -gt 0 ]; then
    echo "⚠️ Échecs pour les statuts: ${FAILED_STATUSES[*]}"
    exit 1
else
    echo "🎉 Purge réussie pour tous les statuts"
fi

echo "🏁 Purge terminée"
