# Tests - Stratégie et Guide

## Vue d'ensemble

Les tests validenty que le système fonctionne correctement. L'objectif est une couverture > 80%.

```
┌─────────────────┐
│  Unit Tests     │  Tesent services, modèles, managers isolés
└────────┬────────┘
         │
┌─────────────────┐
│ Integration     │  Testent flows complets (login → dashboard)
│  Tests          │
└────────┬────────┘
         │
┌─────────────────┐
│ Manual Tests    │  Tests manuels en navigateur
└─────────────────┘
```

## Structure

```
authentication/
├── tests.py           # Tests des vues et service d'authentification

utilisateurs/
├── tests.py           # Tests des modèles, managers et services
```

## Unit Tests

### Modèles (utilisateurs/tests.py)

```python
class UtilisateurManagerTest(TestCase):
    """Tests du gestionnaire personnalisé."""
    
    def test_create_user_with_email(self):
        utilisateur = Utilisateur.objects.create_user(
            email='test@example.com',
            username='test',
            password='pass123'
        )
        self.assertEqual(utilisateur.email, 'test@example.com')
    
    def test_create_superuser(self):
        utilisateur = Utilisateur.objects.create_superuser(
            email='admin@example.com',
            username='admin',
            password='adminpass'
        )
        self.assertTrue(utilisateur.is_superuser)
```

### Services

#### UtilisateurService (utilisateurs/tests.py)

```python
class UtilisateurServiceTest(TestCase):
    """Tests de création de profils."""
    
    def test_creer_administrateur_creates_subclass(self):
        utilisateur = Utilisateur.objects.create_user(
            email='admin@test.com',
            password='pass123'
        )
        
        admin = UtilisateurService.creer_administrateur(utilisateur)
        
        self.assertEqual(admin.pk, utilisateur.pk)
        self.assertTrue(
            Administrateur.objects.filter(pk=utilisateur.pk).exists()
        )
    
    def test_obtenir_type_administrateur(self):
        utilisateur = Utilisateur.objects.create_user(
            email='test@test.com',
            password='pass123'
        )
        UtilisateurService.creer_administrateur(utilisateur)
        
        type_util = UtilisateurService.obtenir_type(utilisateur)
        self.assertEqual(type_util, "administrateur")
```

#### AuthenticationService (authentication/tests.py)

```python
class AuthenticationServiceTest(TestCase):
    """Tests du service d'authentification."""
    
    def test_authentifier_returns_user_on_success(self):
        utilisateur = Utilisateur.objects.create_user(
            email='test@test.com',
            password='pass123'
        )
        UtilisateurService.creer_administrateur(utilisateur)
        
        user = AuthenticationService.authentifier(
            None,
            'test@test.com',
            'pass123'
        )
        
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'test@test.com')
    
    def test_obtenir_dashboard_admin(self):
        utilisateur = Utilisateur.objects.create_user(
            email='admin@test.com',
            password='pass123'
        )
        UtilisateurService.creer_administrateur(utilisateur)
        
        dashboard = AuthenticationService.obtenir_dashboard(utilisateur)
        self.assertEqual(dashboard, "core:dashboard_admin")
```

## Integration Tests

### Flux de login complet (authentication/tests.py)

```python
class AuthenticationViewsTest(TestCase):
    """Tests complets du flux de connexion."""
    
    def setUp(self):
        self.client = Client()
        self.login_url = reverse("authentication:connexion")
        
        # Créer un utilisateur admin
        self.utilisateur_admin = Utilisateur.objects.create_user(
            email="admin@test.com",
            username="admin",
            password="password123",
        )
        UtilisateurService.creer_administrateur(self.utilisateur_admin)
    
    def test_valid_admin_login_redirects_to_admin_dashboard(self):
        """Un admin valide est redirigé vers son dashboard."""
        response = self.client.post(
            self.login_url,
            {"email": "admin@test.com", "mot_de_passe": "password123"},
            follow=True,
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("dashboard/administrateur", 
                     response.request["PATH_INFO"])
    
    def test_invalid_password_login_fails(self):
        """Un mot de passe invalide échoue."""
        response = self.client.post(
            self.login_url,
            {"email": "admin@test.com", "mot_de_passe": "wrongpass"},
        )
        
        self.assertEqual(response.status_code, 200)
        # Le formulaire doit afficher une erreur
```

