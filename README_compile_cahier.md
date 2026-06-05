# Compilation du cahier des charges LaTeX

Ce fichier explique comment compiler proprement le document `Cahier_des_Charges_Gestion_Agricole_Intelligente.tex` et fournit un script prêt à l'emploi.

## Fichiers concernés

- `Cahier_des_Charges_Gestion_Agricole_Intelligente.tex`
- `Cahier_des_Charges_Gestion_Agricole_Intelligente.toc.clean`
- `Cahier_des_Charges_Gestion_Agricole_Intelligente.pdf` (généré)
- `compile_cahier.sh` (script de compilation)

## Prérequis

Le système doit disposer de :

- `pdflatex`
- une distribution TeX Live installée

> Le script `compile_cahier.sh` utilise `pdflatex` en deux passes.

## Commandes pour compiler

Ouvre un terminal dans le dossier `Genie_logiciel` puis exécute :

```bash
cd /mnt/dtamboudisk/Genie_logiciel
chmod +x compile_cahier.sh
./compile_cahier.sh
```

Le script accepte aussi un nom de fichier LaTeX en argument :

```bash
./compile_cahier.sh Cahier_Analyse_Gestion_Agricole_Intelligente.tex
```

## Que fait le script ?

1. Va dans le dossier du projet
2. Compile le fichier LaTeX avec `pdflatex` en deux passes
3. Génère le PDF dans le même dossier

## Commandes manuelles équivalentes

Si tu veux compiler sans le script :

```bash
cd /mnt/dtamboudisk/Genie_logiciel
latexmk -pdf -g Cahier_des_Charges_Gestion_Agricole_Intelligente.tex
```

### Variante manuelle sans `latexmk`

```bash
cd /mnt/dtamboudisk/Genie_logiciel
pdflatex -interaction=nonstopmode -halt-on-error Cahier_des_Charges_Gestion_Agricole_Intelligente.tex
pdflatex -interaction=nonstopmode -halt-on-error Cahier_des_Charges_Gestion_Agricole_Intelligente.tex
```

## Nettoyer les fichiers auxiliaires

Pour supprimer les fichiers temporaires générés par LaTeX :

```bash
latexmk -C Cahier_des_Charges_Gestion_Agricole_Intelligente.tex
```

Si vous n’avez pas `latexmk`, supprimez à la main les fichiers auxiliaires suivants :

- `*.aux`, `*.log`, `*.toc`, `*.out`, `*.synctex.gz`, `*.fdb_latexmk`, `*.fls`

## Résultat

Le PDF final est produit ici :

- `Cahier_des_Charges_Gestion_Agricole_Intelligente.pdf`

## Note

Si `latexmk` indique `Nothing to do`, cela signifie que le PDF est déjà à jour. Le flag `-g` force la recompilation complète.
