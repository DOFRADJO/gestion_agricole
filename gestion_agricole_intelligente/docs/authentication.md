# Authentification - Guide Technique

## Vue d'ensemble

Le système d'authentification fonctionne selon ce flux :

```
Login Form
   ↓
POST /
   ↓
authentication/views.py::connexion()
   ↓
AuthenticationService.authentifier()
   ↓
Django authenticate()
   ↓
Django login()
   ↓
AuthenticationService.obtenir_dashboard()
   ↓
UtilisateurService.obtenir_type()
   ↓
redirect(dashboard_url)
```

## Composants

### 1. Formulaire (authentication/forms.py)

```python
class ConnexionForm(forms.Form):
    email = forms.EmailField(label="Adresse e-mail")
    mot_de_passe = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput()
    )
```

**Points importants :**
- Email obligatoire (pas username)
- Validation HTML5

### 2. Vue (authentication/views.py)

```python
def connexion(request):
    # Si déjà connecté, rediriger vers dashboard
    if request.user.is_authenticated:
        destination = AuthenticationService.obtenir_dashboard(request.user)
        if destination:
            return redirect(destination)
        # Si pas de profil, déconnecter
        AuthenticationService.deconnecter(request)
        messages.error(request, "Profil inexistant")
        return redirect("authentication:connexion")
    
    # Si GET, afficher formulaire
    if request.method == "GET":
        formulaire = ConnexionForm()
        return render(request, "authentication/login.html", {"form": formulaire})
    
    # Si POST, traiter
    formulaire = ConnexionForm(request.POST)
    if formulaire.is_valid():
        utilisateur = AuthenticationService.authentifier(
            request,
            formulaire.cleaned_data["email"],
            formulaire.cleaned_data["mot_de_passe"],
        )
        
        if utilisateur:
            destination = AuthenticationService.obtenir_dashboard(utilisateur)
            if destination:
                return redirect(destination)
            AuthenticationService.deconnecter(request)
            messages.error(request, "Profil inexistant")
            return redirect("authentication:connexion")
        
        messages.error(request, "Email ou mot de passe incorrect")
    
    return render(request, "authentication/login.html", {"form": formulaire})
```

**Points importants :**
- Vérification déjà connecté
- Gestion du cas "pas de profil"
- Erreurs utilisateur différentes

### 3. Service (services/authentication_service.py)

```python
class AuthenticationService:
    
    @staticmethod
    def authentifier(request, email, mot_de_passe):
        """Authentifier un utilisateur."""
        utilisateur = authenticate(
            request=request,
            username=email,  # USERNAME_FIELD = 'email'
            password=mot_de_passe,
        )
        
        if utilisateur is not None:
            login(request, utilisateur)
        
        return utilisateur
    
    @staticmethod
    def deconnecter(request):
        """Déconnecter l'utilisateur."""
        logout(request)
    
    @staticmethod
    def obtenir_dashboard(utilisateur):
        """Obtenir la route du dashboard selon le type."""
        type_utilisateur = UtilisateurService.obtenir_type(utilisateur)
        
        correspondance = {
            "administrateur": "core:dashboard_admin",
            "agronome": "core:dashboard_agronome",
            "agriculteur": "core:dashboard_agriculteur",
        }
        
        return correspondance.get(type_utilisateur)
```

**Points importants :**
- `username=email` car `USERNAME_FIELD = 'email'`
- Pas d'exception, retourne None si échec
- Délégation du type à UtilisateurService

### 4. Service utilisateur (services/utilisateur_service.py)

```python
class UtilisateurService:
    
    @staticmethod
    def obtenir_type(utilisateur):
        """Retourner le type réel de l'utilisateur."""
        if Administrateur.objects.filter(pk=utilisateur.pk).exists():
            return "administrateur"
        
        if Agronome.objects.filter(pk=utilisateur.pk).exists():
            return "agronome"
        
        if Agriculteur.objects.filter(pk=utilisateur.pk).exists():
            return "agriculteur"
        
        return "utilisateur"
```

**Points importants :**
- Requête directe sur les tables de sous-classe
- Pas de hasattr() (fragile et inefficace)
- Retourne toujours un string

## Configuration Django

### settings.py

```python
AUTH_USER_MODEL = 'utilisateurs.Utilisateur'

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.messages',
    
    'authentication',
    'utilisateurs',
    'core',
    # ...
]

MIDDLEWARE = [
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # ...
]
```

### urls.py

```python
urlpatterns = [
    path("", include("authentication.urls")),
    path("", include("core.urls")),
]
```

### authentication/urls.py

```python
app_name = "authentication"

urlpatterns = [
    path("", views.connexion, name="connexion"),
    path("deconnexion/", views.deconnexion, name="deconnexion"),
]
```

### core/urls.py

```python
app_name = "core"

urlpatterns = [
    path("dashboard/administrateur/", views.dashboard_admin, name="dashboard_admin"),
    path("dashboard/agronome/", views.dashboard_agronome, name="dashboard_agronome"),
    path("dashboard/agriculteur/", views.dashboard_agriculteur, name="dashboard_agriculteur"),
]
```

## Flux détaillé

### Étape 1 : Affichage du formulaire

