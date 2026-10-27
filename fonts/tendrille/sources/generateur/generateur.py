"""Générateur paramétrique de Tendrille.

Chaque glyphe est un squelette (ligne médiane du geste d'écriture) tracé avec une plume
elliptique inclinée, puis légèrement irrégularisé de façon déterministe : la graine est
le nom du glyphe, donc chaque build redonne exactement les mêmes contours.

Usage :
    python sources/generateur/generateur.py sources/Tendrille-Regular.ufo [--sobre]
"""

import argparse
import itertools
import json
import math
import random
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import pathops
import ufoLib2
from ufoLib2.objects import Component

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from espacer import a_espacer, calibrer, espacer_glyphe

PARAMETRES = {
    "hauteur_x": 520,
    "hauteur_capitale": 720,
    "ascendante": 770,
    "descendante": -250,
    "depassement": 12,
    "fut": 88,                  # épaisseur d'un fût vertical
    "delie": 52,                # épaisseur des traits dans l'axe de la plume
    "angle_plume": 30,          # degrés : direction des traits les plus fins
    "approche": 58,             # approches calibrées par espacer.py : minuscules droite (n) / ronde (o)
    "approche_ronde": 44,
    "approche_capitale": 64,    # capitales droite (H) / ronde (O)
    "approche_capitale_ronde": 48,
    "amorce": 55,               # longueur des entrées en délié ; 0 : pas de geste d'entrée
    "sortie": 70,               # sorties en ruban dans le mot (pieds, queues, e) : longueur ; 0 : pas de sortie
    "envol": 50,                # … et hauteur à laquelle remonte leur fin
    "sortie_finale": 210,       # ruban des lettres en fin de mot (variantes .fina, fonction calt) : court, le cœur reste près de sa lettre
    "envol_final": 290,
    "coeur_final": 220,         # largeur de la boucle en cœur qui termine le ruban ; 0 : pas de cœur
    "pression_coeur": 0.6,      # trait du cœur plus léger que les lettres, sans être un fil ; lobes ouverts
    "coeur_point": 165,         # largeur du cœur tracé qui sert de point au i et au j
    "coeur_ponctuation": 140,   # cœur des points de ponctuation (. : ; ! ? … ·), plus petit…
    "pression_ponctuation": 0.5,  # … et plus fin, pour que ses lobes restent ouverts
    "penche_coeur": -28,         # inclinaison (degrés) du cœur de fin de mot : penché vers la droite, dans l'élan
    "espace": 330,              # espace entre les mots : large, pour que rubans et cœurs ne lient jamais deux mots
    "espace_fine": 180,         # espace fine (U+2009) et fine insécable (U+202F) de la typographie française
    "debord_max": 40,           # un cœur peut mordre d'autant sur l'espace voisine, pas plus : il ne touche jamais le mot d'à côté
    "hauteur_chiffres": 700,    # chiffres alignés un peu sous les capitales, comme à la main
    "fin_de_mot": False,        # interne : vrai pendant le dessin des variantes .fina
    "capitale_coeur": False,    # interne : vrai pendant le dessin des capitales à cœur (.ss04)
    "points_inverses": False,   # interne : vrai pendant le dessin des variantes .ss02 (cœurs ↔ ronds)
    "a_ecole": False,           # interne : vrai pendant le dessin du a à un étage (.ss01)
    "effile_minimum": 0.25,     # largeur relative à la pointe d'un trait effilé
    "levee_de_plume": 0.82,     # largeur relative là où une boucle se referme
    "force_effilement": 1.0,    # 1 : effilements dessinés ; 0 : traits de largeur constante
    "inclinaison_max": 1.5,     # degrés : inclinaison propre d'un fût
    "asymetrie_max": 0.03,      # part de la tension des courbes
    "vibration_max": 5,         # unités : décalage des points du squelette
}

def version_opentype() -> tuple[int, int]:
    """(versionMajor, versionMinor) lue dans police.json, tenu à jour par release-please : 0.2.0 -> (0, 200).
    Même conversion que tools/polices.py du dépôt fonts ; 0.0.0 tant que la police n'a pas de version publiée."""
    fichier = Path(__file__).resolve().parents[2] / "police.json"
    version = json.loads(fichier.read_text(encoding="utf-8"))["version"] if fichier.exists() else "0.0.0"
    majeure, mineure, correctif = (int(partie) for partie in version.split("."))
    return majeure, mineure * 100 + correctif

# Famille « Tendrille Texte » : mêmes formes, sans le geste irrégulier
PARAMETRES_SOBRES = {
    "fut": 90, "delie": 76, "angle_plume": 12, "amorce": 0, "sortie": 0, "envol": 0, "sortie_finale": 0, "envol_final": 0, "coeur_final": 0, "espace": 280, "espace_fine": 150,
    "levee_de_plume": 1, "force_effilement": 0.35,
    "inclinaison_max": 0, "asymetrie_max": 0, "vibration_max": 0,
}


Commande = tuple[str, tuple[tuple[float, float], ...]]
Squelette = list[Commande]

DESSINS: dict[str, tuple[int | None, Callable[[], tuple[list["Trait"], float, dict]]]] = {}

# Capitales dont l'entrée devient un cœur suspendu au fût dans le jeu « Capitales à cœur » (X.ss04)
CAPITALES_COEUR = ("B", "D", "E", "F", "H", "J", "K", "L", "M", "N", "P", "R", "U", "V", "W", "Y")

# Glyphes dont les points changent de forme avec ss02 (les composés suivent : variantes_composees.py)
POINTS_SS02 = ("i", "j", "period", "colon", "semicolon", "exclam", "question", "ellipsis", "periodcentered",
               "exclamdown", "questiondown", "divide", "bullet", "dotaccentcomb", "dotaccentcomb.case",
               "dieresiscomb", "dieresiscomb.case", "dotaccent", "dieresis")
# Ponctuation remontée au centre des capitales par la fonction case : (glyphe, décalage vertical)
PONCTUATION_CASE = {"hyphen": 100, "endash": 100, "emdash": 100, "uni2212": 40, "parenleft": 65, "parenright": 65,
                    "bracketleft": 65, "bracketright": 65, "braceleft": 65, "braceright": 65,
                    "guillemetleft": 100, "guillemetright": 100, "guilsinglleft": 100, "guilsinglright": 100,
                    "periodcentered": 100, "bullet": 40, "exclamdown": 200, "questiondown": 200}
CHIFFRES = ("zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine")

# En fin de mot, ces lettres prennent un grand ruban terminé par un cœur (X.fina)
LETTRES_FINALES = ("a", "c", "d", "e", "h", "i", "dotlessi", "k", "l", "m", "n", "r", "t", "u", "z")


def glyphe(nom: str, point_code: int | None = None):
    def enregistrer(fonction):
        DESSINS[nom] = (point_code, fonction)
        return fonction
    return enregistrer


# Squelettes ---------------------------------------------------------------

def demi_trait() -> float:
    """Demi-épaisseur d'un fût vertical, pour placer les squelettes."""
    return PARAMETRES["fut"] / 2


def boucle_ovale(cx: float, cy: float, rx: float, ry: float, inclinaison: float = 0) -> Squelette:
    """Ovale tracé d'un seul geste, à partir du haut à droite, dans le sens antihoraire, incliné en degrés."""
    depart = 60
    pas = 90
    points = []
    angle = depart
    fin = depart + 360
    while angle < fin:
        suivant = min(angle + pas, fin)
        points.append(_arc_elliptique(cx, cy, rx, ry, angle, suivant))
        angle = suivant
    debut = _point_ellipse(cx, cy, rx, ry, depart)
    squelette = [("moveTo", (debut,))] + [("curveTo", segment) for segment in points]
    return [(commande, tuple(_tourner(point, (cx, cy), inclinaison) for point in pts)) for commande, pts in squelette]


def boucle_croisee(cx: float, cy: float, rx: float, ry: float, depart: float, depassement: float,
                   inclinaison: float = 0) -> Squelette:
    """Ovale tracé d'un seul geste qui croise son départ, comme à la main.

    Le trait part du haut (angle « depart », en degrés) et tourne dans le sens antihoraire en s'élargissant
    légèrement ; au retour, il continue de « depassement » degrés en plongeant vers l'intérieur,
    donc il passe par-dessus le départ et finit dans la contre-forme.
    """
    def echelle(angle: float) -> tuple[float, float]:
        """Rapport au rayon et sa dérivée (par radian)."""
        tour = 2 * math.pi
        ecart = angle - math.radians(depart)
        if ecart <= tour:
            return 0.97 + 0.09 * ecart / tour, 0.09 / tour
        fin = math.radians(depassement)
        u = (ecart - tour) / fin
        return 1.06 - 0.22 * u * u, -0.44 * u / fin

    def position(angle: float) -> tuple[tuple[float, float], tuple[float, float]]:
        s, ds = echelle(angle)
        point = (cx + s * rx * math.cos(angle), cy + s * ry * math.sin(angle))
        tangente = (ds * rx * math.cos(angle) - s * rx * math.sin(angle), ds * ry * math.sin(angle) + s * ry * math.cos(angle))
        return point, tangente

    bornes = [math.radians(depart + 90 * i) for i in range(5)] + [math.radians(depart + 360 + depassement)]
    point, tangente = position(bornes[0])
    squelette: Squelette = [("moveTo", (point,))]
    for debut_arc, fin_arc in itertools.pairwise(bornes):
        pas = fin_arc - debut_arc
        suivant, tangente_suivante = position(fin_arc - 1e-9)
        squelette.append(("curveTo", ((point[0] + tangente[0] * pas / 3, point[1] + tangente[1] * pas / 3),
                                      (suivant[0] - tangente_suivante[0] * pas / 3, suivant[1] - tangente_suivante[1] * pas / 3),
                                      suivant)))
        point, tangente = suivant, tangente_suivante
    return [(commande, tuple(_tourner(point, (cx, cy), inclinaison) for point in points)) for commande, points in squelette]


def _tourner(point: tuple[float, float], centre: tuple[float, float], degres: float) -> tuple[float, float]:
    angle = math.radians(degres)
    x, y = point[0] - centre[0], point[1] - centre[1]
    return centre[0] + x * math.cos(angle) - y * math.sin(angle), centre[1] + x * math.sin(angle) + y * math.cos(angle)


def _point_ellipse(cx: float, cy: float, rx: float, ry: float, angle: float) -> tuple[float, float]:
    radians = math.radians(angle)
    return cx + rx * math.cos(radians), cy + ry * math.sin(radians)


def _arc_elliptique(cx, cy, rx, ry, debut, fin) -> tuple[tuple[float, float], ...]:
    """Arc d'ellipse approché par une Bézier cubique (exact à 0,03 % près jusqu'à 90°)."""
    a1, a2 = math.radians(debut), math.radians(fin)
    k = 4 / 3 * math.tan((a2 - a1) / 4)
    x1, y1 = math.cos(a1), math.sin(a1)
    x2, y2 = math.cos(a2), math.sin(a2)
    controle1 = (cx + rx * (x1 - k * y1), cy + ry * (y1 + k * x1))
    controle2 = (cx + rx * (x2 + k * y2), cy + ry * (y2 - k * x2))
    return controle1, controle2, (cx + rx * x2, cy + ry * y2)


# Irrégularités déterministes ------------------------------------------------

def irregulariser(traits: list["Trait"], graine: str) -> list["Trait"]:
    """Inclinaison propre, asymétrie des courbes et vibration, toujours identiques pour un glyphe.

    La vibration déplace chaque point sur la courbe avec ses poignées, pour garder des courbes souples ;
    une boucle fermée garde son point d'arrivée sur son point de départ.
    """
    p = PARAMETRES
    hasard = random.Random(graine)
    resultat = []
    for trait in traits:
        inclinaison = math.tan(math.radians(hasard.uniform(-p["inclinaison_max"], p["inclinaison_max"])))
        tension = 1 + hasard.uniform(-p["asymetrie_max"], p["asymetrie_max"])
        nb_points = len(trait.squelette)
        ecarts = [(hasard.uniform(-p["vibration_max"], p["vibration_max"]),
                   hasard.uniform(-p["vibration_max"], p["vibration_max"])) for _ in range(nb_points)]
        if trait.ferme:
            ecarts[-1] = ecarts[0]

        def deplacer(point, ecart, inclinaison=inclinaison):
            return point[0] + point[1] * inclinaison + ecart[0], point[1] + ecart[1]

        def poignee(controle, ancrage, ecart, tension=tension):
            x = ancrage[0] + (controle[0] - ancrage[0]) * tension
            y = ancrage[1] + (controle[1] - ancrage[1]) * tension
            return deplacer((x, y), ecart)

        nouveau: Squelette = []
        precedent, ecart_precedent = None, None
        for (commande, points), ecart in zip(trait.squelette, ecarts, strict=True):
            if commande == "lineTo":  # une ligne devient une courbe tendue : ses raccords restent lisses
                (x0, y0), (x1, y1) = precedent, points[0]
                commande = "curveTo"
                points = ((x0 + (x1 - x0) / 3, y0 + (y1 - y0) / 3), (x0 + 2 * (x1 - x0) / 3, y0 + 2 * (y1 - y0) / 3), points[0])
            if commande == "curveTo":
                c1, c2, arrivee = points
                points = (poignee(c1, precedent, ecart_precedent), poignee(c2, arrivee, ecart), deplacer(arrivee, ecart))
                precedent = arrivee
            else:
                precedent = points[-1]
                points = tuple(deplacer(point, ecart) for point in points)
            ecart_precedent = ecart
            nouveau.append((commande, points))
        resultat.append(Trait(nouveau, trait.effile_debut, trait.effile_fin, trait.ferme, trait.pression))
    return resultat


# Plume ----------------------------------------------------------------------

ECHANTILLONS_PAR_MORCEAU = 16  # précision du bord calculé avant l'ajustement des courbes
MORCEAUX_PAR_SEGMENT = 2       # fixe : même nombre de courbes dans tous les masters
KAPPA = 0.5523                 # quart de cercle en Bézier cubique
RAPPORT_MONTEE = 0.9           # un trait qui monte est plus léger qu'un trait qui descend

Point = tuple[float, float]
Courbe = tuple[Point, Point, Point]  # poignée de départ, poignée d'arrivée, point d'arrivée


@dataclass
class Trait:
    """Un geste : squelette et effilement au départ et à l'arrivée (1 = pas d'effilement).

    Une boucle fermée (o, O) n'a pas d'extrémités : effile_debut y donne la largeur relative
    à l'endroit où la plume se lève, là où la boucle se referme.
    """
    squelette: Squelette
    effile_debut: float = 1.0
    effile_fin: float = 1.0
    ferme: bool = False
    pression: float = 1.0  # < 1 : trait plus léger sur toute sa longueur (boucle du cœur)


def _bezier(p0, p1, p2, p3, t):
    u = 1 - t
    point = tuple(u**3 * a + 3 * u * u * t * b + 3 * u * t * t * c + t**3 * d for a, b, c, d in zip(p0, p1, p2, p3))
    tangente = tuple(3 * u * u * (b - a) + 6 * u * t * (c - b) + 3 * t * t * (d - c) for a, b, c, d in zip(p0, p1, p2, p3))
    return point, tangente


def echantillonner(squelette: Squelette) -> list[tuple[Point, Point]]:
    """Points et tangentes le long du squelette, en nombre fixe par segment (le premier point est partagé)."""
    par_segment = ECHANTILLONS_PAR_MORCEAU * MORCEAUX_PAR_SEGMENT
    echantillons = []
    courant = None
    for commande, points in squelette:
        if commande == "moveTo":
            courant = points[0]
            continue
        if commande == "lineTo":
            controles = (courant, courant, points[0], points[0])
            direction = (points[0][0] - courant[0], points[0][1] - courant[1])
        else:
            controles = (courant, *points)
        for i in range(0 if not echantillons else 1, par_segment + 1):
            t = i / par_segment
            if commande == "lineTo":
                echantillons.append(((courant[0] + direction[0] * t, courant[1] + direction[1] * t), direction))
            else:
                echantillons.append(_bezier(*controles, t))
        courant = points[-1]
    return echantillons


def largeur_plume(tangente: Point) -> float:
    """Plume elliptique inclinée : épaisseur qui varie sans à-coup avec la direction du trait.

    Fine dans l'axe de la plume (« delie »), un fût vertical vaut exactement « fut » ;
    un trait qui monte s'allège progressivement, jusqu'à RAPPORT_MONTEE à la verticale.
    """
    p = PARAMETRES
    direction = math.atan2(tangente[1], tangente[0])
    angle = math.radians(p["angle_plume"])
    plein_carre = (p["fut"] ** 2 - (p["delie"] * math.sin(angle)) ** 2) / math.cos(angle) ** 2
    ecart = direction - angle
    largeur = math.sqrt((p["delie"] * math.cos(ecart)) ** 2 + plein_carre * math.sin(ecart) ** 2)
    montee = max(0.0, math.sin(direction))
    return largeur * (1 - (1 - RAPPORT_MONTEE) * montee * montee)


def _profil_effilement(distances: list[float], trait: Trait) -> list[float]:
    """Facteur de pression le long du trait : monte en douceur depuis la pointe sur la longueur d'une amorce."""
    longueur = distances[-1] or 1
    zone = min(max(PARAMETRES["amorce"], 30) * 1.6, longueur / 2)
    zone_fin = min(max(PARAMETRES["sortie"] * 0.6, 50), longueur / 2)  # le ruban garde du corps, s'effile au bout
    if trait.ferme:
        return [_lisser(min(distance, longueur - distance), zone, trait.effile_debut) for distance in distances]
    return [min(_lisser(distance, zone, trait.effile_debut), _lisser(longueur - distance, zone_fin, trait.effile_fin))
            for distance in distances]


def _lisser(bout: float, zone: float, effile: float) -> float:
    effile = 1 - (1 - effile) * PARAMETRES["force_effilement"]
    if effile >= 1 or bout >= zone:
        return 1.0
    progression = bout / zone
    return effile + (1 - effile) * progression * progression * (3 - 2 * progression)


def _unitaire(vecteur: Point) -> Point:
    norme = math.hypot(*vecteur) or 1
    return vecteur[0] / norme, vecteur[1] / norme


