"""Épines renforcées (jeu stylistique ss02) : chaque minuscule porte une épine longue et une seconde épine
du côté opposé, selon la règle des hauteurs.

ss02 se cumule avec ss04 (minuscules coulantes) : les variantes « x.ss02.ss04 » sont la lettre renforcée
avec les mêmes ronces que « x.ss04 ». Les fonctions s'enchaînent dans l'ordre ss02 puis ss04.
"""

import minuscules
from ornees import coulante, pleins
from parametres import HAUTEUR_EPINE
from primitives import Epine, epine, glyphe, sans_epines

FACTEUR_LONGUE = 1.6


def lire_epine(contour: Epine, p: dict) -> tuple:
    """Retrouve le bord, la hauteur et le côté d'une épine dessinée par primitives.epine."""
    (ancrage, bas), pointe = contour[0], contour[1][3]
    haut = contour[-1][3][1]
    cote = 1 if pointe[0] > ancrage else -1
    return ancrage + cote * p["fut"] * 0.3, (bas + haut) / 2, cote


def bord_oppose(contours: list, y: float, cote: int) -> float | None:
    """Bord extérieur de la lettre à la hauteur y, du côté indiqué."""
    intervalles = pleins(contours, y)
    if not intervalles:
        return None
    return intervalles[-1][1] if cote > 0 else intervalles[0][0]


def renforcer(dessiner):
    """Fonction de dessin : la lettre, son épine allongée et une seconde épine du côté opposé."""
    def dessin(p: dict):
        contours, chasse, ancres = dessiner(p)
        longue = dict(p, epine=p["epine"] * FACTEUR_LONGUE)
        lettre = sans_epines(contours)
        ajouts = []
        for contour in contours:
            if not isinstance(contour, Epine):
                continue
            x, y, cote = lire_epine(contour, p)
            ajouts.append(epine(x, y, cote, longue))
            y_oppose = p["hauteur_x"] * HAUTEUR_EPINE[-cote]
            x_oppose = bord_oppose(lettre, y_oppose, -cote)
            if x_oppose is None:  # la lettre n'existe pas à cette hauteur : même hauteur que la première
                y_oppose, x_oppose = y, bord_oppose(lettre, y, -cote)
            ajouts.append(epine(x_oppose, y_oppose, -cote, longue))
        return lettre + ajouts, chasse, ancres
    return dessin


for _lettre in "abcdefghijklmnopqrstuvwxyz":
    _renforcee = renforcer(getattr(minuscules, f"dessiner_{_lettre}"))
    glyphe(f"{_lettre}.ss02")(_renforcee)
    # mêmes ronces qu'en ss04 seul : la graine reste le nom « x.ss04 »
    glyphe(f"{_lettre}.ss02.ss04")(
        lambda p, dessin=_renforcee, nom=f"{_lettre}.ss04": coulante(nom, dessin, "minuscule", p))
