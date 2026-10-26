"""Moteur de pinceau : transforme un squelette (le chemin du pinceau) en contour texturé.

Étapes pour chaque trait :
1. échantillonnage fin du squelette (points, tangentes, normales) ;
2. demi-épaisseur modulée par la pression (bruit lent) et une goutte en fin de trait ;
3. bords décalés par un bruit lissé indépendant à gauche et à droite ;
4. extrémités arrondies, rééchantillonnage régulier puis lissage en courbes (Catmull-Rom → Bézier) ;
5. fusion des traits par opérations booléennes.
Le hasard vient d'une graine dérivée du nom du glyphe : chaque build donne la même police.
"""

import math
import zlib
from dataclasses import dataclass, field

import pathops

Point = tuple[float, float]
Segment = tuple[Point, Point, Point, Point]  # courbe de Bézier cubique


@dataclass(frozen=True)
class Reglages:
    fut: float = 92                 # épaisseur nominale du trait
    pression: float = 0.08          # variation lente de l'épaisseur (± 8 %)
    amplitude: float = 10           # ondulation des bords, en unités
    goutte: float = 0.08            # épaississement en fin de trait
    espacement_points: float = 60   # distance entre points du contour final
    ondes_bords: tuple[float, ...] = (190, 330, 540)  # ondulation longue (texture B validée)
    ondes_pression: tuple[float, ...] = (320, 560)


@dataclass
class Trait:
    segments: list[Segment]
    ferme: bool = False
    epaisseur: float = 1.0   # multiplie le fût (point du i, oreilles)
    effilement: float = 0.0  # 0 : goutte en fin de trait ; 0,7 : pointe à 30 % de l'épaisseur (oreille)


@dataclass
class Bruit:
    """Bruit lissé : somme de sinusoïdes aux phases tirées d'une graine (périodique, sans grésillement)."""
    graine: str
    ondes: tuple[float, ...]
    phases: list[float] = field(init=False)

    def __post_init__(self) -> None:
        # crc32 plutôt que hash() : hash() change à chaque lancement de Python
        etat = zlib.crc32(self.graine.encode())
        self.phases = []
        for _ in self.ondes:
            etat = (etat * 1103515245 + 12345) % 2**31
            self.phases.append(etat / 2**31 * 2 * math.pi)

    def __call__(self, abscisse: float) -> float:
        total = sum(math.sin(2 * math.pi * abscisse / onde + phase) for onde, phase in zip(self.ondes, self.phases))
        return total / len(self.ondes)


# Construction de squelettes ---------------------------------------------------

def ligne(a: Point, b: Point) -> Segment:
    return (a, _melange(a, b, 1 / 3), _melange(a, b, 2 / 3), b)


def courbe(a: Point, controle_1: Point, controle_2: Point, b: Point) -> Segment:
    return (a, controle_1, controle_2, b)


def ellipse(cx: float, cy: float, rx: float, ry: float) -> Trait:
    k = 0.5523
    bas, gauche, haut, droite = (cx, cy - ry), (cx - rx, cy), (cx, cy + ry), (cx + rx, cy)
    return Trait([
        courbe(bas, (cx - rx * k, cy - ry), (cx - rx, cy - ry * k), gauche),
        courbe(gauche, (cx - rx, cy + ry * k), (cx - rx * k, cy + ry), haut),
        courbe(haut, (cx + rx * k, cy + ry), (cx + rx, cy + ry * k), droite),
        courbe(droite, (cx + rx, cy - ry * k), (cx + rx * k, cy - ry), bas),
    ], ferme=True)


