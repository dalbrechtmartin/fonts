# Changelog

## [1.0.1](https://github.com/dalbrechtmartin/fonts/compare/sorcelle-v1.0.0...sorcelle-v1.0.1) (2026-10-27)


### Bug Fixes

* write the author name in capitals ([7eb0c35](https://github.com/dalbrechtmartin/fonts/commit/7eb0c353bebf495db4ff2df013d1ca9b40c4fe30))

## [1.0.0](https://github.com/dalbrechtmartin/fonts/compare/sorcelle-v0.6.0...sorcelle-v1.0.0) (2026-10-26)


### Features

* **sorcelle:** redraw every GF Latin Core glyph in the Sorcelle style ([5e22574](https://github.com/dalbrechtmartin/fonts/commit/5e22574c4a95f553bf93543f7fe385468df7113e))

## 0.6.0 (2026-10-25)


### Features

* nouveau glyphe λ (pour « λLens »), hors planche dans `glyphs_extra.json`


### Bug Fixes

* petit pont en losange sur chaque jointure diagonale (`BRIDGE = 0.3` pixel) : plus de « petits trous » au zoom dans Æ, Ç et Œ, signalés par le test « Lire Sorcelle » (5 personnes, 59 mots sur 60 lus justes, facilité moyenne 4,8 / 5)

## 0.5.0 (2026-10-25)


### Bug Fixes

* un seul contour par forme (fonction `outline`) : plus de fins traits clairs horizontaux à petite taille ou au zoom (le « a » passe de 16 contours à 2), dessin identique au pixel près à 43 et 86 px

## 0.4.0 (2026-10-24)


### Features

* trois graisses : Regular (400), SemiBold (600) et Bold (700), obtenues en épaississant chaque pixel vers la droite

## 0.3.0 (2026-10-24)


### Features

* minuscules rondes (choisies parmi 2), chiffres alignés et ponctuation redessinés
* nouveau glyphe ✦ (U+2726)
* renommée **Sorcelle** (ancien nom de travail : Yoru)

## 0.2.0 (2026-10-24)


### Features

* capitales « lombarde arrondie » (variante B, choisie parmi 4)

## 0.1.0 (2026-10-24)


### Features

* première version dérivée de Jacquard 24 : capitales brisées à filet
