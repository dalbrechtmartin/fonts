# Brief — Sorcelle

## Idée en une phrase
Une police pixel « lombarde arrondie » pour les titres du portfolio (design system Grimoire), lisible d'un coup d'œil.

## Usage principal et tailles
Titrage à l'écran, à partir de 32 px. Pixels nets aux multiples de la grille : 43, 86 et 129 px (1 pixel de dessin =
30 unités sur 1 000, soit 1, 2 ou 3 pixels d'écran).

## Public et besoins d'accessibilité
Grand public du portfolio. Capitales et minuscules différenciées (C / G, O / 0, I / l / 1, a / o, n / u), mesurées par
OCR et par distance de formes (README de Sorcelle, 24/10/2026). Lisible sur les thèmes Parchemin (clair) et Crypte
(sombre).

## Langues visées → jeu de glyphes : GF_Latin_Core
Français d'abord, puis les langues d'Europe de l'Ouest et centrale couvertes par GF Latin Core. Les 319 caractères sont
déjà présents, mais 187 viennent encore de Jacquard 24 : ils passent au style Sorcelle, dans les trois graisses.

## Personnalité
- Adjectifs : mystérieuse · artisanale · nette
- Anti-adjectifs : Halloween kitsch · gothique illisible · rétro-gaming cliché

## Références (avec ce qui plaît dans chacune)
- Jacquard 24 (Soft Type, OFL) : point de départ, grille pixel et hauteurs (x = 17, capitales = 25, jambages = 7 px).
- Lettrines lombardes des manuscrits : capitales rondes, fûts épais, têtes en crosse.

## Famille et styles
Regular (400), SemiBold (600), Bold (700), tirées d'une seule planche en épaississant chaque pixel vers la droite
(+0, +1, +2 px). Pas d'italique ni de police variable.

## Contraintes
- Dessin pixel sur `planche.png` (Aseprite), compilé par `build.py` ; glyphes hors planche dans `glyphs_extra.json`.
- Toute nouvelle forme suit le style déjà validé : fûts de 5 px (capitales) et 4 px (minuscules), déliés de 2 px,
  panses rondes, points carrés.
- Les lettres accentuées se composent à partir des lettres et des accents déjà dessinés, puis se retouchent à la main.

## Diffusion et licence
OFL 1.1, dérivée de Jacquard 24 (sans nom réservé). Nom réservé pour Sorcelle : non (police dérivée, choix à confirmer
à l'étape 7). Publication : GitHub (releases), site de spécimens, npm (`@danaedev/sorcelle`).

## Premier jalon
1. Accents seuls (15) redessinés, puis les 143 lettres accentuées composées et retouchées : publiable en 0.7.0.
2. Les 40 symboles et signes de ponctuation restants (€ $ £ ¥ ° × ÷ ™ ® ¿ ¡ { } \ | ~ ^ • ‹ › “ ” „ ‘ ‚…) : 1.0.0
   stable, plus aucun glyphe hérité de Jacquard 24 (sauf §, gardé volontairement).
