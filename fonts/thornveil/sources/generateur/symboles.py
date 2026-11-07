"""Symboles et accents isolés de GF_Latin_Core (sans épine, sauf les lettres réutilisées).

Signes mathématiques centrés sur un axe commun (AXE_MATH × hauteur de capitale) ;
accents isolés (¨ ´ ˆ…) tirés des mêmes formes que les diacritiques combinants ;
©, ®, ™, @ réutilisent les lettres dessinées, réduites et sans épine.
"""

import accents
import capitales
import minuscules
from primitives import (
    Trou,
    anneau,
    bande,
    chevron,
    decaler,
    delie_bas,
    echelle,
    epaule,
    forme_s,
    fut,
    glyphe,
    losange,
    miroir,
    sans_epines,
    trait,
)

AXE_MATH = 0.42  # + − = × ÷ < > partagent l'axe et la chasse largeur_math : les calculs s'alignent


def ancres(chasse: float, p: dict) -> dict:
    return {"top": (chasse / 2, p["hauteur_capitale"]), "bottom": (chasse / 2, 0)}


def epaisseur(p: dict) -> float:
    return p["delie"] * 1.2 + p["fut"] * 0.3


def largeur_math(p: dict) -> float:
    return p["contrepoincon"] * 1.2 + p["fut"]


def axe(p: dict) -> float:
    return p["hauteur_capitale"] * AXE_MATH


def barre_math(x: float, y: float, longueur: float, p: dict) -> list:
    e = epaisseur(p)
    return bande((x, y + e / 2), (x + longueur, y + e / 2), e)


def symbole(contours: list, largeur: float, p: dict):
    chasse = largeur + 2 * p["approche"]
    return decaler(contours, p["approche"], 0), chasse, ancres(chasse, p)


# Mathématiques ----------------------------------------------------------------------------

@glyphe("plus", 0x2B)
def dessiner_plus(p):
    L, e, y = largeur_math(p), epaisseur(p), axe(p)
    return symbole([barre_math(0, y, L, p), trait((L / 2, y - L / 2), (L / 2, y + L / 2), e)], L, p)


@glyphe("minus", 0x2212)
def dessiner_minus(p):
    L = largeur_math(p)
    return symbole([barre_math(0, axe(p), L, p)], L, p)


@glyphe("equal", 0x3D)
def dessiner_equal(p):
    L, y = largeur_math(p), axe(p)
    ecart = epaisseur(p) * 1.1
    return symbole([barre_math(0, y + ecart, L, p), barre_math(0, y - ecart, L, p)], L, p)


@glyphe("multiply", 0xD7)
def dessiner_multiply(p):
    L, e, y = largeur_math(p), epaisseur(p), axe(p)
    demi, marge = L * 0.4, L * 0.1  # croix réduite, centrée dans la chasse commune des signes
    return symbole([trait((marge + e / 2, y - demi), (L - marge - e / 2, y + demi), e),
                    trait((marge + e / 2, y + demi), (L - marge - e / 2, y - demi), e)], L, p)


@glyphe("divide", 0xF7)
def dessiner_divide(p):
    L, y = largeur_math(p), axe(p)
    r = accents.rayon_point(p)
    ecart = epaisseur(p) + r * 1.4
    return symbole([barre_math(0, y, L, p), accents.point(L / 2, y + ecart, p), accents.point(L / 2, y - ecart, p)],
                   L, p)


def comparaison(vers_gauche: bool, p: dict):
    """< > : chevron centré dans la chasse commune des signes mathématiques."""
    L, y = largeur_math(p), axe(p)
    epaisseur_chevron = p["fut"] * 0.6
    longueur = L - epaisseur_chevron
    contours = [chevron(0, y, longueur, L * 0.42, epaisseur_chevron)]
    if not vers_gauche:
        contours = miroir(contours, L / 2)
    return symbole(contours, L, p)


@glyphe("less", 0x3C)
def dessiner_less(p):
    return comparaison(True, p)


@glyphe("greater", 0x3E)
def dessiner_greater(p):
    return comparaison(False, p)


@glyphe("asciitilde", 0x7E)
def dessiner_asciitilde(p):
    L = largeur_math(p)
    forme = accents.forme_tilde(p, axe(p) - L * 0.2, L / 1.4)
    return symbole(decaler(forme, L / 2, 0), L, p)


@glyphe("underscore", 0x5F)
def dessiner_underscore(p):
    L = largeur_math(p)
    return symbole([barre_math(0, -120, L, p)], L, p)


