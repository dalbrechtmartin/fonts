"""Chiffres de Thornveil : alignés sur la hauteur de capitale, proportionnels, sans épine.

Pas d'épine sur les chiffres : dans une date ou un prix, une épine peut faire lire un 1 comme un 4.
Paires surveillées : 0/O (0 en losange étroit), 1/I/l (drapeau long et pied horizontal),
5/S (barre haute plate et angle vif), 6/G (tête montante, jamais de croix ni de crochet).
"""

from capitales import mesures
from primitives import Trou, bande, delie_bas, epaule, fut, glyphe, losange, trait


def ancres_chiffre(chasse: float, p: dict) -> dict:
    return {"top": (chasse / 2, p["hauteur_capitale"]), "bottom": (chasse / 2, 0)}


@glyphe("zero", 0x30)
def dessiner_zero(p):
    """0 : losange étroit (environ 70 % de la chasse du O)."""
    f, d, h, _, g, c = mesures(p)
    x0, x1 = g, g + 2 * f + c * 0.9
    milieu, demi = (x0 + x1) / 2, (x1 - x0) / 2
    epaisseur = p["delie"] * 1.6 + f * 0.15
    pente = (h * 0.22 + d) / demi
    haut_int, bas_int = h + d - epaisseur, -d + epaisseur
    cote_haut = haut_int - pente * (demi - f)
    cote_bas = bas_int + pente * (demi - f)
    contours = [
        [(milieu, h + d), (x1, h * 0.78), (x1, h * 0.22), (milieu, -d), (x0, h * 0.22), (x0, h * 0.78)],
        Trou([(milieu, haut_int), (x1 - f, cote_haut), (x1 - f, cote_bas), (milieu, bas_int),
              (x0 + f, cote_bas), (x0 + f, cote_haut)]),
    ]
    chasse = x1 + g
    return contours, chasse, ancres_chiffre(chasse, p)


@glyphe("one", 0x31)
def dessiner_one(p):
    """1 : drapeau long et pied horizontal."""
    f, d, h, hc, g, c = mesures(p)
    x = g + c * 0.55
    pied = p["delie"] * 1.4
    contours = [
        fut(x, -d, h + d, f),
        bande((g, h * 0.66), (x + f * 0.4, h + d), f * 0.3 + p["delie"]),
        bande((x - f * 0.7, -d + pied), (x + f * 1.7, -d + pied + hc * 0.15), pied),
    ]
    chasse = x + f * 1.7 + g
    return contours, chasse, ancres_chiffre(chasse, p)


@glyphe("two", 0x32)
def dessiner_two(p):
    f, d, h, hc, g, c = mesures(p)
    dr = g + f + c
    base = f * 0.25 + p["delie"]
    contours = [
        fut(g, h * 0.66, h + d, f * 0.5),
        epaule(g + f * 0.5, dr, h, f, p),
        fut(dr, h * 0.5, h + d, f),
        trait((dr + f * 0.5, h * 0.55), (g + f * 0.5, h * 0.05), f),
        bande((g, -d + base), (dr + f, -d + base + hc * 0.3), base),
    ]
    chasse = dr + f + g
    return contours, chasse, ancres_chiffre(chasse, p)


@glyphe("three", 0x33)
def dessiner_three(p):
    """3 : toit à tête en losange, côté droit continu, barre médiane soudée aux deux fûts droits."""
    f, d, h, hc, g, c = mesures(p)
    dr = g + f + c
    toit = f * 0.25 + p["delie"]
    contours = [
        bande((g + f * 0.3, h * 0.82), (dr, h + d), toit, debord=f * 0.3),
        losange(g + f * 0.3, h * 0.82 - toit / 2, f * 0.4, f * 0.5),
        fut(dr, h * 0.46, h + d, f),
        fut(dr, -d, h * 0.56, f),
        bande((g + f + c * 0.35, h * 0.52), (dr, h * 0.52 + hc * 0.3), p["delie"] * 1.5 + f * 0.15,
              debord=f * 0.3),
        delie_bas(g + f * 0.5, dr, f, p),
        fut(g, -d, h * 0.28, f * 0.5),
    ]
    chasse = dr + f + g
    return contours, chasse, ancres_chiffre(chasse, p)


@glyphe("four", 0x34)
def dessiner_four(p):
    f, d, h, hc, g, c = mesures(p)
    x = g + f * 0.55 + c * 0.9
    contours = [
        fut(x, -d, h + d, f),
        trait((x + f * 0.3, h + d), (g + f * 0.35, h * 0.3), f * 0.55),
        bande((g, h * 0.3), (x + f * 1.5, h * 0.3 + hc * 0.3), p["delie"] * 1.5 + f * 0.1),
    ]
    chasse = x + f * 1.5 + g
    return contours, chasse, ancres_chiffre(chasse, p)


