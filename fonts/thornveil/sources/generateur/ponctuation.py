"""Ponctuation de base de Thornveil (sans épine : la ponctuation doit rester nette en petit).

Points en losange (comme le point du i), apostrophe courbe distincte de l'apostrophe droite,
guillemets en chevrons, ¡ et ¿ obtenus par demi-tour de ! et ?, ) ] par miroir de ( [.
"""

from primitives import (
    bande,
    chevron,
    coupe,
    decaler,
    epaule,
    fut,
    glyphe,
    losange,
    losange_oriente,
    miroir,
    pivoter,
    trait,
)


def mesures(p: dict):
    """Raccourcis : fût bas de casse, dépassement, hauteur d'x, capitale, approche, contrepoinçon."""
    return (p["fut"], p["depassement_pointe"], p["hauteur_x"], p["hauteur_capitale"], p["approche"],
            p["contrepoincon"])


def rayon_point(p: dict) -> float:
    return 30 + p["fut"] * 0.4


def point(cx: float, cy: float, p: dict, echelle: float = 1) -> list:
    r = rayon_point(p) * echelle
    return losange(cx, cy, r * 0.85, r)


def ancres(chasse: float, p: dict) -> dict:
    return {"top": (chasse / 2, p["hauteur_x"]), "bottom": (chasse / 2, 0)}


def virgule(cx: float, cy: float, p: dict) -> list:
    """Point en losange prolongé d'une queue qui descend vers la gauche."""
    r = rayon_point(p)
    return [point(cx, cy, p), trait((cx + r * 0.3, cy), (cx - r * 0.5, cy - r * 2.4), p["fut"] * 0.45)]


# Points ---------------------------------------------------------------------------------

@glyphe("space", 0x20)
def dessiner_space(p):
    return [], 230, {}


@glyphe("uni00A0", 0xA0)
def dessiner_nbspace(p):
    return [], 230, {}


@glyphe("uni202F", 0x202F)
def dessiner_espace_fine_insecable(p):
    """Espace fine insécable : avant ; ! ? et à l'intérieur des « » en typographie française."""
    return [], 115, {}


@glyphe("uni2009", 0x2009)
def dessiner_espace_fine(p):
    return [], 115, {}


@glyphe("period", 0x2E)
def dessiner_period(p):
    r, g = rayon_point(p), p["approche"]
    cx = g + r * 0.85
    chasse = cx + r * 0.85 + g
    return [point(cx, r * 0.9, p)], chasse, ancres(chasse, p)


@glyphe("comma", 0x2C)
def dessiner_comma(p):
    r, g = rayon_point(p), p["approche"]
    cx = g + r * 1.1
    chasse = cx + r * 0.85 + g
    return virgule(cx, r * 0.9, p), chasse, ancres(chasse, p)


@glyphe("colon", 0x3A)
def dessiner_colon(p):
    r, g, h = rayon_point(p), p["approche"], p["hauteur_x"]
    cx = g + r * 0.85
    chasse = cx + r * 0.85 + g
    return [point(cx, r * 0.9, p), point(cx, h - r, p)], chasse, ancres(chasse, p)


@glyphe("semicolon", 0x3B)
def dessiner_semicolon(p):
    r, g, h = rayon_point(p), p["approche"], p["hauteur_x"]
    cx = g + r * 1.1
    chasse = cx + r * 0.85 + g
    return virgule(cx, r * 0.9, p) + [point(cx, h - r, p)], chasse, ancres(chasse, p)


@glyphe("periodcentered", 0xB7)
def dessiner_periodcentered(p):
    r, g = rayon_point(p), p["approche"]
    cx = g + r * 0.85
    chasse = cx + r * 0.85 + g
    return [point(cx, p["hauteur_x"] * 0.5, p)], chasse, ancres(chasse, p)


