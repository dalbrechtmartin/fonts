# Spécification — Tendrille

Sources des justifications : brief (`brief.md`), mesures de l'audit (`audit.md`), recommandations de lisibilité de la fiche de spécification.

## Décisions (Regular droit)

| Paramètre | Valeur | Justification |
|---|---|---|
| Unités par cadratin | 1000 | standard |
| Hauteur d'x | 520 | lecture à l'écran, malvoyance : haut de la fourchette 0,50 à 0,55 ; au-dessus d'Atkinson (496) et proche d'Andika (508) |
| Hauteur de capitale | 720 | rapport x / capitale 0,72, entre Andika (0,70) et Atkinson (0,74) ; des capitales un peu plus hautes laissent la place aux capitales bouclées |
| Ascendante / descendante | 770 / −250 | hampes au-dessus des capitales (repère humaniste, distingue l de I) ; descendantes assez longues pour un geste manuscrit lisible |
| Dépassement des rondes | 12 | correction optique, environ 2,3 % de la hauteur d'x |
| Fût vertical Regular | 88 | fût / hauteur d'x 0,17, juste sous les références de lecture (0,18) pour plus de finesse ; les traits perpendiculaires à la plume atteignent 97, comme avec une plume elliptique |
| Délié / contraste | 52 / 1,7 | révisé après la première famille : contraste marqué pour l'ambiance romantique et élégante ; délié de 0,83 px à 16 px, d'où un usage recommandé à partir de 18 px (les petites tailles passent par Tendrille Texte) |
| Angle de plume | 30° | angle classique de la calligraphie : pleins et déliés tournent avec les courbes (adjectifs « romance », « manuscrit ») |
| Approches de calibrage (droite / ronde) | minuscules n / o : 58 / 44 ; capitales H / O : 64 / 48 | espacement aéré pour la lecture longue et la dyslexie ; un peu plus d'air entre capitales ; `espacer.py` en déduit l'espacement optique de chaque lettre à chaque génération |
| Boîte de ligne (typo = hhea, interligne 0) | 980 / −260 | (980 − 260) / 2 = 360 = capitale / 2 : capitales centrées dans les boutons et champs ; interlignage par défaut 1,24 ; les contours plus hauts (accents empilés d'African) sont couverts par les métriques win calculées au build |

## Caractère manuscrit (piste audacieuse)

Tous les écarts sont **déterministes** : la graine est le nom du glyphe, donc chaque build et chaque master donnent la même forme, avec la même structure de points (condition de l'interpolation).

| Paramètre | Valeur | Justification |
|---|---|---|
| Inclinaison propre de chaque fût | ±1,5° au plus | une écriture n'est jamais parfaitement verticale ; assez faible pour garder un axe vertical en lecture |
| Entrées en délié | 55 unités, courbes, effilées jusqu'à 25 % de la largeur | geste de la plume (« manuscrit ») ; différencient aussi b d p q |
| Sorties en ruban dans le mot | 70 unités, remontée de 50 | décision après la troisième famille (« pas assez romantique ») : le trait remonte en une seule courbe dès la sortie du virage (un premier dessin qui creusait d'abord faisait un palier disgracieux, surtout sur le a), sans toucher la lettre suivante |
| Rubans à cœur en fin de mot | 210 unités, remontée de 290 (cœur placé plus haut après retour), qui s'enroulent en cœur d'un seul geste : le ruban arrive à la pointe, le trait monte dans le lobe gauche, passe le creux, fait le lobe droit et revient finir sur la pointe, effilé — la pointe du cœur est la fin du trait (choix après retour) (largeur 220, trait à 60 % : 50 % paraissait trop fin, 75 % trop lourd ; penché de −28° dans l'élan, choisi parmi −8°, −18° et −28° : le cœur en mouvement contraste avec le cœur posé du point du i ; au creux, deux gestes qui se rejoignent pour éviter un pli) — décisions après retours : un cœur « posé au bout d'une tige » ne faisait pas écriture naturelle ; un ruban trop long éloignait le cœur de sa lettre ; un cœur trop fin n'était pas harmonieux. Pas de grande entrée en début de mot : les essais (délié, pleine, à boucle) alourdissaient l'attaque des mots | romance visible sans lier les lettres : variantes `X.fina` de a c d e h i k l m n r t u z (le s, dont le trait finit vers la gauche, attend un dessin dédié ; pour le t, c'est la barre qui file en ruban jusqu'au cœur, le pied reste sobre, inspiré de « beauty »), posées par `calt` (actif par défaut) quand la lettre n'est suivie ni d'une lettre, ni d'une apostrophe, ni d'un trait d'union (« dit-elle »), ni d'une espace insécable (« Bonjour ! », où le ruban toucherait la ponctuation) ; le ruban du r, qui part du haut, est réduit à 40 % pour ne pas toucher le mot suivant |
| Espace entre les mots | 330 (Tendrille), 280 (Tendrille Texte) | la frontière des mots doit rester évidente malgré rubans et entrées, essentiel pour les lecteurs dyslexiques |
| Asymétrie des courbes | ±3 % de la tension | chaleur, rejet du « mécanique » |
| Vibration du contour | 5 unités au plus | texture visible en grand corps, invisible en texte (0,08 px à 16 px) |
| Alternances contextuelles (`calt`) | 2 versions de e a n o s t i r | évite deux lettres identiques côte à côte, comme à la main ; les deux versions gardent la même silhouette (recouvrement mesuré ≥ 90 %) |

## Formes distinctives

| Glyphe | Forme | Justification |
|---|---|---|
| a | deux étages par défaut ; un étage (« école ») en `ss01` | grand public par défaut ; enfants qui apprennent à lire à la demande |
| g | un étage, queue ouverte | forme la plus lue à l'écran, déjà proche de l'écriture scolaire |
| I | barres en haut et en bas | se distingue de l et de \|, naturel à la main |
| l | queue arrondie vers la droite | se distingue de I et de 1 (règle I l 1) |
| 1 | drapeau long et pied | se distingue de l (15 %) et de I (46 % ; 73 % avec un premier drapeau trop court) |
| 0 | boucle fermée, plus étroite que O ; barré oblique en `zero` | O/0 mesuré à 17 % ; le O de Tendrille, croisé, s'en distingue encore plus |
| b d p q | b sans queue ; d avec sortie en bas à droite ; p avec amorce en haut à gauche ; q avec queue relevée en bas à droite | aucun simple reflet ; seuil miroir visé sous 80 % (Atkinson est à 85 %) |
| rn / m, cl / d | approches et sorties réglées pour ne jamais fusionner ; recouvrement visé sous 70 % | lecture rapide ; l'irrégularité est le principal risque relevé à l'audit. r à épaule courte et tombante pour garder un blanc avant la lettre suivante ; mesure actuelle de rn / m : 72 % (Tendrille), 50 % (Tendrille Texte), à ramener sous 70 % au crénage (r-n, r-m, r-u) |
| Q | queue détachée qui traverse le bas et file sous la lettre suivante | se distingue de O : mesuré à 42 % (Tendrille) et 47 % (Texte) ; une première queue trop courte donnait 80 % |
| R | jambe droite et oblique | lisibilité en petit corps |
| Capitales | mêmes gestes que les minuscules : entrée en délié sur les fûts, barres en vague (A, G, H, T), panses accrochées au fût (B, D, P, R) ; E, K, L, Z finissent en ruban ; pas de cœur de fin de mot | un titre tout en capitales reste calme ; I/l mesuré à 35 % |
| t, y | t à pied courbe ; y dont le trait droit descend sous la ligne et file vers la gauche, comme la queue du j | formes manuscrites sobres |
| f | fût qui monte de la ligne de base et finit en crochet effilé, barre à la hauteur d'x | le crochet déborde sur la lettre suivante : paires f + lettre haute à régler au crénage |
| k | bras et jambe en deux gestes, jambe qui finit en ruban | le changement de direction au fût est trop brusque pour un seul trait |
| v, w, x | diagonales en pointe ; v et w finissent par une petite boucle vers la droite ; x = descente pleine + montée en délié | vv / w mesuré à 7 % |
| Points du i et du j, et de la ponctuation | dans Tendrille, le même cœur tracé d'un seul geste que les rubans, qui part de la pointe et y revient, pour l'unité de la police : 165 sur i et j ; 140, trait à 50 %, sur . : ; ! ? … · (plus petits, ils doivent rester ouverts) ; rond dans Tendrille Texte | décision après la deuxième famille : romance par défaut dans la famille d'affichage, sobriété aux petites tailles où un cœur deviendrait une tache ; la présence du point compte pour la lecture, pas sa forme |
| ’ et ' | apostrophe typographique courbe ; apostrophe droite verticale | typographie française, codes |
| « » | arrondis, ouverts | typographie française, cohérence manuscrite |
| Chiffres | alignés sur 700 (un peu sous les capitales, comme à la main), proportionnels par défaut, tabulaires en `tnum` ; 4 ouvert en haut, 8 en deux boucles, 9 = le geste du 6 retourné d'un demi-tour (un premier 9 en deux pièces, anneau et queue, laissait voir la jonction) | tableaux et interfaces |
| Guillemets « » ‹ › | chevrons arrondis et ouverts, trait allégé à 75 % | plus petits, ils se bouchaient |
| Espaces | espace fine (U+2009) et fine insécable (U+202F) : 180 (Tendrille), 150 (Texte) | typographie française : avant ; : ! ? » et après « |

## Ornements

| Caractère | Dessin | Usage |
|---|---|---|
| ❦ U+2766 | longue volute fine à deux ondulations (900 unités, trait à 60 %) qui finit en cœur, tournée vers la gauche ; choisie parmi trois essais (volute courte, longue vague, cœur au milieu) | avant un titre |
| ❧ U+2767 | la même volute vers la droite ; marge de chaque côté pour que le cœur penché ne déborde pas | après un titre |
| ♡ U+2661 | le cœur tracé de Tendrille, seul | décoration |

Inspirations : idées reprises de deux polices scriptes montrées par Danaé (voir `references/LISEZMOI.md`) ; non retenus pour Tendrille : trait sans contraste, lettres liées et inclinées, gardés comme piste pour les italiques.

## Styles et axes

- **Axe de graisse `wght`** : 300 à 700, Regular 400 par défaut. Masters Light (fût 58), Regular (fût 90), Bold (fût 150). Light réservé aux corps de 24 px et plus.
- **Italiques** : masters dédiés, inclinaison 9°, vraies formes italiques non liées (a à un étage, f à descendante), mêmes garanties anti-confusion.
- **Axe de grade `GRAD`** (jalon ultérieur) : −40 à 0, allège le texte clair sur fond sombre sans changer la chasse.
- Instances nommées : Light, Regular, Medium, SemiBold, Bold, et leurs italiques.

## Jeux de glyphes visés et points délicats

Paliers : **GF_Latin_Core** (324 glyphes) → **GF_Latin_Plus** (141 glyphes de symboles) → **GF_Latin_African** (557 glyphes).

### Core
- Capitales accentuées : diacritiques `.case`, plus bas et plus plats (É, À, Ç, Œ).
- Roumain : ș ț à virgule souscrite (U+0219, U+021B), distincte de la cédille turque ş.
- Tchèque et slovaque : caron en apostrophe sur ď ť ľ Ľ (`caronalt`).
- Letton : ķ ļ ņ ŗ à virgule souscrite, ģ à virgule retournée au-dessus.
- Turc : İ et ı, `locl` pour i → İ en capitales.
- Catalan `l·l`, néerlandais IJ, allemand ß et ẞ.
- Espaces françaises : insécable U+00A0 et **fine insécable U+202F à ajouter à la main** (absente du jeu Core).

### Plus
- Fractions (`frac`, `numr`, `dnom`), exposants et indices (`sups`, `subs`), chiffres tabulaires.
- Monnaies (₦ ₹ ₿ ₺ ₽…), flèches, signes mathématiques : formes simples et régulières, l'irrégularité y nuirait.

### African
- Lettres nouvelles à dessiner : ŋ Ŋ, ɛ Ɛ, ɔ Ɔ, ɓ Ɓ, ɗ Ɗ, ƙ Ƙ, ƴ Ƴ, ʋ Ʋ, ɣ Ɣ, ə Ə, ʒ Ʒ, etc.
- Accents empilés et combinés (point souscrit + grave, tons) : `mark` et `mkmk` indispensables.
- Ŋ : plusieurs formes selon les communautés ; choix et éventuelle variante locale à étudier à ce palier.
- ʼ (lettre apostrophe U+02BC) distincte de ’ (ponctuation).

## Accents et lettres du jeu Core

- **14 diacritiques combinants** dessinés à la plume (aigu, grave, circonflexe, caron, tilde, macron, brève, double aigu, rond, point, tréma, cédille, virgule souscrite, ogonek), avec une version `.case` plus plate pour les capitales et les minuscules à ascendante ; caron en apostrophe `caroncomb.alt` pour ď ľ ť Ľ.
- **Points suscrits et trémas en cœurs** dans Tendrille, ronds dans Tendrille Texte (cohérent avec les points du i et de la ponctuation).
- **145 lettres accentuées composées** automatiquement par `composer_accents.py`, plus leurs **variantes de fin de mot** (« été », « café » gardent leur ruban à cœur) ; ı ajouté aux lettres à ruban pour í ì î ï finals.
- **Ancres optiques** calculées sur le dessin réel : l'accent se centre sur l'encre de la zone médiane (40 à 80 % de la hauteur de la lettre), là où entrées, pieds et rubans ne décentrent pas la lettre ; ancre haute à l'ascendante pour b d h k l ; ogonek au flanc droit au-dessus du pied ; caron en apostrophe à droite du haut de la hampe.
- **Lettres dessinées** : œ Œ æ Æ (ligatures à flanc partagé ; le o et le e du œ se recouvrent sur une bonne hauteur, sinon un blanc en amande apparaît), ø Ø ł Ł đ Đ Ð ħ Ħ (lettre + barre), ð þ Þ ß ẞ, ı ȷ.
- **Correctif de construction** : le contour extérieur d'une boucle fermée est le plus grand, quel que soit le sens du tracé ; l'ancienne règle inversait les sens et creusait des trous quand une boucle (o de Tendrille Texte, 0, 8, ð, å) en chevauchait un autre trait.

## Symboles et accents isolés (fin du jeu Core)

- **Accents isolés** (´ ` ¨ ¯ ¸ ˆ ˇ ˘ ˙ ˚ ˛ ˜ ˝) : le même dessin que les diacritiques combinants, centré dans une chasse de 340 : ils restent identiques par construction.
- **Maths** (+ − × ÷ = < > ~ ^) alignées sur l'axe 320, milieu des chiffres ; les points du ÷ sont des cœurs dans Tendrille.
- **Puce •** : un cœur dans Tendrille, un rond plein dans Tendrille Texte (« tous les points sont des cœurs »).
- **¡ ¿** redessinés, pas retournés : leur cœur reste pointe en bas.
- **ª º ™ © ®** : petites lettres au squelette réduit et au trait allégé à 75 %, pour garder le poids.
- Couverture GF_Latin_Core : 100 % dans les deux familles.

## Crénage

- Mesuré par `crener.py` (méthode des surfaces, mêmes références que l'espacement, lues dans `PARAMETRES`), appliqué par classes (une lettre, ses composés et ses variantes `.fina`, `.ss01`, `.ss02`).
- Copie projet de l'outil adaptée : noms actuels des guillemets (`guillemetleft`), paires avec les lettres hautes et les ponctuations ! ? : ; à droite, option `--ajout` pour un écart voulu.
- **Tendrille** : écart minimal 60 entre deux encres (30 par défaut) : le crochet effilé du f et les entrées en délié se frôlaient (fl, fb, fk, f!, f’) ; donne aussi c + y, c + v, r + y autour de +90 à +110, vérifiés à l'œil (sans ce crénage, l'entrée du y touche le c).
- **rn / m** : écart voulu de +30 sur r + n, r + m, r + u dans Tendrille : recouvrement mesuré avec crénage de 71 % à 64 % (objectif sous 70 %) ; +45 donnait 57 % mais ouvrait un trou après le r. Tendrille Texte est déjà à 51 %.
- **Entre deux mots** (que le crénage ne voit pas, car une espace les sépare) : un cœur de fin de mot (`.fina`) ou de capitale à cœur (`.ss04`) mord sur l'espace d'au plus 40 unités ; au-delà, sa chasse s'élargit. Décision après retour (« dit Yvon » : le cœur du t touchait le Y) ; le cœur du t, porté par la barre, monte aussi moins haut (40 % de l'envol au lieu de 60 %).
- Résultat : 1 132 paires de classes (Tendrille), 777 (Tendrille Texte) ; contrôle visuel AVATAR, To, Va, LT, L’été, P., Ty, Yo, « Oui » à 48 px et texte courant à 20 et 28 px, sans puis avec crénage.

## Fonctions OpenType

| Fonction | Contenu | Écriture |
|---|---|---|
| `kern` | crénage par classes | `crener.py` |
| `mark`, `mkmk`, `ccmp` | accents par ancres, accents empilés | construction |
| `locl` | turc et azéri, roumain et moldave, catalan, néerlandais | à la main |
| `case` | ponctuation remontée au centre des capitales : tirets, parenthèses, crochets, accolades, guillemets, point médian, puce ; ¡ et ¿ posés sur la ligne (18 glyphes `.case` en composants) | `generateur.py` + `fonctions_opentype.py` |
| `tnum`, `zero` | chiffres tabulaires (`.tf` : chiffre centré dans la chasse du plus large), 0 barré ; proportionnels par défaut | `generateur.py` + `fonctions_opentype.py` |
| `frac`, `numr`, `dnom`, `sups`, `subs` | fractions, exposants, indices (palier Plus) | à la main |
| `calt` | alternances manuscrites ; rubans à cœur en fin de mot (Tendrille) | `fonctions_opentype.py` (bloc fins et débuts de mots ajouté au script du projet) |
| `ss01` | « a d'école » : a à un étage, aussi accentué (à â ä…) et en fin de mot | `generateur.py` + `composer_accents.py --variantes ss01 fina.ss01` |
| `ss02` | « Points ronds » (Tendrille) / « Points en cœur » (Texte) : inverse la forme de tous les points (i, j, ponctuation, ÷, puce, point suscrit, tréma) et des composés qui les portent | `generateur.py` + `variantes_composees.py` |
| `ss03` | hampes bouclées (b d h k l) | `fonctions_opentype.py` |
| `ss04` | « Capitales à cœur » : l'entrée de B D E F H J K L M N P R U V W Y devient un cœur suspendu au sommet du fût, penché de 20° (40° débordait sur la lettre précédente) ; choisi parmi trois essais (suspendu, couché à gauche, boucle d'entrée) ; pour les titres | `fonctions_opentype.py` |
| `ss05` | « Sans rubans de fin de mot » (Tendrille) : annule les formes de fin juste après `calt` | `fonctions_opentype.py` |

**Ordre des fonctions** : `calt` (fins de mots), puis `ss05` qui les annule, puis `case`, `tnum`, et les autres jeux. Chaque variante existe dans ses combinaisons (a.fina.ss01, ï.fina.ss02…), donc les fonctions se cumulent sans se gêner. Exemple : ss01 + ss02 + ss05 donne une Tendrille calme, à a d'école et points ronds, pour un texte scolaire.

Les ornements `ss03` et `ss04` sont **désactivés par défaut** ; `ss02` bascule la forme des points dans un sens ou dans l'autre ; `ss05` retire les rubans à cœur pour qui veut un texte plus calme.

## Méthode de dessin et outils

- Générateur paramétrique Python (`sources/generateur/generateur.py`) : chaque geste est un squelette tracé avec une plume elliptique inclinée ; le bord est calculé finement, puis ajusté en une courbe de Bézier par morceau de squelette (moindres carrés de Schneider), avec des bouts en demi-cercles exacts.
- Chaque trait reste un contour séparé dans les sources, avec un nombre de courbes qui ne dépend que du squelette : les masters restent compatibles pour la police variable. Les polices statiques sont construites depuis une copie (`build/statiques/`, script `statiques.py`) où les traits de chaque glyphe sont fusionnés et nettoyés (coordonnées entières, segments de moins de 6 unités et éclats de moins de 12 × 12 supprimés) ; la police variable gardera les traits séparés.
- Règle de dessin : un virage ne tourne jamais plus serré que la demi-épaisseur du trait, sinon le bord intérieur se plisse.
- Les ornements les plus libres (cœurs, capitales bouclées) pourront passer en import SVG si le code ne suffit pas.
- Ordre de dessin : familles de formes de la fiche de production.

## Rôles des deux familles

Décision prise après la première famille dessinée : l'ambiance voulue est plus romantique et élégante, ce qui demande un contraste marqué. Les rôles sont répartis :

| Famille | Usage | Contraste | Extrémités | Geste |
|---|---|---|---|---|
| **Tendrille** | texte à partir de 18 px, titres, citations | 1,7 (88 / 52), plume à 30° | effilées jusqu'à 25 %, levée de plume à 82 % sur les boucles | irrégularités, amorces et sorties de 55, alternances `calt` |
| **Tendrille Texte** | petites tailles (12 à 18 px), malvoyance, interfaces | 1,18 (90 / 76), plume à 12° | arrondies, effilements réduits à 35 % de ceux de Tendrille | aucune irrégularité, aucune amorce ni sortie (trop courtes, elles se lisent comme des défauts), pas d'alternances |

Les deux familles sortent du même générateur et partagent les métriques, les formes distinctives et les garanties anti-confusion. Tendrille Texte fonctionne partout, y compris dans les logiciels qui ignorent les axes personnalisés.

## Licence et publication (étape 6)

- SIL Open Font License 1.1, **sans nom réservé** (diffusion large, contributions et sous-ensembles web facilités ; reste compatible avec Google Fonts).
- Métadonnées vérifiées dans les polices construites : copyright, créatrice, fabricant, URL, licence et son URL, `fsType` 0 ; identifiant de fabricant « NONE » (un code à 4 lettres réservé auprès de Microsoft reste possible pour toutes les polices de Danaé, sans obligation).
- Version 0.200 (0.x tant que Plus, African, Bold et italiques manquent), dans la seule constante `VERSION` du générateur.
- Build reproductible : `requirements.txt` épinglé ; un clone propre reconstruit des tables glyf, hmtx, GSUB, GPOS, cmap et name identiques.
- Archive de version : `dist/Tendrille-0.200.zip` (polices, licence, FAQ, FONTLOG, auteurs, README et ses aperçus clair et sombre).
- Mention de crédit proposée (facultative) dans le README et le spécimen : « Police Tendrille par Danaé ALBRECHT--MARTIN — https://danaedev.fr ».