def _ajuster(points: list[Point], tangente_depart: Point, tangente_arrivee: Point) -> Courbe:
    """Une Bézier cubique au plus près des points, extrémités et directions imposées (moindres carrés de Schneider)."""
    longueurs = [0.0]
    for a, b in itertools.pairwise(points):
        longueurs.append(longueurs[-1] + math.dist(a, b))
    corde = longueurs[-1] or 1
    depart, arrivee = points[0], points[-1]
    c = [[0.0, 0.0], [0.0, 0.0]]
    x = [0.0, 0.0]
    for point, longueur in zip(points, longueurs, strict=True):
        u = longueur / corde
        b0, b1, b2, b3 = (1 - u) ** 3, 3 * u * (1 - u) ** 2, 3 * u * u * (1 - u), u ** 3
        a1 = (tangente_depart[0] * b1, tangente_depart[1] * b1)
        a2 = (tangente_arrivee[0] * b2, tangente_arrivee[1] * b2)
        c[0][0] += a1[0] * a1[0] + a1[1] * a1[1]
        c[0][1] += a1[0] * a2[0] + a1[1] * a2[1]
        c[1][1] += a2[0] * a2[0] + a2[1] * a2[1]
        reste = (point[0] - (depart[0] * (b0 + b1) + arrivee[0] * (b2 + b3)),
                 point[1] - (depart[1] * (b0 + b1) + arrivee[1] * (b2 + b3)))
        x[0] += a1[0] * reste[0] + a1[1] * reste[1]
        x[1] += a2[0] * reste[0] + a2[1] * reste[1]
    c[1][0] = c[0][1]
    determinant = c[0][0] * c[1][1] - c[0][1] * c[1][0]
    alpha1 = alpha2 = corde / 3
    if abs(determinant) > 1e-9:
        alpha1 = (x[0] * c[1][1] - x[1] * c[0][1]) / determinant
        alpha2 = (c[0][0] * x[1] - c[1][0] * x[0]) / determinant
    if alpha1 < corde * 1e-3 or alpha2 < corde * 1e-3:
        alpha1 = alpha2 = corde / 3
    return ((depart[0] + tangente_depart[0] * alpha1, depart[1] + tangente_depart[1] * alpha1),
            (arrivee[0] + tangente_arrivee[0] * alpha2, arrivee[1] + tangente_arrivee[1] * alpha2), arrivee)


def _bord_en_courbes(bord: list[Point], ferme: bool) -> list[Courbe]:
    """Découpe un bord calculé finement en morceaux de taille fixe et ajuste une courbe sur chacun."""
    nombre = len(bord)

    def tangente(i: int) -> Point:
        if ferme:
            return _unitaire((bord[(i + 1) % nombre][0] - bord[i - 1][0], bord[(i + 1) % nombre][1] - bord[i - 1][1]))
        avant, apres = max(i - 1, 0), min(i + 1, nombre - 1)
        return _unitaire((bord[apres][0] - bord[avant][0], bord[apres][1] - bord[avant][1]))

    courbes = []
    dernier = nombre if ferme else nombre - 1
    for debut in range(0, dernier, ECHANTILLONS_PAR_MORCEAU):
        fin = debut + ECHANTILLONS_PAR_MORCEAU
        morceau = [bord[i % nombre] for i in range(debut, fin + 1)]
        t_fin = tangente(fin % nombre)
        courbes.append(_ajuster(morceau, tangente(debut), (-t_fin[0], -t_fin[1])))
    return courbes


def _demi_cercle(centre: Point, rayon: float, cote: Point, avant: Point) -> list[Courbe]:
    """Bout arrondi exact : deux quarts de cercle du côté « cote » vers le côté opposé, en passant par « avant »."""
    cx, cy = centre

    def point(u: Point, v: Point = (0, 0), k: float = 0) -> Point:
        return cx + rayon * (u[0] + k * v[0]), cy + rayon * (u[1] + k * v[1])

    oppose = (-cote[0], -cote[1])
    return [(point(cote, avant, KAPPA), point(avant, cote, KAPPA), point(avant)),
            (point(avant, oppose, KAPPA), point(oppose, avant, KAPPA), point(oppose))]


def _inverser(depart: Point, courbes: list[Courbe]) -> tuple[Point, list[Courbe]]:
    """Même contour parcouru dans l'autre sens."""
    points = [depart] + [courbe[2] for courbe in courbes]
    inverses = [(courbe[1], courbe[0], points[i]) for i, courbe in enumerate(courbes)]
    return points[-1], inverses[::-1]


def oriente(depart: Point, courbes: list[Courbe], exterieur: bool) -> tuple[Point, list[Courbe]]:
    """Contour extérieur dans le sens antihoraire, contre-forme dans le sens horaire (convention UFO)."""
    polygone = [depart] + [point for courbe in courbes for point in courbe]
    aire = sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(polygone, polygone[1:] + polygone[:1]))
    return (depart, courbes) if (aire > 0) == exterieur else _inverser(depart, courbes)


def _aire(points: list[Point]) -> float:
    return sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(points, points[1:] + points[:1])) / 2


def contours_du_trait(trait: Trait) -> list[tuple[Point, list[Courbe]]]:
    """Contours fermés du trait à largeur variable : bords ajustés en courbes, bouts en demi-cercles."""
    echantillons = echantillonner(trait.squelette)
    distances = [0.0]
    for (a, _), (b, _) in itertools.pairwise(echantillons):
        distances.append(distances[-1] + math.dist(a, b))
    facteurs = _profil_effilement(distances, trait)
    gauche, droite, demis = [], [], []
    for ((x, y), tangente), facteur in zip(echantillons, facteurs):
        tx, ty = _unitaire(tangente)
        demi = largeur_plume(tangente) * facteur * trait.pression / 2
        gauche.append((x - ty * demi, y + tx * demi))
        droite.append((x + ty * demi, y - tx * demi))
        demis.append(demi)
    if trait.ferme:
        # Le contour extérieur est le plus grand, quel que soit le sens du tracé
        # (pour une boucle antihoraire, le bord gauche est à l'intérieur)
        gauche, droite = gauche[:-1], droite[:-1]
        exterieur, interieur = sorted((gauche, droite), key=lambda bord: abs(_aire(bord)), reverse=True)
        return [oriente(exterieur[0], _bord_en_courbes(exterieur, True), exterieur=True),
                oriente(interieur[0], _bord_en_courbes(interieur, True), exterieur=False)]
    (fin, t_fin), (debut, t_debut) = echantillons[-1], echantillons[0]
    t_fin, t_debut = _unitaire(t_fin), _unitaire(t_debut)
    _, retour = _inverser(droite[0], _bord_en_courbes(droite, False))
    courbes = (_bord_en_courbes(gauche, False)
               + _demi_cercle(fin, demis[-1], (-t_fin[1], t_fin[0]), t_fin)
               + retour
               + _demi_cercle(debut, demis[0], (t_debut[1], -t_debut[0]), (-t_debut[0], -t_debut[1])))
    return [oriente(gauche[0], courbes, exterieur=True)]


def tracer_contour(stylo, depart: Point, courbes: list[Courbe]) -> None:
    """Écrit le contour en coordonnées entières, sans segment de longueur nulle
    (sinon l'arrondi crée des segments superposés, signalés par Font Bakery)."""
    def entier(point: Point) -> tuple[int, int]:
        return round(point[0]), round(point[1])

    courant = entier(depart)
    stylo.moveTo(courant)
    for courbe in courbes:
        c1, c2, arrivee = (entier(point) for point in courbe)
        if arrivee == courant:
            continue
        stylo.curveTo(c1, c2, arrivee)
        courant = arrivee
    stylo.closePath()


# Éléments communs des minuscules --------------------------------------------

def _haut_fut(hauteur: float) -> float:
    """Ordonnée du squelette au sommet d'un fût de cette hauteur (le bout rond affleure la hauteur)."""
    return hauteur - demi_trait()


def _haut_arche() -> float:
    p = PARAMETRES
    return p["hauteur_x"] + p["depassement"] - p["delie"] / 2


def _bas_bol() -> float:
    p = PARAMETRES
    return -p["depassement"] + p["delie"] / 2


def entree(x: float, haut: float) -> list[Trait]:
    """Délié presque droit qui monte depuis la gauche et se fond dans le haut du fût ; rien si l'amorce est nulle."""
    a = PARAMETRES["amorce"]
    if not a:
        return []
    if PARAMETRES["capitale_coeur"]:  # le cœur pend au sommet du fût, penché vers la gauche
        return coeur_trace((x - 6, haut - 12), PARAMETRES["coeur_final"], inclinaison=20, effile_debut=0.6)
    squelette = [
        ("moveTo", ((x - a * 1.3, haut - a * 1.1),)),
        ("curveTo", ((x - a * 0.8, haut - a * 0.6), (x - a * 0.3, haut - 8), (x + 6, haut))),
    ]
    return [Trait(squelette, effile_debut=PARAMETRES["effile_minimum"])]


def fut(x: float, haut: float, bas: float) -> Trait:
    return Trait([("moveTo", ((x, haut),)), ("lineTo", ((x, bas),))])


def arche(x_gauche: float, x_droite: float) -> Squelette:
    """Arche de n, h, m : naît bas sur le fût gauche, sommet décalé à gauche, redescend sur le fût droit."""
    haut, sommet = _haut_fut(PARAMETRES["hauteur_x"]), _haut_arche()
    largeur = x_droite - x_gauche
    milieu = x_gauche + largeur * 0.46
    return [
        ("moveTo", ((x_gauche, haut - 150),)),
        ("curveTo", ((x_gauche + 10, sommet - 60), (milieu - largeur * 0.28, sommet), (milieu, sommet))),
        ("curveTo", ((milieu + largeur * 0.32, sommet), (x_droite, sommet - 70), (x_droite, haut - 160))),
    ]


def pied(x: float, ligne: float = 0, avec_ruban: bool = True) -> Squelette:
    """Fin de fût posée sur « ligne » (ligne de base ou descendante) : descend, tourne large vers la droite
    et, si le geste est dessiné, remonte en délié."""
    p = PARAMETRES
    rayon = p["fut"] * 1.15  # assez large pour que le bord intérieur ne se plisse pas quand le trait s'amincit
    bas = ligne + demi_trait() - p["depassement"]
    squelette = [
        ("lineTo", ((x, bas + rayon),)),
        ("curveTo", ((x, bas + rayon * 0.45), (x + rayon * 0.45, bas), (x + rayon, bas))),
    ]
    if avec_ruban:
        squelette += ruban((x + rayon, bas), sens=1)
    return squelette


def ruban(depart: "Point", sens: int, part: float = 1.0) -> Squelette:
    """Sortie en ruban depuis « depart » (trait horizontal) : remonte en une seule courbe et s'envole en délié.
    sens = 1 vers la droite, -1 vers la gauche ; part réduit longueur et remontée (épaule du r, déjà haute).
    Rien si la sortie est nulle."""
    longueur, envol = PARAMETRES["sortie"] * part, PARAMETRES["envol"] * part
    if not longueur:
        return []
    x, y = depart
    # Une seule courbe qui commence à monter dès la sortie du virage : pas de palier au fond
    return [("curveTo", ((x + sens * longueur * 0.3, y), (x + sens * longueur * 0.68, y + envol * 0.3),
                         (x + sens * longueur, y + envol)))]


def queue_gauche(x: float) -> Squelette:
    """Descendante du j et du g : tourne large vers la gauche et file à l'horizontale,
    là où la plume à 30° reste fine."""
    p = PARAMETRES
    rayon = p["fut"] * 1.15
    bas = p["descendante"] + p["delie"] / 2
    return [
        ("lineTo", ((x, bas + rayon),)),
        ("curveTo", ((x, bas + rayon * 0.45), (x - rayon * 0.45, bas), (x - rayon, bas))),
    ] + (ruban((x - rayon, bas), sens=-1) if PARAMETRES["sortie"]
         else [("curveTo", ((x - rayon - 30, bas), (x - rayon - 60, bas + 4), (x - rayon - 80, bas + 12)))])


def largeur_pied() -> float:
    """Débord du pied à droite du fût, pour la chasse."""
    return PARAMETRES["fut"] * 1.15 + PARAMETRES["sortie"] * 0.6


def point_rond(x: float, y: float) -> Trait:
    """Point posé d'un coup de plume : un trait si court qu'il paraît rond (16 unités : assez pour un contour propre)."""
    return Trait([("moveTo", ((x - 6, y + 6),)), ("lineTo", ((x + 6, y - 6),))])


def point(x: float, y_bas: float) -> list[Trait]:
    """Point de ponctuation posé sur « y_bas » : un petit cœur dans Tendrille, un rond dans Tendrille Texte."""
    p = PARAMETRES
    if not points_en_coeur():
        return [point_rond(x, y_bas + demi_trait())]
    return coeur_trace((x, y_bas + 5), p["coeur_ponctuation"], inclinaison=-8, effile_debut=0.45,
                       pression=p["pression_ponctuation"])


def points_en_coeur() -> bool:
    """Cœurs dans Tendrille, ronds dans Tendrille Texte ; ss02 inverse."""
    return bool(PARAMETRES["amorce"]) != PARAMETRES["points_inverses"]


def point_suscrit(x: float) -> list[Trait]:
    """Point du i et du j : le même cœur tracé que les rubans dans Tendrille, un rond dans Tendrille Texte."""
    p = PARAMETRES
    if not points_en_coeur():
        return [point_rond(x, p["hauteur_x"] + 170)]
    return coeur_trace((x, p["hauteur_x"] + 70), p["coeur_point"], inclinaison=-8, effile_debut=0.45)  # pointe en bas


# Cœur tracé d'un seul geste, en coordonnées relatives à sa pointe (largeur 1) : le trait part de la pointe,
# monte dans le lobe gauche, passe le creux, fait le lobe droit et revient finir sur la pointe, effilé.
# Au creux, la plume change brusquement de direction : deux gestes s'y rejoignent.

def coeur_trace(pointe: "Point", largeur: float, inclinaison: float,
                elan: float | None = None, effile_debut: float = 1.0, pression: float | None = None) -> list[Trait]:
    """Cœur qui part de « pointe » et y finit, incliné en degrés.

    elan : direction (radians) du trait qui arrive à la pointe (ruban), pour un départ sans angle ;
    sans elan, le trait part vers le haut et la gauche, comme une plume qui se pose (point du i et du j).
    """
    def placer(u: float, v: float) -> "Point":
        return _tourner((pointe[0] + u * largeur, pointe[1] + v * largeur), pointe, inclinaison)

    if elan is None:
        poignee = placer(-0.18, 0.12)
    else:
        poignee = (pointe[0] + math.cos(elan) * largeur * 0.25, pointe[1] + math.sin(elan) * largeur * 0.25)
    pression = PARAMETRES["pression_coeur"] if pression is None else pression
    lobe_gauche = [
        ("moveTo", (pointe,)),
        ("curveTo", (poignee, placer(-0.48, 0.36), placer(-0.48, 0.62))),
        ("curveTo", (placer(-0.48, 0.86), placer(-0.38, 1.0), placer(-0.22, 0.99))),
        ("curveTo", (placer(-0.08, 0.98), placer(-0.01, 0.9), placer(0, 0.76))),
    ]
    lobe_droit = [
        ("moveTo", (placer(0, 0.76),)),
        ("curveTo", (placer(0.01, 0.9), placer(0.08, 0.98), placer(0.22, 0.99))),
        ("curveTo", (placer(0.38, 1.0), placer(0.48, 0.86), placer(0.48, 0.62))),
        ("curveTo", (placer(0.48, 0.38), placer(0.18, 0.14), pointe)),  # la fin du trait est la pointe du cœur
    ]
    return [Trait(lobe_gauche, effile_debut=effile_debut, pression=pression),
            Trait(lobe_droit, effile_fin=PARAMETRES["effile_minimum"], pression=pression)]


def boucle_en_coeur(squelette: Squelette, largeur: float) -> list[Trait]:
    """Le ruban arrive à la pointe du cœur, qui s'enroule depuis là et y revient, penché dans le sens de l'élan."""
    pointe = squelette[-1][1][-1]
    avant = squelette[-1][1][-2] if squelette[-1][0] == "curveTo" else squelette[-2][1][-1]
    elan = math.atan2(pointe[1] - avant[1], pointe[0] - avant[0])
    return coeur_trace(pointe, largeur, PARAMETRES["penche_coeur"], elan=elan)


def ancres_minuscule(chasse: float, haut: float | None = None) -> dict:
    """Ancres d'une minuscule ; « haut » : hauteur réelle de la lettre (ascendante pour b d h k l)."""
    return {"top": (chasse / 2, PARAMETRES["hauteur_x"] if haut is None else haut), "bottom": (chasse / 2, 0)}


def _avec_arche_et_pied(x_gauche: float, x_droite: float) -> Trait:
    return Trait(arche(x_gauche, x_droite) + pied(x_droite), 0.35, PARAMETRES["effile_minimum"])


# Minuscules -------------------------------------------------------------------

@glyphe("n", 0x6E)
def dessiner_n():
    p = PARAMETRES
    x_gauche = p["approche"] + demi_trait()
    x_droite = x_gauche + p["fut"] + 300
    haut = _haut_fut(p["hauteur_x"])
    traits = [fut(x_gauche, haut, demi_trait()), _avec_arche_et_pied(x_gauche, x_droite)] + entree(x_gauche, haut)
    chasse = x_droite + demi_trait() + p["approche"]
    return traits, chasse, ancres_minuscule(chasse)


@glyphe("h", 0x68)
def dessiner_h():
    p = PARAMETRES
    x_gauche = p["approche"] + demi_trait()
    x_droite = x_gauche + p["fut"] + 300
    haut = _haut_fut(p["ascendante"])
    traits = [fut(x_gauche, haut, demi_trait()), _avec_arche_et_pied(x_gauche, x_droite)] + entree(x_gauche, haut)
    chasse = x_droite + demi_trait() + p["approche"]
    return traits, chasse, ancres_minuscule(chasse, PARAMETRES["ascendante"])


