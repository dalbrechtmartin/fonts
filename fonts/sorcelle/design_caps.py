"""Dessine les capitales lisibles de Sorcelle (et l'étoile ✦) directement sur la planche.

Usage : python design_caps.py sources/Jacquard24-Regular.ttf planche.png

Principes (lisibilité) :
- squelette de capitales romaines, reconnaissable lettre par lettre ;
- habillage « lombarde arrondie » (version 0.2) : fûts de 5 px, déliés de 2 px, panses rondes,
  têtes de fût en crosse, empattements plats, sans filet ;
- paires à risque différenciées : I (empattements) / l / 1, O / 0 / Q, M / N / H, U / V, S / 5, B / 8.
Les capitales accentuées reprennent les accents de Jacquard 24, recentrés sur la nouvelle lettre.
"""
import sys

from fontTools.ttLib import TTFont
from PIL import Image

from extract import glyph_pixels
from grid import ASC_PX, CELL_W, CHARSET, DESC_PX, ORIGIN_X, cell_origin

CAP = 25          # hauteur des capitales, en pixels (750 / 30)
TOP = CAP - 1     # dernière ligne de la capitale
STEM = 5          # fût épais
HAIR = 2          # délié

# Style d'habillage (modifiable par variants.py) ; le squelette des lettres reste le même
STYLE = {
    "filet": False,      # filet parallèle relié au fût (signature de Jacquard 24, retiré en 0.2)
    "top": "curl",       # tête de fût : cut (biseau), flag (drapeau gothique), curl (crosse), flat
    "foot": "slab",      # pied : spur (éperon), diamond (pointe), slab (empattement plat), flat
    "bowl": "round",     # panses : octagon (brisées) ou round (arrondies, esprit lombard)
    "chamfer": 1.0,      # coefficient des pans coupés des panses
}


class Glyph:
    def __init__(self):
        self.px = set()

    def fill(self, x, y):
        self.px.add((int(x), int(y)))

    def rect(self, x0, y0, x1, y1):
        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                self.fill(x, y)

    def erase(self, pts):
        self.px -= set(pts)

    def stem(self, x, y0=0, y1=TOP, w=None, top="cut", foot="spur"):
        w = w or STEM
        top = STYLE["top"] if top == "cut" else top
        foot = STYLE["foot"] if foot == "spur" else foot
        self.rect(x, y0, x + w - 1, y1)
        if top == "cut":    # biseau montant de gauche à droite, comme le l de Jacquard
            self.erase([(x + i, y1 - j) for j in range(w - 1) for i in range(w - 1 - j)])
        elif top == "flag":  # drapeau : losange qui déborde à gauche, typique de la textura
            self.erase([(x, y1)])
            self.rect(x - 1, y1 - 2, x - 1, y1 - 1)
            self.fill(x - 2, y1 - 2)
        elif top == "curl":  # crosse : petit crochet qui retombe à gauche
            self.rect(x - 3, y1, x - 1, y1)
            self.rect(x - 3, y1 - 2, x - 3, y1 - 1)
        if y0 == 0:
            if foot == "spur":   # éperon : pied élargi puis arrondi
                self.rect(x - 1, 1, x + w, 2)
                self.erase([(x, 0)])
            elif foot == "diamond":  # pied en pointe
                self.rect(x - 1, 1, x + w, 1)
                self.erase([(x, 0), (x + w - 1, 0)])
            elif foot == "slab":     # empattement plat
                self.rect(x - 2, 0, x + w + 1, 1)

    def inline(self, x, y0=5, y1=TOP - 5):
        """Filet fin parallèle au fût : la signature graphique de Jacquard 24.
        Relié au fût en haut et en bas pour ne jamais être lu comme un I isolé."""
        if not STYLE["filet"]:
            return
        self.rect(x - 4, y0, x - 3, y1)
        self.rect(x - 2, y0, x - 1, y0)
        self.rect(x - 2, y1, x - 1, y1)

    def hbar(self, x0, x1, y, h=None):
        h = h or HAIR
        self.rect(x0, y, x1, y + h - 1)

    def diag(self, xa, ya, xb, yb, w):
        """Diagonale épaisse (épaisseur horizontale w), de (xa, ya) à (xb, yb)."""
        step = 1 if yb >= ya else -1
        for y in range(ya, yb + step, step):
            t = (y - ya) / (yb - ya) if yb != ya else 0
            x = round(xa + t * (xb - xa))
            for i in range(w):
                self.fill(x + i, y)

    def octagon(self, x0, y0, x1, y1, c, side=None, cap=None, open_right=None):
        """Panse : flancs épais, haut et bas fins. open_right=(ya, yb) ouvre le flanc droit.
        Forme brisée (octogone) ou arrondie selon STYLE["bowl"]."""
        side, cap = side or STEM, cap or HAIR
        c = round(c * STYLE["chamfer"])

        def inside(x, y, a0, b0, a1, b1, ch):
            if a1 < a0 or b1 < b0:
                return False
            if STYLE["bowl"] == "round":
                cx, cy = (a0 + a1) / 2, (b0 + b1) / 2
                rx, ry = (a1 - a0) / 2 + 0.5, (b1 - b0) / 2 + 0.5
                # super-ellipse : arrondie mais pas trop molle, pour rester pixel
                return abs((x - cx) / rx) ** 2.6 + abs((y - cy) / ry) ** 2.6 <= 1
            return (a0 <= x <= a1 and b0 <= y <= b1 and (x - a0) + (y - b0) >= ch and (a1 - x) + (y - b0) >= ch
                    and (x - a0) + (b1 - y) >= ch and (a1 - x) + (b1 - y) >= ch)
        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                if inside(x, y, x0, y0, x1, y1, c) and not inside(x, y, x0 + side, y0 + cap, x1 - side, y1 - cap, max(0, c - 2)):
                    if open_right and x > (x0 + x1) // 2 and open_right[0] <= y <= open_right[1]:
                        continue
                    self.fill(x, y)

    def width(self):
        return max(x for x, _ in self.px) + 1 if self.px else 0


