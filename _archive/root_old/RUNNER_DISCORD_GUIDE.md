# 🤖 GitHub Self-Hosted Runner + Alerting Discord

**Date de création :** 2025-10-25
**Environnement :** VM dataia (VPN)
**Rôle :** Déploiement automatique + Notifications temps réel

---

## 📋 Vue d'ensemble

Le projet utilise un **GitHub Actions Runner self-hosted** installé sur la VM **dataia** pour gérer le déploiement continu (CD) avec notifications Discord en temps réel.

### 🎯 Avantage Principal : Plus Besoin de VPN !

**Avant le runner :**
- ❌ Connexion VPN manuelle requise
- ❌ SSH vers dataia
- ❌ Commandes git pull manuelles
- ❌ Redémarrage Docker manuel
- ❌ Risque d'erreur humaine

**Avec le runner :**
- ✅ **Simple push vers GitHub → Déploiement automatique**
- ✅ Aucune connexion VPN nécessaire
- ✅ Aucune commande manuelle
- ✅ Pipeline entièrement automatisé
- ✅ Notifications Discord en temps réel

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  GitHub Repository (mangetamain)                            │
│  - Push vers main / Workflow manuel                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ Déclenche workflow
                     ↓
┌─────────────────────────────────────────────────────────────┐
│  GitHub Actions Runner (self-hosted)                        │
│  📍 Localisation: VM dataia (VPN)                           │
│  👤 User: dataia25                                          │
│  🏃 Service: systemd                                        │
└────────────────────┬────────────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
         ↓                       ↓
┌──────────────────┐    ┌───────────────────┐
│  Déploiement     │    │  Notifications    │
│  - Pull code     │    │  Discord Webhook  │
│  - Restart       │    │  - Début deploy   │
│  - Health check  │    │  - Succès/Échec   │
│  - Rollback      │    │  - Health status  │
└──────────────────┘    └───────────────────┘
```

---

## 🏃 GitHub Self-Hosted Runner

### 1. Localisation et Configuration

**Serveur :** VM dataia (accessible via VPN uniquement)
**Chemin d'installation :** `/home/dataia25/actions-runner/`
**User :** `dataia25`
**Service :** `systemd` (démarrage automatique)

### 2. Pourquoi Self-Hosted ?

#### ❌ Limitations des runners GitHub hébergés
- Pas d'accès aux serveurs privés (VPN requis)
- Pas d'accès au système de fichiers local
- Pas de contrôle sur Docker local
- Impossible de redémarrer containers sur le serveur

#### ✅ Avantages du runner self-hosted

**🚀 Autonomie Totale - Plus de VPN !**
- **Déploiement automatique** : Push → Déploiement, sans intervention manuelle
- **Pas de connexion VPN** : Les développeurs n'ont plus besoin de se connecter à dataia
- **Workflow simplifié** : `git push` → Tout se passe automatiquement

**🔧 Accès Technique**
- **Accès fichiers** : Accès direct à `/home/dataia25/mangetamain/`
- **Contrôle Docker** : Peut exécuter `docker-compose restart`
- **Performance** : Réseau local (pas de transfert réseau externe)
- **Sécurité** : Credentials stockés localement, pas d'exposition cloud

### 3. Configuration dans les Workflows

Les workflows CD utilisent `runs-on: self-hosted` :

```yaml
# .github/workflows/cd-preprod.yml
jobs:
  deploy-preprod:
    name: Deploy to Preprod
    runs-on: self-hosted  # ← Exécuté sur VM dataia

    steps:
      - name: Pull latest code
        run: |
          cd /home/dataia25/mangetamain/10_preprod
          git reset --hard origin/main
```

```yaml
# .github/workflows/cd-prod.yml
jobs:
  deploy-prod:
    name: Deploy to Production
    runs-on: self-hosted  # ← Exécuté sur VM dataia
    if: github.event.inputs.confirm == 'DEPLOY'
```

### 4. Vérification du Runner

#### Sur la VM dataia

```bash
# Vérifier le service
systemctl status actions.runner.*

# Voir les logs
journalctl -u actions.runner.* -f

# Redémarrer le runner si nécessaire
sudo systemctl restart actions.runner.*
```

#### Sur GitHub

1. Aller dans **Settings → Actions → Runners**
2. Vérifier que le runner apparaît comme **"Idle"** ou **"Active"**
3. Status vert = fonctionnel

---

## 📢 Alerting Discord

### 1. Configuration Webhook

**Secret GitHub :** `DISCORD_WEBHOOK_URL`
- Stocké dans : Settings → Secrets and variables → Actions
- Format : `https://discord.com/api/webhooks/{id}/{token}`
- Accès : Repository owner uniquement

