"""Capitales de Thornveil : squelette lisible proche du romain, habillé de losanges.

Règles communes (documentation/specification.md) :
- une épine par lettre, à gauche à 45 % de la hauteur de capitale (règle des hauteurs) ;
- I, J, l et 1 différenciés : I porte des barres haute et basse, J une queue de diable.
"""

from parametres import HAUTEUR_EPINE
from primitives import (
    ancres,
    bande,
    bord_gauche_diagonale,
    coupe,
    delie_bas,
    epaule,
    epine,
    epine_reglee,
    forme_s,
    fut,
    glyphe,
    queue_diable,
    trait,
)


def mesures(p: dict):
    """Raccourcis : fût capitale, dépassement, hauteur de capitale, facette, approche, contrepoinçon."""
    f = p["fut_capitale"]
    return f, p["depassement_pointe"], p["hauteur_capitale"], coupe(f), p["approche"], p["contrepoincon"]


def deux_futs(p: dict, rapport_contrepoincon: float):
    """Abscisses des deux fûts (gauche, droite) et chasse d'une capitale à deux fûts."""
    f, _, _, _, g, c = mesures(p)
    droite = g + f + c * rapport_contrepoincon
    return g, droite, droite + f + g


def barre(x_depart: float, x_arrivee: float, y: float, p: dict) -> list:
    """Barre horizontale en délié, légèrement montante (plume à 40°)."""
    f, _, _, hc, _, _ = mesures(p)
    return bande((x_depart, y), (x_arrivee, y + hc * 0.3), p["delie"] * 1.4, debord=f * 0.3)


def epine_diagonale(haut, bas, largeur: float, p: dict) -> list:
    """Épine gauche posée sur le bord d'une diagonale, selon la règle des hauteurs."""
    y = p["hauteur_capitale"] * HAUTEUR_EPINE[-1]
    return epine(bord_gauche_diagonale(haut, bas, largeur, y), y, -1, p)


@glyphe("A", 0x41)
def dessiner_A(p):
    """A : jambe droite verticale, jambe gauche en diagonale plus fine, barre basse."""
    f, d, h, _, g, c = mesures(p)
    dr = g + f * 0.5 + c * 1.6
    haut, bas = (dr - f * 0.1, h + d), (g + f * 0.3, -d)
    contours = [
        fut(dr, -d, h + d, f),
        trait(haut, bas, f * 0.55),
        barre(bord_gauche_diagonale(haut, bas, f * 0.55, h * 0.38) + f * 0.3, dr, h * 0.38, p),
        epine_diagonale(haut, bas, f * 0.55, p),
    ]
    chasse = dr + f + g
    # accents centrés sur la pointe du A, qui est à droite
    return contours, chasse, {"top": (dr - f * 0.1, h), "bottom": (chasse / 2, 0), "ogonek": (dr + f * 0.65, 0)}


@glyphe("B", 0x42)
def dessiner_B(p):
    """B : deux panses, la basse plus large."""
    f, d, h, hc, g, c = mesures(p)
    haut_droit, bas_droit = g + f + c * 1.2, g + f + c * 1.45
    contours = [
        fut(g, -d, h + d, f),
        fut(haut_droit, h * 0.55, h + d, f),
        fut(bas_droit, -d, h * 0.52, f),
        epaule(g + f, haut_droit, h, f, p),
        bande((g + f, h * 0.55), (bas_droit, h * 0.55 + hc * 0.4), p["delie"] * 1.5, debord=f * 0.3),
        delie_bas(g + f, bas_droit, f, p),
        epine_reglee(g, h, -1, p),
    ]
    chasse = bas_droit + f + g
    return contours, chasse, ancres(chasse, h)


@glyphe("C", 0x43)
def dessiner_C(p):
    """C : ouvert à droite, crochet en haut à droite."""
    f, d, h, hc, g, c = mesures(p)
    droite = g + f + c * 1.6
    crochet = f * 0.5
    contours = [
        fut(g, -d, h + d, f),
        epaule(g + f, droite - crochet, h, f, p),
        fut(droite - crochet, h * 0.7, h + d, crochet),
        bande((g + f, -d + p["delie"] * 1.5), (droite, hc * 0.8), p["delie"] * 1.5, debord=f * 0.3),
        epine_reglee(g, h, -1, p),
    ]
    chasse = droite + g
    return contours, chasse, ancres(chasse, h)


