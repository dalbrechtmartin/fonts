"""Construit les fichiers de police depuis les sources UFO ou designspace.

Produit :
    fonts/otf/       statiques CFF (bureautique, impression)
    fonts/ttf/       statiques TrueType, hintés avec ttfautohint (écrans Windows)
    fonts/variable/  police variable TrueType (si un .designspace existe)
    fonts/webfonts/  WOFF2 de toutes les versions TrueType (web)

Usage :
    python construire.py sources/ [--sortie fonts/] [--sans-hinting]
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from fontTools.ttLib import TTFont

BIT_PPEM_ENTIER = 1 << 3  # obligatoire sur une police hintée : tailles en pixels arrondies


def lancer_fontmake(arguments: list[str]) -> None:
    commande = [sys.executable, "-m", "fontmake", *arguments, "--overlaps-backend", "pathops"]
    print("$", " ".join(commande))
    subprocess.run(commande, check=True)


def construire_statiques(sources: Path, sortie: Path) -> None:
    designspaces = sorted(sources.glob("*.designspace"))
    ufos = sorted(sources.glob("*.ufo"))
    for format_ in ("otf", "ttf"):
        dossier = sortie / format_
        if designspaces:
            for designspace in designspaces:
                lancer_fontmake(["-m", str(designspace), "-i", "-o", format_, "--output-dir", str(dossier)])
        else:
            for ufo in ufos:
                lancer_fontmake(["-u", str(ufo), "-o", format_, "--output-dir", str(dossier)])


def construire_variable(sources: Path, sortie: Path) -> None:
    for designspace in sorted(sources.glob("*.designspace")):
        lancer_fontmake(["-m", str(designspace), "-o", "variable", "--output-dir", str(sortie / "variable")])


def caler_metriques_windows(sortie: Path) -> None:
    """usWinAscent/Descent = contours extrêmes de toute la famille : moins rogne les accents sous Windows, plus ajoute du vide."""
    fichiers = sorted([*sortie.glob("otf/*.otf"), *sortie.glob("ttf/*.ttf"), *sortie.glob("variable/*.ttf")])
    polices = [TTFont(f) for f in fichiers]
    haut = max(p["head"].yMax for p in polices)
    bas = max(-p["head"].yMin for p in polices)
    for fichier, police in zip(fichiers, polices):
        police["OS/2"].usWinAscent, police["OS/2"].usWinDescent = haut, bas
        police.save(fichier)
    print(f"Métriques Windows : {haut} / {bas} sur {len(fichiers)} fichier(s)")


def hinter(dossier_ttf: Path) -> None:
    from ttfautohint import ttfautohint
    for fichier in sorted(dossier_ttf.glob("*.ttf")):
        temporaire = fichier.with_suffix(".hinte.ttf")
        ttfautohint(in_file=str(fichier), out_file=str(temporaire))
        police = TTFont(temporaire)
        police["head"].flags |= BIT_PPEM_ENTIER
        police.save(fichier)
        temporaire.unlink()
        print(f"Hinting : {fichier.name}")


def compresser_woff2(sortie: Path) -> None:
    dossier_web = sortie / "webfonts"
    dossier_web.mkdir(parents=True, exist_ok=True)
    for fichier in sorted([*sortie.glob("ttf/*.ttf"), *sortie.glob("variable/*.ttf")]):
        police = TTFont(fichier)
        police.flavor = "woff2"
        cible = dossier_web / fichier.with_suffix(".woff2").name
        police.save(cible)
        print(f"WOFF2 : {cible.name} ({cible.stat().st_size // 1024} Ko)")


def main() -> None:
    parseur = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parseur.add_argument("sources", type=Path)
    parseur.add_argument("--sortie", type=Path, default=Path("fonts"))
    parseur.add_argument("--sans-hinting", action="store_true")
    args = parseur.parse_args()

    if not any(args.sources.glob("*.ufo")) and not any(args.sources.glob("*.designspace")):
        raise SystemExit(f"Aucune source .ufo ou .designspace dans {args.sources}")
    for sous_dossier in ("otf", "ttf", "variable", "webfonts"):
        shutil.rmtree(args.sortie / sous_dossier, ignore_errors=True)

    construire_statiques(args.sources, args.sortie)
    construire_variable(args.sources, args.sortie)
    caler_metriques_windows(args.sortie)
    if not args.sans_hinting:
        hinter(args.sortie / "ttf")
    compresser_woff2(args.sortie)
    print(f"\nTerminé : {args.sortie.resolve()}")


if __name__ == "__main__":
    main()
