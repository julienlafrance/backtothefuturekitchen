#!/bin/bash
# Script pour déclencher le déploiement en production
# Usage: ./deploy_prod.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOKEN_FILE="$SCRIPT_DIR/96_keys/github_deploy_token.txt"

if [ ! -f "$TOKEN_FILE" ]; then
    echo "❌ Token introuvable: $TOKEN_FILE"
    exit 1
fi

TOKEN=$(cat "$TOKEN_FILE")

echo "🚀 Déclenchement du déploiement en PRODUCTION..."
echo "📦 Repo: julienlafrance/backtothefuturekitchen"
echo ""

RESPONSE=$(curl -s -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/julienlafrance/backtothefuturekitchen/actions/workflows/cd-prod.yml/dispatches \
  -d '{"ref":"main","inputs":{"confirm":"DEPLOY"}}')

if [ $? -eq 0 ]; then
    echo "✅ Déploiement déclenché avec succès!"
    echo ""
    echo "🔗 Voir le workflow:"
    echo "   https://github.com/julienlafrance/backtothefuturekitchen/actions/workflows/cd-prod.yml"
    echo ""
    echo "💡 Pour suivre en temps réel:"
    echo "   gh run list --workflow=\"CD - Production Deployment\" --limit 3"
    echo "   gh run watch"
else
    echo "❌ Erreur lors du déclenchement"
    echo "$RESPONSE"
    exit 1
fi
