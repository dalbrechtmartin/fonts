"""Capitales de Griffonne : même pinceau, même règle « un élément de chat par lettre ».

- oreilles au sommet du premier fût (B D E F H K L N P R U), du A, du T et du I ;
- visages (oreilles et yeux) dans les rondes C G O Q, yeux dans les boucles de B D P R ;
- queues sur J, L et Q ; oreilles sur le premier trait des diagonales (M V W X Y Z) et sur le haut du S.
"""

from glyphes import (
    METRIQUES,
    RAYON,
    Trait,
    ancres_sur,
    felin,
    fut,
    glyphe,
    oreilles,
    oreilles_panse,
    ronde,
    yeux,
)
from pinceau import arc, courbe, ellipse, ligne, lisse

CAPITALE = METRIQUES["capitale"]
HAUT = CAPITALE - RAYON          # axe du trait qui affleure la hauteur de capitale
BAS = RAYON                      # axe du trait qui affleure la ligne de base
APPROCHE = METRIQUES["approche"]
APPROCHE_RONDE = METRIQUES["approche_ronde"]
APPROCHE_DIAGONALE = 30


def ry_capitale() -> float:
    return CAPITALE / 2 + METRIQUES["depassement"] - RAYON


def boucle(x: float, haut: float, bas: float, saillie: float) -> Trait:
    """Panse accrochée au fût (B D P R) : part du fût en haut, tourne à droite, revient au fût en bas."""
    ry = (haut - bas) / 2
    rx = min(ry, saillie)
    cx = x + saillie - rx
    return Trait([ligne((x, haut), (cx, haut)), *arc(cx, bas + ry, rx, ry, 90, -90), ligne((cx, bas), (x, bas))])


def oreilles_capitale(x: float) -> list[Trait]:
    return oreilles(x, CAPITALE, echelle=1.3)


def oreilles_panse_capitale(cx: float, cy: float, rx: float, ry: float) -> list[Trait]:
    return oreilles_panse(cx, cy, rx, ry, longueur=135, inclinaison=46)


def avec_chat(traits: list[Trait], *elements: list[Trait]) -> list[Trait]:
    """Ajoute les éléments félins quand le niveau marqué est actif."""
    if felin("marque"):
        for element in elements:
            traits = traits + element
    return traits


def ancres(x: float) -> dict[str, tuple[float, float]]:
    return ancres_sur(x, CAPITALE)


# Fûts et barres ----------------------------------------------------------

@glyphe("H", 0x48)
def dessiner_H():
    gauche = APPROCHE + RAYON
    droite = gauche + METRIQUES["fut"] + 420
    barre = Trait([ligne((gauche, 365), (droite, 375))])
    traits = avec_chat([fut(gauche, 0, CAPITALE), fut(droite, 0, CAPITALE), barre], oreilles_capitale(gauche))
    return traits, droite + RAYON + APPROCHE, ancres((gauche + droite) / 2)


@glyphe("I", 0x49)
def dessiner_I():
    """I à courtes barres : jamais confondu avec l (queue) ni 1 (drapeau)."""
    x = APPROCHE + RAYON + 75
    barres = [Trait([ligne((x - 75, HAUT), (x + 75, HAUT + 4))]), Trait([ligne((x - 75, BAS), (x + 75, BAS + 4))])]
    traits = avec_chat([fut(x, 0, CAPITALE), *barres], oreilles_capitale(x))
    return traits, x + 75 + RAYON + APPROCHE, ancres(x)


@glyphe("E", 0x45)
def dessiner_E():
    x = APPROCHE + RAYON
    barres = [Trait([ligne((x, HAUT), (x + 330, HAUT + 6))]),
              Trait([ligne((x, 370), (x + 280, 376))]),
              Trait([ligne((x, BAS), (x + 340, BAS + 6))])]
    traits = avec_chat([fut(x, 0, CAPITALE), *barres], oreilles_capitale(x))
    return traits, x + 340 + RAYON + 45, ancres(x + 160)


@glyphe("F", 0x46)
def dessiner_F():
    x = APPROCHE + RAYON
    barres = [Trait([ligne((x, HAUT), (x + 330, HAUT + 6))]), Trait([ligne((x, 370), (x + 270, 376))])]
    traits = avec_chat([fut(x, 0, CAPITALE), *barres], oreilles_capitale(x))
    return traits, x + 330 + RAYON + 30, ancres(x + 160)


