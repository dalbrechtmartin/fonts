"""Aperçu fidèle (HarfBuzz + FreeType) : met en forme comme un navigateur, dessine sans rogner aux métriques.

Utile pour les coulures de ss01, qui descendent sous la boîte de ligne et que d'autres aperçus coupent.

Usage (depuis Python) :
    from apercu_harfbuzz import planche
    planche([("A H O T", 400, 150, {"ss01": True})], "apercu.png", "fonts/variable/Thornveil-VF.ttf")
"""
import uharfbuzz as hb
from fontTools.pens.freetypePen import FreeTypePen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from PIL import Image, ImageOps


def ligne(chemin, texte, wght, taille, feats):
    tt = TTFont(chemin); blob = hb.Blob.from_file_path(chemin)
    face = hb.Face(blob); font = hb.Font(face); font.set_variations({'wght': wght})
    b = hb.Buffer(); b.add_str(texte); b.guess_segment_properties(); hb.shape(font, b, feats)
    gs = tt.getGlyphSet(location={'wght': wght}); order = tt.getGlyphOrder()
    pen = FreeTypePen(gs); x = 0
    for info, pos in zip(b.glyph_infos, b.glyph_positions):
        gs[order[info.codepoint]].draw(TransformPen(pen, (1, 0, 0, 1, x + pos.x_offset, pos.y_offset))); x += pos.x_advance
    e = taille / 1000
    return pen.image(width=int(x * e) + 60, height=int(1750 * e), transform=(e, 0, 0, e, 30, int(720 * e)), contain=False)

def planche(lignes, sortie, chemin):
    imgs = [ligne(chemin, t, w, s, f) for t, w, s, f in lignes]
    W = max(i.width for i in imgs); H = sum(i.height for i in imgs)
    out = Image.new('L', (W, H), 0); y = 0
    for i in imgs:
        out.paste(i.getchannel('A'), (0, y)); y += i.height
    ImageOps.invert(out).save(sortie)