@glyphe("D", 0x44)
def dessiner_D(p):
    """D : dos gauche droit, côté droit chanfreiné (le distingue de O)."""
    f, d, h, _, g, c = mesures(p)
    dr = g + f + c * 1.7
    toit = f * 0.25 + p["delie"]
    contours = [
        fut(g, -d, h + d, f),
        fut(dr, h * 0.12, h * 0.88, f),
        bande((g, h + d), (dr + f * 0.5, h * 0.88), toit, debord=f * 0.3),
        bande((g + f, -d + p["delie"] * 1.5), (dr + f * 0.5, h * 0.12 + p["delie"] * 1.5), p["delie"] * 1.5,
              debord=f * 0.3),
        epine_reglee(g, h, -1, p),
    ]
    chasse = dr + f + g
    return contours, chasse, ancres(chasse, h)


def peigne_E(p: dict, avec_bas: bool):
    """Fût, barre haute à crochet, barre médiane ; barre basse à crochet pour E."""
    f, d, h, _, g, c = mesures(p)
    droite = g + f + c * 1.35
    crochet = f * 0.5
    contours = [
        fut(g, -d, h + d, f),
        epaule(g + f, droite - crochet, h, f, p),
        fut(droite - crochet, h * 0.74, h + d, crochet),
        barre(g + f, g + f + c * 0.95, h * 0.5, p),
    ]
    if avec_bas:
        contours += [
            delie_bas(g + f, droite - crochet, f, p),
            fut(droite - crochet, -d, h * 0.26, crochet),
        ]
    contours.append(epine_reglee(g, h, -1, p))
    return contours, droite + g


@glyphe("E", 0x45)
def dessiner_E(p):
    contours, chasse = peigne_E(p, avec_bas=True)
    ogonek = (chasse - p["approche"] - p["fut_capitale"] * 0.18, 0)
    return contours, chasse, {**ancres(chasse, p["hauteur_capitale"]), "ogonek": ogonek}


@glyphe("F", 0x46)
def dessiner_F(p):
    contours, chasse = peigne_E(p, avec_bas=False)
    return contours, chasse, ancres(chasse, p["hauteur_capitale"])


@glyphe("G", 0x47)
def dessiner_G(p):
    """G : fût droit qui dépasse au-dessus de la barre, barre qui traverse le fût (jamais une boucle de 6)."""
    f, d, h, _, g, c = mesures(p)
    droite = g + f + c * 1.6
    crochet = f * 0.5
    y_barre = h * 0.46
    contours = [
        fut(g, -d, h + d, f),
        epaule(g + f, droite - crochet, h, f, p),
        fut(droite - crochet, h * 0.62, h + d, crochet),
        fut(droite - f, -d, h * 0.6, f),
        delie_bas(g + f, droite - f, f, p),
        barre(droite - f - c * 0.5, droite + f * 0.35, y_barre, p),
        epine_reglee(g, h, -1, p),
    ]
    chasse = droite + f * 0.35 + g
    return contours, chasse, ancres(chasse, h)


@glyphe("H", 0x48)
def dessiner_H(p):
    """H : barre en délié, épine à gauche."""
    f, d, h, _, _, _ = mesures(p)
    g, dr, chasse = deux_futs(p, 1.7)
    contours = [fut(g, -d, h + d, f), fut(dr, -d, h + d, f), barre(g + f, dr, h * 0.5, p), epine_reglee(g, h, -1, p)]
    return contours, chasse, ancres(chasse, h)


@glyphe("I", 0x49)
def dessiner_I(p):
    """I : barres haute et basse de part et d'autre du fût (le distinguent de l et de 1)."""
    f, d, h, hc, g, _ = mesures(p)
    x = g + f * 0.45
    epaisseur = p["delie"] * 1.4
    gauche, droite = x - f * 0.45, x + f * 1.45
    contours = [
        fut(x, -d, h + d, f),
        bande((gauche, h + d - hc * 0.3), (droite, h + d), epaisseur),
        bande((gauche, -d + epaisseur), (droite, -d + epaisseur + hc * 0.3), epaisseur),
        epine_reglee(x, h, -1, p),
    ]
    chasse = droite + g
    return contours, chasse, {**ancres(chasse, h), "ogonek": (x + f * 0.65, 0)}


@glyphe("J", 0x4A)
def dessiner_J(p):
    """J : descend sous la ligne et finit en queue de diable (le distingue de I)."""
    f, d, h, _, g, _ = mesures(p)
    x = g + f * 1.2
    bas_fut = p["descendante"] * 0.45
    contours = [
        fut(x, bas_fut, h + d, f),
        *queue_diable((x + f * 0.65, bas_fut + p["delie"] * 1.5), (x - f * 1.4, p["descendante"] * 0.3), p),
        epine_reglee(x, h, -1, p),
    ]
    chasse = x + f + g
    return contours, chasse, ancres(chasse, h)


