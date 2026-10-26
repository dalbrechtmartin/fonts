"""Compose les lettres accentuées à partir de la lettre de base et des diacritiques combinants.

Prérequis dans l'UFO :
- lettres de base avec des ancres « top », « bottom » (et « ogonek », « center » au besoin) ;
- diacritiques combinants (acutecomb, uni0302…) avec les ancres correspondantes « _top », « _bottom »…
- variantes « .case » des diacritiques pour les capitales (acutecomb.case), si dessinées ; elles servent
  aussi aux minuscules hautes dont l'ancre « top » atteint la hauteur de capitale (ĺ, ĥ) ;
- caron en apostrophe (ď ť ľ Ľ) : variante « <caron>.alt » avec l'ancre « _caronalt », posée sur
  l'ancre « caronalt » de la lettre ;
- dotlessi et uni0237 (ȷ) pour i et j accentués.

Les glyphes déjà dessinés ne sont jamais écrasés, sauf avec --remplacer.
Avec --variantes alt1 alt2 ss01, chaque composé existe aussi pour les variantes de sa lettre de base
(é.alt1 = e.alt1 + accent), afin que les fonctions calt et ss01 s'appliquent aux accentuées.

Usage :
    python composer_accents.py sources/MaPolice-Regular.ufo [--jeu GF_Latin_Core] [--remplacer]
"""

import argparse
import unicodedata

import ufoLib2
from fontTools.agl import UV2AGL
from ufoLib2.objects import Component

# Noms de production usuels des diacritiques combinants
NOMS_DIACRITIQUES = {
    0x0300: "gravecomb", 0x0301: "acutecomb", 0x0302: "circumflexcomb", 0x0303: "tildecomb",
    0x0304: "macroncomb", 0x0306: "brevecomb", 0x0307: "dotaccentcomb", 0x0308: "dieresiscomb",
    0x0309: "hookabovecomb", 0x030A: "ringcomb", 0x030B: "hungarumlautcomb", 0x030C: "caroncomb",
    0x031B: "horncomb", 0x0323: "dotbelowcomb", 0x0326: "commaaccentcomb", 0x0327: "cedillacomb",
    0x0328: "ogonekcomb",
}
BASES_SANS_POINT = {"i": "dotlessi", "j": "uni0237"}


def nom_glyphe(point_code: int) -> str:
    return UV2AGL.get(point_code, f"uni{point_code:04X}")


def decomposer(point_code: int) -> list[int] | None:
    """Décomposition canonique complète : [base, diacritique, diacritique…] ou None."""
    decomposition = unicodedata.decomposition(chr(point_code))
    if not decomposition or decomposition.startswith("<"):
        return None
    parties = [int(h, 16) for h in decomposition.split()]
    sous_decomposition = decomposer(parties[0])
    return (sous_decomposition or [parties[0]]) + parties[1:]


def trouver_glyphe(police: ufoLib2.Font, point_code: int) -> str | None:
    nom = NOMS_DIACRITIQUES.get(point_code, nom_glyphe(point_code))
    if nom in police:
        return nom
    return next((g.name for g in police if point_code in g.unicodes), None)


def ancres(glyphe) -> dict[str, tuple[float, float]]:
    return {a.name: (a.x, a.y) for a in glyphe.anchors}


def composer(police: ufoLib2.Font, point_code: int) -> str:
    """Retourne « ok » ou la raison pour laquelle le glyphe reste à dessiner."""
    parties = decomposer(point_code)
    if not parties:
        return "pas de décomposition canonique : à dessiner"
    base_point_code, diacritiques = parties[0], parties[1:]
    nom_base = trouver_glyphe(police, base_point_code)
    if not nom_base:
        return f"base « {chr(base_point_code)} » absente"
    hauteur_capitale = police.info.capHeight or 700
    ancre_haute = ancres(police[nom_base]).get("top", (0, 0))[1] >= hauteur_capitale
    est_capitale = unicodedata.category(chr(base_point_code)) == "Lu" or ancre_haute
    if nom_base in BASES_SANS_POINT and BASES_SANS_POINT[nom_base] in police:
        if any(ancre_de_diacritique(police, d, est_capitale) == "top" for d in diacritiques):
            nom_base = BASES_SANS_POINT[nom_base]

    composants = [Component(baseGlyph=nom_base)]
    ancres_courantes = dict(ancres(police[nom_base]))
    for point_diacritique in diacritiques:
        nom_diacritique = nom_du_diacritique(police, point_diacritique, est_capitale)
        if not nom_diacritique:
            return f"diacritique U+{point_diacritique:04X} absent"
        variante = variante_apostrophe(police, nom_base, point_diacritique)
        if variante:
            nom_diacritique = variante
        ancres_diacritique = ancres(police[nom_diacritique])
        ancre_attache = next((n[1:] for n in ancres_diacritique if n.startswith("_")), None)
        if not ancre_attache or ancre_attache not in ancres_courantes:
            return f"ancre « {ancre_attache or '?'} » manquante sur {nom_base} ou {nom_diacritique}"
        bx, by = ancres_courantes[ancre_attache]
        dx, dy = ancres_diacritique[f"_{ancre_attache}"]
        decalage = (bx - dx, by - dy)
        composants.append(Component(baseGlyph=nom_diacritique,
                                     transformation=(1, 0, 0, 1, *decalage)))
        # Empilement (ǖ, ệ) : le diacritique suivant s'accroche au-dessus de celui-ci
        for nom_ancre, (ax, ay) in ancres_diacritique.items():
            if not nom_ancre.startswith("_"):
                ancres_courantes[nom_ancre] = (ax + decalage[0], ay + decalage[1])

    nom = nom_glyphe(point_code)
    glyphe = police[nom] if nom in police else police.newGlyph(nom)
    glyphe.clearContours()
    glyphe.clearComponents()
    glyphe.components.extend(composants)
    glyphe.width = police[nom_base].width
    glyphe.unicodes = [point_code]
    return "ok"


