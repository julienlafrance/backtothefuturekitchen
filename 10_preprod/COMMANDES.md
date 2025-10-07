# 🚀 COMMANDES ESSENTIELLES - Mangetamain Analytics
## Dossier de travail : ~/mangetamain/00_preprod

## 📦 Installation initiale

```bash
# 1. Créer et aller dans le dossier
mkdir -p ~/mangetamain/00_preprod
cd ~/mangetamain/00_preprod

# 2. Extraire le projet complet
unzip ~/Downloads/mangetamain-analytics-complete.zip

# 3. Installer UV (si pas déjà fait)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 4. Lancer le script d'installation
chmod +x ubuntu_setup.sh
./ubuntu_setup.sh

# Ou manuellement :
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

## 🖥️ Développement quotidien

```bash
# Aller dans le projet
cd ~/mangetamain/00_preprod

# Activer l'environnement
source .venv/bin/activate

# Lancer l'application Streamlit
streamlit run src/mangetamain_analytics/main.py

# Ou avec UV
uv run streamlit run src/mangetamain_analytics/main.py
```

## 🧪 Tests et qualité

```bash
# Formater le code (PEP 8)
black src/ tests/

# Vérifier la syntaxe
flake8 src/ tests/

# Vérifier les types
mypy src/

# Lancer les tests
pytest

# Tests avec couverture
pytest --cov=src --cov-report=html

# Voir le rapport de couverture
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

## 📚 Documentation

```bash
# Générer la documentation
cd docs/
sphinx-quickstart  # Première fois seulement
make html

# Voir la documentation
open _build/html/index.html
```

## 🔧 Git workflow

```bash
# Configuration initiale (dans ~/mangetamain/00_preprod)
cd ~/mangetamain/00_preprod
git config user.name "Votre Nom"
git config user.email "votre.email@example.com"

# Workflow recommandé
git checkout -b feature/nom-feature
# ... développement ...
git add .
git commit -m "feat: description de la feature"
git push origin feature/nom-feature
# Créer une Pull Request sur GitHub

# Merge sur main
git checkout main
git pull origin main
git merge feature/nom-feature
git push origin main
```

## 📊 Données

```bash
# Télécharger les données Kaggle
# 1. Aller sur https://www.kaggle.com/datasets/shuyangli94/food-com-recipes-and-user-interactions
# 2. Télécharger le zip
# 3. Extraire dans le dossier data/

# Structure attendue dans ~/mangetamain/00_preprod :
# data/
# ├── interactions_train.csv
# ├── interactions_test.csv
# ├── interactions_validation.csv
# └── PP_users.csv
```

## 🚀 Déploiement Streamlit Cloud

```bash
# 1. Pousser le code sur GitHub (depuis ~/mangetamain/00_preprod)
cd ~/mangetamain/00_preprod
git push origin main

# 2. Aller sur https://share.streamlit.io/
# 3. Connecter votre repository GitHub
# 4. Configurer :
#    - Repository: votre-username/mangetamain-analytics
#    - Branch: main
#    - Main file path: src/mangetamain_analytics/main.py

# 5. Ajouter les secrets (si nécessaire) dans les settings
```

## 📝 Commandes de vérification finale

```bash
# Vérifier que tout fonctionne avant soumission
make check-all  # Si vous créez un Makefile

# Ou manuellement :
black --check src/ tests/
flake8 src/ tests/
mypy src/
pytest --cov=src --cov-fail-under=90
cd docs/ && make html
```

## 🔍 Debug et logs

```bash
# Voir les logs de l'application
tail -f logs/app.log

# Logs d'erreurs seulement
tail -f logs/errors.log

# Logs des interactions utilisateur
tail -f logs/user_interactions.log

# Debug Streamlit
streamlit run src/mangetamain_analytics/main.py --logger.level=debug
```

## 🆘 En cas de problème

```bash
# Réinstaller l'environnement
rm -rf .venv
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt

# Nettoyer les caches
rm -rf __pycache__ .pytest_cache .mypy_cache
find . -name "*.pyc" -delete

# Vérifier l'installation UV
uv --version

# Vérifier Python
python --version
which python
```

## 📋 Checklist avant push

```bash
□ black src/ tests/           # Code formaté
□ flake8 src/ tests/          # PEP 8 OK
□ mypy src/                   # Types OK
□ pytest --cov=src           # Tests OK
□ streamlit run main.py       # App fonctionne
□ git status                  # Rien d'oublié
□ git commit -m "..."         # Message clair
```

## 🎯 Commandes par phase

### Phase 1 : Setup
```bash
cd ~/mangetamain/00_preprod
./ubuntu_setup.sh
git remote add origin https://github.com/username/repo.git
git push -u origin main
```

### Phase 2 : Développement
```bash
git checkout -b develop
# ... code ...
pytest && streamlit run main.py
git commit -am "feat: nouvelle fonctionnalité"
```

### Phase 3 : Tests
```bash
pytest --cov=src --cov-fail-under=90
black src/ tests/
flake8 src/ tests/
mypy src/
```

### Phase 4 : Documentation
```bash
cd docs/
make html
git add docs/
git commit -m "docs: mise à jour documentation"
```

### Phase 5 : Déploiement
```bash
git checkout main
git merge develop
git push origin main
# -> Déploiement automatique Streamlit Cloud
```

---

**💡 Conseil** : Gardez ce fichier sous la main et exécutez ces commandes régulièrement !
