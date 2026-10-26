"""Squelettes des glyphes de Griffonne : le chemin du pinceau, pas le contour.

Chaque fonction enregistrée avec @glyphe retourne (traits, chasse, ancres).
Les mesures viennent de METRIQUES (documentation/specification.md) : aucune valeur ailleurs.
"""

from collections.abc import Callable

from pinceau import Trait, arc, courbe, ellipse, ligne, lisse

METRIQUES = {
    "hauteur_x": 540,
    "capitale": 720,
    "ascendante": 760,
    "descendante": -230,
    "depassement": 12,
    "fut": 92,
    "approche": 70,         # blanc le long d'un fût droit
    "approche_ronde": 50,   # les rondes paraissent plus loin : moins de blanc
    # Boîte de ligne : couvre le glyphe le plus haut (ĺ, 980) et centre les capitales
    # ((985 - 265) / 2 = 360 = capitale / 2) : texte centré au pixel dans les boutons
    "ligne_haut": 985,
    "ligne_bas": -265,
}
RAYON = METRIQUES["fut"] / 2

Dessin = Callable[[], tuple[list[Trait], float, dict[str, tuple[float, float]]]]
GLYPHES: dict[str, tuple[int | None, Dessin]] = {}


def glyphe(nom: str, point_code: int | None = None):
    def enregistrer(fonction: Dessin) -> Dessin:
        GLYPHES[nom] = (point_code, fonction)
        return fonction
    return enregistrer


def fut(x: float, bas: float, haut: float) -> Trait:
    """Fût vertical dont les extrémités arrondies touchent exactement bas et haut."""
    return Trait([ligne((x, bas + RAYON), (x, haut - RAYON))])


def ronde(largeur: float, hauteur: float, marge: float) -> tuple[Trait, float]:
    """Panse fermée de largeur d'encre donnée, avec dépassement haut et bas."""
    m = METRIQUES
    rx, ry = largeur / 2 - RAYON, hauteur / 2 + m["depassement"] - RAYON
    return ellipse(marge + largeur / 2, hauteur / 2, rx, ry), largeur + 2 * marge


def ancres_sur(x: float, hauteur: float) -> dict[str, tuple[float, float]]:
    """Ancres d'accent sur l'axe x (axe du fût, ou centre optique de la lettre)."""
    return {"top": (x, hauteur), "bottom": (x, 0)}


def ancres_centrees(chasse: float, hauteur: float) -> dict[str, tuple[float, float]]:
    return ancres_sur(chasse / 2, hauteur)


# Formes partagées ------------------------------------------------------------

K = 0.5523  # quart d'ellipse en Bézier


def arche(gauche: float, droite: float, jusqu_a: float = RAYON) -> Trait:
    """Épaule ronde qui sort du fût gauche et redescend en fût droit (n, h, m)."""
    m = METRIQUES
    sommet = m["hauteur_x"] + m["depassement"] - RAYON
    rx, ry = (droite - gauche) / 2, 165
    cx, cy = gauche + rx, sommet - ry
    return Trait([
        courbe((gauche, cy), (gauche, cy + ry * K), (cx - rx * K, sommet), (cx, sommet)),
        courbe((cx, sommet), (cx + rx * K, sommet), (droite, cy + ry * K), (droite, cy)),
        ligne((droite, cy), (droite, jusqu_a)),
    ])


def cuvette(gauche: float, droite: float) -> Trait:
    """Arche retournée : descend du fût gauche, remonte vers le fût droit (u)."""
    m = METRIQUES
    fond = -m["depassement"] + RAYON
    rx, ry = (droite - gauche) / 2, 165
    cx, cy = gauche + rx, fond + ry
    return Trait([
        ligne((gauche, m["hauteur_x"] - RAYON), (gauche, cy)),
        courbe((gauche, cy), (gauche, cy - ry * K), (cx - rx * K, fond), (cx, fond)),
        courbe((cx, fond), (cx + rx * K, fond), (droite, cy - ry * K), (droite, cy)),
    ])


