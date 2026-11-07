"""Lettres spéciales de GF_Latin_Core : æ œ ø ß ẞ ð þ ł đ ħ ª º et leurs capitales.

Les ligatures (æ, œ) et lettres barrées réutilisent le dessin des lettres de base ; l'épine
de la seconde lettre d'une ligature est ôtée (une seule épine par lettre).
"""

import capitales
import minuscules
from primitives import (
    ancres,
    bande,
    coupe,
    decaler,
    delie_bas,
    echelle,
    epaule,
    epine_reglee,
    fourche,
    fut,
    glyphe,
    sans_epines,
    trait,
)


def epaisseur_barre(p: dict) -> float:
    return p["delie"] * 1.4 + p["fut"] * 0.15


def ligature(premiere, seconde, decalage: float, p: dict, hauteur: float):
    """Colle la seconde lettre (sans son épine) sur le fût droit de la première."""
    contours_1, _, _ = premiere(p)
    contours_2, chasse_2, _ = seconde(p)
    contours = contours_1 + decaler(sans_epines(contours_2), decalage, 0)
    chasse = decalage + chasse_2
    return contours, chasse, ancres(chasse, hauteur)


def x_droit_minuscule(p: dict) -> float:
    """Abscisse du fût droit d'une minuscule à deux fûts (a, o) moins l'approche de la seconde lettre."""
    _, droite, _ = minuscules.deux_futs(p)
    return droite - p["approche"]


@glyphe("ae", 0xE6)
def dessiner_ae(p):
    return ligature(minuscules.dessiner_a, minuscules.dessiner_e, x_droit_minuscule(p), p, p["hauteur_x"])


@glyphe("oe", 0x153)
def dessiner_oe(p):
    return ligature(minuscules.dessiner_o, minuscules.dessiner_e, x_droit_minuscule(p), p, p["hauteur_x"])


@glyphe("AE", 0xC6)
def dessiner_AE(p):
    f, g, c = p["fut_capitale"], p["approche"], p["contrepoincon"]
    pointe_A = g + f * 0.5 + c * 1.6  # fût droit du A
    return ligature(capitales.dessiner_A, capitales.dessiner_E, pointe_A - g, p, p["hauteur_capitale"])


@glyphe("OE", 0x152)
def dessiner_OE(p):
    _, droite, _ = capitales.deux_futs(p, 1.9)
    return ligature(capitales.dessiner_O, capitales.dessiner_E, droite - p["approche"], p, p["hauteur_capitale"])


def barre_oblique(contours_ancres, hauteur: float, p: dict):
    """Lettre traversée d'une barre oblique fine (ø Ø)."""
    contours, chasse, _ = contours_ancres
    g, d = p["approche"], p["depassement_pointe"]
    barre = trait((g + p["fut"] * 0.2, -d - 50), (chasse - g - p["fut"] * 0.2, hauteur + d + 50),
                  p["delie"] * 1.5 + p["fut"] * 0.1)
    return contours + [barre], chasse, ancres(chasse, hauteur)


@glyphe("oslash", 0xF8)
def dessiner_oslash(p):
    return barre_oblique(minuscules.dessiner_o(p), p["hauteur_x"], p)


@glyphe("Oslash", 0xD8)
def dessiner_Oslash(p):
    return barre_oblique(capitales.dessiner_O(p), p["hauteur_capitale"], p)


def x_haste_d(y: float, p: dict) -> float:
    """Abscisse de l'axe de la haste penchée du d à la hauteur y."""
    f, h = p["fut"], p["hauteur_x"]
    _, droite, _ = minuscules.deux_futs(p)
    bas, haut = (droite + f * 0.5, h * 0.7), (p["approche"] + f + p["contrepoincon"] * 0.15,
                                               p["ascendante"] + p["depassement_pointe"])
    return bas[0] + (haut[0] - bas[0]) * (y - bas[1]) / (haut[1] - bas[1])


