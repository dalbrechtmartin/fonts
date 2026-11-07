"""Minuscules d'Thornveil (a à z, ı, ȷ).

Règles communes (documentation/specification.md) :
- une épine par lettre, à gauche à 45 % de la hauteur d'x ; à droite à 70 % pour les lettres
  à épaule (h, m, n) ;
- n/u, b/d, p/q jamais en miroir ; pas de ſ long ni de r rotunda.
"""

import primitives
from parametres import HAUTEUR_EPINE
from primitives import (
    ancres,
    bande,
    bord_gauche_diagonale,
    coupe,
    epine,
    epine_reglee,
    forme_s,
    fourche,
    fut,
    glyphe,
    losange,
    queue_diable,
    trait,
)


def mesures(p: dict):
    """Raccourcis : fût, dépassement, hauteur d'x, facette, approche, contrepoinçon."""
    f = p["fut"]
    return f, p["depassement_pointe"], p["hauteur_x"], coupe(f), p["approche"], p["contrepoincon"]


def epaule(x_depart: float, x_arrivee: float, p: dict) -> list:
    """Épaule à la hauteur d'x (voir primitives.epaule)."""
    return primitives.epaule(x_depart, x_arrivee, p["hauteur_x"], p["fut"], p)


def delie_bas(x_depart: float, x_arrivee: float, p: dict, epaisseur: float | None = None) -> list:
    """Délié bas des minuscules (voir primitives.delie_bas)."""
    return primitives.delie_bas(x_depart, x_arrivee, p["fut"], p, epaisseur)


def point_i(x_centre: float, p: dict) -> list:
    """Point du i et du j : losange net, placé haut."""
    f, d, h, _, _, _ = mesures(p)
    rayon = 30 + f * 0.4
    return losange(x_centre, h + d + 70 + rayon, rayon * 0.85, rayon)


def deux_futs(p: dict, contrepoincon: float | None = None):
    """Abscisses des deux fûts (gauche, droite) et chasse d'une lettre à deux fûts."""
    f, _, _, _, g, c = mesures(p)
    droite = g + f + (c if contrepoincon is None else contrepoincon)
    return g, droite, droite + f + g


@glyphe("a", 0x61)
def dessiner_a(p):
    """a à deux étages : tête en biais, panse fermée en bas à gauche."""
    f, d, h, hc, _, _ = mesures(p)
    g, dr, chasse = deux_futs(p)
    haut_panse = h * 0.58
    contours = [
        fut(dr, -d, h + d, f),
        fut(g, -d, haut_panse, f),
        bande((g + f * 0.3, h * 0.8), (dr, h + d), f * 0.25 + p["delie"], debord=f * 0.3),
        losange(g + f * 0.3, h * 0.8 - (f * 0.25 + p["delie"]) / 2, f * 0.4, f * 0.5),
        bande((g + f, haut_panse - hc), (dr, haut_panse), p["delie"] * 1.5 + f * 0.15, debord=f * 0.3),
        delie_bas(g + f, dr, p),
        epine_reglee(g, h, -1, p),
    ]
    return contours, chasse, {**ancres(chasse, h), "ogonek": (dr + f * 0.65, 0)}


@glyphe("b", 0x62)
def dessiner_b(p):
    """b : haste à sommet fourchu, panse anguleuse."""
    f, d, h, _, _, _ = mesures(p)
    g, dr, chasse = deux_futs(p)
    haut = p["ascendante"] + d
    contours = [
        fut(g, -d, haut, f),
        fourche(g, haut, f, p),
        fut(dr, -d, h + d, f),
        bande((g + f, h * 0.72), (dr, h + d), f * 0.25 + p["delie"], debord=f * 0.3),
        delie_bas(g + f, dr, p),
        epine_reglee(g, h, -1, p),
    ]
    return contours, chasse, ancres(chasse, p["ascendante"])