def tete_de_chat(cx: float, cy: float) -> list[Trait]:
    """Point du i et du j : une tache ronde et deux oreilles effilées. Se lit comme un point en petit."""
    return [
        Trait([ligne((cx - 12, cy), (cx + 12, cy))], epaisseur=1.45),
        Trait([ligne((cx - 30, cy + 20), (cx - 50, cy + 92))], epaisseur=0.6, effilement=0.75),
        Trait([ligne((cx + 30, cy + 20), (cx + 50, cy + 92))], epaisseur=0.6, effilement=0.75),
    ]


HAUTEUR_POINT = METRIQUES["hauteur_x"] + 175

# Présence du chat dans les lettres par défaut (le ss01 viendra en plus)
NIVEAUX_FELINS = ("lisible", "discret", "marque")
NIVEAU_FELIN = "marque"  # choix validé : chat bien présent par défaut


def felin(niveau_minimal: str) -> bool:
    return NIVEAUX_FELINS.index(NIVEAU_FELIN) >= NIVEAUX_FELINS.index(niveau_minimal)


def oreilles(x: float, haut: float, echelle: float = 1.0) -> list[Trait]:
    """Deux oreilles effilées au sommet d'une hampe : la hampe devient une tête de chat.

    echelle suit la taille de la lettre (1,3 pour les capitales), sinon elles redeviennent des cornes.
    """
    base = haut - RAYON - 10
    epaisseur = 0.75 * echelle ** 0.5
    # Assez grandes pour se lire comme des oreilles dès 32 px, pas comme une encoche
    return [Trait([ligne((x + sens * 22 * echelle, base), (x + sens * 52 * echelle, haut + 62 * echelle))],
                  epaisseur=epaisseur, effilement=0.75) for sens in (-1, 1)]


def oreilles_panse(cx: float, cy: float, rx: float, ry: float,
                   longueur: float = 105, inclinaison: float = 36) -> list[Trait]:
    """Deux oreilles posées sur le haut d'une panse : un chat vu de face."""
    traits = []
    for sens in (-1, 1):
        bx, by = cx + sens * rx * 0.5, cy + ry * 0.82
        traits.append(Trait([ligne((bx, by), (bx + sens * inclinaison, by + longueur))], epaisseur=0.7, effilement=0.75))
    return traits


# Le générateur passe MOUSTACHES à True pour dessiner les variantes « .ss01 » (chats complets)
MOUSTACHES = False


def yeux(cx: float, cy: float, ecart: float = 50, taille: float = 0.5) -> list[Trait]:
    traits = [Trait([ligne((cx + sens * ecart - 4, cy), (cx + sens * ecart + 4, cy))], epaisseur=taille) for sens in (-1, 1)]
    if MOUSTACHES:
        traits += moustaches(cx, cy - ecart * 0.9, ecart)
    return traits


def moustaches(cx: float, cy: float, ecart: float) -> list[Trait]:
    """Trois poils de chaque côté, sous les yeux, qui sortent nettement du visage.

    La taille suit l'écart des yeux, donc la taille du visage (petit visage du a, grand O).
    Trop courts, ils s'arrêtaient dans l'épaisseur du contour et ne se voyaient pas.
    """
    depart, longueur = ecart * 1.5, ecart * 4.4
    traits = []
    for sens in (-1, 1):
        for pente in (0.22, 0.0, -0.22):
            debut = (cx + sens * depart, cy)
            fin = (cx + sens * (depart + longueur), cy + pente * longueur)
            traits.append(Trait([ligne(debut, fin)], epaisseur=0.42, effilement=0.65))
    return traits


def visage(cx: float, rx: float = 205, hauteur_yeux: float = None) -> list[Trait]:
    """Une panse devient une tête de chat : oreilles sur le haut, yeux dans la contreforme."""
    cy = METRIQUES["hauteur_x"] / 2
    hauteur_yeux = cy + 30 if hauteur_yeux is None else hauteur_yeux
    return oreilles_panse(cx, cy, rx, METRIQUES["hauteur_x"] / 2 + METRIQUES["depassement"] - RAYON) + yeux(cx, hauteur_yeux)



# Minuscules à fût et à arche -------------------------------------------------

@glyphe("n", 0x6E)
def dessiner_n():
    m = METRIQUES
    gauche = m["approche"] + RAYON
    droite = gauche + m["fut"] + 300
    chasse = droite + RAYON + m["approche"]
    traits = [fut(gauche, 0, m["hauteur_x"]), arche(gauche, droite)]
    if felin("marque"):
        traits += oreilles(gauche, m["hauteur_x"])
    return traits, chasse, ancres_centrees(chasse, m["hauteur_x"])


