# Contrôle — Sorcelle (GF Latin Core complet)

Polices contrôlées : `dist/Sorcelle-Regular.ttf`, `Sorcelle-SemiBold.ttf`, `Sorcelle-Bold.ttf`, construites par
`python tools/polices.py construire sorcelle` (26/10/2026).

## Contrôles automatiques

| Contrôle | Résultat |
| --- | --- |
| `tools/polices.py verifier sorcelle` (famille, graisses, glyphes du spécimen, version) | OK |
| `verifier.py --jeu GF_Latin_Core` (skill création-police) | 0 erreur, 2 avertissements expliqués ci-dessous |
| Font Bakery 1.1.0, `check-universal` | 0 échec, 4 avertissements expliqués ci-dessous |
| `analyser_police.py` sur le Regular | GF Latin Core 100 %, aucune paire à risque de confusion, b/d et p/q différenciés |
| Glyphes encore dessinés par Jacquard 24 | aucun, sauf `.notdef` et § (gardé volontairement) |

### Corrigé pendant ce contrôle (`build.py`)

- Espace fine insécable U+202F ajoutée (moitié de l'espace, 150 unités) : typographie française.
- Λ (U+039B) ajouté, capitale de λ : le A sans sa barre.
- Entrées Mac (plateforme 1) retirées de la table `name`.
- SemiBold : bit « Regular » de `fsSelection` mis, comme le veut son nom de style (nameID 2 = Regular).
- `usWinAscent` / `usWinDescent` = boîte englobante réelle (990 / 240) au lieu des 1 022 / 750 de Jacquard 24.
  `USE_TYPO_METRICS` étant déjà actif, l'interlignage ne change sur aucun système.
- Police sans hinting avec contrôle des pertes de pixels (smart dropout, table `prep`) et table `gasp`, comme
  `gftools fix-nonhinting`.
- Chasse des signes mathématiques − × ÷ = < > alignée sur celle du + ; `xAvgCharWidth` recalculé.

### Avertissements laissés

| Avertissement | Pourquoi il reste |
| --- | --- |
| Interlignage par défaut 1,00 × corps | police de titrage ; ascendante et descendante couvrent les capitales accentuées. Le portfolio règle `line-height` en CSS |
| Chiffres sans `tnum` | sans objet pour une police de titrage (spécification) |
| `unitsPerEm` = 1 290 | grille de Jacquard 24 : 1 pixel = 30 unités, pixels nets à 43, 86 et 129 px |
| Pas de crénage dans GPOS | l'espacement suit le dessin au pixel ; le crénage de Jacquard 24 visait les anciennes formes |
| Ľ ď ľ ť « décomposés, à vérifier à la main » | dessinés au pixel (pas de composants) : vérifiés à 43, 86 et 129 px, caron en apostrophe séparé du fût |
| Nombre de contours inhabituel (M, m, §, Æ, ß, đ, ħ…) | dessin pixel : jointures diagonales et barres forment des contours séparés |

## Contrôles visuels

- Planches Regular et Bold à 43, 86 et 129 px : lettres accentuées, accents, symboles, paires ẞ / B, Ð Đ / D,
  Ł / L, İ ı / I i, Ș / Ş, Ģ / G, Ø / O, Þ / P, Ŋ / N.
- Accents combinants (texte décomposé) dans Chrome, sur minuscules et capitales : posés à la même hauteur que dans
  les lettres composées (fonction `mark` et variantes `.case`).
- Spécimen de contrôle à 375 px de large : pas de débordement horizontal.

## Lecture OCR (Tesseract 5.4, modèle anglais)

`weights.py` et `legibility.py`, 7 phrases en capitales, minuscules et chiffres, rendues à 129 px :

| Graisse | 0.3 (README) | Maintenant |
| --- | --- | --- |
| Regular | 99,6 % | 99,6 % |
| SemiBold | 98,7 % | 99,1 % |
| Bold | 99,5 % | 99,1 % |

Jacquard 24 sur les mêmes phrases : 85 %. Capitales les plus proches : C / G (27 % de différence), aucune paire
au-dessus du seuil de risque.

Essai indicatif sur les nouveaux symboles (5 lignes, hors script) : 85 % en Regular, 82 % en Bold.
- Lus sans erreur : $ £ € ¢ “ ” ‘ ’ « » ° ®.
- Mal lus : × ÷ − ¿ ¡ ™ • ¶ et ‹ › (lus x, +, -, i, j, ", -, 1, < >). Le modèle anglais de Tesseract reconnaît mal
  ces signes quelle que soit la police ; vérifiés à l'œil.
- { } étaient lus i et f : bec central redessiné en pointe sur trois lignes. Après correction, « {sorts} {x} » est lu
  à 100 % en Regular et en Bold.
- Les lettres accentuées ne sont pas mesurées : il faudrait les modèles de langue de Tesseract (fra, deu, pol…).

## Non testé

- Lecture OCR des lettres accentuées (modèles de langue absents).
- Rendu Windows (DirectWrite) et macOS réels, thème sombre du spécimen sur téléphone.
- Audit axe-core et parcours clavier du spécimen du site (`site/`), inchangé par ce lot.
- Tests avec des personnes (lecture à voix haute, test des 5 secondes).
