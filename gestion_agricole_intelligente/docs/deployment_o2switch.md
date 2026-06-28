# Déploiement sur o2switch

Ce guide explique comment déployer l'application Django sur o2switch pour le domaine `https://gagri.dt-verse.com`.

## 1. Pré-requis

- Compte o2switch avec accès à la zone Python App.
- Base de données MySQL créée dans l'espace o2switch.
- Projet Django prêt dans le dossier `gestion_agricole_intelligente`.
- `requirements.txt` présent à la racine de `gestion_agricole_intelligente`.

## 2. Fichiers clés

- `manage.py`
- `gestion_agricole_intelligente/settings.py`
- `passenger_wsgi.py`
- `requirements.txt`

## 3. Préparer le projet localement

1. Aller dans le dossier applicatif :
   ```bash
   cd gestion_agricole_intelligente
   ```

2. Installer les dépendances :
   ```bash
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```

3. Vérifier la configuration Django :
   ```bash
   python manage.py check
   ```

4. Si nécessaire, préparer les migrations locales :
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. Créer le paquet de déploiement depuis le dossier `gestion_agricole_intelligente` :
   ```bash
   cd gestion_agricole_intelligente
   zip -r gagri-deploy.zip . -x ".git/*" "*.pyc" "__pycache__/*" "venv/*" ".venv/*"
   ```

## 4. Déploiement sur o2switch

### 4.1 Importer les fichiers du projet

Dans l'interface o2switch, créez ou mettez à jour l'application Python.

- `Root file` : le répertoire où se trouve `manage.py` et `passenger_wsgi.py`.
- `Root URL` : `https://gagri.dt-verse.com`.

### 4.2 Variables d'environnement

Définissez les variables suivantes dans l'interface o2switch :

- `DJANGO_SETTINGS_MODULE=gestion_agricole_intelligente.settings`
- `SECRET_KEY=<votre_secret_key>`
- `DEBUG=False`
- `ALLOWED_HOSTS=gagri.dt-verse.com`
- `DB_ENGINE=django.db.backends.mysql`
- `DB_NAME=<nom_base>`
- `DB_USER=<utilisateur_mysql>`
- `DB_PASSWORD=<mot_de_passe_mysql>`
- `DB_HOST=localhost` ou l'hôte fourni par o2switch
- `DB_PORT=3306`

> Sur un hébergement mutualisé, installez `PyMySQL` et retirez `mysqlclient` de `requirements.txt`.
> Ajoutez aussi dans `gestion_agricole_intelligente/__init__.py` :
>
> ```python
> import pymysql
> pymysql.install_as_MySQLdb()
> ```

> Ne déployez pas votre `.env` sur o2switch. Utilisez le gestionnaire de variables d'environnement de l'hébergeur.

### 4.3 Point d'entrée WSGI

Pour o2switch, utilisez :

- `passenger_wsgi.py`

Ce fichier référence `gestion_agricole_intelligente.settings` et permet à Passenger de démarrer l'application.

### 4.4 Installer les dépendances

Dans l'environnement Python o2switch :

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4.5 Appliquer les migrations

```bash
python manage.py migrate
```

### 4.6 Collecter les fichiers statiques

```bash
python manage.py collectstatic --noinput
```

### 4.7 Créer un administrateur

```bash
python manage.py createsuperuser
```

## 5. Spécificités o2switch

- Le `root file` correspond au chemin du projet sur le serveur.
- Le `root URL` est l'URL publique du site.
- o2switch utilise Passenger pour exécuter l'application Python.
- Les variables d'environnement doivent être configurées dans l'interface de l'hébergeur.
- Utilisez MySQL en production, pas SQLite.

## 6. Vérification

- Ouvrez `https://gagri.dt-verse.com`
- Confirmez que la page se charge.
- Connectez-vous avec un compte administrateur.

## 7. Résolution des problèmes courants

- `ImportError` : dépendances manquantes ou `requirements.txt` non installé.
- `DisallowedHost` : ajoutez `gagri.dt-verse.com` dans `ALLOWED_HOSTS`.
- `OperationalError` : vérifiez les paramètres de base de données.
- `TemplateDoesNotExist` : exécutez `collectstatic` et vérifiez `STATIC_ROOT`.

## 8. Notes importantes

- `MEDIA_ROOT` doit pointer vers un dossier accessible en écriture.
- Redémarrez l'application o2switch après toute modification de `settings.py`.
- En production, utilisez toujours `DEBUG=False`.
