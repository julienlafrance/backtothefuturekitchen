# 🍽️ Mangetamain Analytics

Application web d'analyse de données pour l'entreprise Mangetamain, spécialisée dans la recommandation de recettes de cuisine.

## 📋 Description

Cette application Streamlit analyse les données de recettes et d'interactions utilisateurs du dataset Food.com pour découvrir des insights sur les préférences culinaires et les comportements des utilisateurs.

## 🗂️ Structure du projet

```
mangetamain-analytics/
├── src/
│   └── mangetamain_analytics/
│       ├── main.py              # Application Streamlit principale
│       ├── data/                # Modules de données
│       ├── models/              # Modèles et BDD
│       ├── visualization/       # Graphiques et dashboards
│       ├── utils/               # Utilitaires (logs, helpers)
│       └── pages/               # Pages Streamlit
├── tests/                       # Tests unitaires et d'intégration
├── docs/                        # Documentation Sphinx
├── logs/                        # Fichiers de logs
├── config/                      # Configuration
├── pyproject.toml              # Configuration UV et projet
├── requirements.txt            # Dépendances principales
└── requirements-dev.txt        # Dépendances de développement
```

## 🚀 Installation

### Prérequis
- Python 3.9+
- UV (gestionnaire de packages moderne)

### Installation d'UV
```bash
# Sur macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Sur Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Cloner et configurer le projet
```bash
# Créer la structure de dossiers
mkdir -p ~/mangetamain/00_preprod
cd ~/mangetamain/00_preprod

# Extraire le projet (depuis le ZIP fourni)
unzip ~/Downloads/mangetamain-analytics-complete.zip

# Créer et activer l'environnement virtuel avec UV
uv venv
source .venv/bin/activate  # Linux/macOS
# ou .venv\Scripts\activate  # Windows

# Installer les dépendances
uv pip install -r requirements.txt

# Pour le développement, installer aussi les dépendances dev
uv pip install -r requirements-dev.txt

# Copier le fichier d'environnement
cp .env.example .env
```

## 📊 Données

### Dataset Food.com
Le projet utilise le dataset Food.com disponible sur Kaggle :
- **Source** : https://www.kaggle.com/datasets/shuyangli94/food-com-recipes-and-user-interactions
- **Taille** : 25,076 utilisateurs, ~180,000 recettes, 700K+ interactions
- **Période** : 1999-2018

### Fichiers de données
- `interactions_train.csv` : 698,901 interactions d'entraînement
- `interactions_test.csv` : 12,455 interactions de test
- `interactions_validation.csv` : 7,023 interactions de validation
- `PP_users.csv` : 25,076 profils utilisateurs

### Télécharger les données
1. Créer un compte sur Kaggle
2. Télécharger le dataset depuis le lien ci-dessus
3. Extraire les fichiers CSV dans le dossier `data/`

## 🖥️ Utilisation

### Lancer l'application
```bash
# Se placer dans le bon dossier
cd ~/mangetamain/00_preprod

# Démarrer l'application Streamlit
streamlit run src/mangetamain_analytics/main.py

# Ou avec UV
uv run streamlit run src/mangetamain_analytics/main.py
```

L'application sera accessible sur http://localhost:8501

### Fonctionnalités
- ✅ Chargement et validation des données
- ✅ Visualisations interactives (distribution des ingrédients)
- ✅ Métriques clés du dataset
- ✅ Interface utilisateur intuitive
- 🔄 Base de données DuckDB intégrée
- 🔄 Système de logs avec Loguru

## 🛠️ Développement

### Outils de qualité de code
```bash
# Formatage avec Black
black src/ tests/

# Vérification PEP 8 avec Flake8
flake8 src/ tests/

# Type checking avec MyPy
mypy src/

# Tests avec pytest
pytest tests/ --cov=src --cov-report=html

# Pre-commit hooks (optionnel)
pre-commit install
```

### Structure des logs
- `logs/app.log` : Logs généraux de l'application
- `logs/errors.log` : Erreurs uniquement
- `logs/user_interactions.log` : Actions utilisateurs

### Tests
```bash
# Lancer tous les tests
pytest

# Tests avec couverture
pytest --cov=src --cov-report=html

# Tests unitaires seulement
pytest tests/unit/

# Tests d'intégration seulement
pytest tests/integration/
```

## 📚 Documentation

### Générer la documentation
```bash
cd docs/
sphinx-quickstart  # Si première fois
make html
```

La documentation sera disponible dans `docs/_build/html/`

## 🚢 Déploiement

### Streamlit Cloud
1. Pousser le code sur GitHub
2. Connecter le repository à Streamlit Cloud
3. Configurer les variables d'environnement
4. Déployer automatiquement

### Autres plateformes
- **Heroku** : Ajouter un `Procfile`
- **AWS/GCP** : Utiliser Docker
- **Azure** : Azure Container Instances

## 🧪 Tests et CI/CD

### GitHub Actions
Le pipeline CI/CD vérifie automatiquement :
- ✅ Respect PEP 8 (Flake8)
- ✅ Type hints (MyPy)
- ✅ Tests unitaires (pytest)
- ✅ Couverture de code >90%
- ✅ Documentation (Sphinx)

### Configuration GitHub Actions
Créer `.github/workflows/ci.yml` pour automatiser les vérifications.

## 📈 Roadmap

### Phase 1 : Base (Actuelle)
- [x] Structure du projet
- [x] Configuration UV + Loguru
- [x] Application Streamlit de base
- [x] Intégration DuckDB
- [x] Visualisation simple

### Phase 2 : Analyse avancée
- [ ] Analyse des utilisateurs actifs
- [ ] Tendances temporelles
- [ ] Clustering des recettes
- [ ] Système de recommandation

### Phase 3 : Fonctionnalités avancées
- [ ] Machine Learning
- [ ] API REST
- [ ] Authentification utilisateur
- [ ] Tableaux de bord administrateur

## 🤝 Contribution

1. Fork le project
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit (`git commit -m 'Add AmazingFeature'`)
4. Push (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📝 License

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 👥 Équipe

- **Votre nom** - Développeur principal
- **Nom coéquipier 1** - Data Analyst
- **Nom coéquipier 2** - Data Scientist

## 📞 Support

Pour toute question :
- Ouvrir une issue sur GitHub
- Contacter l'équipe par email
- Consulter la documentation

---

**Mangetamain Analytics** - Transformons les données culinaires en insights actionables ! 🍽️📊
