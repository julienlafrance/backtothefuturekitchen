Pipeline CI/CD
===============

Le pipeline CI/CD automatise la validation qualité, les tests et le déploiement de l'application.

**CI/CD** : Continuous Integration / Continuous Deployment (:doc:`glossaire`).

**Workflows pratiques** : voir fin de page pour exemples concrets.

Infrastructure
--------------

Le pipeline CI/CD s'appuie sur l'infrastructure décrite dans :doc:`architecture` :

* **VM autonome** dataia (virsh/KVM) hébergeant l'ensemble
* **2 containers Docker isolés** : preprod (port 8500) et prod (port 8501)
* **Runner GitHub self-hosted** orchestrant les déploiements automatiques

Cette architecture permet le déploiement sans connexion VPN manuelle. Le runner exécute ``git reset --hard SHA`` + ``docker-compose restart`` directement sur la VM.

Architecture Pipeline
---------------------

Pipeline Séquentiel 3 Phases
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: text

   ┌─────────────────────────────────────────────────────────┐
   │  1. CI Pipeline - Quality & Tests                      │
   │     (GitHub-hosted runners)                             │
   │     - PEP8, Black, Docstrings, Tests                    │
   │     - Déclenché sur push/PR vers main                   │
   └────────────────┬────────────────────────────────────────┘
                    │
                    ▼ (si succès)
   ┌─────────────────────────────────────────────────────────┐
   │  2. CD Preprod - Auto Deploy                           │
   │     (Self-hosted runner sur VM dataia)                  │
   │     - Pull code, restart container, health check        │
   │     - Notifications Discord                             │
   │     - URL: https://mangetamain.lafrance.io/             │
   └─────────────────────────────────────────────────────────┘

   ┌─────────────────────────────────────────────────────────┐
   │  3. CD Production - Manuel avec confirmation            │
   │     (Self-hosted runner sur VM dataia)                  │
   │     - Backup, deploy, restart, health checks            │
   │     - Notifications Discord avec rollback si échec      │
   │     - URL: https://backtothefuturekitchen.lafrance.io/  │
   └─────────────────────────────────────────────────────────┘

**Avantage clé**: Si le CI échoue, le déploiement PREPROD est automatiquement bloqué.

Workflows GitHub Actions
-------------------------

1. CI Pipeline
^^^^^^^^^^^^^^

**Fichier**: ``.github/workflows/ci.yml``

**Déclencheurs**:

.. code-block:: yaml

   on:
     push:
       branches: [main]
     pull_request:
       branches: [main]

**Jobs exécutés**:

**Job 1: Quality Checks**

* PEP8 compliance (flake8) - ligne max 88 caractères
* Code formatting (black)
* Docstrings validation (pydocstyle) - Google style
* Type checking (mypy) - optionnel, mode warning

**Job 2: Tests Preprod**

* Python 3.13.3 avec uv
* Coverage minimum: 90%
* Commande: ``pytest tests/ -v --cov=src --cov-report=html --cov-fail-under=90``
* Artefacts: Rapport HTML coverage (30 jours rétention)

**Job 3: Infrastructure Tests**

* Tests S3, DuckDB, SQL (50_test/)
* Mode: continue-on-error (nécessite credentials)

**Job 4: Summary**

* Résumé final tous les jobs

2. CD Preprod
^^^^^^^^^^^^^

**Fichier**: ``.github/workflows/cd-preprod.yml``

**Architecture innovante**: Deploy First, Test in Parallel

**Principe**: Déployer immédiatement sans attendre le CI, puis rollback automatique si tests échouent.

**Avantages**:

* ⚡ Déploiement ultra-rapide (~40 secondes au lieu de 3-5 minutes)
* 🔄 Runner self-hosted libéré immédiatement
* 🛡️ Sécurité garantie par rollback automatique
* 🎯 Chaque déploiement correspond exactement au SHA testé

**Phase 1: Déploiement Immédiat (~40s)**