@glyphe("m", 0x6D)
def dessiner_m():
    p = PARAMETRES
    contre_forme = 240  # plus serrée que le n pour garder un m compact et distinct de « rn »
    x1 = p["approche"] + demi_trait()
    x2 = x1 + p["fut"] + contre_forme
    x3 = x2 + p["fut"] + contre_forme
    haut = _haut_fut(p["hauteur_x"])
    arche_milieu = Trait(arche(x1, x2) + [("lineTo", ((x2, demi_trait()),))], 0.35)
    traits = [fut(x1, haut, demi_trait()), arche_milieu, _avec_arche_et_pied(x2, x3)] + entree(x1, haut)
    chasse = x3 + demi_trait() + p["approche"]
    return traits, chasse, ancres_minuscule(chasse)


@glyphe("u", 0x75)
def dessiner_u():
    p = PARAMETRES
    x_gauche = p["approche"] + demi_trait()
    x_droite = x_gauche + p["fut"] + 300
    haut = _haut_fut(p["hauteur_x"])
    bas = _bas_bol()
    largeur = x_droite - x_gauche
    milieu = x_gauche + largeur * 0.54
    # Le n retourné : descente, bol décalé à droite, remontée qui s'allège
    bol = [
        ("moveTo", ((x_gauche, haut),)),
        ("lineTo", ((x_gauche, p["hauteur_x"] - haut + 160),)),
        ("curveTo", ((x_gauche, bas + 70), (milieu - largeur * 0.32, bas), (milieu, bas))),
        ("curveTo", ((milieu + largeur * 0.28, bas), (x_droite - 10, bas + 60), (x_droite, p["hauteur_x"] - haut + 150))),
    ]
    fut_droit = Trait([("moveTo", ((x_droite, haut),))] + pied(x_droite), effile_fin=p["effile_minimum"])
    traits = [Trait(bol, effile_fin=0.35), fut_droit] + entree(x_gauche, haut)
    chasse = x_droite + demi_trait() + p["approche"]
    return traits, chasse, ancres_minuscule(chasse)


@glyphe("r", 0x72)
def dessiner_r():
    p = PARAMETRES
    x = p["approche"] + demi_trait()
    haut = _haut_fut(p["hauteur_x"])
    sommet = _haut_arche()
    epaule = [
        ("moveTo", ((x, haut - 150),)),
        ("curveTo", ((x + 10, sommet - 60), (x + 50, sommet), (x + 105, sommet))),
        ("curveTo", ((x + 140, sommet), (x + 165, sommet - 25), (x + 178, sommet - 95))),
    ]  # épaule courte qui retombe : garde un blanc avant la lettre suivante (rn ≠ m)
    if p["fin_de_mot"]:  # en fin de mot, l'épaule file en ruban, sans monter au-delà de la hampe
        epaule = epaule[:2] + [("curveTo", ((x + 150, sommet), (x + 180, sommet - 20), (x + 200, sommet - 40)))]
        epaule += ruban((x + 200, sommet - 40), sens=1, part=0.4)
    traits = [fut(x, haut, demi_trait()), Trait(epaule, 0.35, p["effile_minimum"])] + entree(x, haut)
    chasse = x + 178 + p["approche"] * 0.5
    return traits, chasse, ancres_minuscule(chasse)


def _fut_i() -> tuple[list[Trait], float]:
    p = PARAMETRES
    x = p["approche"] + demi_trait()
    haut = _haut_fut(p["hauteur_x"])
    traits = [Trait([("moveTo", ((x, haut),))] + pied(x), effile_fin=p["effile_minimum"])] + entree(x, haut)
    return traits, x


@glyphe("i", 0x69)
def dessiner_i():
    traits, x = _fut_i()
    chasse = x + largeur_pied() + PARAMETRES["approche"] * 0.6
    return traits + point_suscrit(x), chasse, ancres_minuscule(chasse)


@glyphe("dotlessi", 0x131)
def dessiner_dotlessi():
    traits, x = _fut_i()
    chasse = x + largeur_pied() + PARAMETRES["approche"] * 0.6
    return traits, chasse, ancres_minuscule(chasse)


def _queue_j() -> tuple[list[Trait], float]:
    p = PARAMETRES
    x = p["approche"] + demi_trait() + 90  # la queue déborde à gauche
    haut = _haut_fut(p["hauteur_x"])
    traits = [Trait([("moveTo", ((x, haut),))] + queue_gauche(x), effile_fin=p["effile_minimum"])] + entree(x, haut)
    return traits, x


@glyphe("j", 0x6A)
def dessiner_j():
    traits, x = _queue_j()
    chasse = x + demi_trait() + PARAMETRES["approche"]
    return traits + point_suscrit(x), chasse, ancres_minuscule(chasse)


@glyphe("uni0237", 0x237)
def dessiner_dotlessj():
    traits, x = _queue_j()
    chasse = x + demi_trait() + PARAMETRES["approche"]
    return traits, chasse, ancres_minuscule(chasse)


@glyphe("l", 0x6C)
def dessiner_l():
    p = PARAMETRES
    x = p["approche"] + demi_trait()
    haut = _haut_fut(p["ascendante"])
    traits = [Trait([("moveTo", ((x, haut),))] + pied(x), effile_fin=p["effile_minimum"])] + entree(x, haut)
    chasse = x + largeur_pied() + p["approche"] * 0.6
    return traits, chasse, ancres_minuscule(chasse, PARAMETRES["ascendante"])


# Rondes et dérivées -----------------------------------------------------------

RAYON_BOL = 175  # demi-largeur du bol de b d p q g, un peu plus étroit que le o


def arc(cx: float, cy: float, rx: float, ry: float, debut: float, fin: float) -> Squelette:
    """Arc d'ellipse de « debut » à « fin » (degrés ; sens antihoraire si fin > debut, horaire sinon)."""
    nombre = max(1, math.ceil(abs(fin - debut) / 90))
    pas = (fin - debut) / nombre
    squelette: Squelette = [("moveTo", (_point_ellipse(cx, cy, rx, ry, debut),))]
    for i in range(nombre):
        squelette.append(("curveTo", _arc_elliptique(cx, cy, rx, ry, debut + i * pas, debut + (i + 1) * pas)))
    return squelette


def _ry_rond() -> float:
    """Demi-hauteur du squelette d'une ronde de hauteur d'x (le trait dépasse en haut et en bas)."""
    p = PARAMETRES
    return (p["hauteur_x"] + 2 * p["depassement"] - p["delie"]) / 2


def bol(x_fut: float, cote: str) -> Trait:
    """Bol accroché au fût : à gauche (d, q, g) il tourne dans le sens antihoraire, à droite (b, p) dans l'autre."""
    cy = PARAMETRES["hauteur_x"] / 2
    if cote == "gauche":
        squelette = arc(x_fut - RAYON_BOL, cy, RAYON_BOL, _ry_rond(), 25, 335)
    else:
        squelette = arc(x_fut + RAYON_BOL, cy, RAYON_BOL, _ry_rond(), 155, -155)
    return Trait(squelette, effile_debut=0.5, effile_fin=0.8)


@glyphe("c", 0x63)
def dessiner_c():
    p = PARAMETRES
    rx = 220 - demi_trait()
    cx = p["approche_ronde"] + 220
    cy = p["hauteur_x"] / 2
    ouverture = arc(cx, cy, rx, _ry_rond(), 48, 270)
    if p["fin_de_mot"]:  # la fin ne remonte pas : elle s'échappe en ruban
        ouverture += ruban(ouverture[-1][1][-1], sens=1)
    else:
        ouverture = arc(cx, cy, rx, _ry_rond(), 48, 312)
    ouverture = [(commande, tuple(_tourner(point, (cx, cy), -8) for point in points)) for commande, points in ouverture]
    traits = [Trait(ouverture, effile_debut=0.45, effile_fin=p["effile_minimum"])]
    chasse = cx + 220 + p["approche_ronde"]
    return traits, chasse, ancres_minuscule(chasse)


@glyphe("e", 0x65)
def dessiner_e():
    p = PARAMETRES
    rx = 230 - demi_trait()
    ry = _ry_rond()
    cx = p["approche_ronde"] + 230
    cy = p["hauteur_x"] / 2
    haut, bas = cy + ry, cy - ry
    y_barre = 285  # œil au-dessus du milieu, ouverture basse généreuse
    droite = cx + rx
    # Un seul geste : barre vers la droite, virage large, tour par le haut et la gauche, sortie ouverte en bas à droite
    geste = [
        ("moveTo", ((cx - rx + 15, y_barre),)),
        ("curveTo", ((cx + rx * 0.3, y_barre), (droite, y_barre + 10), (droite, y_barre + 95))),
        ("curveTo", ((droite, haut - 60), (cx + rx * 0.55, haut), (cx, haut))),
        ("curveTo", ((cx - rx * 0.55, haut), (cx - rx, cy + ry * 0.55), (cx - rx, cy))),
        ("curveTo", ((cx - rx, cy - ry * 0.55), (cx - rx * 0.55, bas), (cx, bas))),
        ("curveTo", ((cx + rx * 0.42, bas), (cx + rx * 0.74, cy - ry * 0.8), (cx + rx * 0.84, cy - ry * 0.55))),
    ]
    if p["sortie"]:  # la fin ne remonte pas dans l'œil : elle s'échappe vers la droite
        geste[-1] = ("curveTo", ((cx + rx * 0.42, bas), (cx + rx * 0.72, bas + 12), (cx + rx * 0.9, bas + 45)))
        geste.append(("curveTo", ((cx + rx * 1.02, bas + 62), (cx + rx + p["sortie"] * 0.5, bas + 45 + p["envol"] * 0.3),
                                  (cx + rx + p["sortie"] * 0.85, bas + 45 + p["envol"]))))
    geste = [(commande, tuple(_tourner(point, (cx, cy), -6) for point in points)) for commande, points in geste]
    traits = [Trait(geste, effile_debut=0.6, effile_fin=p["effile_minimum"])]
    chasse = cx + 230 + p["approche_ronde"]
    return traits, chasse, ancres_minuscule(chasse)


@glyphe("b", 0x62)
def dessiner_b():
    p = PARAMETRES
    x = p["approche"] + demi_trait()
    haut = _haut_fut(p["ascendante"])
    traits = [fut(x, haut, demi_trait()), bol(x, "droite")] + entree(x, haut)
    chasse = x + 2 * RAYON_BOL + demi_trait() + p["approche_ronde"]
    return traits, chasse, ancres_minuscule(chasse, PARAMETRES["ascendante"])


@glyphe("d", 0x64)
def dessiner_d():
    p = PARAMETRES
    x = p["approche_ronde"] + demi_trait() + 2 * RAYON_BOL
    haut = _haut_fut(p["ascendante"])
    traits = [bol(x, "gauche"), Trait([("moveTo", ((x, haut),))] + pied(x), effile_fin=p["effile_minimum"])]
    traits += entree(x, haut)
    chasse = x + largeur_pied() + p["approche"] * 0.6
    return traits, chasse, ancres_minuscule(chasse, PARAMETRES["ascendante"])


@glyphe("p", 0x70)
def dessiner_p():
    p = PARAMETRES
    x = p["approche"] + demi_trait()
    haut = _haut_fut(p["hauteur_x"])
    traits = [Trait(fut(x, haut, p["descendante"] + demi_trait()).squelette, effile_fin=0.8), bol(x, "droite")]
    traits += entree(x, haut)
    chasse = x + 2 * RAYON_BOL + demi_trait() + p["approche_ronde"]
    return traits, chasse, ancres_minuscule(chasse)


@glyphe("q", 0x71)
def dessiner_q():
    p = PARAMETRES
    x = p["approche_ronde"] + demi_trait() + 2 * RAYON_BOL
    haut = _haut_fut(p["hauteur_x"])
    # Pas d'entrée, mais une queue relevée vers la droite sous la ligne : q n'est jamais le reflet de p
    queue = Trait([("moveTo", ((x, haut),))] + pied(x, ligne=p["descendante"]), effile_fin=p["effile_minimum"])
    traits = [bol(x, "gauche"), queue]
    chasse = x + largeur_pied() + p["approche"] * 0.6
    return traits, chasse, ancres_minuscule(chasse)


@glyphe("g", 0x67)
def dessiner_g():
    p = PARAMETRES
    x = p["approche_ronde"] + demi_trait() + 2 * RAYON_BOL
    haut = _haut_fut(p["hauteur_x"])
    traits = [bol(x, "gauche"), Trait([("moveTo", ((x, haut),))] + queue_gauche(x), effile_fin=p["effile_minimum"])]
    chasse = x + demi_trait() + p["approche"]
    return traits, chasse, ancres_minuscule(chasse)


@glyphe("a", 0x61)
def dessiner_a():
    p = PARAMETRES
    if p["a_ecole"]:  # a à un étage, comme à l'école : un bol et un fût qui finit par le pied
        x = p["approche_ronde"] + demi_trait() + 2 * RAYON_BOL
        haut = _haut_fut(p["hauteur_x"])
        traits = [bol(x, "gauche"), Trait([("moveTo", ((x, haut),))] + pied(x), effile_fin=p["effile_minimum"])]
        chasse = x + largeur_pied() + p["approche"] * 0.6
        return traits, chasse, ancres_minuscule(chasse)
    x_gauche = p["approche_ronde"] + demi_trait()
    x = x_gauche + 330
    sommet = _haut_arche()
    bas = _bas_bol()
    # Crochet du haut qui se fond dans le fût, puis pied
    crochet = [
        ("moveTo", ((x_gauche + 30, 400),)),
        ("curveTo", ((x_gauche + 55, sommet - 10), (x - 190, sommet), (x - 110, sommet))),
        ("curveTo", ((x - 45, sommet), (x, sommet - 55), (x, sommet - 175))),  # virage large, sans pli
    ] + pied(x)
    # Petit bol du bas, qui naît sur le fût
    petit_bol = [
        ("moveTo", ((x, 300),)),
        ("curveTo", ((x - 110, 318), (x_gauche, 285), (x_gauche, 160))),
        ("curveTo", ((x_gauche, 55), (x_gauche + 70, bas), (x_gauche + 160, bas))),
        ("curveTo", ((x_gauche + 240, bas), (x - 15, 45), (x, 95))),
    ]
    traits = [Trait(crochet, effile_debut=0.4, effile_fin=p["effile_minimum"]), Trait(petit_bol, effile_debut=0.4, effile_fin=0.8)]
    chasse = x + largeur_pied() + p["approche"] * 0.6
    return traits, chasse, ancres_minuscule(chasse)


# Barres, diagonales et dernières minuscules -------------------------------------

def barre(x_debut: float, x_fin: float, y: float, montee: float = 10) -> Trait:
    """Barre horizontale légèrement montante, effilée aux deux bouts (f, t)."""
    return Trait([("moveTo", ((x_debut, y),)), ("lineTo", ((x_fin, y + montee),))], effile_debut=0.6, effile_fin=0.6)


def diagonale(depart: "Point", arrivee: "Point", **effilements) -> Trait:
    return Trait([("moveTo", (depart,)), ("lineTo", (arrivee,))], **effilements)


@glyphe("f", 0x66)
def dessiner_f():
    p = PARAMETRES
    x = p["approche"] + demi_trait() + 60
    sommet = p["ascendante"] - p["delie"] / 2
    # Le fût monte de la ligne de base et finit en crochet effilé vers la droite
    fut_crochet = [
        ("moveTo", ((x, demi_trait()),)),
        ("lineTo", ((x, sommet - 170),)),
        ("curveTo", ((x, sommet - 60), (x + 40, sommet), (x + 110, sommet))),
        ("curveTo", ((x + 150, sommet), (x + 175, sommet - 15), (x + 190, sommet - 45))),
    ]
    traits = [Trait(fut_crochet, effile_fin=p["effile_minimum"]), barre(x - 95, x + 140, p["hauteur_x"] - 25)]
    chasse = x + 190 + p["approche"] * 0.3
    return traits, chasse, ancres_minuscule(chasse, PARAMETRES["ascendante"])


@glyphe("t", 0x74)
def dessiner_t():
    p = PARAMETRES
    x = p["approche"] + demi_trait() + 60
    y_barre = p["hauteur_x"] - 25
    if p["fin_de_mot"]:  # le pied reste sobre ; la barre file en ruban jusqu'au cœur
        fut_pied = Trait([("moveTo", ((x, 650),))] + pied(x, avec_ruban=False), effile_debut=0.4, effile_fin=0.6)
        barre_ruban = [("moveTo", ((x - 95, y_barre),)), ("lineTo", ((x + 110, y_barre + 10),))]
        barre_ruban += ruban((x + 110, y_barre + 10), sens=1, part=0.4)  # partie de la barre : reste sous le haut des capitales
        traits = [fut_pied, Trait(barre_ruban, effile_debut=0.6, effile_fin=0.55)]
    else:
        fut_pied = Trait([("moveTo", ((x, 650),))] + pied(x), effile_debut=0.4, effile_fin=p["effile_minimum"])
        traits = [fut_pied, barre(x - 95, x + 125, y_barre)]
    chasse = x + largeur_pied() + p["approche"] * 0.6
    return traits, chasse, ancres_minuscule(chasse)


@glyphe("k", 0x6B)
def dessiner_k():
    p = PARAMETRES
    x = p["approche"] + demi_trait()
    haut = _haut_fut(p["ascendante"])
    bas = demi_trait() - p["depassement"]
    # Deux gestes : le changement de direction au fût est trop brusque pour un seul trait
    bras = [("moveTo", ((x + 225, p["hauteur_x"] - 25),)),
            ("curveTo", ((x + 175, 420), (x + 90, 300), (x + 15, 250)))]
    jambe = [
        ("moveTo", ((x + 25, 265),)),
        ("curveTo", ((x + 110, 215), (x + 170, 130), (x + 195, 70))),
        ("curveTo", ((x + 210, 35), (x + 235, bas), (x + 270, bas))),
    ] + ruban((x + 270, bas), sens=1)
    traits = [fut(x, haut, demi_trait()), Trait(bras, effile_debut=0.45), Trait(jambe, effile_fin=p["effile_minimum"])]
    traits += entree(x, haut)
    chasse = x + 270 + p["sortie"] * 0.6 + p["approche"] * 0.6
    return traits, chasse, ancres_minuscule(chasse, PARAMETRES["ascendante"])


def _haut_diagonale() -> float:
    return _haut_fut(PARAMETRES["hauteur_x"])


