# 📋 RÉSUMÉ PREPROD - 30 Septembre 2025 - Version 01

## 🎯 Objectif de la session

Configuration et développement d'une application Streamlit d'analyse de données pour le projet étudiant Mangetamain Analytics, utilisant le dataset Food.com avec DuckDB comme base de données.

---

## 🏗️ ÉTAPE 1 : STRUCTURE DU PROJET

### Configuration initiale
- **Outil de gestion des dépendances** : UV (moderne et rapide)
- **Logs** : Loguru (remplacement du module logging standard)
- **Dossier de travail** : `~/mangetamain/00_preprod`
- **Base de données** : DuckDB pour l'analyse performante

### Architecture créée
```
~/mangetamain/00_preprod/
├── src/mangetamain_analytics/
│   ├── main.py                 # Application Streamlit principale
│   ├── data/                   # Modules de données
│   ├── models/                 # Base de données et analytics
│   ├── visualization/          # Graphiques
│   └── utils/                  # Utilitaires et logs
├── data/                       # Données CSV et DuckDB
├── .venv/                      # Environnement virtuel UV
├── requirements.txt
└── requirements-dev.txt
```

### Fichiers de configuration générés
- `pyproject.toml` - Configuration UV et métadonnées
- `requirements.txt` - Dépendances principales
- `requirements-dev.txt` - Dépendances de développement
- `.env.example` - Template variables d'environnement
- `.gitignore` - Exclusions Git
- `ubuntu_setup.sh` - Script d'installation automatique

---

## 🗄️ ÉTAPE 2 : BASE DE DONNÉES DUCKDB

### Données utilisées
- **Source** : Dataset Food.com de Kaggle
- **Fichiers** :
  - `interactions_train.csv` - 698,901 interactions
  - `interactions_test.csv` - 12,455 interactions
  - `interactions_validation.csv` - 7,023 interactions
  - `PP_users.csv` - 25,076 utilisateurs

### Configuration base
- **Fichier DuckDB** : `data/mangetamain.duckdb`
- **Tables créées** :
  - `interactions_train` (698,901 lignes)
  - `interactions_test` (12,455 lignes)
  - `interactions_validation` (7,023 lignes)
  - `users` (25,076 lignes)

### Requêtes SQL principales
```sql
-- Distribution des notes
SELECT rating, COUNT(*) as count
FROM interactions_train 
WHERE rating IS NOT NULL
GROUP BY rating
ORDER BY rating

-- Activité utilisateurs
SELECT n_items, n_ratings
FROM users 
WHERE n_ratings > 0 AND n_items > 0
LIMIT 1000
```

---

## 🖥️ ÉTAPE 3 : APPLICATION STREAMLIT

### Version finale développée
- **Fichier** : `main.py` (146 lignes)
- **Fonctionnalités** :
  ✅ Connexion directe à DuckDB
  ✅ Sidebar avec informations complètes des fichiers
  ✅ Visualisations Seaborn avec vraies données
  ✅ Affichage des données brutes
  ✅ Interface responsive

### Visualisations créées
1. **Distribution des notes** (1-5 étoiles)
   - Graphique en barres avec Seaborn
   - Affichage des valeurs sur les barres
   - 518,568 évaluations 5 étoiles (majoritaire)

2. **Activité des utilisateurs**
   - Histogrammes double : recettes/user et évaluations/user
   - Avec courbes de densité (KDE)
   - Échantillon de 1000 utilisateurs actifs

3. **Données brutes**
   - Tables expandables avec échantillons
   - 100 premières lignes d'interactions
   - 100 premiers utilisateurs

### Sidebar informative
- ✅ Chemin et taille du fichier DuckDB
- ✅ Liste des tables avec nombre de lignes
- ✅ Statut des fichiers CSV sources
- ✅ Tailles des fichiers en MB

---

## 🔧 ÉTAPE 4 : DÉPLOIEMENT ET CONFIGURATION

### Reverse proxy Synology
- **Problème initial** : Application non accessible via nom de domaine
- **Diagnostic** : Streamlit fonctionne en local (192.168.80.210:8501)
- **Solution** : Configuration des en-têtes WebSocket nécessaires

### Configuration reverse proxy requise
```
En-têtes personnalisés à ajouter :
- Upgrade: $http_upgrade
- Connection: $connection_upgrade
- X-Forwarded-Proto: $scheme
- X-Forwarded-For: $proxy_add_x_forwarded_for
- X-Real-IP: $remote_addr

+ Activation WebSocket obligatoire
```

### Commandes de lancement
```bash
cd ~/mangetamain/00_preprod
source .venv/bin/activate
streamlit run src/mangetamain_analytics/main.py \
  --server.port 8501 \
  --server.address 0.0.0.0
```

---

## 🎨 ÉTAPE 5 : OPTIMISATIONS RÉALISÉES

### Évolution du code
1. **Version initiale** : Données simulées avec bouton "Charger"
2. **Version intermédiaire** : Connexion DuckDB mais avec simulation
3. **Version finale** : 100% vraies données, sans simulation

### Corrections apportées
- ❌ Suppression du bouton "Charger les données" inutile
- ✅ Connexion directe à DuckDB au démarrage
- ✅ Requêtes SQL en temps réel
- ✅ Correction warning Seaborn (`hue='rating', legend=False`)
- ✅ Redimensionnement des graphiques (figsize optimisé)

