"""Analyse une police (référence, concurrente ou version précédente) et écrit un rapport Markdown.

Mesure : métriques et proportions, graisse et contraste (sur un rendu matriciel, donc approximatifs),
couverture des jeux Google Fonts, fonctions OpenType, axes variables, licence, et paires de glyphes
qui risquent d'être confondues (I l 1, O 0, rn m…).

Usage :
    python analyser_police.py police.ttf [autre.otf…] [--rapport documentation/audit-mesures.md]
"""

import argparse
from pathlib import Path

from fontTools.ttLib import TTFont
from PIL import Image, ImageChops, ImageDraw, ImageFont

TAILLE_RENDU = 400
JEUX_LATINS = ("GF_Latin_Kernel", "GF_Latin_Core", "GF_Latin_Plus", "GF_Latin_African", "GF_Latin_Vietnamese")
# Confusions qui gênent la lecture, notamment pour les personnes malvoyantes ou dyslexiques
PAIRES_CONFUSABLES = (
    ("I", "l"), ("l", "1"), ("I", "1"), ("O", "0"), ("o", "0"), ("rn", "m"), ("cl", "d"),
    ("5", "S"), ("2", "Z"), ("8", "B"), ("6", "b"), ("9", "g"),
    ("vv", "w"), ("u", "n"), ("'", "’"), ("-", "–"),
)
# Lettres qui ne sont que le reflet l'une de l'autre : piège connu pour les lecteurs dyslexiques
PAIRES_MIROIRS = (("b", "d"), ("p", "q"))
SEUIL_CONFUSION = 0.85
SEUIL_MIROIR = 0.90  # un léger détail distinctif (éperon, queue) suffit à passer sous ce seuil


def rendre(police_pil: ImageFont.FreeTypeFont, texte: str) -> Image.Image:
    gauche, haut, droite, bas = police_pil.getbbox(texte)
    image = Image.new("L", (max(droite - gauche, 1) + 4, max(bas - haut, 1) + 4), 0)
    ImageDraw.Draw(image).text((2 - gauche, 2 - haut), texte, font=police_pil, fill=255)
    return image


def rendre_sur_ligne_de_base(police_pil: ImageFont.FreeTypeFont, texte: str, taille: tuple[int, int]) -> Image.Image:
    """Rendu à position fixe : les différences de taille et de hauteur comptent dans la comparaison."""
    image = Image.new("L", taille, 0)
    ImageDraw.Draw(image).text((0, taille[1] * 0.8), texte, font=police_pil, fill=255, anchor="ls")
    return image


def epaisseur_premier_trait(valeurs: list[int]) -> int:
    """Longueur de la première suite de pixels encrés."""
    debut = next((i for i, v in enumerate(valeurs) if v > 127), None)
    if debut is None:
        return 0
    fin = next((i for i in range(debut, len(valeurs)) if valeurs[i] <= 127), len(valeurs))
    return fin - debut