def forme_v(x1: float, largeur: float, haut: float) -> list[Trait]:
    p = PARAMETRES
    x2, xm = x1 + largeur, x1 + largeur / 2
    remontee = [("moveTo", ((xm, 15),)), ("curveTo", ((xm + largeur * 0.18, haut * 0.3), (x2 - 10, haut * 0.75), (x2, haut - 30)))]
    if p["amorce"]:  # la remontée finit en petite boucle vers la droite
        remontee.append(("curveTo", ((x2 + 5, haut), (x2 + 30, haut + 6), (x2 + 55, haut - 10))))
    return [diagonale((x1, haut), (xm, 15), effile_fin=0.8), Trait(remontee, effile_fin=p["effile_minimum"])] + entree(x1, haut)


def forme_w(x1: float, largeur: float, haut: float, creux: float) -> list[Trait]:
    """W manuscrit : le sommet du milieu reste plus bas (de « creux »)."""
    p = PARAMETRES
    xa, xb, xc, x2 = x1 + largeur * 0.25, x1 + largeur * 0.5, x1 + largeur * 0.75, x1 + largeur
    remontee = [("moveTo", ((xc, 15),)), ("curveTo", ((xc + largeur * 0.09, haut * 0.3), (x2 - 8, haut * 0.75), (x2, haut - 30)))]
    if p["amorce"]:
        remontee.append(("curveTo", ((x2 + 5, haut), (x2 + 30, haut + 6), (x2 + 55, haut - 10))))
    return [
        diagonale((x1, haut), (xa, 15), effile_fin=0.8),
        diagonale((xa, 15), (xb, haut - creux), effile_fin=0.8),
        diagonale((xb, haut - creux), (xc, 15), effile_fin=0.8),
        Trait(remontee, effile_fin=p["effile_minimum"]),
    ] + entree(x1, haut)


def forme_x(x1: float, largeur: float, haut: float) -> list[Trait]:
    """Une descente pleine et une montée en délié, comme le donne la plume à 30°."""
    x2 = x1 + largeur
    return [diagonale((x1, haut), (x2, demi_trait()), effile_debut=0.5, effile_fin=0.7),
            diagonale((x1 + 10, demi_trait()), (x2 - 10, haut), effile_debut=0.6, effile_fin=PARAMETRES["effile_minimum"])]


def forme_z(x1: float, largeur: float, haut: float) -> list[Trait]:
    p = PARAMETRES
    x2, bas = x1 + largeur, demi_trait()
    base = [("moveTo", ((x1, bas),)), ("lineTo", ((x2, bas),))] + ruban((x2, bas), sens=1)
    return [
        Trait([("moveTo", ((x1, haut - 10),)), ("lineTo", ((x2, haut),))], effile_debut=0.5),
        diagonale((x2, haut), (x1, bas + 5)),
        Trait(base, effile_fin=p["effile_minimum"] if p["sortie"] else 0.8),
    ]


@glyphe("v", 0x76)
def dessiner_v():
    p = PARAMETRES
    x1 = p["approche"] + demi_trait() + 20
    chasse = x1 + 330 + demi_trait() + p["approche"] * 0.5
    return forme_v(x1, 330, _haut_diagonale()), chasse, ancres_minuscule(chasse)


@glyphe("w", 0x77)
def dessiner_w():
    p = PARAMETRES
    x1 = p["approche"] + demi_trait() + 20
    chasse = x1 + 520 + demi_trait() + p["approche"] * 0.5
    return forme_w(x1, 520, _haut_diagonale(), creux=90), chasse, ancres_minuscule(chasse)


@glyphe("x", 0x78)
def dessiner_x():
    p = PARAMETRES
    x1 = p["approche"] + demi_trait()
    chasse = x1 + 320 + demi_trait() + p["approche"]
    return forme_x(x1, 320, _haut_diagonale()), chasse, ancres_minuscule(chasse)


@glyphe("y", 0x79)
def dessiner_y():
    p = PARAMETRES
    haut = _haut_diagonale()
    x1 = p["approche"] + demi_trait() + 20
    x2 = x1 + 330
    bas = p["descendante"] + p["delie"] / 2
    # Le trait de droite descend sous la ligne et file vers la gauche, comme la queue du j
    queue = [
        ("moveTo", ((x2, haut),)),
        ("curveTo", ((x2 - 40, 300), (x2 - 110, 20), (x2 - 150, -110))),
        ("curveTo", ((x2 - 172, -180), (x2 - 205, bas), (x2 - 255, bas))),
    ] + (ruban((x2 - 255, bas), sens=-1) if p["sortie"]
         else [("curveTo", ((x2 - 285, bas), (x2 - 315, bas + 4), (x2 - 335, bas + 12)))])
    traits = [diagonale((x1, haut), (x2 - 125, 15), effile_fin=0.8), Trait(queue, effile_fin=p["effile_minimum"])]
    traits += entree(x1, haut)
    chasse = x2 + demi_trait() + p["approche"]
    return traits, chasse, ancres_minuscule(chasse)


@glyphe("z", 0x7A)
def dessiner_z():
    p = PARAMETRES
    x1 = p["approche"] + demi_trait()
    chasse = x1 + 300 + demi_trait() + p["sortie"] * 0.6 + p["approche"]
    return forme_z(x1, 300, _haut_diagonale()), chasse, ancres_minuscule(chasse)


def forme_s(x1: float, largeur: float, hauteur: float) -> list[Trait]:
    """Un seul geste, de la pointe en haut à droite jusqu'à la pointe en bas à gauche ; « hauteur » : x ou capitale."""
    p = PARAMETRES
    x2, cx, cy = x1 + largeur, x1 + largeur / 2, hauteur / 2
    sommet = hauteur + p["depassement"] - p["delie"] / 2
    bas = _bas_bol()
    k = hauteur / 520  # proportions dessinées pour la hauteur d'x

    def y(valeur: float) -> float:
        return valeur * k

    geste = [
        ("moveTo", ((x2 - 10, y(430)),)),
        ("curveTo", ((x2 - 40, y(490)), (cx + largeur * 0.2, sommet), (cx, sommet))),
        ("curveTo", ((cx - largeur * 0.37, sommet), (x1, y(460)), (x1, y(380)))),
        ("curveTo", ((x1, y(300)), (cx - largeur * 0.2, y(275)), (cx, y(255)))),
        ("curveTo", ((cx + largeur * 0.23, y(235)), (x2, y(210)), (x2, y(130)))),
        ("curveTo", ((x2, y(50)), (cx + largeur * 0.3, bas), (cx, bas))),
        ("curveTo", ((cx - largeur * 0.3, bas), (x1 - 10, y(40)), (x1 - 15, y(100)))),
    ]
    geste = [(commande, tuple(_tourner(point, (cx, cy), -6) for point in points)) for commande, points in geste]
    return [Trait(geste, effile_debut=0.45, effile_fin=p["effile_minimum"])]


@glyphe("s", 0x73)
def dessiner_s():
    p = PARAMETRES
    x1 = p["approche_ronde"] + demi_trait()
    chasse = x1 + 300 + demi_trait() + p["approche_ronde"]
    return forme_s(x1, 300, p["hauteur_x"]), chasse, ancres_minuscule(chasse)


@glyphe("o", 0x6F)
def dessiner_o():
    p = PARAMETRES
    d = demi_trait()
    largeur = 480
    rx = largeur / 2 - d
    ry = (p["hauteur_x"] + 2 * p["depassement"] - p["delie"]) / 2
    cx = p["approche_ronde"] + largeur / 2
    chasse = largeur + 2 * p["approche_ronde"]
    ancres = {"top": (chasse / 2, p["hauteur_x"]), "bottom": (chasse / 2, 0)}
    if not p["amorce"]:
        boucle = boucle_ovale(cx, p["hauteur_x"] / 2, rx, ry, inclinaison=-8)
        return [Trait(boucle, effile_debut=p["levee_de_plume"], ferme=True)], chasse, ancres
    boucle = boucle_croisee(cx, p["hauteur_x"] / 2, rx, ry, depart=95, depassement=40, inclinaison=-8)
    return [Trait(boucle, effile_debut=0.6, effile_fin=p["effile_minimum"])], chasse, ancres  # même geste que le O


@glyphe("H", 0x48)
def dessiner_H():
    p = PARAMETRES
    d = demi_trait()
    a = p["amorce"]
    x_gauche = p["approche"] + d + a * 0.6
    x_droite = x_gauche + p["fut"] + 420
    haut = p["hauteur_capitale"] - d
    y_barre = p["hauteur_capitale"] * 0.5
    traits = [Trait(fut(x_gauche, haut, d).squelette, effile_fin=0.8), Trait(fut(x_droite, haut, d).squelette, effile_fin=0.8)]
    if not a:
        traits.append(Trait([("moveTo", ((x_gauche, y_barre - 6),)), ("lineTo", ((x_droite, y_barre + 10),))]))
    else:
        # Barre en vague, qui file à droite en délié
        barre = [
            ("moveTo", ((x_gauche - a * 0.6, y_barre - 30),)),
            ("curveTo", ((x_gauche + 90, y_barre + 40), (x_droite - 200, y_barre - 45), (x_droite - 40, y_barre + 5))),
            ("curveTo", ((x_droite + a * 0.3, y_barre + 35), (x_droite + a * 0.8, y_barre + 30), (x_droite + a * 1.3, y_barre + 10))),
        ]
        traits.append(Trait(barre, p["effile_minimum"], p["effile_minimum"]))
    traits += entree(x_gauche, haut)
    chasse = x_droite + d + p["approche"] + a * 0.5
    ancres = {"top": (chasse / 2, p["hauteur_capitale"]), "bottom": (chasse / 2, 0)}
    return traits, chasse, ancres


@glyphe("O", 0x4F)
def dessiner_O():
    p = PARAMETRES
    d = demi_trait()
    largeur = 660
    rx = largeur / 2 - d
    ry = (p["hauteur_capitale"] + 2 * p["depassement"] - p["delie"]) / 2
    cx = p["approche_ronde"] + largeur / 2
    chasse = largeur + 2 * p["approche_ronde"]
    ancres = {"top": (chasse / 2, p["hauteur_capitale"]), "bottom": (chasse / 2, 0)}
    if not p["amorce"]:
        boucle = boucle_ovale(cx, p["hauteur_capitale"] / 2, rx, ry, inclinaison=-6)
        return [Trait(boucle, effile_debut=p["levee_de_plume"], ferme=True)], chasse, ancres
    boucle = boucle_croisee(cx, p["hauteur_capitale"] / 2, rx, ry, depart=95, depassement=40, inclinaison=-6)
    return [Trait(boucle, effile_debut=0.6, effile_fin=p["effile_minimum"])], chasse, ancres  # départ fondu, fin effilée


# Capitales ---------------------------------------------------------------------

def _cap() -> float:
    return PARAMETRES["hauteur_capitale"]


def _haut_cap() -> float:
    return _haut_fut(_cap())


def ancres_capitale(chasse: float) -> dict:
    return {"top": (chasse / 2, _cap()), "bottom": (chasse / 2, 0)}


def fut_capitale(x: float, haut: float | None = None) -> Trait:
    return Trait(fut(x, _haut_cap() if haut is None else haut, demi_trait()).squelette, effile_fin=0.8)


def barre_capitale(x_debut: float, x_fin: float, y: float) -> Trait:
    """Barre en vague légère, comme celle du H, droite quand le geste n'est pas dessiné."""
    if not PARAMETRES["amorce"]:
        return Trait([("moveTo", ((x_debut, y - 6),)), ("lineTo", ((x_fin, y + 6),))])
    largeur = x_fin - x_debut
    vague = [("moveTo", ((x_debut, y - 12),)),
             ("curveTo", ((x_debut + largeur * 0.3, y + 22), (x_debut + largeur * 0.65, y - 22), (x_fin, y + 10)))]
    return Trait(vague, effile_debut=0.6, effile_fin=0.6)


def panse(x: float, y_haut: float, y_bas: float, largeur: float) -> Trait:
    """Demi-rond accroché au fût (B, D, P, R), qui naît fin sur le fût."""
    hauteur = y_haut - y_bas
    squelette = [
        ("moveTo", ((x, y_haut),)),
        ("curveTo", ((x + largeur * 0.55, y_haut), (x + largeur, y_haut - hauteur * 0.05), (x + largeur, (y_haut + y_bas) / 2))),
        ("curveTo", ((x + largeur, y_bas + hauteur * 0.05), (x + largeur * 0.55, y_bas), (x, y_bas))),
    ]
    return Trait(squelette, effile_debut=0.6, effile_fin=0.85)


def _haut_panse() -> float:
    return _cap() + 4 - PARAMETRES["delie"] / 2


@glyphe("A", 0x41)
def dessiner_A():
    p = PARAMETRES
    x1 = p["approche_capitale"] + demi_trait()
    x2 = x1 + 560
    sommet = (x1 + x2) / 2
    traits = [
        diagonale((x1, demi_trait()), (sommet, _haut_cap()), effile_debut=0.8),
        diagonale((sommet, _haut_cap()), (x2, demi_trait()), effile_fin=0.8),
        barre_capitale(x1 + 120, x2 - 90, 250),
    ]
    chasse = x2 + demi_trait() + p["approche_capitale"]
    return traits, chasse, ancres_capitale(chasse)


@glyphe("B", 0x42)
def dessiner_B():
    p = PARAMETRES
    x = p["approche_capitale"] + demi_trait()
    traits = [fut_capitale(x), panse(x, _haut_panse(), 375, 250), panse(x, 375, demi_trait() - 4, 310)] + entree(x, _haut_cap())
    chasse = x + 310 + demi_trait() + p["approche_capitale_ronde"]
    return traits, chasse, ancres_capitale(chasse)


@glyphe("C", 0x43)
def dessiner_C():
    p = PARAMETRES
    rx, ry = 300 - demi_trait(), (_cap() + 2 * p["depassement"] - p["delie"]) / 2
    cx, cy = p["approche_capitale_ronde"] + 300, _cap() / 2
    geste = [(commande, tuple(_tourner(point, (cx, cy), -6) for point in points))
             for commande, points in arc(cx, cy, rx, ry, 48, 312)]
    traits = [Trait(geste, effile_debut=0.45, effile_fin=p["effile_minimum"])]
    chasse = cx + 300 + p["approche_capitale_ronde"]
    return traits, chasse, ancres_capitale(chasse)


@glyphe("D", 0x44)
def dessiner_D():
    p = PARAMETRES
    x = p["approche_capitale"] + demi_trait()
    traits = [fut_capitale(x), panse(x, _haut_panse(), demi_trait() - 4, 470)] + entree(x, _haut_cap())
    chasse = x + 470 + demi_trait() + p["approche_capitale_ronde"]
    return traits, chasse, ancres_capitale(chasse)


def _barres_E(x: float, avec_bas: bool) -> list[Trait]:
    p = PARAMETRES
    bas = demi_trait()
    traits = [Trait([("moveTo", ((x, _haut_cap() + 4),)), ("lineTo", ((x + 340, _haut_cap() + 14),))], effile_fin=0.6),
              Trait([("moveTo", ((x, 370),)), ("lineTo", ((x + 270, 378),))], effile_fin=0.6)]
    if avec_bas:
        base = [("moveTo", ((x, bas),)), ("lineTo", ((x + 340, bas),))] + ruban((x + 340, bas), sens=1)
        traits.append(Trait(base, effile_fin=p["effile_minimum"] if p["sortie"] else 0.8))
    return traits


@glyphe("E", 0x45)
def dessiner_E():
    p = PARAMETRES
    x = p["approche_capitale"] + demi_trait()
    traits = [fut_capitale(x)] + _barres_E(x, avec_bas=True) + entree(x, _haut_cap())
    chasse = x + 340 + p["sortie"] * 0.6 + demi_trait() + p["approche_capitale"] * 0.6
    return traits, chasse, ancres_capitale(chasse)


@glyphe("F", 0x46)
def dessiner_F():
    p = PARAMETRES
    x = p["approche_capitale"] + demi_trait()
    traits = [fut_capitale(x)] + _barres_E(x, avec_bas=False) + entree(x, _haut_cap())
    chasse = x + 340 + demi_trait() + p["approche_capitale"] * 0.4
    return traits, chasse, ancres_capitale(chasse)


@glyphe("G", 0x47)
def dessiner_G():
    p = PARAMETRES
    rx, ry = 310 - demi_trait(), (_cap() + 2 * p["depassement"] - p["delie"]) / 2
    cx, cy = p["approche_capitale_ronde"] + 310, _cap() / 2
    geste = [(commande, tuple(_tourner(point, (cx, cy), -6) for point in points))
             for commande, points in arc(cx, cy, rx, ry, 48, 355)]
    eperon = barre_capitale(cx + 40, cx + rx + 25, cy - 20)
    traits = [Trait(geste, effile_debut=0.45, effile_fin=0.85), eperon]
    chasse = cx + 310 + p["approche_capitale_ronde"]
    return traits, chasse, ancres_capitale(chasse)


@glyphe("I", 0x49)
def dessiner_I():
    p = PARAMETRES
    x = p["approche_capitale"] + demi_trait() + 110
    # Barres en haut et en bas : I ne se confond ni avec l ni avec |
    traits = [fut_capitale(x),
              Trait([("moveTo", ((x - 110, _haut_cap() + 4),)), ("lineTo", ((x + 110, _haut_cap() + 12),))], effile_debut=0.6, effile_fin=0.6),
              Trait([("moveTo", ((x - 110, demi_trait()),)), ("lineTo", ((x + 110, demi_trait() + 6),))], effile_debut=0.6, effile_fin=0.6)]
    chasse = x + 110 + demi_trait() + p["approche_capitale"] * 0.6
    return traits, chasse, ancres_capitale(chasse)


@glyphe("J", 0x4A)
def dessiner_J():
    p = PARAMETRES
    x = p["approche_capitale"] + demi_trait() + 170
    rayon = p["fut"] * 1.15
    bas = demi_trait() - p["depassement"]
    crochet = [
        ("moveTo", ((x, _haut_cap()),)),
        ("lineTo", ((x, bas + rayon * 1.6),)),
        ("curveTo", ((x, bas + rayon * 0.4), (x - rayon * 0.5, bas), (x - rayon * 1.1, bas))),
        ("curveTo", ((x - rayon * 1.5, bas), (x - rayon * 1.8, bas + 25), (x - rayon * 1.95, bas + 70))),
    ]
    traits = [Trait(crochet, effile_fin=p["effile_minimum"])] + entree(x, _haut_cap())
    chasse = x + demi_trait() + p["approche_capitale"]
    return traits, chasse, ancres_capitale(chasse)


