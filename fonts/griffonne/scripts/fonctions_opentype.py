"""Écrit les fonctions OpenType (features.fea) à partir des noms de glyphes de l'UFO.

Conventions de nommage reconnues :
- « X.alt1 », « X.alt2 » : alternances → calt en boucle à 3 temps (X, X.alt1, X.alt2, X…) :
  deux lettres identiques qui se suivent ne sont jamais dessinées pareil (effet manuscrit, pinceau) ;
- « X.ss01 »… : jeux stylistiques ; remplacent X ET ses alternances (calt passe avant) ;
- « X.case » (hors diacritiques, qui servent à la composition) → case ;
- « zero.zero » → zero.
kern, mark et mkmk sont générées au build (ufo2ft) à partir du crénage et des ancres : non écrites ici.

Usage :
    python fonctions_opentype.py sources/MaPolice-Regular.ufo [--nom-jeu ss01 "Chats complets"]
"""

import argparse
import re
import unicodedata

import ufoLib2


def est_diacritique(police, nom: str) -> bool:
    base = police[nom.split(".")[0]] if nom.split(".")[0] in police else None
    return bool(base and base.unicodes and unicodedata.category(chr(base.unicodes[0])) == "Mn")


def bloc_calt(police) -> list[str]:
    bases = sorted(n for n in police.keys() if "." not in n and f"{n}.alt1" in police and f"{n}.alt2" in police)
    if not bases:
        return []
    return [
        f"@PINCEAU_BASE = [{' '.join(bases)}];",
        f"@PINCEAU_ALT1 = [{' '.join(f'{n}.alt1' for n in bases)}];",
        f"@PINCEAU_ALT2 = [{' '.join(f'{n}.alt2' for n in bases)}];",
        "",
        "# Boucle à 3 temps : une règle voit la lettre précédente telle qu'elle vient d'être transformée",
        "feature calt {",
        "    lookup alternances_pinceau {",
        "        sub @PINCEAU_ALT1 @PINCEAU_BASE' by @PINCEAU_ALT2;",
        "        sub @PINCEAU_BASE @PINCEAU_BASE' by @PINCEAU_ALT1;",
        "    } alternances_pinceau;",
        "} calt;",
    ]


def bloc_jeux(police, noms_jeux: dict[str, str]) -> list[str]:
    lignes = []
    jeux = sorted({m.group(1) for n in police.keys() if (m := re.search(r"\.(ss\d\d)$", n))})
    for jeu in jeux:
        lignes += ["", f"feature {jeu} {{"]
        if jeu in noms_jeux:
            lignes += ["    featureNames {", f'        name "{noms_jeux[jeu]}";', "    };"]
        for nom in sorted(n for n in police.keys() if n.endswith(f".{jeu}")):
            base = nom[: -len(f".{jeu}")]
            sources = [s for s in (base, f"{base}.alt1", f"{base}.alt2") if s in police]
            for source in sources:
                lignes.append(f"    sub {source} by {nom};")
        lignes.append(f"}} {jeu};")
    return lignes


def bloc_simple(police, fonction: str, paires: list[tuple[str, str]]) -> list[str]:
    if not paires:
        return []
    return ["", f"feature {fonction} {{", *(f"    sub {a} by {b};" for a, b in paires), f"}} {fonction};"]


def main() -> None:
    parseur = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parseur.add_argument("ufo")
    parseur.add_argument("--nom-jeu", nargs=2, action="append", default=[], metavar=("JEU", "NOM"),
                         help="Nom lisible d'un jeu stylistique, affiché dans les logiciels")
    args = parseur.parse_args()

    police = ufoLib2.Font.open(args.ufo)
    case = [(n[: -len(".case")], n) for n in sorted(police.keys())
            if n.endswith(".case") and n[: -len(".case")] in police and not est_diacritique(police, n)]
    zero = [("zero", "zero.zero")] if "zero.zero" in police else []

    lignes = ["# Généré par fonctions_opentype.py : ne pas modifier à la main.",
              "languagesystem DFLT dflt;", "languagesystem latn dflt;", ""]
    lignes += bloc_calt(police)
    lignes += bloc_simple(police, "case", case)
    lignes += bloc_simple(police, "zero", zero)
    lignes += bloc_jeux(police, dict(args.nom_jeu))
    police.features.text = "\n".join(lignes) + "\n"
    police.save()

    resume = {"calt": sum(1 for n in police.keys() if n.endswith(".alt1") and "." not in n[:-5]),
              "case": len(case), "zero": len(zero),
              "jeux": sorted({m.group(1) for n in police.keys() if (m := re.search(r"\.(ss\d\d)$", n))})}
    print(f"features.fea écrit : calt sur {resume['calt']} lettres, case {resume['case']}, zero {resume['zero']}, "
          f"jeux {', '.join(resume['jeux']) or 'aucun'}")


if __name__ == "__main__":
    main()
