"""Contrôle les polices construites et écrit un rapport Markdown.

Vérifie : couverture du jeu visé, typographie française, métadonnées de licence,
métriques verticales, espaces, glyphes vides. Option : lance aussi Font Bakery.

Usage :
    python verifier.py fonts/ttf/*.ttf [--jeu GF_Latin_Core] [--rapport documentation/controle.md] [--fontbakery]
Code de sortie 1 s'il reste une erreur.
"""

import argparse
import subprocess
import sys
import unicodedata
from pathlib import Path

from fontTools.ttLib import TTFont

CARACTERES_FRANCAIS = "àâæçéèêëîïôœùûüÿÀÂÆÇÉÈÊËÎÏÔŒÙÛÜŸ«»‹›‘’“”–—…€"
ESPACES_FRANCAISES = {0x00A0: "espace insécable", 0x202F: "espace fine insécable (avant ; ! ? et dans « »)"}
BIT_USE_TYPO_METRICS = 1 << 7
ERREUR, ATTENTION, OK = "ERREUR", "ATTENTION", "OK"


class Rapport:
    def __init__(self) -> None:
        self.lignes: list[str] = []
        self.nb_erreurs = 0

    def ajouter(self, niveau: str, message: str) -> None:
        self.nb_erreurs += niveau == ERREUR
        self.lignes.append(f"- **{niveau}** · {message}")

    def titre(self, texte: str) -> None:
        self.lignes.append(f"\n## {texte}\n")


def lister(points_codes) -> str:
    return " ".join(f"{chr(p)} (U+{p:04X})" for p in sorted(points_codes)[:40]) + (" …" if len(points_codes) > 40 else "")


def verifier_couverture(police: TTFont, jeu: str, rapport: Rapport) -> None:
    import glyphsets
    table = police.getBestCmap()
    manquants = set(glyphsets.unicodes_per_glyphset(jeu)) - set(table)
    if manquants:
        rapport.ajouter(ERREUR, f"{jeu} : {len(manquants)} caractère(s) manquant(s) : {lister(manquants)}")
    else:
        rapport.ajouter(OK, f"{jeu} couvert entièrement")
    manquants_fr = {ord(c) for c in CARACTERES_FRANCAIS} - set(table)
    for point_code, role in ESPACES_FRANCAISES.items():
        if point_code not in table:
            rapport.ajouter(ERREUR, f"{role} U+{point_code:04X} absente")
    if manquants_fr:
        rapport.ajouter(ERREUR, f"Typographie française incomplète : {lister(manquants_fr)}")
    else:
        rapport.ajouter(OK, "Typographie française complète (accents des capitales, guillemets, apostrophe, €)")


def verifier_glyphes_vides(police: TTFont, rapport: Rapport) -> None:
    ensemble = police.getGlyphSet()
    from fontTools.pens.boundsPen import BoundsPen
    vides = []
    for point_code, nom in police.getBestCmap().items():
        if unicodedata.category(chr(point_code))[0] in "LNPS":
            stylo = BoundsPen(ensemble)
            ensemble[nom].draw(stylo)
            if stylo.bounds is None:
                vides.append(point_code)
    if vides:
        rapport.ajouter(ERREUR, f"Glyphes visibles sans contour : {lister(vides)}")
    stylo = BoundsPen(ensemble)
    ensemble[".notdef"].draw(stylo)
    if stylo.bounds is None:
        rapport.ajouter(ATTENTION, ".notdef est vide : dessine un rectangle barré pour repérer les caractères absents")


def verifier_licence(police: TTFont, rapport: Rapport) -> None:
    noms = police["name"]
    for identifiant, role in ((0, "copyright"), (9, "créatrice"), (13, "description de licence"), (14, "URL de licence")):
        valeur = noms.getDebugName(identifiant)
        if valeur:
            rapport.ajouter(OK, f"{role} : {valeur[:90]}")
        else:
            rapport.ajouter(ERREUR, f"{role} absent (name ID {identifiant})")
    if "Open Font License" not in (noms.getDebugName(13) or ""):
        rapport.ajouter(ATTENTION, "La description de licence ne mentionne pas l'Open Font License")
    if police["OS/2"].fsType != 0:
        rapport.ajouter(ERREUR, f"fsType = {police['OS/2'].fsType} : mettre 0 (installable)")


