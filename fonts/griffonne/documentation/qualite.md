# Contrôle qualité final — Griffonne

Date : 2026-10-25. Version testée : sources du projet, build complet par la chaîne du README.

## Vérifié (outil, résultat)

| Contrôle | Outil | Résultat |
|---|---|---|
| Couverture | `verifier.py` + glyphsets | GF_Latin_Core 100 % (319 caractères), 858 glyphes |
| Typographie française | `verifier.py` | complète (capitales accentuées, « », ’, espaces insécables, €) |
| Licence et métadonnées | `verifier.py` | copyright, créatrice, OFL 1.1 + URL, nom réservé, fsType 0 |
| Métriques | `verifier.py` | typo = hhea 985 / −265, interligne 0, USE_TYPO_METRICS, win couvrant la famille |
| Qualité technique | Font Bakery `check-universal` | 0 échec, 0 erreur, 1 avertissement (voir plus bas) |
| Confusions | `analyser_police.py` | 18 paires distinctes (I/l/1, O/0, rn/m, b/d, p/q, ’/'…) |
| Fonctions OpenType | HarfBuzz (glyphes produits) + Chromium | calt, ss01, case, zero conformes |
| Espacement, crénage | rendu Chromium avec et sans crénage | AVATAR, To, Va, L’été, P. corrects |
| Centrage vertical | bouton 56 px, Chromium | −0,2 px (encre comprise), corps des capitales ≈ 1 px plus bas (oreilles) |
| Petits corps hintés | FreeType, TTF hinté 11–16 px, clair et sombre | lisible dès 12 px ; oreilles effacées proprement |
| Spécimen accessible | axe-core 4.10 (WCAG 2.1 AA + bonnes pratiques) | 0 violation, clair et sombre |
| Clavier | parcours Tab | ordre logique, focus visible partout, lien d'évitement |
| Redistribution | 320 px, zoom 200 % | sans débordement (corrigé : fieldset du thème) |

## Avertissement restant, justifié
- **Nombre de contours inhabituel** : voulu. Les oreilles, yeux et moustaches ajoutent des contours aux lettres.

## Limites connues (documentées, pas des défauts)
- À 11–12 px, l'apostrophe ’ devient très petite : Griffonne est conçue pour 16 px et plus (brief).
- `ss01` « Chats complets » : pas d'alternance entre deux mêmes lettres ; moustaches débordantes, réservé aux titres dès 32 px.
- À 32 px sur fond sombre, les yeux chargent un peu les panses (niveau félin « marqué », choix validé).

## Pas encore vérifié (à faire de ton côté)
- **Lecteur d'écran réel** (NVDA sous Windows, VoiceOver sur iPhone ou Mac) sur le spécimen publié : axe-core vérifie la structure, pas l'écoute réelle.
- **Rendu sous Windows** (DirectWrite, ClearType) et dans Word : le hinting a été vu avec FreeType uniquement.
- **Tests avec des personnes** : test des 5 secondes (les adjectifs « espiègle, chaleureuse, artisanale » ressortent-ils ?) et lecture à voix haute d'un texte court à 16 px.
- **Marque** : recherche « Griffonne » dans les bases INPI et EUIPO avant publication.
