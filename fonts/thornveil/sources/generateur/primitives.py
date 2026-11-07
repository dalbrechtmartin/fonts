"""Primitives de dessin d'Thornveil et registre des glyphes.

Chaque primitive renvoie un contour : une liste FIXE de points et de courbes, sans opération
booléenne, pour que tous les maîtres gardent la même structure (police variable).
Les contours d'un glyphe se chevauchent ; le build les fusionne pour les statiques.
"""

from collections.abc import Callable

from parametres import COUPE_FIXE, HAUTEUR_EPINE, RAPPORT_COUPE

Point = tuple[float, float]
Courbe = tuple[str, Point, Point, Point]  # ("c", poignée 1, poignée 2, point d'arrivée)
Contour = list[Point | Courbe]  # le premier élément est toujours un point
Dessin = Callable[[dict], tuple[list[Contour], float, dict]]

DESSINS: dict[str, tuple[int | tuple[int, ...] | None, Dessin]] = {}


def glyphe(nom: str, point_code: int | tuple[int, ...] | None = None):
    """Enregistre une fonction de dessin sous un nom de glyphe (un ou plusieurs points de code)."""
    def enregistrer(fonction: Dessin) -> Dessin:
        DESSINS[nom] = (point_code, fonction)
        return fonction
    return enregistrer


def coupe(largeur: float) -> float:
    """Hauteur de la grande facette d'une tête ou d'un pied de fût."""
    return COUPE_FIXE + largeur * RAPPORT_COUPE


def fut(x: float, bas: float, haut: float, largeur: float) -> Contour:
    """Fût de textura taillé en losange : pointe haute décalée à gauche, pointe basse à droite."""
    longue = coupe(largeur)
    courte = longue * 0.35
    return [
        (x, bas + longue), (x + largeur * 0.65, bas), (x + largeur, bas + courte),
        (x + largeur, haut - longue), (x + largeur * 0.35, haut), (x, haut - courte),
    ]


def bande(depart: Point, arrivee: Point, epaisseur: float, debord: float = 0) -> Contour:
    """Trait d'épaisseur verticale constante ; le bord haut passe par depart et arrivee.

    debord prolonge le trait dans les fûts voisins pour que les contours se chevauchent.
    """
    (x1, y1), (x2, y2) = depart, arrivee
    pente = (y2 - y1) / (x2 - x1)
    x1, y1 = x1 - debord, y1 - debord * pente
    x2, y2 = x2 + debord, y2 + debord * pente
    return [(x1, y1), (x2, y2), (x2, y2 - epaisseur), (x1, y1 - epaisseur)]


def trait(depart: Point, arrivee: Point, largeur: float) -> Contour:
    """Trait d'épaisseur horizontale constante entre deux points de son axe (diagonales)."""
    (x1, y1), (x2, y2) = depart, arrivee
    demi = largeur / 2
    return [(x1 - demi, y1), (x1 + demi, y1), (x2 + demi, y2), (x2 - demi, y2)]


def losange(cx: float, cy: float, demi_largeur: float, demi_hauteur: float) -> Contour:
    """Losange (points, terminaisons)."""
    return [(cx, cy - demi_hauteur), (cx + demi_largeur, cy), (cx, cy + demi_hauteur), (cx - demi_largeur, cy)]


def fourche(x: float, haut: float, largeur: float, p: dict) -> Contour:
    """Ergot qui fourche la tête d'une ascendante vers le haut à droite."""
    longue = coupe(largeur)
    return [
        (x + largeur * 0.55, haut - longue * 0.5),
        (x + largeur * 1.05 + p["ornement"] * 1.5, haut),
        (x + largeur, haut - longue * 1.3),
    ]


class Epine(list):
    """Contour d'épine : marqué pour qu'une lettre réutilisée dans une autre (æ, œ, ©…) puisse l'ôter."""


def sans_epines(contours: list[Contour]) -> list[Contour]:
    return [c for c in contours if not isinstance(c, Epine)]


def epine(x_bord: float, y: float, cote: int, p: dict, echelle_base: float = 1,
          ancrage: float | None = None) -> Contour:
    """Épine de rose fine et courbe ; cote = -1 vers la gauche, +1 vers la droite.

    Le bord bas part à l'horizontale puis remonte : la pointe se recourbe vers le haut.
    echelle_base affine la base quand l'épine est raccourcie (ronces), pour garder la forme en croissant.
    ancrage : profondeur de la base dans le trait porteur (par défaut, 30 % du fût) ; à réduire sur une
    tige fine, sinon la base ressort de l'autre côté.
    """
    longueur = p["epine"]
    base = (p["ornement"] * 2.5 + p["fut"] * 0.1) * echelle_base
    ancrage = x_bord - cote * (p["fut"] * 0.3 if ancrage is None else ancrage)  # base noyée dans le trait
    bas, haut = y - base / 2, y + base / 2
    pointe = (x_bord + cote * longueur * 0.55, y + longueur * 0.85)
    return Epine([
        (ancrage, bas),
        ("c", (x_bord + cote * longueur * 0.45, bas + longueur * 0.05),
              (pointe[0], pointe[1] - longueur * 0.4), pointe),
        ("c", (pointe[0] - cote * longueur * 0.1, pointe[1] - longueur * 0.45),
              (x_bord + cote * longueur * 0.15, haut), (ancrage, haut)),
    ])


