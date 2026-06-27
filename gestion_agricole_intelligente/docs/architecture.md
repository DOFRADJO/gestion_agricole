# Architecture du Système

## Vue d'ensemble

L'application Gestion Agricole Intelligente est une système web Django utilisant une architecture en couches :

```
┌─────────────────────────────────┐
│      Interface Utilisateur      │
│         (Templates HTML)        │
└─────────────────┬───────────────┘
                  │
┌─────────────────────────────────┐
│     Couche Présentation         │
│      (Views Django)             │
│  - authentication/views.py      │
│  - core/views.py                │
└─────────────────┬───────────────┘
                  │
┌─────────────────────────────────┐
│     Couche Métier               │
│      (Services)                 │
│  - services/authentication_     │
│    service.py                   │
│  - services/utilisateur_        │
│    service.py                   │
└─────────────────┬───────────────┘
                  │
┌─────────────────────────────────┐
│     Couche Données              │
│      (Models Django)            │
│  - utilisateurs/models.py       │
│  - cultures/models.py           │
└─────────────────┬───────────────┘
                  │
┌─────────────────────────────────┐
│     Base de Données             │
│      (MySQL)                    │
└─────────────────────────────────┘
```

## Principes architecturaux

### 1. Séparation des responsabilités

Chaque couche a une responsabilité bien définie :

- **Views** : Reçoivent les requêtes HTTP, appellent les services
- **Services** : Contiennent la logique métier
- **Models** : Représentent les entités métier et leur persistance

### 2. Héritage multi-table

L'application utilise l'héritage multi-table Django pour représenter les différents types d'utilisateurs :

```
Utilisateur
    ├── pk (id)
    ├── email (unique)
    ├── USERNAME_FIELD = 'email'
    ├── password

Administrateur
    ├── pk → Utilisateur.pk (relations 1:1)
    └── table séparée : utilisateurs_administrateur

Agronome
    ├── pk → Utilisateur.pk (relations 1:1)
    └── table séparée : utilisateurs_agronome

Agriculteur
    ├── pk → Utilisateur.pk (relations 1:1)
    └── table séparée : utilisateurs_agriculteur
```

### 3. Pas de field 'role'

L'application refuse l'utilisation d'un simple champ `role` au profit de l'héritage multi-table. Cela garantit :

- Type checking au niveau Python
- Méthodes spécifiques dans chaque classe
- Intégrité des données

### 4. Service Layer pattern

Toute la logique métier est centralisée dans les services :

```python
# ❌ Ne PAS faire (logique dans la vue)
def login(request):
    user = authenticate(request, username=email, password=pwd)
    if Administrateur.objects.filter(pk=user.pk).exists():
        return redirect('admin')

# ✅ FAIRE (logique dans le service)
def login(request):
    user = AuthenticationService.authentifier(request, email, pwd)
    if user:
        dashboard = AuthenticationService.obtenir_dashboard(user)
        return redirect(dashboard)
```

## Organisation des fichiers

### Applications Django

Chaque application gère son domaine métier :