@glyphe("eth", 0xF0)
def dessiner_eth(p):
    """ð : d traversé d'une barre montante (islandais)."""
    contours, chasse, _ = minuscules.dessiner_d(p)
    y = 640
    x = x_haste_d(y, p)
    e = epaisseur_barre(p)
    return contours + [bande((x - 75, y - 20), (x + 75, y + 35), e)], chasse, ancres(chasse, p["hauteur_x"])


@glyphe("dcroat", 0x111)
def dessiner_dcroat(p):
    """đ : d traversé d'une barre horizontale (croate, vietnamien)."""
    contours, chasse, _ = minuscules.dessiner_d(p)
    y = 650
    x = x_haste_d(y, p)
    e = epaisseur_barre(p)
    return contours + [bande((x - 85, y + e / 2), (x + 85, y + e / 2), e)], chasse, ancres(chasse, p["hauteur_x"])


def D_barre(p):
    """Ð et Đ (même dessin) : D sans épine, barre qui traverse le fût et dépasse à gauche."""
    f, h, g = p["fut_capitale"], p["hauteur_capitale"], p["approche"]
    contours, chasse, _ = capitales.dessiner_D(p)
    e = epaisseur_barre(p)
    decalage = f * 0.45
    barre = bande((g, h * 0.5 + e / 2), (g + f * 1.9, h * 0.5 + e / 2 + coupe(f) * 0.2), e)
    return decaler(sans_epines(contours), decalage, 0) + [barre], chasse + decalage, ancres(chasse + decalage, h)


@glyphe("Eth", 0xD0)
def dessiner_Eth(p):
    return D_barre(p)


@glyphe("Dcroat", 0x110)
def dessiner_Dcroat(p):
    return D_barre(p)


@glyphe("hbar", 0x127)
def dessiner_hbar(p):
    """ħ : h barré sur l'ascendante."""
    f, g, h = p["fut"], p["approche"], p["hauteur_x"]
    contours, chasse, _ = minuscules.dessiner_h(p)
    y = h + (p["ascendante"] - h) * 0.45
    barre = bande((g - f * 0.45, y), (g + f * 1.45, y + coupe(f) * 0.2), epaisseur_barre(p))
    return contours + [barre], chasse, ancres(chasse, p["ascendante"])


@glyphe("Hbar", 0x126)
def dessiner_Hbar(p):
    """Ħ : H barré au-dessus de la traverse."""
    f, g, h = p["fut_capitale"], p["approche"], p["hauteur_capitale"]
    contours, chasse, _ = capitales.dessiner_H(p)
    _, droite, _ = capitales.deux_futs(p, 1.7)
    barre = bande((g - f * 0.35, h * 0.76), (droite + f * 1.35, h * 0.76 + coupe(f) * 0.2), epaisseur_barre(p))
    return contours + [barre], chasse, ancres(chasse, h)


@glyphe("lslash", 0x142)
def dessiner_lslash(p):
    """ł : barre montante au-dessus de l'épine."""
    f, g = p["fut"], p["approche"]
    contours, chasse, _ = minuscules.dessiner_l(p)
    barre = bande((g - f * 0.5, 380), (g + f * 1.5, 470), epaisseur_barre(p))
    return contours + [barre], chasse, ancres(chasse, p["ascendante"])


@glyphe("Lslash", 0x141)
def dessiner_Lslash(p):
    f, g, h = p["fut_capitale"], p["approche"], p["hauteur_capitale"]
    contours, chasse, _ = capitales.dessiner_L(p)
    barre = bande((g - f * 0.3, h * 0.62), (g + f * 1.4, h * 0.72), epaisseur_barre(p))
    return contours + [barre], chasse, ancres(chasse, h)