def epine_reglee(x_bord: float, hauteur: float, cote: int, p: dict) -> Contour:
    """Épine placée selon la règle des hauteurs (hauteur = hauteur d'x ou de capitale)."""
    return epine(x_bord, hauteur * HAUTEUR_EPINE[cote], cote, p)


def bord_gauche_diagonale(haut: Point, bas: Point, largeur: float, y: float) -> float:
    """Abscisse du bord gauche d'un trait() à la hauteur y (pour y poser une épine)."""
    (x1, y1), (x2, y2) = haut, bas
    return x1 + (x2 - x1) * (y - y1) / (y2 - y1) - largeur / 2


def ancres(chasse: float, haut: float) -> dict:
    return {"top": (chasse / 2, haut), "bottom": (chasse / 2, 0)}


def pique(base: Point, direction: Point, longueur: float, cou: float) -> Contour:
    """Pointe de queue de diable en pique de carte : deux lobes arrondis, pointe aiguë, orientée selon direction."""
    norme = (direction[0] ** 2 + direction[1] ** 2) ** 0.5
    ux, uy = direction[0] / norme, direction[1] / norme

    def placer(u: float, v: float) -> Point:
        return base[0] + u * ux - v * uy, base[1] + u * uy + v * ux

    L = longueur
    return [
        placer(-L * 0.15, cou / 2),
        ("c", placer(-L * 0.4, L * 0.2), placer(-L * 0.25, L * 0.5), placer(L * 0.12, L * 0.42)),
        ("c", placer(L * 0.42, L * 0.36), placer(L * 0.75, L * 0.14), placer(L, 0)),
        ("c", placer(L * 0.75, -L * 0.14), placer(L * 0.42, -L * 0.36), placer(L * 0.12, -L * 0.42)),
        ("c", placer(-L * 0.25, -L * 0.5), placer(-L * 0.4, -L * 0.2), placer(-L * 0.15, -cou / 2)),
    ]


def queue_diable(depart: Point, arrivee: Point, p: dict) -> list[Contour]:
    """Queue de diable : part d'un pied de fût, plonge sous la descendante, remonte et finit en pique.

    depart : point haut de la queue dans le pied du fût ; arrivee : point haut de la queue avant la pique.
    """
    epaisseur_depart = p["delie"] * 1.5
    epaisseur_fin = p["delie"] * 1.3 + p["fut"] * 0.1  # assez épaisse pour porter la pique
    (xd, yd), (xa, ya) = depart, arrivee
    ecart = xd - xa
    fond = p["descendante"]
    poignee_1, poignee_2 = (xd - ecart * 0.3, fond - 15), (xa + ecart * 0.15, fond - 10)
    queue = [
        (xd, yd),
        ("c", poignee_1, poignee_2, (xa, ya)),
        (xa, ya - epaisseur_fin),
        ("c", (poignee_2[0], poignee_2[1] - epaisseur_fin), (poignee_1[0], poignee_1[1] - epaisseur_depart),
         (xd, yd - epaisseur_depart)),
    ]
    direction = (xa - poignee_2[0], ya - poignee_2[1])
    taille = 60 + p["fut"] * 0.5
    # la pique recule dans la queue pour s'y souder à toutes les graisses
    recul = epaisseur_fin * 0.6 / (direction[0] ** 2 + direction[1] ** 2) ** 0.5
    base = (xa - direction[0] * recul, ya - epaisseur_fin / 2 - direction[1] * recul)
    pointe = pique(base, direction, taille, epaisseur_fin)
    return [queue, pointe]


# Formes composées communes aux minuscules et aux capitales ----------------------------

def epaule(x_depart: float, x_arrivee: float, haut: float, largeur_fut: float, p: dict) -> Contour:
    """Épaule épaisse qui relie le haut d'un fût au sommet du fût suivant."""
    d = p["depassement_pointe"]
    return bande((x_depart, haut + d - coupe(largeur_fut)), (x_arrivee, haut + d),
                 largeur_fut * 0.25 + p["delie"], debord=largeur_fut * 0.3)


def delie_bas(x_depart: float, x_arrivee: float, largeur_fut: float, p: dict,
              epaisseur: float | None = None) -> Contour:
    """Délié qui ferme le bas d'une lettre, du pied d'un fût vers le fût suivant."""
    e = p["delie"] * 1.5 if epaisseur is None else epaisseur
    return bande((x_depart, -p["depassement_pointe"] + e), (x_arrivee, coupe(largeur_fut)), e,
                 debord=largeur_fut * 0.3)


