#!/bin/bash
# Script de vérification CI locale pour Mangetamain Analytics
# Exécute les mêmes checks que le pipeline GitHub Actions

set -e  # Exit on error

# Couleurs pour l'output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   CI/CD Local Checks - Mangetamain Analytics              ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Fonction pour afficher les étapes
step_counter=1
print_step() {
    echo -e "\n${BLUE}=== [$step_counter/6] $1 ===${NC}\n"
    ((step_counter++))
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Vérifier qu'on est dans le bon répertoire
if [ ! -f "README_CI_CD.md" ]; then
    print_error "Ce script doit être exécuté depuis 000_dev/"
    exit 1
fi

# Déterminer l'environnement à tester (défaut: production)
ENV="${1:-20_prod}"
if [ "$ENV" = "preprod" ]; then
    ENV="10_preprod"
    COV_PATH="src"
elif [ "$ENV" = "prod" ]; then
    ENV="20_prod"
    COV_PATH="streamlit"
else
    COV_PATH="streamlit"
fi

echo -e "Environnement testé: ${GREEN}$ENV${NC}"
echo ""

# 1. Vérifier que l'environnement virtuel existe
print_step "Vérification de l'environnement virtuel"
if [ ! -d "$ENV/.venv" ]; then
    print_warning "Environnement virtuel non trouvé, création en cours..."
    cd "$ENV"
    uv venv
    uv pip install -e ".[dev]"
    cd ..
    print_success "Environnement virtuel créé"
else
    print_success "Environnement virtuel trouvé"
fi

# Activer l'environnement virtuel
source "$ENV/.venv/bin/activate"

# 2. PEP8 Compliance avec flake8
print_step "Vérification PEP8 avec flake8"
cd "$ENV"
if [ "$ENV" = "20_prod" ]; then
    flake8 streamlit/ tests/ --config=../.flake8 --statistics --count || {
        print_error "Échec de la vérification PEP8"
        exit 1
    }
else
    flake8 src/ tests/ --config=../.flake8 --statistics --count || {
        print_error "Échec de la vérification PEP8"
        exit 1
    }
fi
cd ..
print_success "PEP8 compliance validée"

# 3. Formatage avec Black
print_step "Vérification du formatage avec Black"
cd "$ENV"
if [ "$ENV" = "20_prod" ]; then
    black --check --diff streamlit/ tests/ || {
        print_warning "Le code n'est pas formaté correctement"
        echo -e "${YELLOW}Lancer 'black streamlit/ tests/' pour corriger${NC}"
        read -p "Appliquer le formatage automatiquement ? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            black streamlit/ tests/
            print_success "Code formaté automatiquement"
        else
            exit 1
        fi
    }
else
    black --check --diff src/ tests/ || {
        print_warning "Le code n'est pas formaté correctement"
        echo -e "${YELLOW}Lancer 'black src/ tests/' pour corriger${NC}"
        read -p "Appliquer le formatage automatiquement ? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            black src/ tests/
            print_success "Code formaté automatiquement"
        else
            exit 1
        fi
    }
fi
cd ..
print_success "Formatage validé"

# 4. Docstrings avec pydocstyle
print_step "Vérification des docstrings avec pydocstyle"
cd "$ENV"
if [ "$ENV" = "20_prod" ]; then
    pydocstyle streamlit/ --config=../.pydocstyle || print_warning "Certaines docstrings sont manquantes (non bloquant)"
else
    pydocstyle src/ --config=../.pydocstyle || print_warning "Certaines docstrings sont manquantes (non bloquant)"
fi
cd ..
print_success "Vérification des docstrings terminée"

# 5. Type checking avec mypy (optionnel)
print_step "Vérification des types avec mypy (optionnel)"
cd "$ENV"
if [ "$ENV" = "20_prod" ]; then
    mypy streamlit/ --ignore-missing-imports || print_warning "Certains types ne sont pas corrects (non bloquant)"
else
    mypy src/ --ignore-missing-imports || print_warning "Certains types ne sont pas corrects (non bloquant)"
fi
cd ..
print_success "Type checking terminé"

# 6. Tests unitaires avec coverage
print_step "Exécution des tests avec coverage >= 90%"
cd "$ENV"
pytest tests/ -v --cov="$COV_PATH" --cov-report=term-missing --cov-report=html --cov-fail-under=90 || {
    print_error "Les tests ont échoué ou le coverage est < 90%"
    print_warning "Rapport HTML disponible dans $ENV/htmlcov/index.html"
    exit 1
}
cd ..
print_success "Tous les tests sont passés avec coverage >= 90%"

# Résumé final
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   ✅ Tous les checks CI ont passé avec succès !            ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Prochaines étapes:${NC}"
echo "  1. git add ."
echo "  2. git commit -m 'votre message'"
echo "  3. git push"
echo ""
echo -e "${BLUE}Rapport de coverage HTML:${NC} $ENV/htmlcov/index.html"
echo ""
