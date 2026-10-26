"""Écrit les glyphes de Griffonne dans la source UFO.

Usage (depuis la racine du projet) :
    python sources/generateur/generer.py sources/Griffonne-Regular.ufo
Puis : composer_accents.py, construire.py, verifier.py, specimen.py.
"""

import importlib
import sys
import unicodedata

import ufoLib2
from fontTools.pens.recordingPen import RecordingPen

import glyphes as glyphes_module
from glyphes import GLYPHES, METRIQUES
from pinceau import Reglages, dessiner

# Chaque module enregistre ses glyphes dans GLYPHES au chargement
MODULES_DE_GLYPHES = ("glyphes", "capitales", "chiffres", "ponctuation", "diacritiques", "lettres_speciales", "symboles", "variantes")
DEMI_LARGEUR_ACCENT = 90  # largeur réelle d'un accent : ce qui est à côté ne le fait pas monter


def charger_glyphes() -> None:
    for module in MODULES_DE_GLYPHES:
        importlib.import_module(module)


def ajuster_ancres(contour, ancres: dict[str, tuple[float, float]]) -> dict[str, tuple[float, float]]:
    """Ancres calculées sur le dessin réel.

    - « top » monte au-dessus de ce qui dépasse sous l'accent (oreilles du é, du ó) ;
      des oreilles à côté de l'accent (É, ñ) ne le font pas monter.
    - « ogonek » est ajoutée au pied droit de la lettre (ą, ę, ų).
    """
    points = list(contour.points)
    resultat = dict(ancres)
    if "top" in resultat:
        x, y = resultat["top"]
        sous_accent = [py for px, py in points if abs(px - x) <= DEMI_LARGEUR_ACCENT]
        resultat["top"] = (x, max([y, *sous_accent]))
    if "bottom" in resultat and "ogonek" not in resultat:
        pied = [px for px, py in points if py < 120]
        if pied:
            resultat["ogonek"] = (max(pied) - 70, 0)
    return resultat


def appliquer_metriques(police: ufoLib2.Font) -> None:
    info = police.info
    info.xHeight = METRIQUES["hauteur_x"]
    info.capHeight = METRIQUES["capitale"]
    info.ascender = METRIQUES["ascendante"]
    info.descender = METRIQUES["descendante"]
    # Mêmes valeurs typo et hhea, sans interligne ajouté : même rendu sur tous les systèmes
    info.openTypeOS2TypoAscender = info.openTypeHheaAscender = METRIQUES["ligne_haut"]
    info.openTypeOS2TypoDescender = info.openTypeHheaDescender = METRIQUES["ligne_bas"]
    info.openTypeOS2TypoLineGap = info.openTypeHheaLineGap = 0


ALTERNANCES = ("alt1", "alt2")  # 3 versions de chaque lettre avec la version de base : fonction calt


def tracer_proprement(contour, stylo) -> None:
    """Trace en coordonnées entières, sans segment de longueur nulle.

    La fusion des traits laisse des points très proches qui deviennent identiques une fois arrondis :
    des segments nuls, mal gérés par certains moteurs de rendu (avertissement Font Bakery).
    """
    enregistrement = RecordingPen()
    contour.draw(enregistrement)
    operations, precedent, depart = [], None, None
    for operation, points in enregistrement.value:
        entiers = [(round(x), round(y)) for x, y in points]
        if operation == "moveTo":
            operations, precedent, depart = [("moveTo", entiers)], entiers[0], entiers[0]
        elif operation in ("lineTo", "curveTo", "qCurveTo"):
            if any(point != precedent for point in entiers):
                operations.append((operation, entiers))
                precedent = entiers[-1]
        elif operation in ("closePath", "endPath"):
            # Un dernier segment droit qui revient au départ est déjà assuré par la fermeture
            if len(operations) > 1 and operations[-1][0] == "lineTo" and operations[-1][1][0] == depart:
                operations.pop()
            if len(operations) > 2:
                for nom, arguments in operations:
                    getattr(stylo, nom)(*arguments)
                stylo.closePath()
            operations = []


def ecrire_glyphe(police, nom, point_code, traits, chasse, ancres, reglages: Reglages, graine: str) -> None:
    contour = dessiner(traits, reglages, graine=graine)
    glyphe = police[nom] if nom in police else police.newGlyph(nom)
    glyphe.clearContours()
    glyphe.clearAnchors()
    tracer_proprement(contour, glyphe.getPen())
    glyphe.width = round(chasse)
    glyphe.unicodes = [point_code] if point_code else []
    for nom_ancre, (x, y) in ajuster_ancres(contour, ancres).items():
        glyphe.appendAnchor({"name": nom_ancre, "x": round(x), "y": round(y)})


def est_lettre(point_code: int | None) -> bool:
    return bool(point_code) and unicodedata.category(chr(point_code))[0] == "L"


def ecrire(chemin_ufo: str, reglages: Reglages = Reglages()) -> None:
    charger_glyphes()
    police = ufoLib2.Font.open(chemin_ufo)
    appliquer_metriques(police)
    nb_alternances = nb_chats = 0
    for nom, (point_code, dessin) in GLYPHES.items():
        traits, chasse, ancres = dessin()
        ecrire_glyphe(police, nom, point_code, traits, chasse, ancres, reglages, graine=nom)
        if not est_lettre(point_code):
            continue
        # Alternances : même squelette, autre graine, donc un autre tracé de pinceau
        for suffixe in ALTERNANCES:
            ecrire_glyphe(police, f"{nom}.{suffixe}", None, traits, chasse, ancres, reglages, graine=f"{nom}.{suffixe}")
            nb_alternances += 1
        # Chats complets : la même lettre avec moustaches, si elle a un visage
        glyphes_module.MOUSTACHES = True
        traits_chat, _, _ = dessin()
        glyphes_module.MOUSTACHES = False
        if len(traits_chat) > len(traits):
            ecrire_glyphe(police, f"{nom}.ss01", None, traits_chat, chasse, ancres, reglages, graine=nom)
            nb_chats += 1
    police.save()
    print(f"{len(GLYPHES)} glyphes, {nb_alternances} alternances, {nb_chats} chats complets écrits dans {chemin_ufo}")


if __name__ == "__main__":
    ecrire(sys.argv[1])