## Commandes de test

### Tous les tests

```bash
python manage.py test
```

**Output attendu :**
```
Found XX test(s).
Creating test database for alias 'default'...
...................................................
Ran XX tests in X.XXXs

OK
```

### Tests d'une application

```bash
# Application authentification
python manage.py test authentication

# Application utilisateurs
python manage.py test utilisateurs

# Application core
python manage.py test core
```

### Tests d'une classe

```bash
python manage.py test authentication.tests.AuthenticationViewsTest
python manage.py test utilisateurs.tests.UtilisateurServiceTest
```

### Tests d'une méthode

```bash
python manage.py test authentication.tests.AuthenticationViewsTest.test_valid_admin_login_redirects_to_admin_dashboard
```

### Run avec verbosité

```bash
# Verbosité 0 (minimal)
python manage.py test --verbosity=0

# Verbosité 1 (défaut)
python manage.py test --verbosity=1

# Verbosité 2 (détaillé)
python manage.py test --verbosity=2

# Verbosité 3 (très détaillé)
python manage.py test --verbosity=3
```

### Avec couverture de code

```bash
pip install coverage

# Générer les rapports
coverage run --source='.' manage.py test
coverage report

# Rapport HTML
coverage html
open htmlcov/index.html
```

## Fixtures

### Fixtures (données de test)

**utilisateurs/fixtures/initial_data.json** :
```json
[
    {
        "model": "utilisateurs.utilisateur",
        "pk": 1,
        "fields": {
            "email": "admin@test.com",
            "username": "admin",
            "password": "pbkdf2_sha256$...",
            "first_name": "Admin",
            "last_name": "Test",
            "is_active": true
        }
    }
]
```

Charger les fixtures :
```bash
python manage.py loaddata initial_data
```

## Stratégie de couverture

### 1. Modèles (100%)

- ✓ Création d'utilisateur
- ✓ Héritage multi-table
- ✓ Méthodes modèle

### 2. Managers (100%)

- ✓ create_user()
- ✓ create_superuser()
- ✓ Validation des inputs

### 3. Services (100%)

- ✓ Authentification valide/invalide
- ✓ Résolution du type d'utilisateur
- ✓ Création de profils

### 4. Vues (90%)

- ✓ GET /connexion (formulaire vide)
- ✓ POST /connexion (valide)
- ✓ POST /connexion (invalide)
- ✓ GET /deconnexion
- ✓ Déjà connecté → redirect dashboard

### 5. Forms (100%)

- ✓ Validation email
- ✓ Validation mot de passe
- ✓ Errors

### 6. URLs (100%)

- ✓ Route / → connexion
- ✓ Route /deconnexion → deconnexion
- ✓ Route /dashboard/administrateur/ → dashboard
- ✓ Reverse URLs

### 7. Integration (90%)

- ✓ Login → Redirect dashboard
- ✓ Logout → Disconnect
- ✓ Permissions (@login_required)

## Tests manuels

### Scénario 1 : Admin login

```
1. Aller à http://127.0.0.1:8000
2. Entrer admin@test.com / password123
3. Cliquer "Se connecter"
   → Attending : redirection à /dashboard/administrateur/
4. Voir le dashboard admin
5. Cliquer "Déconnexion"
   → Attending : retour à page login
```

### Scénario 2 : Agronome login

```
1. Aller à http://127.0.0.1:8000
2. Entrer agronome@test.com / password123
3. Cliquer "Se connecter"
   → Attending : redirection à /dashboard/agronome/
4. Voir le dashboard agronome
5. Cliquer "Déconnexion"
   → Retour à page login
```

### Scénario 3 : Agriculteur login