@glyphe("K", 0x4B)
def dessiner_K():
    p = PARAMETRES
    x = p["approche_capitale"] + demi_trait()
    bas = demi_trait() - p["depassement"]
    bras = [("moveTo", ((x + 340, _haut_cap()),)), ("curveTo", ((x + 260, 560), (x + 120, 380), (x + 15, 320)))]
    jambe = [
        ("moveTo", ((x + 30, 345),)),
        ("curveTo", ((x + 160, 280), (x + 270, 140), (x + 310, 70))),
        ("curveTo", ((x + 325, 35), (x + 345, bas), (x + 380, bas))),
    ] + ruban((x + 380, bas), sens=1)
    traits = [fut_capitale(x), Trait(bras, effile_debut=0.45), Trait(jambe, effile_fin=p["effile_minimum"])]
    traits += entree(x, _haut_cap())
    chasse = x + 380 + p["sortie"] * 0.6 + p["approche_capitale"] * 0.6
    return traits, chasse, ancres_capitale(chasse)


@glyphe("L", 0x4C)
def dessiner_L():
    p = PARAMETRES
    x = p["approche_capitale"] + demi_trait()
    bas = demi_trait()
    base = [("moveTo", ((x, bas),)), ("lineTo", ((x + 330, bas),))] + ruban((x + 330, bas), sens=1)
    traits = [fut_capitale(x), Trait(base, effile_fin=p["effile_minimum"] if p["sortie"] else 0.8)] + entree(x, _haut_cap())
    chasse = x + 330 + p["sortie"] * 0.6 + demi_trait() + p["approche_capitale"] * 0.6
    return traits, chasse, ancres_capitale(chasse)


@glyphe("M", 0x4D)
def dessiner_M():
    p = PARAMETRES
    x1 = p["approche_capitale"] + demi_trait()
    x2 = x1 + 620
    milieu = (x1 + x2) / 2
    traits = [
        fut_capitale(x1),
        diagonale((x1, _haut_cap()), (milieu, 180), effile_fin=0.85),
        diagonale((milieu, 180), (x2, _haut_cap()), effile_debut=0.85),
        fut_capitale(x2),
    ] + entree(x1, _haut_cap())
    chasse = x2 + demi_trait() + p["approche_capitale"]
    return traits, chasse, ancres_capitale(chasse)


@glyphe("N", 0x4E)
def dessiner_N():
    p = PARAMETRES
    x1 = p["approche_capitale"] + demi_trait()
    x2 = x1 + 480
    traits = [
        fut_capitale(x1),
        diagonale((x1, _haut_cap()), (x2, demi_trait()), effile_fin=0.85),
        Trait([("moveTo", ((x2, demi_trait()),)), ("lineTo", ((x2, _haut_cap()),))], effile_fin=0.6),  # remontée en délié
    ] + entree(x1, _haut_cap())
    chasse = x2 + demi_trait() + p["approche_capitale"]
    return traits, chasse, ancres_capitale(chasse)


@glyphe("P", 0x50)
def dessiner_P():
    p = PARAMETRES
    x = p["approche_capitale"] + demi_trait()
    traits = [fut_capitale(x), panse(x, _haut_panse(), 330, 320)] + entree(x, _haut_cap())
    chasse = x + 320 + demi_trait() + p["approche_capitale_ronde"]
    return traits, chasse, ancres_capitale(chasse)


@glyphe("Q", 0x51)
def dessiner_Q():
    p = PARAMETRES
    traits, chasse, ancres = dessiner_O()
    cx = p["approche_capitale_ronde"] + 330
    # Queue détachée qui traverse le bas : Q ne se confond pas avec O
    queue = [("moveTo", ((cx + 10, 170),)), ("curveTo", ((cx + 120, 80), (cx + 230, -30), (cx + 380, -75)))]
    traits = traits + [Trait(queue, effile_debut=0.6, effile_fin=p["effile_minimum"])]
    return traits, chasse, ancres


@glyphe("R", 0x52)
def dessiner_R():
    p = PARAMETRES
    x = p["approche_capitale"] + demi_trait()
    # Jambe droite et oblique, lisible en petit corps
    traits = [fut_capitale(x), panse(x, _haut_panse(), 350, 300),
              diagonale((x + 150, 350), (x + 360, demi_trait()), effile_fin=0.8)] + entree(x, _haut_cap())
    chasse = x + 360 + demi_trait() + p["approche_capitale"]
    return traits, chasse, ancres_capitale(chasse)


@glyphe("S", 0x53)
def dessiner_S():
    p = PARAMETRES
    x1 = p["approche_capitale_ronde"] + demi_trait()
    chasse = x1 + 400 + demi_trait() + p["approche_capitale_ronde"]
    return forme_s(x1, 400, _cap()), chasse, ancres_capitale(chasse)


@glyphe("T", 0x54)
def dessiner_T():
    p = PARAMETRES
    x = p["approche_capitale"] + demi_trait() + 280
    traits = [fut_capitale(x), barre_capitale(x - 280, x + 280, _haut_cap() + 10)]
    chasse = x + 280 + demi_trait() + p["approche_capitale"] * 0.5
    return traits, chasse, ancres_capitale(chasse)


@glyphe("U", 0x55)
def dessiner_U():
    p = PARAMETRES
    x1 = p["approche_capitale"] + demi_trait()
    x2 = x1 + 500
    milieu = (x1 + x2) / 2
    bas = _bas_bol()
    # Un seul geste : descente, bol, remontée en délié jusqu'en haut
    geste = [
        ("moveTo", ((x1, _haut_cap()),)),
        ("lineTo", ((x1, 260),)),
        ("curveTo", ((x1, 80), (milieu - 150, bas), (milieu, bas))),
        ("curveTo", ((milieu + 150, bas), (x2, 80), (x2, 260))),
        ("lineTo", ((x2, _haut_cap()),)),
    ]
    traits = [Trait(geste, effile_fin=0.6)] + entree(x1, _haut_cap())
    chasse = x2 + demi_trait() + p["approche_capitale"]
    return traits, chasse, ancres_capitale(chasse)


@glyphe("V", 0x56)
def dessiner_V():
    p = PARAMETRES
    x1 = p["approche_capitale"] + demi_trait()
    chasse = x1 + 520 + demi_trait() + p["approche_capitale"] * 0.5
    return forme_v(x1, 520, _haut_cap()), chasse, ancres_capitale(chasse)


@glyphe("W", 0x57)
def dessiner_W():
    p = PARAMETRES
    x1 = p["approche_capitale"] + demi_trait()
    chasse = x1 + 820 + demi_trait() + p["approche_capitale"] * 0.5
    return forme_w(x1, 820, _haut_cap(), creux=160), chasse, ancres_capitale(chasse)


@glyphe("X", 0x58)
def dessiner_X():
    p = PARAMETRES
    x1 = p["approche_capitale"] + demi_trait()
    chasse = x1 + 500 + demi_trait() + p["approche_capitale"]
    return forme_x(x1, 500, _haut_cap()), chasse, ancres_capitale(chasse)


@glyphe("Y", 0x59)
def dessiner_Y():
    p = PARAMETRES
    x1 = p["approche_capitale"] + demi_trait()
    x2 = x1 + 520
    milieu, fourche = (x1 + x2) / 2, 330
    traits = [diagonale((x1, _haut_cap()), (milieu, fourche), effile_fin=0.85),
              diagonale((x2, _haut_cap()), (milieu, fourche), effile_debut=0.6),
              fut_capitale(milieu, haut=fourche)] + entree(x1, _haut_cap())
    chasse = x2 + demi_trait() + p["approche_capitale"]
    return traits, chasse, ancres_capitale(chasse)


@glyphe("Z", 0x5A)
def dessiner_Z():
    p = PARAMETRES
    x1 = p["approche_capitale"] + demi_trait()
    chasse = x1 + 460 + demi_trait() + p["sortie"] * 0.6 + p["approche_capitale"]
    return forme_z(x1, 460, _haut_cap()), chasse, ancres_capitale(chasse)


# Chiffres ---------------------------------------------------------------------

def _ch() -> float:
    return PARAMETRES["hauteur_chiffres"]


def _haut_ch() -> float:
    return _haut_fut(_ch())


def _sommet_ch() -> float:
    return _ch() + PARAMETRES["depassement"] - PARAMETRES["delie"] / 2


def _cadre_chiffre(largeur: float = 400) -> tuple[float, float, float, float]:
    """(x1, x2, cx, chasse) d'un chiffre proportionnel."""
    p = PARAMETRES
    x1 = p["approche"] + demi_trait()
    x2 = x1 + largeur
    return x1, x2, (x1 + x2) / 2, x2 + demi_trait() + p["approche"]


def _anneau(cx: float, cy: float, rx: float, ry: float) -> Trait:
    return Trait(boucle_ovale(cx, cy, rx, ry, inclinaison=-6), effile_debut=PARAMETRES["levee_de_plume"], ferme=True)


def _zero() -> tuple[list[Trait], float, float, float]:
    x1, x2, cx, chasse = _cadre_chiffre(380)
    rx, ry = (x2 - x1) / 2, (_ch() + 2 * PARAMETRES["depassement"] - PARAMETRES["delie"]) / 2
    return [_anneau(cx, _ch() / 2, rx, ry)], chasse, rx, ry


@glyphe("zero", 0x30)
def dessiner_zero():
    """Boucle fermée et plus étroite que le O : 0 ne se confond pas avec O."""
    traits, chasse, _, _ = _zero()
    return traits, chasse, {}


@glyphe("zero.zero", None)
def dessiner_zero_barre():
    traits, chasse, rx, ry = _zero()
    cx, cy = chasse / 2, _ch() / 2
    barre_oblique = diagonale((cx - rx * 0.55, cy - ry * 0.62), (cx + rx * 0.55, cy + ry * 0.62), effile_debut=0.7, effile_fin=0.7)
    return traits + [barre_oblique], chasse, {}


@glyphe("one", 0x31)
def dessiner_one():
    """Drapeau long et pied : 1 ne se confond ni avec l ni avec I."""
    p = PARAMETRES
    x = p["approche"] + demi_trait() + 200
    traits = [diagonale((x - 210, _ch() * 0.62), (x, _haut_ch()), effile_debut=0.5),
              fut(x, _haut_ch(), demi_trait()),
              Trait([("moveTo", ((x - 130, demi_trait()),)), ("lineTo", ((x + 130, demi_trait() + 6),))], effile_debut=0.6, effile_fin=0.6)]
    return traits, x + 130 + demi_trait() + p["approche"], {}


@glyphe("two", 0x32)
def dessiner_two():
    x1, x2, cx, chasse = _cadre_chiffre()
    sommet = _sommet_ch()
    arc_et_descente = [
        ("moveTo", ((x1 + 15, 520),)),
        ("curveTo", ((x1 + 30, 650), (cx - 80, sommet), (cx, sommet))),
        ("curveTo", ((cx + 140, sommet), (x2, 620), (x2, 520))),
        ("curveTo", ((x2, 400), (x2 - 120, 280), (x1, demi_trait() + 10))),
    ]
    base = Trait([("moveTo", ((x1, demi_trait()),)), ("lineTo", ((x2 + 10, demi_trait() + 8),))], effile_fin=0.7)
    return [Trait(arc_et_descente, effile_debut=0.45, effile_fin=0.9), base], chasse, {}


@glyphe("three", 0x33)
def dessiner_three():
    x1, x2, cx, chasse = _cadre_chiffre()
    sommet, bas = _sommet_ch(), _bas_bol()
    # Deux gestes : au milieu, la plume repart vers la droite
    haut = [("moveTo", ((x1 + 10, 560),)),
            ("curveTo", ((x1 + 40, 660), (cx - 60, sommet), (cx + 10, sommet))),
            ("curveTo", ((cx + 130, sommet), (x2 - 10, 620), (x2 - 10, 540))),
            ("curveTo", ((x2 - 10, 450), (cx + 60, 390), (cx - 30, 385)))]
    bas_ = [("moveTo", ((cx - 10, 385),)),
            ("curveTo", ((cx + 120, 385), (x2 + 5, 310), (x2 + 5, 200))),
            ("curveTo", ((x2 + 5, 70), (cx + 70, bas), (cx - 10, bas))),
            ("curveTo", ((cx - 110, bas), (x1 - 5, 40), (x1 - 15, 120)))]
    return [Trait(haut, effile_debut=0.45, effile_fin=0.7), Trait(bas_, effile_debut=0.7, effile_fin=PARAMETRES["effile_minimum"])], chasse, {}


@glyphe("four", 0x34)
def dessiner_four():
    """4 ouvert en haut, comme à la main."""
    x1, x2, _, chasse = _cadre_chiffre(420)
    x_fut = x2 - 80
    traits = [diagonale((x_fut - 30, _haut_ch()), (x1, 230), effile_debut=0.6),
              Trait([("moveTo", ((x1, 230),)), ("lineTo", ((x2 + 10, 238),))], effile_fin=0.7),
              Trait(fut(x_fut, 500, demi_trait()).squelette, effile_debut=0.6, effile_fin=0.8)]
    return traits, chasse, {}


@glyphe("five", 0x35)
def dessiner_five():
    x1, x2, cx, chasse = _cadre_chiffre()
    bas = _bas_bol()
    traits = [Trait([("moveTo", ((x2, _haut_ch() + 6),)), ("lineTo", ((x1 + 30, _haut_ch()),))], effile_debut=0.6),
              diagonale((x1 + 30, _haut_ch()), (x1 + 10, 400)),
              Trait([("moveTo", ((x1 + 10, 400),)),
                     ("curveTo", ((cx - 40, 450), (x2, 420), (x2, 240))),
                     ("curveTo", ((x2, 70), (cx + 60, bas), (cx - 20, bas))),
                     ("curveTo", ((cx - 110, bas), (x1, 40), (x1 - 10, 110)))], effile_debut=0.7, effile_fin=PARAMETRES["effile_minimum"])]
    return traits, chasse, {}


def geste_six(x1: float, x2: float, cx: float) -> Squelette:
    """Le 6 d'un seul geste : depuis la pointe en haut à droite, descente par la gauche, boucle fermée en bas."""
    sommet, bas = _sommet_ch(), _bas_bol()
    return [("moveTo", ((x2 - 20, 640),)),
            ("curveTo", ((x2 - 60, sommet - 5), (cx + 40, sommet), (cx - 10, sommet))),
            ("curveTo", ((x1 + 30, sommet), (x1, 520), (x1, 300))),
            ("curveTo", ((x1, 90), (cx - 80, bas), (cx, bas))),
            ("curveTo", ((cx + 130, bas), (x2, 80), (x2, 210))),
            ("curveTo", ((x2, 340), (cx + 80, 400), (cx, 400))),
            ("curveTo", ((cx - 80, 400), (x1 + 20, 340), (x1 + 10, 260)))]


def inverser(squelette: Squelette) -> Squelette:
    """Même tracé parcouru dans l'autre sens."""
    points = [squelette[0][1][0]] + [commande[1][-1] for commande in squelette[1:]]
    inverse: Squelette = [("moveTo", (points[-1],))]
    for i in range(len(squelette) - 1, 0, -1):
        c1, c2, _ = squelette[i][1]
        inverse.append(("curveTo", (c2, c1, points[i - 1])))
    return inverse


@glyphe("six", 0x36)
def dessiner_six():
    x1, x2, cx, chasse = _cadre_chiffre()
    return [Trait(geste_six(x1, x2, cx), effile_debut=0.45, effile_fin=0.6)], chasse, {}


@glyphe("seven", 0x37)
def dessiner_seven():
    x1, x2, _, chasse = _cadre_chiffre()
    traits = [Trait([("moveTo", ((x1, _haut_ch()),)), ("lineTo", ((x2, _haut_ch() + 6),))], effile_debut=0.6),
              Trait([("moveTo", ((x2, _haut_ch() + 6),)),
                     ("curveTo", ((x2 - 80, 480), (x1 + 110, 200), (x1 + 90, demi_trait())))], effile_fin=0.8)]
    return traits, chasse, {}


@glyphe("eight", 0x38)
def dessiner_eight():
    _, _, cx, chasse = _cadre_chiffre()
    return [_anneau(cx, 530, 140, 150), _anneau(cx, 200, 185, 190)], chasse, {}


@glyphe("nine", 0x39)
def dessiner_nine():
    """Le 6 retourné, d'un seul geste : le bol se referme puis la plume descend dans la queue."""
    x1, x2, cx, chasse = _cadre_chiffre()
    centre = (cx, _ch() / 2)
    retourne = [(commande, tuple(_tourner(point, centre, 180) for point in points)) for commande, points in geste_six(x1, x2, cx)]
    return [Trait(inverser(retourne), effile_debut=0.6, effile_fin=PARAMETRES["effile_minimum"])], chasse, {}


# Ponctuation -----------------------------------------------------------------

def _x_ponctuation() -> float:
    return PARAMETRES["approche"] + demi_trait()


def _chasse_ponctuation(x_droite: float) -> float:
    return x_droite + demi_trait() + PARAMETRES["approche"]


def virgule(x: float, y: float) -> Trait:
    """Virgule : une goutte qui descend en s'effilant vers la gauche."""
    return Trait([("moveTo", ((x + 8, y),)), ("curveTo", ((x + 10, y - 60), (x - 8, y - 130), (x - 48, y - 200)))],
                 effile_fin=PARAMETRES["effile_minimum"])


def virgule_ouvrante(x: float, y: float) -> Trait:
    """Apostrophe ouvrante ‘ : la goutte en haut, la pointe qui monte à droite."""
    return Trait([("moveTo", ((x + 40, y + 160),)), ("curveTo", ((x + 8, y + 120), (x - 6, y + 60), (x - 4, y)))],
                 effile_debut=PARAMETRES["effile_minimum"])


@glyphe("period", 0x2E)
def dessiner_period():
    x = _x_ponctuation()
    return point(x, 0), _chasse_ponctuation(x), {}


@glyphe("comma", 0x2C)
def dessiner_comma():
    x = _x_ponctuation() + 40
    return [virgule(x, 60)], _chasse_ponctuation(x), {}


