"""Symboles de GF_Latin_Core : fonctionnels, sans chat, pour se reconnaître immédiatement (e-mail, code).

- Opérateurs (+ − × ÷ = < > ~) et devises : chasse des chiffres (600), centrés sur l'axe mathématique,
  pour s'aligner avec les chiffres tabulaires dans « 12 + 3 = 15 ».
- ¡ ¿ sont le ! et le ? retournés : retoucher l'un retouche l'autre.
"""

import math

from capitales import boucle
from glyphes import GLYPHES, METRIQUES, RAYON, Trait, glyphe
from pinceau import arc, ellipse, ligne, lisse, transformer
from ponctuation import LARGEUR_POINT, X_POINT, point, virgule

HAUTEUR_X = METRIQUES["hauteur_x"]
CHASSE_CHIFFRE = 600
CENTRE = CHASSE_CHIFFRE / 2
AXE = 340                 # axe mathématique : milieu des chiffres (hauteur 700)
EPAISSEUR = 0.9           # traits de symboles un peu plus légers que le fût
HAUT_CROCHET, BAS_CROCHET = 760, -140


def trait(*points, epaisseur: float = EPAISSEUR) -> Trait:
    return Trait([ligne(points[i], points[i + 1]) for i in range(len(points) - 1)], epaisseur=epaisseur)


def symbole(nom: str, point_code: int, chasse: float):
    def enregistrer(dessin):
        return glyphe(nom, point_code)(lambda: (dessin(), chasse, {}))
    return enregistrer


# Opérateurs ------------------------------------------------------------------

@symbole("plus", 0x2B, CHASSE_CHIFFRE)
def dessiner_plus():
    return [trait((CENTRE, AXE - 200), (CENTRE, AXE + 200)), trait((CENTRE - 200, AXE), (CENTRE + 200, AXE + 4))]


@symbole("minus", 0x2212, CHASSE_CHIFFRE)
def dessiner_moins():
    return [trait((CENTRE - 200, AXE), (CENTRE + 200, AXE + 4))]


@symbole("multiply", 0xD7, CHASSE_CHIFFRE)
def dessiner_fois():
    return [trait((CENTRE - 150, AXE - 150), (CENTRE + 150, AXE + 150)),
            trait((CENTRE - 150, AXE + 150), (CENTRE + 150, AXE - 150))]


@symbole("divide", 0xF7, CHASSE_CHIFFRE)
def dessiner_divise():
    return [trait((CENTRE - 200, AXE), (CENTRE + 200, AXE + 4)), point(CENTRE, AXE + 170), point(CENTRE, AXE - 170)]


@symbole("equal", 0x3D, CHASSE_CHIFFRE)
def dessiner_egal():
    return [trait((CENTRE - 200, AXE + 95), (CENTRE + 200, AXE + 99)), trait((CENTRE - 200, AXE - 95), (CENTRE + 200, AXE - 91))]


@symbole("less", 0x3C, CHASSE_CHIFFRE)
def dessiner_inferieur():
    return [trait((CENTRE + 180, AXE + 220), (CENTRE - 180, AXE)), trait((CENTRE - 180, AXE), (CENTRE + 180, AXE - 220))]


@symbole("greater", 0x3E, CHASSE_CHIFFRE)
def dessiner_superieur():
    return [trait((CENTRE - 180, AXE + 220), (CENTRE + 180, AXE)), trait((CENTRE + 180, AXE), (CENTRE - 180, AXE - 220))]


@symbole("asciitilde", 0x7E, CHASSE_CHIFFRE)
def dessiner_tilde_ascii():
    return [Trait(lisse([(CENTRE - 200, AXE - 30), (CENTRE - 95, AXE + 55), (CENTRE + 90, AXE - 50), (CENTRE + 200, AXE + 35)]),
                  epaisseur=EPAISSEUR)]


@symbole("asciicircum", 0x5E, CHASSE_CHIFFRE)
def dessiner_circonflexe_ascii():
    return [trait((CENTRE - 180, 400), (CENTRE, 700)), trait((CENTRE, 700), (CENTRE + 180, 400))]