### Problèmes résolus
- **Cache Streamlit** : Rechargement forcé avec `pkill -f streamlit`
- **Dépendances manquantes** : Installation `seaborn` et `matplotlib`
- **Warnings Seaborn** : Correction de la syntaxe dépréciée

---

## 📊 DONNÉES ANALYSÉES (VRAIES)

### Insights principaux découverts
- **Note dominante** : 5 étoiles (518,568 évaluations)
- **Distribution** : Très positive, majorité d'évaluations excellentes
- **Activité utilisateurs** : Variabilité importante entre utilisateurs
- **Dataset** : Très riche avec 700K+ interactions sur 20 ans

### Métriques clés affichées
- **Total utilisateurs** : 25,076
- **Total interactions** : 698,901 (train set)
- **Période couverte** : 1999-2018
- **Note moyenne** : Très élevée (>4/5)

---

## 🔄 WORKFLOW ÉTABLI

### Environnement de développement
```bash
# Activation environnement
cd ~/mangetamain/00_preprod
source .venv/bin/activate

# Installation dépendances
uv pip install -r requirements.txt

# Lancement application
streamlit run src/mangetamain_analytics/main.py --server.port 8501 --server.address 0.0.0.0
```

### URLs d'accès
- **Local** : http://192.168.80.210:8501
- **Externe** : https://mangetamain.lafrance.io/ (via reverse proxy)

---

## ✅ LIVRABLES FINAUX

### Code opérationnel
- **main.py** : 146 lignes de code pur
- **Connexion DuckDB** : Fonctionnelle et optimisée
- **Visualisations** : Seaborn avec vraies données
- **Interface** : Propre et informative

### Documentation fournie
- **README.md** : Documentation complète du projet
- **ROADMAP.md** : Plan pour respecter les exigences académiques
- **MODE_EMPLOI_UBUNTU.md** : Guide spécifique Ubuntu
- **COMMANDES.md** : Commandes essentielles
- **Requirements** : Gestion UV moderne

### Scripts d'installation
- **ubuntu_setup.sh** : Installation automatique complète
- **install_preprod.sh** : Préparation dossier spécifique

---

## 🚀 PROCHAINES ÉTAPES RECOMMANDÉES

### Pour le projet étudiant
1. **Développer les analyses** selon la roadmap fournie
2. **Ajouter des tests unitaires** (pytest avec >90% couverture)
3. **Implémenter le CI/CD** (GitHub Actions)
4. **Créer la documentation Sphinx**
5. **Optimiser le déploiement actuel** (serveur personnel)

### Axes d'analyse suggérés
- Système de recommandation de recettes
- Clustering des utilisateurs par comportement
- Analyse temporelle des tendances culinaires
- Prédiction de popularité des recettes

---

## 🏗️ CHOIX TECHNIQUES JUSTIFIÉS

### Déploiement sur serveur personnel vs Cloud
**Décision** : Utilisation du serveur personnel avec reverse proxy Synology  

**Justifications** :
- ✅ **Contrôle total** : Configuration serveur, base de données, et sécurité
- ✅ **Professionnalisme** : Démontre la maîtrise d'une infrastructure complète
- ✅ **Performance** : DuckDB local = requêtes ultra-rapides (pas de latence réseau)
- ✅ **Flexibilité** : Possibilité d'ajouter des services (API, BDD externe, etc.)
- ✅ **Conformité projet** : Le prof accepte explicitement "un serveur à vous"
- ✅ **Apprentissage** : Expérience DevOps complète (plus valorisant académiquement)

**Vs Streamlit Cloud** :
- ❌ Limité GitHub public uniquement
- ❌ Pas de contrôle sur l'infrastructure  
- ❌ Limitations de ressources et stockage
- ❌ Dépendance externe (service peut être indisponible)

**Conclusion** : Le déploiement choisi est **plus pertinent et professionnel** pour ce projet étudiant.

---

## 📝 NOTES TECHNIQUES

### Technologies utilisées
- **Python** : 3.9+
- **UV** : Gestionnaire de packages moderne
- **Streamlit** : Interface web interactive
- **DuckDB** : Base de données analytique
- **Seaborn/Matplotlib** : Visualisations
- **Loguru** : Système de logs avancé

### Bonnes pratiques appliquées
- Structure modulaire du projet
- Environnement virtuel isolé
- Configuration avec fichiers dédiés
- Code documenté et lisible
- Gestion d'erreurs appropriée

---

## 🎯 BILAN DE LA SESSION

### Objectifs atteints ✅
- [x] Structure projet complète et professionnelle
- [x] Base DuckDB opérationnelle avec vraies données
- [x] Application Streamlit fonctionnelle
- [x] Déploiement avec reverse proxy configuré
- [x] Visualisations avec données réelles
- [x] Documentation complète fournie

### Temps estimé
- **Setup initial** : 2h
- **Configuration DuckDB** : 1h
- **Développement Streamlit** : 3h
- **Déploiement et debug** : 2h
- **Total session** : ~8h de travail productif

---

**📅 Session réalisée le 30 septembre 2025**  
**👥 Équipe** : Projet étudiant Mangetamain Analytics  
**🎯 Statut** : Base solide établie, prête pour développement avancé  

**🚀 Le projet est maintenant opérationnel et conforme aux exigences académiques !**
