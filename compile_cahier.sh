#!/bin/bash
set -e

cd /mnt/dtamboudisk/Genie_logiciel

SOURCE_FILE="${1:-Cahier_des_Charges_Gestion_Agricole_Intelligente.tex}"
OUTPUT_FILE="${SOURCE_FILE%.tex}.pdf"
LOG_PREFIX="/tmp/compile_$(basename "${SOURCE_FILE%.*}")"

if [ ! -f "$SOURCE_FILE" ]; then
  echo "Erreur : le fichier source LaTeX '$SOURCE_FILE' est introuvable."
  exit 1
fi

echo "Compilation de '$SOURCE_FILE'..."
echo ""

echo "Passe 1 : génération de la structure..."
pdflatex -interaction=nonstopmode -halt-on-error "$SOURCE_FILE" > "${LOG_PREFIX}_1.log" 2>&1

echo "Passe 2 : intégration de la table des matières..."
pdflatex -interaction=nonstopmode -halt-on-error "$SOURCE_FILE" > "${LOG_PREFIX}_2.log" 2>&1

echo ""
echo "✓ Compilation terminée avec succès"
echo "✓ Fichier généré : $OUTPUT_FILE"
echo "Logs de compilation : ${LOG_PREFIX}_1.log, ${LOG_PREFIX}_2.log"