@glyphe("c", 0x63)
def dessiner_c(p):
    """c : ouvert à droite, petit crochet en haut à droite."""
    f, d, h, hc, g, c = mesures(p)
    droite = g + f + c * 0.85
    crochet = f * 0.5
    contours = [
        fut(g, -d, h + d, f),
        epaule(g + f, droite - crochet, p),
        fut(droite - crochet, h * 0.62, h + d, crochet),
        bande((g + f, -d + p["delie"] * 1.5), (droite, hc * 0.8), p["delie"] * 1.5, debord=f * 0.3),
        epine_reglee(g, h, -1, p),
    ]
    chasse = droite + g
    return contours, chasse, ancres(chasse, h)


@glyphe("d", 0x64)
def dessiner_d(p):
    """d oncial : haste diagonale penchée à gauche (jamais le miroir de b)."""
    f, d, h, _, _, c = mesures(p)
    g, dr, chasse = deux_futs(p)
    contours = [
        fut(g, -d, h + d, f),
        fut(dr, -d, h + d, f),
        epaule(g + f, dr, p),
        trait((dr + f * 0.5, h * 0.7), (g + f + c * 0.15, p["ascendante"] + d), f),
        delie_bas(g + f, dr, p),
        epine_reglee(g, h, -1, p),
    ]
    # caron en apostrophe (ď) au-dessus de la panse, hors de la haste penchée
    caron = (dr + f * 0.8, p["ascendante"])
    return contours, chasse, {**ancres(chasse, h), "caronalt": caron}


@glyphe("e", 0x65)
def dessiner_e(p):
    """e : œil fermé en haut, ouvert en bas à droite."""
    f, d, h, hc, g, c = mesures(p)
    dr = g + f + c * 0.9
    contours = [
        fut(g, -d, h + d, f),
        epaule(g + f, dr, p),
        fut(dr, h * 0.42, h + d, f),
        bande((g + f, h * 0.45), (dr, h * 0.45 + hc * 0.4), p["delie"], debord=f * 0.3),
        bande((g + f, -d + p["delie"] * 1.5), (dr + f * 0.5, hc * 1.1), p["delie"] * 1.5, debord=f * 0.3),
        epine_reglee(g, h, -1, p),
    ]
    chasse = dr + f + g
    return contours, chasse, {**ancres(chasse, h), "ogonek": (dr + f * 0.5, 0)}


@glyphe("f", 0x66)
def dessiner_f(p):
    """f : crochet en haut à droite, barre à la hauteur d'x."""
    f, d, h, hc, g, c = mesures(p)
    x = g + f * 0.3
    haut = p["ascendante"] - 40
    contours = [
        fut(x, -d, haut, f),
        bande((x + f, haut - hc), (x + f + c * 0.7, p["ascendante"] + d), f * 0.25 + p["delie"], debord=f * 0.3),
        bande((x - f * 0.3, h), (x + f + c * 0.5, h + hc * 0.3), p["delie"] * 1.4),
        epine_reglee(x, h, -1, p),
    ]
    chasse = x + f + c * 0.45 + g
    return contours, chasse, ancres(chasse, p["ascendante"])


@glyphe("g", 0x67)
def dessiner_g(p):
    """g à un étage, queue de diable terminée en pique."""
    f, d, h, _, _, _ = mesures(p)
    g, dr, chasse = deux_futs(p)
    bas_fut = p["descendante"] * 0.6
    contours = [
        fut(g, -d, h + d, f),
        fut(dr, bas_fut, h + d, f),
        epaule(g + f, dr, p),
        delie_bas(g + f, dr, p),
        *queue_diable((dr + f * 0.65, bas_fut + p["delie"] * 1.5), (g - f * 0.1, p["descendante"] * 0.3), p),
        epine_reglee(g, h, -1, p),
    ]
    return contours, chasse, ancres(chasse, h)


@glyphe("h", 0x68)
def dessiner_h(p):
    """h : comme n, avec une ascendante fourchue ; épine à droite (lettre à épaule)."""
    f, d, h, _, _, _ = mesures(p)
    g, dr, chasse = deux_futs(p)
    haut = p["ascendante"] + d
    contours = [
        fut(g, -d, haut, f),
        fourche(g, haut, f, p),
        fut(dr, -d, h + d, f),
        epaule(g + f, dr, p),
        epine_reglee(dr + f, h, 1, p),
    ]
    return contours, chasse, ancres(chasse, p["ascendante"])


