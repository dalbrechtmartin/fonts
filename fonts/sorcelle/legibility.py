"""Mesure de lisibilité : OCR Tesseract + confusions entre capitales.

Usage : python legibility.py sources/Jacquard24-Regular.ttf dist/Sorcelle-Regular.ttf

1. OCR : chaque phrase est rendue à 3 px par pixel de police puis lue par Tesseract ;
   score = part de caractères correctement reconnus (indicateur, pas une vérité absolue).
2. Confusions : distance entre bitmaps de capitales (part de pixels différents) ;
   les paires les plus proches sont celles qu'un lecteur risque de confondre.
"""
import difflib
import itertools
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFont

SENTENCES = [
    "THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG",
    "PACK MY BOX WITH FIVE DOZEN LIQUOR JUGS",
    "ALBRECHT MARTIN PARCOURS PROJETS GRIMOIRE",
    "Danae Albrecht Martin",
    "Quiz Jumps Over Kind Vexed Wizards",
    "the quick brown fox jumps over the lazy dog",
    "Parcours 2021 2024 2026 et 365 jours",
]
RISKY = ["Il", "I1", "l1", "O0", "o0", "ao", "ce", "hn", "nu", "rn", "il", "5S", "8B", "2Z"]
CAPS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
SIZE = 43 * 3


def ocr(font_path, text):
    font = ImageFont.truetype(font_path, SIZE)
    left, top, right, bottom = font.getbbox(text)
    img = Image.new("L", (right + 80, bottom + 80), 255)
    ImageDraw.Draw(img).text((40, 40), text, font=font, fill=0)
    with tempfile.NamedTemporaryFile(suffix=".png") as tmp:
        img.save(tmp.name)
        out = subprocess.run(["tesseract", tmp.name, "-", "--psm", "7", "-l", "eng"],
                             capture_output=True, text=True).stdout.strip()
    return out


def score(expected, got):
    return difflib.SequenceMatcher(None, expected.replace(" ", ""), got.replace(" ", "")).ratio()


def bitmap(font, char, size=64):
    img = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(img)
    l, t, r, b = font.getbbox(char)
    draw.text(((size - (r - l)) / 2 - l, (size - (b - t)) / 2 - t), char, font=font, fill=255)
    return [1 if p > 127 else 0 for p in img.tobytes()]


def confusions(font_path, top=6):
    font = ImageFont.truetype(font_path, 43)
    maps = {c: bitmap(font, c) for c in CAPS}
    pairs = []
    for a, b in itertools.combinations(CAPS, 2):
        ma, mb = maps[a], maps[b]
        union = sum(1 for x, y in zip(ma, mb) if x or y)
        diff = sum(1 for x, y in zip(ma, mb) if x != y)
        pairs.append((diff / union if union else 1, a + b))
    pairs.sort()
    return pairs[:top]


def risky(font_path):
    font = ImageFont.truetype(font_path, 43)
    out = []
    for pair in RISKY:
        ma, mb = bitmap(font, pair[0]), bitmap(font, pair[1])
        union = sum(1 for x, y in zip(ma, mb) if x or y)
        diff = sum(1 for x, y in zip(ma, mb) if x != y)
        out.append((pair, diff / union if union else 1))
    return out


def main(original, yoru):
    for name, path in (("Jacquard 24", original), ("Sorcelle", yoru)):
        total = 0
        print(f"== {name}")
        for text in SENTENCES:
            got = ocr(path, text)
            s = score(text, got)
            total += s
            print(f"  {s:5.0%}  {text!r} -> {got!r}")
        print(f"  Moyenne OCR : {total / len(SENTENCES):.0%}")
        closest = ", ".join(f"{p} ({d:.0%})" for d, p in confusions(path))
        print(f"  Capitales les plus proches (différence) : {closest}")
        print("  Paires à risque : " + ", ".join(f"{p} ({d:.0%})" for p, d in risky(path)))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
