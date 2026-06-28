# Pipeline de déploiement et CI

Ce document décrit un pipeline GitHub Actions pour automatiser les tests et préparer le paquet de déploiement.

## 1. Objectif

- Valider le code automatiquement.
- Exécuter les tests Django.
- Construire un artefact de déploiement prêt à être importé sur o2switch.

## 2. Workflow GitHub Actions

Le workflow se déclenche sur :

- `push` sur `main`
- `pull_request`

Il exécute :

1. `pip install -r requirements.txt`
2. `python manage.py check`
3. `python manage.py test`
4. `python manage.py collectstatic --noinput`
5. création d'un ZIP de déploiement depuis le dossier `gestion_agricole_intelligente`

## 3. Artefact de déploiement

L'artefact `gagri-deploy.zip` contient le code source du dossier `gestion_agricole_intelligente` prêt à être déployé sur o2switch.

## 4. Limitation o2switch

o2switch ne propose pas toujours un déploiement Git direct. Le pipeline automatise la qualité et la création du paquet, mais l'envoi final vers o2switch reste généralement manuel via l'interface de l'hébergeur.

## 5. Améliorations futures

- Ajouter des tests unitaires supplémentaires.
- Ajouter un contrôle de style (`ruff`, `flake8`).
- Publier des versions via GitHub Releases.
