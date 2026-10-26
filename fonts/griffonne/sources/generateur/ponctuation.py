"""Ponctuation de Griffonne : fonctionnelle, sans chat, pour se reconnaître immédiatement.

Une seule touche de caractère : l'apostrophe ’ et les guillemets anglais en goutte de pinceau,
bien distincts de l'apostrophe droite ' (défaut relevé dans la police Cat de l'audit).
Inclut les espaces de la typographie française et les guillemets « ».
"""

from glyphes import METRIQUES, RAYON, Trait, glyphe
from pinceau import arc, courbe, ligne, lisse

APPROCHE = 60
RAYON_POINT = RAYON * 1.15       # un point un peu plus gros que le trait : il se voit en petit
HAUTEUR_X = METRIQUES["hauteur_x"]
CAPITALE = METRIQUES["capitale"]
MILIEU_X = HAUTEUR_X / 2          # axe des tirets et des guillemets


def point(x: float, y: float) -> Trait:
    return Trait([ligne((x - 5, y), (x + 5, y))], epaisseur=RAYON_POINT / RAYON)


def goutte_haute(x: float, sens: int) -> Trait:
    """Goutte de pinceau en haut (’ si sens = 1, ‘ si sens = -1 : retournée)."""
    if sens == 1:
        return Trait([courbe((x, 670), (x + 12, 630), (x + 6, 575), (x - 30, 515))], epaisseur=1.15, effilement=0.65)
    return Trait([courbe((x, 545), (x - 12, 585), (x - 6, 640), (x + 30, 700))], epaisseur=1.15, effilement=0.65)


def ponctuation(nom: str, point_code: int, chasse: float):
    def enregistrer(dessin):
        return glyphe(nom, point_code)(lambda: (dessin(), chasse, {}))
    return enregistrer


ESPACE_FINE = 125


@ponctuation("uni202F", 0x202F, ESPACE_FINE)
def dessiner_espace_fine():
    """Espace fine insécable : avant ; ! ? et dans « » en français."""
    return []


LARGEUR_POINT = 2 * (APPROCHE + RAYON_POINT)
X_POINT = LARGEUR_POINT / 2


@ponctuation("period", 0x2E, LARGEUR_POINT)
def dessiner_point():
    return [point(X_POINT, RAYON_POINT)]


def virgule() -> list[Trait]:
    return [Trait([courbe((X_POINT, 55), (X_POINT + 8, 0), (X_POINT - 6, -60), (X_POINT - 40, -115))],
                  epaisseur=1.15, effilement=0.65)]


@ponctuation("comma", 0x2C, LARGEUR_POINT)
def dessiner_virgule():
    return virgule()


@ponctuation("colon", 0x3A, LARGEUR_POINT)
def dessiner_deux_points():
    return [point(X_POINT, RAYON_POINT), point(X_POINT, HAUTEUR_X - RAYON_POINT)]


@ponctuation("semicolon", 0x3B, LARGEUR_POINT)
def dessiner_point_virgule():
    return virgule() + [point(X_POINT, HAUTEUR_X - RAYON_POINT)]


@ponctuation("exclam", 0x21, LARGEUR_POINT + 20)
def dessiner_exclamation():
    x = (LARGEUR_POINT + 20) / 2
    return [Trait([ligne((x, CAPITALE - RAYON), (x, 250))], effilement=0.4), point(x, RAYON_POINT)]


@ponctuation("question", 0x3F, 480)
def dessiner_question():
    return [Trait(lisse([(110, 560), (225, CAPITALE + 6 - RAYON), (370, 640), (390, 480), (265, 380), (250, 245)])),
            point(250, RAYON_POINT)]


@ponctuation("quotesingle", 0x27, 200)
def dessiner_apostrophe_droite():
    return [Trait([ligne((100, CAPITALE - RAYON), (100, 500))])]


