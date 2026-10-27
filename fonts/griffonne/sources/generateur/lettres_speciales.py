"""Lettres spéciales de GF_Latin_Core, sans décomposition Unicode : ß ẞ ø Ø ł Ł đ Đ ð Ð þ Þ ħ Ħ ª º.

La plupart dérivent d'une lettre existante (ø = o + barre) : on reprend son dessin, chat compris,
sans le recopier. Retoucher le o retouche donc aussi le ø.
"""

from capitales import CAPITALE, HAUT, avec_chat, boucle, oreilles_capitale
from glyphes import (
    GLYPHES,
    METRIQUES,
    RAYON,
    Trait,
    felin,
    fut,
    glyphe,
    oreilles_panse,
    panse_ry,
    yeux,
)
from pinceau import ellipse, ligne, lisse, transformer

ASCENDANTE = METRIQUES["ascendante"]
DESCENDANTE = METRIQUES["descendante"]
HAUTEUR_X = METRIQUES["hauteur_x"]
EPAISSEUR_BARRE = 0.8   # barres ajoutées (ø, ł, đ) un peu plus fines que le fût


def dessin_de(nom: str):
    """(traits, chasse, ancres) d'une lettre déjà enregistrée."""
    return GLYPHES[nom][1]()


def barre(depart: tuple[float, float], arrivee: tuple[float, float]) -> Trait:
    return Trait([ligne(depart, arrivee)], epaisseur=EPAISSEUR_BARRE)


def derivee(nom: str, point_code: int, source: str, ajout):
    """Enregistre une lettre = la source + des traits ajoutés (ajout reçoit chasse et ancres)."""
    def dessiner():
        traits, chasse, ancres = dessin_de(source)
        return traits + ajout(chasse, ancres), chasse, ancres
    glyphe(nom, point_code)(dessiner)


# Lettres barrées ------------------------------------------------------------------

derivee("oslash", 0xF8, "o", lambda chasse, _: [barre((chasse / 2 - 235, -35), (chasse / 2 + 235, HAUTEUR_X + 35))])
derivee("Oslash", 0xD8, "O", lambda chasse, _: [barre((chasse / 2 - 330, -45), (chasse / 2 + 330, CAPITALE + 45))])

FUT_MINUSCULE = METRIQUES["approche"] + RAYON  # axe du fût gauche de l, h

derivee("lslash", 0x142, "l", lambda *_: [barre((FUT_MINUSCULE - 85, 330), (FUT_MINUSCULE + 95, 455))])
derivee("Lslash", 0x141, "L", lambda *_: [barre((FUT_MINUSCULE - 80, 290), (FUT_MINUSCULE + 140, 430))])
derivee("hbar", 0x127, "h", lambda *_: [barre((FUT_MINUSCULE - 90, 640), (FUT_MINUSCULE + 120, 644))])
derivee("dcroat", 0x111, "d", lambda _, ancres: [barre((ancres["top"][0] + 105, 640), (ancres["top"][0] + 300, 644))])


def barre_D(chasse, _):
    return [barre((FUT_MINUSCULE - 90, 370), (FUT_MINUSCULE + 150, 374))]


derivee("Dcroat", 0x110, "D", barre_D)
derivee("Eth", 0xD0, "D", barre_D)  # Ð islandais et Đ croate partagent la même forme


def barre_H(chasse, _):
    gauche, droite = FUT_MINUSCULE, chasse - RAYON - METRIQUES["approche"]
    return [barre((gauche - 70, 560), (droite + 70, 566))]


derivee("Hbar", 0x126, "H", barre_H)


# Lettres redessinées à partir de leurs parties ---------------------------------------------

@glyphe("thorn", 0xFE)
def dessiner_thorn():
    """þ : le p, dont le fût monte jusqu'à l'ascendante."""
    traits, chasse, ancres = dessin_de("p")
    return [fut(FUT_MINUSCULE, DESCENDANTE, ASCENDANTE)] + traits[1:], chasse, ancres


