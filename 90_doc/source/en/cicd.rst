CI/CD Pipeline
==============

The CI/CD pipeline automates quality validation, testing and application deployment.

**CI/CD**: Continuous Integration / Continuous Deployment (:doc:`glossaire`).

**Practical workflows**: see end of page for concrete examples.

Infrastructure
--------------

The CI/CD pipeline relies on the infrastructure described in :doc:`architecture`:

* **Standalone VM** dataia (virsh/KVM) hosting the entire stack
* **2 isolated Docker containers**: preprod (port 8500) and prod (port 8501)
* **GitHub self-hosted runner** orchestrating automatic deployments

This architecture enables deployment without manual VPN connection. The runner executes ``git reset --hard SHA`` + ``docker-compose restart`` directly on the VM.

Pipeline Architecture
---------------------

Parallel Pipeline with Automatic Rollback
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: text

   Push to main
        │
        ├──────────────────────────────────────┐
        │                                       │
        ▼                                       ▼
   ┌─────────────────────────────────┐  ┌──────────────────────────────────┐
   │  1. CI Pipeline                 │  │  2. CD Preprod                   │
   │  (GitHub-hosted runners)        │  │  (Self-hosted runner)            │
   │                                 │  │                                  │
   │  - PEP8, Black, Docstrings      │  │  ⚡ DEPLOY FIRST (~40s)          │
   │  - Unit tests                   │  │  - Save rollback point           │
   │  - Coverage ≥90%                │  │  - git reset --hard SHA          │
   │  - Infrastructure tests         │  │  - docker-compose restart        │
   │                                 │  │  - Health check                  │
   │  Duration: ~2-3 minutes         │  │  - Launch CI watcher script      │
   └────────────┬────────────────────┘  │                                  │
                │                       │  🔍 WATCH CI IN BACKGROUND       │
                │                       │  - Poll CI status (5 min max)    │
                │                       │                                  │
                ├───────────────────────┤                                  │
                │                       │                                  │
                ▼                       ▼                                  │
           ✅ CI SUCCESS          ❌ CI FAILURE                           │
                │                       │                                  │
                │                       ▼                                  │
                │              🔄 AUTOMATIC ROLLBACK                      │
                │              - git reset --hard last-validated-sha      │
                │              - docker-compose restart                   │
                │              - Discord notification with CI logs        │
                │                                                          │
                ▼                                                          │
           Mark SHA validated                                             │
           Success notification                                           │
   └──────────────────────────────────────────────────────────────────────┘

   ┌─────────────────────────────────────────────────────────┐
   │  3. CD Production - Manual with confirmation            │
   │     (Self-hosted runner on dataia VM)                   │
   │     - Automatic backup before deploy                    │
   │     - git reset --hard validated SHA                    │
   │     - docker-compose restart                            │
   │     - Health checks (3 attempts)                        │
   │     - Discord notifications                             │
   │     - URL: https://backtothefuturekitchen.lafrance.io/  │
   └─────────────────────────────────────────────────────────┘

**Key advantages**:

* ⚡ **Ultra-fast deployment**: 40s instead of 3-5 min (no CI wait)
* 🔒 **Guaranteed security**: Automatic rollback if CI fails
* 🎯 **Traceability**: Each deployment corresponds exactly to tested SHA
* 🔄 **Runner freed**: Self-hosted runner available immediately

GitHub Actions Workflows
-------------------------

1. CI Pipeline
^^^^^^^^^^^^^^

**File**: ``.github/workflows/ci.yml``

**Triggers**:

.. code-block:: yaml

   on:
     push:
       branches: [main]
     pull_request:
       branches: [main]

**Executed jobs**:

**Job 1: Quality Checks**

* PEP8 compliance (flake8) - max 88 characters per line
* Code formatting (black)
* Docstring validation (pydocstyle) - Google style
* Type checking (mypy) - optional, warning mode

**Job 2: Preprod Tests**

* Python 3.13.7 with uv
* Minimum coverage: 90%
* Command: ``pytest tests/ -v --cov=src --cov-report=html --cov-fail-under=90``
* Artifacts: HTML coverage report (30 days retention)

**Job 3: Infrastructure Tests**

* S3, DuckDB, SQL tests (50_test/)
* Mode: continue-on-error (requires credentials)

**Job 4: Summary**

* Final summary of all jobs

2. CD Preprod
^^^^^^^^^^^^^