@ponctuation("quotedbl", 0x22, 330)
def dessiner_guillemet_droit():
    return [Trait([ligne((100, CAPITALE - RAYON), (100, 500))]), Trait([ligne((230, CAPITALE - RAYON), (230, 500))])]


@ponctuation("quoteright", 0x2019, 220)
def dessiner_apostrophe():
    return [goutte_haute(120, 1)]


@ponctuation("quoteleft", 0x2018, 220)
def dessiner_guillemet_ouvrant_simple():
    return [goutte_haute(100, -1)]


@ponctuation("quotedblright", 0x201D, 360)
def dessiner_guillemet_fermant_anglais():
    return [goutte_haute(120, 1), goutte_haute(250, 1)]


@ponctuation("quotedblleft", 0x201C, 360)
def dessiner_guillemet_ouvrant_anglais():
    return [goutte_haute(100, -1), goutte_haute(230, -1)]


def chevron(pointe_x: float, vers_gauche: bool) -> list[Trait]:
    ouverture = 85 if vers_gauche else -85
    return [Trait([ligne((pointe_x + ouverture, MILIEU_X + 125), (pointe_x, MILIEU_X))], epaisseur=0.85),
            Trait([ligne((pointe_x, MILIEU_X), (pointe_x + ouverture, MILIEU_X - 125))], epaisseur=0.85)]


@ponctuation("guilsinglleft", 0x2039, 270)
def dessiner_chevron_ouvrant():
    return chevron(95, vers_gauche=True)


@ponctuation("guilsinglright", 0x203A, 270)
def dessiner_chevron_fermant():
    return chevron(175, vers_gauche=False)


@ponctuation("guillemotleft", 0xAB, 410)
def dessiner_guillemet_francais_ouvrant():
    return chevron(95, vers_gauche=True) + chevron(225, vers_gauche=True)


@ponctuation("guillemotright", 0xBB, 410)
def dessiner_guillemet_francais_fermant():
    return chevron(185, vers_gauche=False) + chevron(315, vers_gauche=False)


def tiret(longueur: float) -> list[Trait]:
    return [Trait([ligne((APPROCHE + RAYON, MILIEU_X), (APPROCHE + RAYON + longueur, MILIEU_X + 4))], epaisseur=0.95)]


@ponctuation("hyphen", 0x2D, 2 * (APPROCHE + RAYON) + 180)
def dessiner_trait_union():
    return tiret(180)


@ponctuation("endash", 0x2013, 2 * (APPROCHE + RAYON) + 400)
def dessiner_tiret_demi_cadratin():
    return tiret(400)


@ponctuation("emdash", 0x2014, 1000)
def dessiner_tiret_cadratin():
    return [Trait([ligne((RAYON + 20, MILIEU_X), (1000 - RAYON - 20, MILIEU_X + 6))], epaisseur=0.95)]


@ponctuation("parenleft", 0x28, 290)
def dessiner_parenthese_ouvrante():
    return [Trait([courbe((215, 760), (60, 570), (60, 40), (215, -150))])]


@ponctuation("parenright", 0x29, 290)
def dessiner_parenthese_fermante():
    return [Trait([courbe((75, 760), (230, 570), (230, 40), (75, -150))])]


@ponctuation("slash", 0x2F, 420)
def dessiner_barre_oblique():
    return [Trait([ligne((70, -110), (350, 760))])]


@ponctuation("ellipsis", 0x2026, 3 * LARGEUR_POINT)
def dessiner_points_de_suspension():
    return [point(X_POINT + i * LARGEUR_POINT, RAYON_POINT) for i in range(3)]


@ponctuation("Euro", 0x20AC, 600)
def dessiner_euro():
    cx, cy = 340, 350
    return [Trait(arc(cx, cy, 215, cy + METRIQUES["depassement"] - RAYON, 45, 315)),
            Trait([ligne((95, 415), (390, 419))], epaisseur=0.85),
            Trait([ligne((95, 285), (360, 289))], epaisseur=0.85)]
