# Services - Guide de développement

## Vue d'ensemble

Les services contiennent toute la logique métier de l'application. Une vue n'appelle JAMAIS la logique métier directement.

## Structure

```
services/
├── authentication_service.py     # Authentification et dashboards
├── utilisateur_service.py        # Gestion des utilisateurs
├── culture_service.py            # Gestion des cultures
├── prediction_service.py         # Prédictions de rendement
├── observation_service.py        # Observations des cultures
├── recommandation_service.py     # Recommandations
└── __init__.py
```

## Principes

### 1. Un service = un domaine métier

```python
# ✅ Correct : chaque service a une responsabilité claire
class AuthenticationService:
    @staticmethod
    def authentifier(request, email, password):
        ...
    
    @staticmethod
    def obtenir_dashboard(utilisateur):
        ...

class UtilisateurService:
    @staticmethod
    def creer_administrateur(utilisateur):
        ...
    
    @staticmethod
    def obtenir_type(utilisateur):
        ...
```

### 2. Tous les méthodes doivent être @staticmethod

```python
# ❌ Mauvais (utilise self)
class AuthenticationService:
    def authentifier(self, request, email, password):
        ...

# ✅ Correct (@staticmethod)
class AuthenticationService:
    @staticmethod
    def authentifier(request, email, password):
        ...
```

### 3. Pas d'état global

```python
# ❌ Mauvais
class UtilisateurService:
    utilisateur_cache = {}
    
    def get(self, pk):
        return self.utilisateur_cache.get(pk)

# ✅ Correct
class UtilisateurService:
    @staticmethod
    def get(pk):
        return Utilisateur.objects.get(pk=pk)
```

## AuthenticationService

### authentifier()

```python
@staticmethod
def authentifier(request, email, mot_de_passe):
    """
    Authentifier un utilisateur par email et mot de passe.
    
    Args:
        request: HttpRequest
        email: str
        mot_de_passe: str
    
    Returns:
        Utilisateur si succès, None sinon
    
    Raises:
        Aucune exception levée
    """
    utilisateur = authenticate(
        request=request,
        username=email,  # USERNAME_FIELD = 'email'
        password=mot_de_passe,
    )
    
    if utilisateur is not None:
        login(request, utilisateur)
    
    return utilisateur
```

**Utilisation :**
```python
utilisateur = AuthenticationService.authentifier(request, 'admin@test.com', 'pass123')
if utilisateur:
    print(f"Bienvenue {utilisateur.first_name}")
else:
    print("Identifiants invalides")
```

### deconnecter()

```python
@staticmethod
def deconnecter(request):
    """
    Déconnecter l'utilisateur courant.
    
    Args:
        request: HttpRequest
    """
    logout(request)
```

**Utilisation :**
```python
AuthenticationService.deconnecter(request)
```

### obtenir_dashboard()

```python
@staticmethod
def obtenir_dashboard(utilisateur):
    """
    Obtenir la route du dashboard selon le type d'utilisateur.
    
    Args:
        utilisateur: Utilisateur instance
    
    Returns:
        str: Route du dashboard ('core:dashboard_admin', etc.)
        None si aucun profil
    """
    type_utilisateur = UtilisateurService.obtenir_type(utilisateur)
    
    correspondance = {
        "administrateur": "core:dashboard_admin",
        "agronome": "core:dashboard_agronome",
        "agriculteur": "core:dashboard_agriculteur",
    }
    
    return correspondance.get(type_utilisateur)
```

**Utilisation :**
```python
dashboard = AuthenticationService.obtenir_dashboard(request.user)
if dashboard:
    return redirect(dashboard)
```

## UtilisateurService

### obtenir_type()

```python
@staticmethod
def obtenir_type(utilisateur):
    """
    Retourner le type réel de l'utilisateur.
    
    Args:
        utilisateur: Utilisateur instance
    
    Returns:
        str: "administrateur", "agronome", "agriculteur", ou "utilisateur"
    """
    if Administrateur.objects.filter(pk=utilisateur.pk).exists():
        return "administrateur"
    
    if Agronome.objects.filter(pk=utilisateur.pk).exists():
        return "agronome"
    
    if Agriculteur.objects.filter(pk=utilisateur.pk).exists():
        return "agriculteur"
    
    return "utilisateur"
```

**Utilisation :**
```python
type_util = UtilisateurService.obtenir_type(utilisateur)
print(f"Type: {type_util}")  # Output: "administrateur"
```

### creer_administrateur()

```python
@staticmethod
def creer_administrateur(utilisateur: Utilisateur):
    """
    Créer un profil administrateur pour un utilisateur.
    
    Args:
        utilisateur: Utilisateur instance (déjà créée)
    
    Returns:
        Administrateur instance
    """
    administrateur = UtilisateurService._creer_sous_classe(
        utilisateur,
        Administrateur,
    )
    
    UtilisateurService.ajouter_groupe(utilisateur, "Administrateurs")
    
    return administrateur
```

**Utilisation :**
```python
utilisateur = Utilisateur.objects.create_user(
    email='admin@test.com',
    username='admin',
    password='pass123'
)

admin = UtilisateurService.creer_administrateur(utilisateur)
print(f"Admin créé: {admin.id}")
```

### creer_agronome()