def cap_glyphs():
    G = {}

    g = Glyph()                                     # A : pointe nette, barre basse
    g.diag(7, TOP, 0, 0, HAIR + 1)
    g.diag(8, TOP, 14, 0, STEM)
    g.rect(7, TOP - 1, 10, TOP)
    g.hbar(3, 13, 8)
    g.rect(-1, 0, 4, 1)
    g.rect(12, 0, 19, 1)
    G["A"] = g

    g = Glyph()                                     # B : deux panses, la haute plus petite
    g.stem(0, foot="flat")
    g.octagon(-10, 12, 14, TOP, 4)
    g.octagon(-10, 0, 16, 13, 4)
    g.erase([(x, y) for x, y in list(g.px) if x < 0])
    g.rect(0, 0, 3, TOP)
    g.inline(0)
    G["B"] = g

    g = Glyph()                                     # C : octogone ouvert, terminaison en ergot
    g.octagon(0, 0, 16, TOP, 6, open_right=(6, 18))
    g.rect(14, 17, 16, 20)
    g.rect(15, 4, 17, 7)
    g.inline(0, 8, TOP - 8)
    G["C"] = g

    g = Glyph()                                     # D
    g.octagon(-12, 0, 17, TOP, 7)
    g.erase([(x, y) for x, y in list(g.px) if x < 0])
    g.stem(0, top="flat", foot="spur")
    g.inline(0)
    G["D"] = g

    g = Glyph()                                     # E : barres fines, empattements verticaux
    g.stem(0)
    g.hbar(0, 14, TOP - 1)
    g.rect(13, TOP - 5, 14, TOP)
    g.hbar(0, 10, 11)
    g.rect(9, 9, 10, 14)
    g.hbar(0, 15, 0)
    g.rect(14, 0, 15, 5)
    g.inline(0)
    G["E"] = g

    g = Glyph()                                     # F
    g.stem(0)
    g.hbar(0, 14, TOP - 1)
    g.rect(13, TOP - 5, 14, TOP)
    g.hbar(0, 10, 11)
    g.rect(9, 9, 10, 14)
    g.inline(0)
    G["F"] = g

    g = Glyph()                                     # G : C + éperon et barre rentrante
    g.octagon(0, 0, 17, TOP, 6, open_right=(10, 18))
    g.rect(15, 18, 17, 21)
    g.rect(14, 0, 17, 11)
    g.hbar(9, 17, 10)
    g.inline(0, 8, TOP - 8)
    G["G"] = g

    g = Glyph()                                     # H : barre fine à mi-hauteur
    g.stem(0)
    g.stem(13)
    g.hbar(4, 13, 12)
    g.inline(0)
    G["H"] = g

    g = Glyph()                                     # I : empattements des deux côtés (≠ l, 1)
    g.rect(3, 0, 6, TOP)
    g.hbar(0, 9, TOP - 1)
    g.hbar(0, 9, 0)
    G["I"] = g

    g = Glyph()                                     # J : crochet bas à gauche
    g.rect(8, 5, 11, TOP)
    g.hbar(4, 13, TOP - 1)
    g.octagon(0, 0, 11, 9, 4, open_right=None)
    g.erase([(x, y) for x in range(12) for y in range(5, 10) if x < 8])
    g.rect(0, 4, 3, 7)
    G["J"] = g

    g = Glyph()                                     # K : bras fin, jambe épaisse
    g.stem(0)
    g.diag(4, 11, 13, TOP, HAIR + 1)
    g.diag(5, 13, 14, 0, STEM)
    g.rect(11, TOP - 1, 15, TOP)
    g.rect(13, 0, 18, 1)
    g.inline(0)
    G["K"] = g

    g = Glyph()                                     # L
    g.stem(0)
    g.hbar(0, 14, 0)
    g.rect(13, 0, 14, 6)
    g.inline(0)
    G["L"] = g

    g = Glyph()                                     # M : V central qui descend bas (≠ N, H)
    g.stem(0)
    g.stem(18)
    g.diag(3, TOP, 10, 4, STEM)
    g.diag(12, 4, 18, TOP, HAIR + 1)
    g.inline(0)
    G["M"] = g

    g = Glyph()                                     # N : diagonale épaisse
    g.stem(0, top="flat")
    g.stem(14)
    g.diag(2, TOP, 14, 2, STEM)
    g.inline(0)
    G["N"] = g

    g = Glyph()                                     # O : octogone plein (≠ 0, plus étroit)
    g.octagon(0, 0, 19, TOP, 7)
    g.inline(0, 8, TOP - 8)
    G["O"] = g

    g = Glyph()                                     # P : panse haute
    g.stem(0)
    g.octagon(-10, 10, 16, TOP, 5)
    g.erase([(x, y) for x, y in list(g.px) if x < 0])
    g.rect(0, 10, 3, TOP)
    g.inline(0)
    G["P"] = g

    g = Glyph()                                     # Q : queue qui sort sous la ligne de base
    g.octagon(0, 0, 19, TOP, 7)
    g.diag(10, 7, 18, -4, STEM - 1)
    g.inline(0, 8, TOP - 8)
    G["Q"] = g

    g = Glyph()                                     # R : P + jambe
    g.stem(0)
    g.octagon(-10, 10, 16, TOP, 5)
    g.erase([(x, y) for x, y in list(g.px) if x < 0])
    g.rect(0, 10, 3, TOP)
    g.diag(8, 11, 15, 0, STEM)
    g.rect(13, 0, 19, 1)
    g.inline(0)
    G["R"] = g

    g = Glyph()                                     # S : épine diagonale épaisse (≠ 5)
    g.hbar(4, 15, TOP - 1)
    g.rect(14, TOP - 6, 16, TOP)
    g.octagon(0, 12, 8, TOP, 3, side=STEM, cap=HAIR)
    g.erase([(x, y) for x in range(5, 9) for y in range(12, TOP - 1)])
    g.diag(2, 15, 12, 8, STEM)
    g.octagon(8, 0, 16, 12, 3, side=STEM, cap=HAIR)
    g.erase([(x, y) for x in range(8, 12) for y in range(2, 12)])
    g.hbar(0, 12, 0)
    g.rect(0, 0, 2, 6)
    G["S"] = g

    g = Glyph()                                     # T
    g.hbar(0, 17, TOP - 1)
    g.rect(0, TOP - 5, 1, TOP)
    g.rect(16, TOP - 5, 17, TOP)
    g.stem(7, top="flat")
    G["T"] = g

    g = Glyph()                                     # U : fût droit qui descend jusqu'à l'éperon (≠ V)
    g.stem(0, y0=7)
    g.stem(14, top="cut")
    g.octagon(0, 0, 17, 14, 5)
    g.erase([(x, y) for x in range(4, 14) for y in range(2, 15)])
    G["U"] = g

    g = Glyph()                                     # V : pointe basse
    g.diag(0, TOP, 7, 0, STEM)
    g.diag(16, TOP, 9, 0, HAIR + 1)
    g.rect(7, 0, 10, 1)
    g.rect(-1, TOP - 1, 5, TOP)
    g.rect(14, TOP - 1, 19, TOP)
    G["V"] = g

    g = Glyph()                                     # W : double V
    g.diag(0, TOP, 5, 0, STEM)
    g.diag(12, 18, 7, 0, HAIR)
    g.diag(12, 18, 17, 0, STEM)
    g.diag(24, TOP, 19, 0, HAIR + 1)
    g.rect(-1, TOP - 1, 5, TOP)
    g.rect(22, TOP - 1, 26, TOP)
    G["W"] = g

    g = Glyph()                                     # X
    g.diag(0, TOP, 14, 0, STEM)
    g.diag(15, TOP, 1, 0, HAIR)
    g.rect(-1, TOP - 1, 5, TOP)
    g.rect(12, TOP - 1, 17, TOP)
    g.rect(-1, 0, 4, 1)
    g.rect(11, 0, 18, 1)
    G["X"] = g

    g = Glyph()                                     # Y
    g.diag(0, TOP, 7, 12, STEM)
    g.diag(16, TOP, 9, 12, HAIR + 1)
    g.stem(7, y0=0, y1=12, top="flat")
    g.rect(-1, TOP - 1, 5, TOP)
    g.rect(14, TOP - 1, 19, TOP)
    G["Y"] = g

    g = Glyph()                                     # Z : diagonale épaisse, barres fines
    g.hbar(1, 15, TOP - 1)
    g.rect(0, TOP - 5, 1, TOP)
    g.diag(12, TOP - 2, 1, 2, STEM)
    g.hbar(0, 16, 0)
    g.rect(15, 0, 16, 5)
    G["Z"] = g

    g = Glyph()                                     # x minuscule : croix nette (celui de Jacquard se lit « r »)
    xh = 16                                         # dernière ligne des minuscules (510 / 30 = 17 lignes)
    g.diag(0, xh, 11, 0, STEM)
    g.diag(12, xh, 1, 0, HAIR)
    g.rect(-1, xh - 1, 4, xh)
    g.rect(10, xh - 1, 14, xh)
    g.rect(-1, 0, 3, 1)
    g.rect(9, 0, 15, 1)
    G["x"] = g

    g = Glyph()                                     # ✦ étoile à quatre branches, centrée sur les minuscules
    cx, cy = 8, 9
    for r in range(10):
        half = max(0, 2 - r // 4)
        for d in range(-half, half + 1):
            for x, y in ((cx + d, cy + r), (cx + d, cy - r), (cx + r, cy + d), (cx - r, cy + d)):
                g.fill(x, y)
    g.rect(cx - 2, cy - 2, cx + 2, cy + 2)
    G["✦"] = g
    return G


def normalise(g):
    """Décale le glyphe pour que sa colonne la plus à gauche soit la colonne 1 (approche gauche)."""
    xmin = min(x for x, _ in g.px)
    return {(x - xmin + 1, y) for x, y in g.px}


def accent_of(font, char, base):
    """Accent (ou cédille) de Jacquard 24, centré horizontalement sur la nouvelle lettre."""
    original = glyph_pixels(font, char)
    if char in "Ç":
        part = {(x, y) for x, y in original if y < 0}
    else:
        part = {(x, y) for x, y in original if y >= CAP + 1}
    if not part:
        return set()
    acx = (min(x for x, _ in part) + max(x for x, _ in part)) / 2
    bcx = (min(x for x, _ in base) + max(x for x, _ in base)) / 2
    dx = round(bcx - acx)
    return {(x + dx, y) for x, y in part}


ACCENTED = {"À": "A", "Â": "A", "Ä": "A", "Ç": "C", "É": "E", "È": "E", "Ê": "E", "Ë": "E",
            "Î": "I", "Ï": "I", "Ô": "O", "Ö": "O", "Ù": "U", "Û": "U", "Ü": "U", "Ÿ": "Y"}


def ligature(left, right, overlap):
    """Œ et Æ : la deuxième lettre partage le flanc droit de la première."""
    w = max(x for x, _ in left) + 1
    return left | {(x + w - overlap, y) for x, y in right}


def write_cell(img, index, pixels):
    x0, base_y = cell_origin(index)
    for y in range(base_y - ASC_PX, base_y + DESC_PX):
        for x in range(x0, x0 + CELL_W):
            r, g, b, a = img.getpixel((x, y))
            if a > 0 and (r, g, b) == (0, 0, 0):
                img.putpixel((x, y), (0, 0, 0, 0))
    for col, row in pixels:
        x, y = x0 + ORIGIN_X + col, base_y - 1 - row
        if x0 <= x < x0 + CELL_W:
            img.putpixel((x, y), (0, 0, 0, 255))


def main(ttf, sheet):
    font = TTFont(ttf)
    img = Image.open(sheet).convert("RGBA")
    caps = {k: normalise(v) for k, v in cap_glyphs().items()}
    designed = dict(caps)
    for char, base in ACCENTED.items():
        designed[char] = caps[base] | accent_of(font, char, caps[base])
    designed["Œ"] = ligature(caps["O"], caps["E"], STEM)
    designed["Æ"] = ligature(caps["A"], caps["E"], STEM + 2)
    for index, char in enumerate(CHARSET):
        if char in designed:
            write_cell(img, index, designed[char])
    img.save(sheet)
    print(f"{len(designed)} glyphes dessinés sur {sheet}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
