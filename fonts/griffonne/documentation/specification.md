# Spécification — Griffonne

Valeurs en unités sur un cadratin de 1000. Source de vérité dans le code : `sources/generateur/glyphes.py` (METRIQUES) et `pinceau.py` (Reglages).

## Décisions
| Paramètre | Valeur | Justification |
|---|---|---|
| Hauteur d'x | 540 | lisible dès 16 px |
| Capitale | 720 | rapport 0,75, lettres rondes |
| Ascendante / descendante | 760 / −230 | l plus haut que I |
| Dépassement des rondes | 12 | correction optique |
| Fût | 92 (0,17 × hauteur d'x) | presque le double de Cat, tient en petit et sur fond sombre |
| Contraste | ≈ 1,15 | pinceau rond, le caractère vient de la texture |
| Boîte de ligne | 985 / −265, interligne 0 (typo = hhea) | couvre le glyphe le plus haut (ĺ 980) ; (985 − 265) / 2 = 360 = capitale / 2 : capitales centrées dans les boutons (mesuré : −0,2 px encre comprise, corps des capitales ≈ 1 px plus bas à cause des oreilles) ; interlignage par défaut 1,25 |
| Texture | ±10 unités, ondes 190 · 330 · 540, points tous les 60 | texture B validée : invisible à 16 px, visible dès 96 px |
| Pression | ±8 %, ondes 320 · 560 | variation lente de l'épaisseur |
| Goutte | +8 % en fin de trait | le pinceau qui se pose |

## Formes distinctives
- I avec courtes barres ; l à queue de chat ; 1 à drapeau.
- d à queue en bas à droite ; q à queue descendante enroulée.
- a à deux étages ; g à un étage.
- 0 plus étroit que O ; `zero` barré en option.
- ' droite, ’ en goutte.
- Niveau félin par défaut : **marqué** (choix validé). Règle : **chaque lettre porte un élément de chat** —
  - panses = visages (oreilles et yeux) : o p q g c (tête qui ouvre la bouche) ; e : oreilles seules (E2) ; a : deux étages, oreilles de panse sur le crochet et petits yeux dans le ventre — le a entier est la tête du chat ; b d : oreilles sur la hampe et yeux dans la panse ;
  - oreilles au sommet des hampes et des fûts (h k l f t, n m r u) et du premier trait des diagonales (v w x y z) ; s : oreilles sur la courbe haute ;
  - queues : a l t u d q, descendante du y ; têtes de chat sur les points du i et du j.
  - Capitales (module `capitales.py`) : oreilles au sommet du premier fût (B D E F H K L N P R U), du A, du T et du I ; visages dans C G O Q ; yeux dans les boucles de B D P R ; queues sur J L Q ; oreilles sur le premier trait de M V W X Y Z et sur le haut du S. Oreilles à l'échelle 1,3 (sinon elles se lisent comme des cornes).
  - Oreilles assez grandes pour se lire dès 32 px (± 52, + 62 au-dessus de la hauteur). Réglage : `NIVEAU_FELIN` dans `glyphes.py`.
- Point d'attention : à 32 px sur fond sombre, les yeux chargent les panses. Pour les paragraphes, le style « Texte » (amplitude 0, niveau lisible) reste disponible si besoin.

## Chiffres et ponctuation
- Chiffres alignés **et tabulaires par défaut** (chasse commune 600) : les colonnes s'alignent sans `tnum`. Hauteur 700, sous la capitale.
- Règle unique pour les chiffres (validée) : la même paire d'oreilles, centrée sur le point le plus haut de chaque chiffre, 0 compris. Le 0 reste plus étroit que le O et sans yeux (O/0 : 16 %). Réglage : `CHAT_CHIFFRES` dans `chiffres.py`.
- Ponctuation sans chat, pour se reconnaître immédiatement ; ’ et “ ” en goutte de pinceau, distincts de ' et " droits ; espace fine insécable U+202F (125).

## Accents
- 14 diacritiques combinants (module `diacritiques.py`), chacun décliné en minuscule, `.case` (plus bas et aplati) et isolé.
- Ancre `top` calculée sur le dessin : au-dessus de ce qui dépasse dans la largeur de l'accent (± 90). Les oreilles sous l'accent le font monter (é, ô), celles d'à côté non (É, ñ).
- Caron en apostrophe pour ď ť ľ Ľ ; `.case` aussi pour les minuscules hautes (ĺ).
- Composés automatiquement : 145 accentuées de GF_Latin_Core. Typographie française complète (œ æ Œ Æ dessinés).
- Point de vigilance : Á Í Ó Å culminent vers 960 (accent au-dessus d'oreilles centrées) ; interlignage serré vérifié sans collision.

## Lettres spéciales (module `lettres_speciales.py`)
- Dérivées d'une lettre existante, chat compris (retoucher la source retouche la dérivée) : ø Ø ł Ł đ Đ Ð ħ Ħ, þ (p à fût long).
- Redessinées : ð (yeux dans la panse), Þ, ß et ẞ à ventre ouvert, loin du fût, pour ne pas lire un B (ß/B 56 %, ẞ/B 61 %).
- ª º : a et o réduits (× 0,58), surélevés et soulignés.

## Symboles (module `symboles.py`)
- Sans chat, comme la ponctuation : reconnaissance immédiate (e-mail, code).
- Opérateurs et devises en chasse de chiffre (600), centrés sur l'axe mathématique 340.
- ¡ ¿ = ! ? retournés (transformer, échelle -1).
- GF_Latin_Core couvert à 100 %. Font Bakery check-universal : 0 échec, 4 avertissements (contours des oreilles, voulu ; pas encore de crénage ; À à 959 > ascendante typo 950 ; segments superposés à examiner).

## Espacement et crénage
- Espacement optique (`scripts/espacer.py`) calibré sur la spécification : n 70 / o 50, H 70 / O 50 ; profondeur maximale calculée (50 minuscules, 75 capitales). 72 lettres dessinées réglées (a : 114 → 47 à gauche ; l : 13 → 38 à droite).
- Crénage mesuré (`scripts/crener.py`) : 400 paires de classes ; paires normales à 0 (oo, co) ; AV −66, To −140, Va −52, LT −65, ’s −62 ; ponctuation bornée à −100 (L’été lisible).
- Ordre de construction : générateur → espacer → composer_accents → crener → construire (README).
- Font Bakery : 0 échec, 2 avertissements restants (contours des oreilles, voulu ; segments superposés à examiner).

## Chats (`ss01`, dès 32 px)
Le niveau marqué étant déjà par défaut, `ss01` ajoute les chats complets : moustaches, corps assis dans les rondes, queues sur les capitales (J, L, Q). Yeux ≥ 0,5 × fût.

## Jeu de glyphes et fonctions
GF_Latin_Core. Fonctions réalisées (vérifiées avec HarfBuzz et dans Chromium) :
- `calt` : 3 tracés par lettre (graines différentes), boucle à 3 temps, accentuées comprises ; 221 lettres.
- `ss01` « Chats complets » : moustaches sur les 29 lettres à visage (et leurs accentuées) ; remplace aussi les alternances ; limite connue : pas d'alternance à l'intérieur de ss01.
- `case` : 14 signes remontés au centre des capitales. `zero` : zéro barré.
- `kern`, `mark`, `mkmk` générées au build. `tnum` inutile (chiffres tabulaires par défaut). `locl` turc abandonné : la conversion i → İ est faite par le logiciel (`lang="tr"`), sans petites capitales il n'apporte rien.
- Poids : 858 glyphes, WOFF2 123 Ko (budget 200 Ko).

## Méthode
Générateur Python : squelette → épaisseur, pression, bruit lissé → union. Graine = nom du glyphe (crc32).

## Budget
WOFF2 < 200 Ko au total, mesuré à chaque jalon (le plafond par glyphe est abandonné : 30 à 100 segments selon le nombre de traits).

## Alternative plus sobre
Même générateur avec amplitude 0 : style « Texte » monolinéaire.
