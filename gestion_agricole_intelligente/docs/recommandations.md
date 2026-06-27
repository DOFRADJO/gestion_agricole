# CU5 : Consultation des Recommandations Agronomiques

## Description

CU5 permet aux agriculteurs de consulter des recommandations agronomiques automatiquement générées à partir des prédictions de rendement. Les recommandations sont :

- **Générées automatiquement** à partir des prédictions existantes
- **Lues seules** (pas de CRUD manuel)
- **Basées sur le rendement prédit** et le niveau de confiance
- **Consultables par historique** pour suivre l'évolution

## Architecture

### Modèles

#### Recommandation (recommandations/models.py)

```python
class Recommandation(models.Model):
    culture = ForeignKey(Culture)
    dateRecommandation = DateField(auto_now_add=True)
    type = CharField(max_length=100)  # "Faible rendement", "Rendement moyen", "Rendement élevé"
    contenu = TextField()  # Contenu textuel de la recommandation
```

**Contraintes** :
- Clé unique : `(culture, dateRecommandation)` — une seule recommandation par culture par jour
- Pas de champ `updated_at` car une nouvelle recommandation remplace l'ancienne

### Services

#### RecommendationService (services/recommandation_service.py)

**Méthodes principales** :

```python
@staticmethod
def generer_recommandation(culture: Culture) -> Recommandation:
    """
    Génère ou met à jour la recommandation pour une culture.
    Récupère la prédiction la plus récente et applique une logique
    provisoire pour déterminer le type et le contenu.
    """
    
@staticmethod
def obtenir_recommandation(culture: Culture) -> Recommandation:
    """
    Retourne la recommandation la plus récente pour une culture.
    Génère automatiquement une recommandation si elle n'existe pas.
    Utilisé lors de la consultation.
    """
    
@staticmethod
def obtenir_recommandations(utilisateur) -> QuerySet:
    """
    Retourne toutes les recommandations accessibles à l'utilisateur.
    - Agriculteur : ses recommandations uniquement
    - Agronome/Admin : toutes les recommandations
    
    Génère automatiquement les recommandations pour toutes les cultures
    de l'utilisateur avant de les retourner.
    """
    
@staticmethod
def obtenir_recommandations_agriculteur(utilisateur) -> QuerySet:
    """
    Restreint l'accès aux recommandations d'un agriculteur.
    Lève PermissionDenied si l'utilisateur n'est pas agriculteur.
    """
    
@staticmethod
def mettre_a_jour_recommandation(culture: Culture) -> Recommandation:
    """
    Recalcule la recommandation pour une culture.
    Appelée après un ajout d'observation pour affiner la recommandation.
    """
    
@staticmethod
def historique(utilisateur, culture=None) -> QuerySet:
    """
    Retourne l'historique des recommandations.
    Filtre par utilisateur et culture si fournis.
    """
```

**Logique de génération (provisoire)** :

```
Pour chaque culture :
  1. Récupérer sa prédiction la plus récente
  2. Si rendement < 2.5 :
     type = "Faible rendement"
     contenu = "Appliquer un apport d'engrais adapté, ..."
  3. Sinon si rendement < 4.0 :
     type = "Rendement moyen"
     contenu = "Maintenir les bonnes pratiques culturales, ..."
  4. Sinon :
     type = "Rendement élevé"
     contenu = "Poursuivre les pratiques actuelles, ..."
  5. Si niveauConfiance < 0.5 :
     Ajouter : "Le niveau de confiance est faible ; complétez les observations..."
  6. Sauvegarder la recommandation (ou la mettre à jour si elle existe)
```

**Note** : Cette logique est **temporaire** et doit être remplacée par un moteur IA en production.

### Vues

#### recommandations/views.py

```python
@login_required
def liste_recommandations(request):
    """
    Affiche la liste des recommandations accessibles à l'utilisateur.
    - GET /recommandations/ : liste
    """
    
@login_required
def detail_recommandation(request, pk):
    """
    Affiche le détail d'une recommandation.
    - GET /recommandations/<pk>/
    - Vérifie les permissions : agriculteur ne peut voir que ses propres recommandations
    """
    
@login_required
def historique_recommandations(request):
    """
    Affiche l'historique complet des recommandations.
    - GET /recommandations/historique/
    - Limité aux recommandations accessibles par l'utilisateur
    """
```

### Routes

#### recommandations/urls.py

```python
urlpatterns = [
    path("", views.liste_recommandations, name="liste"),
    path("historique/", views.historique_recommandations, name="historique"),
    path("<int:pk>/", views.detail_recommandation, name="detail"),
]
```

### Templates

- **templates/recommandations/liste.html** : liste avec table paginée
- **templates/recommandations/detail.html** : détail avec contexte agriculteur
- **templates/recommandations/historique.html** : historique complet

### Intégration

#### Sidebar (templates/base/sidebar.html)

