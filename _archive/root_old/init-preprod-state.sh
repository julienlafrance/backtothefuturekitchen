#!/bin/bash
# Script d'initialisation pour le workflow CD-preprod avec rollback auto
# À exécuter UNE FOIS sur le serveur self-hosted (dataia)

set -e

echo "🔧 Initialisation des prérequis pour CD-preprod avec rollback auto..."

# 1. Créer le dossier d'état
echo "📁 Création /var/app-state..."
sudo mkdir -p /var/app-state
sudo chown dataia25:dataia25 /var/app-state
sudo chmod 755 /var/app-state

# 2. Initialiser le fichier STATE avec le SHA actuel de preprod
echo "📝 Initialisation du fichier state avec le SHA actuel..."
cd /home/dataia25/mangetamain/10_preprod
CURRENT_SHA=$(git rev-parse HEAD)
echo "$CURRENT_SHA" | sudo tee /var/app-state/last-validated-sha.txt
sudo chown dataia25:dataia25 /var/app-state/last-validated-sha.txt
echo "✅ Rollback point initialisé: $CURRENT_SHA"

# 3. Créer le fichier de log
echo "📋 Création du fichier de log..."
sudo touch /var/log/preprod-deployments.log
sudo chown dataia25:dataia25 /var/log/preprod-deployments.log
sudo chmod 644 /var/log/preprod-deployments.log
echo "[$(date)] INIT: Rollback point = $CURRENT_SHA" | sudo tee -a /var/log/preprod-deployments.log

# 4. Vérifier les permissions
echo ""
echo "✅ Vérification des permissions:"
ls -la /var/app-state/
ls -la /var/log/preprod-deployments.log

echo ""
echo "✅ Initialisation terminée!"
echo "Vous pouvez maintenant commiter et pusher le nouveau workflow."
