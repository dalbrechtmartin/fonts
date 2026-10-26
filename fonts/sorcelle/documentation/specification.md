# Spécification — Sorcelle 0.7 et 1.0

Objectif : passer les 198 glyphes hérités de Jacquard 24 au style Sorcelle, dans les trois graisses
([brief](brief.md), [audit](audit.md)). Les valeurs déjà validées en 0.6 ne changent pas ; elles sont rappelées pour
servir de règle aux nouveaux glyphes. Unité de dessin : le pixel de la planche (1 px = 30 unités).

## Décisions

| Paramètre | Valeur | Justification |
| --- | --- | --- |
| Unités par cadratin | 1 290 (inchangé) | grille de Jacquard 24 : 1 px = 30 unités, pixels nets à 43, 86 et 129 px |
| Hauteur d'x | 17 px (510) | conservée (audit) |
| Hauteur de capitale et des hampes | 25 px (750) | conservée |
| Hauteur des chiffres | 23 px | déjà validée en 0.6 (un peu sous les capitales) |
| Ascendante / descendante | 1 020 / −270 (34 / −9 px) | inchangées ; couvrent les capitales accentuées (accent le plus haut : 33 px) |
| Boîte de ligne | typo = hhea, interligne 0 | (1 020 − 270) / 2 = 375 = capitale / 2 : capitales déjà centrées au pixel |
| Fût capitales / minuscules | 5 px / 4 px | style validé en 0.6 |
| Délié | 2 px | idem |
| Graisses | +0, +1, +2 px vers la droite | `build.py` ; s'appliquera aux 198 glyphes une fois sur la planche (risque 1 de l'audit) |
| Approche gauche | 1 px (`normalise`) | règle des scripts de dessin existants |

## Accents

Zone des accents, mesurée sur les accents français déjà en place :

| | Lignes occupées | Hauteur max | Écart avec la lettre |
| --- | --- | --- | --- |
| Capitales | 27 à 32 | 6 px | 2 px au-dessus de la capitale |
| Minuscules | 21 à 26 | 6 px | 4 px au-dessus de l'x |
| Sous la ligne de base | −1 à −6 | 6 px | collé à la lettre |

- **Gardés tels quels** (validés en 0.6) : aigu et grave (5 × 6 px), circonflexe (6 × 10), tréma (4 × 10), cédille (6 × 5).
- **À dessiner, mêmes gabarits** : caron (circonflexe retourné), brève, point (2 × 2, comme les points de ponctuation),
  rond (4 × 4 creux), tilde (3 × 8), macron (2 × 8), double aigu (deux aigus serrés, 10 px de large), ogonek (sous la
  ligne, accroché à droite), virgule souscrite (forme de la virgule, 4 px), caron en apostrophe (forme de ’, à droite
  de ď ľ ť Ľ).
- **Capitales** : mêmes accents, posés sur les lignes 27 à 32. Pas de variante `.case` plus plate : 6 px tiennent déjà
  sous l'ascendante.
- **Barres et barres obliques** : Ł ł (oblique 2 px au milieu du fût), Đ đ Ħ ħ (barre horizontale 2 px), Ø ø (oblique
  qui traverse la panse, comme le 0 barré).

## Jeu de glyphes et points délicats (GF Latin Core)

