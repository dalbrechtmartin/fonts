# Audit des références

Mesures détaillées : `audit-mesures.md` (produit par `analyser_police.py`). Grille visuelle remplie d'après une planche rendue à 52 px.

## 1. Tableau comparatif

| Point | Love Script | Andika | Atkinson Hyperlegible |
|---|---|---|---|
| Classification | scripte calligraphique liée | humaniste sans empattement, formes « école » | grotesque à détails de lisibilité |
| Hauteur d'x / capitale | 0,61 : petite | 0,70 : grande | 0,74 : très grande |
| Ouvertures | sans objet (formes liées) | ouvertes | moyennes |
| Contraste et axe | fort, axe incliné (mesure 1,9 approximative : o incliné) | faible (1,16), axe vertical | faible (1,20), axe vertical |
| Fût / hauteur d'x | 0,09 : maigre | 0,18 | 0,18 |
| Terminaisons | effilées, en boucle | droites, adoucies | droites |
| Formes distinctives | capitales à grandes boucles, l bouclé, I et J très proches | a et g à un étage, l à queue | 0 barré, q à éperon, b d p q différenciés |
| Chasse et espacement | irrégulière, serrée, virgule détachée | normale, aérée | normale, aérée |
| Lisibilité | aucune paire confondue en mesure, mais lettres peu reconnaissables isolées | toutes les paires distinctes ; b/d 70 %, p/q 75 % en miroir | rn/m 67 %, b/d 85 % en miroir (proche du seuil de 90 %) |
| Couverture | Kernel 93 % (manquent œ et Ÿ), Core 60 %, Plus 5 % | Kernel et Core 100 %, Plus 75 %, African 99 % | Kernel 100 %, Core 95 %, Plus 26 % |
| Fonctions OpenType | ss01 à ss07 | nombreuses variantes (cvNN, ssNN), smcp, frac, mark | case, frac, tnum, pnum, mark |
| Licence | « All rights reserved », aucune licence fournie | OFL 1.1, noms réservés « Andika » et « SIL » | OFL 1.1 |
| Ce qui plaît | cœurs entre les mots, boucles, capitales ornées → **romance** | formes « école », chaleur discrète, couverture → **cœur**, public enfant | rigueur anti-confusion → malvoyance |
| Ce qui gêne | illisible en texte courant, petite hauteur d'x, couverture française incomplète | neutre, peu de geste → manque **manuscrit** | sèche, régulière → **mécanique**, **institutionnelle** |

## 2. Codes communs à respecter

- Pour une police de lecture accessible (Andika, Atkinson) : grande hauteur d'x (0,70 à 0,74 de la capitale), contraste faible (1,1 à 1,2), axe vertical, espacement aéré, fût autour de 0,18 de la hauteur d'x.
- Différenciation explicite des paires I l 1, O 0, b d p q par un détail (queue, barre, éperon) plutôt que par la seule proportion.
- Pour une scripte romantique (Love Script) : les ornements passent par des jeux stylistiques, pas par les formes par défaut.

## 3. Espace libre

Aucune des trois ne combine :
- un **geste manuscrit visible** (amorces, sorties de trait, irrégularités) ;
- les **garanties de lisibilité** d'Andika et d'Atkinson ;
- des **ornements romantiques activables** (cœurs entre les mots, capitales bouclées) ;
- une **couverture Latin Plus** complète (la meilleure, Andika, est à 75 %) ;
- une **famille variable avec italiques** (les trois sont statiques).

C'est la place de la nouvelle police.

## 4. Risques repérés

- **Lisibilité** : l'irrégularité manuscrite peut rapprocher des paires (rn/m, u/n, b/d) ; chaque famille de glyphes sera mesurée avec `analyser_police.py`, avec un seuil miroir plus strict que celui d'Atkinson.
- **Romance par défaut** : tout ornement actif par défaut dégrade la lecture ; ils restent dans des fonctions désactivées.
- **Couverture** : Latin Plus demande des lettres à dessiner entièrement, et leurs accents doivent rester lisibles avec un tracé irrégulier.
- **Interpolation** : les irrégularités doivent avoir la même structure de points dans chaque master.
- **Licence** : Love Script n'a pas de licence libre ; elle est mesurée seulement, jamais copiée, jamais versionnée ni redistribuée.