def arc(cx: float, cy: float, rx: float, ry: float, debut: float, fin: float) -> list[Segment]:
    """Arc d'ellipse de l'angle debut à fin (degrés, sens antihoraire si fin > debut), en quarts au plus."""
    nb = max(1, math.ceil(abs(fin - debut) / 90))
    pas = math.radians(fin - debut) / nb
    k = 4 / 3 * math.tan(pas / 4)
    segments = []
    for i in range(nb):
        a0, a1 = math.radians(debut) + i * pas, math.radians(debut) + (i + 1) * pas
        p0 = (cx + rx * math.cos(a0), cy + ry * math.sin(a0))
        p3 = (cx + rx * math.cos(a1), cy + ry * math.sin(a1))
        c1 = (p0[0] - k * rx * math.sin(a0), p0[1] + k * ry * math.cos(a0))
        c2 = (p3[0] + k * rx * math.sin(a1), p3[1] - k * ry * math.cos(a1))
        segments.append((p0, c1, c2, p3))
    return segments


def lisse(points: list[Point]) -> list[Segment]:
    """Courbe ouverte qui passe par tous les points (Catmull-Rom), pour les formes en S."""
    etendus = [points[0], *points, points[-1]]
    segments = []
    for i in range(1, len(etendus) - 2):
        p0, p1, p2, p3 = etendus[i - 1:i + 3]
        controle_1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        controle_2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        segments.append((p1, controle_1, controle_2, p2))
    return segments


def transformer(traits: list[Trait], echelle: float = 1.0, dx: float = 0, dy: float = 0) -> list[Trait]:
    """Met à l'échelle puis décale des traits (épaisseur comprise) : ª º, accents isolés.

    Une échelle de -1 retourne la forme d'un demi-tour (¡ ¿) ; l'épaisseur reste positive.
    """
    return [Trait([tuple((x * echelle + dx, y * echelle + dy) for x, y in segment) for segment in trait.segments],
                  trait.ferme, trait.epaisseur * abs(echelle), trait.effilement) for trait in traits]


# Géométrie -------------------------------------------------------------------

def _melange(a: Point, b: Point, t: float) -> Point:
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def _point_bezier(s: Segment, t: float) -> Point:
    u = 1 - t
    return tuple(u**3 * s[0][i] + 3 * u * u * t * s[1][i] + 3 * u * t * t * s[2][i] + t**3 * s[3][i] for i in range(2))


def _echantillonner(trait: Trait, pas: float = 4) -> list[tuple[Point, Point, float]]:
    """Points denses du squelette : (point, normale unitaire, abscisse curviligne)."""
    points: list[Point] = []
    for segment in trait.segments:
        longueur = sum(math.dist(_point_bezier(segment, i / 20), _point_bezier(segment, (i + 1) / 20)) for i in range(20))
        nb = max(2, int(longueur / pas))
        debut = 0 if not points else 1
        points += [_point_bezier(segment, i / nb) for i in range(debut, nb + 1)]
    if trait.ferme:
        points.pop()
    resultat, abscisse = [], 0.0
    for i, point in enumerate(points):
        precedent = points[i - 1] if (i > 0 or trait.ferme) else point
        suivant = points[(i + 1) % len(points)] if (i < len(points) - 1 or trait.ferme) else point
        dx, dy = suivant[0] - precedent[0], suivant[1] - precedent[1]
        norme = math.hypot(dx, dy) or 1
        if i > 0:
            abscisse += math.dist(points[i - 1], point)
        resultat.append((point, (-dy / norme, dx / norme), abscisse))
    return resultat


def _reechantillonner(polygone: list[Point], espacement: float) -> list[Point]:
    perimetre = sum(math.dist(polygone[i], polygone[(i + 1) % len(polygone)]) for i in range(len(polygone)))
    nb = max(8, round(perimetre / espacement))
    pas, resultat, cumul, i = perimetre / nb, [], 0.0, 0
    for k in range(nb):
        cible = k * pas
        while True:
            a, b = polygone[i % len(polygone)], polygone[(i + 1) % len(polygone)]
            longueur = math.dist(a, b)
            if cumul + longueur >= cible or longueur == 0 and i > 4 * len(polygone):
                resultat.append(_melange(a, b, (cible - cumul) / longueur if longueur else 0))
                break
            cumul += longueur
            i += 1
    return resultat