Le lien recommandations est **maintenant actif** (non désactivé) :
```html
<li class="nav-item mb-1">
    <a class="nav-link d-flex align-items-center" href="{% url 'recommandations:liste' %}">
        <span class="nav-link-icon"><i class="bi bi-lightbulb"></i></span>
        <span class="nav-link-text">Recommandations</span>
    </a>
</li>
```

#### Dashboards (services/dashboard_service.py)

- **Admin** : affiche le total des recommandations du système
- **Agronome** : affiche le total des recommandations
- **Agriculteur** : affiche le nombre de ses recommandations

Les quick actions incluent un lien vers `/recommandations/`.

#### Modèle Agriculteur (utilisateurs/models.py)

```python
class Agriculteur(Utilisateur):
    def consulter_recommandations(self):
        """Retourne les recommandations destinées à l'agriculteur."""
        from services.recommandation_service import RecommendationService
        return RecommendationService.obtenir_recommandations_agriculteur(self)
```

## Permis d'accès

| Rôle | Liste | Détail | Historique | Génération |
|------|------|--------|-----------|-----------|
| Agriculteur | Ses seules | Ses seules | Ses seules | Auto |
| Agronome | Toutes | Toutes | Toutes | Auto |
| Admin | Toutes | Toutes | Toutes | Auto |

## Flux d'utilisation

### Consulter une recommandation (Agriculteur)

```
1. Agriculteur clique sur "Recommandations" dans la sidebar
2. Vue obtient ses recommandations via RecommendationService.obtenir_recommandations()
3. Service génère les recommandations manquantes pour ses cultures
4. Liste affichée avec type, date, culture
5. Clic sur "Voir" redirige vers le détail
6. Détail affiche le contenu complet de la recommandation
```

### Consulter l'historique

```
1. Agriculteur clique sur "Voir l'historique des recommandations"
2. Vue récupère l'historique complet via RecommendationService.historique()
3. Historique trié par date décroissante
4. Agriculteur peut revoir toutes les recommandations précédentes
```

## Tests

### Classes de test

- **RecommendationServiceTest** : tests de génération, récupération, historique
- **RecommendationViewsTest** : tests des vues et permissions
- **RecommendationIntegrationTest** : tests de l'intégration avec predictions/observations

### Cas d'essai clé

```bash
python manage.py test recommandations.tests
```

- ✓ Génération automatique de recommandation
- ✓ Récupération avec génération automatique si absente
- ✓ Une seule recommandation par culture par jour
- ✓ Les agriculteurs ne voient que leurs recommandations
- ✓ Les agronomes voient toutes les recommandations
- ✓ Les détails sont accessibles en tant qu'agriculteur
- ✓ L'historique fonctionne correctement
- ✓ Recommandation varie selon la prédiction
- ✓ Intégration avec les prédictions

## Documentation DB

### Schéma Recommandation

```sql
CREATE TABLE recommandations_recommandation (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    culture_id BIGINT NOT NULL,
    dateRecommandation DATE NOT NULL,
    type VARCHAR(100) NOT NULL,
    contenu LONGTEXT NOT NULL,
    UNIQUE(culture_id, dateRecommandation),
    INDEX(dateRecommandation),
    INDEX(culture_id),
    FOREIGN KEY(culture_id) REFERENCES cultures_culture(id)
);
```

## Déploiement

### Migrations

```bash
python manage.py makemigrations recommandations
python manage.py migrate recommandations
```

### Collecte des statiques

```bash
python manage.py collectstatic --noinput
```

## Notes développeur

### Extension future

Pour remplacer la logique provisoire par une IA :

1. Créer un fichier `recommandations/ia_engine.py`
2. Implémenter une classe `IARecommendationEngine`
3. Modifier `RecommendationService._calculer_recommandation()` pour utiliser le moteur IA
4. Tester l'intégration avec les cas d'essai existants

### Performance

- **Cache** : Envisager de cacher les recommandations du jour (le champ `unique_together` garde une par jour)
- **Génération massive** : Si besoin, créer une commande Django pour générer les recommandations la nuit
- **Requêtes** : Utiliser `select_related()` pour éviter les requêtes N+1

### Sécurité

- ✓ Vérification des permissions sur chaque vue
- ✓ Utilisation du décorateur `@login_required`
- ✓ Validation des données avec `full_clean()`
- ✓ Pas de modification manuelle des recommandations (lecture seule)

## Résumé des fichiers

```
recommandations/
├── models.py          # Modèle Recommandation
├── views.py           # Vues liste/détail/historique
├── urls.py            # Routes CU5
├── admin.py           # Admin Django
├── apps.py            # Configuration app
└── tests.py           # Tests complets

services/
└── recommandation_service.py  # Service récom + logique

utilisateurs/
└── models.py          # Méthode Agriculteur.consulter_recommandations()

services/
└── dashboard_service.py       # Intégration Dashboard CU5

templates/recommandations/
├── liste.html         # Listing
├── detail.html        # Détail
└── historique.html    # Historique
```

## Maintenance

- Voir `docs/services.md` pour l'architecture générale des services
- Voir `docs/architecture.md` pour le flux d'intégration
- Voir `README.md` pour les instructions de démarrage