@glyphe("h", 0x68)
def dessiner_h():
    m = METRIQUES
    gauche = m["approche"] + RAYON
    droite = gauche + m["fut"] + 300
    chasse = droite + RAYON + m["approche"]
    traits = [fut(gauche, 0, m["ascendante"]), arche(gauche, droite)]
    if felin("discret"):
        traits += oreilles(gauche, m["ascendante"])
    return traits, chasse, ancres_centrees(chasse, m["ascendante"])


@glyphe("m", 0x6D)
def dessiner_m():
    m = METRIQUES
    gauche = m["approche"] + RAYON
    milieu = gauche + m["fut"] + 230
    droite = milieu + m["fut"] + 230
    chasse = droite + RAYON + m["approche"]
    traits = [fut(gauche, 0, m["hauteur_x"]), arche(gauche, milieu), arche(milieu, droite)]
    if felin("marque"):
        traits += oreilles(gauche, m["hauteur_x"])
    return traits, chasse, ancres_centrees(chasse, m["hauteur_x"])


@glyphe("u", 0x75)
def dessiner_u():
    m = METRIQUES
    gauche = m["approche"] + RAYON
    droite = gauche + m["fut"] + 300
    chasse = droite + RAYON + m["approche"]
    if felin("discret"):
        jambe = Trait(queue_droite(droite, m["hauteur_x"] - RAYON, -m["depassement"] + RAYON, 95, 80))
        chasse += 60
    else:
        jambe = fut(droite, 0, m["hauteur_x"])
    traits = [cuvette(gauche, droite), jambe]
    if felin("marque"):
        traits += oreilles(gauche, m["hauteur_x"])
    return traits, chasse, ancres_sur(gauche + (droite - gauche) / 2 + RAYON, m["hauteur_x"])


@glyphe("r", 0x72)
def dessiner_r():
    m = METRIQUES
    gauche = m["approche"] + RAYON
    sommet = m["hauteur_x"] + m["depassement"] - RAYON
    epaule = Trait([courbe((gauche, 330), (gauche + 10, sommet - 20), (gauche + 120, sommet + 4), (gauche + 215, sommet - 40))])
    chasse = gauche + 215 + RAYON + 25  # r ouvert à droite : approche réduite
    traits = [fut(gauche, 0, m["hauteur_x"]), epaule]
    if felin("marque"):
        traits += oreilles(gauche, m["hauteur_x"])
    return traits, chasse, ancres_sur(gauche + 60, m["hauteur_x"])


@glyphe("dotlessi", 0x131)
def dessiner_dotlessi():
    m = METRIQUES
    x = m["approche"] + RAYON
    chasse = 2 * x
    return [fut(x, 0, m["hauteur_x"])], chasse, ancres_centrees(chasse, m["hauteur_x"])


@glyphe("i", 0x69)
def dessiner_i():
    traits, chasse, ancres = dessiner_dotlessi()
    return traits + tete_de_chat(chasse / 2, HAUTEUR_POINT), chasse, ancres


def crochet_j(x: float) -> Trait:
    m = METRIQUES
    bas = m["descendante"] - m["depassement"] + RAYON
    return Trait([
        ligne((x, m["hauteur_x"] - RAYON), (x, -40)),
        courbe((x, -40), (x, bas - 20), (x - 70, bas), (x - 175, bas + 70)),
    ])


@glyphe("uni0237", 0x237)
def dessiner_dotlessj():
    m = METRIQUES
    x = 175 + RAYON  # le crochet passe sous la lettre précédente : approche gauche réduite
    chasse = x + RAYON + m["approche"]
    return [crochet_j(x)], chasse, ancres_sur(x, m["hauteur_x"])


@glyphe("j", 0x6A)
def dessiner_j():
    traits, chasse, ancres = dessiner_dotlessj()
    return traits + tete_de_chat(ancres["top"][0], HAUTEUR_POINT), chasse, ancres