### 2. Types de Notifications

#### 🚀 Déploiement Preprod (Auto)

```
🚀 **Déploiement Preprod démarré**
📦 Commit: `abc1234`
💬 Message: Fix bug in login
👤 Par: julienlafrance
```

```
✅ **Déploiement Preprod réussi!**
🌐 URL: https://mangetamain.lafrance.io/
📦 Commit: `abc1234`
💬 Fix bug in login
🕐 2025-10-25 14:30:15
```

```
❌ **ÉCHEC Déploiement Preprod**
📦 Commit: `abc1234`
💬 Fix bug in login
⚠️ **Container dans état cassé - intervention manuelle requise**
📋 Vérifier les logs: `docker-compose -f docker-compose-preprod.yml logs`
👤 Commit par: julienlafrance
```

#### 🚨 Déploiement Production (Manuel)

```
🚨 **Déploiement PRODUCTION démarré**
📦 Commit: `def5678`
💬 Message: New feature
👤 Par: julienlafrance
⚠️ Déploiement manuel confirmé
```

```
✅ **Déploiement PRODUCTION réussi!**
🌐 URL: https://backtothefuturekitchen.lafrance.io/
📦 Commit: `def5678`
💬 New feature
🕐 2025-10-25 14:35:42
👤 Déployé par: julienlafrance
```

```
🚨 **ÉCHEC CRITIQUE - Déploiement PRODUCTION**
❌ Health check échoué
📦 Commit tenté: `def5678`
💬 New feature
🔙 Backup disponible: `abc1234`
⚠️ **PRODUCTION POTENTIELLEMENT CASSÉE**
📋 Rollback manuel requis:
```
cd /home/dataia25/mangetamain/20_prod
git reset --hard abc1234
cd ../30_docker
docker-compose -f docker-compose-prod.yml restart
```
👤 Tenté par: julienlafrance
```

#### ⚠️ Déploiement Production Annulé

```
⚠️ **Déploiement PRODUCTION annulé**
Confirmation incorrecte (attendu: DEPLOY)
👤 Par: julienlafrance
```

### 3. Implémentation dans les Workflows

#### Notification de démarrage

```yaml
- name: Notify deployment start
  run: |
    COMMIT_MSG="${{ github.event.head_commit.message }}"
    COMMIT_MSG_FIRST_LINE=$(echo "$COMMIT_MSG" | head -1)
    curl -H "Content-Type: application/json" \
      -d "{\"content\":\"🚀 **Déploiement Preprod démarré**\n📦 Commit: \`${GITHUB_SHA:0:7}\`\n💬 Message: ${COMMIT_MSG_FIRST_LINE}\n👤 Par: ${{ github.actor }}\"}" \
      "${{ secrets.DISCORD_WEBHOOK_URL }}"
```

#### Notification de succès

```yaml
- name: Notify deployment success
  if: success()
  run: |
    curl -H "Content-Type: application/json" \
      -d "{\"content\":\"✅ **Déploiement Preprod réussi!**\n🌐 URL: https://mangetamain.lafrance.io/\n📦 Commit: \`${GITHUB_SHA:0:7}\`\n🕐 $(date +'%Y-%m-%d %H:%M:%S')\"}" \
      "${{ secrets.DISCORD_WEBHOOK_URL }}"
```

#### Notification d'échec

```yaml
- name: Notify deployment failure
  if: failure()
  run: |
    curl -H "Content-Type: application/json" \
      -d "{\"content\":\"❌ **ÉCHEC Déploiement Preprod**\n📦 Commit: \`${GITHUB_SHA:0:7}\`\n⚠️ **Container dans état cassé**\"}" \
      "${{ secrets.DISCORD_WEBHOOK_URL }}"
```

### 4. Avantages Discord vs Email

| Critère | Discord | Email |
|---------|---------|-------|
| **Temps réel** | ✅ Instantané | ⚠️ Délai de livraison |
| **Formatage** | ✅ Markdown + Emojis | ⚠️ Limité |
| **Groupement** | ✅ Canal dédié | ❌ Boîte mail |
| **Accessibilité** | ✅ Mobile + Desktop | ⚠️ Dépend client |
| **Historique** | ✅ Persistant | ⚠️ Limite stockage |
| **Collaboration** | ✅ Commentaires | ❌ Forwarding |
| **Alertes critiques** | ✅ Notifications push | ⚠️ Peut être filtré |

