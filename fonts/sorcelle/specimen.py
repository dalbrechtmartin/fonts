"""Aperçu de Sorcelle à côté de Jacquard 24, à la taille pixel exacte (x2 et x4).

Usage : python specimen.py sources/Jacquard24-Regular.ttf dist/Sorcelle-Regular.ttf specimen.png
"""
import sys

from PIL import Image, ImageDraw, ImageFont

LINES = [
    "Danaé Albrecht--Martin",
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    "abcdefghijklmnopqrstuvwxyz 0123456789",
    "Parcours · Projets · Créations · Réseaux",
    "« Œuvre » à l'été, ça brûle ! ÀÉÈÊÇ",
]
INK = (29, 24, 34)
MUTED = (90, 79, 95)
BG = (241, 233, 216)
UNIT_SIZE = 43  # 1290 unités / 30 = 43 : à 43 px, 1 pixel de police = 1 pixel d'écran


def main(original, yoru, out):
    fonts = [("Jacquard 24", ImageFont.truetype(original, UNIT_SIZE * 2)),
             ("Sorcelle", ImageFont.truetype(yoru, UNIT_SIZE * 2))]
    label = ImageFont.load_default(size=14)
    height = 40 + len(LINES) * len(fonts) * 100 + 160
    img = Image.new("RGB", (1500, height), BG)
    draw = ImageDraw.Draw(img)
    y = 20
    for text in LINES:
        for name, font in fonts:
            draw.text((20, y), name, fill=MUTED, font=label)
            draw.text((140, y - 20), text, fill=INK, font=font)
            y += 100
    big = ImageFont.truetype(yoru, UNIT_SIZE * 4)
    draw.text((20, y), "Sorcelle x4", fill=MUTED, font=label)
    draw.text((140, y - 30), "Grimoire", fill=(107, 63, 181), font=big)
    img.save(out)
    print(f"-> {out}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