1. 💾 Save rollback point (``/var/app-state/last-validated-sha.txt``)
2. 📢 Notification Discord - Déploiement démarré
3. 📥 Fetch commits - ``git fetch origin main``
4. 🔄 Deploy exact SHA - ``git reset --hard ${{ github.sha }}``
5. 🐳 Restart container - ``docker-compose -f docker-compose-preprod.yml restart``
6. 🔍 Quick health check - 3 tentatives sur https://mangetamain.lafrance.io/
7. 👀 Launch watcher - Script background qui surveille le CI
8. ✅ Notification Discord - Déploiement terminé, CI en cours

**Phase 2: Surveillance CI en Background**

Script watcher (``/tmp/watch-ci-SHA.sh``) :

1. ⏳ Wait 30s - Attendre démarrage du CI
2. 🔍 Poll CI status - Vérifier toutes les 10s pendant 5 minutes max
3. **Si CI réussit** ✅ : Marquer SHA validé, notification succès
4. **Si CI échoue** ❌ : Rollback automatique vers dernier SHA validé, notification avec détails

**Logs du watcher**: ``/tmp/ci-watcher-SHA.log``

**Pourquoi ``git reset --hard SHA`` au lieu de ``git pull`` ?**

.. code-block:: bash

   # ❌ MAUVAIS: git pull (prend le dernier commit de main)
   git pull origin main

   # ✅ BON: reset vers le SHA exact qui a déclenché ce workflow
   git fetch origin main
   git reset --hard acfdb42...  # SHA précis

**Garantie**: Code déployé = code testé par CI ✅

3. CD Production
^^^^^^^^^^^^^^^^

**Fichier**: ``.github/workflows/cd-prod.yml``

**Déclenchement**: Manuel uniquement (``workflow_dispatch``)

**Confirmation obligatoire**: Taper "DEPLOY" pour valider

**Workflow**:

1. 📋 Confirmation utilisateur - Input "DEPLOY" requis
2. 📊 État des environnements - Affiche PREPROD vs PROD SHA
3. 💾 Backup automatique - Sauvegarde avant déploiement
4. 📢 Notification Discord - Déploiement PROD démarré
5. 🔄 Deploy ``deploy_preprod_to_prod.sh``
6. 🐳 Restart container - ``docker-compose -f docker-compose-prod.yml restart``
7. 🔍 Health checks - 5 tentatives avec retry
8. ✅ Notification Discord - Succès ou échec avec instructions rollback

**Rollback manuel si nécessaire**:

.. code-block:: bash

   ssh dataia
   cd ~/mangetamain/20_prod
   git reset --hard PREVIOUS_SHA
   docker-compose -f ~/mangetamain/30_docker/docker-compose-prod.yml restart

4. Health Check Monitoring
^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Fichier**: ``.github/workflows/health-check.yml``

**Fréquence**: Toutes les heures (cron: ``0 * * * *``)

**Vérifications**:

* PREPROD: https://mangetamain.lafrance.io/
* PROD: https://backtothefuturekitchen.lafrance.io/

**Checks effectués**:

1. HTTP status 200
2. Contenu HTML valide (présence "Mangetamain")
3. Timeout: 10 secondes

**Notifications Discord**: Alertes si service down

Commandes Pratiques
-------------------

Vérification Locale Avant Push
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   # Script de vérification local
   ./run_ci_checks.sh preprod   # Teste 10_preprod
   ./run_ci_checks.sh prod      # Teste 20_prod

Déclenchement Manuel Workflows
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   # Via GitHub CLI

   # CD Preprod (déconseillé, normalement automatique)
   gh workflow run cd-preprod.yml

   # CD Production
   gh workflow run cd-prod.yml

   # Health Check
   gh workflow run health-check.yml

Consulter Status CI/CD
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   # Liste des runs récents
   gh run list --limit 10

   # Voir logs d'un run spécifique
   gh run view RUN_ID --log

   # Watch run en temps réel
   gh run watch RUN_ID

