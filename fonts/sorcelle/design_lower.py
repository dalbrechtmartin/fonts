"""Dessine les minuscules, les chiffres et la ponctuation de Sorcelle, dans le style des capitales.

Usage : python design_lower.py sources/Jacquard24-Regular.ttf planche.png
(à lancer après design_caps.py)

Principes (lisibilité) :
- formes humanistes simples, panses rondes (même famille que les capitales « lombarde arrondie ») ;
- fûts de 4 px, déliés de 2 px, crosse en haut des hampes, petit drapeau en haut des fûts courts ;
- paires à risque différenciées : l (sortie à droite) / I (empattements) / 1 (drapeau + socle),
  O / 0 (0 plus étroit, barré), a à deux étages (≠ o, d), g à boucle ouverte, rn / m ;
- hauteurs de Jacquard 24 conservées : x = 17 px, hampes et capitales 25 px, jambages 7 px.
"""
import sys

from fontTools.ttLib import TTFont
from PIL import Image

import design_caps
from design_caps import Glyph, normalise, write_cell
from extract import glyph_pixels
from grid import CHARSET

LS = 4      # fût des minuscules
H = 2       # délié
XH = 16     # dernière ligne des minuscules
ASC = 24    # dernière ligne des hampes (= capitales)
DSC = -6    # dernière ligne des jambages

# Style des minuscules : "ronde" (panses rondes, drapeaux) ou "brisee" (panses en octogone, têtes en biseau)
LSTYLE = {"name": "ronde"}


class L(Glyph):
    def fut(self, x, y0, y1, top=None, foot=None, w=LS):
        self.rect(x, y0, x + w - 1, y1)
        if LSTYLE["name"] == "brisee":
            top = "flag" if top == "curl" else top
            foot = "diamond" if foot == "slab" else foot
        if top == "curl":      # crosse, comme les capitales
            self.rect(x - 3, y1, x - 1, y1)
            self.rect(x - 3, y1 - 2, x - 3, y1 - 1)
        elif top == "flag":    # petit drapeau à gauche
            if LSTYLE["name"] == "brisee":   # biseau gothique : tête taillée en pointe
                self.erase([(x, y1), (x + 1, y1), (x, y1 - 1)])
                self.rect(x - 2, y1 - 3, x - 1, y1 - 2)
                self.fill(x - 1, y1 - 1)
            else:
                self.rect(x - 2, y1 - 1, x - 1, y1)
        if foot == "slab":
            self.rect(x - 2, y0, x + w + 1, y0 + 1)
        elif foot == "diamond":  # pied en pointe (textura)
            self.rect(x - 1, y0 + 1, x + w, y0 + 1)
            self.erase([(x, y0), (x + w - 1, y0)])
        elif foot == "exit":   # sortie vers la droite
            self.rect(x + w, y0, x + w + 1, y0 + 1)

    def ring(self, x0, y0, x1, y1, side=LS, cap=H, open_right=None):
        self.octagon(x0, y0, x1, y1, 4, side=side, cap=cap, open_right=open_right)

    def keep(self, cond):
        self.px = {(x, y) for x, y in self.px if cond(x, y)}

    def mirror(self):
        xmax = max(x for x, _ in self.px)
        self.px = {(xmax - x, y) for x, y in self.px}
        return self


