"""Reconstruit la police Sorcelle depuis la planche retouchée.

Usage : python build.py sources/Jacquard24-Regular.ttf planche.png dist/

- Les glyphes de la planche remplacent ceux de Jacquard 24 ; les autres sont gardés.
- La chasse (largeur) de chaque lettre suit ton dessin : marges d'origine conservées.
- Sortie : trois graisses (Regular 400, SemiBold 600, Bold 700) en TTF et WOFF2, sous licence OFL 1.1.
- Les graisses s'obtiennent en épaississant chaque pixel vers la droite (1 px pour SemiBold, 2 px pour Bold),
  la chasse grandit d'autant : les approches et les contreformes restent lisibles.
- La version vient de police.json (mise à jour par release-please à chaque version publiée).
"""
import json
import os
import sys
import unicodedata

from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont, newTable
from fontTools.ttLib.tables.ttProgram import Program
from PIL import Image

from design_accents import poser, ramener
from grid import CHARSET, ECART_ACCENT_HAUT, LIGNE_ACCENT_MINUSCULE, PX, read_cell

HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(HERE, "police.json"), encoding="utf-8") as fh:
    META = json.load(fh)
FAMILY = META["nom"]
VERSION = META["version"]       # semver, ex. « 0.6.0 »


def revision(version):
    """« 0.6.1 » -> « 0.601 » : forme attendue par head.fontRevision et le nom « Version 0.601 »
    (même règle que revision_opentype dans tools/polices.py)."""
    major, minor, patch = (int(p) for p in version.split("."))
    return f"{major}.{minor}{patch:02d}"


# graisse CSS -> (nom de style, pixels ajoutés à droite)
# demi-diagonale du pont posé sur les jointures diagonales, en fraction de pixel
BRIDGE = 0.3
WEIGHTS = {400: ("Regular", 0), 600: ("SemiBold", 1), 700: ("Bold", 2)}
COPYRIGHT = ("Copyright 2023 The Soft Type Project Authors (https://github.com/scfried/soft-type-jacquard). "
             "Copyright 2026 Danaé ALBRECHT--MARTIN (https://danaedev.fr), modifications de Jacquard 24.")
CREATRICE = "Danaé ALBRECHT--MARTIN"
CENTRE_ACCENT_COMBINANT = -8    # colonne du centre d'un accent combinant (chasse nulle, au-dessus de la lettre d'avant)
ACCENTS_DESSOUS = {0x326, 0x327, 0x328}


def outline(pixels):
    """Contour fusionné des pixels : une seule forme par zone, sans joint entre les carrés.

    Chaque pixel apporte ses 4 bords orientés ; un bord partagé par deux pixels voisins
    apparaît dans les deux sens et s'annule. Les bords restants forment des boucles :
    sens horaire pour l'extérieur, antihoraire pour les trous (convention TrueType).
    Sans cette fusion, l'anticrénelage laisse un fin trait clair entre deux carrés
    qui se touchent (les « stries » visibles à petite taille ou au zoom).
    """
    edges = set()
    for c, r in pixels:
        square = [(c, r), (c, r + 1), (c + 1, r + 1), (c + 1, r)]   # sens horaire, y vers le haut
        for i in range(4):
            a, b = square[i], square[(i + 1) % 4]
            if (b, a) in edges:
                edges.discard((b, a))
            else:
                edges.add((a, b))
    starts = {}
    for a, b in edges:
        starts.setdefault(a, []).append(b)
    loops = []
    while starts:
        first = next(iter(starts))
        loop, prev, cur = [first], None, first
        while True:
            options = starts[cur]
            if len(options) == 1 or prev is None:
                nxt = options[0]
            else:
                # coin où deux pixels se touchent en diagonale : on tourne à droite
                # pour ne jamais croiser le contour
                dx, dy = cur[0] - prev[0], cur[1] - prev[1]
                right = (cur[0] + dy, cur[1] - dx)
                nxt = right if right in options else options[0]
            options.remove(nxt)
            if not options:
                del starts[cur]
            prev, cur = cur, nxt
            if cur == first and first not in starts:
                break
            if cur == first:
                break
            loop.append(cur)
        # on retire les points alignés
        pts = []
        n = len(loop)
        for i in range(n):
            p0, p1, p2 = loop[i - 1], loop[i], loop[(i + 1) % n]
            if (p1[0] - p0[0]) * (p2[1] - p1[1]) != (p1[1] - p0[1]) * (p2[0] - p1[0]):
                pts.append(p1)
        loops.append(pts)
    return loops