@glyphe("L", 0x4C)
def dessiner_L():
    """L dont la barre se relève en queue de chat."""
    x = APPROCHE + RAYON
    pied = Trait([ligne((x, HAUT), (x, BAS)), ligne((x, BAS), (x + 250, BAS + 4)),
                  courbe((x + 250, BAS + 4), (x + 320, BAS + 6), (x + 350, BAS + 40), (x + 355, BAS + 115))])
    traits = avec_chat([pied], oreilles_capitale(x))
    return traits, x + 355 + RAYON + 30, {**ancres(x + 120), "caronalt": (x + RAYON + 80, CAPITALE)}


@glyphe("T", 0x54)
def dessiner_T():
    """T coiffé d'une tête de chat : oreilles au-dessus de la barre."""
    cx = APPROCHE_DIAGONALE + RAYON + 250
    traits = avec_chat([Trait([ligne((cx - 250, HAUT), (cx + 250, HAUT + 6))]), fut(cx, 0, CAPITALE)],
                       oreilles_capitale(cx))
    return traits, cx + 250 + RAYON + APPROCHE_DIAGONALE, ancres(cx)


@glyphe("J", 0x4A)
def dessiner_J():
    """J dont le crochet s'enroule en queue."""
    x = APPROCHE + RAYON + 230
    fond = -METRIQUES["depassement"] + RAYON
    crochet = Trait([ligne((x, HAUT), (x, 210)),
                     courbe((x, 210), (x, fond + 10), (x - 90, fond), (x - 180, fond + 30)),
                     courbe((x - 180, fond + 30), (x - 240, fond + 50), (x - 250, fond + 110), (x - 215, fond + 150))])
    traits = avec_chat([crochet], oreilles_capitale(x))
    return traits, x + RAYON + APPROCHE, ancres(x)


@glyphe("K", 0x4B)
def dessiner_K():
    x = APPROCHE + RAYON
    bras = Trait([ligne((x + 360, HAUT), (x + 20, 290))])
    jambe = Trait([ligne((x + 140, 400), (x + 380, BAS))])
    traits = avec_chat([fut(x, 0, CAPITALE), bras, jambe], oreilles_capitale(x))
    return traits, x + 380 + RAYON + 40, ancres(x + 180)


@glyphe("N", 0x4E)
def dessiner_N():
    gauche = APPROCHE + RAYON
    droite = gauche + METRIQUES["fut"] + 400
    diagonale = Trait([ligne((gauche, HAUT), (droite, BAS))])
    traits = avec_chat([fut(gauche, 0, CAPITALE), diagonale, fut(droite, 0, CAPITALE)], oreilles_capitale(gauche))
    return traits, droite + RAYON + APPROCHE, ancres((gauche + droite) / 2)


@glyphe("U", 0x55)
def dessiner_U():
    gauche = APPROCHE + RAYON
    droite = gauche + 470
    rx, fond = (droite - gauche) / 2, -METRIQUES["depassement"] + RAYON
    cuvette = Trait([ligne((gauche, HAUT), (gauche, 250)), *arc(gauche + rx, 250, rx, 250 - fond, 180, 360),
                     ligne((droite, 250), (droite, HAUT))])
    traits = avec_chat([cuvette], oreilles_capitale(gauche))
    return traits, droite + RAYON + APPROCHE, ancres(gauche + rx)


# Boucles : B D P R --------------------------------------------------------

@glyphe("P", 0x50)
def dessiner_P():
    x = APPROCHE + RAYON
    traits = avec_chat([fut(x, 0, CAPITALE), boucle(x, HAUT, 330, 330)],
                       oreilles_capitale(x), yeux(x + 175, 505, ecart=45, taille=0.45))
    return traits, x + 330 + RAYON + APPROCHE_RONDE, ancres(x + 165)


@glyphe("R", 0x52)
def dessiner_R():
    x = APPROCHE + RAYON
    jambe = Trait([ligne((x + 170, 330), (x + 360, BAS))])
    traits = avec_chat([fut(x, 0, CAPITALE), boucle(x, HAUT, 330, 330), jambe],
                       oreilles_capitale(x), yeux(x + 175, 505, ecart=45, taille=0.45))
    return traits, x + 360 + RAYON + 40, ancres(x + 165)


@glyphe("B", 0x42)
def dessiner_B():
    x = APPROCHE + RAYON
    traits = avec_chat([fut(x, 0, CAPITALE), boucle(x, HAUT, 385, 300), boucle(x, 385, BAS, 345)],
                       oreilles_capitale(x), yeux(x + 180, 215, ecart=45, taille=0.45))
    return traits, x + 345 + RAYON + APPROCHE_RONDE, ancres(x + 170)


