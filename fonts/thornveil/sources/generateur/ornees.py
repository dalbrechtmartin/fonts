"""Ronces coulantes : capitales et chiffres (jeu ss01), minuscules (jeu ss04), qui fondent en ronces sous la ligne
de base.

Langage d'ornement (principe des polices « dripping », adapté à Thornveil, aucun contour repris) :
- la coulure naît dans la lettre (vers 22 % de sa hauteur), très large, comme si le bas fondait,
  puis s'étrangle sous la ligne de base ;
- elle descend comme une racine de ronce : tracé cassé à angles vifs ;
- épines de rose le long de la tige, en alternance ; la tige s'effile jusqu'à une pointe fine ;
- longueurs fixes d'une graisse à l'autre (en hauteur de capitale), largeur qui suit le fût ;
- placement automatique sur les pieds de chaque lettre, motif et longueur tirés d'une graine stable
  (le nom du glyphe) : chaque ronce diffère, le résultat est identique à chaque génération.
Chaque ronce coulante a un nombre fixe de points : les maîtres restent compatibles.
"""

import zlib
from itertools import pairwise

import capitales
import chiffres
import minuscules
from parametres import GRAISSE_DEFAUT, parametres
from primitives import epine, glyphe, sans_epines

NAISSANCE = 0.22             # hauteur où naît la coulure, en fraction de la hauteur de la lettre
ECHANTILLONS = 16            # points le long de la tige (fixe : compatibilité des maîtres)
FACTEUR_EPINE = 0.9          # longueur des épines de ronce, par rapport à celles des lettres
BASE_EPINE = 0.9             # base proportionnée : même forme en croissant que sur les lettres
# Motifs de cassures : écarts latéraux successifs de la racine, en fraction de sa longueur.
# Leur nombre varie d'un motif à l'autre ; l'échantillonnage garde un nombre de points fixe.
MOTIFS = (
    (0.18, -0.14, 0.10),
    (-0.15, 0.12, -0.08),
    (0.08, 0.16, -0.12),
    (-0.10, -0.06, 0.14),
    (0.14, -0.04, -0.12, 0.06),
    (0.0, 0.15, -0.10),
    (-0.16, 0.10),
    (0.12, -0.16, 0.08, -0.04),
)


def col(fut: float) -> float:
    """Largeur de la tige au plus étroit, sous la ligne de base."""
    return fut * 0.32 + 10


def largeur(y: float, naissance: float, longueur: float, etroit: float) -> float:
    """Profil de la tige : large dans la lettre, étranglée sous la ligne de base, effilée en pointe fine."""
    if y >= 0:
        return etroit * (1.3 + 0.4 * min(y / (naissance * 0.6), 1))  # fin : ne bouche pas les contrepoinçons
    if y >= -0.12 * longueur:
        return etroit * (1.3 - 0.3 * (-y) / (0.12 * longueur))
    reste = min((-y - 0.12 * longueur) / (0.88 * longueur), 1)
    return etroit * max(1 - reste, 0.02)


def parcours(x: float, naissance: float, longueur: float, motif: tuple) -> list:
    """Tracé de la racine : verticale dans la lettre, puis cassures successives vers le bas."""
    points = [(x, naissance), (x, 0)]
    decalage = 0
    for i, ecart in enumerate(motif, start=1):
        decalage += ecart * longueur
        points.append((x + decalage, -longueur * i / len(motif)))
    return points


