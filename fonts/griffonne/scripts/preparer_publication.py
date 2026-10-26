"""Prépare l'archive de version d'une police : dist/<Nom>-<version>.zip.

Contenu : fonts/ (otf, ttf, variable, webfonts), OFL.txt, OFL-FAQ.txt, FONTLOG.txt, AUTHORS.txt, README.md.
La version est lue dans la police construite (name ID 5), pas saisie à la main.
Refuse de préparer l'archive s'il manque la licence ou si verifier.py signale une erreur.

Usage (depuis la racine du projet) :
    python scripts/preparer_publication.py [--polices fonts/] [--sortie dist/]
"""

import argparse
import re
import subprocess
import sys
import zipfile
from pathlib import Path

from fontTools.ttLib import TTFont

FICHIERS_OBLIGATOIRES = ("OFL.txt", "FONTLOG.txt", "README.md")
FICHIERS_FACULTATIFS = ("OFL-FAQ.txt", "AUTHORS.txt")


def version_et_nom(dossier_polices: Path) -> tuple[str, str]:
    reference = next(dossier_polices.glob("ttf/*.ttf"), None) or next(dossier_polices.glob("otf/*.otf"))
    noms = TTFont(reference)["name"]
    version = re.search(r"\d+\.\d+", noms.getDebugName(5) or "").group(0)
    famille = re.sub(r"[^A-Za-z0-9]", "", noms.getDebugName(1) or "Police")
    return famille, version


def main() -> None:
    parseur = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parseur.add_argument("--polices", type=Path, default=Path("fonts"))
    parseur.add_argument("--sortie", type=Path, default=Path("dist"))
    args = parseur.parse_args()

    manquants = [f for f in FICHIERS_OBLIGATOIRES if not Path(f).exists()]
    if manquants:
        raise SystemExit(f"Archive non préparée : fichiers manquants {', '.join(manquants)}")
    controle = subprocess.run([sys.executable, "scripts/verifier.py", *map(str, sorted(args.polices.glob("ttf/*.ttf")))],
                              capture_output=True, text=True, check=False)
    if controle.returncode != 0:
        raise SystemExit("Archive non préparée : verifier.py signale des erreurs.\n" + controle.stdout[-1500:])

    famille, version = version_et_nom(args.polices)
    args.sortie.mkdir(exist_ok=True)
    archive = args.sortie / f"{famille}-{version}.zip"
    racine = f"{famille}-{version}"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zip_:
        for fichier in sorted(args.polices.rglob("*")):
            if fichier.is_file():
                zip_.write(fichier, f"{racine}/{fichier.as_posix()}")
        for nom in (*FICHIERS_OBLIGATOIRES, *FICHIERS_FACULTATIFS):
            if Path(nom).exists():
                zip_.write(nom, f"{racine}/{nom}")
    with zipfile.ZipFile(archive) as zip_:
        contenu = zip_.namelist()
    print(f"{archive} ({archive.stat().st_size // 1024} Ko, {len(contenu)} fichiers)")
    for nom in contenu:
        print("  ", nom)


if __name__ == "__main__":
    main()