@glyphe("five", 0x35)
def dessiner_five(p):
    """5 : barre haute plate et angle vif en haut à gauche (le distingue de S)."""
    f, d, h, hc, g, c = mesures(p)
    dr = g + f + c
    contours = [
        fut(g, h * 0.45, h + d, f),
        bande((g + f * 0.5, h + d - hc * 0.2), (dr + f, h + d), f * 0.25 + p["delie"]),
        bande((g + f, h * 0.5 + hc * 0.2), (dr, h * 0.58), p["delie"] * 1.5 + f * 0.15, debord=f * 0.3),
        fut(dr, -d, h * 0.58, f),
        delie_bas(g + f * 0.5, dr, f, p),
        fut(g, -d, h * 0.28, f * 0.5),
    ]
    chasse = dr + f + g
    return contours, chasse, ancres_chiffre(chasse, p)


@glyphe("six", 0x36)
def dessiner_six(p):
    """6 : tête épaisse qui monte vers la droite, sans crochet ni croix (le distingue de G)."""
    f, d, h, hc, g, c = mesures(p)
    dr = g + f + c
    haut_panse = h * 0.52
    contours = [
        fut(g, -d, h * 0.8, f),
        bande((g + f * 0.3, h * 0.78), (dr + f * 0.4, h + d), f * 0.25 + p["delie"], debord=f * 0.3),
        fut(dr, -d, haut_panse, f),
        bande((g + f, haut_panse - hc), (dr, haut_panse), f * 0.25 + p["delie"], debord=f * 0.3),
        delie_bas(g + f, dr, f, p),
    ]
    chasse = dr + f + g
    return contours, chasse, ancres_chiffre(chasse, p)


@glyphe("seven", 0x37)
def dessiner_seven(p):
    f, d, h, hc, g, c = mesures(p)
    dr = g + f + c
    contours = [
        fut(g, h * 0.7, h + d, f * 0.5),
        bande((g, h + d - hc * 0.3), (dr + f, h + d), f * 0.25 + p["delie"]),
        trait((dr + f * 0.5, h * 0.95), (g + f * 0.9, -d), f),
    ]
    chasse = dr + f + g
    return contours, chasse, ancres_chiffre(chasse, p)


@glyphe("eight", 0x38)
def dessiner_eight(p):
    """8 : panse haute plus étroite que la basse (taille pincée, le distingue de B et de 0)."""
    f, d, h, hc, g, c = mesures(p)
    dr = g + f + c
    retrait, f_haut = f * 0.25, f * 0.85
    haut_gauche, haut_droit = g + retrait, dr + f - retrait - f_haut
    contours = [
        fut(haut_gauche, h * 0.52, h + d, f_haut),
        fut(haut_droit, h * 0.52, h + d, f_haut),
        epaule(haut_gauche + f_haut, haut_droit, h, f_haut, p),
        bande((g + f * 0.5, h * 0.55), (dr + f * 0.5, h * 0.55 + hc * 0.3), p["delie"] * 1.5),
        fut(g, -d, h * 0.5, f),
        fut(dr, -d, h * 0.5, f),
        delie_bas(g + f, dr, f, p),
    ]
    chasse = dr + f + g
    return contours, chasse, ancres_chiffre(chasse, p)


@glyphe("nine", 0x39)
def dessiner_nine(p):
    f, d, h, hc, g, c = mesures(p)
    dr = g + f + c
    bas_droit = h * 0.12
    e = p["delie"] * 1.5
    contours = [
        fut(g, h * 0.42, h + d, f),
        fut(dr, bas_droit, h + d, f),
        epaule(g + f, dr, h, f, p),
        bande((g + f, h * 0.42 + hc * 0.3 + e), (dr, h * 0.42 + hc + e), e, debord=f * 0.3),
        bande((g, -d + e + hc * 0.2), (dr + f * 0.65, bas_droit + e), e),
    ]
    chasse = dr + f + g
    return contours, chasse, ancres_chiffre(chasse, p)


@glyphe("zero.zero")
def dessiner_zero_pointe(p):
    """Zéro pointé (fonction zero) : le losange central lève toute confusion avec O."""
    contours, chasse, ancres_zero = dessiner_zero(p)
    r = 25 + p["fut_capitale"] * 0.3
    return contours + [losange(chasse / 2, p["hauteur_capitale"] / 2, r * 0.8, r * 1.3)], chasse, ancres_zero
