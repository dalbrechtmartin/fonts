"""Écrit les fonctions OpenType (features.fea) à partir des noms de glyphes de l'UFO.

Conventions de nommage reconnues :
- « X.alt1 », « X.alt2 » : alternances → calt en boucle à 3 temps (X, X.alt1, X.alt2, X…) :
  deux lettres identiques qui se suivent ne sont jamais dessinées pareil (effet manuscrit, pinceau) ;
- « X.ss01 »… : jeux stylistiques ; remplacent X ET ses alternances (calt passe avant) ;
- « X.case » (hors diacritiques, qui servent à la composition) → case ;
- « zero.zero » → zero ; « X.tf » (chiffres tabulaires) → tnum ;
- « X.fina » : forme de fin de mot → calt contextuel : X devient X.fina quand il n'est pas suivi
  d'une lettre, d'une apostrophe, d'un trait d'union (« aujourd’hui », « dit-elle ») ni d'une espace
  insécable (« Bonjour ! » : le ruban toucherait la ponctuation) ; le jeu ss05 annule ces formes ;
- « X.init » : forme de début de mot → calt contextuel : X devient X.init quand il n'est pas précédé
  d'une lettre ou d'une apostrophe ; un mot d'une lettre prend sa forme de fin.
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


def bloc_fins_de_mots(police, noms_jeux: dict[str, str]) -> list[str]:
    fins = sorted(n for n in police.keys() if "." not in n and f"{n}.fina" in police)
    debuts = sorted(n for n in police.keys() if "." not in n and f"{n}.init" in police)
    if not fins and not debuts:
        return []
    lettres = sorted(n for n in police.keys() if n.split(".")[0] in police and police[n.split(".")[0]].unicodes
                     and unicodedata.category(chr(police[n.split(".")[0]].unicodes[0])).startswith("L"))
    lettres += [n for n in ("quoteright", "quotesingle", "hyphen", "periodcentered") if n in police]  # « aujourd’hui », « dit-elle », « l·l »
    insecables = [n for n in ("uni00A0", "uni202F") if n in police]
    lignes = ["", f"@DANS_LE_MOT = [{' '.join(lettres)}];"]
    if insecables:  # devant une insécable (« Bonjour ! ») le ruban toucherait la ponctuation
        lignes.append(f"@INSECABLES = [{' '.join(insecables)}];")
    if fins:
        lignes += [f"@FIN_BASE = [{' '.join(fins)}];", f"@FIN_FINA = [{' '.join(f'{n}.fina' for n in fins)}];"]
    if debuts:
        lignes += [f"@INIT_BASE = [{' '.join(debuts)}];", f"@INIT = [{' '.join(f'{n}.init' for n in debuts)}];"]
    lignes += ["", "# Fins de mots d'abord : un mot d'une seule lettre garde sa forme de fin", "feature calt {"]
    if fins:
        lignes += ["    lookup fins_de_mots {", "        ignore sub @FIN_BASE' @DANS_LE_MOT;"]
        if insecables:
            lignes.append("        ignore sub @FIN_BASE' @INSECABLES;")
        lignes += ["        sub @FIN_BASE' by @FIN_FINA;", "    } fins_de_mots;"]
    if debuts:
        lignes += ["    lookup debuts_de_mots {", "        ignore sub @DANS_LE_MOT @INIT_BASE';",
                   "        sub @INIT_BASE' by @INIT;", "    } debuts_de_mots;"]
    lignes.append("} calt;")
    if fins:  # ss05 annule les formes de fin juste après calt, avant les autres jeux
        lignes += ["", "feature ss05 {"]
        if "ss05" in noms_jeux:
            lignes += ["    featureNames {", f'        name "{noms_jeux["ss05"]}";', "    };"]
        lignes += ["    sub @FIN_FINA by @FIN_BASE;", "} ss05;"]
    return lignes


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
    tabulaires = [(n[: -len(".tf")], n) for n in sorted(police.keys()) if n.endswith(".tf") and n[: -len(".tf")] in police]

    lignes = ["# Généré par fonctions_opentype.py : ne pas modifier à la main.",
              "languagesystem DFLT dflt;", "languagesystem latn dflt;", ""]
    lignes += bloc_calt(police)
    lignes += bloc_fins_de_mots(police, dict(args.nom_jeu))
    lignes += bloc_simple(police, "case", case)
    lignes += bloc_simple(police, "zero", zero)
    lignes += bloc_simple(police, "tnum", tabulaires)
    lignes += bloc_jeux(police, dict(args.nom_jeu))
    police.features.text = "\n".join(lignes) + "\n"
    police.save()

    resume = {"calt": sum(1 for n in police.keys() if n.endswith(".alt1") and "." not in n[:-5]),
              "case": len(case), "zero": len(zero), "tnum": len(tabulaires),
              "jeux": sorted({m.group(1) for n in police.keys() if (m := re.search(r"\.(ss\d\d)$", n))})}
    resume["fins"] = sum(1 for n in police.keys() if n.endswith(".fina"))
    resume["debuts"] = sum(1 for n in police.keys() if n.endswith(".init"))
    print(f"features.fea écrit : calt sur {resume['calt']} lettres, fins de mots {resume['fins']}, "
          f"débuts de mots {resume['debuts']}, "
          f"case {resume['case']}, zero {resume['zero']}, tnum {resume['tnum']}, "
          f"jeux {', '.join(resume['jeux']) or 'aucun'}")


if __name__ == "__main__":
    main()
