"""Variantes pour les fonctions OpenType, construites à partir des glyphes existants.

- « .case » : ponctuation remontée au centre des capitales, pour « (PARIS) » ou « « ALERTE » » ;
- « zero.zero » : zéro barré, pour les identifiants et le code.
Les alternances « .alt1 / .alt2 » et les chats « .ss01 » sont produits par generer.py.
"""

from chiffres import CENTRE, HAUTEUR
from glyphes import GLYPHES, METRIQUES, Trait, glyphe
from pinceau import ligne, transformer

CENTRE_CAPITALES = METRIQUES["capitale"] / 2

# Centre vertical actuel de chaque signe → décalage pour le poser au centre des capitales
CENTRES = {
    "parenleft": 305, "parenright": 305, "bracketleft": 310, "bracketright": 310,
    "braceleft": 310, "braceright": 310,
    "hyphen": 270, "endash": 270, "emdash": 270,
    "guillemotleft": 270, "guillemotright": 270, "guilsinglleft": 270, "guilsinglright": 270,
    "periodcentered": 290,
}


def remonte(nom: str, decalage: float):
    def dessiner():
        traits, chasse, ancres = GLYPHES[nom][1]()
        return transformer(traits, dy=decalage), chasse, ancres
    return dessiner


for nom, centre in CENTRES.items():
    glyphe(f"{nom}.case")(remonte(nom, CENTRE_CAPITALES - centre))


@glyphe("zero.zero")
def dessiner_zero_barre():
    traits, chasse, ancres = GLYPHES["zero"][1]()
    barre = Trait([ligne((CENTRE - 95, HAUTEUR * 0.22), (CENTRE + 95, HAUTEUR * 0.78))], epaisseur=0.7)
    return traits + [barre], chasse, ancres
