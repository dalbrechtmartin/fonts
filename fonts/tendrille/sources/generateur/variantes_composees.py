"""Composés dont un diacritique change avec un jeu stylistique (ä ë ï ż… avec ss02).

composer_accents.py remplace la lettre de base d'un composé par sa variante (é.fina = e.fina + accent),
mais pas le diacritique. Ici, pour chaque glyphe fait de composants, si l'un d'eux a une variante
« .<jeu> », on crée « <glyphe>.<jeu> » avec ce composant échangé : ï.ss02 = ı + tréma.ss02.
À lancer après composer_accents.py.

Usage :
    python sources/generateur/variantes_composees.py sources/Tendrille-Regular.ufo ss02
"""

import argparse

import ufoLib2
from ufoLib2.objects import Component


def main() -> None:
    parseur = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parseur.add_argument("ufo")
    parseur.add_argument("jeu", help="suffixe du jeu stylistique, ex. ss02")
    arguments = parseur.parse_args()
    police = ufoLib2.Font.open(arguments.ufo)
    suffixe = f".{arguments.jeu}"
    composes = [g for g in police if g.components and not g.contours and not g.name.endswith(suffixe)]
    nb = 0
    for compose in composes:
        if not any(f"{c.baseGlyph}{suffixe}" in police for c in compose.components):
            continue
        variante = police[compose.name + suffixe] if compose.name + suffixe in police else police.newGlyph(compose.name + suffixe)
        variante.clearContours()
        variante.clearComponents()
        for composant in compose.components:
            nom = f"{composant.baseGlyph}{suffixe}" if f"{composant.baseGlyph}{suffixe}" in police else composant.baseGlyph
            variante.components.append(Component(baseGlyph=nom, transformation=composant.transformation))
        variante.width = compose.width
        nb += 1
    police.save()
    print(f"{nb} composés en variante {suffixe}")


if __name__ == "__main__":
    main()
