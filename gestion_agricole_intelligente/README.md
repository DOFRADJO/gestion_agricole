# Gestion Agricole Intelligente

Application web Django pour la gestion intelligente des cultures agricoles, développée avec Django 6, Python 3.13 et MySQL.

## 📋 Table des matières

- [Installation](#installation)
- [Configuration](#configuration)
- [Démarrage](#démarrage)
- [Initialisation](#initialisation)
- [Authentification](#authentification)
- [Tests](#tests)
- [Architecture](#architecture)

## 💻 Installation

### Prérequis

- Python 3.13+
- MySQL 8.0+
- pip et virtualenv

### Étapes d'installation

1. **Cloner le projet**
```bash
cd /mnt/dtamboudisk/Genie_logiciel
git clone <url-du-repo> gestion_agricole_intelligente
cd gestion_agricole_intelligente
```

2. **Créer et activer l'environnement virtuel**
```bash
python -m venv .venv
source .venv/bin/activate  # Sur Linux/Mac
# ou
.venv\Scripts\activate  # Sur Windows
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

## ⚙️ Configuration

### 1. Créer la base de données MySQL

```sql
CREATE DATABASE gestion_agricole_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'gestion_user'@'127.0.0.1' IDENTIFIED BY 'motdepasse123';
GRANT ALL PRIVILEGES ON gestion_agricole_db.* TO 'gestion_user'@'127.0.0.1';
FLUSH PRIVILEGES;
```

### 2. Configurer le fichier .env

Créer un fichier `.env` à la racine du projet :

```env
# Django
SECRET_KEY=django-insecure-fh6!@e4qp)zbr6njvv27w3@y0bbh%dgl@@@rkq21_x1+j^zc%$
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# Database
DB_ENGINE=django.db.backends.mysql
DB_NAME=gestion_agricole_db
DB_USER=gestion_user
DB_PASSWORD=motdepasse123
DB_HOST=127.0.0.1
DB_PORT=3306
```

## 🚀 Démarrage

### 1. Vérifier la configuration

```bash
python manage.py check
```

### 2. Appliquer les migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Initialiser l'application

Cette commande crée les groupes et le premier administrateur :

```bash
python manage.py init_application
```

Ou avec des paramètres personnalisés :

```bash
python manage.py init_application \
  --email=admin@monentreprise.com \
  --password=MonMotDePasse123
```

### 4. Lancer le serveur

```bash
python manage.py runserver
```

L'application est accessible à : `http://127.0.0.1:8000`

## 🔐 Authentification

### Connexion

1. Accéder à `http://127.0.0.1:8000`
2. Entrer l'email et le mot de passe
3. L'utilisateur est redirigé automatiquement vers son dashboard selon son type

### Types d'utilisateurs

- **Administrateur** : Accès complet à l'application, gestion des utilisateurs
- **Agronome** : Accès à la gestion des cultures et observations
- **Agriculteur** : Accès aux prédictions et recommandations

### Créer d'autres utilisateurs

```bash
python manage.py shell
```

```python
from utilisateurs.models import Utilisateur
from services.utilisateur_service import UtilisateurService

# Créer un utilisateur de base
utilisateur = Utilisateur.objects.create_user(
    email="agronome@example.com",
    username="agronome",
    first_name="Jean",
    last_name="Dupont",
    password="password123"
)

# Lui assigner un profil
UtilisateurService.creer_agronome(utilisateur)
# ou
UtilisateurService.creer_agriculteur(utilisateur)
# ou
UtilisateurService.creer_administrateur(utilisateur)
```

## 🧪 Tests

### Exécuter tous les tests

```bash
python manage.py test
```

### Exécuter les tests d'une application

```bash
python manage.py test authentication
python manage.py test utilisateurs
python manage.py test core
```

### Exécuter une classe de tests

```bash
python manage.py test authentication.tests.AuthenticationViewsTest
python manage.py test utilisateurs.tests.UtilisateurServiceTest
```

### Exécuter une méthode de test

```bash
python manage.py test authentication.tests.AuthenticationViewsTest.test_valid_admin_login_redirects_to_admin_dashboard
```

### Couverture de code

```bash
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

## 📁 Architecture

### Structure du projet

```
gestion_agricole_intelligente/
├── authentication/          # Authentification des utilisateurs
│   ├── forms.py            # Formulaires de connexion
│   ├── views.py            # Vues de connexion/déconnexion
│   ├── urls.py             # Routes d'authentification
│   └── tests.py            # Tests d'authentification
├── core/                   # Cœur de l'application
│   ├── views.py            # Vues des dashboards
│   ├── urls.py             # Routes des dashboards
│   └── tests.py            # Tests du cœur
├── utilisateurs/           # Gestion des utilisateurs
│   ├── models.py           # Modèles (Utilisateur, Administrateur, Agronome, Agriculteur)
│   ├── managers.py         # Gestionnaire personnalisé d'utilisateurs
│   ├── tests.py            # Tests des utilisateurs
│   └── forms.py            # Formulaires des utilisateurs
├── common/                 # Commandes de gestion
│   ├── management/
│   │   └── commands/
│   │       └── init_application.py  # Initialisation de l'application
│   └── tests.py            # Tests communs
├── cultures/               # Gestion des cultures
├── observations/           # Observations des cultures
├── predictions/            # Prédictions de rendement
├── recommandations/        # Recommandations
├── services/               # Logique métier
│   ├── authentication_service.py     # Service d'authentification
│   ├── utilisateur_service.py        # Service de gestion des utilisateurs
│   ├── culture_service.py            # Service de gestion des cultures
│   └── ...                           # Autres services
├── templates/              # Templates HTML
│   ├── base/               # Templates de base
│   ├── authentication/     # Templates d'authentification
│   ├── core/               # Templates des dashboards
│   └── ...                 # Autres templates
├── static/                 # Fichiers statiques (CSS, JS, images)
├── media/                  # Fichiers uploadés
├── docs/                   # Documentation technique
├── manage.py               # Utilitaire Django
├── requirements.txt        # Dépendances Python
└── README.md              # Ce fichier
```

### Architecture métier

L'application suit une architecture stricte :

```
View (authentication/views.py)
    ↓
Service (services/authentication_service.py)
    ↓
Model (utilisateurs/models.py)
    ↓
Database (MySQL)
```

### Multi-table inheritance

L'application utilise l'héritage multi-table Django :

```
Utilisateur (AbstractUser)
    ├── Administrateur (hérite de Utilisateur)
    ├── Agronome (hérite de Utilisateur)
    └── Agriculteur (hérite de Utilisateur)
```

Avantages :
- Type réel de l'utilisateur préservé
- Méthodes spécifiques par type utilisateur
- Requêtes de base de données efficaces

## 📚 Documentation technique

Voir les fichiers dans le dossier `docs/` :

- `architecture.md` - Détails de l'architecture
- `authentication.md` - Flux d'authentification détaillé
- `services.md` - Description des services
- `utilisateurs.md` - Gestion des utilisateurs
- `tests.md` - Stratégie de tests

## 🔧 Commandes utiles

### Créer un superutilisateur (admin Django)

```bash
python manage.py createsuperuser
```

Puis initialiser son profil Administrateur :

```bash
python manage.py shell
```

```python
from utilisateurs.models import Utilisateur
from services.utilisateur_service import UtilisateurService

utilisateur = Utilisateur.objects.get(username='admin')
UtilisateurService.creer_administrateur(utilisateur)
```

### Nettoyer la base de données

```bash
# Réinitialiser les migrations
python manage.py migrate zero utilisateurs

# Supprimer toutes les données de la table utilisateurs
python manage.py migrate --plan utilisateurs
```

### Générer les migrationsapidement

```bash
python manage.py makemigrations --merge
python manage.py showmigrations
```

## 🐛 Débogage

### Activer le debug en console

Les logs sont disponibles dans la console lors du `runserver`.

### Utiliser Django shell

```bash
python manage.py shell
```

```python
from utilisateurs.models import Utilisateur, Administrateur
from services.utilisateur_service import UtilisateurService

# Compter les utilisateurs
print(Utilisateur.objects.count())

# Compter les administrateurs
print(Administrateur.objects.count())

# Vérifier le type d'un utilisateur
utilisateur = Utilisateur.objects.first()
print(UtilisateurService.obtenir_type(utilisateur))
```

## ✅ Validation du CU1

Pour valider que le CU1 (Authentification) est complètement fonctionnel :

```bash
# 1. Vérifier les configurations
python manage.py check

# 2. Créer les tables
python manage.py makemigrations
python manage.py migrate

# 3. Initialiser l'application
python manage.py init_application

# 4. Exécuter les tests
python manage.py test

# 5. Lancer le serveur
python manage.py runserver
```

Puis tester manuellement :
1. Accéder à `http://127.0.0.1:8000`
2. Se connecter avec `admin@gestion-agricole.local` / `admin123`
3. Vérifier la redirection vers le dashboard administrateur
4. Tester la déconnexion

## 📝 Licence

Ce projet est développé dans le cadre d'un cours de Génie Logiciel.

## 📧 Contact

Pour toute question ou problème, veuillez contacter l'équipe de développement.