- **authentication/** : Connexion, déconnexion, gestion des sessions
- **utilisateurs/** : Modèles et managers d'utilisateurs
- **core/** : Vues des dashboards, cœur de l'application
- **common/** : Commandes de gestion
- **cultures/** : Gestion des cultures agricoles
- **observations/** : Observations des cultures
- **predictions/** : Prédictions de rendement
- **recommandations/** : Recommandations pour l'agriculteur

### Services

La logique métier est dans `services/` :

- **authentication_service.py** : Authentification et resolution de dashboard
- **utilisateur_service.py** : CRUD utilisateurs et gestion des profils
- **culture_service.py** : Logique métier des cultures
- **prediction_service.py** : Calcul des prédictions
- **observation_service.py** : Gestion des observations
- **recommandation_service.py** : Génération des recommandations

## Flux de données

### Cas d'utilisation : Connexion d'un administrateur

```
1. Interface (login.html)
   └─> Formulaire POST avec email et mot de passe

2. View (authentication/views.py → connexion())
   └─> Récupère les données du formulaire
   └─> Appelle AuthenticationService.authentifier()

3. Service (services/authentication_service.py)
   └─> Appelle Django authenticate()
   └─> Appelle Django login()
   └─> Appelle AuthenticationService.obtenir_dashboard()
   └─> Appelle UtilisateurService.obtenir_type()

4. Service (services/utilisateur_service.py)
   └─> Requête : Administrateur.objects.filter(pk=user.pk)
   └─> Retourne le type "administrateur"

5. Service (authentication_service_service.py)
   └─> Retourne la route "core:dashboard_admin"

6. View (authentication/views.py)
   └─> Redirige vers la route

7. Database (MySQL)
   └─> Requête SELECT * FROM utilisateurs_utilisateur WHERE id=X
   └─> Requête SELECT * FROM utilisateurs_administrateur WHERE id=X
```

## Modèles de données

### Utilisateur

```python
class Utilisateur(AbstractUser):
    email = EmailField(unique=True)
    USERNAME_FIELD = 'email'
    
    # Hérité de AbstractUser
    username, first_name, last_name, password, is_active, 
    is_staff, is_superuser, groups, user_permissions, etc.
```

### Administrateur

```python
class Administrateur(Utilisateur):
    # Hérite de Utilisateur
    # Table séparée : utilisateurs_administrateur
    # Clé primaire = Utilisateur.pk
    
    # Méthodes
    creer_utilisateur()
    modifier_utilisateur()
    supprimer_utilisateur()
```

### Agronome

```python
class Agronome(Utilisateur):
    consulter_cultures()
    consulter_observations()
```

### Agriculteur

```python
class Agriculteur(Utilisateur):
    consulter_predictions()
    consulter_recommandations()
```

## Requêtes de base de données

### Vérifier si un utilisateur est administrateur

```python
# ❌ Mauvais (utilise hasattr qui charge l'objet)
if hasattr(user, 'administrateur'):
    ...

# ✅ Correct (une seule requête)
Administrateur.objects.filter(pk=user.pk).exists()

# ✅ Correct (retourne l'objet directement)
try:
    admin = user.administrateur  # Accès au profil
except Administrateur.DoesNotExist:
    ...
```

### Créer un administrateur

```python
# ✅ Correct (multi-table inheritance)
utilisateur = Utilisateur.objects.create_user(
    email='admin@example.com',
    username='admin',
    password='pass123'
)

# Créer la ligne de sous-classe
administrateur = Administrateur(
    pk=utilisateur.pk,
    email=utilisateur.email,
    username=utilisateur.username,
    password=utilisateur.password,
    # ... tous les champs du parent
)
administrateur.save(force_insert=False)
```

## Sécurité

### Authentification

- Utilisation de `django.contrib.auth.authenticate()`
- Support de sessions HTTP
- Protection CSRF sur tous les formulaires

### Autorisation

- Décorateur `@login_required` sur les vues protégées
- Groupes Django pour les rôles
- Vérification du type d'utilisateur avant redirection

### Bonnes pratiques

- Passwords hachés avec PBKDF2 de Django
- Email unique par utilisateur
- Validation des formulaires côté serveur

## Performance

### Optimisations

- Select_related et prefetch_related when needed
- Indexes sur email et pk
- Caching if needed

### Limitations

- Pas de pagination (si > 100 utilisateurs, ajouter)
- Pas de cache (ajouter Redis si nécessaire)

## Déploiement

### Configuration de production

1. `DEBUG = False`
2. `ALLOWED_HOSTS` configuré correctement
3. `SECRET_KEY` changée et sécurisée
4. HTTPS forcé
5. Database backup régulier

### Variables d'environnement

Toutes sensibles via `.env` :

```
SECRET_KEY
DEBUG
DB_ENGINE
DB_NAME
DB_USER
DB_PASSWORD
DB_HOST
DB_PORT
```

## Tests

Couverture des tests requise : > 80%

- Unit tests sur les modèles
- Unit tests sur les services
- Integration tests pour les flows complets
- Fixtures pour les données de test

Voir `docs/tests.md` pour les détails.