def _vers_chemin(polygone: list[Point]) -> pathops.Path:
    """Contour fermé lissé : chaque côté devient une courbe de Catmull-Rom convertie en Bézier."""
    chemin = pathops.Path()
    stylo = chemin.getPen()
    n = len(polygone)
    stylo.moveTo(polygone[0])
    for i in range(n):
        p0, p1, p2, p3 = (polygone[(i + d) % n] for d in (-1, 0, 1, 2))
        controle_1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        controle_2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        stylo.curveTo(controle_1, controle_2, p2)
    stylo.closePath()
    return chemin


# Trait de pinceau ----------------------------------------------------------

def _bords(trait: Trait, reglages: Reglages, graine: str) -> tuple[list[Point], list[Point], list[float]]:
    pression = Bruit(f"{graine}/pression", reglages.ondes_pression)
    bruit_gauche = Bruit(f"{graine}/gauche", reglages.ondes_bords)
    bruit_droite = Bruit(f"{graine}/droite", reglages.ondes_bords)
    echantillons = _echantillonner(trait)
    longueur = echantillons[-1][2] or 1
    gauche, droite, rayons = [], [], []
    for (x, y), (nx, ny), s in echantillons:
        if trait.effilement:
            profil = 1 - trait.effilement * s / longueur
        else:
            profil = 1 + reglages.goutte * (0 if trait.ferme else max(0.0, (s / longueur - 0.8) / 0.2))
        rayon = reglages.fut / 2 * trait.epaisseur * (1 + reglages.pression * pression(s)) * profil
        # Sur un trait fin, l'ondulation diminue d'autant : les bords ne se croisent jamais
        amplitude = reglages.amplitude * min(1.0, rayon / (reglages.fut / 2))
        decalage_gauche = rayon + amplitude * bruit_gauche(s)
        decalage_droite = rayon + amplitude * bruit_droite(s)
        gauche.append((x + nx * decalage_gauche, y + ny * decalage_gauche))
        droite.append((x - nx * decalage_droite, y - ny * decalage_droite))
        rayons.append(rayon)
    return gauche, droite, rayons


def _demi_cercle(centre: Point, depart: Point, rayon: float, sens: float, nb: int = 12) -> list[Point]:
    angle_depart = math.atan2(depart[1] - centre[1], depart[0] - centre[0])
    return [(centre[0] + rayon * math.cos(angle_depart + sens * math.pi * k / nb),
             centre[1] + rayon * math.sin(angle_depart + sens * math.pi * k / nb)) for k in range(1, nb)]


def trait_de_pinceau(trait: Trait, reglages: Reglages, graine: str) -> pathops.Path:
    gauche, droite, rayons = _bords(trait, reglages, graine)
    if trait.ferme:
        exterieur = _vers_chemin(_reechantillonner(gauche, reglages.espacement_points))
        interieur = _vers_chemin(_reechantillonner(droite, reglages.espacement_points))
        a, b = (exterieur, interieur) if abs(exterieur.area) > abs(interieur.area) else (interieur, exterieur)
        return pathops.op(a, b, pathops.PathOp.DIFFERENCE)
    echantillons = _echantillonner(trait)
    fin, debut = echantillons[-1][0], echantillons[0][0]
    # Sens de rotation des embouts : de la gauche vers la droite en passant par l'avant du trait
    sens_fin = -1.0
    polygone = (gauche + _demi_cercle(fin, gauche[-1], rayons[-1], sens_fin)
                + droite[::-1] + _demi_cercle(debut, droite[0], rayons[0], sens_fin))
    chemin = _vers_chemin(_reechantillonner(polygone, reglages.espacement_points))
    chemin.simplify(fix_winding=True)
    return chemin


def dessiner(traits: list[Trait], reglages: Reglages, graine: str) -> pathops.Path:
    """Fusionne tous les traits d'un glyphe en un contour propre."""
    resultat = pathops.Path()
    for indice, trait in enumerate(traits):
        resultat = pathops.op(resultat, trait_de_pinceau(trait, reglages, f"{graine}/{indice}"), pathops.PathOp.UNION)
    resultat.simplify(fix_winding=True)
    return resultat