@symbole("percent", 0x25, 680)
def dessiner_pourcent():
    return [Trait(ellipse(175, 555, 75, 105).segments, ferme=True, epaisseur=0.75),
            Trait(ellipse(505, 145, 75, 105).segments, ferme=True, epaisseur=0.75),
            trait((120, 30), (560, 670))]


@symbole("numbersign", 0x23, CHASSE_CHIFFRE)
def dessiner_diese():
    return [trait((205, 40), (255, 660)), trait((375, 40), (425, 660)),
            trait((95, 455), (505, 459)), trait((80, 245), (490, 249))]


# Devises ---------------------------------------------------------------------

@symbole("dollar", 0x24, CHASSE_CHIFFRE)
def dessiner_dollar():
    s = Trait(lisse([(450, 590), (310, 690), (155, 600), (200, 440), (400, 330), (455, 170), (300, 25), (135, 105)]))
    return [s, trait((CENTRE, -90), (CENTRE, 790), epaisseur=0.75)]


@symbole("cent", 0xA2, CHASSE_CHIFFRE)
def dessiner_cent():
    return [Trait(arc(CENTRE + 10, 300, 175, 230, 50, 312)), trait((CENTRE + 25, -40), (CENTRE + 5, 640), epaisseur=0.75)]


@symbole("sterling", 0xA3, CHASSE_CHIFFRE)
def dessiner_livre():
    corps = Trait(lisse([(470, 560), (400, 680), (270, 690), (200, 560), (215, 300), (150, 70)]))
    return [corps, trait((110, RAYON), (500, RAYON + 4)), trait((100, 350), (380, 354))]


@symbole("yen", 0xA5, CHASSE_CHIFFRE)
def dessiner_yen():
    return [trait((95, 674), (CENTRE, 360)), trait((505, 674), (CENTRE, 360)), trait((CENTRE, 360), (CENTRE, RAYON)),
            trait((135, 300), (465, 304), epaisseur=0.75), trait((135, 170), (465, 174), epaisseur=0.75)]


# Délimiteurs -----------------------------------------------------------------

@symbole("bracketleft", 0x5B, 330)
def dessiner_crochet_ouvrant():
    return [trait((250, HAUT_CROCHET), (125, HAUT_CROCHET), (125, BAS_CROCHET), (250, BAS_CROCHET))]


@symbole("bracketright", 0x5D, 330)
def dessiner_crochet_fermant():
    return [trait((80, HAUT_CROCHET), (205, HAUT_CROCHET), (205, BAS_CROCHET), (80, BAS_CROCHET))]


@symbole("braceleft", 0x7B, 360)
def dessiner_accolade_ouvrante():
    return [Trait(lisse([(285, HAUT_CROCHET), (185, 700), (185, 400), (105, 310)]), epaisseur=EPAISSEUR),
            Trait(lisse([(105, 310), (185, 220), (185, -80), (285, BAS_CROCHET)]), epaisseur=EPAISSEUR)]


@symbole("braceright", 0x7D, 360)
def dessiner_accolade_fermante():
    return [Trait(lisse([(75, HAUT_CROCHET), (175, 700), (175, 400), (255, 310)]), epaisseur=EPAISSEUR),
            Trait(lisse([(255, 310), (175, 220), (175, -80), (75, BAS_CROCHET)]), epaisseur=EPAISSEUR)]


@symbole("bar", 0x7C, 300)
def dessiner_barre_verticale():
    return [trait((150, BAS_CROCHET), (150, 780))]


@symbole("backslash", 0x5C, 420)
def dessiner_barre_inverse():
    return [trait((70, 760), (350, -110))]


@symbole("underscore", 0x5F, 500)
def dessiner_souligne():
    return [trait((30, -115), (470, -111))]


# Signes divers ---------------------------------------------------------------

@symbole("ampersand", 0x26, 680)
def dessiner_esperluette():
    return [Trait(lisse([(600, 30), (420, 210), (255, 420), (225, 570), (300, 690), (410, 665), (425, 560),
                         (340, 455), (170, 330), (120, 170), (235, 25), (400, 40), (560, 260)]))]


@symbole("asterisk", 0x2A, 500)
def dessiner_asterisque():
    cx, cy, r = 250, 560, 120
    return [trait((cx, cy - r), (cx, cy + r)), trait((cx - 104, cy - 60), (cx + 104, cy + 60)),
            trait((cx - 104, cy + 60), (cx + 104, cy - 60))]