@glyphe("colon", 0x3A)
def dessiner_colon():
    x = _x_ponctuation()
    return point(x, 0) + point(x, 340), _chasse_ponctuation(x), {}


@glyphe("semicolon", 0x3B)
def dessiner_semicolon():
    x = _x_ponctuation() + 40
    return [virgule(x, 60)] + point(x + 8, 340), _chasse_ponctuation(x), {}


@glyphe("exclam", 0x21)
def dessiner_exclam():
    x = _x_ponctuation()
    trait = Trait(fut(x, _haut_cap(), 230).squelette, effile_fin=0.35)
    return [trait] + point(x, 0), _chasse_ponctuation(x), {}


@glyphe("question", 0x3F)
def dessiner_question():
    p = PARAMETRES
    x1 = _x_ponctuation()
    x2 = x1 + 300
    cx = (x1 + x2) / 2
    sommet = _cap() + p["depassement"] - p["delie"] / 2
    crochet = [("moveTo", ((x1, 560),)),
               ("curveTo", ((x1 + 10, 680), (cx - 50, sommet), (cx, sommet))),
               ("curveTo", ((cx + 120, sommet), (x2, 640), (x2, 540))),
               ("curveTo", ((x2, 440), (cx, 400), (cx, 300))),
               ("lineTo", ((cx, 230),))]
    return [Trait(crochet, effile_debut=0.45, effile_fin=0.4)] + point(cx, 0), _chasse_ponctuation(x2), {}


@glyphe("quoteright", 0x2019)
def dessiner_quoteright():
    x = _x_ponctuation() + 40
    return [virgule(x, 700)], _chasse_ponctuation(x), {}


@glyphe("quoteleft", 0x2018)
def dessiner_quoteleft():
    x = _x_ponctuation()
    return [virgule_ouvrante(x, 540)], _chasse_ponctuation(x + 40), {}


@glyphe("quotesingle", 0x27)
def dessiner_quotesingle():
    x = _x_ponctuation()
    return [Trait(fut(x, _haut_cap(), 540).squelette, effile_fin=0.5)], _chasse_ponctuation(x), {}


@glyphe("quotedbl", 0x22)
def dessiner_quotedbl():
    x = _x_ponctuation()
    traits = [Trait(fut(x + d, _haut_cap(), 540).squelette, effile_fin=0.5) for d in (0, 140)]
    return traits, _chasse_ponctuation(x + 140), {}


@glyphe("quotedblright", 0x201D)
def dessiner_quotedblright():
    x = _x_ponctuation() + 40
    return [virgule(x, 700), virgule(x + 130, 700)], _chasse_ponctuation(x + 130), {}


@glyphe("quotedblleft", 0x201C)
def dessiner_quotedblleft():
    x = _x_ponctuation()
    return [virgule_ouvrante(x, 540), virgule_ouvrante(x + 130, 540)], _chasse_ponctuation(x + 170), {}


def chevron(x_pointe: float, sens: int) -> list[Trait]:
    """Chevron arrondi et ouvert : sens = -1 pointe à gauche (« ‹), 1 pointe à droite (» ›)."""
    y, h, largeur = 270, 150, 160
    ouvert = x_pointe - sens * largeur
    pression = 0.75  # trait allégé : à cette taille, le chevron se boucherait
    return [Trait([("moveTo", ((ouvert, y + h),)), ("curveTo", ((ouvert - sens * 40, y + h * 0.6), (x_pointe - sens * 30, y + 20), (x_pointe, y)))],
                  effile_debut=0.5, pression=pression),
            Trait([("moveTo", ((x_pointe, y),)), ("curveTo", ((x_pointe - sens * 30, y - 20), (ouvert - sens * 40, y - h * 0.6), (ouvert, y - h)))],
                  effile_fin=0.5, pression=pression)]


@glyphe("guilsinglleft", 0x2039)
def dessiner_guilsinglleft():
    x = _x_ponctuation()
    return chevron(x, -1), _chasse_ponctuation(x + 160), {}


@glyphe("guilsinglright", 0x203A)
def dessiner_guilsinglright():
    x = _x_ponctuation() + 160
    return chevron(x, 1), _chasse_ponctuation(x), {}


@glyphe("guillemetleft", 0xAB)
def dessiner_guillemetleft():
    x = _x_ponctuation()
    return chevron(x, -1) + chevron(x + 190, -1), _chasse_ponctuation(x + 350), {}


@glyphe("guillemetright", 0xBB)
def dessiner_guillemetright():
    x = _x_ponctuation() + 160
    return chevron(x, 1) + chevron(x + 190, 1), _chasse_ponctuation(x + 190), {}


def tiret(longueur: float) -> tuple[list[Trait], float]:
    x = _x_ponctuation()
    trait = Trait([("moveTo", ((x, 270),)), ("lineTo", ((x + longueur, 280),))], effile_debut=0.6, effile_fin=0.6)
    return [trait], _chasse_ponctuation(x + longueur)


@glyphe("hyphen", 0x2D)
def dessiner_hyphen():
    traits, chasse = tiret(190)
    return traits, chasse, {}


@glyphe("endash", 0x2013)
def dessiner_endash():
    traits, _ = tiret(400)
    return traits, 500, {}


@glyphe("emdash", 0x2014)
def dessiner_emdash():
    traits, _ = tiret(900)
    return traits, 1000, {}


def _parenthese(sens: int) -> tuple[list[Trait], float]:
    """sens = 1 : ( ; sens = -1 : ) ; un arc qui va de l'ascendante sous la ligne de base."""
    x = _x_ponctuation()
    bord, creux = (x + 130, x) if sens == 1 else (x, x + 130)
    arc_ = [("moveTo", ((bord, 760),)), ("curveTo", ((creux - sens * 25, 600), (creux - sens * 25, 0), (bord, -170)))]
    return [Trait(arc_, effile_debut=0.6, effile_fin=0.6)], _chasse_ponctuation(x + 130)


@glyphe("parenleft", 0x28)
def dessiner_parenleft():
    traits, chasse = _parenthese(1)
    return traits, chasse, {}


@glyphe("parenright", 0x29)
def dessiner_parenright():
    traits, chasse = _parenthese(-1)
    return traits, chasse, {}


def _crochet(sens: int) -> tuple[list[Trait], float]:
    x = _x_ponctuation()
    x_fut, x_bout = (x, x + 120) if sens == 1 else (x + 120, x)
    traits = [Trait(fut(x_fut, 760, -170).squelette),
              Trait([("moveTo", ((x_fut, 760),)), ("lineTo", ((x_bout, 764),))], effile_fin=0.6),
              Trait([("moveTo", ((x_fut, -170),)), ("lineTo", ((x_bout, -166),))], effile_fin=0.6)]
    return traits, _chasse_ponctuation(x + 120)


@glyphe("bracketleft", 0x5B)
def dessiner_bracketleft():
    traits, chasse = _crochet(1)
    return traits, chasse, {}


@glyphe("bracketright", 0x5D)
def dessiner_bracketright():
    traits, chasse = _crochet(-1)
    return traits, chasse, {}


@glyphe("slash", 0x2F)
def dessiner_slash():
    x = _x_ponctuation()
    return [diagonale((x, -100), (x + 300, 740), effile_debut=0.7, effile_fin=0.7)], _chasse_ponctuation(x + 300), {}


@glyphe("ellipsis", 0x2026)
def dessiner_ellipsis():
    x = _x_ponctuation()
    ecart = max(200, PARAMETRES["coeur_ponctuation"] * 1.7)  # trois cœurs qui ne se touchent pas
    traits = point(x, 0) + point(x + ecart, 0) + point(x + 2 * ecart, 0)
    return traits, _chasse_ponctuation(x + 2 * ecart), {}


@glyphe("periodcentered", 0xB7)
def dessiner_periodcentered():
    x = _x_ponctuation()
    return point(x, 230), _chasse_ponctuation(x), {}


# Ornements --------------------------------------------------------------------

def _marge_ornement() -> float:
    """Marge de chaque côté d'un ornement : le cœur, penché, ne déborde jamais de la chasse."""
    return PARAMETRES["approche"] + PARAMETRES["coeur_final"] * 0.75


def _volute(largeur: float) -> list[Trait]:
    """Longue volute fine à deux ondulations, qui s'enroule en cœur à son extrémité."""
    p = PARAMETRES
    x0, y = _marge_ornement(), 230
    ligne = [("moveTo", ((x0, y),)),
             ("curveTo", ((x0 + largeur * 0.15, y + 70), (x0 + largeur * 0.3, y + 70), (x0 + largeur * 0.42, y))),
             ("curveTo", ((x0 + largeur * 0.55, y - 70), (x0 + largeur * 0.7, y - 70), (x0 + largeur * 0.82, y))),
             ("curveTo", ((x0 + largeur * 0.9, y + 40), (x0 + largeur * 0.96, y + 90), (x0 + largeur, y + 150)))]
    pointe = ligne[-1][1][-1]
    elan = math.atan2(pointe[1] - ligne[-1][1][1][1], pointe[0] - ligne[-1][1][1][0])
    return [Trait(ligne, effile_debut=p["effile_minimum"], effile_fin=0.6, pression=0.6),
            *coeur_trace(pointe, p["coeur_final"], p["penche_coeur"], elan=elan, pression=0.55)]


def _miroir(traits: list[Trait], axe: float) -> list[Trait]:
    return [Trait([(c, tuple((2 * axe - x, y) for x, y in pts)) for c, pts in trait.squelette],
                  trait.effile_debut, trait.effile_fin, trait.ferme, trait.pression) for trait in traits]


@glyphe("uni2767", 0x2767)
def dessiner_ornement_fin():
    """❧ : volute à cœur à placer après un titre."""
    largeur = 900
    chasse = 2 * _marge_ornement() + largeur
    return _volute(largeur), chasse, {}


@glyphe("uni2766", 0x2766)
def dessiner_ornement_debut():
    """❦ : la même volute en miroir, à placer avant un titre."""
    traits, chasse, _ = dessiner_ornement_fin()
    return _miroir(traits, chasse / 2), chasse, {}


@glyphe("uni2661", 0x2661)
def dessiner_coeur_blanc():
    """♡ : le cœur tracé de Tendrille, seul."""
    p = PARAMETRES
    largeur = 520
    pointe = (p["approche"] + largeur * 0.55, 0)
    return coeur_trace(pointe, largeur, inclinaison=0, effile_debut=0.6), largeur * 1.1 + 2 * p["approche"], {}


# Lettres non composables (Core) ----------------------------------------------------

def decaler(traits: list[Trait], dx: float, dy: float = 0) -> list[Trait]:
    return [Trait([(c, tuple((x + dx, y + dy) for x, y in pts)) for c, pts in trait.squelette],
                  trait.effile_debut, trait.effile_fin, trait.ferme, trait.pression) for trait in traits]


def barre_traversante(x: float, y: float, demi_longueur: float = 90, pente: float = 0.25) -> Trait:
    """Barre légèrement montante qui traverse un fût (ł, đ, ħ)."""
    return diagonale((x - demi_longueur, y - demi_longueur * pente), (x + demi_longueur, y + demi_longueur * pente),
                     effile_debut=0.6, effile_fin=0.6)


@glyphe("lslash", 0x142)
def dessiner_lslash():
    traits, chasse, ancres = dessiner_l()
    x = PARAMETRES["approche"] + demi_trait()
    return traits + [barre_traversante(x, 400)], chasse, ancres


@glyphe("Lslash", 0x141)
def dessiner_Lslash():
    traits, chasse, ancres = dessiner_L()
    x = PARAMETRES["approche_capitale"] + demi_trait()
    return traits + [barre_traversante(x + 20, 360, 110)], chasse, ancres


@glyphe("dcroat", 0x111)
def dessiner_dcroat():
    traits, chasse, ancres = dessiner_d()
    x = PARAMETRES["approche_ronde"] + demi_trait() + 2 * RAYON_BOL
    return traits + [barre_traversante(x, 630, 100, 0.08)], chasse, ancres


@glyphe("Dcroat", 0x110)
def dessiner_Dcroat():
    traits, chasse, ancres = dessiner_D()
    x = PARAMETRES["approche_capitale"] + demi_trait()
    return traits + [barre_traversante(x + 20, 360, 120, 0.08)], chasse, ancres


@glyphe("Eth", 0xD0)
def dessiner_Eth():
    return dessiner_Dcroat()


@glyphe("hbar", 0x127)
def dessiner_hbar():
    traits, chasse, ancres = dessiner_h()
    x = PARAMETRES["approche"] + demi_trait()
    return traits + [barre_traversante(x, 630, 100, 0.08)], chasse, ancres


@glyphe("Hbar", 0x126)
def dessiner_Hbar():
    traits, chasse, ancres = dessiner_H()
    p = PARAMETRES
    x_gauche = p["approche"] + demi_trait() + p["amorce"] * 0.6
    x_droite = x_gauche + p["fut"] + 420
    barre_haute = Trait([("moveTo", ((x_gauche - 80, 560),)), ("lineTo", ((x_droite + 80, 568),))], effile_debut=0.6, effile_fin=0.6)
    return traits + [barre_haute], chasse, ancres


@glyphe("oslash", 0xF8)
def dessiner_oslash():
    traits, chasse, ancres = dessiner_o()
    cx, cy = chasse / 2, PARAMETRES["hauteur_x"] / 2
    return traits + [diagonale((cx - 220, cy - 300), (cx + 220, cy + 300), effile_debut=0.7, effile_fin=0.7)], chasse, ancres


@glyphe("Oslash", 0xD8)
def dessiner_Oslash():
    traits, chasse, ancres = dessiner_O()
    cx, cy = chasse / 2, PARAMETRES["hauteur_capitale"] / 2
    return traits + [diagonale((cx - 300, cy - 400), (cx + 300, cy + 400), effile_debut=0.7, effile_fin=0.7)], chasse, ancres


@glyphe("oe", 0x153)
def dessiner_oe():
    """œ : le o et le e se touchent et partagent leur flanc, comme dans « cœur »."""
    o_traits, o_chasse, _ = dessiner_o()
    e_traits, e_chasse, _ = dessiner_e()
    # Les flancs bombés en sens contraire ne se touchent qu'en un point : on les fait se recouvrir
    # sur une bonne hauteur pour qu'ils forment un flanc commun, sans blanc en amande
    recouvrement = 2 * demi_trait() + PARAMETRES["approche_ronde"] * 2 + 70
    traits = o_traits + decaler(e_traits, o_chasse - recouvrement)
    chasse = o_chasse - recouvrement + e_chasse
    return traits, chasse, ancres_minuscule(chasse)


@glyphe("ae", 0xE6)
def dessiner_ae():
    """æ : le fût du a devient le flanc gauche du e."""
    p = PARAMETRES
    x_gauche = p["approche_ronde"] + demi_trait()
    x = x_gauche + 330
    sommet, bas = _haut_arche(), _bas_bol()
    crochet = [("moveTo", ((x_gauche + 30, 400),)),
               ("curveTo", ((x_gauche + 55, sommet - 10), (x - 190, sommet), (x - 110, sommet))),
               ("curveTo", ((x - 45, sommet), (x, sommet - 55), (x, sommet - 175))),
               ("lineTo", ((x, 140),))]
    petit_bol = [("moveTo", ((x, 300),)),
                 ("curveTo", ((x - 110, 318), (x_gauche, 285), (x_gauche, 160))),
                 ("curveTo", ((x_gauche, 55), (x_gauche + 70, bas), (x_gauche + 160, bas))),
                 ("curveTo", ((x_gauche + 240, bas), (x - 15, 45), (x, 95)))]
    e_traits, e_chasse, _ = dessiner_e()
    dx = x - (p["approche_ronde"] + 230 - (230 - demi_trait())) - 15
    traits = [Trait(crochet, effile_debut=0.4), Trait(petit_bol, effile_debut=0.4, effile_fin=0.8)] + decaler(e_traits, dx)
    chasse = dx + e_chasse
    return traits, chasse, ancres_minuscule(chasse)


@glyphe("OE", 0x152)
def dessiner_OE():
    """Œ : un demi-O ouvert à droite, fermé par le fût du E."""
    p = PARAMETRES
    rx, ry = 300 - demi_trait(), (_cap() + 2 * p["depassement"] - p["delie"]) / 2
    cx, cy = p["approche_capitale_ronde"] + 300, _cap() / 2
    x_fut = cx + rx * 0.25
    demi_o = Trait(arc(cx, cy, rx, ry, 75, 285), effile_debut=0.7, effile_fin=0.7)
    traits = [demi_o, fut_capitale(x_fut)] + _barres_E(x_fut, avec_bas=True)
    chasse = x_fut + 340 + p["sortie"] * 0.6 + demi_trait() + p["approche_capitale"] * 0.6
    return traits, chasse, ancres_capitale(chasse)


@glyphe("AE", 0xC6)
def dessiner_AE():
    """Æ : la jambe gauche du A rejoint le fût du E."""
    p = PARAMETRES
    x1 = p["approche_capitale"] + demi_trait()
    x_fut = x1 + 360
    traits = [diagonale((x1, demi_trait()), (x_fut, _haut_cap()), effile_debut=0.8),
              fut_capitale(x_fut), barre_capitale(x1 + 110, x_fut, 250)] + _barres_E(x_fut, avec_bas=True)
    chasse = x_fut + 340 + p["sortie"] * 0.6 + demi_trait() + p["approche_capitale"] * 0.6
    return traits, chasse, ancres_capitale(chasse)


@glyphe("eth", 0xF0)
def dessiner_eth():
    p = PARAMETRES
    rx = 200 - demi_trait()
    cx, cy = p["approche_ronde"] + 200, 240
    bol = Trait(boucle_ovale(cx, cy, rx, 220, inclinaison=-8), effile_debut=p["levee_de_plume"], ferme=True)
    hampe = [("moveTo", ((cx + rx * 0.85, 330),)),
             ("curveTo", ((cx + rx * 0.9, 520), (cx + 40, p["ascendante"] - 100), (cx - 70, p["ascendante"] - 30)))]
    traits = [bol, Trait(hampe, effile_fin=p["effile_minimum"]), barre_traversante(cx + 20, 620, 90, 0.4)]
    chasse = cx + 200 + p["approche_ronde"]
    return traits, chasse, ancres_minuscule(chasse, p["ascendante"])


