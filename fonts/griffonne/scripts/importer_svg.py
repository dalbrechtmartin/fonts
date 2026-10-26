"""Importe des glyphes dessinés en SVG dans une source UFO.

Convention de dessin (un fichier par glyphe, nommé par son nom de glyphe : a.svg, eacute.svg, A.svg) :
- le plan de travail fait la hauteur d'un cadratin (1000 unités par défaut) ;
- la ligne de base est à `ascender` unités du haut du plan de travail ;
- la largeur du plan de travail est la chasse du glyphe (approche comprise).
Les contours sont fusionnés et réorientés (skia-pathops) : chevauchements et sens corrigés.

Usage :
    python importer_svg.py dossier_svg/ sources/MaPolice-Regular.ufo
"""

import argparse
import re
import unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path

import pathops
import ufoLib2
from fontTools.agl import toUnicode
from fontTools.pens.transformPen import TransformPen
from fontTools.svgLib.path import SVGPath


def boite_svg(racine_svg: ET.Element) -> tuple[float, float, float, float]:
    """Retourne (x, y, largeur, hauteur) du viewBox, ou des attributs width/height."""
    if "viewBox" in racine_svg.attrib:
        x, y, largeur, hauteur = (float(v) for v in re.split(r"[\s,]+", racine_svg.attrib["viewBox"].strip()))
        return x, y, largeur, hauteur
    return 0.0, 0.0, float(racine_svg.attrib["width"].rstrip("px")), float(racine_svg.attrib["height"].rstrip("px"))


def importer_glyphe(fichier: Path, police: ufoLib2.Font) -> None:
    texte = fichier.read_text(encoding="utf-8")
    x0, y0, largeur, hauteur = boite_svg(ET.fromstring(texte))
    echelle = police.info.unitsPerEm / hauteur
    chemin = pathops.Path()
    # SVG : y vers le bas depuis le haut ; police : y vers le haut depuis la ligne de base
    transformation = (echelle, 0, 0, -echelle, -x0 * echelle, police.info.ascender + y0 * echelle)
    SVGPath.fromstring(texte.encode("utf-8")).draw(TransformPen(chemin, transformation))
    chemin.simplify(fix_winding=True, keep_starting_points=False)

    nom = fichier.stem
    glyphe = police.newGlyph(nom) if nom not in police else police[nom]
    glyphe.clearContours()
    chemin.draw(glyphe.getPen())
    glyphe.width = round(largeur * echelle)
    caractere = toUnicode(nom)
    if len(caractere) == 1 and not glyphe.unicodes:
        glyphe.unicodes = [ord(caractere)]


def main() -> None:
    parseur = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parseur.add_argument("dossier_svg", type=Path)
    parseur.add_argument("ufo", type=Path)
    args = parseur.parse_args()

    police = ufoLib2.Font.open(args.ufo)
    fichiers = sorted(args.dossier_svg.glob("*.svg"))
    if not fichiers:
        raise SystemExit(f"Aucun SVG dans {args.dossier_svg}")
    for fichier in fichiers:
        importer_glyphe(fichier, police)
        glyphe = police[fichier.stem]
        nom_unicode = unicodedata.name(chr(glyphe.unicodes[0]), "?") if glyphe.unicodes else "sans Unicode"
        print(f"{fichier.stem:<16} chasse {glyphe.width:>5}  {nom_unicode}")
    police.save()
    print(f"{len(fichiers)} glyphe(s) importé(s) dans {args.ufo}")


if __name__ == "__main__":
    main()