@glyphe("percent", 0x25)
def dessiner_percent(p):
    L, h = largeur_math(p), p["hauteur_capitale"]
    r, e = L * 0.22, p["delie"] * 1.2 + p["fut"] * 0.15

    def rond(cx, cy):
        return [losange(cx, cy, r, r * 1.2), Trou(losange(cx, cy, r - e, r * 1.2 - e * 1.2))]

    contours = rond(r, h * 0.78) + rond(L - r, h * 0.22) + [trait((r * 0.6, -10), (L - r * 0.6, h + 10), e * 1.3)]
    return symbole(contours, L, p)


@glyphe("numbersign", 0x23)
def dessiner_numbersign(p):
    L, h = largeur_math(p), p["hauteur_capitale"]
    e = p["fut"] * 0.5
    inclinaison = L * 0.12
    contours = [trait((L * 0.3, 0), (L * 0.3 + inclinaison, h * 0.85), e),
                trait((L * 0.7 - inclinaison, 0), (L * 0.7, h * 0.85), e),
                barre_math(0, h * 0.28, L, p), barre_math(inclinaison, h * 0.56, L, p)]
    return symbole(contours, L + inclinaison, p)


@glyphe("backslash", 0x5C)
def dessiner_backslash(p):
    f, c = p["fut"], p["contrepoincon"]
    largeur = c + f * 0.7
    forme = [trait((f * 0.35, p["descendante"] * 0.6), (c + f * 0.35, p["ascendante"]), f * 0.7)]
    return symbole(miroir(forme, largeur / 2), largeur, p)


def accolade(p: dict):
    f, h = p["fut"], p["hauteur_capitale"]
    largeur, e = f * 0.9 + 20, f * 0.6
    x = f * 0.5
    contours = [
        fut(x, h * 0.48, h * 0.82, f * 0.8), fut(x, h * 0.02, h * 0.38, f * 0.8),
        trait((x + f * 0.4, h * 0.78), (x + largeur + f * 0.4, p["ascendante"]), e),
        trait((x + f * 0.4, h * 0.06), (x + largeur + f * 0.4, p["descendante"] * 0.6), e),
        trait((x + f * 0.4, h * 0.52), (0, h * 0.43), e), trait((0, h * 0.43), (x + f * 0.4, h * 0.34), e),
    ]
    return contours, x + largeur + f * 0.75


@glyphe("braceleft", 0x7B)
def dessiner_braceleft(p):
    contours, largeur = accolade(p)
    return symbole(contours, largeur, p)


@glyphe("braceright", 0x7D)
def dessiner_braceright(p):
    contours, largeur = accolade(p)
    return symbole(miroir(contours, largeur / 2), largeur, p)


@glyphe("degree", 0xB0)
def dessiner_degree(p):
    r = accents.rayon_point(p) * 1.6
    e = p["delie"] * 1.2 + p["fut"] * 0.1
    cy = p["hauteur_capitale"] - r
    return symbole([losange(r, cy, r, r), Trou(losange(r, cy, r - e * 1.2, r - e))], 2 * r, p)


# Monnaies ------------------------------------------------------------------------------------

@glyphe("dollar", 0x24)
def dessiner_dollar(p):
    contours, largeur = forme_s(p, p["hauteur_capitale"], p["fut_capitale"] * 0.9, p["contrepoincon"] * 0.9,
                                avec_epine=False)
    contours = decaler(contours, -p["approche"], 0)
    largeur -= 2 * p["approche"]
    e = p["delie"] * 1.4
    tige = fut(largeur / 2 - e / 2, -110, p["hauteur_capitale"] + 110, e)
    return symbole(contours + [tige], largeur, p)


@glyphe("cent", 0xA2)
def dessiner_cent(p):
    contours, chasse, _ = minuscules.dessiner_c(p)
    contours = decaler(sans_epines(contours), -p["approche"], 0)
    largeur = chasse - 2 * p["approche"]
    e = p["delie"] * 1.4
    tige = fut(largeur * 0.45 - e / 2, -90, p["hauteur_x"] + 110, e)
    return symbole(contours + [tige], largeur, p)