@glyphe("bullet", 0x2022)
def dessiner_bullet(p):
    r, g = rayon_point(p) * 1.4, p["approche"]
    cx = g + r * 0.85
    chasse = cx + r * 0.85 + g
    return [point(cx, p["hauteur_x"] * 0.5, p, echelle=1.4)], chasse, ancres(chasse, p)


@glyphe("ellipsis", 0x2026)
def dessiner_ellipsis(p):
    r, g = rayon_point(p), p["approche"]
    pas = r * 2.6
    cx = g + r * 0.85
    contours = [point(cx + i * pas, r * 0.9, p) for i in range(3)]
    chasse = cx + 2 * pas + r * 0.85 + g
    return contours, chasse, ancres(chasse, p)


# ! ? ¡ ¿ ---------------------------------------------------------------------------------

def exclamation(p: dict):
    f, d, _, H, g, _ = mesures(p)
    largeur = f * 0.9
    cx = g + largeur / 2
    contours = [fut(g, H * 0.32, H + d, largeur), point(cx, rayon_point(p) * 0.9, p)]
    return contours, g + largeur + g


def interrogation(p: dict):
    f, d, _, H, g, c = mesures(p)
    largeur = f * 0.9
    dr = g + f * 0.8 + c * 0.7
    cx = (g + dr + largeur) / 2
    contours = [
        fut(g, H * 0.66, H + d, largeur * 0.55),
        epaule(g + largeur * 0.55, dr, H, largeur, p),
        fut(dr, H * 0.55, H + d, largeur),
        trait((dr + largeur * 0.45, H * 0.6), (cx, H * 0.34), largeur * 0.8),
        fut(cx - largeur * 0.4, H * 0.22, H * 0.38, largeur * 0.8),
        point(cx, rayon_point(p) * 0.9, p),
    ]
    return contours, dr + largeur + g


@glyphe("exclam", 0x21)
def dessiner_exclam(p):
    contours, chasse = exclamation(p)
    return contours, chasse, ancres(chasse, p)


@glyphe("exclamdown", 0xA1)
def dessiner_exclamdown(p):
    contours, chasse = exclamation(p)
    return pivoter(contours, chasse / 2, p["hauteur_x"] / 2), chasse, ancres(chasse, p)


@glyphe("question", 0x3F)
def dessiner_question(p):
    contours, chasse = interrogation(p)
    return contours, chasse, ancres(chasse, p)


@glyphe("questiondown", 0xBF)
def dessiner_questiondown(p):
    contours, chasse = interrogation(p)
    return pivoter(contours, chasse / 2, p["hauteur_x"] / 2), chasse, ancres(chasse, p)


# Apostrophes et guillemets -----------------------------------------------------------------

def apostrophe_droite(x: float, p: dict) -> list:
    """Coin effilé vertical : l'apostrophe droite (') ne se confond pas avec la courbe (’)."""
    f, d, _, H, _, _ = mesures(p)
    demi = f * 0.25
    return [(x - demi, H + d), (x + demi, H + d), (x + demi * 0.4, H * 0.66), (x - demi * 0.4, H * 0.66)]


def virgule_haute(cx: float, p: dict, retournee: bool) -> list:
    """Virgule placée en haut de capitale (’), ou retournée (‘)."""
    r = rayon_point(p)
    cy = p["hauteur_capitale"] - r
    forme = virgule(cx, cy, p)
    return pivoter(forme, cx, cy) if retournee else forme


def ecart_double(p: dict) -> float:
    return rayon_point(p) * 2.2


@glyphe("quotesingle", 0x27)
def dessiner_quotesingle(p):
    g, f = p["approche"], p["fut"]
    x = g + f * 0.25
    chasse = x + f * 0.25 + g
    return [apostrophe_droite(x, p)], chasse, ancres(chasse, p)


@glyphe("quotedbl", 0x22)
def dessiner_quotedbl(p):
    g, f = p["approche"], p["fut"]
    x = g + f * 0.25
    pas = f * 0.5 + 40
    chasse = x + pas + f * 0.25 + g
    return [apostrophe_droite(x, p), apostrophe_droite(x + pas, p)], chasse, ancres(chasse, p)


