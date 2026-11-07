"""Active le « smart dropout » sur la police variable (non hintée), à lancer après construire.py.

Sans instructions dans la table prep, un rasteriseur TrueType peut faire disparaître des traits plus fins
qu'un pixel (déliés, épines, ronces) : le smart dropout le lui interdit. Ajoute aussi une table gasp
(lissage à toutes les tailles), puis régénère le WOFF2 de la variable.

Usage :
    python scripts/finaliser_variable.py fonts/
"""

import sys
from pathlib import Path

from fontTools.ttLib import TTFont, newTable
from fontTools.ttLib.tables import ttProgram
from fontTools.ttLib.woff2 import compress


def finaliser(chemin: Path, dossier_web: Path) -> None:
    police = TTFont(chemin)
    prep = newTable("prep")
    prep.program = ttProgram.Program()
    prep.program.fromAssembly(["PUSHW[]", "511", "SCANCTRL[]", "PUSHB[]", "4", "SCANTYPE[]"])
    police["prep"] = prep
    gasp = newTable("gasp")
    gasp.version = 1
    gasp.gaspRange = {0xFFFF: 0x000F}
    police["gasp"] = gasp
    police.save(chemin)
    compress(str(chemin), str(dossier_web / f"{chemin.stem}.woff2"))
    print(f"smart dropout et gasp ajoutés : {chemin}")


def main(dossier: str) -> None:
    racine = Path(dossier)
    for chemin in sorted((racine / "variable").glob("*.ttf")):
        finaliser(chemin, racine / "webfonts")


if __name__ == "__main__":
    main(sys.argv[1])