@glyphe("D", 0x44)
def dessiner_D():
    x = APPROCHE + RAYON
    traits = avec_chat([fut(x, 0, CAPITALE), boucle(x, HAUT, BAS, 470)],
                       oreilles_capitale(x), yeux(x + 240, 400))
    return traits, x + 470 + RAYON + APPROCHE_RONDE, ancres(x + 230)


# Rondes : C G O Q S ---------------------------------------------------------

def centre_ronde(largeur: float) -> tuple[float, float, float, float]:
    """(cx, cy, rx, ry) du squelette d'une ronde de capitale de largeur d'encre donnée."""
    rx = largeur / 2 - RAYON
    return APPROCHE_RONDE + largeur / 2, CAPITALE / 2, rx, ry_capitale()


def visage_capitale(cx: float, cy: float, rx: float, ry: float) -> list[Trait]:
    return oreilles_panse_capitale(cx, cy, rx, ry) + yeux(cx, cy + 50, ecart=62)


@glyphe("O", 0x4F)
def dessiner_O():
    panse, chasse = ronde(680, CAPITALE, APPROCHE_RONDE)
    cx, cy, rx, ry = centre_ronde(680)
    return avec_chat([panse], visage_capitale(cx, cy, rx, ry)), chasse, ancres(cx)


@glyphe("Q", 0x51)
def dessiner_Q():
    """Q dont la queue sort en bas à droite et se relève : la queue du chat."""
    panse, chasse = ronde(680, CAPITALE, APPROCHE_RONDE)
    cx, cy, rx, ry = centre_ronde(680)
    queue = Trait([courbe((cx + 90, 60), (cx + 170, -50), (cx + 280, -70), (cx + 370, -10))])
    traits = avec_chat([panse, queue], visage_capitale(cx, cy, rx, ry))
    return traits, chasse + 60, ancres(cx)


@glyphe("C", 0x43)
def dessiner_C():
    cx, cy, rx, ry = centre_ronde(640)
    ouverture = Trait(arc(cx, cy, rx, ry, 48, 315))
    traits = avec_chat([ouverture], visage_capitale(cx, cy, rx, ry))
    return traits, cx + rx * 0.7 + RAYON + 45, ancres(cx)


@glyphe("G", 0x47)
def dessiner_G():
    cx, cy, rx, ry = centre_ronde(660)
    fin = (cx + rx * 0.94, cy - ry * 0.34)  # point de l'arc à 340°
    corps = Trait([*arc(cx, cy, rx, ry, 45, 340), ligne(fin, (fin[0], 330))])
    barre = Trait([ligne((cx + 70, 330), (fin[0], 334))])
    traits = avec_chat([corps, barre], oreilles_panse_capitale(cx, cy, rx, ry), yeux(cx - 20, cy + 70, ecart=55))
    return traits, cx + rx + RAYON + APPROCHE_RONDE, ancres(cx)


@glyphe("S", 0x53)
def dessiner_S():
    cx = APPROCHE_RONDE + RAYON + 215
    sommet, fond = CAPITALE + METRIQUES["depassement"] - RAYON, -METRIQUES["depassement"] + RAYON
    epine = Trait(lisse([
        (cx + 195, 610), (cx + 20, sommet), (cx - 195, 540), (cx - 60, 395),
        (cx + 115, 320), (cx + 215, 175), (cx + 15, fond), (cx - 215, 95),
    ]))
    traits = avec_chat([epine], oreilles_panse_capitale(cx + 10, CAPITALE / 2, 190, ry_capitale()))
    return traits, cx + 215 + RAYON + APPROCHE_RONDE, ancres(cx)


# Diagonales : A M V W X Y Z ---------------------------------------------------

@glyphe("A", 0x41)
def dessiner_A():
    """A dont le sommet est une tête de chat."""
    gauche = APPROCHE_DIAGONALE + RAYON
    sommet_x = gauche + 280
    droite = sommet_x + 280
    traits = [Trait([ligne((gauche, BAS), (sommet_x, HAUT))]), Trait([ligne((sommet_x, HAUT), (droite, BAS))]),
              Trait([ligne((gauche + 110, 250), (droite - 110, 256))])]
    return avec_chat(traits, oreilles_capitale(sommet_x)), droite + RAYON + APPROCHE_DIAGONALE, ancres(sommet_x)


@glyphe("V", 0x56)
def dessiner_V():
    gauche = APPROCHE_DIAGONALE + RAYON
    milieu, droite = gauche + 290, gauche + 580
    traits = [Trait([ligne((gauche, HAUT), (milieu, BAS))]), Trait([ligne((milieu, BAS), (droite, HAUT))])]
    return avec_chat(traits, oreilles_capitale(gauche)), droite + RAYON + APPROCHE_DIAGONALE, ancres(milieu)


