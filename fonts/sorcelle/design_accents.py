"""Dessine les accents de Sorcelle et compose les lettres accentuées de GF Latin Core (0.7).

Usage : python design_accents.py planche.png   (après design_caps.py et design_lower.py)

Les lettres de base sont relues sur la planche (retouches Aseprite comprises), puis chaque lettre composée est écrite
dans sa case. Règles (documentation/specification.md) :
- accents des minuscules à partir de la ligne 21, des capitales et des hampes 3 lignes au-dessus de la lettre ;
- aigu, grave, circonflexe, tréma et cédille repris de é è ê ë ç (validés en 0.6), les autres dessinés au même gabarit ;
- virgule souscrite pour le roumain et le letton, caron en apostrophe sur ď ľ ť Ľ.
"""
import sys
import unicodedata

from PIL import Image

from design_caps import ligature, write_cell
from grid import CHARSET, ECART_ACCENT_HAUT, LIGNE_ACCENT_MINUSCULE, read_cell


def motif(*lignes):
    """Pixels d'un dessin en texte (« # » = pixel), première ligne en haut, dernière ligne en y = 0."""
    return {(x, len(lignes) - 1 - y) for y, ligne in enumerate(lignes) for x, car in enumerate(ligne) if car == "#"}


def decaler(pixels, dx=0, dy=0):
    return {(x + dx, y + dy) for x, y in pixels}


def ramener(pixels, bas=0):
    """Colonne la plus à gauche en 0, ligne la plus basse en `bas`."""
    return decaler(pixels, -min(x for x, _ in pixels), bas - min(y for _, y in pixels))


def centre(pixels):
    xs = [x for x, _ in pixels]
    return (min(xs) + max(xs)) / 2


def haut(pixels):
    return max(y for _, y in pixels)


def fut(pixels, y0, y1, droite=False):
    """Colonnes du fût le plus à gauche (ou à droite) entièrement rempli entre les lignes y0 et y1."""
    pleines = sorted(x for x in {x for x, _ in pixels} if all((x, y) in pixels for y in range(y0, y1 + 1)))
    groupes = [[pleines[0]]]
    for x in pleines[1:]:
        if x == groupes[-1][-1] + 1:
            groupes[-1].append(x)
        else:
            groupes.append([x])
    groupe = groupes[-1] if droite else groupes[0]
    return groupe[0], groupe[-1]


def rectangle(x0, y0, x1, y1):
    return {(x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)}


def oblique(xa, ya, xb, yb):
    """Trait oblique de 2 px de large de (xa, ya) à (xb, yb)."""
    pas = max(abs(xb - xa), abs(yb - ya))
    points = {(round(xa + (xb - xa) * i / pas), round(ya + (yb - ya) * i / pas)) for i in range(pas + 1)}
    return points | decaler(points, dx=1)


# --- Accents ------------------------------------------------------------------------------------

def accents(planche):
    """{nom: pixels} ; accents du dessus avec leur ligne du bas en y = 0, accents du dessous sous la ligne 0."""
    def dessus(car, base):
        return ramener({p for p in planche[car] - planche[base] if p[1] >= 18})

    circonflexe = dessus("ê", "e")
    cedille = {p for p in planche["ç"] if p[1] < 0}
    return {
        "aigu": dessus("é", "e"),
        "grave": dessus("è", "e"),
        "circonflexe": circonflexe,
        "trema": dessus("ë", "e"),
        "caron": {(x, haut(circonflexe) - y) for x, y in circonflexe},
        "breve": motif("##......##",
                       "###....###",
                       ".########.",
                       "..######.."),
        "point": motif("####", "####", "####", "####"),
        "rond": motif(".####.",
                      "##..##",
                      "##..##",
                      ".####."),
        "tilde": motif(".###....##",
                       "#####..###",
                       "###..#####",
                       "##....###."),
        "macron": motif("##########", "##########", "##########"),
        "double_aigu": motif("....###..###",
                             "...###..###.",
                             "..###..###..",
                             ".###..###..."),
        "virgule_haut": motif(".##",
                              "##.",
                              "###",
                              "###"),
        "cedille": decaler(cedille, dx=-min(x for x, _ in cedille)),
        "ogonek": decaler(motif("..##",
                                ".##.",
                                "##..",
                                "##..",
                                ".###"), dy=-5),
        "virgule": decaler(motif("###",
                                 "###",
                                 ".##",
                                 "##."), dy=-5),
        "apostrophe": motif("####",
                            "####",
                            "####",
                            "..##",
                            ".##."),
    }


DESSOUS = {"cedille", "ogonek", "virgule"}
COMBINANTS = {0x300: "grave", 0x301: "aigu", 0x302: "circonflexe", 0x303: "tilde", 0x304: "macron",
              0x306: "breve", 0x307: "point", 0x308: "trema", 0x30A: "rond", 0x30B: "double_aigu",
              0x30C: "caron", 0x312: "virgule_haut", 0x326: "virgule", 0x327: "cedille", 0x328: "ogonek"}
