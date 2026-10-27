#!/usr/bin/env bash
# Régénère Tendrille de bout en bout : dessin et espacement, accents composés, variantes, fonctions OpenType, build.
set -euo pipefail
cd "$(dirname "$0")"
python3 sources/generateur/generateur.py sources/Tendrille-Regular.ufo
python3 sources/generateur/generateur.py sources/TendrilleTexte-Regular.ufo --sobre
for ufo in sources/*.ufo; do
    python3 scripts/composer_accents.py "$ufo" --jeu GF_Latin_Core --remplacer --variantes fina ss01 fina.ss01
    python3 sources/generateur/variantes_composees.py "$ufo" ss02
done
# Références d'espacement lues dans PARAMETRES : une valeur n'est écrite qu'à un seul endroit
read -r MIN_DROITE MIN_RONDE CAP_DROITE CAP_RONDE < <(python3 -c "
import sys; sys.path.insert(0, 'sources/generateur')
from generateur import PARAMETRES as p
print(p['approche'], p['approche_ronde'], p['approche_capitale'], p['approche_capitale_ronde'])")
REFERENCES=(--minuscules "n:$MIN_DROITE" "o:$MIN_RONDE" --capitales "H:$CAP_DROITE" "O:$CAP_RONDE")
# Tendrille : rn ne doit pas ressembler à m (écart voulu et mesuré, voir documentation/specification.md)
RN="${CRENAGE_RN:-30}"
# Tendrille : gestes effilés (crochet du f, entrées en délié) qui ne doivent pas se frôler : écart minimal 60
python3 scripts/crener.py sources/Tendrille-Regular.ufo "${REFERENCES[@]}" --ecart-minimal 60 \
    --ajout r n "$RN" --ajout r m "$RN" --ajout r u "$RN"
python3 scripts/crener.py sources/TendrilleTexte-Regular.ufo "${REFERENCES[@]}"
python3 scripts/fonctions_opentype.py sources/Tendrille-Regular.ufo \
    --nom-jeu ss01 "a d'école" --nom-jeu ss02 "Points ronds" \
    --nom-jeu ss04 "Capitales à cœur" --nom-jeu ss05 "Sans rubans de fin de mot"
python3 scripts/fonctions_opentype.py sources/TendrilleTexte-Regular.ufo \
    --nom-jeu ss01 "a d'école" --nom-jeu ss02 "Points en cœur"
# Statiques : traits fusionnés et nettoyés dans une copie (les sources gardent un contour par trait)
python3 sources/generateur/statiques.py sources/ build/statiques/
python3 scripts/construire.py build/statiques/ --sortie fonts/
# Spécimen, avec la mention à copier (facultative pour l'OFL, toujours appréciée)
python3 scripts/specimen.py fonts/webfonts/Tendrille-Regular.woff2 fonts/webfonts/TendrilleTexte-Regular.woff2 \
    --nom "Tendrille" --credit "Police Tendrille par Danaé ALBRECHT--MARTIN (https://danaedev.fr)" \
    --texte "❦ Tout va bien. Le fleuve, la forêt et l’été : « Voyez ! » dit Yvon à Paul. ❧"