@symbole("at", 0x40, 900)
def dessiner_arobase():
    interieur = Trait(ellipse(400, 300, 105, 130).segments, ferme=True, epaisseur=EPAISSEUR)
    # Le jambage finit là où commence l'anneau (angle -15°) : les deux traits se soudent
    cx, cy, rx, ry, depart = 430, 300, 340, 370, -15
    jonction = (cx + rx * math.cos(math.radians(depart)), cy + ry * math.sin(math.radians(depart)))
    rayon_jambage = (jonction[0] - 505) / 2
    jambage = Trait([ligne((505, 430), (505, jonction[1])),
                     *arc(505 + rayon_jambage, jonction[1], rayon_jambage, 100, 180, 360)], epaisseur=EPAISSEUR)
    exterieur = Trait(arc(cx, cy, rx, ry, depart, 300), epaisseur=EPAISSEUR)
    return [interieur, jambage, exterieur]


@symbole("section", 0xA7, 560)
def dessiner_paragraphe():
    return [Trait(lisse([(420, 640), (300, 710), (170, 630), (220, 510), (380, 430), (410, 300), (290, 225)]), epaisseur=EPAISSEUR),
            Trait(lisse([(280, 475), (160, 405), (150, 275), (310, 190), (380, 60), (260, -40), (140, 25)]), epaisseur=EPAISSEUR)]


@symbole("paragraph", 0xB6, 580)
def dessiner_pied_de_mouche():
    return [trait((330, -120), (330, 700)), trait((460, -120), (460, 700)), trait((330, 700), (480, 700)),
            Trait(arc(330, 515, 135, 185, 90, 270), epaisseur=1.6)]


@symbole("copyright", 0xA9, 820)
def dessiner_copyright():
    return [Trait(ellipse(410, 350, 335, 340).segments, ferme=True, epaisseur=0.75),
            Trait(arc(415, 350, 140, 155, 45, 315), epaisseur=0.8)]


@symbole("registered", 0xAE, 820)
def dessiner_marque_deposee():
    x = 320
    return [Trait(ellipse(410, 350, 335, 340).segments, ferme=True, epaisseur=0.75),
            Trait(boucle(x, 525, 360, 175).segments, epaisseur=0.8), trait((x, 525), (x, 170), epaisseur=0.8),
            trait((x + 95, 360), (x + 190, 175), epaisseur=0.8)]


@symbole("trademark", 0x2122, 620)
def dessiner_marque():
    e = 0.6
    return [trait((60, 700), (270, 702), epaisseur=e), trait((165, 700), (165, 430), epaisseur=e),
            trait((330, 430), (340, 700), (430, 520), (520, 700), (530, 430), epaisseur=e)]


@symbole("degree", 0xB0, 320)
def dessiner_degre():
    return [Trait(ellipse(160, 600, 75, 80).segments, ferme=True, epaisseur=0.6)]


@symbole("periodcentered", 0xB7, LARGEUR_POINT)
def dessiner_point_median():
    return [point(X_POINT, HAUTEUR_X / 2 + 20)]


@symbole("bullet", 0x2022, 420)
def dessiner_puce():
    return [Trait([ligne((205, AXE - 10), (215, AXE - 10))], epaisseur=2.0)]


@symbole("quotesinglbase", 0x201A, 220)
def dessiner_virgule_basse():
    return transformer(virgule(), dx=110 - X_POINT)


@symbole("quotedblbase", 0x201E, 360)
def dessiner_guillemets_bas():
    return transformer(virgule(), dx=115 - X_POINT) + transformer(virgule(), dx=245 - X_POINT)


# Retournés : ¡ ¿ ----------------------------------------------------------------

def retourne(source: str, hauteur: float):
    """Demi-tour de la source : son point se retrouve en haut (hauteur d'x), sa forme sous la ligne."""
    def dessiner():
        traits, chasse, _ = GLYPHES[source][1]()
        return transformer(traits, -1, dx=chasse, dy=hauteur), chasse, {}
    return dessiner


glyphe("exclamdown", 0xA1)(retourne("exclam", HAUTEUR_X))
glyphe("questiondown", 0xBF)(retourne("question", HAUTEUR_X))
