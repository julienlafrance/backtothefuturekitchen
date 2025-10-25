#!/bin/bash
################################################################################
# Script de déploiement PREPROD → PROD
#
# Description : Copie les fichiers de 10_preprod/ vers 20_prod/
# Utilisation : ./deploy_preprod_to_prod.sh
#
# Note : Ce script est exécuté localement sur dataia
#        GitHub Actions gère le redémarrage Docker et les tests
#
# Auteur : Project team
# Date : 2025-10-25
################################################################################

set -e  # Arrêter le script en cas d'erreur

# Configuration
LOG_FILE="logs/deploy_$(date +%Y%m%d_%H%M%S).log"
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PREPROD_DIR="$BASE_DIR/10_preprod/src/mangetamain_analytics"
PROD_DIR="$BASE_DIR/20_prod/streamlit"

# Couleurs pour affichage console
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

################################################################################
# Fonction de logging
################################################################################
log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    echo "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"

    # Affichage console avec couleurs
    case $level in
        ERROR)
            echo -e "${RED}❌ $message${NC}"
            ;;
        SUCCESS)
            echo -e "${GREEN}✅ $message${NC}"
            ;;
        INFO)
            echo -e "ℹ️  $message"
            ;;
        WARNING)
            echo -e "${YELLOW}⚠️  $message${NC}"
            ;;
    esac
}

################################################################################
# Fonction de gestion d'erreur
################################################################################
handle_error() {
    local step=$1
    local error_msg=$2
    log "ERROR" "Échec lors de l'étape : $step"
    log "ERROR" "Détails : $error_msg"
    log "ERROR" "Déploiement interrompu avec code d'erreur 1"
    exit 1
}

################################################################################
# Début du script
################################################################################
log "INFO" "=========================================="
log "INFO" "Déploiement PREPROD → PROD - Début"
log "INFO" "=========================================="
log "INFO" "Base directory: $BASE_DIR"
log "INFO" "Log file: $LOG_FILE"

# Créer le répertoire logs s'il n'existe pas
mkdir -p logs

################################################################################
# Vérifications préliminaires
################################################################################
log "INFO" "Étape 1/6 : Vérifications préliminaires"

if [ ! -d "$PREPROD_DIR" ]; then
    handle_error "Vérification PREPROD" "Répertoire PREPROD introuvable : $PREPROD_DIR"
fi

if [ ! -f "$PREPROD_DIR/main.py" ]; then
    handle_error "Vérification main.py" "Fichier main.py introuvable dans PREPROD"
fi

# Créer la structure de base PROD si elle n'existe pas
log "INFO" "Création de la structure de base PROD si nécessaire..."
mkdir -p "$BASE_DIR/20_prod/streamlit" || handle_error "Création structure" "Impossible de créer 20_prod/streamlit"
mkdir -p "$BASE_DIR/20_prod/logs" || handle_error "Création structure" "Impossible de créer 20_prod/logs"
# Note: data/ not created - all data loaded from S3 Parquet files

log "SUCCESS" "Vérifications préliminaires OK"

################################################################################
# Copie des modules de visualisation
################################################################################
log "INFO" "Étape 2/6 : Copie des modules de visualisation"

if [ ! -d "$PREPROD_DIR/visualization" ]; then
    handle_error "Copie visualization" "Répertoire visualization/ introuvable dans PREPROD"
fi

# Créer le répertoire de destination s'il n'existe pas
mkdir -p "$PROD_DIR/visualization" || handle_error "Copie visualization" "Impossible de créer $PROD_DIR/visualization"

