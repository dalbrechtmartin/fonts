"""Ajoute la fonction locl à features.fea, à lancer après fonctions_opentype.py (qui réécrit le fichier).

Roumain et moldave : ş Ş (cédille) s'affichent avec la virgule souscrite (ș Ș), forme correcte dans ces
langues quand un texte a été saisi avec la cédille.
Les locl catalan (ŀ), néerlandais (ĳ) et turc/azéri (petites capitales) attendent GF_Latin_Plus.

Usage :
    python sources/generateur/fonctions_locales.py sources/Thornveil-Regular.ufo
"""

import sys
from pathlib import Path

DEBUT, FIN = "# --- locl (fonctions_locales.py) ---", "# --- fin locl ---"
LOCL = f"""{DEBUT}
languagesystem DFLT dflt;
languagesystem latn dflt;
languagesystem latn ROM;
languagesystem latn MOL;

feature locl {{
    script latn;
    language ROM exclude_dflt;
    sub scedilla by uni0219;
    sub Scedilla by uni0218;
    language MOL exclude_dflt;
    sub scedilla by uni0219;
    sub Scedilla by uni0218;
}} locl;
{FIN}
"""


def main(chemin_ufo: str) -> None:
    fichier = Path(chemin_ufo) / "features.fea"
    texte = fichier.read_text(encoding="utf-8") if fichier.exists() else ""
    if DEBUT in texte:  # relance : on remplace le bloc précédent
        texte = texte[:texte.index(DEBUT)] + texte[texte.index(FIN) + len(FIN):]
    # les déclarations languagesystem doivent précéder toute fonction
    lignes = [l for l in texte.splitlines() if not l.startswith("languagesystem")]
    fichier.write_text(LOCL + "\n" + "\n".join(lignes).strip() + "\n", encoding="utf-8")
    print(f"locl roumain et moldave ajoutée à {fichier}")


if __name__ == "__main__":
    main(sys.argv[1])
