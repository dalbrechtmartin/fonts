"""Retire les variantes coulantes (ss01, ss04) des lettres à accent bas, à lancer après composer_accents.py.

Cédille, ogonek et virgule souscrite se mêleraient aux ronces coulantes et deviendraient illisibles :
avec ss01 ou ss04 actifs, ç ą ș… gardent leur forme normale.

Usage :
    python sources/generateur/sans_coulures_accents_bas.py sources/Thornveil-Regular.ufo
"""

import sys

import ufoLib2

ACCENTS_BAS = {"cedillacomb", "ogonekcomb", "commaaccentcomb"}
SUFFIXES = (".ss01", ".ss04")


def main(chemin: str) -> None:
    police = ufoLib2.Font.open(chemin)
    a_retirer = [g.name for g in police if g.name.endswith(SUFFIXES)
                 and any(c.baseGlyph in ACCENTS_BAS for c in g.components)]
    for nom in a_retirer:
        del police[nom]
    police.save()
    print(f"{len(a_retirer)} variantes coulantes à accent bas retirées")


if __name__ == "__main__":
    main(sys.argv[1])
