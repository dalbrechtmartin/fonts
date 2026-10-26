"""Génère plusieurs variantes de capitales de Sorcelle et une planche de comparaison.

Usage : python variants.py sources/Jacquard24-Regular.ttf variantes/
"""
import os
import shutil
import sys

from PIL import Image, ImageDraw, ImageFont

import build
import design_caps
import design_lower
import extract
import legibility

VARIANTS = [
    ("v0", "v0.1 actuelle", dict(stem=4, hair=2, filet=True, top="cut", foot="spur", bowl="octagon", chamfer=1.0)),
    ("A", "A · Brisée lourde", dict(stem=5, hair=2, filet=False, top="flag", foot="diamond", bowl="octagon", chamfer=1.1)),
    ("B", "B · Lombarde arrondie", dict(stem=5, hair=2, filet=False, top="curl", foot="slab", bowl="round", chamfer=1.0)),
    ("C", "C · Lombarde à filet", dict(stem=5, hair=2, filet=True, top="curl", foot="slab", bowl="round", chamfer=1.0)),
    ("D", "D · Pixel nette", dict(stem=4, hair=3, filet=False, top="flat", foot="slab", bowl="octagon", chamfer=0.6)),
]
LINES = ["Danaé Albrecht--Martin", "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "Projets · Réseaux · Œuvres"]
INK, MUTED, BG = (29, 24, 34), (90, 79, 95), (241, 233, 216)


def apply(params):
    design_caps.STEM, design_caps.HAIR = params["stem"], params["hair"]
    design_caps.STYLE.update({k: params[k] for k in ("filet", "top", "foot", "bowl", "chamfer")})


def main(ttf, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    results = []
    for slug, label, params in VARIANTS:
        apply(params)
        sheet = os.path.join(out_dir, f"planche-{slug}.png")
        extract.main(ttf, sheet)
        design_caps.main(ttf, sheet)
        design_lower.main(ttf, sheet)
        build.main(ttf, sheet, os.path.join(out_dir, slug))
        font_path = os.path.join(out_dir, slug, "Sorcelle-Regular.ttf")
        scores = [legibility.score(t, legibility.ocr(font_path, t)) for t in legibility.SENTENCES]
        results.append((slug, label, font_path, sum(scores) / len(scores)))
    # Planche de comparaison, taille pixel exacte x2
    size = 43 * 2
    label_font = extract.load_label_font(18)
    img = Image.new("RGB", (1560, 70 + len(results) * 330), BG)
    draw = ImageDraw.Draw(img)
    y = 20
    for slug, label, font_path, ocr in results:
        font = ImageFont.truetype(font_path, size)
        draw.text((20, y), f"{label}   ·   lecture OCR : {ocr:.0%}", fill=MUTED, font=label_font)
        for i, line in enumerate(LINES):
            draw.text((20, y + 14 + i * 98), line, fill=INK, font=font)
        y += 330
    img.save(os.path.join(out_dir, "comparaison.png"))
    for slug, label, _, ocr in results:
        print(f"{label:28} OCR {ocr:.0%}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