def echantillonner(points: list, n: int) -> list:
    """n + 1 points régulièrement répartis le long d'une ligne brisée."""
    longueurs = [((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2) ** 0.5 for a, b in pairwise(points)]
    total = sum(longueurs)
    resultat = []
    for k in range(n + 1):
        cible, i = total * k / n, 0
        while i < len(longueurs) - 1 and cible > longueurs[i]:
            cible -= longueurs[i]
            i += 1
        t = cible / longueurs[i]
        (ax, ay), (bx, by) = points[i], points[i + 1]
        resultat.append((ax + (bx - ax) * t, ay + (by - ay) * t))
    return resultat


def ronce_coulante(x: float, longueur: float, hauteur_lettre: float, fut: float, p: dict,
                   motif: tuple, epines: tuple = ((0.45, -1), (0.7, 1))) -> list:
    """Tige qui naît dans la lettre, descend en racine cassée, porte des épines et finit en pointe fine."""
    naissance = hauteur_lettre * NAISSANCE
    etroit = col(fut)
    axe = echantillonner(parcours(x, naissance, longueur, motif), ECHANTILLONS)
    gauche, droite = [], []
    for i, (px, py) in enumerate(axe):
        (ax, ay), (bx, by) = axe[max(i - 1, 0)], axe[min(i + 1, len(axe) - 1)]
        dx, dy = bx - ax, by - ay
        norme = (dx * dx + dy * dy) ** 0.5
        demi = largeur(py, naissance, longueur, etroit) / 2
        nx, ny = -dy / norme * demi, dx / norme * demi
        gauche.append((px + nx, py + ny))
        droite.append((px - nx, py - ny))
    contours = [gauche + droite[::-1]]
    # épines de rose le long de la tige, sur le bord du côté indiqué
    petite = dict(p, epine=p["epine"] * FACTEUR_EPINE)
    for position, cote in epines:
        i = round(position * ECHANTILLONS)
        bord = gauche[i] if cote < 0 else droite[i]
        profondeur = largeur(axe[i][1], naissance, longueur, etroit) * 0.4  # reste dans la tige
        contours.append(epine(bord[0], bord[1], cote, petite, echelle_base=BASE_EPINE, ancrage=profondeur))
    return contours


# Placement automatique ---------------------------------------------------------------------------

LONGUEURS = {"capitale": (0.95, 0.6, 0.8, 0.45), "minuscule": (0.85, 0.5, 0.7, 0.4)}
MAXIMUM = {"capitale": 3, "minuscule": 2}


def graine(nom: str) -> int:
    """Graine stable tirée du nom du glyphe : chaque lettre a ses ronces, identiques à chaque génération."""
    return zlib.crc32(nom.encode())


def polygone(contour: list) -> list:
    """Approximation polygonale d'un contour (poignées comprises) : suffit pour couper la lettre."""
    points = []
    for element in contour:
        points += list(element[1:]) if element[0] == "c" else [element]
    return points


def pleins(contours: list, y: float) -> list:
    """Intervalles d'abscisses où la lettre est pleine à la hauteur y (union des contours)."""
    morceaux = []
    for contour in contours:
        pts = polygone(contour)
        croisements = sorted(
            a[0] + (y - a[1]) * (b[0] - a[0]) / (b[1] - a[1])
            for a, b in zip(pts, pts[1:] + pts[:1]) if (a[1] <= y < b[1]) or (b[1] <= y < a[1])
        )
        morceaux += list(zip(croisements[::2], croisements[1::2]))
    fusion = []
    for debut, fin in sorted(morceaux):
        if fusion and debut <= fusion[-1][1]:
            fusion[-1] = (fusion[-1][0], max(fusion[-1][1], fin))
        else:
            fusion.append((debut, fin))
    return fusion


REPERAGE = 0.3   # hauteur de repérage des fûts : au-dessus des déliés du bas, même en Black


def centres_pleins(contours: list, hauteur_lettre: float, fut: float) -> list:
    """Pieds candidats : fûts repérés à REPERAGE de la hauteur de la lettre, qui descendent bien jusqu'à
    la ligne de base. Repérer plus bas confondrait un fût avec un délié du bas épais (o, e, c en Black)
    et la ronce traverserait le contrepoinçon."""
    lettre = sans_epines(contours)
    pres_du_bas = pleins(lettre, hauteur_lettre * NAISSANCE * 0.5)
    return [(a + b) / 2 for a, b in pleins(lettre, hauteur_lettre * REPERAGE)
            if b - a >= fut * 0.6 and any(debut <= (a + b) / 2 <= fin for debut, fin in pres_du_bas)]


def pied_de_secours(contours: list, hauteur_lettre: float) -> list:
    """Lettre sans fût vertical près de la base (X, V…) : la partie pleine la plus large au ras de la base."""
    au_ras = pleins(sans_epines(contours), hauteur_lettre * NAISSANCE * 0.5)
    debut, fin = max(au_ras, key=lambda intervalle: intervalle[1] - intervalle[0])
    return [(debut + fin) / 2]


def pieds(contours: list, hauteur_lettre: float, fut: float, maximum: int) -> list:
    """Abscisses des pieds de la lettre, au plus maximum : les extrêmes, et le milieu s'il en faut trois.
    Toute lettre a au moins une ronce."""
    larges = centres_pleins(contours, hauteur_lettre, fut) or pied_de_secours(contours, hauteur_lettre)
    if len(larges) <= maximum:
        return larges
    if maximum == 2:
        return [larges[0], larges[-1]]
    return [larges[0], larges[len(larges) // 2], larges[-1]]


def placement(dessiner, sorte: str) -> list:
    """Pieds repérés sur la graisse par défaut, en fraction de la chasse.

    Leur nombre est le même pour tous les maîtres (exigence de la police variable) ; chaque maître
    se recale ensuite sur ses propres pieds (voir recaler).
    """
    p = parametres(GRAISSE_DEFAUT)
    contours, chasse, _ = dessiner(p)
    hauteur, fut = mesures_sorte(sorte, p)
    return [x / chasse for x in pieds(contours, hauteur, fut, MAXIMUM[sorte])]


def recaler(cibles: list, candidats: list) -> list:
    """Pour chaque position de référence, le pied réel le plus proche (sans en prendre deux fois le même).

    En Black, les fûts s'élargissent et se déplacent : sans ce recalage, une ronce tomberait dans un
    contrepoinçon. S'il manque des pieds, la position de référence est gardée.
    """
    libres, resultat = list(candidats), []
    for cible in cibles:
        if libres:
            proche = min(libres, key=lambda x: abs(x - cible))
            libres.remove(proche)
            resultat.append(proche)
        else:
            resultat.append(cible)
    return resultat


def mesures_sorte(sorte: str, p: dict) -> tuple:
    if sorte == "capitale":
        return p["hauteur_capitale"], p["fut_capitale"]
    return p["hauteur_x"], p["fut"]


def coulante(nom: str, dessiner, sorte: str, p: dict):
    """Lettre de base + ronces coulantes placées sur ses pieds, motifs et longueurs tirés de la graine."""
    contours, chasse, ancres = dessiner(p)
    hauteur, fut = mesures_sorte(sorte, p)
    n = graine(nom)
    ajouts = []
    cibles = [fraction * chasse for fraction in placement(dessiner, sorte)]
    candidats = centres_pleins(contours, hauteur, fut) or pied_de_secours(contours, hauteur)
    for i, x in enumerate(recaler(cibles, candidats)):
        motif = MOTIFS[(n + i * 3) % len(MOTIFS)]
        longueur = LONGUEURS[sorte][(n // 7 + i) % len(LONGUEURS[sorte])] * p["hauteur_capitale"]
        cotes = ((0.45, -1), (0.7, 1)) if (n + i) % 2 == 0 else ((0.45, 1), (0.7, -1))
        ajouts += ronce_coulante(x, longueur, hauteur, fut, p, motif, cotes)
    return contours + ajouts, chasse, ancres


def enregistrer(dessins: list, sorte: str, suffixe: str) -> None:
    """dessins : liste de (nom du glyphe de base, fonction de dessin)."""
    for base, dessiner in dessins:
        nom = f"{base}.{suffixe}"
        glyphe(nom)(lambda p, nom=nom, dessiner=dessiner: coulante(nom, dessiner, sorte, p))


CHIFFRES = ("zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine")

enregistrer([(l, getattr(capitales, f"dessiner_{l}")) for l in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"], "capitale", "ss01")
# les chiffres, alignés sur la hauteur de capitale, coulent avec les capitales (ss01) ;
# le zéro pointé aussi, pour que les fonctions zero et ss01 se cumulent
enregistrer([(n, getattr(chiffres, f"dessiner_{n}")) for n in CHIFFRES] + [("zero.zero", chiffres.dessiner_zero_pointe)],
            "capitale", "ss01")
enregistrer([(l, getattr(minuscules, f"dessiner_{l}")) for l in "abcdefghijklmnopqrstuvwxyz"], "minuscule", "ss04")
