# Spécification — Thornveil

Police de titrage pour logos : elle s'écarte des repères « texte et interface » (espacement serré, contraste fort), ce que justifie le brief. Les valeurs d'espacement sont des points de départ : `espacer.py` les recalcule.

## Décisions (chacune avec sa justification)

| Paramètre | Valeur | Justification (brief, règle ou mesure) |
|---|---|---|
| Unités par cadratin | 1000 | standard |
| Hauteur d'x | 520 | grande, pour rester lisible en favicon (brief) ; rapport 0,74 dans la fourchette des étalons (0,71–0,78, audit) |
| Hauteur de capitale | 700 | rapport hauteur d'x / capitale 0,74 (audit) |
| Ascendante / descendante | 770 / −230 | ascendantes au-dessus des capitales, code du genre ; descendantes courtes pour composer des logos compacts |
| Dépassement | 12 sur les pointes de losange, 10 sur les courbes | correction optique |
| Angle de plume | 40° | gothique à plume large, axe incliné (images 1, 2) |
| Fût bas de casse (wght 300 / 400 / 900) | 80 / 100 / 200 | 400 = 0,19 × hauteur d'x, comme les étalons (0,19–0,21) ; 900 pour les logos massifs (image 1) ; 400 obtenu par interpolation, sans table avar |
| Fût capitale | fût bas de casse × 1,08 | les capitales paraissent sinon plus maigres |
| Délié de construction (300 / 900) | 30 / 50 | jamais sous 30 : environ 1 px à 32 px, le favicon reste lisible |
| Délié d'ornement (épines, paraphes) (300 / 900) | 18 / 26 | presque constant d'une graisse à l'autre : garde le caractère ciselé (images 1, 2) ; réservé aux grandes tailles |
| Contrepoinçon de n (blanc entre fûts) | 1,4 × fût | plus ouvert que la textura classique (≈ 1 × fût) : limite l'effet « palissade » et la confusion n/u (audit) |
| Approche de base (fût / losange) | 45 / 35 | serrée pour le titrage, recalculée par `espacer.py` |
| Épines par défaut | une par lettre ; fines (base ≈ 2,5 × délié d'ornement + 0,1 × fût), courbes, pointe recourbée vers le haut ; longueur 120 (wght 300) à 155 (wght 900) ; vers la gauche, sauf n (et lettres à épaule) vers la droite. Règle des hauteurs : épine droite à 70 % de la hauteur du fût, épine gauche à 45 % | demande de Danaé ; deux épines voisines ne se font jamais face ; l'épine à droite du n garde n/u distincts (34 %) |
| Boîte de ligne (typo = hhea, interligne 0) | 1000 / −300 | couvre les capitales accentuées ; (1000 − 300) / 2 = 350 = capitale / 2 : capitales centrées en CSS ; interlignage 1,3 |

## Formes distinctives

| Lettres | Décision | Pourquoi |
|---|---|---|
| n / u | n : épaule anguleuse, épine à droite ; u : délié en bas, épine à gauche. Cible : recouvrement < 70 % (mesuré : 34 %) | confusion n° 1 du genre (75–91 %, audit) |
| m, in, ni, iu, rn | contrepoinçons à 1,4 × fût, point du i en losange net, haut | les suites de jambages fusionnent |
| a | deux étages | se distingue de o et d ; évite l'aspect manuscrit |
| d | forme onciale (haste inclinée à gauche) | b/d jamais en miroir (dyslexie) |
| b | haste à sommet fourchu, panse anguleuse | idem |
| p / q | p : pied à épine ; q : descendante droite nue | p/q jamais en miroir |
| I / J / l / 1 | I : barres haute et basse de part et d'autre du fût ; J : descend sous la ligne et finit en queue de diable ; l : sommet fourchu et pied en délié ; 1 : drapeau long et pied horizontal | I et J se confondent en gothique classique |
| O / 0 / o | 0 en losange étroit (≈ 80 % de la chasse de O), variante pointée par `zero` | identifiants, noms de marque |
| Queues (g, j, y, J) | queue de diable : plonge sous la descendante, remonte et finit en pique de carte ♠ soudée à la queue | demande de Danaé |
| s, r | s rond, r simple | pas de ſ long ni de r rotunda : anti-adjectif « médiéval » |
| Capitales par défaut | squelette lisible (proche du romain) habillé de losanges | lisibilité ; les capitales gothiques classiques sont peu reconnaissables |
| ’ et ' | apostrophe courbe distincte de l'apostrophe droite | UnifrakturMaguntia les confond (98 %, audit) |
| « » | dessinés en losanges, espaces fines insécables prévues | typographie française |

## Styles et axes
- Axe `wght` de 300 à 900, deux maîtres (300 et 900), instance par défaut 400.
- Instances nommées : Light 300, Regular 400, Medium 500, Bold 700, Black 900.
- Pas d'axe `GRAD` : pour un logo clair sur fond sombre, baisser la graisse (ex. 400 → 370) suffit, la chasse n'a pas besoin de rester fixe.

## Jeu de glyphes visé et points délicats
- Premier jalon : **GF_Latin_Core**. Cible finale : **GF_Latin_Plus**.
- Accents `.case` plus bas et plus plats sur capitales.
- Caron en apostrophe sur ď ť ľ Ľ (variante `caron.alt`).
- Virgules souscrites roumaines ș ț, distinctes de la cédille turque ş.
- Letton ķ ļ ņ ŗ ģ ; turc İ ı avec `locl` ; catalan l·l ; néerlandais IJ ; allemand ß ẞ.
- Ogonek ą ę ų et barres ł đ ħ : à dessiner à la main, les fûts serrés laissent peu de place.

## Glyphes décoratifs
| Glyphe | Codage | Note |
|---|---|---|
| Étoile à 4 branches | ✦ U+2726 (pleine), ✧ U+2727 (contour) | — |
| Lunes | ☽ U+263D, ☾ U+263E | — |
| Cœur | ♥ U+2665 | — |
| Chauve-souris | 🦇 U+1F987 et zone privée U+E000 | 🦇 risque d'être affiché par la police emoji du système : rendu à tester à l'étape 6 ; U+E000 sert de secours fiable |

Dans un logo web, ces glyphes sont décoratifs : `aria-hidden="true"`, et le nom porté par le texte alternatif.

## Fonctions OpenType
- `kern`, `mark`, `mkmk`, `ccmp`, `case` (tirets, guillemets, points médians remontés pour les capitales), `zero` (zéro pointé).
- `locl` roumain et moldave (ş Ş → ș Ș). Catalan (ŀ), néerlandais (ĳ) et turc/azéri (petites capitales) reportés à l'extension GF_Latin_Plus : les lettres concernées n'existent pas dans GF_Latin_Core.
- `ss01` « Capitales et chiffres coulants » (chiffres et zéro pointé compris) et `ss04` « Minuscules coulantes » : ronces coulantes. La coulure naît dans la lettre (22 % de sa hauteur), s'étrangle sous la ligne de base, descend en racine cassée (8 motifs de cassures), porte deux épines de rose (même forme en croissant que sur les lettres, racine ajustée à la largeur de la tige) et s'effile en pointe fine. Placement automatique sur les vrais fûts de chaque lettre (repérés à 30 % de la hauteur) ; une lettre sans fût près de la base (X, V…) reçoit sa ronce sur sa partie pleine la plus large au ras de la ligne de base : toutes les lettres ont au moins une ronce ; nombre de ronces décidé sur le Regular pour la compatibilité des maîtres, motif et longueur tirés d'une graine stable (nom du glyphe). Lettres à accent bas (ç ą ș…) exclues : l'accent resterait illisible. Les coulures descendent jusqu'à environ −665 unités : prévoir un interlignage d'environ 1,6 sur plusieurs lignes.
- `ss02` « Épines renforcées » : sur chaque minuscule, l'épine devient longue (× 1,6) et une seconde épine pousse du côté opposé, à la hauteur de la règle (70 % à droite, 45 % à gauche). Se cumule avec `ss04` grâce aux variantes `x.ss02.ss04` (mêmes ronces qu'en `ss04` seul).
- `ss03` (paraphes de fin de mot) abandonné : les ronces coulantes (`ss01`, `ss04`) jouent ce rôle d'ornement.

## Méthode de dessin et outils
- Dessin paramétrique en Python à partir de `assets/generateur_exemple.py` : formes en losanges et fûts droits, très adaptées au code ; une valeur vit à un seul endroit (`PARAMETRES`) ; structure de points identique entre maîtres garantie par construction.
- Construction fontmake, contrôle Font Bakery, licence OFL 1.1.

## Alternative plus sobre
- Aucune épine par défaut : bas de casse et capitales « gothique moderne » nets ; toutes les épines passent dans `ss02`.
- Gain : lisibilité maximale en petit (favicon, bas de page). Perte : l'identité « épineuse » n'apparaît que si on active la variante.