@glyphe("thorn", 0xFE)
def dessiner_thorn():
    p = PARAMETRES
    x = p["approche"] + demi_trait()
    haut = _haut_fut(p["ascendante"])
    traits = [Trait(fut(x, haut, p["descendante"] + demi_trait()).squelette, effile_fin=0.8), bol(x, "droite")] + entree(x, haut)
    chasse = x + 2 * RAYON_BOL + demi_trait() + p["approche_ronde"]
    return traits, chasse, ancres_minuscule(chasse, p["ascendante"])


@glyphe("Thorn", 0xDE)
def dessiner_Thorn():
    p = PARAMETRES
    x = p["approche_capitale"] + demi_trait()
    traits = [fut_capitale(x), panse(x, 560, 170, 330)] + entree(x, _haut_cap())
    chasse = x + 330 + demi_trait() + p["approche_capitale_ronde"]
    return traits, chasse, ancres_capitale(chasse)


@glyphe("germandbls", 0xDF)
def dessiner_germandbls():
    """ß : le fût monte, s'arrondit en haut, puis deux bosses comme un 3."""
    p = PARAMETRES
    x = p["approche"] + demi_trait()
    sommet = p["ascendante"] - p["delie"] / 2
    bas = _bas_bol()
    haut = [("moveTo", ((x, demi_trait()),)), ("lineTo", ((x, 560),)),
            ("curveTo", ((x, sommet - 60), (x + 70, sommet), (x + 150, sommet))),
            ("curveTo", ((x + 240, sommet), (x + 280, sommet - 80), (x + 270, 600))),
            ("curveTo", ((x + 260, 500), (x + 190, 450), (x + 110, 440)))]
    bas_ = [("moveTo", ((x + 130, 440),)),
            ("curveTo", ((x + 260, 430), (x + 320, 330), (x + 320, 220))),
            ("curveTo", ((x + 320, 80), (x + 230, bas), (x + 150, bas))),
            ("curveTo", ((x + 110, bas), (x + 80, 25), (x + 70, 60)))]
    traits = [Trait(haut, effile_fin=0.7), Trait(bas_, effile_debut=0.7, effile_fin=p["effile_minimum"])]
    chasse = x + 320 + demi_trait() + p["approche_ronde"]
    return traits, chasse, ancres_minuscule(chasse, p["ascendante"])


@glyphe("uni1E9E", 0x1E9E)
def dessiner_germandbls_capitale():
    """ẞ : fût, barre haute, diagonale vers le milieu, puis une panse arrondie."""
    p = PARAMETRES
    x = p["approche_capitale"] + demi_trait()
    haut = _haut_cap()
    bas = _bas_bol()
    traits = [fut_capitale(x),
              Trait([("moveTo", ((x, haut + 4),)), ("lineTo", ((x + 330, haut + 10),))], effile_fin=0.8),
              diagonale((x + 330, haut + 10), (x + 150, 420), effile_fin=0.8),
              Trait([("moveTo", ((x + 150, 420),)),
                     ("curveTo", ((x + 330, 410), (x + 400, 300), (x + 400, 210))),
                     ("curveTo", ((x + 400, 70), (x + 300, bas), (x + 190, bas))),
                     ("curveTo", ((x + 140, bas), (x + 100, 25), (x + 90, 60)))], effile_debut=0.8, effile_fin=p["effile_minimum"])]
    traits += entree(x, haut)
    chasse = x + 400 + demi_trait() + p["approche_capitale_ronde"]
    return traits, chasse, ancres_capitale(chasse)


# Diacritiques ------------------------------------------------------------------
# Glyphes de chasse nulle, accrochés par leurs ancres « _top », « _bottom »… ; la version « .case »,
# plus plate et plus basse, sert aux capitales et aux minuscules à ascendante (ĺ, ď).

ECART_ACCENT = 70  # blanc entre le haut de la lettre et le bas de l'accent


DESSINS_ACCENTS: dict[str, Callable] = {}


def _accent(nom: str, point_code: int, dessin):
    """Enregistre un diacritique haut et sa version capitale ; dessin(y0, k) → traits (k : facteur de hauteur)."""
    DESSINS_ACCENTS[nom] = dessin
    def minuscule():
        y = PARAMETRES["hauteur_x"]
        return dessin(y + ECART_ACCENT, 1.0), 0, {"_top": (0, y)}

    def capitale():
        y = PARAMETRES["hauteur_capitale"]
        return dessin(y + ECART_ACCENT * 0.6, 0.75), 0, {"_top": (0, y)}

    glyphe(nom, point_code)(minuscule)
    glyphe(f"{nom}.case", None)(capitale)


_accent("acutecomb", 0x301, lambda y, k: [diagonale((55, y + 160 * k), (-35, y), effile_fin=0.5)])
_accent("gravecomb", 0x300, lambda y, k: [diagonale((-55, y + 160 * k), (35, y), effile_fin=0.5)])
_accent("circumflexcomb", 0x302, lambda y, k: [diagonale((-110, y), (0, y + 150 * k), effile_debut=0.6),
                                                diagonale((0, y + 150 * k), (110, y), effile_fin=0.6)])
_accent("caroncomb", 0x30C, lambda y, k: [diagonale((-110, y + 150 * k), (0, y), effile_debut=0.6),
                                           diagonale((0, y), (110, y + 150 * k), effile_fin=0.6)])
_accent("tildecomb", 0x303, lambda y, k: [Trait([("moveTo", ((-130, y + 30 * k),)),
                                                  ("curveTo", ((-80, y + 130 * k), (-30, y + 120 * k), (0, y + 70 * k))),
                                                  ("curveTo", ((30, y + 20 * k), (80, y + 10 * k), (130, y + 110 * k)))],
                                                 effile_debut=0.6, effile_fin=0.6)])
_accent("macroncomb", 0x304, lambda y, k: [Trait([("moveTo", ((-120, y + 40 * k),)), ("lineTo", ((120, y + 50 * k),))],
                                                  effile_debut=0.6, effile_fin=0.6)])
_accent("brevecomb", 0x306, lambda y, k: [Trait([("moveTo", ((-110, y + 140 * k),)),
                                                  ("curveTo", ((-95, y + 20 * k), (95, y + 20 * k), (110, y + 140 * k)))],
                                                 effile_debut=0.6, effile_fin=0.6)])
_accent("hungarumlautcomb", 0x30B, lambda y, k: [diagonale((-10, y + 160 * k), (-80, y), effile_fin=0.5),
                                                  diagonale((110, y + 160 * k), (40, y), effile_fin=0.5)])
_accent("ringcomb", 0x30A, lambda y, k: [Trait(boucle_ovale(0, y + 75 * k, 58, 62 * k), ferme=True, pression=0.75)])
# Points : des cœurs dans Tendrille, des ronds dans Tendrille Texte
_accent("dotaccentcomb", 0x307, lambda y, k: point(0, y - 10))
_accent("dieresiscomb", 0x308, lambda y, k: point(-85, y - 10) + point(85, y - 10))


@glyphe("cedillacomb", 0x327)
def dessiner_cedille():
    crochet = [("moveTo", ((0, 20),)), ("lineTo", ((8, -60),)),
               ("curveTo", ((70, -70), (85, -140), (40, -170))),
               ("curveTo", ((10, -190), (-30, -185), (-60, -170)))]
    return [Trait(crochet, effile_fin=PARAMETRES["effile_minimum"], pression=0.85)], 0, {"_bottom": (0, 0)}


@glyphe("commaaccentcomb", 0x326)
def dessiner_virgule_souscrite():
    trait = [("moveTo", ((8, -55),)), ("curveTo", ((10, -100), (-5, -160), (-35, -215)))]
    return [Trait(trait, effile_fin=PARAMETRES["effile_minimum"])], 0, {"_bottom": (0, 0)}


@glyphe("ogonekcomb", 0x328)
def dessiner_ogonek():
    crochet = [("moveTo", ((0, 30),)),
               ("curveTo", ((-70, -30), (-80, -150), (10, -190))),
               ("curveTo", ((40, -200), (60, -195), (80, -180)))]
    return [Trait(crochet, effile_fin=PARAMETRES["effile_minimum"], pression=0.85)], 0, {"_ogonek": (0, 0)}


@glyphe("caroncomb.alt", None)
def dessiner_caron_apostrophe():
    """Caron en apostrophe de ď ť ľ Ľ, posé à droite de la hampe."""
    trait = [("moveTo", ((10, 0),)), ("curveTo", ((12, -45), (0, -95), (-25, -140)))]
    return [Trait(trait, effile_fin=PARAMETRES["effile_minimum"])], 0, {"_caronalt": (0, 0)}


# Accents isolés, symboles, maths --------------------------------------------------

AXE_MATH = 320  # milieu des chiffres : « 2 + 3 = 5 » s'aligne


def _accent_isole(nom_combinant: str, largeur: float = 340):
    """Accent isolé : le même dessin que le diacritique, centré dans une chasse."""
    def dessiner():
        x = largeur / 2
        traits = DESSINS_ACCENTS[nom_combinant](PARAMETRES["hauteur_x"] + ECART_ACCENT, 1.0)
        return decaler(traits, x), largeur, {}
    return dessiner


for _nom, _code, _combinant in (("acute", 0xB4, "acutecomb"), ("grave", 0x60, "gravecomb"), ("dieresis", 0xA8, "dieresiscomb"),
                                ("macron", 0xAF, "macroncomb"), ("circumflex", 0x2C6, "circumflexcomb"),
                                ("caron", 0x2C7, "caroncomb"), ("breve", 0x2D8, "brevecomb"), ("dotaccent", 0x2D9, "dotaccentcomb"),
                                ("ring", 0x2DA, "ringcomb"), ("tilde", 0x2DC, "tildecomb"), ("hungarumlaut", 0x2DD, "hungarumlautcomb")):
    glyphe(_nom, _code)(_accent_isole(_combinant))


@glyphe("cedilla", 0xB8)
def dessiner_cedilla_isolee():
    traits, _, _ = dessiner_cedille()
    return decaler(traits, 170), 340, {}


@glyphe("ogonek", 0x2DB)
def dessiner_ogonek_isole():
    traits, _, _ = dessiner_ogonek()
    return decaler(traits, 170), 340, {}


def _cadre_symbole(largeur: float) -> tuple[float, float, float]:
    x1 = PARAMETRES["approche"] + demi_trait()
    return x1, x1 + largeur, x1 + largeur + demi_trait() + PARAMETRES["approche"]


LARGEUR_MATH = 440  # tous les signes mathématiques partagent une chasse : un calcul s'aligne


def _cadre_math(largeur: float) -> tuple[float, float, float]:
    """Signe de « largeur » centré dans la chasse commune des signes mathématiques."""
    x1, x2, chasse = _cadre_symbole(LARGEUR_MATH)
    marge = (LARGEUR_MATH - largeur) / 2
    return x1 + marge, x2 - marge, chasse


def horizontale(x1: float, x2: float, y: float) -> Trait:
    return Trait([("moveTo", ((x1, y),)), ("lineTo", ((x2, y + 4),))], effile_debut=0.7, effile_fin=0.7)


@glyphe("asciicircum", 0x5E)
def dessiner_asciicircum():
    x1, x2, chasse = _cadre_symbole(380)
    cx = (x1 + x2) / 2
    return [diagonale((x1, 380), (cx, 700), effile_debut=0.6), diagonale((cx, 700), (x2, 380), effile_fin=0.6)], chasse, {}


@glyphe("asciitilde", 0x7E)
def dessiner_asciitilde():
    x1, x2, chasse = _cadre_math(440)
    l = x2 - x1
    vague = [("moveTo", ((x1, AXE_MATH - 30),)),
             ("curveTo", ((x1 + l * 0.15, AXE_MATH + 70), (x1 + l * 0.35, AXE_MATH + 70), (x1 + l * 0.5, AXE_MATH))),
             ("curveTo", ((x1 + l * 0.65, AXE_MATH - 70), (x1 + l * 0.85, AXE_MATH - 70), (x2, AXE_MATH + 30)))]
    return [Trait(vague, effile_debut=0.6, effile_fin=0.6)], chasse, {}


@glyphe("plus", 0x2B)
def dessiner_plus():
    x1, x2, chasse = _cadre_math(440)
    cx = (x1 + x2) / 2
    return [horizontale(x1, x2, AXE_MATH), Trait(fut(cx, AXE_MATH + 220, AXE_MATH - 220).squelette, effile_debut=0.7, effile_fin=0.7)], chasse, {}


@glyphe("uni2212", 0x2212)
def dessiner_minus():
    x1, x2, chasse = _cadre_math(440)
    return [horizontale(x1, x2, AXE_MATH)], chasse, {}


@glyphe("equal", 0x3D)
def dessiner_equal():
    x1, x2, chasse = _cadre_math(440)
    return [horizontale(x1, x2, AXE_MATH + 90), horizontale(x1, x2, AXE_MATH - 90)], chasse, {}


@glyphe("multiply", 0xD7)
def dessiner_multiply():
    x1, x2, chasse = _cadre_math(340)
    return [diagonale((x1, AXE_MATH - 170), (x2, AXE_MATH + 170), effile_debut=0.7, effile_fin=0.7),
            diagonale((x1, AXE_MATH + 170), (x2, AXE_MATH - 170), effile_debut=0.7, effile_fin=0.7)], chasse, {}


@glyphe("divide", 0xF7)
def dessiner_divide():
    x1, x2, chasse = _cadre_math(440)
    cx = (x1 + x2) / 2
    return [horizontale(x1, x2, AXE_MATH)] + point(cx, AXE_MATH + 90) + point(cx, AXE_MATH - 230), chasse, {}


@glyphe("less", 0x3C)
def dessiner_less():
    x1, x2, chasse = _cadre_math(400)
    return [diagonale((x2, AXE_MATH + 200), (x1, AXE_MATH), effile_debut=0.6),
            diagonale((x1, AXE_MATH), (x2, AXE_MATH - 200), effile_fin=0.6)], chasse, {}


@glyphe("greater", 0x3E)
def dessiner_greater():
    x1, x2, chasse = _cadre_math(400)
    return [diagonale((x1, AXE_MATH + 200), (x2, AXE_MATH), effile_debut=0.6),
            diagonale((x2, AXE_MATH), (x1, AXE_MATH - 200), effile_fin=0.6)], chasse, {}


@glyphe("numbersign", 0x23)
def dessiner_numbersign():
    x1, x2, chasse = _cadre_symbole(480)
    return [diagonale((x1 + 160, 690), (x1 + 100, 10), effile_fin=0.8), diagonale((x1 + 380, 690), (x1 + 320, 10), effile_fin=0.8),
            horizontale(x1, x2, 470), horizontale(x1 - 20, x2 - 20, 230)], chasse, {}


@glyphe("backslash", 0x5C)
def dessiner_backslash():
    x1, x2, chasse = _cadre_symbole(300)
    return [diagonale((x1, 740), (x2, -100), effile_debut=0.7, effile_fin=0.7)], chasse, {}


@glyphe("underscore", 0x5F)
def dessiner_underscore():
    x1, x2, chasse = _cadre_symbole(460)
    return [horizontale(x1, x2, -150)], chasse, {}


@glyphe("bar", 0x7C)
def dessiner_bar():
    x1, _, chasse = _cadre_symbole(0)
    return [Trait(fut(x1, 760, -170).squelette, effile_debut=0.8, effile_fin=0.8)], chasse, {}


def _accolade(sens: int) -> tuple[list[Trait], float]:
    """sens = 1 : { ; sens = -1 : } ; deux arcs qui se rejoignent en pointe au milieu."""
    x1, x2, chasse = _cadre_symbole(200)
    bord, pointe = (x2, x1) if sens == 1 else (x1, x2)
    milieu, mi = (x1 + x2) / 2, 295
    haut = [("moveTo", ((bord, 760),)), ("curveTo", ((milieu - sens * 10, 760), (milieu, 700), (milieu, 600))),
            ("curveTo", ((milieu, 380), (milieu - sens * 20, mi + 20), (pointe, mi)))]
    bas = [("moveTo", ((pointe, mi),)), ("curveTo", ((milieu - sens * 20, mi - 20), (milieu, 210), (milieu, -10))),
           ("curveTo", ((milieu, -110), (milieu - sens * 10, -170), (bord, -170)))]
    return [Trait(haut, effile_debut=0.6, effile_fin=0.6), Trait(bas, effile_debut=0.6, effile_fin=0.6)], chasse


@glyphe("braceleft", 0x7B)
def dessiner_braceleft():
    traits, chasse = _accolade(1)
    return traits, chasse, {}


@glyphe("braceright", 0x7D)
def dessiner_braceright():
    traits, chasse = _accolade(-1)
    return traits, chasse, {}


@glyphe("asterisk", 0x2A)
def dessiner_asterisk():
    x1, x2, chasse = _cadre_symbole(320)
    cx, cy = (x1 + x2) / 2, 560
    branches = [diagonale((cx, cy), (cx + 150 * math.cos(math.radians(a)), cy + 150 * math.sin(math.radians(a))), effile_fin=0.4)
                for a in (90, 162, 234, 306, 18)]
    return branches, chasse, {}


@glyphe("bullet", 0x2022)
def dessiner_bullet():
    """Puce : un cœur dans Tendrille, un rond plein dans Tendrille Texte (ss02 inverse)."""
    x1, _, chasse = _cadre_symbole(220)
    cx = x1 + 110
    if not points_en_coeur():
        return [Trait([("moveTo", ((cx - 30, AXE_MATH - 20),)), ("lineTo", ((cx + 30, AXE_MATH + 20),))], pression=1.6)], chasse, {}
    return coeur_trace((cx, AXE_MATH - 110), 220, inclinaison=-8, effile_debut=0.45, pression=0.6), chasse, {}


@glyphe("degree", 0xB0)
def dessiner_degree():
    x1, _, chasse = _cadre_symbole(180)
    return [Trait(boucle_ovale(x1 + 90, 600, 80, 85), ferme=True, pression=0.7)], chasse, {}


@glyphe("percent", 0x25)
def dessiner_percent():
    x1, x2, chasse = _cadre_symbole(560)
    return [Trait(boucle_ovale(x1 + 90, 560, 85, 130), ferme=True, pression=0.8),
            Trait(boucle_ovale(x2 - 90, 160, 85, 130), ferme=True, pression=0.8),
            diagonale((x1 + 20, 10), (x2 - 20, 690), effile_debut=0.7, effile_fin=0.7)], chasse, {}