@glyphe("l", 0x6C)
def dessiner_l():
    """l terminé par une queue de chat qui remonte : impossible à confondre avec I ou 1."""
    m = METRIQUES
    x = m["approche"] + RAYON
    # Queue courte et relevée : longue et à plat, elle se lisait comme un L en petit
    queue = Trait(queue_droite(x, m["ascendante"] - RAYON, -m["depassement"] + RAYON, 115, 95))
    chasse = x + 115 + RAYON + 15
    traits = [queue] + (oreilles(x, m["ascendante"]) if felin("discret") else [])
    return traits, chasse, {**ancres_sur(x, m["ascendante"]), "caronalt": (x + RAYON + 70, m["ascendante"])}


@glyphe("o", 0x6F)
def dessiner_o():
    m = METRIQUES
    panse_o, chasse = ronde(510, m["hauteur_x"], m["approche_ronde"])
    cx, cy, rx, ry = chasse / 2, m["hauteur_x"] / 2, 255 - RAYON, panse_ry()
    traits = [panse_o]
    if felin("discret"):
        traits += oreilles_panse(cx, cy, rx, ry)
    if felin("marque"):
        traits += yeux(cx, cy + 30)
    return traits, chasse, ancres_centrees(chasse, m["hauteur_x"])


# Rondes et panses ---------------------------------------------------------------

PANSE_RX = 205  # demi-largeur du squelette d'une panse de minuscule


def panse_ry() -> float:
    m = METRIQUES
    return m["hauteur_x"] / 2 + m["depassement"] - RAYON


def panse(cx: float) -> Trait:
    return ellipse(cx, METRIQUES["hauteur_x"] / 2, PANSE_RX, panse_ry())


def queue_droite(x: float, depart: float, bas: float, longueur: float, remontee: float) -> list:
    """Fût qui descend puis s'enroule vers la droite en queue de chat (d, q)."""
    return [ligne((x, depart), (x, bas + 120)),
            courbe((x, bas + 120), (x, bas + 10), (x + longueur * 0.35, bas), (x + longueur, bas + remontee))]


@glyphe("b", 0x62)
def dessiner_b():
    m = METRIQUES
    x = m["approche"] + RAYON
    chasse = x + 2 * PANSE_RX + RAYON + m["approche_ronde"]
    traits = [fut(x, 0, m["ascendante"]), panse(x + PANSE_RX)]
    if felin("discret"):
        traits += oreilles(x, m["ascendante"])
    if felin("marque"):
        traits += yeux(x + PANSE_RX, m["hauteur_x"] / 2 + 30)
    return traits, chasse, ancres_sur(x + PANSE_RX, m["ascendante"])


@glyphe("p", 0x70)
def dessiner_p():
    m = METRIQUES
    x = m["approche"] + RAYON
    chasse = x + 2 * PANSE_RX + RAYON + m["approche_ronde"]
    traits = [fut(x, m["descendante"], m["hauteur_x"]), panse(x + PANSE_RX)]
    if felin("marque"):
        traits += visage(x + PANSE_RX)
    return traits, chasse, ancres_sur(x + PANSE_RX, m["hauteur_x"])


def centre_panse_gauche() -> float:
    m = METRIQUES
    return m["approche_ronde"] + RAYON + PANSE_RX


@glyphe("d", 0x64)
def dessiner_d():
    """d à queue en bas à droite : jamais le simple reflet du b."""
    m = METRIQUES
    cx = centre_panse_gauche()
    x = cx + PANSE_RX
    fond = -m["depassement"] + RAYON
    queue = Trait(queue_droite(x, m["ascendante"] - RAYON, fond, 120, 75))
    chasse = x + 120 + RAYON + 15
    traits = [panse(cx), queue]
    if felin("discret"):
        traits += oreilles(x, m["ascendante"])
    if felin("marque"):
        traits += yeux(cx, m["hauteur_x"] / 2 + 30)
    return traits, chasse, {**ancres_sur(cx, m["ascendante"]), "caronalt": (x + RAYON + 70, m["ascendante"])}


@glyphe("q", 0x71)
def dessiner_q():
    """q à queue descendante enroulée : jamais le simple reflet du p."""
    m = METRIQUES
    cx = centre_panse_gauche()
    x = cx + PANSE_RX
    fond = m["descendante"] - m["depassement"] + RAYON
    queue = Trait(queue_droite(x, m["hauteur_x"] - RAYON, fond, 150, 70))
    chasse = x + 150 + RAYON + 15
    traits = [panse(cx), queue] + (visage(cx) if felin("marque") else [])
    return traits, chasse, ancres_sur(cx, m["hauteur_x"])


