# Documentation du module Cultures

Ce document décrit le module `cultures` de l'application Gestion Agricole Intelligente.

## Objectif

Le module Cultures permet aux utilisateurs de gérer l'ensemble des cultures agricoles avec un parcours complet : création, consultation, modification, suppression, recherche, tri, filtrage et pagination.

## Architecture

Le module respecte l'architecture View → Service → Model :

- `cultures/views.py` expose les routes et récupère les données de l'utilisateur.
- `services/culture_service.py` contient toute la logique métier des cultures.
- `cultures/models.py` définit le modèle de données et effectue les validations métier.
- `cultures/forms.py` propose des ModelForms professionnels avec validation Bootstrap.

## Modèle Culture

Le modèle `Culture` contient les champs :

- `agriculteur` : clé étrangère vers `utilisateurs.Agriculteur`
- `nom` : nom de la culture
- `superficie` : surface en hectares
- `date_plantation` : date de plantation
- `localisation` : localisation physique de la culture
- `description` : texte libre
- `date_creation` et `date_modification`

### Validation métier

- `superficie` doit être strictement positive.
- `date_plantation` ne peut pas être dans le futur.
- Un agriculteur ne peut pas créer deux cultures portant le même nom.

## Services

### `CultureService`

Fonctions principales :

- `creer_culture(utilisateur, formulaire)`
- `modifier_culture(utilisateur, culture, formulaire)`
- `supprimer_culture(utilisateur, culture)`
- `obtenir_cultures(utilisateur, params)`
- `obtenir_culture(utilisateur, pk)`

### Fonctionnalités prises en charge

- Recherche par nom, localisation ou description.
- Filtrage par localisation et plage de dates de plantation.
- Tri par nom ou date.
- Pagination avec 10 résultats par page.
- Contrôle d'accès : un agriculteur ne voit que ses propres cultures.

## Pages du module

- `cultures:liste` — liste paginée des cultures
- `cultures:ajouter` — formulaire d'ajout de culture
- `cultures:detail` — détail d'une culture
- `cultures:modifier` — modification d'une culture
- `cultures:supprimer` — confirmation et suppression

## Tests

La couverture du module comprend :

- tests de service métier
- tests de formulaire
- tests de vues client
- tests de validation et permissions

## Flux utilisateur

1. L'utilisateur se connecte.
2. Il accède à la page `Cultures` depuis le menu.
3. Il peut rechercher, filtrer et trier les cultures.
4. Il peut ajouter une nouvelle culture.
5. Il peut consulter une culture et modifier/supprimer si autorisé.
6. La suppression demande confirmation.

## Améliorations

- Le tableau de bord utilise des cartes et des actions rapides.
- L'affichage est responsive et compatible mobile.
- Les erreurs sont affichées avec des messages clairs.