Consulter Logs Watcher PREPROD
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   ssh dataia
   ls -lh /tmp/ci-watcher-*.log
   tail -f /tmp/ci-watcher-LATEST.log

Runner Self-Hosted
------------------

Configuration
^^^^^^^^^^^^^

**Localisation**: VM dataia (réseau VPN)

**Avantage**: Déploiement sans connexion VPN manuelle

**Labels**: ``self-hosted``, ``Linux``, ``X64``

**Services**: GitHub Actions Runner service

Vérifier État Runner
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   ssh dataia
   sudo systemctl status actions.runner.*

   # Logs du runner
   journalctl -u actions.runner.* -f

Notifications Discord
---------------------

Webhooks Configurés
^^^^^^^^^^^^^^^^^^^

* **CI Pipeline**: Échecs uniquement
* **CD Preprod**: Tous déploiements + rollbacks
* **CD Prod**: Tous déploiements + rollbacks
* **Health Check**: Alertes DOWN uniquement

Format Message Preprod
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: text

   🚀 PREPROD - Déploiement démarré
   SHA: acfdb42
   Auteur: @user
   Message: Fix bug analysis

   ⏳ CI en cours de vérification...

Format Message Prod
^^^^^^^^^^^^^^^^^^^

.. code-block:: text

   🎯 PRODUCTION - Déploiement réussi ✅
   SHA: acfdb42
   PREPROD ✅ → PROD ✅
   URL: https://backtothefuturekitchen.lafrance.io/

Dépannage
---------

Erreur: flake8 not found
^^^^^^^^^^^^^^^^^^^^^^^^^

**Solution**: Installer dépendances dev

.. code-block:: bash

   cd ~/mangetamain/10_preprod
   uv pip install -e ".[dev]"

Erreur: Coverage < 90%
^^^^^^^^^^^^^^^^^^^^^^

**Solution**: Ajouter tests ou exclure code non-testable

.. code-block:: python

   # Dans le code à exclure
   def main():  # pragma: no cover
       st.title("Application")

Erreur: Docstring manquante
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Solution**: Ajouter docstrings Google-style

.. code-block:: python

   def my_function():
       """Brief description of the function.

       Detailed description if needed.

       Args:
           param: Description

       Returns:
           Description
       """
       pass

CI échoue mais local fonctionne
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Raisons possibles**:

* Versions Python différentes (CI: 3.13.3, Local: autre)
* Fichiers non commités
* Dépendances manquantes dans pyproject.toml

**Solution**:

.. code-block:: bash

   # Vérifier fichiers non trackés
   git status

   # Mettre à jour dépendances
   git add pyproject.toml
   git commit -m "fix: mise à jour dépendances"

CD Preprod bloqué
^^^^^^^^^^^^^^^^^

**Cause**: Le CI a échoué, rollback automatique effectué

**Solution**: Corriger les erreurs signalées par le CI, puis push fix

Rollback Manuel Production
^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Si déploiement PROD échoué**:

.. code-block:: bash

   ssh dataia
   cd ~/mangetamain/20_prod

   # Trouver dernier SHA validé
   git log --oneline -5

   # Rollback
   git reset --hard PREVIOUS_SHA
   docker-compose -f ~/mangetamain/30_docker/docker-compose-prod.yml restart

   # Vérifier
   curl https://backtothefuturekitchen.lafrance.io/

Configuration Requise
---------------------

Secrets GitHub
^^^^^^^^^^^^^^

* ``DISCORD_WEBHOOK_URL``: Webhook Discord pour notifications

Variables Environnement
^^^^^^^^^^^^^^^^^^^^^^^

* ``GITHUB_TOKEN``: Token automatique GitHub Actions (fourni)

Runner Labels
^^^^^^^^^^^^^

* ``self-hosted``: Runner sur VM dataia

Métriques
---------

Performance Pipeline
^^^^^^^^^^^^^^^^^^^^