@glyphe("dollar", 0x24)
def dessiner_dollar():
    x1, x2, chasse = _cadre_symbole(360)
    cx = (x1 + x2) / 2
    return forme_s(x1, 360, 700) + [Trait(fut(cx, 790, -90).squelette, effile_debut=0.6, effile_fin=0.6, pression=0.8)], chasse, {}


@glyphe("cent", 0xA2)
def dessiner_cent():
    traits, chasse, _ = dessiner_c()
    cx = chasse / 2 + 10
    return traits + [Trait(fut(cx, 640, -100).squelette, effile_debut=0.6, effile_fin=0.6, pression=0.8)], chasse, {}


@glyphe("Euro", 0x20AC)
def dessiner_euro():
    traits, chasse, _ = dessiner_C()
    x = PARAMETRES["approche_capitale_ronde"] - 20
    return traits + [horizontale(x, x + 360, 420), horizontale(x, x + 330, 290)], chasse, {}


@glyphe("yen", 0xA5)
def dessiner_yen():
    traits, chasse, _ = dessiner_Y()
    x1 = PARAMETRES["approche_capitale"] + demi_trait()
    return traits + [horizontale(x1 + 110, x1 + 410, 260), horizontale(x1 + 110, x1 + 410, 130)], chasse, {}


@glyphe("sterling", 0xA3)
def dessiner_sterling():
    """£ : une boucle en crosse qui descend, une barre, une base qui file à droite."""
    x1, x2, chasse = _cadre_symbole(440)
    crosse = [("moveTo", ((x2 - 20, 600),)),
              ("curveTo", ((x2 - 40, 690), (x1 + 260, 720), (x1 + 180, 690))),
              ("curveTo", ((x1 + 90, 650), (x1 + 100, 500), (x1 + 120, 380))),
              ("curveTo", ((x1 + 140, 250), (x1 + 100, 100), (x1, demi_trait())))]
    return [Trait(crosse, effile_debut=0.5), horizontale(x1 + 20, x1 + 300, 360), horizontale(x1, x2, demi_trait())], chasse, {}


@glyphe("ampersand", 0x26)
def dessiner_ampersand():
    """& d'un seul geste : diagonale, boucle du haut, panse du bas, queue à droite."""
    x1, x2, chasse = _cadre_symbole(520)
    cx = x1 + 210
    bas = _bas_bol()
    geste = [("moveTo", ((x2, demi_trait()),)),
             ("curveTo", ((x2 - 120, 140), (x1 + 120, 380), (x1 + 120, 520))),
             ("curveTo", ((x1 + 120, 640), (cx - 30, 700), (cx + 10, 700))),
             ("curveTo", ((cx + 90, 700), (cx + 120, 640), (cx + 110, 590))),
             ("curveTo", ((cx + 90, 500), (x1, 400), (x1, 210))),
             ("curveTo", ((x1, 80), (cx - 70, bas), (cx + 10, bas))),
             ("curveTo", ((cx + 170, bas), (x2 - 60, 180), (x2 + 10, 360)))]
    return [Trait(geste, effile_debut=0.6, effile_fin=PARAMETRES["effile_minimum"])], chasse, {}


@glyphe("at", 0x40)
def dessiner_at():
    x1, x2, chasse = _cadre_symbole(720)
    cx = (x1 + x2) / 2
    interieur = Trait(boucle_ovale(cx - 30, 300, 120, 150), ferme=True, pression=0.85)
    fut_et_tour = [("moveTo", ((cx + 90, 450),)), ("lineTo", ((cx + 90, 210),)),
                   ("curveTo", ((cx + 90, 150), (cx + 150, 130), (cx + 200, 150)))] + arc(cx, 320, 360, 380, -20, 300)[1:]
    return [interieur, Trait(fut_et_tour, effile_fin=PARAMETRES["effile_minimum"], pression=0.85)], chasse, {}


@glyphe("section", 0xA7)
def dessiner_section():
    x1, _, chasse = _cadre_symbole(320)
    return decaler(forme_s(x1, 320, 440), 0, 280) + decaler(forme_s(x1, 320, 440), 0, -60), chasse, {}


@glyphe("paragraph", 0xB6)
def dessiner_paragraph():
    x1, x2, chasse = _cadre_symbole(420)
    panse = Trait(boucle_ovale(x1 + 150, 520, 150, 170), ferme=True, pression=0.9)
    return [panse, Trait(fut(x1 + 290, 690, -150).squelette, effile_fin=0.8), Trait(fut(x2, 690, -150).squelette, effile_fin=0.8),
            horizontale(x1 + 150, x2, 690)], chasse, {}


def _reduire(traits: list[Trait], facteur: float, dx: float, dy: float, pression: float = 0.75) -> list[Trait]:
    """Petites lettres (ª º ™) : le squelette rapetisse, le trait s'allège un peu pour garder le poids."""
    return [Trait([(c, tuple((x * facteur + dx, y * facteur + dy) for x, y in pts)) for c, pts in trait.squelette],
                  trait.effile_debut, trait.effile_fin, trait.ferme, pression) for trait in traits]


def _ordinal(dessiner_lettre) -> tuple[list[Trait], float]:
    traits, chasse_lettre, _ = dessiner_lettre()
    facteur = 0.6
    x1, _, chasse = _cadre_symbole(chasse_lettre * facteur - 2 * PARAMETRES["approche"])
    return _reduire(traits, facteur, x1 - PARAMETRES["approche"], 380) + [horizontale(x1, chasse - x1, 300)], chasse


@glyphe("ordfeminine", 0xAA)
def dessiner_ordfeminine():
    traits, chasse = _ordinal(dessiner_a)
    return traits, chasse, {}


@glyphe("ordmasculine", 0xBA)
def dessiner_ordmasculine():
    traits, chasse = _ordinal(dessiner_o)
    return traits, chasse, {}


def _cercle_marque(dessiner_lettre) -> tuple[list[Trait], float]:
    """© ® : un cercle fin autour d'une petite capitale."""
    x1, x2, chasse = _cadre_symbole(720)
    cx = (x1 + x2) / 2
    cercle = Trait(boucle_ovale(cx, 340, 360, 360), ferme=True, pression=0.7)
    lettre, chasse_lettre, _ = dessiner_lettre()
    facteur = 0.55
    return [cercle] + _reduire(lettre, facteur, cx - chasse_lettre * facteur / 2, 140), chasse


@glyphe("copyright", 0xA9)
def dessiner_copyright():
    traits, chasse = _cercle_marque(dessiner_C)
    return traits, chasse, {}


@glyphe("registered", 0xAE)
def dessiner_registered():
    traits, chasse = _cercle_marque(dessiner_R)
    return traits, chasse, {}


@glyphe("trademark", 0x2122)
def dessiner_trademark():
    t_traits, t_chasse, _ = dessiner_T()
    m_traits, m_chasse, _ = dessiner_M()
    facteur = 0.42
    x0 = PARAMETRES["approche"]
    traits = _reduire(t_traits, facteur, x0, 420) + _reduire(m_traits, facteur, x0 + t_chasse * facteur, 420)
    return traits, x0 + (t_chasse + m_chasse) * facteur + PARAMETRES["approche"], {}


@glyphe("exclamdown", 0xA1)
def dessiner_exclamdown():
    """¡ : le cœur reste pointe en bas, le trait s'épaissit en descendant."""
    x = _x_ponctuation()
    trait = Trait(fut(x, 280, PARAMETRES["descendante"] + demi_trait()).squelette, effile_debut=0.35)
    return [trait] + point(x, 360), _chasse_ponctuation(x), {}


@glyphe("questiondown", 0xBF)
def dessiner_questiondown():
    traits, chasse, _ = dessiner_question()
    crochet = traits[:1]  # le premier trait du ? est son crochet ; le point est redessiné à l'endroit
    centre = (chasse / 2, 230)
    retourne = [Trait([(c, tuple(_tourner(pt, centre, 180) for pt in pts)) for c, pts in trait.squelette],
                      trait.effile_debut, trait.effile_fin, trait.ferme, trait.pression) for trait in crochet]
    retourne = decaler(retourne, 0, -60)
    return retourne + point(chasse / 2, 360), chasse, {}


@glyphe("quotesinglbase", 0x201A)
def dessiner_quotesinglbase():
    return dessiner_comma()


@glyphe("quotedblbase", 0x201E)
def dessiner_quotedblbase():
    x = _x_ponctuation() + 40
    return [virgule(x, 60), virgule(x + 130, 60)], _chasse_ponctuation(x + 130), {}


# Écriture dans l'UFO ----------------------------------------------------------

def ecrire(chemin_ufo: str) -> None:
    police = ufoLib2.Font.open(chemin_ufo)
    p = PARAMETRES
    police.info.xHeight, police.info.capHeight = p["hauteur_x"], p["hauteur_capitale"]
    police.info.ascender, police.info.descender = p["ascendante"], p["descendante"]
    police.info.versionMajor, police.info.versionMinor = version_opentype()
    for nom in [g.name for g in police if "." in g.name and g.name != ".notdef"]:  # variantes : toujours redessinées
        del police[nom]
    for nom, (point_code, dessiner) in DESSINS.items():
        ecrire_glyphe(police, nom, point_code, dessiner, graine=nom)
    if p["sortie_finale"]:
        normal = {cle: p[cle] for cle in ("sortie", "envol", "fin_de_mot")}
        p.update(sortie=p["sortie_finale"], envol=p["envol_final"], fin_de_mot=True)
        for nom in LETTRES_FINALES:  # même graine que la lettre : seul le ruban change
            ecrire_glyphe(police, f"{nom}.fina", None, DESSINS[nom][1], graine=nom, coeur=p["coeur_final"])
        p.update(normal)
    for fin in (False, True) if p["sortie_finale"] else (False,):  # a « école », aussi en fin de mot
        normal = {cle: p[cle] for cle in ("sortie", "envol", "fin_de_mot")}
        if fin:
            p.update(sortie=p["sortie_finale"], envol=p["envol_final"], fin_de_mot=True)
        p["a_ecole"] = True
        ecrire_glyphe(police, "a.fina.ss01" if fin else "a.ss01", None, DESSINS["a"][1], graine="a",
                      coeur=p["coeur_final"] if fin else 0)
        p["a_ecole"] = False
        p.update(normal)
    p["points_inverses"] = True  # points de l'autre forme (ss02), y compris pour le i de fin de mot
    for nom in POINTS_SS02:
        ecrire_glyphe(police, f"{nom}.ss02", None, DESSINS[nom][1], graine=nom)
    if p["sortie_finale"]:
        normal = {cle: p[cle] for cle in ("sortie", "envol", "fin_de_mot")}
        p.update(sortie=p["sortie_finale"], envol=p["envol_final"], fin_de_mot=True)
        ecrire_glyphe(police, "i.fina.ss02", None, DESSINS["i"][1], graine="i", coeur=p["coeur_final"])
        p.update(normal)
    p["points_inverses"] = False
    variantes_par_composant(police)
    if p["amorce"]:
        p["capitale_coeur"] = True
        for nom in CAPITALES_COEUR:
            ecrire_glyphe(police, f"{nom}.ss04", None, DESSINS[nom][1], graine=nom)
        p["capitale_coeur"] = False
    espaces = {"space": (0x20, p["espace"]), "uni00A0": (0xA0, p["espace"]),
               "uni2009": (0x2009, p["espace_fine"]), "uni202F": (0x202F, p["espace_fine"])}
    for nom, (point_code, chasse) in espaces.items():
        glyphe_espace = police[nom] if nom in police else police.newGlyph(nom)
        glyphe_espace.unicodes, glyphe_espace.width = [point_code], chasse
    espacer(police)
    limiter_debords(police)
    police.save()
    print(f"{len(police.keys()) - 1} glyphes écrits et espacés dans {chemin_ufo}")


def ecrire_glyphe(police, nom: str, point_code: int | None, dessiner, graine: str, coeur: float = 0) -> None:
    """Dessine un glyphe ; avec « coeur », une boucle en cœur prolonge le trait qui finit le plus à droite (le ruban)."""
    traits, chasse, ancres = dessiner()
    glyphe_ufo = police[nom] if nom in police else police.newGlyph(nom)
    glyphe_ufo.clearContours()
    glyphe_ufo.clearAnchors()
    stylo = glyphe_ufo.getPen()
    elements = irregulariser(traits, graine)
    if coeur:
        ruban_final = max(elements, key=lambda e: e.squelette[-1][1][-1][0])
        ruban_final.effile_fin = 0.55  # le ruban garde le corps du cœur, qu'il prolonge
        elements += boucle_en_coeur(ruban_final.squelette, coeur)
    for element in elements:
        for depart, courbes in contours_du_trait(element):
            tracer_contour(stylo, depart, courbes)
    glyphe_ufo.width = round(chasse)
    glyphe_ufo.unicodes = [point_code] if point_code else []
    if "top" in ancres:
        ancres = ancres_optiques(glyphe_ufo, nom, ancres["top"][1])
    for nom_ancre, (x, y) in ancres.items():
        glyphe_ufo.appendAnchor({"name": nom_ancre, "x": round(x), "y": round(y)})


def variantes_par_composant(police) -> None:
    """Chiffres tabulaires (.tf, chasse commune, chiffre centré) et ponctuation des capitales (.case, remontée)."""
    chasse_tabulaire = max(police[nom].width for nom in CHIFFRES)
    for nom in CHIFFRES:
        _composant(police, f"{nom}.tf", nom, (chasse_tabulaire - police[nom].width) / 2, 0, chasse_tabulaire)
    for nom, decalage in PONCTUATION_CASE.items():
        _composant(police, f"{nom}.case", nom, 0, decalage, police[nom].width)


def _composant(police, nom: str, base: str, dx: float, dy: float, chasse: float) -> None:
    glyphe_ufo = police[nom] if nom in police else police.newGlyph(nom)
    glyphe_ufo.clearContours()
    glyphe_ufo.clearComponents()
    glyphe_ufo.components.append(Component(baseGlyph=base, transformation=(1, 0, 0, 1, round(dx), round(dy))))
    glyphe_ufo.width = round(chasse)


LETTRES_OGONEK = set("aeiuAEIU")
LETTRES_CARON_APOSTROPHE = set("dltL")


def _bande(chemin: pathops.Path, y_bas: float, y_haut: float) -> tuple[float, float] | None:
    """Étendue horizontale de l'encre entre deux hauteurs."""
    bande = pathops.Path()
    stylo = bande.getPen()
    gauche, _, droite, _ = chemin.bounds
    for point_bande in ((gauche - 10, y_bas), (droite + 10, y_bas), (droite + 10, y_haut), (gauche - 10, y_haut)):
        (stylo.lineTo if bande.points else stylo.moveTo)(point_bande)
    stylo.closePath()
    coupe = pathops.op(chemin, bande, pathops.PathOp.INTERSECTION)
    return None if coupe.bounds == (0, 0, 0, 0) else (coupe.bounds[0], coupe.bounds[2])


def ancres_optiques(glyphe_ufo, nom: str, hauteur: float) -> dict:
    """Ancres posées sur le dessin réel : l'accent se centre sur l'encre de la zone médiane,
    là où ni les entrées ni les pieds ni les rubans ne décentrent la lettre."""
    chemin = pathops.Path()
    glyphe_ufo.draw(chemin.getPen())
    milieu = _bande(chemin, hauteur * 0.4, hauteur * 0.8)
    x = (milieu[0] + milieu[1]) / 2 if milieu else glyphe_ufo.width / 2
    ancres = {"top": (x, hauteur), "bottom": (x, 0)}
    lettre = nom.split(".")[0]
    if lettre in LETTRES_OGONEK:
        flanc = _bande(chemin, 120, 260)
        ancres["ogonek"] = ((flanc[1] if flanc else x) - 25, 0)
    if lettre in LETTRES_CARON_APOSTROPHE:
        haut_hampe = hauteur if lettre != "t" else 650
        hampe = _bande(chemin, haut_hampe - 200, haut_hampe)
        ancres["caronalt"] = ((hampe[1] if hampe else x) + 45, haut_hampe - 10)
    return ancres


def limiter_debords(police) -> None:
    """Un cœur de fin de mot (.fina) ou de capitale (.ss04) déborde sur l'espace voisine d'au plus debord_max :
    au-delà, la chasse s'élargit, pour qu'il ne touche jamais la lettre du mot d'à côté (« dit Yvon »)."""
    limite = PARAMETRES["debord_max"]
    for glyphe_ufo in police:
        if not glyphe_ufo.contours:
            continue
        boite = glyphe_ufo.getBounds(police)
        if glyphe_ufo.name.endswith(".fina") and boite.xMax - glyphe_ufo.width > limite:
            glyphe_ufo.width = math.ceil(boite.xMax - limite)
        if glyphe_ufo.name.endswith(".ss04") and boite.xMin < -limite:
            decalage = math.ceil(-limite - boite.xMin)
            glyphe_ufo.move((decalage, 0))
            glyphe_ufo.width += decalage


def espacer(police) -> None:
    """Espacement optique par surfaces de blanc (scripts/espacer.py), calibré sur n/o et H/O.

    Les chasses calculées dans les fonctions de dessin ne sont que des points de départ.
    """
    p = PARAMETRES
    references = {
        "minuscules": (("n", p["approche"]), ("o", p["approche_ronde"])),
        "capitales": (("H", p["approche_capitale"]), ("O", p["approche_capitale_ronde"])),
    }
    reglages = {categorie: calibrer(police, *paire) for categorie, paire in references.items()}
    for glyphe in police:
        if a_espacer(glyphe, police):
            categorie = "capitales" if glyphe.unicodes and chr(glyphe.unicodes[0]).isupper() else "minuscules"
            espacer_glyphe(glyphe, police, *reglages[categorie])


if __name__ == "__main__":
    parseur = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parseur.add_argument("ufo")
    parseur.add_argument("--sobre", action="store_true", help="paramètres de la famille Tendrille Texte")
    arguments = parseur.parse_args()
    if arguments.sobre:
        PARAMETRES.update(PARAMETRES_SOBRES)
    ecrire(arguments.ufo)
