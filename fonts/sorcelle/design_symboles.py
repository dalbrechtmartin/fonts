"""Dessine les 28 symboles et signes de ponctuation de GF Latin Core encore hérités de Jacquard 24 (1.0).

Usage : python design_symboles.py planche.png   (après design_accents.py)

Règles (documentation/specification.md) : même poids que la ponctuation de la 0.6 (traits de 3 px, points carrés),
symboles monétaires tirés des lettres de la planche, ¡ ¿ retournés sous la ligne de base, guillemets tirés de ’ , « ».
"""
import sys

from PIL import Image

from design_accents import centre, decaler, fut, motif, rectangle
from design_caps import write_cell
from grid import CHARSET, read_cell

TRAIT = 3       # épaisseur des signes (+, =, /, parenthèses)


def miroir(pixels):
    """Symétrie gauche-droite."""
    largeur = max(x for x, _ in pixels)
    return {(largeur - x, y) for x, y in pixels}


def retourner(pixels):
    """Rotation d'un demi-tour (¡ ¿ ‘)."""
    xs, ys = [x for x, _ in pixels], [y for _, y in pixels]
    return {(max(xs) + min(xs) - x, max(ys) + min(ys) - y) for x, y in pixels}


def cote_a_cote(gauche, droite, ecart):
    return gauche | decaler(droite, dx=max(x for x, _ in gauche) + 1 + ecart - min(x for x, _ in droite))


def barre_verticale(pixels, rangs):
    """Trait de 3 px au centre du glyphe, sur les lignes données (barre de $ et ¢)."""
    milieu = round(centre(pixels))
    return {(x, y) for x in range(milieu - 1, milieu + 2) for y in rangs}


def symboles(p):
    out = {}
    out["\\"] = miroir(p["/"])
    haut_crochet, bas_crochet = max(y for _, y in p["["]), min(y for _, y in p["["])
    out["|"] = rectangle(0, bas_crochet, TRAIT - 1, haut_crochet)
    # Bec central en pointe, sur trois lignes de diagonale : sans lui, { se lit i (essai OCR)
    accolade = motif(
        "......###",
        "....#####",
        *["...###..."] * 10,
        "..###....",
        ".###.....",
        "###......",
        ".###.....",
        "..###....",
        *["...###..."] * 10,
        "....#####",
        "......###")
    out["{"] = decaler(accolade, dy=bas_crochet)
    out["}"] = miroir(out["{"])
    out["~"] = decaler(motif(".####.....##",
                             "######...###",
                             "###...######",
                             "##.....####."), dy=8)

    # ¡ ¿ : ! et ? retournés, le haut sur la hauteur d'x
    hauteur_x = max(y for _, y in p["x"])
    for droit, inverse in (("!", "¡"), ("?", "¿")):
        tourne = retourner(p[droit])
        out[inverse] = decaler(tourne, dy=hauteur_x - max(y for _, y in tourne))

    # Signes mathématiques, alignés sur le + (barre sur les lignes 9 à 11)
    barre = {q for q in p["+"] if 9 <= q[1] <= 11}
    out["−"] = barre
    tige = {q for q in p["+"] if q[1] not in range(9, 12)}
    x0, x1 = min(x for x, _ in tige), max(x for x, _ in tige)
    out["÷"] = barre | rectangle(x0, 14, x1, 16) | rectangle(x0, 4, x1, 6)
    croix = set()
    for i in range(11):
        croix |= {(i + j, 5 + i) for j in range(TRAIT)} | {(i + j, 15 - i) for j in range(TRAIT)}
    out["×"] = decaler(croix, dx=2)
    out["·"] = decaler(motif("####", "####", "####", "####"), dy=7)
    out["•"] = decaler(motif(".####.", "######", "######", "######", "######", ".####."), dy=6)
    out["°"] = decaler(motif(".#####.", "##...##", "##...##", "##...##", ".#####."),
                       dy=max(y for _, y in p["0"]) - 4)

    # Guillemets simples et anglais, tirés de « » ’ ,
    gauche = {q for q in p["«"] if q[0] <= min(x for x, _ in p["«"]) + 6}
    out["‹"] = gauche
    out["›"] = miroir(gauche)
    apostrophe = p["’"]
    ouvrant = retourner(apostrophe)
    out["‘"] = ouvrant
    out["“"] = cote_a_cote(ouvrant, ouvrant, 2)
    out["”"] = cote_a_cote(apostrophe, apostrophe, 2)
    out["‚"] = p[","]
    out["„"] = cote_a_cote(p[","], p[","], 2)

    # Monnaies
    hauteur_s = max(y for _, y in p["S"])
    out["$"] = p["S"] | barre_verticale(p["S"], [*range(hauteur_s + 1, hauteur_s + 4), -1, -2, -3])
    hauteur_c = max(y for _, y in p["c"])
    out["¢"] = p["c"] | barre_verticale(p["c"], [*range(hauteur_c + 1, hauteur_c + 4), -1, -2, -3])
    euro = decaler(p["C"], dx=3)
    out["€"] = euro | rectangle(0, 14, 12, 15) | rectangle(0, 9, 12, 10)
    y0, y1 = fut(p["Y"], 2, 10)
    out["¥"] = p["Y"] | rectangle(y0 - 4, 9, y1 + 4, 10) | rectangle(y0 - 4, 13, y1 + 4, 14)
    out["£"] = motif(
        "......#######..",
        "....##########.",
        "...####....####",
        "...####.....###",
        "..####......###",
        "..####.........",
        "..####.........",
        "..####.........",
        "..####.........",
        "..####.........",
        "##########.....",
        "##########.....",
        "..####.........",
        "..####.........",
        "..####.........",
        "..####.........",
        "..####.........",
        "..####.........",
        "..####.........",
        "..####.........",
        ".####..........",
        ".####......###.",
        "#####......###.",
        "###############",
        "###############")

    # ™ : T et M en petites capitales de 9 px, en haut de la capitale
    t = motif("########", "########", *["...##..."] * 7)
    m = motif("##.....##", "###...###", "####.####", "##.###.##", "##..#..##", *["##.....##"] * 4)
    out["™"] = decaler(cote_a_cote(t, m, 1), dy=hauteur_s - 8)
    # ® : anneau du © avec un R
    anneau = {q for q in p["©"] if not (5 <= q[0] <= 19 and 3 <= q[1] <= 17)}
    r = motif("#######..",
              "###..###.",
              "###...###",
              "###...###",
              "###..###.",
              "#######..",
              "###.###..",
              "###..###.",
              "###...###",
              "###...###",
              "###...###")
    gauche_anneau = min(x for x, _ in anneau)
    out["®"] = anneau | decaler(r, dx=gauche_anneau + 8, dy=5)
    out["¶"] = motif(
        ".##########",
        "###########",
        "#######.##.",
        "#######.##.",
        "#######.##.",
        "#######.##.",
        ".######.##.",
        "...####.##.",
        *["....###.##."] * 17)
    return out


def main(chemin_planche):
    img = Image.open(chemin_planche).convert("RGBA")
    planche = {car: read_cell(img, rang) for rang, car in enumerate(CHARSET)}
    dessins = {car: decaler(pix, dx=1 - min(x for x, _ in pix)) for car, pix in symboles(planche).items()}
    for rang, car in enumerate(CHARSET):
        if car in dessins:
            write_cell(img, rang, dessins[car])
    img.save(chemin_planche)
    print(f"{len(dessins)} symboles dessinés sur {chemin_planche}")


if __name__ == "__main__":
    main(sys.argv[1])
