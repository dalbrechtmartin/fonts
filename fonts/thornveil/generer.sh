#!/usr/bin/env bash
# Régénère Thornveil de bout en bout : dessin, espacement, accents, crénage, fonctions OpenType, build, spécimen.
# Ordre imposé : le générateur réécrit les chasses, l'espacement dépend du dessin, le crénage de l'espacement,
# les composés des deux.
set -euo pipefail
cd "$(dirname "$0")"
python3 sources/generateur/thornveil.py sources/
REFERENCES=(--minuscules n:45 o:40 --capitales H:55 O:45)
for graisse in Light Regular Black; do
    ufo="sources/Thornveil-$graisse.ufo"
    python3 scripts/espacer.py "$ufo" "${REFERENCES[@]}"
    python3 scripts/composer_accents.py "$ufo" --jeu GF_Latin_Core --remplacer --variantes ss01 ss02 ss04 ss02.ss04
    python3 sources/generateur/composes_lettons.py "$ufo"
    python3 sources/generateur/sans_coulures_accents_bas.py "$ufo"
    python3 scripts/crener.py "$ufo" "${REFERENCES[@]}"
    python3 scripts/fonctions_opentype.py "$ufo" --nom-jeu ss01 "Capitales et chiffres coulants" \
        --nom-jeu ss02 "Épines renforcées" --nom-jeu ss04 "Minuscules coulantes"
    python3 sources/generateur/fonctions_locales.py "$ufo"
done
python3 scripts/construire.py sources/ --sortie fonts/
python3 scripts/finaliser_variable.py fonts/
# Spécimen, avec la mention à copier (facultative pour l'OFL, toujours appréciée)
python3 scripts/specimen.py fonts/webfonts/*.woff2 --nom "Thornveil" \
    --credit "Police Thornveil par Danaé ALBRECHT--MARTIN (https://danaedev.fr)"
