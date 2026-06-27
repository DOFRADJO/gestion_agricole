# CU3 — Observations

This document describes the Observations module (CU3): model, services, forms, views, templates, URLs, permissions and tests.

## Objectif

Le module Observations permet d'enregistrer des relevés liés à une `Culture` (phénologie, ravageur, maladie, météo, etc.), d'ajouter des commentaires et des photos, et de consulter/filtrer les observations.

## Modèle `Observation`

Champs principaux (voir `observations/models.py`):

- `culture` (ForeignKey → `cultures.Culture`) : culture observée.
- `observateur` (ForeignKey → `utilisateurs.Utilisateur`, nullable) : auteur de l'observation.
- `type` (CharField, choix) : type d'observation (phénologie, ravageur, maladie, météo, autre).
- `valeur` (DecimalField, optionnel) : valeur numérique associée (ex. : densité, mesure).
- `commentaire` (TextField) : texte libre.
- `photo` (ImageField, optionnel) : photo de l'observation (upload vers `media/observations/`).
- `date_observation` (DateTimeField) : date et heure de l'observation (par défaut maintenant).
- `date_creation`, `date_modification` (DateTimeField automatiques)

Contraintes métier:
- `date_observation` ne peut pas être dans le futur (validée dans `clean()`).

## Service `ObservationService`

Fichier: `services/observation_service.py`

API principal:
- `creer_observation(utilisateur, formulaire)` — crée une observation; assigne `observateur` si absent.
- `modifier_observation(utilisateur, observation, formulaire)` — modifie si permissions valides.
- `supprimer_observation(utilisateur, observation)` — supprime si permissions valides.
- `obtenir_observation(utilisateur, pk)` — récupère l'observation (permission check simple).
- `lister_observations(utilisateur, params)` — liste paginée avec filtres (`culture`, `type`, `date_debut`, `date_fin`).

Permissions (implémentées de façon conservatrice):
- `administrateur` et `agronome` peuvent modifier/supprimer.
- `agriculteur` peut visualiser les observations liées à ses cultures.

Remarques d'implémentation:
- Les vues restent fines et délèguent la logique aux services.
- Les requêtes utilisent `select_related` pour optimiser les jointures.

## Formulaires

Fichier: `observations/forms.py`

- `ObservationForm` — ModelForm pour `Observation`.
- Widget `date_observation` est rendu en `datetime-local` (compatible HTML5) et les valeurs d'instance sont préformatées en `YYYY-MM-DDTHH:MM`.
- Validation: `clean_date_observation` empêche les dates futures.

## Vues et URLs

Vues implémentées (convention similaire à `cultures`):
- `liste_observations` — liste + pagination + filtres.
- `ajouter_observation` — création (POST avec `multipart/form-data`).
- `consulter_observation` — détail.
- `modifier_observation` — édition.
- `supprimer_observation` — confirmation puis suppression.

URLs (fichier `observations/urls.py`):

```
path('', views.liste_observations, name='liste')
path('ajouter/', views.ajouter_observation, name='ajouter')
path('<int:pk>/', views.consulter_observation, name='detail')
path('<int:pk>/modifier/', views.modifier_observation, name='modifier')
path('<int:pk>/supprimer/', views.supprimer_observation, name='supprimer')
```

Le projet inclut `observations.urls` dans le fichier principal `gestion_agricole_intelligente/urls.py` sous le préfixe `/observations/`.

## Templates

Chemin: `templates/observations/`

- `_form.html` — partial de rendu du formulaire.
- `ajouter.html`, `modifier.html` — formulaires pour create/edit.
- `liste.html` — tableau paginé d'observations, actions (Voir/Modifier/Supprimer).
- `detail.html` — page de détail (affiche photo si présente).
- `supprimer.html` — confirmation de suppression.

Les templates réutilisent les composants existants (`components/breadcrumb.html`, `components/pagination.html`) et le layout global (`base/base.html`).

## Tests

Fichier: `observations/tests.py`

- Tests de modèle: création et représentation string.
- Tests des vues: accès restreint aux utilisateurs non authentifiés, agronome peut ajouter.

Commande pour lancer les tests du module:

```bash
DB_ENGINE=django.db.backends.sqlite3 DB_NAME=:memory: SECRET_KEY='test' DEBUG=True ALLOWED_HOSTS=localhost python manage.py test observations -v2
```

## Migrations

Après l'ajout de l'app, générer et appliquer les migrations:

```bash
python manage.py makemigrations observations
python manage.py migrate
```

## Ajouts côté UI

- Le menu `Observations` a été activé dans `templates/base/sidebar.html` et pointe sur `observations:liste`.
- Le `DashboardService` utilise désormais le compte d'observations pour afficher une statistique dans le dashboard.

## Guide d'utilisation rapide

1. Connectez-vous en tant qu'`agronome` ou `administrateur`.
2. Ouvrez le menu `Observations`.
3. Cliquez sur `Nouvelle observation` pour ajouter un relevé (joindre une photo si besoin).
4. Utilisez les filtres pour limiter par culture / type / plage de dates.

## Points d'amélioration futurs

- Permissions plus fines (ex. : rôles et politiques basées sur objets).
- API REST pour Observations (Django REST Framework).
- Thumbnails pour les photos et nettoyage des fichiers supprimés.
- Tests supplémentaires pour les règles de permission et les cas d'erreur.