def diagonal_joints(pixels):
    """Coins où deux pixels se touchent seulement en diagonale (aucun voisin commun)."""
    joints = set()
    for c, r in pixels:
        if (c + 1, r + 1) in pixels and (c + 1, r) not in pixels and (c, r + 1) not in pixels:
            joints.add((c + 1, r + 1))
        if (c + 1, r - 1) in pixels and (c + 1, r) not in pixels and (c, r - 1) not in pixels:
            joints.add((c + 1, r))
    return joints


def draw_glyph(pixels):
    pen = TTGlyphPen(None)
    for pts in outline(pixels):
        pen.moveTo((pts[0][0] * PX, pts[0][1] * PX))
        for x, y in pts[1:]:
            pen.lineTo((x * PX, y * PX))
        pen.closePath()
    # Pont en losange sur chaque jointure diagonale : sans lui, deux pixels qui ne se touchent
    # que par un coin laissent un « petit trou » à l'anticrénelage (retour du test de lecture)
    half = round(PX * BRIDGE)
    for x, y in sorted(diagonal_joints(pixels)):
        cx, cy = x * PX, y * PX
        pen.moveTo((cx, cy + half))
        pen.lineTo((cx + half, cy))
        pen.lineTo((cx, cy - half))
        pen.lineTo((cx - half, cy))
        pen.closePath()
    return pen.glyph()


def add_glyph(font, cmap, char):
    """Glyphe vide pour un caractère absent de Jacquard 24, ajouté au cmap."""
    name = f"uni{ord(char):04X}"
    font.setGlyphOrder(font.getGlyphOrder() + [name])
    font["glyf"][name] = draw_glyph(set())
    font["hmtx"][name] = (0, 0)
    for table in font["cmap"].tables:
        if table.isUnicode():
            table.cmap[ord(char)] = name
    cmap[ord(char)] = name
    return name


def write_glyph(font, name, char, pixels, rsb_px):
    """Contour et chasse d'un glyphe ; un accent combinant a une chasse nulle."""
    glyph = draw_glyph(pixels)
    font["glyf"][name] = glyph
    glyph.recalcBounds(font["glyf"])
    combinant = unicodedata.category(char) == "Mn"
    font["hmtx"][name] = (0 if combinant else (max(c for c, _ in pixels) + 1 + rsb_px) * PX, glyph.xMin)


def fonction_mark(dessins):
    """Fonction `mark` en syntaxe .fea : accents combinants posés sur les lettres de la planche,
    à la même hauteur que dans les lettres composées (design_accents.py)."""
    def centre(pixels):
        xs = [c for c, _ in pixels]
        return round((min(xs) + max(xs) + 1) / 2 * PX)

    classes, bases = [], []
    for name, (char, pixels) in dessins.items():
        if unicodedata.category(char) == "Mn":
            if ord(char) == 0x328:      # ogonek : accroché à droite du pied
                classes.append(f"markClass \\{name} <anchor {(max(c for c, _ in pixels) + 1) * PX} 0> @OGONEK;")
            elif ord(char) in ACCENTS_DESSOUS:
                classes.append(f"markClass \\{name} <anchor {centre(pixels)} 0> @DESSOUS;")
            else:
                bas = min(r for _, r in pixels) * PX
                classes.append(f"markClass \\{name} <anchor {centre(pixels)} {bas}> @DESSUS;")
        elif char.isalpha():
            hauteur = max(r for _, r in pixels)
            bas = LIGNE_ACCENT_MINUSCULE if hauteur <= 16 else hauteur + ECART_ACCENT_HAUT
            corps = {p for p in pixels if p[1] >= 0}
            pied = [c for c, r in pixels if r == 0] or [c for c, _ in pixels]
            bases.append(f"  pos base \\{name} <anchor {centre(corps)} {bas * PX}> mark @DESSUS"
                         f" <anchor {centre(corps)} 0> mark @DESSOUS <anchor {(max(pied) + 1) * PX} 0> mark @OGONEK;")
    return "\n".join(classes) + "\nfeature mark {\n" + "\n".join(bases) + "\n} mark;\n"