# Copier tous les fichiers .py
cp "$PREPROD_DIR/visualization"/*.py "$PROD_DIR/visualization/" 2>/dev/null || handle_error "Copie visualization" "Échec de la copie des fichiers .py"

# Compter les fichiers copiés
nb_files=$(ls -1 "$PROD_DIR/visualization"/*.py 2>/dev/null | wc -l)
log "SUCCESS" "Modules de visualisation copiés ($nb_files fichiers)"

################################################################################
# Copie des utilitaires (utils/)
################################################################################
log "INFO" "Étape 3/6 : Copie des utilitaires"

if [ ! -d "$PREPROD_DIR/utils" ]; then
    handle_error "Copie utils" "Répertoire utils/ introuvable dans PREPROD"
fi

# Créer le répertoire de destination s'il n'existe pas
mkdir -p "$PROD_DIR/utils" || handle_error "Copie utils" "Impossible de créer $PROD_DIR/utils"

# Copier tous les fichiers .py
cp "$PREPROD_DIR/utils"/*.py "$PROD_DIR/utils/" 2>/dev/null || handle_error "Copie utils" "Échec de la copie des fichiers .py"

# Compter les fichiers copiés
nb_files=$(ls -1 "$PROD_DIR/utils"/*.py 2>/dev/null | wc -l)
log "SUCCESS" "Utilitaires copiés ($nb_files fichiers)"

################################################################################
# Copie des assets (CSS, logo, favicon)
################################################################################
log "INFO" "Étape 4/6 : Copie des assets"

if [ ! -d "$PREPROD_DIR/assets" ]; then
    handle_error "Copie assets" "Répertoire assets/ introuvable dans PREPROD"
fi

# Créer le répertoire de destination s'il n'existe pas
mkdir -p "$PROD_DIR/assets" || handle_error "Copie assets" "Impossible de créer $PROD_DIR/assets"

# Copier tous les fichiers
cp -r "$PREPROD_DIR/assets/"* "$PROD_DIR/assets/" 2>/dev/null || handle_error "Copie assets" "Échec de la copie des fichiers assets"

# Compter les fichiers copiés
nb_files=$(ls -1 "$PROD_DIR/assets" 2>/dev/null | wc -l)
log "SUCCESS" "Assets copiés ($nb_files fichiers)"

################################################################################
# Copie du fichier principal main.py
################################################################################
log "INFO" "Étape 5/8 : Copie du fichier main.py"

# Backup de l'ancien main.py
if [ -f "$PROD_DIR/main.py" ]; then
    backup_file="$PROD_DIR/main.py.backup_$(date +%Y%m%d_%H%M%S)"
    cp "$PROD_DIR/main.py" "$backup_file" || log "WARNING" "Impossible de créer le backup de main.py"
    log "INFO" "Backup créé : $backup_file"
fi

# Copier le nouveau main.py
cp "$PREPROD_DIR/main.py" "$PROD_DIR/main.py" || handle_error "Copie main.py" "Échec de la copie de main.py"

# Vérifier la taille du fichier copié
file_size=$(stat -f%z "$PROD_DIR/main.py" 2>/dev/null || stat -c%s "$PROD_DIR/main.py" 2>/dev/null)
log "SUCCESS" "main.py copié ($file_size bytes)"

################################################################################
# Copie des dépendances Python (pyproject.toml et uv.lock)
################################################################################
log "INFO" "Étape 6/8 : Synchronisation des dépendances Python"

PREPROD_ROOT="$BASE_DIR/10_preprod"
PROD_ROOT="$BASE_DIR/20_prod"

# Vérifier que pyproject.toml existe en PREPROD
if [ ! -f "$PREPROD_ROOT/pyproject.toml" ]; then
    handle_error "Copie pyproject.toml" "Fichier pyproject.toml introuvable dans PREPROD"
fi

# Backup de l'ancien pyproject.toml
if [ -f "$PROD_ROOT/pyproject.toml" ]; then
    backup_pyproject="$PROD_ROOT/pyproject.toml.backup_$(date +%Y%m%d_%H%M%S)"
    cp "$PROD_ROOT/pyproject.toml" "$backup_pyproject" || log "WARNING" "Impossible de créer backup pyproject.toml"
    log "INFO" "Backup pyproject.toml créé : $backup_pyproject"
fi

# Copier pyproject.toml et adapter pour PROD
cp "$PREPROD_ROOT/pyproject.toml" "$PROD_ROOT/pyproject.toml" || handle_error "Copie pyproject.toml" "Échec de la copie"

# Adaptations pour PROD :
# 1. Commenter readme car README.md n'est pas déployé en PROD (artifact)
sed -i 's/^readme = .*$/# readme = "README.md" (disabled in PROD - artifact)/' "$PROD_ROOT/pyproject.toml"

# 2. Commenter [build-system] pour éviter de builder le package en PROD
# On veut juste installer les dépendances, pas construire un wheel
sed -i 's/^\[build-system\]$/# [build-system] (disabled in PROD - no package build needed)/' "$PROD_ROOT/pyproject.toml"
sed -i 's/^requires = \["hatchling"\]$/# requires = ["hatchling"]/' "$PROD_ROOT/pyproject.toml"
sed -i 's/^build-backend = "hatchling.build"$/# build-backend = "hatchling.build"/' "$PROD_ROOT/pyproject.toml"

log "SUCCESS" "pyproject.toml copié et adapté pour PROD (readme et build-system désactivés)"

# NE PAS copier uv.lock : il doit être régénéré par 'uv sync' en PROD
# car pyproject.toml a été modifié (build-system commenté)
if [ -f "$PROD_ROOT/uv.lock" ]; then
    backup_uvlock="$PROD_ROOT/uv.lock.backup_$(date +%Y%m%d_%H%M%S)"
    mv "$PROD_ROOT/uv.lock" "$backup_uvlock" || log "WARNING" "Impossible de créer backup uv.lock"
    log "INFO" "Ancien uv.lock sauvegardé : $backup_uvlock"
fi
log "INFO" "uv.lock sera régénéré par 'uv sync' au démarrage du container PROD"

log "SUCCESS" "Dépendances Python synchronisées"

################################################################################
# Création du README.md bidon (requis par pyproject.toml build)
################################################################################
log "INFO" "Étape 7/9 : Création du README.md pour build Python"

# Supprimer l'ancien README.md s'il existe (fichier ou répertoire)
if [ -e "$PROD_ROOT/README.md" ]; then
    log "INFO" "Ancien README.md détecté, suppression..."
    rm -rf "$PROD_ROOT/README.md" || log "WARNING" "Impossible de supprimer l'ancien README.md"
fi

# Créer le nouveau README.md
cat > "$PROD_ROOT/README.md" << 'EOF'
# PROD - Artifact

Ce répertoire est un **artifact généré** par le script de déploiement.

**Source de vérité** : `10_preprod/`

**Ne pas modifier directement ce répertoire.**

Fichier README.md requis par pyproject.toml pour le build Python.
EOF

if [ -f "$PROD_ROOT/README.md" ]; then
    log "SUCCESS" "README.md créé (fichier bidon pour build Python)"
else
    handle_error "Création README.md" "Échec de la création du fichier README.md"
fi

################################################################################
# Résumé final
################################################################################
log "INFO" "Étape 8/9 : Redémarrage du container requis"
log "INFO" "⚠️  Les nouvelles dépendances Python nécessitent un redémarrage du container PROD"
log "INFO" "Le container fera 'uv sync' au démarrage pour installer les packages"

log "INFO" "Étape 9/9 : Résumé du déploiement"

log "SUCCESS" "=========================================="
log "SUCCESS" "Déploiement terminé avec succès !"
log "SUCCESS" "=========================================="
log "INFO" "Fichiers copiés de PREPROD → PROD :"
log "INFO" "  - visualization/   : Modules d'analyse"
log "INFO" "  - utils/           : Utilitaires (colors, chart_theme)"
log "INFO" "  - assets/          : CSS, logo, favicon"
log "INFO" "  - main.py          : Application principale"
log "INFO" "  - pyproject.toml   : Dépendances Python (adapté pour PROD)"
log "INFO" "  - README.md        : Fichier bidon pour build Python"
log "INFO" ""
log "INFO" "⚠️  uv.lock sera régénéré par 'uv sync' dans le container PROD"
log "INFO" ""
log "INFO" "Prochaines étapes (gérées par GitHub Actions) :"
log "INFO" "  1. Redémarrage du container Docker PROD"
log "INFO" "  2. Health checks automatiques"
log "INFO" "  3. Notification Discord"
log "INFO" ""
log "INFO" "Log complet : $LOG_FILE"
log "SUCCESS" "=========================================="

exit 0
