# 🔧 Installation S3 - Garage avec Bypass DNAT

## 🎯 Objectif

Configurer l'accès S3 Garage haute performance (534-917 MB/s) en bypassant le reverse proxy.

---

## ✅ Installation (une seule fois)

### 1. Configuration DNS locale

```bash
echo "192.168.80.202  s3fast.lafrance.io" | sudo tee -a /etc/hosts
```

### 2. Installation iptables-persistent

```bash
sudo apt update
sudo apt install iptables-persistent -y
```

### 3. Règle iptables DNAT

```bash
sudo iptables -t nat -A OUTPUT -p tcp -d 192.168.80.202 --dport 80 -j DNAT --to-destination 192.168.80.202:3910
```

### 4. Sauvegarde permanente

```bash
sudo netfilter-persistent save
```

### 5. Vérification

```bash
# DNS
getent hosts s3fast.lafrance.io
# Doit afficher: 192.168.80.202  s3fast.lafrance.io

# iptables
sudo iptables -t nat -L OUTPUT -n -v | grep 3910
# Doit afficher la règle DNAT
```

---

## 📁 Configuration des credentials

Les credentials sont dans `96_keys/` (ignoré par git).

### Structure

```
96_keys/
├── credentials          # Profil s3fast
├── aws_config          # Config AWS
└── garage_s3.duckdb    # Base DuckDB avec secret S3
```

### Fichier `credentials`

```ini
[s3fast]
aws_access_key_id = GK4feb...
aws_secret_access_key = 50e63b...
endpoint_url = http://s3fast.lafrance.io
region = garage-fast
bucket = mangetamain
```

### Fichier `aws_config`

```ini
[profile s3fast]
region = garage-fast
s3 =
    endpoint_url = http://s3fast.lafrance.io
```

### Base DuckDB `garage_s3.duckdb`

Créer une fois :

```bash
cd ~/mangetamain/96_keys
duckdb garage_s3.duckdb
```

Dans DuckDB :

```sql
INSTALL httpfs;
LOAD httpfs;

CREATE SECRET s3fast (
    TYPE s3,
    KEY_ID 'votre_access_key_id',
    SECRET 'votre_secret_access_key',
    ENDPOINT 's3fast.lafrance.io',
    REGION 'garage-fast',
    URL_STYLE 'path',
    USE_SSL false
);
.quit
```

---

## 🐳 Configuration Docker

Les `docker-compose.yml` sont déjà configurés avec :

```yaml
services:
  mon-service:
    extra_hosts:
      - "s3fast.lafrance.io:192.168.80.202"
    cap_add:
      - NET_ADMIN
    command: bash -c "
      apt-get update && 
      apt-get install -y iptables && 
      iptables -t nat -A OUTPUT -p tcp -d 192.168.80.202 --dport 80 -j DNAT --to-destination 192.168.80.202:3910 &&
      # ... reste du démarrage
      "
```

Aucune modification nécessaire dans le code !

---

## 🔒 Sécurité

```bash
# Vérifier que 96_keys/ est dans .gitignore
grep "96_keys" ~/mangetamain/.gitignore
```

---

## 📊 Performances attendues

- **Hôte** : ~534 MB/s
- **Docker** : ~917 MB/s
- **vs HTTPS** : +381% à +726% plus rapide

---

## 🔄 Désinstallation

```bash
# Supprimer règle iptables
sudo iptables -t nat -D OUTPUT -p tcp -d 192.168.80.202 --dport 80 -j DNAT --to-destination 192.168.80.202:3910
sudo netfilter-persistent save

# Supprimer DNS local
sudo sed -i '/s3fast.lafrance.io/d' /etc/hosts
```

---

**Dernière mise à jour** : 2025-10-09