def rename(font, weight=400):
    style, _ = WEIGHTS[weight]
    ribbi = style in ("Regular", "Bold")
    names = font["name"]
    values = {
        0: COPYRIGHT,
        1: FAMILY if ribbi else f"{FAMILY} {style}",
        2: style if ribbi else "Regular",
        3: f"{VERSION};DANAEDEV;{FAMILY}-{style}",
        4: f"{FAMILY} {style}",
        5: f"Version {revision(VERSION)}",
        6: f"{FAMILY}-{style}",
        9: CREATRICE,
        11: "https://danaedev.fr",
        12: "https://danaedev.fr",
        13: "This Font Software is licensed under the SIL Open Font License, Version 1.1.",
        14: "https://openfontlicense.org",
    }
    if not ribbi:
        values[16] = FAMILY
        values[17] = style
    # Noms Windows seulement : les entrées Mac (plateforme 1) sont obsolètes
    names.names = [n for n in names.names
                   if n.platformID != 1 and n.nameID not in values and n.nameID not in (16, 17)]
    for name_id, text in values.items():
        names.setName(text, name_id, 3, 1, 0x409)
    os2, head = font["OS/2"], font["head"]
    os2.usWeightClass = weight
    os2.fsSelection &= ~(0x01 | 0x20 | 0x40)          # ni italique, ni gras, ni regular
    os2.fsSelection |= 0x20 if style == "Bold" else 0x40   # SemiBold : style « Regular » de sa famille (nameID 2)
    head.macStyle = (head.macStyle & ~0x01) | (0x01 if style == "Bold" else 0)


