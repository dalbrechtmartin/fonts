"""Chiffres de Griffonne : alignés et tabulaires (même chasse pour tous, les colonnes s'alignent).

Règle unique pour toute la série (on lit les chiffres en colonnes, l'homogénéité prime) :
chaque chiffre déclare son point le plus haut, et le traitement félin s'y applique de la même façon.
Le 0 reste plus étroit que le O et sans yeux : il ne se confond pas avec la lettre.
"""

from glyphes import METRIQUES, RAYON, Trait, ancres_sur, felin, glyphe, oreilles
from pinceau import ellipse, ligne, lisse

HAUTEUR = 700                    # un peu sous la capitale (720) : les chiffres ne crient pas dans le texte
HAUT = HAUTEUR - RAYON
BAS = RAYON
SOMMET_ROND = HAUTEUR + METRIQUES["depassement"] - RAYON
FOND_ROND = -METRIQUES["depassement"] + RAYON
CHASSE = 600                     # chasse tabulaire commune
CENTRE = CHASSE / 2
ECHELLE_OREILLES = 1.2
CHAT_CHIFFRES = "oreilles"  # "oreilles" : même paire sur chaque chiffre ; "aucun" : chiffres neutres


def chiffre(nom: str, point_code: int):
    """Enregistre un chiffre : chasse tabulaire, ancres centrées, oreilles sur son point le plus haut."""
    def enregistrer(dessin):
        def dessiner():
            traits, sommet_x = dessin()
            if felin("marque") and CHAT_CHIFFRES == "oreilles":
                traits = traits + oreilles(sommet_x, HAUTEUR, echelle=ECHELLE_OREILLES)
            return traits, CHASSE, ancres_sur(CENTRE, HAUTEUR)
        return glyphe(nom, point_code)(dessiner)
    return enregistrer


@chiffre("zero", 0x30)
def dessiner_zero():
    return [ellipse(CENTRE, HAUTEUR / 2, 210 - RAYON, HAUTEUR / 2 + METRIQUES["depassement"] - RAYON)], CENTRE


@chiffre("one", 0x31)
def dessiner_un():
    """1 à drapeau franc : jamais confondu avec l ou I."""
    x = CENTRE + 40
    return [Trait([ligne((x, BAS), (x, HAUT))]), Trait([ligne((x, HAUT), (x - 170, HAUT - 135))])], x


@chiffre("two", 0x32)
def dessiner_deux():
    corps = Trait(lisse([(145, 530), (270, SOMMET_ROND - 2), (410, 645), (455, 520), (390, 360), (150, BAS + 5)]))
    return [corps, Trait([ligne((150, BAS), (460, BAS + 4))])], 285


@chiffre("three", 0x33)
def dessiner_trois():
    haut = Trait(lisse([(150, 590), (300, SOMMET_ROND), (450, 575), (410, 420), (270, 385)]))
    bas = Trait(lisse([(270, 385), (430, 335), (465, 185), (320, FOND_ROND), (140, 105)]))
    return [haut, bas], CENTRE


@chiffre("four", 0x34)
def dessiner_quatre():
    x = 400
    return [Trait([ligne((x, BAS), (x, HAUT))]), Trait([ligne((x, HAUT), (120, 230))]),
            Trait([ligne((120, 230), (505, 234))])], x


@chiffre("five", 0x35)
def dessiner_cinq():
    gauche = 175
    barre = Trait([ligne((gauche, HAUT), (465, HAUT + 4))])
    corps = Trait([ligne((gauche, HAUT), (165, 395)),
                   *lisse([(165, 395), (300, 450), (455, 355), (460, 190), (320, FOND_ROND), (140, 100)])])
    return [barre, corps], (gauche + 465) / 2


@chiffre("six", 0x36)
def dessiner_six():
    cy, rx, ry = 220, 165, 220 - FOND_ROND
    hampe = Trait(lisse([(430, 600), (300, SOMMET_ROND), (170, 520), (CENTRE - rx, cy + 40)]))
    return [hampe, ellipse(CENTRE, cy, rx, ry)], CENTRE


@chiffre("seven", 0x37)
def dessiner_sept():
    gauche = 140
    return [Trait([ligne((gauche, HAUT), (460, HAUT + 4))]), Trait([ligne((460, HAUT + 4), (235, BAS))])], (gauche + 460) / 2


@chiffre("eight", 0x38)
def dessiner_huit():
    haut_cy, haut_ry = 520, SOMMET_ROND - 520
    bas_cy, bas_ry = 190, 190 - FOND_ROND
    boucles = [ellipse(CENTRE, haut_cy, 140, haut_ry), ellipse(CENTRE, bas_cy, 165, bas_ry)]
    return boucles, CENTRE


@chiffre("nine", 0x39)
def dessiner_neuf():
    cy, rx = 480, 165
    ry = SOMMET_ROND - cy
    queue = Trait(lisse([(CENTRE + rx, cy - 30), (450, 250), (330, FOND_ROND), (165, 105)]))
    return [ellipse(CENTRE, cy, rx, ry), queue], CENTRE