**File**: ``.github/workflows/cd-preprod.yml``

**Innovative architecture**: Deploy First, Test in Parallel

**Principle**: Deploy immediately without waiting for CI, then automatic rollback if tests fail.

**Advantages**:

* ⚡ Ultra-fast deployment (~40 seconds instead of 3-5 minutes)
* 🔄 Self-hosted runner freed immediately
* 🛡️ Security guaranteed by automatic rollback
* 🎯 Each deployment corresponds exactly to tested SHA

**Phase 1: Immediate Deployment (~40s)**

1. 💾 Save rollback point (``/var/app-state/last-validated-sha.txt``)
2. 📢 Discord notification - Deployment started
3. 📥 Fetch commits - ``git fetch origin main``
4. 🔄 Deploy exact SHA - ``git reset --hard ${{ github.sha }}``
5. 🐳 Restart container - ``docker-compose -f docker-compose-preprod.yml restart``
6. 🔍 Quick health check - 3 attempts on https://mangetamain.lafrance.io/
7. 👀 Launch watcher - Background script monitoring CI
8. ✅ Discord notification - Deployment complete, CI in progress

**Phase 2: Background CI Monitoring**

Watcher script (``/tmp/watch-ci-SHA.sh``):

1. ⏳ Wait 30s - Wait for CI startup
2. 🔍 Poll CI status - Check every 10s for 5 minutes max
3. **If CI succeeds** ✅: Mark SHA validated, success notification
4. **If CI fails** ❌: Automatic rollback to last validated SHA, notification with details

**Watcher logs**: ``/tmp/ci-watcher-SHA.log``

**Why ``git reset --hard SHA`` instead of ``git pull``?**

.. code-block:: bash

   # ❌ WRONG: git pull (takes latest commit from main)
   git pull origin main

   # ✅ CORRECT: reset to exact SHA that triggered this workflow
   git fetch origin main
   git reset --hard acfdb42...  # Precise SHA

**Guarantee**: Deployed code = code tested by CI ✅

3. CD Production
^^^^^^^^^^^^^^^^

**File**: ``.github/workflows/cd-prod.yml``

**Trigger**: Manual only (``workflow_dispatch``)

**Mandatory confirmation**: Type "DEPLOY" to validate

**Workflow**:

1. 📋 User confirmation - "DEPLOY" input required
2. 📊 Environment status - Displays PREPROD vs PROD SHA
3. 💾 Automatic backup - Save before deployment
4. 📢 Discord notification - PROD deployment started
5. 🔄 Deploy ``deploy_preprod_to_prod.sh``
6. 🐳 Restart container - ``docker-compose -f docker-compose-prod.yml restart``
7. 🔍 Health checks - 5 attempts with retry
8. ✅ Discord notification - Success or failure with rollback instructions

**Manual rollback if needed**:

.. code-block:: bash

   ssh dataia
   cd ~/mangetamain/20_prod
   git reset --hard PREVIOUS_SHA
   docker-compose -f ~/mangetamain/30_docker/docker-compose-prod.yml restart

4. Health Check Monitoring
^^^^^^^^^^^^^^^^^^^^^^^^^^^

**File**: ``.github/workflows/health-check.yml``

**Frequency**: Every hour (cron: ``0 * * * *``)

**Verifications**:

* PREPROD: https://mangetamain.lafrance.io/
* PROD: https://backtothefuturekitchen.lafrance.io/

**Performed checks**:

1. HTTP status 200
2. Valid HTML content (presence of "Mangetamain")
3. Timeout: 10 seconds

**Discord notifications**: Alerts if service down

5. Documentation Build
^^^^^^^^^^^^^^^^^^^^^^

**File**: ``.github/workflows/documentation.yml``

**Triggers**:

.. code-block:: yaml

   on:
     push:
       branches: [main]
       paths:
         - '90_doc/source/**'
         - '90_doc/requirements.txt'
         - '.github/workflows/documentation.yml'
     workflow_dispatch:

**Principle**: Workflow completely **isolated from preprod/prod CI/CD**. A doc build failure never impacts application deployments.

**Workflow**:

1. 📦 Setup Python 3.13.7
2. 📥 Install Sphinx dependencies (sphinx, sphinx-rtd-theme, myst-parser)
3. 🔨 Build documentation (``sphinx-build -b html source build/html``)
4. 📄 Add ``.nojekyll`` file (disables Jekyll processing)
5. 🚀 Deploy to GitHub Pages (``gh-pages`` branch)
6. 📬 Discord notification (failures only)