@glyphe("Thorn", 0xDE)
def dessiner_Thorn():
    x = FUT_MINUSCULE
    traits = avec_chat([fut(x, 0, CAPITALE), boucle(x, 565, 175, 330)],
                       oreilles_capitale(x), yeux(x + 175, 370, ecart=45, taille=0.45))
    return traits, x + 330 + RAYON + METRIQUES["approche_ronde"], {"top": (x + 165, CAPITALE), "bottom": (x + 165, 0)}


@glyphe("eth", 0xF0)
def dessiner_eth():
    """ð : une panse dont le flanc droit remonte en cou recourbé, barré ; yeux dans la panse."""
    rx, cy, ry = 205, HAUTEUR_X / 2, panse_ry()
    cx = METRIQUES["approche_ronde"] + RAYON + rx
    cou = Trait(lisse([(cx + rx, cy + 60), (cx + 170, 560), (cx + 40, 720), (cx - 110, ASCENDANTE + 20)]))
    traits = [ellipse(cx, cy, rx, ry), cou, barre((cx - 40, 590), (cx + 200, 700))]
    if felin("marque"):
        traits += yeux(cx, cy + 30)
    chasse = cx + rx + RAYON + METRIQUES["approche_ronde"]
    return traits, chasse, {"top": (cx, ASCENDANTE), "bottom": (cx, 0)}


@glyphe("germandbls", 0xDF)
def dessiner_eszett():
    """ß : boucle haute étroite, taille profonde, ventre OUVERT qui s'arrête loin du fût.

    Un ventre refermé contre le fût faisait lire un B (61 % de recouvrement).
    """
    x = FUT_MINUSCULE
    sommet = ASCENDANTE + METRIQUES["depassement"] - RAYON
    fond = RAYON - METRIQUES["depassement"]
    haut = Trait([ligne((x, RAYON), (x, 540)),
                  *lisse([(x, 540), (x + 15, sommet - 60), (x + 130, sommet), (x + 240, 660), (x + 215, 545), (x + 95, 470)])])
    ventre = Trait(lisse([(x + 95, 470), (x + 290, 405), (x + 335, 225), (x + 260, fond + 15), (x + 175, fond)]))
    traits = [haut, ventre]
    if felin("marque"):
        traits += oreilles_panse(x + 125, 590, 120, 140)
    return traits, x + 345 + RAYON + METRIQUES["approche_ronde"], {"top": (x + 170, ASCENDANTE), "bottom": (x + 170, 0)}


@glyphe("uni1E9E", 0x1E9E)
def dessiner_eszett_capital():
    """ẞ : toit plat, diagonale qui s'arrête loin du fût, ventre ouvert ; oreilles sur le fût.

    Sur le B, la panse se raccroche au fût : ici rien ne revient contre lui (sinon 65 % avec B).
    """
    x = FUT_MINUSCULE
    fond = RAYON - METRIQUES["depassement"]
    traits = [fut(x, 0, CAPITALE), Trait([ligne((x, HAUT), (x + 330, HAUT + 4))]),
              Trait([ligne((x + 330, HAUT + 4), (x + 175, 415))]),
              Trait(lisse([(x + 175, 415), (x + 345, 345), (x + 365, 175), (x + 260, fond + 10), (x + 175, fond)]))]
    return avec_chat(traits, oreilles_capitale(x)), x + 355 + RAYON + 50, {"top": (x + 180, CAPITALE), "bottom": (x + 180, 0)}


# Ordinaux ª º : la lettre réduite et surélevée, soulignée -------------------------------------------

ECHELLE_ORDINAL = 0.58
BASE_ORDINAL = 330


def ordinal(source: str):
    def dessiner():
        traits, chasse, _ = dessin_de(source)
        largeur = chasse * ECHELLE_ORDINAL
        reduits = transformer(traits, ECHELLE_ORDINAL, dx=40, dy=BASE_ORDINAL + 40)
        souligne = Trait([ligne((60, BASE_ORDINAL), (largeur + 20, BASE_ORDINAL + 3))], epaisseur=0.7)
        return reduits + [souligne], largeur + 80, {}
    return dessiner


glyphe("ordfeminine", 0xAA)(ordinal("a"))
glyphe("ordmasculine", 0xBA)(ordinal("o"))
