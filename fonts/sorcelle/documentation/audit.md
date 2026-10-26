# Audit — Sorcelle 0.6.0

Police existante à compléter : 132 caractères redessinés dans le style Sorcelle, 198 encore hérités de Jacquard 24.
Mesures complètes : [`audit-mesures.md`](audit-mesures.md) (`analyser_police.py` sur Jacquard 24, Sorcelle Regular et
Bold). Planche des glyphes hérités : [`images/audit-herites.png`](images/audit-herites.png).

## Comparatif

| Point | Jacquard 24 (origine) | Sorcelle 0.6.0 (redessiné) | Glyphes hérités dans Sorcelle |
| --- | --- | --- | --- |
| Classification | textura pixel (gothique) | lombarde arrondie pixel | textura pixel |
| Hauteur d'x | 17 px (0,68 de la capitale) | 17 px, conservée | 17 px |
| Ouvertures | fermées, fûts brisés | ouvertes, panses rondes | fermées |
| Contraste | 1,95 sur « o » | 1,95 (Regular), 2,95 (Bold) | celui de Jacquard, **identique dans les 3 graisses** |
| Terminaisons | losanges, pointes | crosses, empattements plats | losanges, pointes |
| Formes distinctives | a, g gothiques | a à deux étages, g à crochet ouvert, 0 barré, l à sortie | gothiques |
| Chasse | étroite, régulière | suit le dessin, + 1 ou 2 px par graisse | étroite, fixe |
| Lisibilité (OCR, 7 phrases) | 82 % | 99,6 % | non mesurée, visiblement plus faible |
| Confusions (seuil 85 %) | o / 0 : 86 %, u / n : 88 % | aucune (o / 0 : 52 %, u / n : 66 %) | — |
| Couverture | GF Latin Core 100 % | GF Latin Core 100 % | 187 des 319 caractères de GF Latin Core |
| Ce qui plaît | grille et hauteurs | lisible, mystérieux sans gothique | — |
| Ce qui gêne | gothique peu lisible | — | rupture de style franche : un « Ñ » ou un « € » dans un titre saute aux yeux |

## Inventaire des 198 glyphes hérités

| Groupe | Nombre | Exemples | Méthode prévue |
| --- | --- | --- | --- |
| Lettres accentuées | 143 | Á Ã Å Ñ Ø Č Ł Ő Ș ẞ ß Ŋ Ħ ı ȷ ĳ ª º | composées (base Sorcelle + accent Sorcelle), retouches à la main |
| Accents seuls | 15 + 12 combinants | ^ ˇ ˘ ˙ ˚ ˛ ˜ ˝ ¨ ¯ ´ ¸ ` | dessinés sur la planche |
| Symboles et ponctuation | 28 | $ € £ ¥ ¢ ° × ÷ ™ ® ¶ ¿ ¡ { } \ \| ~ • ‹ › “ ” „ ‘ ‚ − | dessinés sur la planche |

## Codes du genre à respecter

- Grille pixel stricte : tout est multiple de 30 unités, pixels nets à 43, 86 et 129 px.
- Accents des capitales dans la hauteur prévue par la planche (`ASC_PX` = 36 px) : aplatis plutôt que débordants.
- Signes de ponctuation au même poids que les lettres (points carrés de la ponctuation déjà redessinée).
- Symboles monétaires et ™ ® à hauteur de capitale ou de chiffre (23 px), lisibles d'abord.

## Espace libre

Une lombarde pixel lisible qui couvre vraiment l'Europe latine dans trois graisses : les polices pixel de titrage
s'arrêtent souvent au français ou gardent leurs accents en un seul poids.

## Risques repérés

1. **Graisses** : les glyphes hors planche ne sont pas épaissis par `build.py` ; SemiBold et Bold les affichent en
   Regular. Les mettre sur la planche règle le problème pour les 198.
2. **Diacritiques à distinguer** : virgule souscrite (Ș Ț, roumain) ≠ cédille (Ş Ţ, turc) ; caron en apostrophe sur
   ď ľ ť Ľ ; ogonek de Ą Ę ; barre de Ł, Đ, Ħ ; ẞ capitale ≠ ß.
3. **Place des accents sur les capitales** : Ő, Ǎ, Ẁ et les doubles accents doivent tenir sous l'ascendante
   (1 020 unités = 34 px) sans toucher la ligne du dessus.
4. **Fonctions héritées** : `kern` (29 paires de Jacquard 24) et `mark` (ancres de Jacquard 24) visent les formes
   d'origine. À refaire ou retirer quand les glyphes changent, sinon espacements et accents combinants mal placés.
5. **Métadonnées** : le nom de la créatrice (nameID 9) n'est pas renseigné.
6. **Licence** : dérivée de Jacquard 24 (OFL, sans nom réservé) ; garder le copyright d'origine à côté du mien, déjà
   fait.
