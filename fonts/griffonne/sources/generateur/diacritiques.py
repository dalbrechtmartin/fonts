"""Diacritiques de Griffonne : combinants, variantes pour capitales (.case) et accents isolés.

Chaque diacritique est dessiné une seule fois par une fonction de forme (x centré sur 0,
y depuis son point d'accroche), puis décliné :
- combinant minuscule : accroche « _top » à la hauteur d'x (ou « _bottom », « _ogonek » à 0) ;
- « .case » : posé sur la capitale, plus bas et plus plat pour ne pas toucher la ligne du dessus ;
- isolé (´ ¨ ¸…) : même forme, centrée dans une chasse propre.
La composition (composer_accents.py) accroche ces formes aux ancres des lettres.
"""

from collections.abc import Callable

from glyphes import METRIQUES, Trait, glyphe
from pinceau import arc, courbe, ellipse, ligne, lisse, transformer

HAUTEUR_X = METRIQUES["hauteur_x"]
CAPITALE = METRIQUES["capitale"]
EPAISSEUR = 0.8            # un accent est plus léger qu'un fût
ECART = 80                 # blanc entre la lettre et l'accent (minuscules)
ECART_CASE = 35            # sur les capitales, l'accent descend
APLATI_CASE = 0.65         # et s'aplatit : il ne touche pas la ligne du dessus
CHASSE_ISOLE = 320

# Forme : (hauteur de départ, aplatissement) -> traits, dessinés autour de x = 0
Forme = Callable[[float, float], list[Trait]]


def point_accent(x: float, y: float) -> Trait:
    return Trait([ligne((x - 4, y), (x + 4, y))], epaisseur=0.95)


# Formes du haut --------------------------------------------------------------

def aigu(y: float, h: float) -> list[Trait]:
    return [Trait([ligne((45, y + 115 * h), (-35, y))], epaisseur=EPAISSEUR * 1.1, effilement=0.45)]


def grave(y: float, h: float) -> list[Trait]:
    return [Trait([ligne((-45, y + 115 * h), (35, y))], epaisseur=EPAISSEUR * 1.1, effilement=0.45)]


def circonflexe(y: float, h: float) -> list[Trait]:
    sommet = (0, y + 100 * h)
    return [Trait([ligne((-85, y), sommet)], epaisseur=EPAISSEUR), Trait([ligne(sommet, (85, y))], epaisseur=EPAISSEUR)]


def caron(y: float, h: float) -> list[Trait]:
    creux = (0, y)
    return [Trait([ligne((-85, y + 100 * h), creux)], epaisseur=EPAISSEUR),
            Trait([ligne(creux, (85, y + 100 * h))], epaisseur=EPAISSEUR)]


def trema(y: float, h: float) -> list[Trait]:
    return [point_accent(-75, y + 40 * h), point_accent(75, y + 40 * h)]


def point_suscrit(y: float, h: float) -> list[Trait]:
    return [point_accent(0, y + 40 * h)]


def tilde(y: float, h: float) -> list[Trait]:
    return [Trait(lisse([(-100, y + 10), (-50, y + 70 * h), (45, y + 15), (100, y + 75 * h)]), epaisseur=EPAISSEUR * 0.9)]


def macron(y: float, h: float) -> list[Trait]:
    return [Trait([ligne((-95, y + 30 * h), (95, y + 34 * h))], epaisseur=EPAISSEUR)]


def breve(y: float, h: float) -> list[Trait]:
    rayon = 80
    return [Trait(arc(0, y + rayon * h + 10, rayon, rayon * h, 200, 340), epaisseur=EPAISSEUR * 0.9)]


def rond(y: float, h: float) -> list[Trait]:
    rayon = 48 * h
    anneau = ellipse(0, y + rayon + 20, 48, rayon)
    return [Trait(anneau.segments, ferme=True, epaisseur=0.55)]  # trait fin, sinon l'anneau se bouche


def double_aigu(y: float, h: float) -> list[Trait]:
    return [Trait([ligne((x + 45, y + 115 * h), (x - 30, y))], epaisseur=EPAISSEUR, effilement=0.45) for x in (-55, 60)]


