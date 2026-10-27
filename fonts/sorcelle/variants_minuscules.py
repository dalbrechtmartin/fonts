"""Compare les deux styles de minuscules (ronde / brisee) -> variantes/minuscules/comparaison-minuscules.png

Usage (dans ce dossier) : python variants_minuscules.py
"""
import os
import sys

sys.path.insert(0, '.')
from PIL import Image, ImageDraw, ImageFont

import build
import design_caps
import design_lower
import extract
import legibility

ttf = 'sources/Jacquard24-Regular.ttf'
out = 'variantes/minuscules'
os.makedirs(out, exist_ok=True)
res = []
for name, label in (("ronde", "1 · Minuscules rondes"), ("brisee", "2 · Minuscules brisées (touche gothique)")):
    design_lower.LSTYLE["name"] = name
    sheet = f'{out}/planche-{name}.png'
    extract.main(ttf, sheet); design_caps.main(ttf, sheet); design_lower.main(ttf, sheet)
    build.main(ttf, sheet, f'{out}/{name}')
    fp = f'{out}/{name}/Sorcelle-Regular.ttf'
    sc = [legibility.score(t, legibility.ocr(fp, t)) for t in legibility.SENTENCES]
    res.append((label, fp, sum(sc) / len(sc)))
LINES = ["Danaé Albrecht--Martin", "abcdefghijklmnopqrstuvwxyz", "Parcours · Projets · Créations", "« Œuvre » à l'été ! 0123456789"]
lf = extract.load_label_font(18)
img = Image.new('RGB', (1560, 40 + len(res) * 430), (241, 233, 216))
d = ImageDraw.Draw(img); y = 20
for label, fp, ocr in res:
    f = ImageFont.truetype(fp, 86)
    d.text((20, y), f"{label}   ·   lecture OCR : {ocr:.0%}", fill=(90, 79, 95), font=lf)
    for i, line in enumerate(LINES):
        d.text((20, y + 14 + i * 98), line, fill=(29, 24, 34), font=f)
    y += 430
img.save(f'{out}/comparaison-minuscules.png')
for r in res: print(r[0], f"{r[2]:.0%}")
design_lower.LSTYLE["name"] = "ronde"
