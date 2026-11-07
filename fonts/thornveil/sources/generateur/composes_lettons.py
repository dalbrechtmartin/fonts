"""Recompose les lettres lettones avec une virgule, à lancer après composer_accents.py.

Unicode décompose ķ ļ ņ ŗ (et capitales) avec une cédille, mais le letton les écrit avec une
virgule souscrite ; ģ s'écrit avec une virgule retournée au-dessus (U+0312).

Usage :
    python sources/generateur/composes_lettons.py sources/Thornveil-Regular.ufo
"""

import sys

import ufoLib2
from ufoLib2.objects import Component

# lettre composée (point de code) -> (base, diacritique, ancre de la base)
LETTONES = {
    0x136: ("K", "commaaccentcomb", "bottom"), 0x137: ("k", "commaaccentcomb", "bottom"),
    0x13B: ("L", "commaaccentcomb", "bottom"), 0x13C: ("l", "commaaccentcomb", "bottom"),
    0x145: ("N", "commaaccentcomb", "bottom"), 0x146: ("n", "commaaccentcomb", "bottom"),
    0x156: ("R", "commaaccentcomb", "bottom"), 0x157: ("r", "commaaccentcomb", "bottom"),
    0x122: ("G", "commaaccentcomb", "bottom"), 0x123: ("g", "uni0312", "top"),
}


def ancre(glyphe, nom: str) -> tuple[float, float]:
    return next((a.x, a.y) for a in glyphe.anchors if a.name == nom)


def main(chemin: str) -> None:
    police = ufoLib2.Font.open(chemin)
    par_point_code = {u: g for g in police for u in g.unicodes}
    presentes = {u: v for u, v in LETTONES.items() if u in par_point_code}  # selon le jeu de glyphes composé
    for point_code, (base, diacritique, nom_ancre) in presentes.items():
        bx, by = ancre(police[base], nom_ancre)
        dx, dy = ancre(police[diacritique], f"_{nom_ancre}")
        glyphe = par_point_code[point_code]
        glyphe.clearContours()
        glyphe.clearComponents()
        glyphe.components.extend([
            Component(baseGlyph=base),
            Component(baseGlyph=diacritique, transformation=(1, 0, 0, 1, bx - dx, by - dy)),
        ])
        glyphe.width = police[base].width
    police.save()
    print(f"{len(presentes)} lettres lettones recomposées avec la virgule")


if __name__ == "__main__":
    main(sys.argv[1])