# Formes du bas (y = 0 : ligne de base de la lettre) ---------------------------------

def cedille(y: float, h: float) -> list[Trait]:
    return [Trait(lisse([(0, y + 15), (10, y - 55), (75, y - 105), (25, y - 170), (-60, y - 165)]), epaisseur=0.7)]


def virgule_souscrite(y: float, h: float) -> list[Trait]:
    return [Trait([courbe((0, y - 60), (12, y - 105), (2, y - 150), (-35, y - 205))], epaisseur=1.0, effilement=0.6)]


def ogonek(y: float, h: float) -> list[Trait]:
    return [Trait(lisse([(0, y + 25), (-45, y - 80), (5, y - 170), (85, y - 160)]), epaisseur=0.7, effilement=0.3)]


# Déclinaison ---------------------------------------------------------------

def enregistrer_isole(isole: tuple[str, int] | None, traits: Callable[[], list[Trait]]) -> None:
    """Accent isolé (´ ¨ ¸…) : la forme centrée dans sa propre chasse."""
    if isole:
        nom, point_code = isole
        glyphe(nom, point_code)(lambda: (transformer(traits(), dx=CHASSE_ISOLE / 2), CHASSE_ISOLE, {}))


def decliner(nom: str, point_code: int, forme: Forme, isole: tuple[str, int] | None = None) -> None:
    """Enregistre le combinant minuscule, sa variante .case et l'accent isolé."""
    def combinant(hauteur: float, ecart: float, aplati: float):
        def dessiner():
            traits = forme(hauteur + ecart, aplati)
            sommet = hauteur + ecart + 140 * aplati
            # « top » sur l'accent : un second accent s'empile au-dessus (ǖ, ǘ)
            return traits, 0, {"_top": (0, hauteur), "top": (0, sommet)}
        return dessiner

    glyphe(nom, point_code)(combinant(HAUTEUR_X, ECART, 1.0))
    glyphe(f"{nom}.case")(combinant(CAPITALE, ECART_CASE, APLATI_CASE))
    enregistrer_isole(isole, lambda: forme(HAUTEUR_X + ECART, 1.0))


def decliner_bas(nom: str, point_code: int, forme: Forme, ancre: str, isole: tuple[str, int] | None = None) -> None:
    """Diacritique souscrit : accroché à la ligne de base, le même sous minuscules et capitales."""
    glyphe(nom, point_code)(lambda: (forme(0, 1.0), 0, {f"_{ancre}": (0, 0)}))
    enregistrer_isole(isole, lambda: forme(0, 1.0))


decliner("gravecomb", 0x300, grave, ("grave", 0x60))
decliner("acutecomb", 0x301, aigu, ("acute", 0xB4))
decliner("uni0302", 0x302, circonflexe, ("circumflex", 0x2C6))
decliner("tildecomb", 0x303, tilde, ("tilde", 0x2DC))
decliner("uni0304", 0x304, macron, ("macron", 0xAF))
decliner("uni0306", 0x306, breve, ("breve", 0x2D8))
decliner("uni0307", 0x307, point_suscrit, ("dotaccent", 0x2D9))
decliner("uni0308", 0x308, trema, ("dieresis", 0xA8))
decliner("uni030A", 0x30A, rond, ("ring", 0x2DA))
decliner("uni030B", 0x30B, double_aigu, ("hungarumlaut", 0x2DD))
decliner("uni030C", 0x30C, caron, ("caron", 0x2C7))
@glyphe("uni030C.alt")
def dessiner_caron_apostrophe():
    """Caron en apostrophe de ď ť ľ Ľ (tchèque, slovaque) : posé à droite de la hampe."""
    return [Trait([courbe((0, 0), (12, -40), (6, -95), (-30, -155))], epaisseur=1.05, effilement=0.6)], 0, {"_caronalt": (0, 0)}


decliner_bas("uni0326", 0x326, virgule_souscrite, "bottom")
decliner_bas("uni0327", 0x327, cedille, "bottom", ("cedilla", 0xB8))
decliner_bas("uni0328", 0x328, ogonek, "ogonek", ("ogonek", 0x2DB))