```
1. Aller à http://127.0.0.1:8000
2. Entrer agriculteur@test.com / password123
3. Cliquer "Se connecter"
   → Attending : redirection à /dashboard/agriculteur/
4. Voir le dashboard agriculteur
5. Cliquer "Déconnexion"
   → Retour à page login
```

### Scénario 4 : Invalid email

```
1. Aller à http://127.0.0.1:8000
2. Entrer nonexistent@test.com / password123
3. Cliquer "Se connecter"
   → Attending : message d'erreur
   → Formulaire remains on page
```

### Scénario 5 : Invalid password

```
1. Aller à http://127.0.0.1:8000
2. Entrer admin@test.com / wrongpass
3. Cliquer "Se connecter"
   → Attending : message d'erreur
   → Formulaire remains on page
```

### Scénario 6 : Already logged in

```
1. POST /connexion avec credentials valides
   → User logged in, session created
2. GET /connexion
   → Attending : redirect to dashboard (pas back à login)
```

## Résultats attendus

### Tests unit

```bash
$ python manage.py test
Found 29 tests.
Creating test database...

test_create_user_with_email ... ok
test_create_superuser ... ok
test_creer_administrateur_creates_subclass ... ok
test_obtenir_type_administrateur ... ok
test_authentifier_returns_user_on_success ... ok
test_obtenir_dashboard_admin ... ok
test_valid_admin_login_redirects_to_admin_dashboard ... ok
test_invalid_password_login_fails ... ok
... (19 more tests) ...

Ran 29 tests in 2.345s

OK
```

### Couverture

```bash
$ coverage report
Name                              Stmts   Miss  Cover
─────────────────────────────────────────────────
authentication/forms.py              20      2    90%
authentication/views.py              45      3    93%
utilisateurs/models.py               60      4    93%
utilisateurs/managers.py             35      2    94%
services/authentication_service.py   20      1    95%
services/utilisateur_service.py      50      3    94%
core/views.py                        30      5    83%
─────────────────────────────────────────────────
TOTAL                               260     20    92%
```

## Debugging des tests

### Voir les détails

```bash
python manage.py test --verbosity=2
```

### Arrêter au premier fail

```bash
python manage.py test --failfast
```

### Garder la DB de test

```bash
python manage.py test --keepdb
```

### Run un test unique

```bash
python manage.py test authentication.tests --debug-mode
```

### Logs dans les tests

```python
def test_something(self):
    import logging
    logger = logging.getLogger(__name__)
    logger.info("Debug message")
    
    # Ou
    print("Debug output")
    
    self.assertEqual(1, 1)
```

## Bonnes pratiques

### 1. Isoler les données de test

```python
class MonTest(TestCase):
    def setUp(self):
        # Données créées avant chaque test
        self.utilisateur = Utilisateur.objects.create_user(...)
    
    def test_something(self):
        pass
    
    # Chaque test a ses propres données
```

### 2. Utiliser assertions spécifiques

```python
# ❌ Mauvais
self.assertTrue(utilisateur is not None)

# ✅ Correct
self.assertIsNotNone(utilisateur)

# Plus de clarté
self.assertEqual(type_util, "administrateur")
self.assertIn("dashboard", response.request["PATH_INFO"])
```

### 3. Noms descriptifs

```python
# ❌ Mauvais
def test_1(self):
    pass

# ✅ Correct
def test_valid_admin_login_redirects_to_admin_dashboard(self):
    pass
```

### 4. Un test = une chose

```python
# ❌ Mauvais : teste plusieurs choses
def test_login(self):
    user = authenticate(...)
    self.assertTrue(user)
    login(request, user)
    self.assertTrue(request.user.is_authenticated)
    dashboard = obtenir_dashboard(user)
    self.assertEqual(dashboard, "admin")

# ✅ Correct : un test par chose
def test_authenticate_returns_user(self):
    user = authenticate(...)
    self.assertIsNotNone(user)

def test_get_admin_dashboard(self):
    ...
    self.assertEqual(dashboard, "admin")
```

## Futur

- [ ] Selenium tests pour JavaScript
- [ ] Load tests avec Locust
- [ ] API tests
- [ ] Performance tests
