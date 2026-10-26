"""Transforme Jacquard 24 en planche PNG à retoucher dans Aseprite.

Usage : python extract.py sources/Jacquard24-Regular.ttf planche.png

Sur la planche :
- chaque case = un caractère, 1 pixel de la planche = 1 « pixel » de la police (30 unités) ;
- seuls les pixels NOIRS (#000000) font partie des lettres : c'est eux que tu dessines ;
- les repères en couleur (ligne de base, hauteur des capitales, hauteur des minuscules,
  étiquettes) sont ignorés par build.py : tu peux les laisser.
"""
import sys
import unicodedata

from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

from grid import (
    ASC_PX,
    CELL_H,
    CELL_W,
    CHARSET,
    COLS,
    GUIDE_BASE,
    GUIDE_CAP,
    GUIDE_LABEL,
    GUIDE_XH,
    LABEL_H,
    ORIGIN_X,
    PX,
    cell_origin,
)


def load_label_font(size=10):
    """Police des étiquettes : Arial sous Windows, DejaVu sous Linux, sinon celle de Pillow."""
    for name in ("arial.ttf", "DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default(size=size)


LABEL_FONT = load_label_font()


def glyph_pixels(font, char):
    """Renvoie l'ensemble des pixels (colonne, ligne depuis la ligne de base) remplis."""
    glyph_set = font.getGlyphSet()
    name = font.getBestCmap().get(ord(char))
    if name is None:      # caractère absent de la police d'origine : case vide à dessiner
        return set()
    pen = DecomposingRecordingPen(glyph_set)
    glyph_set[name].draw(pen)
    contours, current = [], []
    for op, args in pen.value:
        if op == "moveTo":
            current = [args[0]]
        elif op in ("lineTo", "qCurveTo", "curveTo"):
            current.append(args[-1])
        elif op in ("closePath", "endPath"):
            contours.append(current)
    filled = set()
    if not contours:
        return filled
    xs = [p[0] for c in contours for p in c]
    ys = [p[1] for c in contours for p in c]
    for col in range(int(min(xs) // PX), int(max(xs) // PX) + 1):
        for row in range(int(min(ys) // PX), int(max(ys) // PX) + 1):
            cx, cy = col * PX + PX / 2, row * PX + PX / 2
            inside = False  # règle pair-impair sur tous les contours
            for c in contours:
                for i in range(len(c)):
                    (x1, y1), (x2, y2) = c[i - 1], c[i]
                    if (y1 > cy) != (y2 > cy) and cx < x1 + (cy - y1) * (x2 - x1) / (y2 - y1):
                        inside = not inside
            if inside:
                filled.add((col, row))
    return filled


def case_presente(img, index):
    """La case a déjà ses repères (planche existante)."""
    x0, base_y = cell_origin(index)
    return base_y < img.height and img.getpixel((x0, base_y)) == GUIDE_BASE


def main(ttf_path, out_path, etendre=False):
    font = TTFont(ttf_path)
    os2 = font["OS/2"]
    cap_px, xh_px = os2.sCapHeight // PX, os2.sxHeight // PX
    rows = (len(CHARSET) + COLS - 1) // COLS
    img = Image.new("RGBA", (COLS * CELL_W, rows * CELL_H), (255, 255, 255, 0))
    if etendre:
        ancienne = Image.open(out_path).convert("RGBA")
        img.paste(ancienne, (0, 0))
    draw = ImageDraw.Draw(img)
    hmtx = font["hmtx"]
    cmap = font.getBestCmap()
    ajoutes = 0
    for index, char in enumerate(CHARSET):
        if etendre and case_presente(img, index):
            continue
        ajoutes += 1
        x0, base_y = cell_origin(index)
        advance_px = hmtx[cmap[ord(char)]][0] // PX if ord(char) in cmap else 0
        # Repères (ignorés à la reconstruction)
        draw.line([(x0, base_y), (x0 + CELL_W - 2, base_y)], fill=GUIDE_BASE)
        draw.line([(x0, base_y - cap_px), (x0 + CELL_W - 2, base_y - cap_px)], fill=GUIDE_CAP)
        draw.line([(x0, base_y - xh_px), (x0 + CELL_W - 2, base_y - xh_px)], fill=GUIDE_XH)
        draw.line([(x0 + ORIGIN_X + advance_px, base_y - cap_px - 4),
                   (x0 + ORIGIN_X + advance_px, base_y + 6)], fill=GUIDE_LABEL)
        etiquette = f"◌{char}" if unicodedata.category(char) == "Mn" else char
        draw.text((x0 + 3, base_y - ASC_PX - LABEL_H + 1), etiquette, fill=GUIDE_LABEL, font=LABEL_FONT)
        for col, row in glyph_pixels(font, char):
            if 0 <= ORIGIN_X + col < CELL_W:      # accents combinants : contours à gauche de l'origine
                img.putpixel((x0 + ORIGIN_X + col, base_y - 1 - row), (0, 0, 0, 255))
    img.save(out_path)
    print(f"{ajoutes} caractère(s) -> {out_path} ({img.width} × {img.height} px)")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], etendre="--etendre" in sys.argv[3:])