def guillemet_courbe(nombre: int, p: dict, retournee: bool, en_bas: bool):
    r, g = rayon_point(p), p["approche"]
    cx = g + r * 1.1
    contours = []
    for i in range(nombre):
        forme = virgule(cx + i * ecart_double(p), r * 0.9, p) if en_bas else \
            virgule_haute(cx + i * ecart_double(p), p, retournee)
        contours += forme
    chasse = cx + (nombre - 1) * ecart_double(p) + r * 0.85 + g
    return contours, chasse, ancres(chasse, p)


@glyphe("quoteright", 0x2019)
def dessiner_quoteright(p):
    return guillemet_courbe(1, p, retournee=False, en_bas=False)


@glyphe("quoteleft", 0x2018)
def dessiner_quoteleft(p):
    return guillemet_courbe(1, p, retournee=True, en_bas=False)


@glyphe("quotesinglbase", 0x201A)
def dessiner_quotesinglbase(p):
    return guillemet_courbe(1, p, retournee=False, en_bas=True)


@glyphe("quotedblright", 0x201D)
def dessiner_quotedblright(p):
    return guillemet_courbe(2, p, retournee=False, en_bas=False)


@glyphe("quotedblleft", 0x201C)
def dessiner_quotedblleft(p):
    return guillemet_courbe(2, p, retournee=True, en_bas=False)


@glyphe("quotedblbase", 0x201E)
def dessiner_quotedblbase(p):
    return guillemet_courbe(2, p, retournee=False, en_bas=True)


def chevrons(nombre: int, vers_gauche: bool, p: dict):
    f, _, h, _, g, _ = mesures(p)
    longueur, demi_hauteur, epaisseur = f * 0.9 + 30, h * 0.25, f * 0.7
    pas = longueur * 0.8
    contours = [chevron(g + i * pas, h * 0.45, longueur, demi_hauteur, epaisseur) for i in range(nombre)]
    chasse = g + (nombre - 1) * pas + longueur + epaisseur + g
    if not vers_gauche:
        contours = miroir(contours, chasse / 2)
    return contours, chasse, ancres(chasse, p)


@glyphe("guilsinglleft", 0x2039)
def dessiner_guilsinglleft(p):
    return chevrons(1, True, p)


@glyphe("guilsinglright", 0x203A)
def dessiner_guilsinglright(p):
    return chevrons(1, False, p)


@glyphe("guillemotleft", 0xAB)
def dessiner_guillemotleft(p):
    return chevrons(2, True, p)


@glyphe("guillemotright", 0xBB)
def dessiner_guillemotright(p):
    return chevrons(2, False, p)


# Tirets ---------------------------------------------------------------------------------

def tiret(longueur: float, p: dict):
    f, _, h, _, g, _ = mesures(p)
    epaisseur = p["delie"] * 1.2 + f * 0.35
    haut = h * 0.42 + epaisseur
    contours = [bande((g, haut), (g + longueur, haut + coupe(f) * 0.3), epaisseur)]
    chasse = g + longueur + g
    return contours, chasse, ancres(chasse, p)


@glyphe("hyphen", 0x2D)
def dessiner_hyphen(p):
    return tiret(p["contrepoincon"] * 0.9 + p["fut"] * 0.6, p)


@glyphe("endash", 0x2013)
def dessiner_endash(p):
    return tiret(p["contrepoincon"] * 1.6 + p["fut"], p)


@glyphe("emdash", 0x2014)
def dessiner_emdash(p):
    return tiret(p["contrepoincon"] * 3 + p["fut"] * 1.5, p)


# Parenthèses, crochets, barres ---------------------------------------------------------------

