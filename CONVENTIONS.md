# Conventions du Projet

## Commits

### Messages de commit

- **Ne PAS mentionner d'outils d'assistance** (Claude, ChatGPT, etc.) dans les messages de commit
- **Ne PAS ajouter de signature** type "Generated with [Tool]" ou "Co-Authored-By: [AI]"
- Format libre ou avec préfixe optionnel: `fix:`, `feat:`, `test:`, etc.
- Rester concis et factuel
- Décrire ce qui a été fait, pas comment

### Exemples conformes

```
fix: Résoudre erreurs flake8 CI/CD et nettoyer code obsolète DuckDB
feat: Workflow PROD avec backup versionné
test: Vérification pipeline CI/CD séquentiel
Harmoniser palette couleurs saisonnières avec analyse_seasonality
```

### Exemples NON conformes

```
❌ fix: Corriger bug

🤖 Generated with [Claude Code](https://claude.com/claude-code)
Co-Authored-By: Claude <noreply@anthropic.com>

❌ feat: Ajouter feature (contient signature AI)
```

## Code

### Style

- Utiliser **Black** pour le formatage (`black src/ tests/`)
- Respecter **PEP 8** (vérifier avec `flake8`)
- Coverage minimum: 90%+

### Structure

- PREPROD (`10_preprod/`) = source de vérité
- PROD (`20_prod/`) = artifact généré par déploiement (non tracké dans git)
- Toutes les données chargées depuis S3 Parquet (pas de fichiers locaux)

### Tests

- Tests unitaires obligatoires pour nouveau code
- Lancer avant commit: `pytest tests/`
- Coverage: `pytest --cov=src/mangetamain_analytics`

## Git

### Branches

- `main` = branche principale
- Push sur `main` déclenche automatiquement CI puis CD-Preprod

### Fichiers ignorés

- `**/data/` = TOUT le répertoire data/ et son contenu
- `.venv/` = environnements virtuels
- `20_prod/` = artifact PROD complet
- `*.duckdb`, `*.csv`, `*.pkl` = fichiers de données

## CI/CD

### Pipeline

1. **CI Pipeline - Quality & Tests** (automatique sur push)
   - Checks qualité code (flake8, black)
   - Tests unitaires + coverage

2. **CD - Preprod Deployment** (automatique après CI réussi)
   - Déploie sur https://mangetamain.lafrance.io/
   - Attend que CI passe avant de déployer

3. **CD - Production Deployment** (manuel uniquement)
   - Déclenché via GitHub Actions avec confirmation "DEPLOY"

### Règles

- Ne jamais pousser si les tests échouent
- Ne jamais skip les hooks (pas de `--no-verify`)
- Vérifier flake8 avant commit: `flake8 src/ tests/`

## Documentation

- Documenter les changements majeurs dans `SESSION_*.md`
- Garder les README à jour
- Commenter le code complexe (pas le code évident)

---

**Note**: Ce fichier sera lu automatiquement par les outils d'assistance pour respecter les conventions du projet.
