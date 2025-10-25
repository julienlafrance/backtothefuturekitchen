#!/bin/bash
################################################################################
# Script de déploiement PREPROD → PROD (simplifié)
#
# Description : Backup, efface et recrée 20_prod/ depuis 10_preprod/
# Utilisation : ./deploy_preprod_to_prod.sh
################################################################################

set -e

# Configuration
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_DIR="$BASE_DIR/backups/prod_$(date +%Y%m%d_%H%M%S)"
PROD_DIR="$BASE_DIR/20_prod"

# Couleurs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}🚀 Déploiement PREPROD → PROD${NC}"
echo "================================"

# 1. BACKUP
echo -e "\n${YELLOW}📦 Backup 20_prod/${NC}"
mkdir -p "$BACKUP_DIR"
if [ -d "$PROD_DIR/streamlit" ]; then
    cp -r "$PROD_DIR/streamlit" "$BACKUP_DIR/"
    echo "✅ Backup → $BACKUP_DIR/streamlit/"
fi

# 2. EFFACE (garde .gitkeep)
echo -e "\n${YELLOW}🗑️  Nettoyage 20_prod/${NC}"

# Supprimer les __pycache__ créés par Docker (ignorer erreurs permissions)
find "$PROD_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Supprimer le reste
rm -rf "$PROD_DIR"/{streamlit,logs,.venv,pyproject.toml,README.md,uv.lock}
echo "✅ Répertoire nettoyé"

# 3. COPIE (3 éléments)
echo -e "\n${YELLOW}📋 Copie PREPROD → PROD${NC}"

# Créer structure
mkdir -p "$PROD_DIR/streamlit"
mkdir -p "$PROD_DIR/logs"

# 1. Code source
cp -r "$BASE_DIR/10_preprod/src/mangetamain_analytics"/* "$PROD_DIR/streamlit/"
echo "✅ streamlit/ (code source)"

# 2. pyproject.toml
cp "$BASE_DIR/10_preprod/pyproject.toml" "$PROD_DIR/"
echo "✅ pyproject.toml"

# 3. README.md
cp "$BASE_DIR/10_preprod/README.md" "$PROD_DIR/"
echo "✅ README.md"

# 4. RÉSULTAT
echo -e "\n${GREEN}✅ DÉPLOIEMENT TERMINÉ${NC}"
echo "================================"
echo "Backup  : $BACKUP_DIR"
echo "PROD    : $PROD_DIR"
echo ""
echo "Prochaine étape: GitHub Actions redémarrera le container"
