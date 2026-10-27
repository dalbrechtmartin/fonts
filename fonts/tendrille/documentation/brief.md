# Brief — Tendrille

## Idée en une phrase
Une semi-manuscrite de lecture, chaleureuse et romantique, lisible par le plus grand nombre à l'écran, dont les ornements (cœurs, boucles) s'activent à la demande.

## Usage principal et tailles
- Texte courant, lecture longue.
- Écran seul : contraste de traits faible, contre-formes ouvertes, terminaisons nettes, TTF hintés.
- Tailles de contrôle : 12 à 48 px, thèmes clair et sombre.

## Public et besoins d'accessibilité
Grand public international, lecteurs dyslexiques, personnes âgées ou malvoyantes, enfants qui apprennent à lire.
- Formes non miroirs : b, d, p, q différenciés.
- Confusions éliminées : I l 1 |, 0 O o, rn/m, cl/d.
- Grande hauteur d'x, ouvertures larges, espacement généreux.
- Formes « école » du a et du g (un étage) en jeu stylistique.
- Aucune promesse thérapeutique sur la dyslexie : on parle de différenciation et d'espacement.

## Langues visées → jeux de glyphes : GF_Latin_Core + GF_Latin_Plus + GF_Latin_African
Couverture internationale large, atteinte par paliers : GF_Latin_Core → GF_Latin_Plus → GF_Latin_African.
- Core : français et langues européennes à alphabet latin (GF_Latin_Kernel ne suffit pas : ni œ ni capitales accentuées).
- Plus : symboles du texte courant (fractions, exposants, monnaies, flèches, signes mathématiques, chiffres tabulaires).
- African : langues d'Afrique et des Amériques ; lettres à dessiner entièrement (ŋ, ɛ, ɔ, ɓ, ɗ, ƙ, ʋ, ɣ, ƴ…).

## Personnalité
- Adjectifs : cœur · romance · manuscrit
- Anti-adjectifs : mécanique · froide · institutionnelle

Piste retenue : semi-manuscrite audacieuse (lettres non liées, dessin libre, irrégularités visibles, amorces et sorties de trait), à la plume, romantique et élégante. Une seconde famille plus sobre, Tendrille Texte, prend en charge les petites tailles et la malvoyance (voir la spécification).

## Références (avec ce qui plaît dans chacune)
- **Love Script** (mightype, dafont) : les cœurs qui relient les mots, les boucles et les capitales ornées.
  - Non retenus : le fort contraste plein / délié et l'inclinaison.
  - Traduction : fins de mots à sortie en cœur (ligatures discrétionnaires ou ornements), capitales bouclées et hampes bouclées en jeux stylistiques, tous désactivés par défaut.
  - Licence à vérifier sur le texte fourni dans l'archive. Mesurée seulement, aucun contour copié, jamais versionnée dans le dépôt public.

## Famille et styles
Famille complète avec italiques, construite en police variable :
- axe de graisse (masters Light, Regular, Bold) ;
- italiques en masters dédiés.

## Contraintes
- Aucun délai : projet personnel au long cours.
- Dessin paramétrique en code : la graisse est un paramètre, les irrégularités manuscrites sont déterministes (graine fixe) pour garder des masters compatibles. Les ornements pourront passer en import SVG si le code ne suffit pas.

## Diffusion et licence (OFL 1.1, nom réservé : non)
- OFL 1.1.
- Dépôt GitHub `dalbrechtmartin/fonts` et npm `@danaedev`.

## Premier jalon
Regular droit, jeu GF_Latin_Core, sans ornements.

Jalons suivants :
1. Bold → première version variable (axe de graisse)
2. Extension GF_Latin_Plus, puis GF_Latin_African
3. Italiques
4. Ornements romance (cœurs, capitales et hampes bouclées)
