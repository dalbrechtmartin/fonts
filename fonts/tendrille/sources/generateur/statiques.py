"""Copie des sources pour les polices statiques : traits fusionnés et contours nettoyés.

Les sources gardent un contour par trait (la police variable en a besoin pour interpoler).
Pour les statiques, on fusionne ici les traits qui se chevauchent dans chaque glyphe dessiné, puis on nettoie
le résultat : coordonnées entières, segments minuscules supprimés. Sinon la fusion faite au build
laisse des segments superposés ou de longueur nulle (signalés par Font Bakery).
Les composés (é, ď…) gardent leurs composants : ils pointent vers des glyphes déjà nettoyés.

Usage :
    python sources/generateur/statiques.py sources/ build/statiques/
"""

import argparse
import math
import shutil
from pathlib import Path

import pathops
import ufoLib2

LONGUEUR_MINIMALE = 6  # unités : un segment plus court disparaît dans son voisin (invisible à l'œil)
ILOT_MAXIMAL = 12  # unités : un contour plus petit dans les deux sens est un éclat laissé par la fusion


def fusionner(glyphe) -> pathops.Path:
    """Union des contours du glyphe (règle non nulle)."""
    chemin = pathops.Path()
    glyphe.draw(chemin.getPen())
    chemin.simplify(fix_winding=True, keep_starting_points=False)
    return chemin


def nettoyer(chemin: pathops.Path, stylo) -> None:
    """Réécrit le chemin en coordonnées entières, sans segment trop court ni répété."""
    deja_vus = set()
    for contour in chemin.contours:
        segments = []
        courant = None
        for verbe, points in contour.segments:
            points = tuple((round(x), round(y)) for x, y in points)
            if verbe == "moveTo":
                courant = points[0]
                continue
            if verbe in ("closePath", "endPath"):
                break
            arrivee = points[-1]
            if math.dist(courant, arrivee) < LONGUEUR_MINIMALE:
                continue
            cle = (courant, *points)
            if cle in deja_vus or (arrivee, *reversed(points[:-1]), courant) in deja_vus:
                continue
            deja_vus.add(cle)
            segments.append((verbe, points))
            courant = arrivee
        tous_points = [point for _, points in segments for point in points]
        if len(segments) < 2 or (max(x for x, _ in tous_points) - min(x for x, _ in tous_points) < ILOT_MAXIMAL
                                 and max(y for _, y in tous_points) - min(y for _, y in tous_points) < ILOT_MAXIMAL):
            continue
        stylo.moveTo(segments[-1][1][-1])
        for verbe, points in segments:
            getattr(stylo, verbe)(*points)
        stylo.closePath()


def preparer(source: Path, destination: Path) -> None:
    shutil.rmtree(destination, ignore_errors=True)
    shutil.copytree(source, destination)
    police = ufoLib2.Font.open(destination)
    for glyphe in police:
        if glyphe.contours and not glyphe.components:
            chemin = fusionner(glyphe)
            glyphe.clearContours()
            nettoyer(chemin, glyphe.getPen())
    police.save()


def main() -> None:
    parseur = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parseur.add_argument("sources", type=Path)
    parseur.add_argument("destination", type=Path)
    arguments = parseur.parse_args()
    arguments.destination.mkdir(parents=True, exist_ok=True)
    for ufo in sorted(arguments.sources.glob("*.ufo")):
        preparer(ufo, arguments.destination / ufo.name)
        print(f"Statique préparée : {arguments.destination / ufo.name}")


if __name__ == "__main__":
    main()