def forme_s(p: dict, haut: float, f: float, contrepoincon: float,
            avec_epine: bool = True) -> tuple[list[Contour], float]:
    """s rond (minuscule ou capitale) : fût haut à gauche et fût bas à droite reliés par un dos épais."""
    d, g = p["depassement_pointe"], p["approche"]
    dr = g + f + contrepoincon
    crochet = f * 0.5
    # le bord gauche du fût commence au-dessus de sa facette basse : il doit couvrir la base de l'épine
    base_epine = p["ornement"] * 2.5 + p["fut"] * 0.1
    bas_fut_gauche = min(haut * 0.36, haut * HAUTEUR_EPINE[-1] - base_epine / 2 - coupe(f) - 5)
    contours = [
        fut(g, bas_fut_gauche, haut + d, f),
        fut(dr, -d, haut * 0.55, f),
        epaule(g + f, dr + f - crochet, haut, f, p),
        fut(dr + f - crochet, haut * 0.72, haut + d, crochet),
        bande((g + f * 0.5, haut * 0.62), (dr + f * 0.5, haut * 0.5), f * 0.55 + p["delie"] * 0.5),
        fut(g, -d, haut * 0.28, crochet),
        delie_bas(g + crochet, dr, f, p),
    ]
    if avec_epine:
        contours.append(epine_reglee(g, haut, -1, p))
    return contours, dr + f + g


# Trous et transformations -----------------------------------------------------------------

class Trou(list):
    """Contour intérieur (contrepoinçon) : écrit dans le sens horaire, il évide la forme qui le contient."""


def transformer(contours: list[Contour], fonction) -> list[Contour]:
    """Applique fonction(point) à tous les points et poignées ; garde la nature (Trou) de chaque contour."""
    resultat = []
    for contour in contours:
        nouveau = [fonction(e) if e[0] != "c" else ("c", *(fonction(q) for q in e[1:])) for e in contour]
        resultat.append(type(contour)(nouveau))
    return resultat


def decaler(contours: list[Contour], dx: float, dy: float) -> list[Contour]:
    return transformer(contours, lambda q: (q[0] + dx, q[1] + dy))


def pivoter(contours: list[Contour], cx: float, cy: float) -> list[Contour]:
    """Demi-tour autour de (cx, cy) : ¡ et ¿ à partir de ! et ?, ‘ à partir de ’."""
    return transformer(contours, lambda q: (2 * cx - q[0], 2 * cy - q[1]))


def miroir(contours: list[Contour], axe_x: float) -> list[Contour]:
    """Symétrie gauche-droite autour de la verticale axe_x : ) à partir de (."""
    return transformer(contours, lambda q: (2 * axe_x - q[0], q[1]))


def losange_oriente(cx: float, cy: float, longueur: float, largeur: float, angle_degres: float) -> Contour:
    """Losange allongé tourné d'un angle (branches d'astérisque)."""
    from math import cos, radians, sin
    ux, uy = cos(radians(angle_degres)), sin(radians(angle_degres))
    demi_l, demi_w = longueur / 2, largeur / 2
    return [(cx + ux * demi_l, cy + uy * demi_l), (cx - uy * demi_w, cy + ux * demi_w),
            (cx - ux * demi_l, cy - uy * demi_l), (cx + uy * demi_w, cy - ux * demi_w)]


def chevron(x_pointe: float, y_milieu: float, longueur: float, demi_hauteur: float, epaisseur: float) -> Contour:
    """Chevron pointé vers la gauche (‹) ; miroir() donne ›."""
    haut, bas = (x_pointe + longueur, y_milieu + demi_hauteur), (x_pointe + longueur, y_milieu - demi_hauteur)
    return [(x_pointe, y_milieu), haut, (haut[0] + epaisseur, haut[1]), (x_pointe + epaisseur, y_milieu),
            (bas[0] + epaisseur, bas[1]), bas]


def echelle(contours: list[Contour], facteur: float, dx: float, dy: float) -> list[Contour]:
    """Réduit (ou agrandit) puis déplace : ordinaux ª º, lettres dans © ® ™ @."""
    return transformer(contours, lambda q: (q[0] * facteur + dx, q[1] * facteur + dy))


def anneau(cx: float, cy: float, rayon: float, epaisseur: float) -> list[Contour]:
    """Anneau octogonal (©, ®, @) : contour extérieur et trou intérieur."""
    def octogone(r: float) -> Contour:
        a = r * 0.42
        return [(cx - a, cy + r), (cx + a, cy + r), (cx + r, cy + a), (cx + r, cy - a),
                (cx + a, cy - r), (cx - a, cy - r), (cx - r, cy - a), (cx - r, cy + a)]
    return [octogone(rayon), Trou(octogone(rayon - epaisseur))]