@glyphe("thorn", 0xFE)
def dessiner_thorn(p):
    """þ : fût de l'ascendante à la descendante, panse à la hauteur d'x."""
    f, d, h = p["fut"], p["depassement_pointe"], p["hauteur_x"]
    g, droite, chasse = minuscules.deux_futs(p)
    haut = p["ascendante"] + d
    contours = [
        fut(g, p["descendante"] - d, haut, f),
        fourche(g, haut, f, p),
        fut(droite, -d, h + d, f),
        epaule(g + f, droite, h, f, p),
        delie_bas(g + f, droite, f, p),
        epine_reglee(g, h, -1, p),
    ]
    return contours, chasse, ancres(chasse, p["ascendante"])


@glyphe("Thorn", 0xDE)
def dessiner_Thorn(p):
    """Þ : fût et panse suspendue au milieu."""
    f, d, h, hc, g, c = capitales.mesures(p)
    droite = g + f + c * 1.2
    e = p["delie"] * 1.5
    contours = [
        fut(g, -d, h + d, f),
        fut(droite, h * 0.2, h * 0.8, f),
        bande((g + f, h * 0.78), (droite, h * 0.8 + hc * 0.3), f * 0.25 + p["delie"], debord=f * 0.3),
        bande((g + f, h * 0.22 + e), (droite, h * 0.22 + hc * 0.5 + e), e, debord=f * 0.3),
        epine_reglee(g, h, -1, p),
    ]
    chasse = droite + f + g
    return contours, chasse, ancres(chasse, h)


def forme_eszett(p: dict, f: float, haut_tige: float, haut_dos: float, milieu: float, hauteur: float):
    """ß et ẞ : longue tige, dos en 3 sur la droite (barre médiane détachée de la tige)."""
    d, g, c = p["depassement_pointe"], p["approche"], p["contrepoincon"]
    droite = g + f + c * 0.85
    e = p["delie"] * 1.5
    contours = [
        fut(g, -d, haut_tige, f),
        epaule(g + f, droite, haut_dos - d, f, p),
        fut(droite, milieu, haut_dos, f),
        bande((g + f + c * 0.25, milieu + e), (droite, milieu + coupe(f) * 0.3 + e), e, debord=f * 0.3),
        fut(droite + f * 0.1, -d, milieu + coupe(f) * 0.4, f),
        delie_bas(g + f, droite + f * 0.1, f, p),
        epine_reglee(g, hauteur, -1, p),
    ]
    return contours, droite + f * 1.1 + g


@glyphe("germandbls", 0xDF)
def dessiner_germandbls(p):
    h = p["hauteur_x"]
    haut = p["ascendante"] - 30
    contours, chasse = forme_eszett(p, p["fut"], haut, haut, h * 0.58, h)
    return contours, chasse, ancres(chasse, p["ascendante"])


@glyphe("uni1E9E", 0x1E9E)
def dessiner_Germandbls(p):
    h, d = p["hauteur_capitale"], p["depassement_pointe"]
    contours, chasse = forme_eszett(p, p["fut_capitale"], h + d, h + d, h * 0.55, h)
    return contours, chasse, ancres(chasse, h)


def ordinal(lettre, p: dict):
    """ª º : lettre réduite, levée, soulignée."""
    facteur = 0.55
    g, h = p["approche"], p["hauteur_capitale"]
    contours, chasse_lettre, _ = lettre(p)
    largeur = chasse_lettre * facteur
    dy = h - p["hauteur_x"] * facteur - 10
    e = epaisseur_barre(p)
    trait_dessous = bande((g, dy - 50), (largeur - g * 0.5, dy - 50), e)
    contours = echelle(sans_epines(contours), facteur, g * 0.5, dy) + [trait_dessous]
    chasse = largeur + g
    return contours, chasse, ancres(chasse, h)


@glyphe("ordfeminine", 0xAA)
def dessiner_ordfeminine(p):
    return ordinal(minuscules.dessiner_a, p)


@glyphe("ordmasculine", 0xBA)
def dessiner_ordmasculine(p):
    return ordinal(minuscules.dessiner_o, p)