---

## 🔄 Workflow Complet de Déploiement

### Preprod (Automatique) - **Sans VPN !**

**Ancien workflow (manuel) :**
```
1. Developer: Connexion VPN
2. Developer: ssh dataia
3. Developer: cd /home/dataia25/mangetamain/10_preprod
4. Developer: git pull
5. Developer: cd ../30_docker
6. Developer: docker-compose -f docker-compose-preprod.yml restart
7. Developer: Vérifier que ça marche
8. Developer: Déconnexion VPN
```

**Nouveau workflow (automatisé) :**
```
1. Developer fait git push vers main (depuis n'importe où)
         ↓
2. GitHub Actions déclenche workflow CD Preprod
         ↓
3. Runner self-hosted (dataia) exécute AUTOMATIQUEMENT:
   - 📢 Notification Discord: "Déploiement démarré"
   - 🔄 git pull latest code
   - 🐳 docker-compose restart
   - ⏳ Wait 60s for Streamlit
   - 🔍 Health check (10 tentatives)
         ↓
4. Si succès:
   - ✅ Notification Discord: "Déploiement réussi + URL"
   Si échec:
   - ❌ Notification Discord: "ÉCHEC + commande rollback"
```

**Gain :** 8 étapes manuelles → 1 simple `git push` 🚀

---

### Production (Manuel avec confirmation) - **À venir**

**Workflow actuel :**
```
1. Developer déclenche workflow manuellement
         ↓
2. Saisir "DEPLOY" pour confirmer
         ↓
3. Si confirmé:
   - Runner self-hosted (dataia) exécute:
     • 📢 Notification Discord: "Déploiement PROD démarré"
     • 💾 Backup commit ID actuel
     • 🔄 git pull latest code
     • 🐳 docker-compose restart
     • ⏳ Wait 60s for Streamlit
     • 🔍 Health check (10 tentatives)
         ↓
4. Si succès:
   - ✅ Notification Discord: "Déploiement PROD réussi + URL"
   Si échec:
   - 🚨 Notification Discord: "ÉCHEC CRITIQUE + rollback manuel"
   Si annulé:
   - ⚠️ Notification Discord: "Déploiement annulé"
```

**Évolutions prévues (production) :**
- 📋 Copie des fichiers depuis preprod vers prod
- 🐳 Redémarrage Docker
- 🧪 Tests automatiques post-déploiement
- 🔄 Rollback automatique si tests échouent

---

## 🔒 Sécurité

### 1. Runner Self-Hosted