@glyphe("dotlessi", 0x131)
def dessiner_dotlessi(p):
    f, d, h, _, g, _ = mesures(p)
    chasse = g + f + g
    return ([fut(g, -d, h + d, f), epine_reglee(g, h, -1, p)], chasse,
            {**ancres(chasse, h), "ogonek": (g + f * 0.65, 0)})


@glyphe("i", 0x69)
def dessiner_i(p):
    contours, chasse, ancres_i = dessiner_dotlessi(p)
    return contours + [point_i(p["approche"] + p["fut"] * 0.5, p)], chasse, ancres_i


@glyphe("uni0237", 0x237)
def dessiner_dotlessj(p):
    """ȷ : descendante terminée par une queue de diable vers la gauche."""
    f, d, h, _, g, _ = mesures(p)
    x = g + f * 0.6
    bas_fut = p["descendante"] * 0.65
    contours = [
        fut(x, bas_fut, h + d, f),
        *queue_diable((x + f * 0.65, bas_fut + p["delie"] * 1.5), (x - f * 1.3, p["descendante"] * 0.3), p),
        epine_reglee(x, h, -1, p),
    ]
    chasse = x + f + g
    return contours, chasse, ancres(chasse, h)


@glyphe("j", 0x6A)
def dessiner_j(p):
    contours, chasse, ancres_j = dessiner_dotlessj(p)
    return contours + [point_i(p["approche"] + p["fut"] * 1.1, p)], chasse, ancres_j


@glyphe("k", 0x6B)
def dessiner_k(p):
    """k : bras épais qui monte, jambe en diagonale."""
    f, d, h, _, g, c = mesures(p)
    haut = p["ascendante"] + d
    contours = [
        fut(g, -d, haut, f),
        fourche(g, haut, f, p),
        trait((g + f * 0.6, h * 0.42), (g + f + c * 0.75, h + d), f * 0.75),
        trait((g + f + c * 0.15, h * 0.5), (g + f + c * 0.8, -d), f),
        epine_reglee(g, h, -1, p),
    ]
    chasse = g + f + c * 0.85 + f * 0.45 + g
    return contours, chasse, ancres(chasse, p["ascendante"])


@glyphe("l", 0x6C)
def dessiner_l(p):
    """l : sommet fourchu et pied en délié (se distingue de I et de 1)."""
    f, d, h, hc, g, c = mesures(p)
    haut = p["ascendante"] + d
    contours = [
        fut(g, -d, haut, f),
        fourche(g, haut, f, p),
        bande((g + f, -d + p["delie"] * 1.5), (g + f + c * 0.45, hc * 0.8), p["delie"] * 1.5, debord=f * 0.3),
        epine_reglee(g, h, -1, p),
    ]
    chasse = g + f + c * 0.3 + g
    caron = (g + f * 1.15 + p["ornement"] * 1.5 + 25, p["ascendante"])  # ľ
    return contours, chasse, {**ancres(chasse, p["ascendante"]), "caronalt": caron}


@glyphe("m", 0x6D)
def dessiner_m(p):
    """m : trois fûts, deux épaules ; épine à droite (lettre à épaule)."""
    f, d, h, _, g, c = mesures(p)
    contrepoincon = c * 0.85
    x2 = g + f + contrepoincon
    x3 = x2 + f + contrepoincon
    contours = [
        fut(g, -d, h + d, f),
        fut(x2, -d, h + d, f),
        fut(x3, -d, h + d, f),
        epaule(g + f, x2, p),
        epaule(x2 + f, x3, p),
        epine_reglee(x3 + f, h, 1, p),
    ]
    chasse = x3 + f + g
    return contours, chasse, ancres(chasse, h)