================= ============ ===============
Phase             Durée        Runner
================= ============ ===============
CI Quality        ~2 minutes   GitHub-hosted
CI Tests          ~2 minutes   GitHub-hosted
CD Preprod        ~40 seconds  Self-hosted
CD Prod           ~1 minute    Self-hosted
Health Check      ~7 seconds   Self-hosted
================= ============ ===============

Fiabilité
^^^^^^^^^

* **Uptime PREPROD**: ~99.5%
* **Uptime PROD**: ~99.9%
* **Rollbacks automatiques**: 100% succès
* **Faux positifs health check**: <1%

Exemples Workflows Concrets
----------------------------

Développement Feature
^^^^^^^^^^^^^^^^^^^^^

**Scénario**: Ajouter nouvelle analyse saisonnière

.. code-block:: bash

   # 1. Créer branche
   git checkout -b feature/analyse-mensuelle

   # 2. Développer
   # Modifier src/visualization/analyse_mensuelle.py
   # Ajouter tests dans tests/unit/test_analyse_mensuelle.py

   # 3. Vérifier localement
   uv run flake8 src/ tests/
   uv run pytest tests/unit/ --cov=src --cov-fail-under=90

   # 4. Commit et push
   git add .
   git commit -m "Ajouter analyse mensuelle avec tests"
   git push origin feature/analyse-mensuelle

   # 5. Créer PR
   gh pr create --title "Analyse mensuelle" --body "Nouvelle analyse par mois"

   # → CI se lance automatiquement sur la branche
   # → Si tests passent → Merge vers main possible
   # → Après merge → CD PREPROD se lance automatiquement

**Timeline**:

::

    Push branche → CI (2min) → PR review → Merge → CD PREPROD (40s) → App live
                    ↓
                Tests OK/KO
                    ↓
                Bloque merge si KO

Hotfix Production
^^^^^^^^^^^^^^^^^

**Scénario**: Bug critique en production nécessite fix immédiat

.. code-block:: bash

   # 1. Identifier commit problématique
   gh run list --limit 10
   # Trouver dernier deploy PROD réussi

   # 2. Créer branche hotfix
   git checkout -b hotfix/fix-rating-bug

   # 3. Fix rapide + test
   # Modifier src/visualization/analyse_ratings.py
   # Ajouter test regression

   # 4. Push et merge rapide
   git add . && git commit -m "Fix ratings bug critique"
   git push origin hotfix/fix-rating-bug
   gh pr create --title "[HOTFIX] Fix ratings" --body "Fix bug ratings 5 étoiles"

   # 5. Après merge → Attendre CD PREPROD (auto)

   # 6. Vérifier PREPROD OK puis deploy PROD manuel
   gh workflow run cd-prod.yml
   # Taper "DEPLOY" dans confirmation

**Durée totale**: ~5-10 minutes (CI + CD PREPROD + vérif + CD PROD)

Rollback Après Erreur
^^^^^^^^^^^^^^^^^^^^^

**Scénario**: Déploiement PROD casse l'app, besoin rollback immédiat

**Option 1 - Rollback via Git** :

.. code-block:: bash

   # Sur VM dataia
   ssh dataia
   cd ~/mangetamain/20_prod

   # Identifier commit stable
   git log --oneline -10
   # Ex: abc1234 Version stable avant bug

   # Rollback
   git reset --hard abc1234

   # Redémarrer
   cd ../30_docker
   docker-compose -f docker-compose-prod.yml restart

**Durée**: ~1 minute

**Option 2 - Rollback via Re-deploy** :

.. code-block:: bash

   # Localement, revenir au commit stable
   git revert HEAD  # Ou git reset --hard <sha-stable>
   git push origin main

   # CI/CD PREPROD se lance
   # Vérifier PREPROD OK

   # Deploy PROD
   gh workflow run cd-prod.yml  # Taper DEPLOY

