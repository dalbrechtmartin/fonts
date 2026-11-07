"""Générateur paramétrique d'Thornveil : écrit les glyphes dans les trois maîtres UFO et le designspace.

Modules :
- parametres.py : décisions chiffrées de la spécification (une seule source de vérité) ;
- primitives.py : formes de base et registre des glyphes ;
- minuscules.py, capitales.py, chiffres.py, ponctuation.py, accents.py, speciales.py, symboles.py,
  decor.py, ornees.py (ss01, ss04), renforcees.py (ss02) : dessin des glyphes ;
- composes_lettons.py : recompose les lettres lettones avec la virgule (après composer_accents.py).

Usage :
    python sources/generateur/thornveil.py sources/
"""

import sys
from pathlib import Path

import ufoLib2
from fontTools.designspaceLib import (
    AxisDescriptor,
    AxisLabelDescriptor,
    DesignSpaceDocument,
    InstanceDescriptor,
    SourceDescriptor,
)
from fontTools.pens.areaPen import AreaPen
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.reverseContourPen import ReverseContourPen

import accents  # noqa: F401  (enregistre les glyphes)
import capitales  # noqa: F401  (enregistre les glyphes)
import chiffres  # noqa: F401  (enregistre les glyphes)
import decor  # noqa: F401  (enregistre les glyphes)
import minuscules  # noqa: F401  (enregistre les glyphes)
import ornees  # noqa: F401  (enregistre les glyphes)
import ponctuation  # noqa: F401  (enregistre les glyphes)
import renforcees  # noqa: F401  (enregistre les glyphes)
import speciales  # noqa: F401  (enregistre les glyphes)
import symboles  # noqa: F401  (enregistre les glyphes)
from parametres import GRAISSE_DEFAUT, GRAISSE_MAX, GRAISSE_MIN, INSTANCES, NOMS_MAITRES, parametres
from primitives import DESSINS, Contour, Point, Trou

FAMILLE = "Thornveil"
# Version OpenType des sources (0.1.0 -> 0.100). Dans le dépôt fonts, release-please la fait évoluer
# dans police.json, et tools/polices.py la réécrit dans les fichiers compilés.
VERSION = (0, 100)


def arrondir(point: Point) -> Point:
    return round(point[0]), round(point[1])


def tracer(contour: Contour, stylo) -> None:
    """Trace en coordonnées entières, sans jamais sauter de point : tous les maîtres doivent garder
    exactement la même structure (un point qui retombe sur son voisin après arrondi reste un point)."""
    stylo.moveTo(arrondir(contour[0]))
    for element in contour[1:]:
        if element[0] == "c":
            stylo.curveTo(*(arrondir(point) for point in element[1:]))
        else:
            stylo.lineTo(arrondir(element))
    stylo.closePath()


def ecrire_maitre(chemin_ufo: Path, graisse: int) -> None:
    police = ufoLib2.Font.open(chemin_ufo)
    p = parametres(graisse)
    info = police.info
    info.styleName = NOMS_MAITRES[graisse]
    info.versionMajor, info.versionMinor = VERSION
    info.postscriptFontName = f"{FAMILLE}-{NOMS_MAITRES[graisse]}"
    info.openTypeOS2WeightClass = graisse
    info.xHeight, info.capHeight = p["hauteur_x"], p["hauteur_capitale"]
    info.ascender, info.descender = p["ascendante"], p["descendante"]
    info.openTypeOS2TypoAscender = info.openTypeHheaAscender = p["ligne_haut"]
    info.openTypeOS2TypoDescender = info.openTypeHheaDescender = p["ligne_bas"]
    info.openTypeOS2TypoLineGap = info.openTypeHheaLineGap = 0
    for nom, (point_code, dessiner) in DESSINS.items():
        contours, chasse, ancres_glyphe = dessiner(p)
        g = police[nom] if nom in police else police.newGlyph(nom)
        g.clearContours()
        g.clearAnchors()
        for contour in contours:
            enregistrement, mesure = RecordingPen(), AreaPen()
            tracer(contour, enregistrement)
            enregistrement.replay(mesure)
            # convention UFO : contours extérieurs antihoraires (aire positive), trous horaires
            voulu_positif = not isinstance(contour, Trou)
            stylo = g.getPen() if (mesure.value > 0) == voulu_positif else ReverseContourPen(g.getPen())
            enregistrement.replay(stylo)
        g.width = round(chasse)
        if point_code is None:
            g.unicodes = []
        else:
            g.unicodes = list(point_code) if isinstance(point_code, tuple) else [point_code]
        for nom_ancre, (x, y) in ancres_glyphe.items():
            g.appendAnchor({"name": nom_ancre, "x": round(x), "y": round(y)})
    police.save()


def ecrire_designspace(dossier: Path) -> None:
    doc = DesignSpaceDocument()
    axe = AxisDescriptor()
    axe.name, axe.tag = "Weight", "wght"
    axe.minimum, axe.default, axe.maximum = GRAISSE_MIN, GRAISSE_DEFAUT, GRAISSE_MAX
    # étiquettes de la table STAT : noms des graisses affichés par les logiciels
    axe.axisLabels = [AxisLabelDescriptor(name=style, userValue=graisse) for style, graisse in INSTANCES.items()]
    doc.addAxis(axe)
    for graisse, style in NOMS_MAITRES.items():
        source = SourceDescriptor()
        source.filename = f"{FAMILLE}-{style}.ufo"
        source.familyName, source.styleName = FAMILLE, style
        source.location = {"Weight": graisse}
        doc.addSource(source)
    for style, graisse in INSTANCES.items():
        instance = InstanceDescriptor()
        instance.familyName, instance.styleName = FAMILLE, style
        instance.postScriptFontName = f"{FAMILLE}-{style}"  # déclaré : sinon déduit de façon variable au build
        instance.filename = f"instances/{FAMILLE}-{style}.ufo"
        instance.location = {"Weight": graisse}
        # regroupement de styles (Windows, bureautique) : Regular et Bold forment le couple de base ;
        # les autres graisses sont chacune le « Regular » de leur propre famille
        if style in ("Regular", "Bold"):
            instance.styleMapFamilyName, instance.styleMapStyleName = FAMILLE, style.lower()
        else:
            instance.styleMapFamilyName, instance.styleMapStyleName = f"{FAMILLE} {style}", "regular"
        doc.addInstance(instance)
    doc.write(dossier / f"{FAMILLE}.designspace")


def main(dossier: str) -> None:
    racine = Path(dossier)
    for graisse, style in NOMS_MAITRES.items():
        ecrire_maitre(racine / f"{FAMILLE}-{style}.ufo", graisse)
    ecrire_designspace(racine)
    print(f"{len(DESSINS)} glyphes écrits dans {len(NOMS_MAITRES)} maîtres, designspace à jour")


if __name__ == "__main__":
    main(sys.argv[1])