@glyphe("n", 0x6E)
def dessiner_n(p):
    """n : épaule épaisse et anguleuse, épine à droite : les deux le distinguent de u."""
    f, d, h, _, _, _ = mesures(p)
    g, dr, chasse = deux_futs(p)
    contours = [fut(g, -d, h + d, f), fut(dr, -d, h + d, f), epaule(g + f, dr, p), epine_reglee(dr + f, h, 1, p)]
    return contours, chasse, ancres(chasse, h)


@glyphe("o", 0x6F)
def dessiner_o(p):
    """o : deux fûts fermés en haut par l'épaule et en bas par un délié."""
    f, d, h, _, _, _ = mesures(p)
    g, dr, chasse = deux_futs(p)
    contours = [
        fut(g, -d, h + d, f), fut(dr, -d, h + d, f),
        epaule(g + f, dr, p), delie_bas(g + f, dr, p),
        epine_reglee(g, h, -1, p),
    ]
    return contours, chasse, ancres(chasse, h)


@glyphe("p", 0x70)
def dessiner_p(p):
    """p : descendante à gauche, panse fermée (jamais le miroir de q)."""
    f, d, h, _, _, _ = mesures(p)
    g, dr, chasse = deux_futs(p)
    contours = [
        fut(g, p["descendante"] - d, h + d, f), fut(dr, -d, h + d, f),
        epaule(g + f, dr, p), delie_bas(g + f, dr, p),
        epine_reglee(g, h, -1, p),
    ]
    return contours, chasse, ancres(chasse, h)


@glyphe("q", 0x71)
def dessiner_q(p):
    """q : descendante droite nue à droite."""
    f, d, h, _, _, _ = mesures(p)
    g, dr, chasse = deux_futs(p)
    contours = [
        fut(g, -d, h + d, f), fut(dr, p["descendante"] - d, h + d, f),
        epaule(g + f, dr, p), delie_bas(g + f, dr, p),
        epine_reglee(g, h, -1, p),
    ]
    return contours, chasse, ancres(chasse, h)


@glyphe("r", 0x72)
def dessiner_r(p):
    """r simple : drapeau terminé par une petite goutte taillée."""
    f, d, h, _, g, c = mesures(p)
    bout = g + f + c * 0.7
    goutte = f * 0.45
    contours = [
        fut(g, -d, h + d, f),
        epaule(g + f, bout - goutte, p),
        fut(bout - goutte, h * 0.7, h + d, goutte),
        epine_reglee(g, h, -1, p),
    ]
    chasse = g + f + c * 0.55 + g
    return contours, chasse, ancres(chasse, h)


@glyphe("s", 0x73)
def dessiner_s(p):
    """s rond (voir primitives.forme_s)."""
    contours, chasse = forme_s(p, p["hauteur_x"], p["fut"], p["contrepoincon"] * 0.75)
    return contours, chasse, ancres(chasse, p["hauteur_x"])


@glyphe("t", 0x74)
def dessiner_t(p):
    """t : tête un peu au-dessus de la hauteur d'x, barre, pied en délié."""
    f, d, h, hc, g, c = mesures(p)
    x = g + f * 0.3
    contours = [
        fut(x, -d, h + d + 70, f),
        bande((x - f * 0.3, h), (x + f + c * 0.5, h + hc * 0.3), p["delie"] * 1.4),
        bande((x + f, -d + p["delie"] * 1.5), (x + f + c * 0.5, hc * 0.8), p["delie"] * 1.5, debord=f * 0.3),
        epine_reglee(x, h, -1, p),
    ]
    chasse = x + f + c * 0.5 + g
    caron = (x + f + c * 0.55, h + d + 70)  # ť : au-delà de la barre
    return contours, chasse, {**ancres(chasse, h), "caronalt": caron}


@glyphe("u", 0x75)
def dessiner_u(p):
    """u : délié en bas (le distingue de n), épine à gauche."""
    f, d, h, _, _, _ = mesures(p)
    g, dr, chasse = deux_futs(p)
    contours = [
        fut(g, -d, h + d, f), fut(dr, -d, h + d, f),
        delie_bas(g + f, dr, p, epaisseur=p["delie"]),
        epine_reglee(g, h, -1, p),
    ]
    return contours, chasse, {**ancres(chasse, h), "ogonek": (dr + f * 0.65, 0)}