def variante_apostrophe(police: ufoLib2.Font, nom_base: str, point_code: int) -> str | None:
    """Caron en apostrophe (ď ť ľ Ľ) si la lettre a une ancre « caronalt » et la variante existe."""
    if point_code != 0x30C or "caronalt" not in ancres(police[nom_base]):
        return None
    nom = f"{trouver_glyphe(police, point_code)}.alt"
    return nom if nom in police else None


def nom_du_diacritique(police: ufoLib2.Font, point_code: int, est_capitale: bool) -> str | None:
    nom = trouver_glyphe(police, point_code)
    if nom and est_capitale and f"{nom}.case" in police:
        return f"{nom}.case"
    return nom


def ancre_de_diacritique(police: ufoLib2.Font, point_code: int, est_capitale: bool) -> str | None:
    nom = nom_du_diacritique(police, point_code, est_capitale)
    if not nom:
        return None
    return next((n[1:] for n in ancres(police[nom]) if n.startswith("_")), None)


def composer_variantes(police: ufoLib2.Font, suffixes: list[str]) -> int:
    """é.alt1 = e.alt1 + accents de é, pour chaque composé dont la lettre de base a la variante."""
    nb = 0
    composes = [g for g in police if g.components and g.unicodes and "." not in g.name]
    for compose in composes:
        base = compose.components[0].baseGlyph
        for suffixe in suffixes:
            base_variante = f"{base}.{suffixe}"
            if base_variante not in police:
                continue
            nom = f"{compose.name}.{suffixe}"
            variante = police[nom] if nom in police else police.newGlyph(nom)
            variante.clearContours()
            variante.clearComponents()
            ancres_variante = ancres(police[base_variante])
            ancres_base = ancres(police[base])
            variante.components.append(Component(baseGlyph=base_variante))
            for composant in compose.components[1:]:
                # L'accent suit le déplacement de son ancre entre la lettre et sa variante
                nom_ancre = premiere_ancre_de(police, composant.baseGlyph)
                bx, by = ancres_base.get(nom_ancre, (0, 0))
                vx, vy = ancres_variante.get(nom_ancre, (bx, by))
                dx, dy = composant.transformation[4:]
                variante.components.append(Component(baseGlyph=composant.baseGlyph,
                                                     transformation=(1, 0, 0, 1, dx + vx - bx, dy + vy - by)))
            variante.width = police[base_variante].width
            nb += 1
    return nb


def premiere_ancre_de(police: ufoLib2.Font, nom_diacritique: str) -> str | None:
    """Ancre de la lettre à laquelle le diacritique s'accroche (« _top » → « top »)."""
    return next((n[1:] for n in ancres(police[nom_diacritique]) if n.startswith("_")), None)


def cibles(police: ufoLib2.Font, jeu: str | None) -> list[int]:
    if jeu:
        import glyphsets
        points_codes = glyphsets.unicodes_per_glyphset(jeu)
    else:
        points_codes = range(0x00C0, 0x0250)
    return sorted(p for p in points_codes if decomposer(p) or unicodedata.category(chr(p)).startswith("L"))


def main() -> None:
    parseur = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parseur.add_argument("ufo")
    parseur.add_argument("--jeu", help="Jeu de glyphes Google Fonts visé, ex. GF_Latin_Core")
    parseur.add_argument("--remplacer", action="store_true", help="Recomposer aussi les glyphes existants")
    parseur.add_argument("--variantes", nargs="*", default=[], help="Suffixes de variantes à composer aussi, ex. alt1 alt2 ss01")
    args = parseur.parse_args()

    police = ufoLib2.Font.open(args.ufo)
    deja_dessines = {u for g in police for u in g.unicodes if not g.components}
    composes, a_dessiner = [], {}
    for point_code in cibles(police, args.jeu):
        if point_code in deja_dessines and not args.remplacer:
            continue
        resultat = composer(police, point_code)
        if resultat == "ok":
            composes.append(chr(point_code))
        else:
            a_dessiner[chr(point_code)] = resultat
    nb_variantes = composer_variantes(police, args.variantes)
    police.save()

    print(f"Composés ({len(composes)}) : {''.join(composes)}")
    if args.variantes:
        print(f"Variantes composées : {nb_variantes}")
    if a_dessiner:
        print(f"\nReste à traiter ({len(a_dessiner)}), par cause :")
        par_cause: dict[str, list[str]] = {}
        for caractere, raison in a_dessiner.items():
            par_cause.setdefault(raison, []).append(caractere)
        for raison, caracteres in sorted(par_cause.items(), key=lambda e: -len(e[1])):
            print(f"  {raison} ({len(caracteres)}) : {''.join(caracteres)}")


if __name__ == "__main__":
    main()