```python
@staticmethod
def creer_agronome(utilisateur: Utilisateur):
    """Créer un profil agronome pour un utilisateur."""
    agronome = UtilisateurService._creer_sous_classe(
        utilisateur,
        Agronome,
    )
    
    UtilisateurService.ajouter_groupe(utilisateur, "Agronomes")
    
    return agronome
```

### creer_agriculteur()

```python
@staticmethod
def creer_agriculteur(utilisateur: Utilisateur):
    """Créer un profil agriculteur pour un utilisateur."""
    agriculteur = UtilisateurService._creer_sous_classe(
        utilisateur,
        Agriculteur,
    )
    
    UtilisateurService.ajouter_groupe(utilisateur, "Agriculteurs")
    
    return agriculteur
```

### _creer_sous_classe() (interne)

```python
@staticmethod
def _creer_sous_classe(utilisateur: Utilisateur, sous_classe):
    """
    Créer une instance de sous-classe pour un utilisateur.
    
    Interne : ne pas appeler directement!
    
    Args:
        utilisateur: Utilisateur instance
        sous_classe: Classe de sous-classe (Administrateur, Agronome, etc.)
    
    Returns:
        Instance de sous-classe
    """
    # Vérifier si existe déjà
    instance = sous_classe.objects.filter(pk=utilisateur.pk).first()
    if instance:
        return instance  # Idempotent
    
    # Extraire champs du parent
    attributs = UtilisateurService._extraire_champs_parent(utilisateur)
    
    # Créer la sous-classe avec le même pk
    instance = sous_classe(pk=utilisateur.pk, **attributs)
    instance.save(force_insert=False)
    
    return instance
```

### ajouter_groupe()

```python
@staticmethod
def ajouter_groupe(utilisateur, nom_groupe):
    """
    Ajouter l'utilisateur à un groupe Django.
    
    Args:
        utilisateur: Utilisateur instance
        nom_groupe: str nom du groupe
    """
    groupe, _ = Group.objects.get_or_create(name=nom_groupe)
    utilisateur.groups.add(groupe)
```

## Modèle de conception

### Pattern : Service factory

Tous les services utilisent @staticmethod pour éviter les états globaux :

```python
# ✅ Correct
class MonService:
    @staticmethod
    def faire_quelquechose():
        return Objet.objects.all()

# Utilisation
resultats = MonService.faire_quelquechose()
```

### Pattern : Input validation

```python
# ✅ Valider les inputs
@staticmethod
def authentifier(request, email, mot_de_passe):
    if not email or not mot_de_passe:
        return None
    # ...
```

### Pattern : Error handling

```python
# ✅ Retourner None ou une valeur défaut
@staticmethod
def obtenir_dashboard(utilisateur):
    type_util = UtilisateurService.obtenir_type(utilisateur)
    return correspondance.get(type_util)  # Retourne None si absent

# ❌ Ne PAS lever d'exception pour la logique métier
@staticmethod
def obtenir_dashboard(utilisateur):
    # Ne PAS faire:
    # if type_util not in correspondance:
    #     raise Exception("Type invalide")
```

## Bonnes pratiques

### 1. Toujours utiliser @staticmethod

```python
# ✅ Correct
class MonService:
    @staticmethod
    def faire():
        return 42

# Usage
resultat = MonService.faire()
```

### 2. Pas d'accès à `self`

```python
# ❌ Mauvais
class MonService:
    @staticmethod
    def faire(self):  # ❌ self inutile!
        pass

# ✅ Correct
class MonService:
    @staticmethod
    def faire():
        pass
```

### 3. Pas de modification de l'objet after stateless

```python
# ✅ Correct : chaque appel indépendant
result1 = AuthenticationService.authentifier(req1, 'email1', 'pass1')
result2 = AuthenticationService.authentifier(req2, 'email2', 'pass2')
```

### 4. Toujours retourner, ne pas modifier le contexte

```python
# ✅ Correct : retourner le résultat
def creer_administrateur(utilisateur):
    admin = _creer_sous_classe(utilisateur, Administrateur)
    ajouter_groupe(utilisateur, "Administrateurs")
    return admin  # Retourner, pas modifier global

# ❌ Mauvais : modifier global
ADMINISTRATEURS = []
def creer_administrateur(utilisateur):
    ADMINISTRATEURS.append(utilisateur)
```

## Types de services

### 1. Services de lecture seule

```python
@staticmethod
def obtenir_type(utilisateur):
    # Pas de modification
    return type_util
```

### 2. Services de création

```python
@staticmethod
def creer_administrateur(utilisateur):
    # Crée nouveau record
    administrateur = _creer_sous_classe(...)
    ajouter_groupe(...)
    return administrateur
```

### 3. Services composites

```python
@staticmethod
def authentifier(request, email, password):
    utilisateur = authenticate(...)  # Appelle Django
    if utilisateur:
        login(request, utilisateur)  # Appelle Django
    return utilisateur
```

## Tests

Chaque service doit avoir des tests complètes.

Voir `docs/tests.md` pour la stratégie de tests.

## Déploiement

Les services n'ont pas de dépendances à l'environnement (sauf Django), donc ils déploient correctement en production.

En cas de migration d'une logique métier :

1. Ajouter la nouvelle implémentation dans le service
2. Mettre à jour les tests
3. Mettre à jour les vues pour appeler le nouveau service
4. Supprimer l'ancienne implémentation
5. Tests d'intégration pour confirmer