```
GET /
  ↓
connexion(request)
  ↓
if request.user.is_authenticated: False
  ↓
if request.method == 'GET': True
  ↓
return render(login.html)
```

### Étape 2 : Soumission du formulaire

```
POST /
  email=admin@example.com
  mot_de_passe=admin123
  
  ↓
connexion(request)
  ↓
if request.user.is_authenticated: False
  ↓
if request.method == 'POST': True
  ↓
formulaire = ConnexionForm(POST)
formulaire.is_valid()
  ↓
authentifier('admin@example.com', 'admin123')
```

### Étape 3 : Authentification

```
authentifier(request, email, password)
  ↓
authenticate(request, username='admin@example.com', password='admin123')
  ↓
UtilisateurManager.authenticate()  # Django
  ↓
Utilisateur.objects.get(email='admin@example.com')
  ↓
check_password()  # PBKDF2
  ↓
if password_valid: return utilisateur else return None
  ↓
if utilisateur:
    login(request, utilisateur)  # Crée session
  ↓
return utilisateur
```

### Étape 4 : Résolution du dashboard

```
obtenir_dashboard(utilisateur)
  ↓
obtenir_type(utilisateur)
  ↓
Administrateur.objects.filter(pk=2).exists()  # Yes
  ↓
return "administrateur"
  ↓
correspondance = {...}
return correspondance["administrateur"]  # "core:dashboard_admin"
  ↓
return "core:dashboard_admin"
```

### Étape 5 : Redirection

```
if destination:
    return redirect(destination)  # "core:dashboard_admin"
  ↓
Django URL resolver
  ↓
reverse('core:dashboard_admin')
  ↓
/dashboard/administrateur/
  ↓
django.contrib.auth.decorators.login_required()
  ↓
if request.user.is_authenticated: True
  ↓
dashboard_admin(request)
  ↓
return render(dashboard_admin.html)
```

## Problèmes courants et solutions

### Problème 1 : Redirection infinie vers login

**Cause :** Le type d'utilisateur n'est pas détecté → obtenir_dashboard() retourne None

**Solution :** Vérifier que la sous-classe existe
```bash
python manage.py shell
>>> from utilisateurs.models import Administrateur
>>> Administrateur.objects.filter(pk=2).exists()
True  # Parfait, la under-classe existe
False  # Problème!
```

**Fix :** Créer la sous-classe manuellement
```python
from services.utilisateur_service import UtilisateurService
utilisateur = Utilisateur.objects.get(pk=2)
UtilisateurService.creer_administrateur(utilisateur)
```

### Problème 2 : USERNAME_FIELD pas respecté

**Cause :** Utilisation de authenticate(username=username) au lieu de authenticate(username=email)

**Symptôme :** "Username does not exist"

**Solution :** Toujours passer l'email dans le paramètre `username`
```python
authenticate(
    request=request,
    username=email,  # C'est l'email!
    password=password
)
```

### Problème 3 : Multi-table inheritance incorrecte

**Cause :** Création d'utilisateur sans créer la sous-classe

**Symptôme :** Administrateur.objects.count() < Utilisateur.objects.count()

**Solution :** Toujours appeler le service
```python
# ❌ Mauvais
utilisateur = Utilisateur.objects.create_user(...)

# ✅ Correct
utilisateur = Utilisateur.objects.create_user(...)
UtilisateurService.creer_administrateur(utilisateur)
```

## Tests

### Test d'authentification basique

```python
def test_login_with_valid_credentials(self):
    utilisateur = Utilisateur.objects.create_user(
        email='test@example.com',
        password='pass123'
    )
    UtilisateurService.creer_administrateur(utilisateur)
    
    response = self.client.post('/', {
        'email': 'test@example.com',
        'mot_de_passe': 'pass123'
    }, follow=True)
    
    self.assertEqual(response.status_code, 200)
    self.assertIn('dashboard/administrateur', response.request['PATH_INFO'])
```

### Test de détection de type

```python
def test_obtenir_type_administrateur(self):
    utilisateur = Utilisateur.objects.create_user(
        email='test@example.com'
    )
    UtilisateurService.creer_administrateur(utilisateur)
    
    type_utilisateur = UtilisateurService.obtenir_type(utilisateur)
    self.assertEqual(type_utilisateur, "administrateur")
```

## Sécurité

### Points importants

1. **Passwords hachés** : Django utilise PBKDF2 par défaut
2. **CSRF protection** : Tous les formulaires ont {% csrf_token %}
3. **Session timeout** : Configurable via SESSION_COOKIE_AGE
4. **HTTPS** : À forcer en production

### Bonnes pratiques

```python
# ❌ Ne PAS stocker le password en clair
password = request.POST['password']

# ✅ Laisser Django gérer
authenticate(password=password)  # Django hash et compare

# ❌ Ne PAS montrer différences d'erreur
"Email non trouvé" vs "Mot de passe incorrect"

# ✅ Message générique
"Email ou mot de passe incorrect"
```

## Améliorations futures

1. **Two-factor authentication** (2FA)
2. **OAuth2** (Google, Facebook)
3. **LDAP** pour entreprise
4. **Rate limiting** sur les tentatives
5. **Email verification** après inscription
6. **Password reset** par email

Voir `docs/deployment.md` pour la sécurité en production.