def verifier_metriques(police: TTFont, rapport: Rapport) -> None:
    os2, hhea, head = police["OS/2"], police["hhea"], police["head"]
    if (hhea.ascent, hhea.descent) != (os2.sTypoAscender, os2.sTypoDescender):
        rapport.ajouter(ERREUR, f"hhea ({hhea.ascent}, {hhea.descent}) ≠ typo ({os2.sTypoAscender}, {os2.sTypoDescender}) : "
                                "interlignage différent selon le système")
    if not os2.fsSelection & BIT_USE_TYPO_METRICS:
        rapport.ajouter(ATTENTION, "Bit USE_TYPO_METRICS non activé")
    if os2.usWinAscent < head.yMax or os2.usWinDescent < -head.yMin:
        rapport.ajouter(ERREUR, f"Rognage possible sous Windows : win ({os2.usWinAscent}, {os2.usWinDescent}) "
                                f"< contours ({head.yMax}, {-head.yMin})")
    interligne = (os2.sTypoAscender - os2.sTypoDescender + os2.sTypoLineGap) / head.unitsPerEm
    niveau = OK if 1.1 <= interligne <= 1.4 else ATTENTION
    rapport.ajouter(niveau, f"Interlignage par défaut : {interligne:.2f} × corps (le CSS appliquera ≥ 1,5 au texte courant)")


def verifier_espaces_et_chiffres(police: TTFont, rapport: Rapport) -> None:
    table, chasses = police.getBestCmap(), police["hmtx"].metrics
    if 0x20 in table and 0xA0 in table and chasses[table[0x20]][0] != chasses[table[0xA0]][0]:
        rapport.ajouter(ERREUR, "L'espace insécable n'a pas la chasse de l'espace")
    chiffres = {chasses[table[p]][0] for p in range(0x30, 0x3A) if p in table}
    fonctions = {r.FeatureTag for r in police["GSUB"].table.FeatureList.FeatureRecord} if "GSUB" in police else set()
    if len(chiffres) > 1 and "tnum" not in fonctions:
        rapport.ajouter(ATTENTION, "Chiffres proportionnels sans fonction tnum : les tableaux de nombres ne s'aligneront pas")
    elif chiffres:
        rapport.ajouter(OK, "Chiffres alignables en tableau")


def lancer_fontbakery(fichiers: list[str], rapport: Rapport) -> None:
    sortie = Path("build") / "fontbakery.md"
    sortie.parent.mkdir(exist_ok=True)
    resultat = subprocess.run([sys.executable, "-m", "fontbakery", "check-universal", "--ghmarkdown", str(sortie), *fichiers],
                              capture_output=True, text=True)
    niveau = OK if resultat.returncode == 0 else ATTENTION
    rapport.ajouter(niveau, f"Font Bakery (check-universal) : rapport complet dans {sortie}")


def main() -> None:
    parseur = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parseur.add_argument("polices", nargs="+")
    parseur.add_argument("--jeu", default="GF_Latin_Core")
    parseur.add_argument("--rapport", type=Path)
    parseur.add_argument("--fontbakery", action="store_true")
    args = parseur.parse_args()

    rapport = Rapport()
    rapport.lignes.append("# Rapport de contrôle")
    for fichier in args.polices:
        police = TTFont(fichier)
        rapport.titre(Path(fichier).name)
        verifier_couverture(police, args.jeu, rapport)
        verifier_glyphes_vides(police, rapport)
        verifier_licence(police, rapport)
        verifier_metriques(police, rapport)
        verifier_espaces_et_chiffres(police, rapport)
    if args.fontbakery:
        rapport.titre("Font Bakery")
        lancer_fontbakery(args.polices, rapport)
    rapport.lignes.append(f"\n**Bilan : {rapport.nb_erreurs} erreur(s).**")

    texte = "\n".join(rapport.lignes)
    if args.rapport:
        args.rapport.write_text(texte + "\n", encoding="utf-8")
    print(texte)
    sys.exit(1 if rapport.nb_erreurs else 0)


if __name__ == "__main__":
    main()