**Documentation URL**: https://julienlafrance.github.io/backtothefuturekitchen/

**Discord notifications**: Failures only (like CI Pipeline)

**Documentation architecture**:

.. code-block:: text

   90_doc/
   ├── source/         # .rst files (tracked in Git)
   │   ├── conf.py     # Sphinx configuration
   │   └── *.rst       # Documentation pages
   ├── build/          # Generated HTML (ignored by Git)
   └── Makefile        # Sphinx commands

**Update workflow**:

.. code-block:: bash

   cd 90_doc/source
   # Modify .rst files
   vim installation.rst

   # Local build to test (optional)
   cd ..
   make html
   firefox build/html/index.html

   # Commit and push
   git add source/
   git commit -m "Doc: update installation"
   git push

   # → GitHub Actions builds automatically
   # → Doc published in 2-3 minutes on GitHub Pages

**Key points**:

* 💾 HTML removed from main repo (38 MB saved)
* ⚡ Automatic build on push to main
* 🌐 Deployment on separate ``gh-pages`` branch
* 🔒 **Isolated workflow**: doc failure ≠ preprod/prod impact
* 📝 Only ``.rst`` files are tracked in Git

**GitHub Pages vs tracked HTML advantages**:

* Correct GitHub statistics (Python instead of HTML)
* Lighter repo (-38 MB)
* Professional and stable URL
* No Git history pollution with generated HTML

Practical Commands
------------------

Local Verification Before Push
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   # Local verification script
   ./70_scripts/run_ci_checks.sh preprod   # Test 10_preprod
   ./70_scripts/run_ci_checks.sh prod      # Test 20_prod

Manual Workflow Trigger
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   # Via GitHub CLI

   # CD Preprod (discouraged, normally automatic)
   gh workflow run cd-preprod.yml

   # CD Production
   gh workflow run cd-prod.yml

   # Health Check
   gh workflow run health-check.yml

Check CI/CD Status
^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   # List recent runs
   gh run list --limit 10

   # View logs of specific run
   gh run view RUN_ID --log

   # Watch run in real-time
   gh run watch RUN_ID

Check PREPROD Watcher Logs
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   ssh dataia
   ls -lh /tmp/ci-watcher-*.log
   tail -f /tmp/ci-watcher-LATEST.log

Self-Hosted Runner
------------------

Configuration
^^^^^^^^^^^^^

**Location**: dataia VM (VPN network)

**Advantage**: Deployment without manual VPN connection

**Labels**: ``self-hosted``, ``Linux``, ``X64``

**Services**: GitHub Actions Runner service

Check Runner Status
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   ssh dataia
   sudo systemctl status actions.runner.*

   # Runner logs
   journalctl -u actions.runner.* -f

Discord Notifications
---------------------

Configured Webhooks
^^^^^^^^^^^^^^^^^^^

* **CI Pipeline**: Failures only
* **CD Preprod**: All deployments + rollbacks
* **CD Prod**: All deployments + rollbacks
* **Health Check**: DOWN alerts only
* **Documentation**: Failures only

Preprod Message Format
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: text

   🚀 PREPROD - Deployment started
   SHA: acfdb42
   Author: @user
   Message: Fix bug analysis

   ⏳ CI verification in progress...

Prod Message Format
^^^^^^^^^^^^^^^^^^^

.. code-block:: text

   🎯 PRODUCTION - Deployment successful ✅
   SHA: acfdb42
   PREPROD ✅ → PROD ✅
   URL: https://backtothefuturekitchen.lafrance.io/

Troubleshooting
---------------

Error: flake8 not found
^^^^^^^^^^^^^^^^^^^^^^^

**Solution**: Install dev dependencies

.. code-block:: bash

   cd ~/mangetamain/10_preprod
   uv pip install -e ".[dev]"

Error: Coverage < 90%
^^^^^^^^^^^^^^^^^^^^^

**Solution**: Add tests or exclude non-testable code

.. code-block:: python

   # In code to exclude
   def main():  # pragma: no cover
       st.title("Application")

Error: Missing docstring
^^^^^^^^^^^^^^^^^^^^^^^^^

**Solution**: Add Google-style docstrings

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

CI fails but local works
^^^^^^^^^^^^^^^^^^^^^^^^^