@glyphe("K", 0x4B)
def dessiner_K(p):
    """K : bras et jambe en diagonales depuis le milieu du fût."""
    f, d, h, _, g, c = mesures(p)
    contours = [
        fut(g, -d, h + d, f),
        trait((g + f * 0.6, h * 0.42), (g + f + c * 1.2, h + d), f * 0.7),
        trait((g + f + c * 0.25, h * 0.5), (g + f + c * 1.3, -d), f),
        epine_reglee(g, h, -1, p),
    ]
    chasse = g + f + c * 1.3 + f * 0.5 + g
    return contours, chasse, ancres(chasse, h)


@glyphe("L", 0x4C)
def dessiner_L(p):
    """L : barre basse terminée par un crochet montant."""
    f, d, h, _, g, c = mesures(p)
    droite = g + f + c * 1.2
    crochet = f * 0.5
    contours = [
        fut(g, -d, h + d, f),
        delie_bas(g + f, droite - crochet, f, p),
        fut(droite - crochet, -d, h * 0.26, crochet),
        epine_reglee(g, h, -1, p),
    ]
    chasse = droite + g
    return contours, chasse, {**ancres(chasse, h), "caronalt": (g + f + 30, h)}  # Ľ


@glyphe("M", 0x4D)
def dessiner_M(p):
    """M : trois fûts, deux épaules."""
    f, d, h, _, g, c = mesures(p)
    x2 = g + f + c * 1.05
    x3 = x2 + f + c * 1.05
    contours = [
        fut(g, -d, h + d, f), fut(x2, -d, h + d, f), fut(x3, -d, h + d, f),
        epaule(g + f, x2, h, f, p), epaule(x2 + f, x3, h, f, p),
        epine_reglee(g, h, -1, p),
    ]
    chasse = x3 + f + g
    return contours, chasse, ancres(chasse, h)


@glyphe("N", 0x4E)
def dessiner_N(p):
    """N : diagonale épaisse descendante entre deux fûts plus fins."""
    f, d, h, _, _, _ = mesures(p)
    g, dr, chasse = deux_futs(p, 1.7)
    fin = f * 0.6
    contours = [
        fut(g, -d, h + d, fin),
        fut(dr + f - fin, -d, h + d, fin),
        trait((g + f * 0.5, h + d - coupe(f) * 0.5), (dr + f * 0.5, -d + coupe(f) * 0.5), f),
        epine_reglee(g, h, -1, p),
    ]
    return contours, chasse, ancres(chasse, h)


@glyphe("O", 0x4F)
def dessiner_O(p):
    """O : comme o en plus large."""
    f, d, h, _, _, _ = mesures(p)
    g, dr, chasse = deux_futs(p, 1.9)
    contours = [
        fut(g, -d, h + d, f), fut(dr, -d, h + d, f),
        epaule(g + f, dr, h, f, p), delie_bas(g + f, dr, f, p),
        epine_reglee(g, h, -1, p),
    ]
    return contours, chasse, ancres(chasse, h)


def boucle_P(p: dict):
    """Fût et panse haute communs à P et R ; renvoie aussi l'abscisse du fût de panse."""
    f, d, h, hc, g, c = mesures(p)
    droite = g + f + c * 1.35
    contours = [
        fut(g, -d, h + d, f),
        fut(droite, h * 0.42, h + d, f),
        epaule(g + f, droite, h, f, p),
        bande((g + f, h * 0.42), (droite, h * 0.42 + hc), p["delie"] * 1.5, debord=f * 0.3),
        epine_reglee(g, h, -1, p),
    ]
    return contours, droite


@glyphe("P", 0x50)
def dessiner_P(p):
    contours, droite = boucle_P(p)
    chasse = droite + p["fut_capitale"] + p["approche"]
    return contours, chasse, ancres(chasse, p["hauteur_capitale"])


@glyphe("Q", 0x51)
def dessiner_Q(p):
    """Q : O avec une queue en diagonale qui sort en bas à droite."""
    f, d, h, _, _, c = mesures(p)
    g, dr, chasse = deux_futs(p, 1.9)
    contours = [
        fut(g, -d, h + d, f), fut(dr, -d, h + d, f),
        epaule(g + f, dr, h, f, p), delie_bas(g + f, dr, f, p),
        trait((dr - c * 0.4, h * 0.18), (dr + f * 1.1, -d - 90), f * 0.55),
        epine_reglee(g, h, -1, p),
    ]
    return contours, chasse, ancres(chasse, h)


@glyphe("R", 0x52)
def dessiner_R(p):
    """R : P avec une jambe diagonale."""
    f, d, h, _, g, c = mesures(p)
    contours, droite = boucle_P(p)
    contours.append(trait((g + f + c * 0.55, h * 0.45), (droite + f * 0.6, -d), f))
    chasse = droite + f + f * 0.2 + g
    return contours, chasse, ancres(chasse, h)


@glyphe("S", 0x53)
def dessiner_S(p):
    """S (voir primitives.forme_s)."""
    contours, chasse = forme_s(p, p["hauteur_capitale"], p["fut_capitale"], p["contrepoincon"] * 1.15)
    return contours, chasse, ancres(chasse, p["hauteur_capitale"])