@glyphe("g", 0x67)
def dessiner_g():
    """g à un étage : panse et crochet vers la gauche (le q, lui, part à droite)."""
    m = METRIQUES
    cx = centre_panse_gauche()
    x = cx + PANSE_RX
    fond = m["descendante"] - m["depassement"] + RAYON
    crochet = Trait([ligne((x, m["hauteur_x"] - RAYON), (x, -40)),
                     courbe((x, -40), (x, fond - 10), (x - 110, fond), (x - 270, fond + 75))])
    chasse = x + RAYON + m["approche"]
    traits = [panse(cx), crochet] + (visage(cx) if felin("marque") else [])
    return traits, chasse, ancres_sur(cx, m["hauteur_x"])


@glyphe("c", 0x63)
def dessiner_c():
    m = METRIQUES
    rx = 195
    cx = m["approche_ronde"] + RAYON + rx
    ouverture = Trait(arc(cx, m["hauteur_x"] / 2, rx, panse_ry(), 50, 312))
    chasse = cx + rx * 0.64 + RAYON + 45
    traits = [ouverture] + (visage(cx, rx) if felin("marque") else [])  # une tête qui ouvre la bouche
    return traits, chasse, ancres_sur(cx, m["hauteur_x"])


@glyphe("e", 0x65)
def dessiner_e():
    m = METRIQUES
    rx = 195
    cx = m["approche_ronde"] + RAYON + rx
    hauteur_barre = m["hauteur_x"] / 2 + 15
    barre = Trait([ligne((cx - rx, hauteur_barre), (cx + rx, hauteur_barre))])
    boucle = Trait(arc(cx, m["hauteur_x"] / 2, rx, panse_ry(), 4, 318))
    chasse = cx + rx + RAYON + m["approche_ronde"]
    traits = [barre, boucle] + (oreilles_panse(cx, m["hauteur_x"] / 2, rx, panse_ry()) if felin("marque") else [])
    return traits, chasse, ancres_sur(cx, m["hauteur_x"])


@glyphe("a", 0x61)
def dessiner_a():
    """a à deux étages : oreilles sur le crochet, yeux dans le ventre ; le a entier est la tête du chat."""
    m = METRIQUES
    x = m["approche"] + RAYON + 380
    sommet = m["hauteur_x"] + m["depassement"] - RAYON
    if felin("discret"):
        pied = queue_droite(x, 360, -m["depassement"] + RAYON, 90, 75)
    else:
        pied = [ligne((x, 360), (x, RAYON))]
    tete = Trait([courbe((x - 310, 400), (x - 296, sommet), (x, sommet), (x, 360)), *pied])
    rx, ry = 165, 135
    cx, cy = x - rx, -m["depassement"] + RAYON + ry
    traits = [tete, ellipse(cx, cy, rx, ry)]
    if felin("marque"):
        # Oreilles de panse (larges, inclinées) : des oreilles verticales sur le crochet se lisaient comme des cornes
        traits += oreilles_panse(x - 150, m["hauteur_x"] / 2, 150, panse_ry())
        # Petits yeux : gros et rapprochés dans un ventre étroit, on lisait un groin
        traits += yeux(cx, cy + 28, ecart=44, taille=0.36)
    chasse = x + RAYON + m["approche"] + (55 if felin("discret") else 0)
    return traits, chasse, ancres_sur(cx, m["hauteur_x"])


# Formes libres, barres et diagonales -------------------------------------------

def haut_x() -> float:
    return METRIQUES["hauteur_x"] - RAYON


def bas_x() -> float:
    return RAYON


def barre_x(gauche: float, droite: float) -> Trait:
    """Barre du f et du t, posée sur la hauteur d'x, à peine montante."""
    y = METRIQUES["hauteur_x"] - 30
    return Trait([ligne((gauche, y), (droite, y + 6))])


