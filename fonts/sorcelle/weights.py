"""Spécimen et test de lisibilité des trois graisses de Sorcelle.

Usage : python weights.py dist graisses.png   (nécessite Tesseract pour la partie OCR)
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

import extract
import legibility

STYLES = [("Regular", 400), ("SemiBold", 600), ("Bold", 700)]
LINES = ["Danaé Albrecht--Martin", "Projets · Créations · Réseaux", "ABCDEFGHIJKLMNOPQRSTUVWXYZ 0123456789"]
INK, MUTED, BG = (29, 24, 34), (90, 79, 95), (241, 233, 216)


def main(dist, out):
    label = extract.load_label_font(18)
    img = Image.new("RGB", (1700, 60 + len(STYLES) * 300), BG)
    d = ImageDraw.Draw(img)
    y = 20
    for style, weight in STYLES:
        path = os.path.join(dist, f"Sorcelle-{style}.ttf")
        scores = [legibility.score(t, legibility.ocr(path, t)) for t in legibility.SENTENCES]
        ocr = sum(scores) / len(scores)
        print(f"{style:9} ({weight}) OCR {ocr:.1%}")
        d.text((20, y), f"Sorcelle {style} · {weight} · lecture OCR : {ocr:.0%}", fill=MUTED, font=label)
        big = ImageFont.truetype(path, 86)
        small = ImageFont.truetype(path, 43)
        d.text((20, y + 26), LINES[0], fill=INK, font=big)
        d.text((20, y + 140), LINES[1], fill=INK, font=small)
        d.text((20, y + 200), LINES[2], fill=INK, font=small)
        y += 300
    img.save(out)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