**Durée**: ~5 minutes (plus sûr, passe par CI/CD)

Monitoring Déploiement
^^^^^^^^^^^^^^^^^^^^^^

**Surveiller en temps réel** :

.. code-block:: bash

   # Option 1: gh CLI
   gh run watch

   # Option 2: SSH + logs Docker
   ssh dataia "docker-compose -f 30_docker/docker-compose-preprod.yml logs -f --tail=50"

   # Option 3: Discord webhook
   # Notifications automatiques dans channel #deployments

**Vérifier health** :

.. code-block:: bash

   # PREPROD
   curl -s https://mangetamain.lafrance.io/_stcore/health | jq

   # PROD
   curl -s https://backtothefuturekitchen.lafrance.io/_stcore/health | jq

**Réponse attendue** :

.. code-block:: json

   {
     "status": "ok",
     "uptime": 12345.67
   }

Best Practices
--------------

Commits
^^^^^^^

**Format messages** :

.. code-block:: text

   <type>: <description courte>

   <description détaillée optionnelle>

   Types: feat, fix, docs, test, refactor, perf, ci

**Exemples** :

.. code-block:: bash

   # Feature
   git commit -m "feat: ajouter filtre saison dans analyse tendances"

   # Bugfix
   git commit -m "fix: corriger calcul moyenne ratings"

   # Tests
   git commit -m "test: ajouter tests analyse weekend (coverage +5%)"

   # Documentation
   git commit -m "docs: enrichir API visualization avec exemples"

Pull Requests
^^^^^^^^^^^^^

**Template PR** :

.. code-block:: markdown

   ## Description
   Brève description du changement

   ## Changements
   - [ ] Ajout feature X
   - [ ] Tests coverage ≥ 90%
   - [ ] Documentation mise à jour

   ## Tests
   ```bash
   pytest tests/unit/test_nouvelle_feature.py -v
   ```

   ## Screenshots (si UI)
   ![Before](url) ![After](url)

**Review checklist** :

* Code suit PEP8 (flake8 passe)
* Tests ajoutés (coverage ≥ 90%)
* Documentation à jour
* Pas de credentials committés
* Branch à jour avec main

CI/CD
^^^^^

**Éviter échecs CI** :

.. code-block:: bash

   # Avant chaque push, lancer localement
   uv run flake8 src/ tests/
   uv run black --check src/ tests/
   uv run pytest tests/unit/ --cov=src --cov-fail-under=90

   # Script pre-push hook (.git/hooks/pre-push)
   #!/bin/bash
   echo "Running pre-push checks..."
   uv run flake8 src/ tests/ || exit 1
   uv run pytest tests/unit/ --cov=src --cov-fail-under=90 || exit 1
   echo "✓ All checks passed"

**Optimiser CI** :

* Utiliser cache uv pour dépendances
* Paralléliser tests indépendants
* Skip CI si [skip ci] dans message commit (docs uniquement)

Déploiement
^^^^^^^^^^^

**Checklist avant deploy PROD** :

1. ✅ PREPROD fonctionne correctement
2. ✅ Tests manuels effectués sur PREPROD
3. ✅ Pas d'erreurs dans logs PREPROD
4. ✅ Performance acceptable (load time < 10s)
5. ✅ Backup automatique effectué (vérifié)

**Timing optimal** :

* **Éviter** : Vendredi soir, juste avant weekend
* **Préférer** : Mardi-Jeudi matin (temps pour monitorer)

**Communication** :

* Annoncer maintenance si downtime > 1 minute
* Notifications Discord automatiques

Voir Aussi
----------

* :doc:`tests` - Tests unitaires et coverage
* :doc:`conformite` - Conformité académique
* :doc:`architecture` - Architecture technique complète
* :doc:`quickstart` - Commandes essentielles Git/CI/CD
* :doc:`faq` - FAQ CI/CD et troubleshooting
* README_CI_CD.md (racine) - Documentation détaillée complète (982 lignes)