def lower_glyphs():
    G = {}

    def arch(g, x0, x1, top=XH, depth=14):
        """Arche (haut de n, m, h) : anneau prolongé sous la ligne et coupé."""
        a = L()
        a.ring(x0, top - 2 * depth, x1, top)
        a.keep(lambda x, y: y >= top - depth // 2)
        g.px |= a.px

    g = L()                                         # a : deux étages (≠ o, d)
    g.fut(9, 0, 12, foot="exit")
    a = L(); a.ring(0, 6, 12, XH); a.keep(lambda x, y: y >= 12)
    g.px |= a.px
    g.rect(0, 11, 3, 13)
    b = L(); b.ring(0, 0, 12, 9); b.keep(lambda x, y: x <= 9)
    g.px |= b.px
    g.rect(4, 8, 12, 9)
    G["a"] = g

    g = L()                                         # b
    g.ring(-10, 0, 13, XH)
    g.keep(lambda x, y: x >= 0)
    g.fut(0, 0, ASC, top="curl")
    G["b"] = g

    g = L()                                         # c : ouverture à droite, deux ergots
    g.ring(0, 0, 12, XH, open_right=(5, 11))
    g.rect(10, 11, 12, 13)
    g.rect(10, 3, 12, 5)
    G["c"] = g

    g = L()                                         # d
    g.ring(0, 0, 23, XH)
    g.keep(lambda x, y: x <= 12)
    g.fut(9, 0, ASC, top="curl", foot="exit")
    G["d"] = g

    g = L()                                         # e : barre fine, ouverture basse à droite
    g.ring(0, 0, 12, XH, open_right=(3, 7))
    g.rect(0, 8, 12, 9)
    g.rect(10, 3, 12, 4)
    G["e"] = g

    g = L()                                         # f : crochet en haut, barre à hauteur x
    g.fut(2, 0, 20, foot="slab")
    a = L(); a.ring(2, 12, 13, ASC); a.keep(lambda x, y: y >= 20 and x <= 10)
    g.px |= a.px
    g.rect(9, 20, 11, 22)
    g.rect(0, XH - 1, 10, XH)
    G["f"] = g

    g = L()                                         # g : panse + jambage en crochet ouvert
    g.ring(0, 1, 12, XH)
    g.keep(lambda x, y: x <= 9)
    g.fut(9, -3, XH)
    g.rect(9, XH - 1, 13, XH)
    a = L(); a.ring(0, DSC, 12, 4); a.keep(lambda x, y: y <= -2)
    g.px |= a.px
    g.rect(0, -3, 3, -1)
    G["g"] = g

    g = L()                                         # h
    g.fut(0, 0, ASC, top="curl", foot="slab")
    arch(g, 0, 13)
    g.fut(10, 0, 9, foot="slab")
    G["h"] = g

    g = L()                                         # i (point carré bien détaché)
    g.fut(2, 0, XH, top="flag", foot="exit")
    g.rect(2, 20, 5, 23)
    G["i"] = g

    g = L()                                         # j
    g.fut(5, -3, XH, top="flag")
    a = L(); a.ring(-2, DSC, 8, 2); a.keep(lambda x, y: y <= -3 and x >= 0)
    g.px |= a.px
    g.rect(5, 20, 8, 23)
    G["j"] = g

    g = L()                                         # k : bras fin, jambe épaisse
    g.fut(0, 0, ASC, top="curl", foot="slab")
    g.diag(4, 6, 11, XH, H + 1)
    g.rect(9, XH - 1, 14, XH)
    g.diag(5, 8, 11, 0, LS)
    g.rect(10, 0, 16, 1)
    G["k"] = g

    g = L()                                         # l : sortie à droite (≠ I, 1)
    g.fut(0, 2, ASC, top="curl")
    a = L(); a.ring(0, 0, 10, 10); a.keep(lambda x, y: y <= 3 and x >= 0)
    g.px |= a.px
    g.rect(7, 2, 9, 4)
    G["l"] = g

    g = L()                                         # m : trois fûts, deux arches
    g.fut(0, 0, XH, top="flag", foot="slab")
    arch(g, 0, 11)
    g.fut(8, 0, 9, foot="slab")
    arch(g, 8, 19)
    g.fut(16, 0, 9, foot="slab")
    G["m"] = g

    g = L()                                         # n
    g.fut(0, 0, XH, top="flag", foot="slab")
    arch(g, 0, 13)
    g.fut(10, 0, 9, foot="slab")
    G["n"] = g

    g = L()                                         # o
    g.ring(0, 0, 13, XH)
    G["o"] = g

    g = L()                                         # p
    g.ring(-10, 0, 13, XH)
    g.keep(lambda x, y: x >= 0)
    g.fut(0, DSC, XH, top="flag", foot="slab")
    G["p"] = g

    g = L()                                         # q
    g.ring(0, 0, 23, XH)
    g.keep(lambda x, y: x <= 12)
    g.fut(9, DSC, XH, foot="slab")
    G["q"] = g

    g = L()                                         # r : épaule courte (rn ≠ m)
    g.fut(0, 0, XH, top="flag", foot="slab")
    a = L(); a.ring(0, 2, 11, XH); a.keep(lambda x, y: y >= 12 and x >= 2)
    g.px |= a.px
    g.rect(9, 11, 11, 13)
    G["r"] = g

    g = L()                                         # s : épine épaisse
    g.rect(3, XH - 1, 10, XH)
    g.rect(10, 12, 12, XH - 1)
    a = L(); a.ring(0, 7, 8, XH, side=LS - 1); a.keep(lambda x, y: x <= 4)
    g.px |= a.px
    g.diag(1, 11, 9, 5, LS)
    b = L(); b.ring(4, 0, 12, 9, side=LS - 1); b.keep(lambda x, y: x >= 8)
    g.px |= b.px
    g.rect(2, 0, 9, 1)
    g.rect(0, 1, 2, 4)
    G["s"] = g

    g = L()                                         # t : haut court, pied recourbé
    g.fut(2, 3, 21)
    g.rect(0, XH - 1, 10, XH)
    a = L(); a.ring(2, 0, 12, 10); a.keep(lambda x, y: y <= 3 and x >= 2)
    g.px |= a.px
    g.rect(9, 2, 11, 4)
    G["t"] = g

    g = L()                                         # u
    g.fut(0, 7, XH, top="flag")
    a = L(); a.ring(0, 0, 13, 2 * 14); a.keep(lambda x, y: y <= 7)
    g.px |= a.px
    g.fut(10, 0, XH, top="flag", foot="exit")
    G["u"] = g

    g = L()                                         # v
    g.diag(0, XH, 6, 0, LS)
    g.diag(13, XH, 8, 0, H + 1)
    g.rect(6, 0, 9, 1)
    g.rect(-1, XH - 1, 4, XH)
    g.rect(11, XH - 1, 15, XH)
    G["v"] = g

    g = L()                                         # w
    g.diag(0, XH, 4, 0, LS)
    g.diag(10, 12, 6, 0, H)
    g.diag(10, 12, 14, 0, LS)
    g.diag(20, XH, 16, 0, H + 1)
    g.rect(-1, XH - 1, 4, XH)
    g.rect(18, XH - 1, 22, XH)
    G["w"] = g

    g = L()                                         # x
    g.diag(0, XH, 11, 0, LS)
    g.diag(12, XH, 1, 0, H)
    g.rect(-1, XH - 1, 4, XH)
    g.rect(10, XH - 1, 14, XH)
    g.rect(-1, 0, 3, 1)
    g.rect(9, 0, 15, 1)
    G["x"] = g

    g = L()                                         # y : v dont le bras droit plonge
    g.diag(0, XH, 6, 1, LS)
    g.diag(13, XH, 3, DSC + 1, H + 1)
    g.rect(-1, XH - 1, 4, XH)
    g.rect(11, XH - 1, 15, XH)
    g.rect(0, DSC, 5, DSC + 1)
    G["y"] = g

    g = L()                                         # z
    g.rect(1, XH - 1, 12, XH)
    g.rect(0, XH - 4, 1, XH)
    g.diag(9, XH - 2, 1, 2, LS)
    g.rect(0, 0, 13, 1)
    g.rect(12, 0, 13, 4)
    G["z"] = g
    return G


def digit_glyphs():
    """Chiffres alignés, hauteur 23 px (un peu sous les capitales), chasse fixe."""
    G = {}
    T = 22

    g = L()                                         # 0 : plus étroit que O, barré
    g.ring(0, 0, 13, T)
    g.diag(5, 7, 8, 15, 2)
    G["0"] = g

    g = L()                                         # 1 : long drapeau oblique + socle (≠ I, l)
    g.fut(6, 0, T)
    g.diag(0, T - 8, 5, T, 3)
    g.rect(2, 0, 13, 1)
    G["1"] = g

    g = L()                                         # 2
    a = L(); a.ring(0, 8, 13, T); a.keep(lambda x, y: y >= 14)
    g.px |= a.px
    g.rect(0, 13, 3, 16)
    g.diag(9, 14, 1, 2, LS)
    g.rect(0, 0, 13, 1)
    g.rect(12, 0, 13, 4)
    G["2"] = g

    g = L()                                         # 3 : haut plat (≠ 8)
    g.rect(1, T - 1, 13, T)
    g.diag(12, T - 2, 6, 13, LS - 1)
    a = L(); a.ring(0, 0, 13, 14); a.keep(lambda x, y: x >= 5 or y <= 4)
    g.px |= a.px
    g.rect(0, 2, 3, 5)
    G["3"] = g

    g = L()                                         # 4 : fermé, barre basse
    g.fut(9, 0, T)
    g.diag(9, T, 0, 7, H + 1)
    g.rect(0, 6, 14, 7)
    g.rect(7, 0, 14, 1)
    G["4"] = g

    g = L()                                         # 5 : haut plat, fût vertical (≠ S)
    g.rect(1, T - 1, 13, T)
    g.fut(1, 11, T)
    a = L(); a.ring(-4, 0, 13, 14); a.keep(lambda x, y: x >= 3 or y <= 4)
    g.px |= a.px
    g.rect(0, 2, 3, 5)
    G["5"] = g

    g = L()                                         # 6
    g.ring(0, 0, 13, 13)
    a = L(); a.ring(0, 0, 13, T); a.keep(lambda x, y: x <= 8 and y >= 6)
    g.px |= a.px
    g.rect(9, T - 4, 11, T - 1)
    g.rect(5, T - 1, 9, T)
    G["6"] = g

    g = L()                                         # 7 : barre + jambe droite (≠ 1)
    g.rect(0, T - 1, 13, T)
    g.rect(0, T - 4, 1, T)
    g.diag(12, T - 2, 4, 0, LS)
    G["7"] = g

    g = L()                                         # 8 : panse haute plus petite
    g.ring(1, 11, 12, T)
    g.ring(0, 0, 13, 12)
    G["8"] = g

    g = L()                                         # 9
    g.px = {(13 - x, T - y) for x, y in digit_glyphs_six().px}
    G["9"] = g
    return G


def digit_glyphs_six():
    T = 22
    g = L()
    g.ring(0, 0, 13, 13)
    a = L(); a.ring(0, 0, 13, T); a.keep(lambda x, y: x <= 8 and y >= 6)
    g.px |= a.px
    g.rect(9, T - 4, 11, T - 1)
    g.rect(5, T - 1, 9, T)
    return g


def punct_glyphs():
    G = {}

    def dot(g, x, y):
        g.rect(x, y, x + 3, y + 3)

    g = L(); dot(g, 0, 0); G["."] = g
    g = L(); dot(g, 0, 0); g.rect(2, -3, 3, -1); g.rect(1, -4, 2, -3); G[","] = g
    g = L(); dot(g, 0, 0); dot(g, 0, 13); G[":"] = g
    g = L(); dot(g, 0, 13); dot(g, 0, 0); g.rect(2, -3, 3, -1); g.rect(1, -4, 2, -3); G[";"] = g
    g = L(); g.rect(0, 9, 3, ASC); g.rect(1, 7, 2, 8); dot(g, 0, 0); G["!"] = g

    g = L()                                         # ?
    a = L(); a.ring(0, 10, 13, ASC); a.keep(lambda x, y: y >= 17)
    g.px |= a.px
    g.rect(0, 16, 3, 19)
    g.diag(10, 17, 5, 9, LS)
    g.rect(5, 7, 8, 9)
    dot(g, 5, 0)
    G["?"] = g

    g = L(); g.rect(0, 19, 3, ASC); g.rect(1, 17, 2, 18); G["'"] = g
    g = L(); g.rect(1, 18, 3, ASC); g.rect(0, ASC - 3, 0, ASC); g.rect(0, 16, 1, 17); G["’"] = g
    g = L(); g.rect(0, 19, 3, ASC); g.rect(1, 17, 2, 18); g.rect(6, 19, 9, ASC); g.rect(7, 17, 8, 18); G['"'] = g

    def chevron(g, x, right):
        for i in range(6):
            for t in range(3):
                xx = x + i + t if right else x + 5 - i + t
                g.fill(xx, 10 + i)
                g.fill(xx, 10 - i)
    g = L(); chevron(g, 0, True); chevron(g, 7, True); G["«"] = g
    g = L(); chevron(g, 0, False); chevron(g, 7, False); G["»"] = g

    g = L()                                         # ( )
    a = L(); a.ring(0, -3, 16, ASC + 1, side=3); a.keep(lambda x, y: x <= 6)
    g.px |= a.px
    G["("] = g
    G[")"] = L(); G[")"].px = set(g.px); G[")"].mirror()

    g = L(); g.rect(0, -3, 3, ASC + 1); g.rect(4, -3, 7, -2); g.rect(4, ASC, 7, ASC + 1); G["["] = g
    G["]"] = L(); G["]"].px = set(g.px); G["]"].mirror()

    g = L(); g.rect(0, 9, 9, 11); G["-"] = g
    g = L(); g.rect(0, 9, 15, 10); G["–"] = g
    g = L(); g.rect(0, 9, 23, 10); G["—"] = g
    g = L(); dot(g, 0, 0); dot(g, 7, 0); dot(g, 14, 0); G["…"] = g

    g = L()                                         # & : forme latine simple
    a = L(); a.ring(2, 13, 12, ASC, side=3); g.px |= a.px
    b = L(); b.ring(0, 0, 13, 14); b.keep(lambda x, y: x <= 9)
    g.px |= b.px
    g.diag(5, 14, 17, 0, LS)
    g.rect(11, 5, 18, 6)
    G["&"] = g

    g = L()                                         # @
    g.ring(0, -4, 24, 20, side=3)
    g.erase([(x, y) for x in range(18, 25) for y in range(-2, 6)])
    a = L(); a.ring(6, 1, 15, 13, side=3); g.px |= a.px
    g.fut(14, 1, 13, w=3)
    g.rect(14, 1, 20, 2)
    g.rect(19, 1, 21, 6)
    G["@"] = g

    g = L()                                         # #
    g.diag(5, 0, 8, ASC - 2, 3)
    g.diag(12, 0, 15, ASC - 2, 3)
    g.rect(0, 15, 19, 16)
    g.rect(0, 6, 19, 7)
    G["#"] = g

    g = L()                                         # %
    a = L(); a.ring(0, 14, 8, ASC, side=3); g.px |= a.px
    b = L(); b.ring(12, 0, 20, 10, side=3); g.px |= b.px
    g.diag(3, 0, 17, ASC, 3)
    G["%"] = g

    g = L()                                         # * : croix de trois traits
    g.rect(5, 13, 7, ASC)
    for i in range(9):
        g.rect(1 + i, 14 + i, 2 + i, 14 + i)
        g.rect(1 + i, 22 - i, 2 + i, 22 - i)
    G["*"] = g

    g = L(); g.diag(0, -2, 11, ASC, 3); G["/"] = g
    g = L(); g.rect(6, 3, 8, 17); g.rect(0, 9, 14, 11); G["+"] = g
    g = L(); g.rect(0, 12, 13, 13); g.rect(0, 6, 13, 7); G["="] = g
    g = L(); g.rect(0, -3, 14, -2); G["_"] = g

    g = L()                                         # < >
    for i in range(7):
        g.rect(9 - i - 2, 10 + i, 9 - i, 10 + i)
        g.rect(9 - i - 2, 10 - i, 9 - i, 10 - i)
    G[">"] = g
    G["<"] = L(); G["<"].px = set(g.px); G["<"].mirror()

    # § : celui de Jacquard 24 est conservé (gothique, rare, déjà lisible)

    g = L()                                         # ©
    g.ring(0, -2, 24, 22, side=3)
    c = L(); c.ring(7, 4, 17, 16, side=3, open_right=(8, 12)); g.px |= c.px
    G["©"] = g
    return G


def lower_accent(font, char, base):
    """Accent (y ≥ 19) ou cédille (y < 0) de Jacquard 24, centré sur la nouvelle minuscule."""
    original = glyph_pixels(font, char)
    part = {(x, y) for x, y in original if (y < 0 if char == "ç" else y >= 19)}
    if char == "ÿ":
        part = {(x, y) for x, y in original if y >= 19}
    if not part:
        return set()
    acx = (min(x for x, _ in part) + max(x for x, _ in part)) / 2
    xs = [x for x, y in base if y >= 0]
    bcx = (min(xs) + max(xs)) / 2
    dx = round(bcx - acx)
    return {(x + dx, y) for x, y in part}


LOWER_ACCENTED = {"à": "a", "â": "a", "ä": "a", "ç": "c", "é": "e", "è": "e", "ê": "e", "ë": "e",
                  "î": "ı", "ï": "ı", "ô": "o", "ö": "o", "ù": "u", "û": "u", "ü": "u", "ÿ": "y"}


def ligature(left, right, overlap):
    w = max(x for x, _ in left) + 1
    return left | {(x + w - overlap, y) for x, y in right}


def all_glyphs(font):
    saved = design_caps.STYLE["bowl"], design_caps.STYLE["chamfer"]
    if LSTYLE["name"] == "brisee":
        design_caps.STYLE["bowl"], design_caps.STYLE["chamfer"] = "octagon", 1.25
    try:
        return _all_glyphs(font)
    finally:
        design_caps.STYLE["bowl"], design_caps.STYLE["chamfer"] = saved


def _all_glyphs(font):
    low = {k: normalise(v) for k, v in lower_glyphs().items()}
    dotless = {(x, y) for x, y in low["i"] if y <= XH}
    low["ı"] = dotless
    out = {k: v for k, v in low.items() if k != "ı"}
    for char, base in LOWER_ACCENTED.items():
        out[char] = low[base] | lower_accent(font, char, low[base])
    out["œ"] = ligature(low["o"], low["e"], LS)
    out["æ"] = ligature({(x, y) for x, y in low["a"] if not (y <= 1 and x > 13)}, low["e"], LS + 1)
    # chiffres et signes : toujours ronds (les panses brisées les abîment à cette taille)
    bowl, chamfer = design_caps.STYLE["bowl"], design_caps.STYLE["chamfer"]
    design_caps.STYLE["bowl"], design_caps.STYLE["chamfer"] = "round", 1.0
    name, LSTYLE["name"] = LSTYLE["name"], "ronde"
    out.update({k: normalise(v) for k, v in digit_glyphs().items()})
    out.update({k: normalise(v) for k, v in punct_glyphs().items()})
    design_caps.STYLE["bowl"], design_caps.STYLE["chamfer"] = bowl, chamfer
    LSTYLE["name"] = name
    return out


def main(ttf, sheet):
    font = TTFont(ttf)
    img = Image.open(sheet).convert("RGBA")
    designed = all_glyphs(font)
    for index, char in enumerate(CHARSET):
        if char in designed:
            write_cell(img, index, designed[char])
    img.save(sheet)
    print(f"{len(designed)} glyphes dessinés sur {sheet}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
