# Documentation du module Prédictions

## Objectif CU4

Le module Prédictions permet aux agriculteurs, agronomes et administrateurs de consulter les prédictions de rendement générées automatiquement à partir des observations des cultures.

Le système ne permet pas de créer, modifier ou supprimer manuellement une prédiction.

## Modèle `Prediction`

Fichier : `predictions/models.py`

Champs :

- `idPrediction` (clé primaire automatique)
- `datePrediction` (DateField) : date de génération de la prédiction
- `rendementEstime` (FloatField) : rendement estimé en t/ha
- `niveauConfiance` (FloatField) : niveau de confiance entre 0.0 et 1.0
- `culture` (ForeignKey → `cultures.Culture`) : culture associée
- `commentaires` (TextField) : annotations internes du service de prédiction

Contraintes métier :

- `datePrediction` ne peut pas être dans le futur
- `rendementEstime` doit être supérieur ou égal à 0
- `niveauConfiance` doit être compris entre 0.0 et 1.0

## Service `PredictionService`

Fichier : `services/prediction_service.py`

Méthodes principales :

- `generer_prediction(culture)` : génère ou met à jour la prédiction pour une culture
- `obtenir_prediction(culture)` : retourne la prédiction la plus récente pour une culture, en la générant automatiquement si nécessaire
- `obtenir_predictions_agriculteur(utilisateur)` : retourne les prédictions actuelles des cultures d'un agriculteur
- `obtenir_predictions(utilisateur)` : retourne les prédictions accessibles à l'utilisateur
- `recalculer_prediction(culture)` : force la génération d'une nouvelle prédiction
- `historique(utilisateur, culture=None)` : retourne l'historique des prédictions accessibles

### Architecture évolutive

Le service isole le calcul de la prédiction dans une méthode dédiée (`_calculer_prediction`).
Cela permet de remplacer simplement l'algorithme provisoire par un modèle IA ultérieur sans modifier les vues ou les templates.

### Algorithme provisoire

L'algorithme actuel est volontairement simple :

- sans observation, il produit une prédiction provisoire basée sur l'âge de la culture
- avec des observations, il calcule un rendement estimé à partir du nombre d'observations et de l'ancienneté de la culture
- le niveau de confiance augmente avec le nombre d'observations et l'ancienneté

Ce calcul est documenté dans `services/prediction_service.py` comme preuve de concept, et il est remplacera un futur modèle IA.

## Vues et URLs

Vues :

- `liste_predictions` : liste des prédictions actuelles
- `detail_prediction` : détail d'une prédiction
- `historique_predictions` : historique des prédictions générées

URLs :

- `/predictions/` → liste
- `/predictions/historique/` → historique
- `/predictions/<pk>/` → détail

## Permissions

- Agriculteur : consulte uniquement ses propres prédictions
- Agronome : consulte toutes les prédictions
- Administrateur : consulte toutes les prédictions si cela est utile à l'administration

## Intégration UI

- Ajout du lien `Prédictions` dans le menu latéral
- Mise à jour du dashboard avec le nombre de prédictions et un accès rapide
- Réutilisation complète du layout existant, des cartes Bootstrap et du style actuel

## Tests

Les tests couvrent :

- génération automatique des prédictions
- consultation des prédictions
- historique des prédictions
- permissions par rôle
- liaison Culture → Observation → Prediction

## Travaux futurs

- remplacer `_calculer_prediction` par un moteur IA ou un modèle de machine learning
- ajouter un calcul de score plus riche à partir des observations structurées
- introduire des métriques de performance et des audits de génération
