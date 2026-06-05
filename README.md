# Gestion Agricole Intelligente

Ce dépôt contient le cahier des charges de la solution de gestion agricole intelligente, écrit en LaTeX.

## Contenu du dépôt

- `Cahier_des_Charges_Gestion_Agricole_Intelligente.tex` : source principale du cahier des charges.
- `Cahier_des_Charges_Gestion_Agricole_Intelligente.pdf` : version compilée du cahier des charges.
- `Cahier_Analyse_Gestion_Agricole_Intelligente.tex` : cahier d'analyse lié au projet.
- `compile_cahier.sh` : script de compilation local.
- `README_compile_cahier.md` : documentation dédiée à la compilation du cahier.
- `images/` et `media/` : ressources utilisées par les documents.

## Objectif

Ce dépôt sert de point de départ pour :

1. définir le cahier des charges du projet,
2. documenter les choix fonctionnels et techniques,
3. préparer la suite avec le cahier de conception,
4. héberger l’implémentation logicielle future.

## Prérequis locaux

Pour compiler les documents en local, installez :

- un environnement TeX Live (`texlive`),
- `pdflatex`,
- `git`.

Sur une distribution Debian/Ubuntu :

```bash
sudo apt update
sudo apt install texlive-latex-recommended texlive-latex-extra texlive-fonts-recommended texlive-lang-french git
```

> `latexmk` n’est pas obligatoire pour le script fourni, mais peut être utile pour des compilations plus complètes.

## Compilation locale

1. Ouvrez un terminal dans le dossier du dépôt :

```bash
cd /mnt/dtamboudisk/Genie_logiciel
```

2. Rendez le script exécutable si nécessaire :

```bash
chmod +x compile_cahier.sh
```

3. Lancez la compilation du cahier des charges :

```bash
./compile_cahier.sh
```

4. Le PDF généré sera :

```bash
Cahier_des_Charges_Gestion_Agricole_Intelligente.pdf
```

### Compilation manuelle

Si vous voulez compiler manuellement sans le script :

```bash
pdflatex -interaction=nonstopmode -halt-on-error Cahier_des_Charges_Gestion_Agricole_Intelligente.tex
pdflatex -interaction=nonstopmode -halt-on-error Cahier_des_Charges_Gestion_Agricole_Intelligente.tex
```

### Nettoyer les fichiers auxiliaires

Pour supprimer les fichiers temporaires générés par LaTeX :

```bash
latexmk -C Cahier_des_Charges_Gestion_Agricole_Intelligente.tex
```

## Utilisation GitHub

### Initialiser le dépôt local

```bash
git init
git add .
git commit -m "Ajout du cahier de charges et de la documentation"
```

### Pousser vers GitHub

1. Créez un dépôt GitHub.
2. Ajoutez la remote :

```bash
git remote add origin https://github.com/<utilisateur>/<repo>.git
```

3. Poussez sur la branche principale :

```bash
git push -u origin main
```

### Workflow recommandé

- créez une branche pour chaque évolution :

```bash
git checkout -b feature/cahier-conception
```

- ajoutez les modifications :

```bash
git add .
```

- committez avec un message clair :

```bash
git commit -m "Ajout du cahier de conception et du plan d’implémentation"
```

- poussez la branche :

```bash
git push origin feature/cahier-conception
```

## Évolution future

Ce dépôt est conçu pour évoluer naturellement. Les prochaines étapes prévues sont :

- ajout du cahier de conception,
- définition de l’architecture logicielle,
- développement des sources de l’implémentation,
- tests et documentation technique.

## Bonnes pratiques

- versionnez surtout les sources `.tex`, les images et le script,
- évitez de pousser les fichiers temporaires LaTeX (`.aux`, `.log`, `.toc`, …),
- conservez les fichiers PDF générés seulement si vous souhaitez partager le résultat final.