ACCENTS_SEULS = {"^": "circonflexe", "`": "grave", "¨": "trema", "¯": "macron", "´": "aigu", "¸": "cedille",
                 "ˆ": "circonflexe", "ˇ": "caron", "˘": "breve", "˙": "point", "˚": "rond", "˛": "ogonek",
                 "˜": "tilde", "˝": "double_aigu"}
# Virgule souscrite malgré la décomposition Unicode en cédille (letton) ; ģ : virgule retournée au-dessus
VIRGULE_SOUSCRITE = set("ĶķĻļŅņŖŗĢ")
CARON_APOSTROPHE = set("ďľťĽ")


def accent_seul(accent, nom):
    """Accent sans lettre (spacing ou combinant) : à hauteur de minuscule, approche gauche de 1 px."""
    return decaler(accent, dx=1 - min(x for x, _ in accent),
                   dy=0 if nom in DESSOUS else LIGNE_ACCENT_MINUSCULE)


def poser(base, accent, nom, lettre):
    """Lettre de base + accent, centré au-dessus ou au-dessous."""
    if nom in DESSOUS:
        if nom == "ogonek":     # accroché à droite du pied
            droite = max(x for x, y in base if y == 0)
            return base | decaler(accent, dx=droite - max(x for x, _ in accent))
        return base | decaler(accent, dx=round(centre({p for p in base if p[1] >= 0}) - centre(accent)))
    hauteur = haut(base)
    bas = LIGNE_ACCENT_MINUSCULE if hauteur <= 16 else hauteur + ECART_ACCENT_HAUT
    # l et L : accent centré sur la tête du fût, pas sur tout le pied
    reference = {p for p in base if p[1] >= hauteur - 2} if lettre in "lL" else {p for p in base if p[1] >= 0}
    return base | decaler(accent, dx=round(centre(reference) - centre(accent)), dy=bas)


# --- Lettres entières -----------------------------------------------------------------------------

def lettres_entieres(p):
    """Lettres sans décomposition Unicode, construites à partir des lettres de la planche."""
    out = {"ı": {q for q in p["i"] if q[1] <= 16}, "ȷ": {q for q in p["j"] if q[1] <= 16}}

    def barre(lettre, y, y0, y1, depasse_gauche=2, depasse_droite=2, droite=False):
        x0, x1 = fut(p[lettre], y0, y1, droite)
        return p[lettre] | rectangle(x0 - depasse_gauche, y, x1 + depasse_droite, y + 1)

    out["Đ"] = out["Ð"] = barre("D", 11, 5, 20, depasse_droite=3)
    out["đ"] = barre("d", 20, 17, 21)
    xs = [x for x, _ in p["H"]]
    out["Ħ"] = p["H"] | rectangle(min(xs), 18, max(xs), 19)
    out["ħ"] = barre("h", 20, 17, 21)
    for lettre in "Ll":
        x0, x1 = fut(p[lettre], 5, 20)
        out["Ł" if lettre == "L" else "ł"] = p[lettre] | oblique(x0 - 3, 8, x1 + 2, 16)
    for lettre, barree in (("O", "Ø"), ("o", "ø")):
        xs = [x for x, _ in p[lettre]]
        out[barree] = p[lettre] | oblique(min(xs), -1, max(xs) - 1, haut(p[lettre]) + 1)

    # Þ : fût du P sur toute la hauteur, panse descendue de 5 lignes
    gauche = min(x for x, _ in p["P"])
    out["Þ"] = ({q for q in p["P"] if q[0] <= gauche + 4}
                | decaler({q for q in p["P"] if q[0] > gauche + 4 and q[1] >= 10}, dy=-5))
    # þ : p avec la hampe du b
    xp, _ = fut(p["p"], 2, 13)
    xb, _ = fut(p["b"], 17, 21)
    hampe = decaler({q for q in p["b"] if q[1] >= 17 and q[0] <= xb + 3}, dx=xp - xb)
    out["þ"] = {q for q in p["p"] if not (q[1] >= 15 and q[0] < xp)} | hampe

    # Ŋ ŋ : jambe droite prolongée sous la ligne de base en crochet, comme le j
    for lettre, eng in (("N", "Ŋ"), ("n", "ŋ")):
        x0, x1 = fut(p[lettre], 3, 9, droite=True)
        corps = {q for q in p[lettre] if not (q[1] <= 1 and q[0] >= x0 - 2)}
        crochet = (rectangle(x0, -4, x1, 1) | rectangle(x0 - 5, -4, x0 - 4, -3)
                   | rectangle(x0 - 5, -5, x1 - 1, -5) | rectangle(x0 - 4, -6, x1 - 2, -6))
        out[eng] = corps | crochet

    # Λ : le A sans sa barre (lignes 8 et 9 reprises des jambes voisines)
    out["Λ"] = ({q for q in p["A"] if q[1] not in (8, 9)} | {(x, 9) for x, y in p["A"] if y == 10}
               | {(x, 8) for x, y in p["A"] if y == 7})
    out["Ĳ"] = ligature(p["I"], p["J"], -1)
    out["ĳ"] = ligature(p["i"], p["j"], -1)
    out["ð"] = {q for q in p["o"] if q[1] <= 11} | decaler(motif(
        "..###.........",
        "...###.##.....",
        "....######....",
        "....#######...",
        "...##...####..",
        ".........####.",
        "..........####",
        "....##########",
        "..############",
        ".####.....####",
        "####......####",
        "####......####",
        "####......####"), dx=min(x for x, _ in p["o"]), dy=12)
    out["ß"] = motif(
        ".....######......",
        "...##########....",
        "..####....####...",
        "..####.....####..",
        "..####.....####..",
        "..####.....####..",
        "..####....####...",
        "..####..####.....",
        "..####..####.....",
        "..####...######..",
        "..####.....#####.",
        "..####......####.",
        "..####......####.",
        "..####......####.",
        "..####......####.",
        "..####......####.",
        "..####......####.",
        "..####......####.",
        "..####......####.",
        "..####.....#####.",
        "..####....#####..",
        "..####.#######...",
        "..####.######....",
        "########.........",
        "########.........")
    # ẞ ≠ B : angle vif en haut à droite, diagonale qui redescend vers le fût, bas ouvert
    out["ẞ"] = motif(
        "#################...",
        "#################...",
        "#####........#####..",
        "#####.......#####...",
        "#####......#####....",
        "#####.....#####.....",
        "#####....#####......",
        "#####...#########...",
        "#####.......######..",
        "#####.........#####.",
        "#####..........#####",
        "#####..........#####",
        "#####..........#####",
        "#####..........#####",
        "#####..........#####",
        "#####..........#####",
        "#####..........#####",
        "#####.........#####.",
        "#####........######.",
        "#####.......######..",
        "#####.....######....",
        "#####...######......",
        "#####...####........",
        "#######.............",
        "#######.............")
    souligne = ["#######", "#######"]
    out["ª"] = decaler(motif(".#####.", "##...##", "....###", ".######", "##...##", "##..###", ".######",
                             ".......", *souligne), dy=15)
    out["º"] = decaler(motif(".#####.", "##...##", "##...##", "##...##", "##...##", "##...##", ".#####.",
                             ".......", *souligne), dy=15)
    return out