**Risques atténués :**
- ✅ Runner isolé sur VM VPN (pas d'accès public)
- ✅ User dédié `dataia25` (pas de root)
- ✅ Workflows approuvés uniquement (pas de fork PR)
- ✅ Secrets GitHub stockés chiffrés
- ✅ Accès repository limité (pas de write sur main)

**Best Practices appliquées :**
- Runner sur réseau privé uniquement
- Pas d'exécution de code non vérifié
- Logs auditables (systemd + GitHub Actions)
- Mise à jour régulière du runner

### 2. Discord Webhook

**Protections :**
- ✅ Secret stocké dans GitHub Secrets (chiffré)
- ✅ Pas de données sensibles dans notifications (pas de credentials)
- ✅ Webhook régénérable si compromis
- ✅ Messages formatés (pas d'injection possible)

**Limitations volontaires :**
- Pas de commit messages complets (risque de leak info sensible)
- Pas de variables d'environnement
- Pas de contenu fichiers
- Seulement metadata publique (SHA, auteur, URLs)

---

## 📊 Monitoring

### 1. Vérifier Health du Runner

```bash
# SSH vers dataia
ssh dataia

# Status du service
systemctl status actions.runner.*

# Logs en temps réel
journalctl -u actions.runner.* -f

# Vérifier connectivité GitHub
curl -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/USER/REPO/actions/runners
```

### 2. Vérifier Discord Webhook

```bash
# Test manuel du webhook
curl -H "Content-Type: application/json" \
  -d '{"content":"🧪 Test notification depuis CLI"}' \
  "https://discord.com/api/webhooks/YOUR_WEBHOOK_URL"
```

### 3. Logs de Déploiement

**GitHub Actions :**
- Aller dans **Actions** → Workflow exécuté → Logs détaillés

**Sur la VM dataia :**
```bash
# Logs Docker Preprod
docker-compose -f /home/dataia25/mangetamain/30_docker/docker-compose-preprod.yml logs -f

# Logs Docker Prod
docker-compose -f /home/dataia25/mangetamain/30_docker/docker-compose-prod.yml logs -f
```

---

## 🛠️ Maintenance

### 1. Mise à jour du Runner

```bash
ssh dataia
cd /home/dataia25/actions-runner

# Télécharger nouvelle version
./svc.sh stop
# ... update steps from GitHub ...
./svc.sh start
```

### 2. Régénération du Webhook Discord

Si le webhook est compromis :

1. **Créer nouveau webhook** dans Discord Server Settings
2. **Mettre à jour** le secret GitHub `DISCORD_WEBHOOK_URL`
3. **Tester** avec un workflow manuel
4. **Révoquer** l'ancien webhook

### 3. Troubleshooting

#### Runner ne démarre pas

```bash
# Vérifier les erreurs
journalctl -u actions.runner.* -n 50

# Redémarrer
sudo systemctl restart actions.runner.*

# Vérifier connectivité réseau
ping github.com
curl https://api.github.com
```

#### Notifications Discord ne fonctionnent pas

```bash
# Tester webhook manuellement
curl -H "Content-Type: application/json" \
  -d '{"content":"Test"}' \
  "$DISCORD_WEBHOOK_URL"

# Vérifier secret GitHub
# Settings → Secrets → DISCORD_WEBHOOK_URL existe ?
```

#### Health check échoue

```bash
# Vérifier que l'app répond
curl https://mangetamain.lafrance.io/
curl https://backtothefuturekitchen.lafrance.io/

# Vérifier containers
docker ps | grep streamlit

# Vérifier logs
docker-compose logs streamlit-preprod
docker-compose logs streamlit-prod
```

---

## 💡 Bénéfices Concrets

### Pour les Développeurs

| Avant (Manuel) | Après (Runner) |
|----------------|----------------|
| 1. Se connecter au VPN | ✅ Simple `git push` |
| 2. SSH vers dataia | ✅ Pas de connexion serveur |
| 3. Naviguer vers le bon dossier | ✅ Automatique |
| 4. Git pull manuellement | ✅ Automatique |
| 5. Redémarrer Docker | ✅ Automatique |
| 6. Attendre et vérifier | ✅ Health check auto |
| 7. Tester l'URL | ✅ Notification Discord |
| 8. Déconnexion VPN | ✅ Pas de VPN nécessaire |
| **⏱️ Temps : ~5-10 minutes** | **⏱️ Temps : 30 secondes** |
| **❌ Risque d'erreur humaine** | **✅ Process standardisé** |

### Pour l'Équipe

- **Productivité :** Déploiements 10-20x plus rapides
- **Fiabilité :** Process identique à chaque fois
- **Traçabilité :** Logs GitHub Actions + Notifications Discord
- **Accessibilité :** Déploiement depuis n'importe où (mobile, tablet, etc.)
- **Collaboration :** Notifications partagées sur Discord

---

## 📋 Checklist d'Installation (Référence)

Si besoin de réinstaller le runner (une seule fois sur dataia) :

- [ ] Télécharger runner depuis GitHub Settings → Actions → Runners → New self-hosted runner
- [ ] Extraire dans `/home/dataia25/actions-runner`
- [ ] Configurer avec token d'enregistrement
- [ ] Installer comme service systemd : `./svc.sh install`
- [ ] Démarrer : `./svc.sh start`
- [ ] Vérifier : `./svc.sh status`
- [ ] Tester avec workflow manuel
- [ ] Vérifier notifications Discord

**Une fois installé :** Plus jamais besoin de se connecter en VPN pour déployer ! 🎉

---

## 🔗 Références

### Documentation Officielle
- **GitHub Actions Self-Hosted Runners :** https://docs.github.com/en/actions/hosting-your-own-runners
- **Discord Webhooks API :** https://discord.com/developers/docs/resources/webhook

### Fichiers du Projet
- **Workflow CD Preprod :** `.github/workflows/cd-preprod.yml`
- **Workflow CD Prod :** `.github/workflows/cd-prod.yml`
- **Docker Compose Preprod :** `30_docker/docker-compose-preprod.yml`
- **Docker Compose Prod :** `30_docker/docker-compose-prod.yml`

### URLs des Environnements
- **Preprod :** https://mangetamain.lafrance.io/
- **Production :** https://backtothefuturekitchen.lafrance.io/

---

**Document créé le :** 2025-10-25
**Auteur :** Project team
**Version :** 1.0
**Status :** ✅ Complet et documenté