def pointe_v(x_gauche: float, x_droite: float, p: dict) -> list:
    """Fond en pointe de v et w : diagonale épaisse du pied gauche vers un fût droit court."""
    f, d, h, hc, _, _ = mesures(p)
    epaisseur = f * 0.5 + p["delie"]
    return bande((x_gauche, -d + epaisseur), (x_droite, h * 0.3 + hc), epaisseur, debord=f * 0.3)


@glyphe("v", 0x76)
def dessiner_v(p):
    """v : fût droit court (le distingue de u)."""
    f, d, h, _, _, _ = mesures(p)
    g, dr, chasse = deux_futs(p)
    contours = [
        fut(g, -d, h + d, f), fut(dr, h * 0.3, h + d, f),
        pointe_v(g + f, dr, p),
        epine_reglee(g, h, -1, p),
    ]
    return contours, chasse, ancres(chasse, h)


@glyphe("w", 0x77)
def dessiner_w(p):
    f, d, h, _, g, c = mesures(p)
    contrepoincon = c * 0.85
    x2 = g + f + contrepoincon
    x3 = x2 + f + contrepoincon
    contours = [
        fut(g, -d, h + d, f), fut(x2, -d, h + d, f), fut(x3, h * 0.3, h + d, f),
        delie_bas(g + f, x2, p),
        pointe_v(x2 + f, x3, p),
        epine_reglee(g, h, -1, p),
    ]
    chasse = x3 + f + g
    return contours, chasse, ancres(chasse, h)


@glyphe("x", 0x78)
def dessiner_x(p):
    """x : diagonale épaisse descendante, diagonale fine montante."""
    f, d, h, _, g, c = mesures(p)
    droite = g + 2 * f + c
    haut, bas = (g + f / 2, h + d), (droite - f / 2, -d)
    y_epine = h * HAUTEUR_EPINE[-1]
    contours = [
        trait(haut, bas, f),
        trait((g + f * 0.3, -d), (droite - f * 0.3, h + d), p["delie"] * 1.5),
        epine(bord_gauche_diagonale(haut, bas, f, y_epine), y_epine, -1, p),
    ]
    chasse = droite + g
    return contours, chasse, ancres(chasse, h)


@glyphe("y", 0x79)
def dessiner_y(p):
    """y : comme u, fût droit prolongé en queue de diable (le distingue de u et de g)."""
    f, d, h, _, _, _ = mesures(p)
    g, dr, chasse = deux_futs(p)
    bas_fut = p["descendante"] * 0.65
    contours = [
        fut(g, -d, h + d, f), fut(dr, bas_fut, h + d, f),
        delie_bas(g + f, dr, p),
        *queue_diable((dr + f * 0.65, bas_fut + p["delie"] * 1.5), (g - f * 0.1, p["descendante"] * 0.3), p),
        epine_reglee(g, h, -1, p),
    ]
    return contours, chasse, ancres(chasse, h)


@glyphe("z", 0x7A)
def dessiner_z(p):
    """z : barres en délié, diagonale épaisse."""
    f, d, h, hc, g, c = mesures(p)
    droite = g + c + f * 1.2
    barre = p["delie"] * 1.8 + f * 0.1
    haut, bas = (droite - f * 0.5, h + d - hc * 0.3), (g + f * 0.5, -d + hc * 0.3)
    y_epine = h * HAUTEUR_EPINE[-1]
    contours = [
        bande((g, h + d - hc * 0.5), (droite, h + d), barre),
        trait(haut, bas, f),
        bande((g, -d + barre), (droite, -d + barre + hc * 0.5), barre),
        epine(bord_gauche_diagonale(haut, bas, f, y_epine), y_epine, -1, p),
    ]
    chasse = droite + g
    return contours, chasse, ancres(chasse, h)