| Lot | Glyphes | Règle |
| --- | --- | --- |
| Composées simples | Á Ã Å Ā Ă Ą Ć Ċ Č Ď Ē Ė Ę Ě Ğ Ġ Ģ Ī Į İ Í Ì Ķ Ĺ Ļ Ľ Ń Ņ Ň Ñ Ó Ò Õ Ō Ő Ŕ Ŗ Ř Ś Ş Š Ș Ť Ţ Ț Ú Ū Ŭ Ů Ű Ų Ŵ Ẁ Ẃ Ẅ Ŷ Ý Ỳ Ź Ż Ž et leurs minuscules | lettre Sorcelle + accent, centré sur la lettre |
| Roumain | Ș ș Ț ț | virgule souscrite, jamais la cédille (≠ Ş ş du turc) |
| Letton | Ķ ķ Ļ ļ Ņ ņ Ŗ ŗ, ģ | virgule souscrite (malgré la décomposition Unicode en cédille) ; ģ : virgule retournée au-dessus |
| Tchèque et slovaque | ď ľ ť Ľ | caron en apostrophe à droite, sans élargir la lettre plus que nécessaire |
| Turc | İ, ı | ı existe déjà (base de î ï) ; İ = I + point. `locl` de Jacquard gardé (i → İ en capitales turques) |
| Lettres à barre | Đ đ Ð Ħ ħ Ł ł Ø ø | barres de 2 px ; Ð = Đ (même dessin, deux codes) |
| À dessiner entières | ß ẞ ð Þ þ Ŋ ŋ ȷ IJ ij ª º | ß et ẞ distincts ; ð (eth islandais) ≠ đ : panse ronde, hampe courbe barrée ; ȷ = j sans point ; IJ ij en ligature serrée ; ª º = a et o en exposant, soulignés |
| Accents seuls | ^ ` ¨ ¯ ´ ¸ ˆ ˇ ˘ ˙ ˚ ˛ ˜ ˝ et 15 combinants (U+0300…) | mêmes dessins que sur les lettres ; combinants en chasse nulle, placés pour une minuscule |

## Symboles et ponctuation (jalon 1.0)

| Glyphes | Règle |
| --- | --- |
| $ € £ ¥ ¢ | hauteur des chiffres (23 px) ; barres de 2 px qui dépassent de 2 px en haut et en bas pour $ ; € sur le C rond |
| ° | rond creux 6 × 6, en haut des chiffres |
| × ÷ − | même ligne et même largeur que + et = déjà dessinés ; − de la largeur du + |
| ™ ® | ™ : T et M en petites capitales de 9 px en haut ; ® : même anneau que © avec un R |
| ¡ ¿ | ! et ? retournés, qui descendent sous la ligne de base (convention espagnole) |
| “ ” „ ‘ ‚ ‹ › | tirés de ’ , « » déjà dessinés (même poids, mêmes points carrés) |
| { } \ \| ~ ¶ · • | même hauteur que ( ) [ ] ; · et • : points carrés de 2 px et 4 px à mi-hauteur d'x |

## Fonctions OpenType

| Fonction | Décision | Justification |
| --- | --- | --- |
| `kern` | supprimer les 29 paires de Jacquard 24 | elles visent les anciennes formes ; l'espacement suit déjà le dessin (approche 1 px). Crénage à refaire à l'étape d'espacement si une paire le demande |
| `mark` | regénérer : ancre en haut au centre de chaque lettre, centre bas de chaque accent combinant | les ancres de Jacquard placent mal les accents combinants sur les nouvelles lettres |
| `ccmp`, `locl` | garder | substitutions par noms de glyphes, valables quel que soit le dessin |
| `case`, `tnum`, `zero`, `frac`, `GRAD` | sans objet | police de titrage, chiffres alignés et 0 déjà barré par défaut |

## Méthode de dessin et outils

- Même chaîne qu'en 0.6, sans nouvel outil : scripts Python qui dessinent pixel par pixel sur `planche.png`, puis
  `build.py`. La composition par ancres de l'outillage UFO (`composer_accents.py`) ne s'applique pas à une police pixel.
- `grid.CHARSET` : les nouveaux caractères sont **ajoutés à la fin**, pour que les cases existantes ne bougent pas
  (retouches Aseprite conservées).
- Nouveau script `design_accents.py` : dessine les accents, puis compose chaque lettre accentuée à partir des lettres
  de la planche (lit les pixels déjà dessinés, donc tient compte des retouches). Les cas délicats ci-dessus sont des
  règles du script, retouchables ensuite dans Aseprite.
- Nouveau script `design_symboles.py` (jalon 1.0) pour les 28 symboles.
- `build.py` : retire `kern`, regénère `mark`, renseigne le nom de la créatrice (nameID 9).
- Contrôle après chaque lot : planche Regular et Bold à 43 et 86 px, clair et sombre, et OCR (`legibility.py`).

## Alternative plus sobre

Pas de piste audacieuse ici : on prolonge un style validé. Pour aller plus vite, on peut ne dessiner que les lettres
utiles au français et à l'Europe de l'Ouest (≈ 40 glyphes) et laisser le reste en Jacquard 24, mais la rupture de style
de l'audit resterait visible dans les autres langues.
