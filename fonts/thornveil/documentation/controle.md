# Rapport de contrôle

## Thornveil-Black.ttf

- **OK** · GF_Latin_Core couvert entièrement
- **OK** · Typographie française complète (accents des capitales, guillemets, apostrophe, €)
- **OK** · copyright : Copyright 2026 Danaé ALBRECHT--MARTIN (https://danaedev.fr)
- **OK** · créatrice : Danaé ALBRECHT--MARTIN
- **OK** · description de licence : This Font Software is licensed under the SIL Open Font License, Version 1.1. This license 
- **OK** · URL de licence : https://openfontlicense.org
- **OK** · Interlignage par défaut : 1.30 × corps (le CSS appliquera ≥ 1,5 au texte courant)
- **ATTENTION** · Chiffres proportionnels sans fonction tnum : les tableaux de nombres ne s'aligneront pas

## Thornveil-Bold.ttf

- **OK** · GF_Latin_Core couvert entièrement
- **OK** · Typographie française complète (accents des capitales, guillemets, apostrophe, €)
- **OK** · copyright : Copyright 2026 Danaé ALBRECHT--MARTIN (https://danaedev.fr)
- **OK** · créatrice : Danaé ALBRECHT--MARTIN
- **OK** · description de licence : This Font Software is licensed under the SIL Open Font License, Version 1.1. This license 
- **OK** · URL de licence : https://openfontlicense.org
- **OK** · Interlignage par défaut : 1.30 × corps (le CSS appliquera ≥ 1,5 au texte courant)
- **ATTENTION** · Chiffres proportionnels sans fonction tnum : les tableaux de nombres ne s'aligneront pas

## Thornveil-Light.ttf

- **OK** · GF_Latin_Core couvert entièrement
- **OK** · Typographie française complète (accents des capitales, guillemets, apostrophe, €)
- **OK** · copyright : Copyright 2026 Danaé ALBRECHT--MARTIN (https://danaedev.fr)
- **OK** · créatrice : Danaé ALBRECHT--MARTIN
- **OK** · description de licence : This Font Software is licensed under the SIL Open Font License, Version 1.1. This license 
- **OK** · URL de licence : https://openfontlicense.org
- **OK** · Interlignage par défaut : 1.30 × corps (le CSS appliquera ≥ 1,5 au texte courant)
- **ATTENTION** · Chiffres proportionnels sans fonction tnum : les tableaux de nombres ne s'aligneront pas

## Thornveil-Medium.ttf

- **OK** · GF_Latin_Core couvert entièrement
- **OK** · Typographie française complète (accents des capitales, guillemets, apostrophe, €)
- **OK** · copyright : Copyright 2026 Danaé ALBRECHT--MARTIN (https://danaedev.fr)
- **OK** · créatrice : Danaé ALBRECHT--MARTIN
- **OK** · description de licence : This Font Software is licensed under the SIL Open Font License, Version 1.1. This license 
- **OK** · URL de licence : https://openfontlicense.org
- **OK** · Interlignage par défaut : 1.30 × corps (le CSS appliquera ≥ 1,5 au texte courant)
- **ATTENTION** · Chiffres proportionnels sans fonction tnum : les tableaux de nombres ne s'aligneront pas

## Thornveil-Regular.ttf

- **OK** · GF_Latin_Core couvert entièrement
- **OK** · Typographie française complète (accents des capitales, guillemets, apostrophe, €)
- **OK** · copyright : Copyright 2026 Danaé ALBRECHT--MARTIN (https://danaedev.fr)
- **OK** · créatrice : Danaé ALBRECHT--MARTIN
- **OK** · description de licence : This Font Software is licensed under the SIL Open Font License, Version 1.1. This license 
- **OK** · URL de licence : https://openfontlicense.org
- **OK** · Interlignage par défaut : 1.30 × corps (le CSS appliquera ≥ 1,5 au texte courant)
- **ATTENTION** · Chiffres proportionnels sans fonction tnum : les tableaux de nombres ne s'aligneront pas

## Thornveil-VF.ttf

- **OK** · GF_Latin_Core couvert entièrement
- **OK** · Typographie française complète (accents des capitales, guillemets, apostrophe, €)
- **OK** · copyright : Copyright 2026 Danaé ALBRECHT--MARTIN (https://danaedev.fr)
- **OK** · créatrice : Danaé ALBRECHT--MARTIN
- **OK** · description de licence : This Font Software is licensed under the SIL Open Font License, Version 1.1. This license 
- **OK** · URL de licence : https://openfontlicense.org
- **OK** · Interlignage par défaut : 1.30 × corps (le CSS appliquera ≥ 1,5 au texte courant)
- **ATTENTION** · Chiffres proportionnels sans fonction tnum : les tableaux de nombres ne s'aligneront pas

**Bilan : 0 erreur(s).**

## Font Bakery (check-universal), lancé séparément sur les statiques et sur la variable

- Statiques : 0 échec, 0 erreur. Variable : 0 échec, 0 erreur.
- Avertissements laissés, justifiés :
  - `contour_count` : nombres de contours inhabituels, attendus pour une police ornée (épines, ronces, contours qui se chevauchent par construction).
  - `overlapping_path_segments` : segments d'une unité nés de l'arrondi. Les supprimer à l'écriture casserait la compatibilité des maîtres de la variable (un point retombe sur son voisin dans un maître et pas dans un autre). Sans effet visible.
  - `mandatory_avar_table` : interpolation linéaire voulue (le maître Regular est dessiné à 400, la progression des graisses est déjà régulière).

## Corrections faites pendant le contrôle

- Espace fine insécable (U+202F) et espace fine (U+2009) ajoutées.
- Table STAT : étiquettes de graisse (Light, Regular, Medium, Bold, Black).
- Regroupement de styles : Regular et Bold forment le couple de base ; Light, Medium et Black sont chacun le Regular de leur famille.
- Smart dropout et table gasp sur la variable (`scripts/finaliser_variable.py`).
- Signes mathématiques + − = × ÷ < > à chasse égale.
- Rond du Å/Ů et virgule souscrite (ș ț ķ ļ ņ ģ) limités : ils dépassaient la boîte de ligne en Black.
- Diacritique inutile `uni0312.case` retiré.
- Chiffres ajoutés au jeu ss01, renommé « Capitales et chiffres coulants » ; zéro pointé coulant (`zero` + `ss01` se cumulent). Contrôles relancés ensuite : mêmes résultats.

## Mesures

- Lisibilité (`controle-mesures.md`) : toutes les paires « distinct », miroirs « formes différenciées » (n/u 22 %, I/l 54 %, I/1 69 %, O/0 19 %).
- Centrage vertical : centre de la boîte de ligne (1000 / −300) = 350 = moitié de la hauteur de capitale.
- Boîte de ligne : aucun glyphe de base n'en sort, dans aucune graisse. Les ronces de ss01 et ss04 en sortent volontairement (jusqu'à −665) : interlignage d'environ 1,6 sur plusieurs lignes.
- Petits corps (TTF hinté, rendu FreeType, 11 à 16 px, clair et sombre) : lecture correcte dès 12 px ; les épines disparaissent sous 16 px environ (ornement de titrage).

## Spécimen (`specimen/index.html`)

- axe-core 4.10 (wcag2a, wcag2aa, wcag21aa, best-practice) : 0 violation en thème clair et en thème sombre.
- 320 px de large : aucun débordement horizontal (scrollWidth = innerWidth).

## Non vérifié à ce stade

- Rendu réel sous Windows (ClearType), macOS et iOS ; impression papier.
- Navigation clavier et zoom à 200 % du spécimen, faits par une personne.
- Rendu de 🦇 (U+1F987) dans les navigateurs : certains préfèrent leur emoji couleur ; U+E000 reste l'accès garanti.
- Tests avec des personnes (5 secondes, lecture à voix haute, personnes dyslexiques ou malvoyantes) : non faits.
- Chiffres tabulaires (tnum) : non prévus, choix assumé pour une police de logos.
