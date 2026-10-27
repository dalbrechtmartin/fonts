# Changelog

## [1.0.2](https://github.com/dalbrechtmartin/fonts/compare/griffonne-v1.0.1...griffonne-v1.0.2) (2026-10-27)


### Bug Fixes

* **griffonne:** write the version from police.json into the font files ([ce6e18e](https://github.com/dalbrechtmartin/fonts/commit/ce6e18eef3a40d139697044de17ed6bde00a1c33))
* write the author name in capitals ([7eb0c35](https://github.com/dalbrechtmartin/fonts/commit/7eb0c353bebf495db4ff2df013d1ca9b40c4fe30))

## [1.0.1](https://github.com/dalbrechtmartin/fonts/compare/griffonne-v1.0.0...griffonne-v1.0.1) (2026-10-26)


### Bug Fixes

* **griffonne:** drop the reserved font name ([8b89145](https://github.com/dalbrechtmartin/fonts/commit/8b89145a51a2e767a627cb0ccbe5f8793f40691e))

## 1.0.0 (2026-10-26)


### Features

* première version publique : couverture GF Latin Core (8 langues), fonctions `calt`, `ss01` « Chats complets », `case` et `zero`


### Bug Fixes

* contours sans segments de longueur nulle ; contrôle Font Bakery à 0 échec, spécimen à 0 violation axe-core (`documentation/qualite.md`)

## 0.1.0 (2026-10-25)


### Features

* création du projet et moteur de pinceau (texture B, ondulation longue ±10 à graine fixe)
* minuscules complètes, niveau félin « marqué » par défaut : un élément de chat sur chaque lettre (oreilles, visages, queues)
* capitales A–Z, chiffres tabulaires 0–9 aux oreilles homogènes, ponctuation et espace fine insécable
* diacritiques, œ æ Œ Æ et 145 accentuées composées : typographie française complète
* lettres spéciales (ß ẞ ø ł đ ð þ ħ ª º…) et symboles : GF Latin Core couvert à 100 %
* espacement optique et crénage mesuré (400 paires de classes)
* métriques verticales 985 / −265 : rien ne dépasse, capitales centrées dans les boutons


### Bug Fixes

* point du j centré sur son fût
* queue du l raccourcie et relevée : il ne se lit plus comme un L en petit
