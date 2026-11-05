# Audit — références

Les cinq images sont des lettrages, pas des polices : elles sont décrites sans mesures. Les chiffres viennent de quatre gothiques sous OFL mesurées comme étalons du genre (détail dans `audit-mesures.md`). Les mesures de graisse et de contraste sont approximatives (rendu matriciel du « o »).

## 1. Images de lettrage (grille visuelle)

| Point | Paradyse | Born from shadows | Nocturne Whispers | Fairytales / Traces |
|---|---|---|---|---|
| Classification | textura fantaisie | textura fantaisie | fraktur / textura | fraktur à capitales cursives |
| Hauteur d'x | grande | grande | moyenne | grande |
| Ouvertures | fermées | fermées | moyennes | moyennes |
| Contraste et axe | fort, axe incliné (plume) | fort, axe incliné | fort | moyen |
| Terminaisons | losanges, épines | losanges, épines, pointes | losanges, crochets | losanges, déliés en boucle |
| Formes distinctives | P à paraphe, y à boucle | B et f à épines, point final en losange | capitales ornées, a à deux étages | Y et F cursifs, paraphe en infini + cœur |
| Chasse | étroite | étroite | normale | étroite |
| Espacement | serré | serré | aéré | serré |
| Lisibilité | moyenne (n/u, a/d) | faible au premier coup d'œil (silhouettes chargées) | bonne en bas de casse | bonne |
| Ce qui plaît | épines, paraphes, décor chauves-souris | épines fines, symétrie, lunes et étoiles | alphabet complet cohérent | paraphe à cœur suspendu |
| Ce qui gêne | proche du « black metal » si poussé | proche du « black metal » | proche du « médiéval historique » | — |

## 2. Étalons mesurés (OFL)

| Point | Grenze Gotisch | Texturina | UnifrakturMaguntia | Pirata One |
|---|---|---|---|---|
| Hauteur d'x / capitale | 0,74 | 0,71 | 0,78 | 0,75 |
| Fût / hauteur d'x | 0,21 | 0,20 | 0,19 | 0,20 |
| Variation | wght 100–900 | wght + opsz | statique | statique |
| GF_Latin_Core | 100 % | 100 % | 67 % | 95 % |
| GF_Latin_Plus | 57 % | 55 % | 13 % | 13 % |
| Fonctions | ss01, salt, dlig, case… | case, frac… | liga, hlig | kern |
| Confusion n/u | 75 % | 75 % | 82 % | 91 % (risque) |

## 3. Codes communs du genre (à respecter)
- Rapport hauteur d'x / capitale entre 0,71 et 0,78 : grande hauteur d'x.
- Fût autour de 0,20 × hauteur d'x au Regular.
- Fûts verticaux serrés, attaques et pieds en losange, axe de plume incliné.
- Capitales plus ornées que le bas de casse.

## 4. Espace libre
- Aucun étalon ne couvre GF_Latin_Plus en entier (55–57 % au mieux).
- Aucun ne propose d'épines ni de paraphes activables, ni de glyphes décoratifs (étoiles, lunes, chauves-souris, cœurs).
- Seule Grenze Gotisch est variable en graisse parmi les gothiques de « fantaisie » ; aucune n'est épineuse.
- Créneau : gothique moderne variable, épineuse à la demande, pensée pour composer des logos.

## 5. Risques
- **Lisibilité** : n/u est la confusion structurelle du genre (75 à 91 %). Idem pour les suites de jambages (m, in, ni, iu, rn). À traiter par un détail distinctif (attaque de n, pied de u).
- **Lisibilité** : capitales gothiques classiques peu reconnaissables ; capitales par défaut à garder lisibles, capitales ornées en variante.
- **Anti-adjectif** : épines sur chaque lettre = black metal. Épines en dose mesurée par défaut, renforcées en variante.
- **Couverture** : caron, ogonek, ł, ŋ, ĳ difficiles à intégrer aux fûts serrés et aux losanges.
- **Variation** : épines et paraphes doivent garder la même structure de points entre les deux maîtres.
- **Licence** : les cinq images sont de licence inconnue : jamais versionnées dans le dépôt public.
