# Gestion des utilisateurs

## Objectif

Ce document décrit la gestion des utilisateurs par l'administrateur (CU6).
L'objectif est de permettre à un administrateur de créer, modifier, supprimer,
rechercher et filtrer les comptes utilisateurs depuis l'interface.

## Concepts clés

- Le projet utilise un modèle utilisateur custom `utilisateurs.models.Utilisateur`.
- Trois sous-classes concrètes représentent les profils métier :
  - `Administrateur`
  - `Agronome`
  - `Agriculteur`
- Le type réel d'un utilisateur est déterminé par la présence d'une ligne de sous-classe.
- Aucune modification de schéma n'a été nécessaire pour CU6.
- La logique métier est centralisée dans `services/utilisateur_service.py`.

## Fonctionnalités implémentées

### Liste des utilisateurs

- Route : `/utilisateurs/`
- Vue : `utilisateurs.views.liste_utilisateurs`
- Filtrage :
  - recherche libre sur email, username, prénom, nom
  - type de profil (`administrateur`, `agronome`, `agriculteur`, `utilisateur`)
  - statut actif / inactif

### Création d'un utilisateur

- Route : `/utilisateurs/ajouter/`
- Vue : `utilisateurs.views.creer_utilisateur`
- Formulaire : `utilisateurs.forms.UtilisateurForm`
- Données gérées :
  - email
  - username
  - prénom
  - nom
  - type de profil
  - mot de passe
  - statut actif

### Modification d'un utilisateur

- Route : `/utilisateurs/modifier/<id>/`
- Vue : `utilisateurs.views.modifier_utilisateur`
- Comportements spécifiques :
  - le mot de passe est facultatif, il n'est modifié que s'il est saisi
  - l'administrateur connecté ne peut pas se retirer lui-même du rôle admin
  - l'administrateur connecté ne peut pas désactiver son propre compte

### Suppression d'un utilisateur

- Route : `/utilisateurs/supprimer/<id>/`
- Vue : `utilisateurs.views.supprimer_utilisateur`
- Protection : l'administrateur connecté ne peut pas supprimer son propre compte.

## Architecture et implémentation

### services/utilisateur_service.py

Ce service expose les méthodes suivantes :

- `obtenir_type(utilisateur)` : retourne le type réel du compte
- `obtenir_utilisateurs(parametres)` : liste filtrée des utilisateurs
- `creer_utilisateur(formulaire)` : crée un compte et lui assigne un profil
- `modifier_utilisateur(formulaire, utilisateur)` : met à jour un compte et son profil
- `supprimer_utilisateur(utilisateur)` : supprime un compte
- `creer_administrateur(utilisateur)`, `creer_agronome(utilisateur)`, `creer_agriculteur(utilisateur)`

Le service maintient la cohérence entre le compte `Utilisateur`, les sous-classes de profil
et les groupes Django associés.

### utilisateurs/forms.py

`UtilisateurForm` encapsule la validation et la saisie des champs :

- email unique
- mot de passe obligatoire seulement à la création
- type de profil
- active / inactive

### utilisateurs/views.py

- Toutes les vues sont protégées par `@login_required`.
- L'accès est restreint aux administrateurs via `_verifier_administrateur()`.
- Les templates de la gestion utilisateur se trouvent dans `templates/utilisateurs/`.

## Templates

- `templates/utilisateurs/liste.html`
- `templates/utilisateurs/form.html`
- `templates/utilisateurs/supprimer.html`

## Points de validation

- Seul l'administrateur peut accéder aux pages utilisateurs.
- Les comptes utilisateurs peuvent être créés sans profil explicite de base,
  puis transformés en profil métier.
- La modification du type d'utilisateur reconstruit la sous-classe appropriée.
- La suppression d'un conseil lié au profil se fait sans reconstruction de schéma.

## Tests associés

- `python manage.py test utilisateurs`
- Les tests couvrent :
  - création de profil
  - assignation de groupe
  - détection de type utilisateur
  - accès aux vues pour administrateur / refus pour non-admin
  - création, modification et suppression via le formulaire admin

## Notes d'intégration

- Le menu administrateur contient désormais un lien `Utilisateurs`.
- Le dashboard administrateur propose une action rapide vers `/utilisateurs/`.
- Le routage est défini dans `utilisateurs/urls.py` et inclus depuis `gestion_agricole_intelligente/urls.py`.