@glyphe("s", 0x73)
def dessiner_s():
    m = METRIQUES
    cx = m["approche_ronde"] + RAYON + 165
    sommet = m["hauteur_x"] + m["depassement"] - RAYON
    fond = -m["depassement"] + RAYON
    epine = Trait(lisse([
        (cx + 150, 465), (cx + 15, sommet), (cx - 150, 405), (cx - 40, 295),
        (cx + 90, 240), (cx + 165, 135), (cx + 10, fond), (cx - 165, 75),
    ]))
    chasse = cx + 165 + RAYON + m["approche_ronde"]
    traits = [epine] + (oreilles_panse(cx + 10, m["hauteur_x"] / 2, 150, panse_ry()) if felin("marque") else [])
    return traits, chasse, ancres_sur(cx, m["hauteur_x"])


@glyphe("f", 0x66)
def dessiner_f():
    m = METRIQUES
    x = m["approche"] + RAYON + 60
    sommet = m["ascendante"] + m["depassement"] - RAYON
    hampe = Trait([ligne((x, RAYON), (x, 560)),
                   courbe((x, 560), (x, sommet), (x + 70, sommet), (x + 180, sommet - 55))])
    chasse = x + 150 + RAYON + 10  # le crochet déborde un peu : il se crène avec la lettre suivante
    traits = [hampe, barre_x(x - 110, x + 150)] + (oreilles(x + 30, m["ascendante"]) if felin("marque") else [])
    return traits, chasse, ancres_sur(x, m["ascendante"])


@glyphe("t", 0x74)
def dessiner_t():
    """t à petite queue de chat, cousine de celle du l."""
    m = METRIQUES
    x = m["approche"] + RAYON + 60
    queue = Trait(queue_droite(x, 690 - RAYON, -m["depassement"] + RAYON, 105, 85))
    chasse = x + 140 + RAYON + 20
    traits = [queue, barre_x(x - 110, x + 140)] + (oreilles(x, 690) if felin("marque") else [])
    return traits, chasse, {**ancres_sur(x, 690), "caronalt": (x + RAYON + 60, 690)}


@glyphe("k", 0x6B)
def dessiner_k():
    m = METRIQUES
    x = m["approche"] + RAYON
    bras = Trait([ligne((x + 285, haut_x()), (x + 20, 215))])
    jambe = Trait([ligne((x + 110, 300), (x + 300, bas_x()))])
    chasse = x + 300 + RAYON + 45
    traits = [fut(x, 0, m["ascendante"]), bras, jambe] + (oreilles(x, m["ascendante"]) if felin("discret") else [])
    return traits, chasse, ancres_sur(x + 140, m["ascendante"])


def chevron(gauche: float, ecart: float, bas: float = None) -> list[Trait]:
    """Deux coups de pinceau qui se rejoignent en bas (v, w)."""
    bas = bas_x() if bas is None else bas
    return [Trait([ligne((gauche, haut_x()), (gauche + ecart, bas))]),
            Trait([ligne((gauche + ecart, bas), (gauche + 2 * ecart, haut_x()))])]


APPROCHE_DIAGONALE = 30  # les diagonales laissent déjà du blanc en haut ou en bas


@glyphe("v", 0x76)
def dessiner_v():
    m = METRIQUES
    gauche = APPROCHE_DIAGONALE + RAYON
    chasse = gauche + 2 * 225 + RAYON + APPROCHE_DIAGONALE
    traits = chevron(gauche, 225) + (oreilles(gauche, m["hauteur_x"]) if felin("marque") else [])
    return traits, chasse, ancres_centrees(chasse, m["hauteur_x"])


@glyphe("w", 0x77)
def dessiner_w():
    m = METRIQUES
    gauche = APPROCHE_DIAGONALE + RAYON
    ecart = 170
    traits = chevron(gauche, ecart) + chevron(gauche + 2 * ecart, ecart)
    if felin("marque"):
        traits += oreilles(gauche, m["hauteur_x"])
    chasse = gauche + 4 * ecart + RAYON + APPROCHE_DIAGONALE
    return traits, chasse, ancres_centrees(chasse, m["hauteur_x"])