**Possible reasons**:

* Different Python versions (CI: 3.13.7, Local: other)
* Uncommitted files
* Missing dependencies in pyproject.toml

**Solution**:

.. code-block:: bash

   # Check untracked files
   git status

   # Update dependencies
   git add pyproject.toml
   git commit -m "fix: update dependencies"

CD Preprod Blocked
^^^^^^^^^^^^^^^^^^

**Cause**: CI failed, automatic rollback performed

**Solution**: Fix errors reported by CI, then push fix

Manual Production Rollback
^^^^^^^^^^^^^^^^^^^^^^^^^^^

**If PROD deployment failed**:

.. code-block:: bash

   ssh dataia
   cd ~/mangetamain/20_prod

   # Find last validated SHA
   git log --oneline -5

   # Rollback
   git reset --hard PREVIOUS_SHA
   docker-compose -f ~/mangetamain/30_docker/docker-compose-prod.yml restart

   # Verify
   curl https://backtothefuturekitchen.lafrance.io/

Required Configuration
----------------------

GitHub Secrets
^^^^^^^^^^^^^^

* ``DISCORD_WEBHOOK_URL``: Discord webhook for notifications

Environment Variables
^^^^^^^^^^^^^^^^^^^^^

* ``GITHUB_TOKEN``: Automatic GitHub Actions token (provided)

Runner Labels
^^^^^^^^^^^^^

* ``self-hosted``: Runner on dataia VM

Metrics
-------

Pipeline Performance
^^^^^^^^^^^^^^^^^^^^

================= ============ ===============
Phase             Duration     Runner
================= ============ ===============
CI Quality        ~2 minutes   GitHub-hosted
CI Tests          ~2 minutes   GitHub-hosted
CD Preprod        ~40 seconds  Self-hosted
CD Prod           ~1 minute    Self-hosted
Health Check      ~7 seconds   Self-hosted
================= ============ ===============

Reliability
^^^^^^^^^^^

* **PREPROD Uptime**: ~99.5%
* **PROD Uptime**: ~99.9%
* **Automatic rollbacks**: 100% success
* **False positive health checks**: <1%

Concrete Workflow Examples
---------------------------

Feature Development
^^^^^^^^^^^^^^^^^^^

**Scenario**: Add new seasonal analysis

.. code-block:: bash

   # 1. Create branch
   git checkout -b feature/analyse-mensuelle

   # 2. Develop
   # Modify src/visualization/analyse_mensuelle.py
   # Add tests in tests/unit/test_analyse_mensuelle.py

   # 3. Check locally
   uv run flake8 src/ tests/
   uv run pytest tests/unit/ --cov=src --cov-fail-under=90

   # 4. Commit and push
   git add .
   git commit -m "Add monthly analysis with tests"
   git push origin feature/analyse-mensuelle

   # 5. Create PR
   gh pr create --title "Monthly analysis" --body "New analysis by month"

   # → CI runs automatically on branch
   # → If tests pass → Merge to main possible
   # → After merge → CD PREPROD runs automatically

**Timeline**:

::

    Push branch → CI (2min) → PR review → Merge → CD PREPROD (40s) → App live
                    ↓
                Tests OK/KO
                    ↓
                Blocks merge if KO

Production Hotfix
^^^^^^^^^^^^^^^^^

**Scenario**: Critical bug in production requires immediate fix

.. code-block:: bash

   # 1. Identify problematic commit
   gh run list --limit 10
   # Find last successful PROD deploy

   # 2. Create hotfix branch
   git checkout -b hotfix/fix-rating-bug

   # 3. Quick fix + test
   # Modify src/visualization/analyse_ratings.py
   # Add regression test

   # 4. Push and quick merge
   git add . && git commit -m "Fix critical ratings bug"
   git push origin hotfix/fix-rating-bug
   gh pr create --title "[HOTFIX] Fix ratings" --body "Fix 5-star ratings bug"

   # 5. After merge → Wait for CD PREPROD (auto)

   # 6. Verify PREPROD OK then manual PROD deploy
   gh workflow run cd-prod.yml
   # Type "DEPLOY" in confirmation

**Total duration**: ~5-10 minutes (CI + CD PREPROD + check + CD PROD)

Rollback After Error
^^^^^^^^^^^^^^^^^^^^

**Scenario**: PROD deployment breaks app, need immediate rollback

**Option 1 - Rollback via Git**:

.. code-block:: bash

   # On dataia VM
   ssh dataia
   cd ~/mangetamain/20_prod

   # Identify stable commit
   git log --oneline -10
   # Ex: abc1234 Stable version before bug

   # Rollback
   git reset --hard abc1234

   # Restart
   cd ../30_docker
   docker-compose -f docker-compose-prod.yml restart

**Duration**: ~1 minute

**Option 2 - Rollback via Re-deploy**:

.. code-block:: bash

   # Locally, return to stable commit
   git revert HEAD  # Or git reset --hard <stable-sha>
   git push origin main

   # CI/CD PREPROD runs
   # Verify PREPROD OK

   # Deploy PROD
   gh workflow run cd-prod.yml  # Type DEPLOY

**Duration**: ~5 minutes (safer, goes through CI/CD)

Deployment Monitoring
^^^^^^^^^^^^^^^^^^^^^

**Monitor in real-time**:

.. code-block:: bash

   # Option 1: gh CLI
   gh run watch

   # Option 2: SSH + Docker logs
   ssh dataia "docker-compose -f 30_docker/docker-compose-preprod.yml logs -f --tail=50"

   # Option 3: Discord webhook
   # Automatic notifications in #deployments channel

**Check health**:

.. code-block:: bash

   # PREPROD
   curl -s https://mangetamain.lafrance.io/_stcore/health | jq

   # PROD
   curl -s https://backtothefuturekitchen.lafrance.io/_stcore/health | jq

**Expected response**:

.. code-block:: json

   {
     "status": "ok",
     "uptime": 12345.67
   }

Best Practices
--------------

Commits
^^^^^^^

**Message format**:

.. code-block:: text

   <type>: <short description>

   <optional detailed description>

   Types: feat, fix, docs, test, refactor, perf, ci

**Examples**:

.. code-block:: bash

   # Feature
   git commit -m "feat: add season filter in trends analysis"

   # Bugfix
   git commit -m "fix: correct ratings average calculation"

   # Tests
   git commit -m "test: add weekend analysis tests (coverage +5%)"

   # Documentation
   git commit -m "docs: enrich visualization API with examples"

Pull Requests
^^^^^^^^^^^^^

**PR Template**:

.. code-block:: markdown

   ## Description
   Brief description of the change

   ## Changes
   - [ ] Add feature X
   - [ ] Tests coverage ≥ 90%
   - [ ] Documentation updated

   ## Tests
   ```bash
   pytest tests/unit/test_new_feature.py -v
   ```

   ## Screenshots (if UI)
   ![Before](url) ![After](url)

**Review checklist**:

* Code follows PEP8 (flake8 passes)
* Tests added (coverage ≥ 90%)
* Documentation updated
* No committed credentials
* Branch up to date with main

CI/CD
^^^^^

**Avoid CI failures**:

.. code-block:: bash

   # Before each push, run locally
   uv run flake8 src/ tests/
   uv run black --check src/ tests/
   uv run pytest tests/unit/ --cov=src --cov-fail-under=90

   # Pre-push hook script (.git/hooks/pre-push)
   #!/bin/bash
   echo "Running pre-push checks..."
   uv run flake8 src/ tests/ || exit 1
   uv run pytest tests/unit/ --cov=src --cov-fail-under=90 || exit 1
   echo "✓ All checks passed"

**Optimize CI**:

* Use uv cache for dependencies
* Parallelize independent tests
* Skip CI if [skip ci] in commit message (docs only)

Deployment
^^^^^^^^^^

**Checklist before PROD deploy**:

1. ✅ PREPROD works correctly
2. ✅ Manual tests performed on PREPROD
3. ✅ No errors in PREPROD logs
4. ✅ Acceptable performance (load time < 10s)
5. ✅ Automatic backup performed (verified)

**Optimal timing**:

* **Avoid**: Friday evening, just before weekend
* **Prefer**: Tuesday-Thursday morning (time to monitor)

**Communication**:

* Announce maintenance if downtime > 1 minute
* Automatic Discord notifications

See Also
--------

* :doc:`tests` - Unit tests and coverage
* :doc:`conformite` - Academic compliance
* :doc:`architecture` - Complete technical architecture
* :doc:`quickstart` - Essential Git/CI/CD commands
* :doc:`faq` - CI/CD FAQ and troubleshooting
* README_CI_CD.md (root) - Complete detailed documentation (982 lines)