# --- Planche --------------------------------------------------------------------------------------

def composer(planche):
    acc = accents(planche)
    dessins = lettres_entieres(planche)
    planche = {**planche, **dessins}
    for car, nom in ACCENTS_SEULS.items():
        dessins[car] = accent_seul(acc[nom], nom)
    for code, nom in COMBINANTS.items():
        dessins[chr(code)] = accent_seul(acc[nom], nom)
    for car in CHARSET:
        if car in dessins or car in ORIGINAUX or not car.isalpha():
            continue
        decomposition = unicodedata.decomposition(car).split()
        if len(decomposition) != 2:
            continue
        lettre, code = chr(int(decomposition[0], 16)), int(decomposition[1], 16)
        nom = COMBINANTS[code]
        if car in VIRGULE_SOUSCRITE:
            nom = "virgule"
        elif car == "ģ":
            nom = "virgule_haut"
        if car in CARON_APOSTROPHE:
            base = planche[lettre]
            _, x1 = fut(base, haut(base) - 5, haut(base) - 1)
            dessins[car] = base | decaler(acc["apostrophe"], dx=x1 + 2, dy=haut(base) - haut(acc["apostrophe"]))
            continue
        if nom not in DESSOUS and lettre in "ij":
            lettre = {"i": "ı", "j": "ȷ"}[lettre]
        dessins[car] = poser(planche[lettre], acc[nom], nom, lettre)
    return dessins


ORIGINAUX = CHARSET[:CHARSET.index("✦") + 1]   # cases de la 0.6, dessinées par design_caps et design_lower


def main(chemin_planche):
    img = Image.open(chemin_planche).convert("RGBA")
    planche = {car: read_cell(img, rang) for rang, car in enumerate(ORIGINAUX)}
    dessins = composer(planche)
    for rang, car in enumerate(CHARSET):
        if car in dessins and car not in ORIGINAUX:
            write_cell(img, rang, dessins[car])
    img.save(chemin_planche)
    print(f"{len([c for c in dessins if c not in ORIGINAUX])} glyphes dessinés sur {chemin_planche}")


if __name__ == "__main__":
    main(sys.argv[1])