def mesurer_traits(police_pil: ImageFont.FreeTypeFont, unites_par_cadratin: int) -> dict[str, float]:
    """Fût vertical et délié horizontal de « o », en unités de la police."""
    image = rendre(police_pil, "o")
    largeur, hauteur = image.size
    pixels = image.load()
    ligne_milieu = [pixels[x, hauteur // 2] for x in range(largeur)]
    colonne_milieu = [pixels[largeur // 2, y] for y in range(hauteur)]
    echelle = unites_par_cadratin / TAILLE_RENDU
    fut, delie = epaisseur_premier_trait(ligne_milieu) * echelle, epaisseur_premier_trait(colonne_milieu) * echelle
    return {"fut": fut, "delie": delie, "contraste": fut / delie if delie else 0}


def recouvrement(image_a: Image.Image, image_b: Image.Image) -> float:
    """Intersection / union des deux silhouettes."""
    intersection = ImageChops.multiply(image_a, image_b).point(lambda v: 255 if v > 127 else 0)
    union = ImageChops.lighter(image_a, image_b).point(lambda v: 255 if v > 127 else 0)
    nb_union = union.histogram()[255]
    return intersection.histogram()[255] / nb_union if nb_union else 0


def similarite(police_pil: ImageFont.FreeTypeFont, a: str, b: str, miroir: bool = False) -> float:
    largeur = int(max(police_pil.getlength(a), police_pil.getlength(b))) + 4
    taille = (largeur, int(TAILLE_RENDU * 1.4))
    image_a = rendre_sur_ligne_de_base(police_pil, a, taille)
    image_b = rendre_sur_ligne_de_base(police_pil, b, taille)
    if miroir:
        image_b = image_b.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    # On compare les formes, pas leur position dans la chasse : centres d'encre alignés
    boite_a, boite_b = image_a.getbbox(), image_b.getbbox()
    if boite_a and boite_b:
        decalage = (boite_a[0] + boite_a[2] - boite_b[0] - boite_b[2]) // 2
        image_b = ImageChops.offset(image_b, decalage, 0)
    return recouvrement(image_a, image_b)


def hauteur_mesuree(police: TTFont, caractere: str) -> int:
    from fontTools.pens.boundsPen import BoundsPen
    nom = police.getBestCmap().get(ord(caractere))
    if not nom:
        return 0
    stylo = BoundsPen(police.getGlyphSet())
    police.getGlyphSet()[nom].draw(stylo)
    return round(stylo.bounds[3]) if stylo.bounds else 0


def couverture(police: TTFont) -> list[str]:
    try:
        import glyphsets
    except ImportError:
        return ["- glyphsets non installé : couverture non mesurée"]
    table = set(police.getBestCmap())
    lignes = []
    for jeu in JEUX_LATINS:
        attendus = set(glyphsets.unicodes_per_glyphset(jeu))
        lignes.append(f"- {jeu} : {100 * len(attendus & table) / len(attendus):.0f} %")
    return lignes


def analyser(fichier: Path) -> str:
    police = TTFont(fichier)
    noms, os2, upm = police["name"], police["OS/2"], police["head"].unitsPerEm
    # Formes de base, sans fonctions OpenType : un ruban de fin de mot fausserait les comparaisons
    police_pil = ImageFont.truetype(str(fichier), TAILLE_RENDU, layout_engine=ImageFont.Layout.BASIC)
    hauteur_x = getattr(os2, "sxHeight", 0) or hauteur_mesuree(police, "x")
    hauteur_capitale = getattr(os2, "sCapHeight", 0) or hauteur_mesuree(police, "H")
    traits = mesurer_traits(police_pil, upm)
    fonctions = sorted({r.FeatureTag for t in ("GSUB", "GPOS") if t in police
                        for r in police[t].table.FeatureList.FeatureRecord})
    axes = [f"{a.axisTag} {a.minValue:g}–{a.maxValue:g}" for a in police["fvar"].axes] if "fvar" in police else []

    lignes = [
        f"## {noms.getDebugName(4)} ({fichier.name})",
        "",
        "### Identité et licence",
        f"- Créatrice ou créateur : {noms.getDebugName(9) or 'non renseigné'}",
        f"- Copyright : {noms.getDebugName(0) or 'non renseigné'}",
        f"- Licence : {noms.getDebugName(13) or 'non renseignée'} {noms.getDebugName(14) or ''}",
        f"- Version : {noms.getDebugName(5)}",
        "",
        f"### Proportions (unités sur un cadratin de {upm})",
        f"- Hauteur d'x : {hauteur_x} ; hauteur de capitale : {hauteur_capitale}",
        f"- Rapport hauteur d'x / capitale : {hauteur_x / hauteur_capitale:.2f}" if hauteur_capitale else "- Rapport non calculable",
        f"- Ascendante / descendante (typo) : {os2.sTypoAscender} / {os2.sTypoDescender}, interligne {os2.sTypoLineGap}",
        f"- Graisse déclarée : {os2.usWeightClass}, chasse déclarée : {os2.usWidthClass}",
        "",
        "### Graisse et contraste (mesures approximatives sur « o »)",
        f"- Fût : {traits['fut']:.0f} ; délié : {traits['delie']:.0f} ; contraste : {traits['contraste']:.2f}",
        f"- Fût / hauteur d'x : {traits['fut'] / hauteur_x:.3f}" if hauteur_x else "",
        "",
        "### Couverture",
        f"- Glyphes : {len(police.getGlyphOrder())} ; caractères : {len(police.getBestCmap())}",
        *couverture(police),
        "",
        "### Fonctions OpenType et variation",
        f"- Fonctions : {', '.join(fonctions) or 'aucune'}",
        f"- Axes : {', '.join(axes) or 'police statique'}",
        "",
        f"### Risques de confusion (recouvrement des silhouettes, seuil {SEUIL_CONFUSION:.0%})",
    ]
    for a, b in PAIRES_CONFUSABLES:
        if all(ord(c) in police.getBestCmap() for c in a + b):
            score = similarite(police_pil, a, b)
            niveau = "**RISQUE**" if score >= SEUIL_CONFUSION else "distinct"
            lignes.append(f"- `{a}` / `{b}` : {score:.0%} · {niveau}")
    lignes += ["", "### Lettres en miroir (b/d, p/q : un reflet exact gêne les lecteurs dyslexiques)"]
    for a, b in PAIRES_MIROIRS:
        if all(ord(c) in police.getBestCmap() for c in a + b):
            score = similarite(police_pil, a, b, miroir=True)
            niveau = "**reflet quasi exact**" if score >= SEUIL_MIROIR else "formes différenciées"
            lignes.append(f"- `{a}` / reflet de `{b}` : {score:.0%} · {niveau}")
    return "\n".join(l for l in lignes if l is not None)


def main() -> None:
    parseur = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parseur.add_argument("polices", nargs="+", type=Path)
    parseur.add_argument("--rapport", type=Path)
    args = parseur.parse_args()

    texte = "# Mesures des polices analysées\n\n" + "\n\n".join(analyser(f) for f in args.polices) + "\n"
    if args.rapport:
        args.rapport.write_text(texte, encoding="utf-8")
    print(texte)


if __name__ == "__main__":
    main()