@glyphe("sterling", 0xA3)
def dessiner_sterling(p):
    """£ : fût à crochet en haut, barre qui traverse, base pleine largeur à crochet montant."""
    f, d, h, _, _, c = capitales.mesures(p)
    x = f * 0.45
    droite = x + f + c * 1.0
    crochet = f * 0.5
    contours = [
        fut(x, h * 0.08, h * 0.85, f),
        epaule(x + f, droite - crochet, h * 0.9, f, p),
        fut(droite - crochet, h * 0.66, h * 0.9 + d, crochet),
        barre_math(0, h * 0.45, x + f + c * 0.5, p),
        delie_bas(0, droite - crochet, f, p),
        fut(droite - crochet, -d, h * 0.24, crochet),
    ]
    return symbole(contours, droite, p)


@glyphe("yen", 0xA5)
def dessiner_yen(p):
    contours, chasse, _ = capitales.dessiner_Y(p)
    contours = decaler(sans_epines(contours), -p["approche"], 0)
    largeur = chasse - 2 * p["approche"]
    h = p["hauteur_capitale"]
    milieu = largeur / 2
    portee = p["contrepoincon"] * 0.55 + p["fut_capitale"] * 0.5
    contours += [barre_math(milieu - portee, h * 0.36, portee * 2, p), barre_math(milieu - portee, h * 0.18, portee * 2, p)]
    return symbole(contours, largeur, p)


@glyphe("Euro", 0x20AC)
def dessiner_Euro(p):
    contours, chasse, _ = capitales.dessiner_C(p)
    decalage = p["fut_capitale"] * 0.5
    contours = decaler(sans_epines(contours), decalage - p["approche"], 0)
    largeur = chasse - 2 * p["approche"] + decalage
    h = p["hauteur_capitale"]
    longueur = p["fut_capitale"] * 1.5 + p["contrepoincon"] * 0.9
    contours += [barre_math(0, h * 0.58, longueur, p), barre_math(0, h * 0.38, longueur, p)]
    return symbole(contours, largeur, p)


# Typographie ---------------------------------------------------------------------------------

@glyphe("ampersand", 0x26)
def dessiner_ampersand(p):
    """& : boucle haute, diagonales croisées, panse basse fermée, bras montant à droite."""
    f, d, h, hc, _, c = capitales.mesures(p)
    fin = f * 0.7
    x1 = f * 0.55
    x2 = x1 + fin + c * 0.45
    droite = f * 2.2 + c * 1.4
    haut_d1, bas_d1 = (x1 + fin * 0.5, h * 0.64), (droite - f * 0.45, -d)
    y_bras = h * 0.38
    t = (haut_d1[1] - y_bras) / (haut_d1[1] - bas_d1[1])
    x_bras = haut_d1[0] + t * (bas_d1[0] - haut_d1[0])
    epaisseur_bras = f * 0.25 + p["delie"]
    fin_bras = (droite + f * 0.15, y_bras + hc * 0.6 + 40)
    contours = [
        fut(x1, h * 0.6, h + d, fin),
        fut(x2, h * 0.66, h + d, fin),
        epaule(x1 + fin, x2, h, fin, p),
        trait((x2 + fin * 0.5, h * 0.7), (f * 0.5, h * 0.4), fin),
        trait(haut_d1, bas_d1, f),
        fut(0, -d, h * 0.46, f),
        delie_bas(f, droite - f * 0.8, f, p),
        bande((x_bras - f * 0.2, y_bras), fin_bras, epaisseur_bras),
        losange(fin_bras[0], fin_bras[1] - epaisseur_bras / 2, f * 0.4, f * 0.5),
    ]
    return symbole(contours, droite + f * 0.4, p)


@glyphe("at", 0x40)
def dessiner_at(p):
    h = p["hauteur_capitale"]
    rayon = h * 0.5
    e = p["delie"] * 1.5 + p["fut"] * 0.25
    cy = h * 0.4
    contours_a, chasse_a, _ = minuscules.dessiner_a(p)
    facteur = 0.62
    a = echelle(sans_epines(contours_a), facteur, rayon - chasse_a * facteur / 2, cy - p["hauteur_x"] * facteur / 2)
    return symbole(anneau(rayon, cy, rayon, e) + a, rayon * 2, p)


def lettre_encerclee(lettre, p: dict):
    """© ® : capitale réduite sans épine, dans un anneau octogonal."""
    h = p["hauteur_capitale"]
    rayon = h * 0.48
    e = p["delie"] * 1.2 + p["fut"] * 0.15
    cy = h * 0.5
    contours, chasse, _ = lettre(p)
    facteur = 0.5
    reduite = echelle(sans_epines(contours), facteur, rayon - chasse * facteur / 2, cy - h * facteur / 2)
    return symbole(anneau(rayon, cy, rayon, e) + reduite, rayon * 2, p)