@glyphe("W", 0x57)
def dessiner_W():
    gauche, ecart = APPROCHE_DIAGONALE + RAYON, 205
    sommets = [gauche + i * ecart for i in range(5)]
    hauteurs = [HAUT, BAS, HAUT - 120, BAS, HAUT]
    traits = [Trait([ligne((sommets[i], hauteurs[i]), (sommets[i + 1], hauteurs[i + 1]))]) for i in range(4)]
    return avec_chat(traits, oreilles_capitale(gauche)), sommets[-1] + RAYON + APPROCHE_DIAGONALE, ancres(sommets[2])


@glyphe("M", 0x4D)
def dessiner_M():
    gauche = APPROCHE + RAYON
    droite = gauche + 600
    milieu = (gauche + droite) / 2
    traits = [Trait([ligne((gauche, BAS), (gauche + 30, HAUT))]), Trait([ligne((gauche + 30, HAUT), (milieu, 240))]),
              Trait([ligne((milieu, 240), (droite - 30, HAUT))]), Trait([ligne((droite - 30, HAUT), (droite, BAS))])]
    return avec_chat(traits, oreilles_capitale(gauche + 30)), droite + RAYON + APPROCHE, ancres(milieu)


@glyphe("X", 0x58)
def dessiner_X():
    gauche, droite = APPROCHE_DIAGONALE + RAYON + 10, APPROCHE_DIAGONALE + RAYON + 530
    traits = [Trait([ligne((gauche, HAUT), (droite, BAS))]), Trait([ligne((droite + 10, HAUT), (gauche - 10, BAS))])]
    return avec_chat(traits, oreilles_capitale(gauche)), droite + RAYON + APPROCHE_DIAGONALE + 10, ancres((gauche + droite) / 2)


@glyphe("Y", 0x59)
def dessiner_Y():
    gauche = APPROCHE_DIAGONALE + RAYON
    milieu, droite = gauche + 270, gauche + 540
    traits = [Trait([ligne((gauche, HAUT), (milieu, 330))]), Trait([ligne((droite, HAUT), (milieu, 330))]),
              fut(milieu, 0, 380)]
    return avec_chat(traits, oreilles_capitale(gauche)), droite + RAYON + APPROCHE_DIAGONALE, ancres(milieu)


@glyphe("Z", 0x5A)
def dessiner_Z():
    gauche = APPROCHE + RAYON - 15
    droite = gauche + 440
    traits = [Trait([ligne((gauche, HAUT), (droite, HAUT + 8))]), Trait([ligne((droite, HAUT + 8), (gauche, BAS))]),
              Trait([ligne((gauche, BAS), (droite + 10, BAS + 6))])]
    return avec_chat(traits, oreilles_capitale(gauche)), droite + RAYON + APPROCHE - 15, ancres((gauche + droite) / 2)


# Ligatures du français ---------------------------------------------------------

@glyphe("OE", 0x152)
def dessiner_OE():
    """Œ : un O-visage dont le flanc droit devient le fût du E."""
    cx, cy, rx, ry = centre_ronde(600)
    x = cx + rx
    barres = [Trait([ligne((x, HAUT), (x + 300, HAUT + 6))]), Trait([ligne((x, 370), (x + 250, 376))]),
              Trait([ligne((x, BAS), (x + 310, BAS + 6))])]
    traits = avec_chat([ellipse(cx, cy, rx, ry), fut(x, 0, CAPITALE), *barres], visage_capitale(cx, cy, rx, ry))
    return traits, x + 310 + RAYON + 45, ancres(x)


@glyphe("AE", 0xC6)
def dessiner_AE():
    """Æ : la jambe gauche du A monte jusqu'au fût du E, coiffé des oreilles."""
    gauche = APPROCHE_DIAGONALE + RAYON
    x = gauche + 340
    hauteur_barre = 250
    x_barre = gauche + (hauteur_barre - BAS) / (HAUT - BAS) * (x - gauche)
    barres = [Trait([ligne((x, HAUT), (x + 300, HAUT + 6))]), Trait([ligne((x, 370), (x + 250, 376))]),
              Trait([ligne((x, BAS), (x + 310, BAS + 6))]), Trait([ligne((x_barre, hauteur_barre), (x, hauteur_barre + 4))])]
    traits = avec_chat([Trait([ligne((gauche, BAS), (x, HAUT))]), fut(x, 0, CAPITALE), *barres], oreilles_capitale(x))
    return traits, x + 310 + RAYON + 45, ancres(x)