@glyphe("x", 0x78)
def dessiner_x():
    m = METRIQUES
    gauche, droite = APPROCHE_DIAGONALE + RAYON + 10, APPROCHE_DIAGONALE + RAYON + 410
    traits = [Trait([ligne((gauche, haut_x()), (droite, bas_x()))]),
              Trait([ligne((droite + 10, haut_x()), (gauche - 10, bas_x()))])]
    if felin("marque"):
        traits += oreilles(gauche, m["hauteur_x"])
    chasse = droite + RAYON + APPROCHE_DIAGONALE + 10
    return traits, chasse, ancres_centrees(chasse, m["hauteur_x"])


@glyphe("y", 0x79)
def dessiner_y():
    """y dont la descendante s'enroule vers la gauche, comme une queue posée."""
    m = METRIQUES
    gauche = APPROCHE_DIAGONALE + RAYON
    milieu, droite = gauche + 220, gauche + 440
    fond = m["descendante"] - m["depassement"] + RAYON
    traits = [Trait([ligne((gauche, haut_x()), (milieu, 40))]),
              Trait([ligne((droite, haut_x()), (milieu - 10, -10)),
                     courbe((milieu - 10, -10), (milieu - 60, fond + 20), (milieu - 120, fond), (milieu - 230, fond + 70))])]
    if felin("marque"):
        traits += oreilles(gauche, m["hauteur_x"])
    chasse = droite + RAYON + APPROCHE_DIAGONALE
    return traits, chasse, ancres_centrees(chasse, m["hauteur_x"])


@glyphe("z", 0x7A)
def dessiner_z():
    m = METRIQUES
    gauche = m["approche"] + RAYON - 15
    droite = gauche + 350
    traits = [Trait([ligne((gauche, haut_x()), (droite, haut_x() + 8))]),
              Trait([ligne((droite, haut_x() + 8), (gauche, bas_x()))]),
              Trait([ligne((gauche, bas_x()), (droite + 10, bas_x() + 6))])]
    if felin("marque"):
        traits += oreilles(gauche, m["hauteur_x"])
    chasse = droite + RAYON + m["approche"] - 15
    return traits, chasse, ancres_centrees(chasse, m["hauteur_x"])


# Ligatures du français ---------------------------------------------------------

@glyphe("oe", 0x153)
def dessiner_oe():
    """œ : un o-visage soudé à un e ; un seul chat par lettre."""
    m = METRIQUES
    cy, ry = m["hauteur_x"] / 2, panse_ry()
    rx_o, rx_e = 180, 190
    cx_o = m["approche_ronde"] + RAYON + rx_o
    cx_e = cx_o + rx_o + rx_e - 40
    traits = [ellipse(cx_o, cy, rx_o, ry), Trait([ligne((cx_e - rx_e, cy + 15), (cx_e + rx_e, cy + 15))]),
              Trait(arc(cx_e, cy, rx_e, ry, 4, 318))]
    if felin("marque"):
        traits += oreilles_panse(cx_o, cy, rx_o, ry) + yeux(cx_o, cy + 30, ecart=45)
    chasse = cx_e + rx_e + RAYON + m["approche_ronde"]
    return traits, chasse, ancres_centrees(chasse, m["hauteur_x"])


@glyphe("ae", 0xE6)
def dessiner_ae():
    """æ : le a (oreilles sur le crochet, yeux dans le ventre) dont le fût devient le dos du e."""
    m = METRIQUES
    x = m["approche"] + RAYON + 330
    sommet = m["hauteur_x"] + m["depassement"] - RAYON
    cy, ry = m["hauteur_x"] / 2, panse_ry()
    tete = Trait([courbe((x - 290, 400), (x - 276, sommet), (x, sommet), (x, 360)), ligne((x, 360), (x, RAYON))])
    rx_v, ry_v = 150, 135
    cx_v, cy_v = x - rx_v, -m["depassement"] + RAYON + ry_v
    rx_e = 190
    cx_e = x + rx_e
    traits = [tete, ellipse(cx_v, cy_v, rx_v, ry_v),
              Trait([ligne((x, cy + 15), (cx_e + rx_e, cy + 15))]), Trait(arc(cx_e, cy, rx_e, ry, 4, 318))]
    if felin("marque"):
        traits += oreilles_panse(x - 145, cy, 145, ry) + yeux(cx_v, cy_v + 28, ecart=40, taille=0.36)
    chasse = cx_e + rx_e + RAYON + m["approche_ronde"]
    return traits, chasse, ancres_centrees(chasse, m["hauteur_x"])