def parenthese(p: dict):
    f, d, _, H, g, _ = mesures(p)
    largeur, epaisseur = f * 0.9 + 20, f * 0.7
    x = g
    contours = [
        fut(x, H * 0.18, H * 0.82, f * 0.8),
        trait((x + f * 0.4, H * 0.78), (x + largeur + f * 0.4, p["ascendante"] + d), epaisseur),
        trait((x + f * 0.4, H * 0.22), (x + largeur + f * 0.4, p["descendante"] * 0.7), epaisseur),
    ]
    return contours, x + largeur + f * 0.75 + g


def crochet_droit(p: dict):
    f, _, _, _, g, c = mesures(p)
    epaisseur = p["delie"] * 1.5 + f * 0.15
    haut, bas = p["ascendante"], p["descendante"] * 0.75
    droite = g + f * 0.8 + c * 0.45
    contours = [
        fut(g, bas, haut, f * 0.8),
        bande((g, haut), (droite, haut), epaisseur),
        bande((g, bas + epaisseur), (droite, bas + epaisseur), epaisseur),
    ]
    return contours, droite + g


@glyphe("parenleft", 0x28)
def dessiner_parenleft(p):
    contours, chasse = parenthese(p)
    return contours, chasse, ancres(chasse, p)


@glyphe("parenright", 0x29)
def dessiner_parenright(p):
    contours, chasse = parenthese(p)
    return miroir(contours, chasse / 2), chasse, ancres(chasse, p)


@glyphe("bracketleft", 0x5B)
def dessiner_bracketleft(p):
    contours, chasse = crochet_droit(p)
    return contours, chasse, ancres(chasse, p)


@glyphe("bracketright", 0x5D)
def dessiner_bracketright(p):
    contours, chasse = crochet_droit(p)
    return miroir(contours, chasse / 2), chasse, ancres(chasse, p)


@glyphe("slash", 0x2F)
def dessiner_slash(p):
    f, _, _, _, g, c = mesures(p)
    contours = [trait((g + f * 0.35, p["descendante"] * 0.6), (g + c + f * 0.35, p["ascendante"]), f * 0.7)]
    chasse = g + c + f * 0.7 + g
    return contours, chasse, ancres(chasse, p)


@glyphe("bar", 0x7C)
def dessiner_bar(p):
    f, d, _, _, g, _ = mesures(p)
    contours = [fut(g, p["descendante"] * 0.85, p["ascendante"] + d, f * 0.6)]
    chasse = g + f * 0.6 + g
    return contours, chasse, ancres(chasse, p)


@glyphe("asterisk", 0x2A)
def dessiner_asterisk(p):
    f, _, _, H, g, _ = mesures(p)
    longueur, largeur = H * 0.24, f * 0.5
    cx, cy = g + longueur / 2, H * 0.76
    contours = [losange_oriente(cx, cy, longueur, largeur, angle) for angle in (90, 30, 150)]
    chasse = cx + longueur / 2 + g
    return contours, chasse, ancres(chasse, p)


# Variantes « .case » (fonction case) : ponctuation centrée sur la hauteur d'x, remontée au milieu
# des capitales quand le texte est tout en capitales (« THORNVEIL – ÉDITION »).
CENTREE_SUR_HAUTEUR_X = [
    ("hyphen", dessiner_hyphen), ("endash", dessiner_endash), ("emdash", dessiner_emdash),
    ("guilsinglleft", dessiner_guilsinglleft), ("guilsinglright", dessiner_guilsinglright),
    ("guillemotleft", dessiner_guillemotleft), ("guillemotright", dessiner_guillemotright),
    ("periodcentered", dessiner_periodcentered), ("bullet", dessiner_bullet),
]


def remonter(dessiner, p: dict):
    contours, chasse, ancres_glyphe = dessiner(p)
    return decaler(contours, 0, (p["hauteur_capitale"] - p["hauteur_x"]) / 2), chasse, ancres_glyphe


for _nom, _dessiner in CENTREE_SUR_HAUTEUR_X:
    glyphe(f"{_nom}.case")(lambda p, dessiner=_dessiner: remonter(dessiner, p))