def main(ttf_path, sheet_path, out_dir, weight=400):
    style, smear = WEIGHTS[weight]
    font = TTFont(ttf_path)
    img = Image.open(sheet_path).convert("RGBA")
    cmap = font.getBestCmap()
    glyf, hmtx = font["glyf"], font["hmtx"]
    dessins = {}
    for index, char in enumerate(CHARSET):
        pixels = read_cell(img, index)
        pixels |= {(c + i, r) for c, r in pixels for i in range(1, smear + 1)}
        name = cmap.get(ord(char))
        if name is None:          # nouveau caractère (ex. ✦) : on crée le glyphe
            if not pixels:
                continue
            name = add_glyph(font, cmap, char)
            rsb_px = 2
        else:
            old_glyph = glyf[name]
            old_glyph.recalcBounds(glyf)
            old_adv, _ = hmtx[name]
            rsb_px = max(2 if char.isalnum() else 0,
                         (old_adv - (old_glyph.xMax if old_glyph.numberOfContours else 0)) // PX)
        if not pixels:
            continue
        if unicodedata.category(char) == "Mn":
            xs = [c for c, _ in pixels]
            pixels = {(c + round(CENTRE_ACCENT_COMBINANT - (min(xs) + max(xs)) / 2), r) for c, r in pixels}
        dessins[name] = (char, pixels)
        write_glyph(font, name, char, pixels, rsb_px)
    # Glyphes ajoutés hors planche (glyphs_extra.json) : ex. λ pour « λLens »
    extra_path = os.path.join(HERE, "glyphs_extra.json")
    if os.path.exists(extra_path):
        with open(extra_path, encoding="utf-8") as fh:
            extra = json.load(fh)
        for char, pts in extra.items():
            pixels = {(c, r) for c, r in pts}
            pixels |= {(c + i, r) for c, r in pixels for i in range(1, smear + 1)}
            name = cmap.get(ord(char)) or add_glyph(font, cmap, char)
            write_glyph(font, name, char, pixels, 2)
    # Glyphes sans case sur la planche, appelés par les substitutions de Jacquard 24 (ccmp, locl) :
    # tirés des glyphes dessinés pour qu'aucun dessin d'origine ne reste
    par_nom = {name: pixels for name, (_, pixels) in dessins.items()}
    aigu = ramener(par_nom[cmap[0x301]])
    derives = {
        "i.loclTRK": ("i", par_nom[cmap[ord("i")]]),
        "periodcentered.loclCAT": ("·", par_nom[cmap[0xB7]]),
        "periodcentered.loclCAT.case": ("·", par_nom[cmap[0xB7]]),
        "uni004A0301": ("J", poser(par_nom[cmap[ord("J")]], aigu, "aigu", "J")),
        "uni006A0301": ("j", poser(par_nom[cmap[0x237]], aigu, "aigu", "ȷ")),
    }
    # Accents combinants après une capitale (.case) : même dessin, remonté à la hauteur des accents de capitales
    montee = max(r for _, r in par_nom[cmap[ord("H")]]) + ECART_ACCENT_HAUT - LIGNE_ACCENT_MINUSCULE
    for name in font.getGlyphOrder():
        racine, _, suffixe = name.partition(".")
        if suffixe == "case" and racine in dessins and unicodedata.category(dessins[racine][0]) == "Mn":
            derives[name] = (dessins[racine][0], {(c, r + montee) for c, r in par_nom[racine]})
    for name, (char, pixels) in derives.items():
        dessins[name] = (char, pixels)
        write_glyph(font, name, char, pixels, 2)
    # Signes mathématiques sur la chasse du + : les calculs restent alignés
    largeur = font["hmtx"][cmap[ord("+")]][0] // PX
    for char in "−×÷=<>":
        name = cmap[ord(char)]
        pixels = dessins[name][1]
        xs = [c for c, _ in pixels]
        marge = (largeur - (max(xs) - min(xs) + 1)) // 2
        pixels = {(c - min(xs) + marge, r) for c, r in pixels}
        dessins[name] = (char, pixels)
        write_glyph(font, name, char, pixels, largeur - 1 - max(c for c, _ in pixels))
    # Espace fine insécable (typographie française) : moitié de l'espace, arrondie au pixel
    if 0x202F not in cmap:
        name = add_glyph(font, cmap, chr(0x202F))
        font["hmtx"][name] = (round(font["hmtx"][cmap[32]][0] / 2 / PX) * PX, 0)
    # Crénage et ancres de Jacquard 24 visent les anciennes formes : GPOS refait avec la seule fonction mark
    del font["GPOS"]
    addOpenTypeFeaturesFromString(font, fonction_mark(dessins), tables=["GPOS"])
    # Les instructions de hinting d'origine ne correspondent plus : police sans hinting, avec le seul contrôle
    # des pertes de pixels (smart dropout), comme gftools fix-nonhinting
    for table in ("fpgm", "cvt "):
        if table in font:
            del font[table]
    for name in glyf.keys():
        g = glyf[name]
        g.recalcBounds(glyf)
        if g.numberOfContours != 0:
            g.program = Program()
            g.program.fromBytecode(b"")
    prep = newTable("prep")
    prep.program = Program()
    prep.program.fromAssembly(["PUSHW[ ]", "511", "SCANCTRL[ ]", "PUSHB[ ]", "4", "SCANTYPE[ ]"])
    font["prep"] = prep
    gasp = newTable("gasp")
    gasp.version, gasp.gaspRange = 1, {0xFFFF: 0x000F}
    font["gasp"] = gasp
    font["maxp"].maxStackElements = max(font["maxp"].maxStackElements, 1)
    # Zone de rendu Windows = boîte englobante réelle des glyphes
    os2 = font["OS/2"]
    os2.usWinAscent = max(g.yMax for g in glyf.values() if g.numberOfContours)
    os2.usWinDescent = -min(g.yMin for g in glyf.values() if g.numberOfContours)
    os2.recalcAvgCharWidth(font)
    rename(font, weight)
    font["head"].fontRevision = float(revision(VERSION))
    os.makedirs(out_dir, exist_ok=True)
    ttf_out = os.path.join(out_dir, f"{FAMILY}-{style}.ttf")
    font.save(ttf_out)
    font.flavor = "woff2"
    font.save(os.path.join(out_dir, f"{FAMILY}-{style}.woff2"))
    print(f"-> {ttf_out} (+ .woff2)")


def build_all(ttf_path, sheet_path, out_dir):
    for weight in WEIGHTS:
        main(ttf_path, sheet_path, out_dir, weight)


if __name__ == "__main__":
    build_all(sys.argv[1], sys.argv[2], sys.argv[3])