@glyphe("T", 0x54)
def dessiner_T(p):
    """T : fût centré, toit à crochets aux deux bouts."""
    f, d, h, _, g, c = mesures(p)
    droite = g + f * 2 + c * 1.3
    x = (g + droite) / 2 - f / 2
    crochet = f * 0.5
    toit = f * 0.25 + p["delie"]
    contours = [
        fut(x, -d, h * 0.9, f),
        bande((g, h + d - coupe(f) * 0.3), (droite, h + d), toit),
        fut(g, h * 0.74, h + d, crochet),
        fut(droite - crochet, h * 0.74, h + d, crochet),
        epine_reglee(x, h, -1, p),
    ]
    chasse = droite + g
    return contours, chasse, ancres(chasse, h)


@glyphe("U", 0x55)
def dessiner_U(p):
    f, d, h, _, _, _ = mesures(p)
    g, dr, chasse = deux_futs(p, 1.7)
    contours = [
        fut(g, -d, h + d, f), fut(dr, -d, h + d, f),
        delie_bas(g + f, dr, f, p, epaisseur=p["delie"] * 1.2),
        epine_reglee(g, h, -1, p),
    ]
    return contours, chasse, {**ancres(chasse, h), "ogonek": (dr + f * 0.65, 0)}


def pointe_V(x_gauche: float, x_droite: float, p: dict) -> list:
    """Fond en pointe de V et W : diagonale épaisse du pied gauche vers un fût droit court."""
    f, d, h, hc, _, _ = mesures(p)
    epaisseur = f * 0.5 + p["delie"]
    return bande((x_gauche, -d + epaisseur), (x_droite, h * 0.3 + hc), epaisseur, debord=f * 0.3)


@glyphe("V", 0x56)
def dessiner_V(p):
    f, d, h, _, _, _ = mesures(p)
    g, dr, chasse = deux_futs(p, 1.7)
    contours = [fut(g, -d, h + d, f), fut(dr, h * 0.3, h + d, f), pointe_V(g + f, dr, p), epine_reglee(g, h, -1, p)]
    return contours, chasse, ancres(chasse, h)


@glyphe("W", 0x57)
def dessiner_W(p):
    f, d, h, _, g, c = mesures(p)
    x2 = g + f + c * 1.05
    x3 = x2 + f + c * 1.05
    contours = [
        fut(g, -d, h + d, f), fut(x2, -d, h + d, f), fut(x3, h * 0.3, h + d, f),
        delie_bas(g + f, x2, f, p), pointe_V(x2 + f, x3, p),
        epine_reglee(g, h, -1, p),
    ]
    chasse = x3 + f + g
    return contours, chasse, ancres(chasse, h)


@glyphe("X", 0x58)
def dessiner_X(p):
    f, d, h, _, g, c = mesures(p)
    droite = g + 2 * f + c * 1.5
    haut, bas = (g + f / 2, h + d), (droite - f / 2, -d)
    contours = [
        trait(haut, bas, f),
        trait((g + f * 0.3, -d), (droite - f * 0.3, h + d), p["delie"] * 1.5),
        epine_diagonale(haut, bas, f, p),
    ]
    chasse = droite + g
    return contours, chasse, ancres(chasse, h)


@glyphe("Y", 0x59)
def dessiner_Y(p):
    """Y : bras épais et bras fin qui se rejoignent sur un fût court."""
    f, d, h, _, g, c = mesures(p)
    droite = g + 2 * f + c * 1.5
    milieu = (g + droite) / 2
    haut, bas = (g + f / 2, h + d), (milieu, h * 0.42)
    contours = [
        trait(haut, bas, f),
        trait((droite - f * 0.3, h + d), (milieu, h * 0.42), p["delie"] * 1.5),
        fut(milieu - f / 2, -d, h * 0.48, f),
        epine_diagonale(haut, bas, f, p),
    ]
    chasse = droite + g
    return contours, chasse, ancres(chasse, h)


@glyphe("Z", 0x5A)
def dessiner_Z(p):
    f, d, h, hc, g, c = mesures(p)
    droite = g + c * 1.5 + f * 1.2
    epaisseur = p["delie"] * 1.8 + f * 0.1
    haut, bas = (droite - f * 0.5, h + d - hc * 0.3), (g + f * 0.5, -d + hc * 0.3)
    contours = [
        bande((g, h + d - hc * 0.5), (droite, h + d), epaisseur),
        trait(haut, bas, f),
        bande((g, -d + epaisseur), (droite, -d + epaisseur + hc * 0.5), epaisseur),
        epine_diagonale(haut, bas, f, p),
    ]
    chasse = droite + g
    return contours, chasse, ancres(chasse, h)