@glyphe("copyright", 0xA9)
def dessiner_copyright(p):
    return lettre_encerclee(capitales.dessiner_C, p)


@glyphe("registered", 0xAE)
def dessiner_registered(p):
    return lettre_encerclee(capitales.dessiner_R, p)


@glyphe("trademark", 0x2122)
def dessiner_trademark(p):
    h = p["hauteur_capitale"]
    facteur = 0.42
    contours_t, chasse_t, _ = capitales.dessiner_T(p)
    contours_m, chasse_m, _ = capitales.dessiner_M(p)
    dy = h - h * facteur
    contours = echelle(sans_epines(contours_t), facteur, 0, dy) + \
        echelle(sans_epines(contours_m), facteur, chasse_t * facteur, dy)
    return symbole(contours, (chasse_t + chasse_m) * facteur, p)


@glyphe("section", 0xA7)
def dessiner_section(p):
    """§ : deux s superposés qui se chevauchent."""
    h = p["hauteur_capitale"]
    contours, largeur = forme_s(p, p["hauteur_x"], p["fut"], p["contrepoincon"] * 0.6, avec_epine=False)
    contours = decaler(contours, -p["approche"], 0)
    largeur -= 2 * p["approche"]
    facteur = h * 0.62 / p["hauteur_x"]
    haut = echelle(contours, facteur, 0, h * 0.4)
    bas = echelle(contours, facteur, 0, -h * 0.05)
    return symbole(haut + bas, largeur * facteur, p)


@glyphe("paragraph", 0xB6)
def dessiner_paragraph(p):
    """¶ : deux fûts et une panse pleine en haut à gauche."""
    f, d, h, _, _, c = capitales.mesures(p)
    fin = f * 0.6
    x1 = c * 0.9
    x2 = x1 + fin + c * 0.35
    contours = [
        fut(x1, p["descendante"] * 0.6, h + d, fin),
        fut(x2, p["descendante"] * 0.6, h + d, fin),
        bande((x1, h + d), (x2 + fin, h + d), p["delie"] * 1.5),
        [(x1 + fin * 0.5, h + d), (x1 + fin * 0.5, h * 0.42), (c * 0.25, h * 0.48), (0, h * 0.72), (c * 0.3, h + d)],
    ]
    return symbole(contours, x2 + fin, p)


# Accents isolés ------------------------------------------------------------------------------

def accent_isole(forme, p: dict, base: float | None = None, longueur: float | None = None):
    L = longueur or accents.LONGUEUR_ACCENT
    largeur = L * 1.4
    y = base if base is not None else p["hauteur_x"] + accents.ecart_minuscule(p)
    return symbole(decaler(forme(p, y, L), largeur / 2, 0), largeur, p)


for _nom, _code, _forme in [
    ("grave", 0x60, accents.forme_grave), ("acute", 0xB4, accents.forme_aigu),
    ("circumflex", 0x2C6, accents.forme_circonflexe), ("caron", 0x2C7, accents.forme_caron),
    ("dieresis", 0xA8, accents.forme_trema), ("macron", 0xAF, accents.forme_macron),
    ("breve", 0x2D8, accents.forme_breve), ("dotaccent", 0x2D9, accents.forme_point),
    ("ring", 0x2DA, accents.forme_rond), ("tilde", 0x2DC, accents.forme_tilde),
    ("hungarumlaut", 0x2DD, accents.forme_double_aigu),
]:
    glyphe(_nom, _code)(lambda p, forme=_forme: accent_isole(forme, p))


@glyphe("asciicircum", 0x5E)
def dessiner_asciicircum(p):
    """^ : circonflexe agrandi, à mi-hauteur de capitale."""
    return accent_isole(accents.forme_circonflexe, p, base=p["hauteur_capitale"] * 0.5,
                        longueur=accents.LONGUEUR_ACCENT * 1.3)


def accent_bas_isole(dessiner, p: dict):
    contours, _, _ = dessiner(p)
    largeur = accents.LONGUEUR_ACCENT
    return symbole(decaler(contours, largeur / 2, 0), largeur, p)


@glyphe("cedilla", 0xB8)
def dessiner_cedilla(p):
    return accent_bas_isole(accents.dessiner_cedillacomb, p)


@glyphe("ogonek", 0x2DB)
def dessiner_ogonek(p):
    return accent_bas_isole(accents.dessiner_ogonekcomb, p)
