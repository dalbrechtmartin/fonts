# Rapport de contrôle

## Tendrille-Regular.ttf

- **OK** · GF_Latin_Core couvert entièrement
- **OK** · Typographie française complète (accents des capitales, guillemets, apostrophe, €)
- **OK** · copyright : Copyright 2026 Danaé ALBRECHT--MARTIN (https://danaedev.fr)
- **OK** · créatrice : Danaé ALBRECHT--MARTIN
- **OK** · description de licence : This Font Software is licensed under the SIL Open Font License, Version 1.1. This license 
- **OK** · URL de licence : https://openfontlicense.org
- **OK** · Interlignage par défaut : 1.24 × corps (le CSS appliquera ≥ 1,5 au texte courant)
- **OK** · Chiffres alignables en tableau

## TendrilleTexte-Regular.ttf

- **OK** · GF_Latin_Core couvert entièrement
- **OK** · Typographie française complète (accents des capitales, guillemets, apostrophe, €)
- **OK** · copyright : Copyright 2026 Danaé ALBRECHT--MARTIN (https://danaedev.fr)
- **OK** · créatrice : Danaé ALBRECHT--MARTIN
- **OK** · description de licence : This Font Software is licensed under the SIL Open Font License, Version 1.1. This license 
- **OK** · URL de licence : https://openfontlicense.org
- **OK** · Interlignage par défaut : 1.24 × corps (le CSS appliquera ≥ 1,5 au texte courant)
- **OK** · Chiffres alignables en tableau

**Bilan : 0 erreur(s).**

## Font Bakery (check-universal), famille par famille

| Famille | Erreurs | Échecs | Avertissements |
|---|---|---|---|
| Tendrille | 0 | 0 | 1 : `contour_count` |
| Tendrille Texte | 0 | 0 | 1 : `contour_count` |

- `contour_count` : attendu. Chaque geste de plume est un trait (le i a un fût et un cœur séparés, le ë un e et deux cœurs, les capitales à cœur un cœur de plus) ; les contours diffèrent donc des polices de référence.
- Vérifiées ensemble, les deux familles déclenchent `consistent_family_name` et `typographic_family_name` : ce sont deux familles distinctes par choix (Tendrille, Tendrille Texte), sans défaut.
- `fontdata_namecheck` peut apparaître en erreur quand le service en ligne de Google Fonts n'est pas joignable : ce n'est pas un défaut de la police.
- Corrigés pendant ce contrôle : largeurs des signes mathématiques (chasse commune de 644) ; segments superposés ou de longueur nulle (les statiques sont construites depuis une copie où les traits sont fusionnés et nettoyés : coordonnées entières, segments de moins de 6 unités et éclats de moins de 12 × 12 supprimés ; les sources gardent un contour par trait pour la future police variable).

## Mesures de lisibilité (analyser_police.py, formes de base)

Toutes les paires confusables sont « distinctes » et les miroirs « différenciés » dans les deux familles (détail : `controle-mesures.md`). rn / m : 71 % sans crénage, 64 % avec (Tendrille) ; 50 % (Tendrille Texte).

## Contrôles visuels

| Contrôle | Résultat |
|---|---|
| Petits corps hintés (FreeType, 11 à 16 px, clair et sombre) | Tendrille Texte nette dès 11 px. Tendrille lisible à 11–12 px ; ses cœurs y deviennent de simples points (usage prévu : 18 px et plus) |
| Mots difficiles | « Illégal 1l0O », « minimum », « Œuvre », « 1 250,50 € », « jZ7#qL! » lisibles dans les deux familles |
| Centrage vertical (bouton de 56 px, `inline-flex`) | encre à 1 px du centre (Tendrille), 0,5 px (Texte) ; police système : −1 px |
| Interlignage par défaut (1,24), capitales accentuées sous des descendantes | aucune collision, blanc serré ; le CSS de texte courant appliquera au moins 1,5 |
| Espace entre les mots | les cœurs de fin de mot mordent sur l'espace d'au plus 40 unités (« dit Yvon » corrigé) |
| Spécimen : axe-core (wcag2a, wcag2aa, wcag21aa, best-practice) | 0 violation, thème clair et thème sombre |
| Spécimen : 640 px (zoom 200 %) et 320 px | aucun débordement horizontal (mesuré par `scrollWidth`) |
| Spécimen : clavier | lien d'évitement en premier, tous les réglages atteints, focus visible |
| Daltonisme | sans objet : police monochrome, aucune information portée par la couleur |

## Non vérifié

- Rendu Windows réel (ClearType) et macOS / iOS : seul le rendu FreeType a été vu.
- Jeux stylistiques et `calt` dans Word, LibreOffice, Canva, Figma.
- Impression papier.
- Tests avec des personnes (test des 5 secondes, lecture à voix haute, personnes dyslexiques, malvoyantes, âgées, enfants) : pas faits.
