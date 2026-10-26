"""Crénage mesuré : paires choisies, valeur calculée par la méthode des surfaces, appliquée par classes.

La mesure est exactement celle d'espacer.py (même profondeur maximale, même calibrage) : le blanc d'une
paire = approches dans la zone + creux de chaque profil plafonnés. Une paire que l'espacement règle déjà
(co, ae) obtient donc zéro ; seules les vraies interactions sont crénées : capitale contre minuscule (To),
diagonales (AV), ponctuation basse ou haute (T. L’).
Référence : nn pour les minuscules, HH pour les capitales.
Deux corrections classiques : la surface est amortie (× 0,7, sinon on sur-crène : To) ; et la plus courte
distance entre les deux lettres, comparée à celle de la référence, capte l'emboîtement des diagonales (AV),
que la surface ne voit pas. On garde le plus fort des deux.
Zone mesurée : hauteur des capitales si les deux le sont, hauteur d'x sinon ; pour la ponctuation,
les lignes où elle a de l'encre (le point au pied, l'apostrophe en haut).
Garde-fous : écart minimal sur toute la hauteur (ornements compris), bornes, seuil de visibilité.
Classes : chaque lettre de base et ses composés (e, é, è…) partagent le même crénage.

À lancer après espacer.py et composer_accents.py (le crénage dépend de l'espacement).

Usage :
    python crener.py sources/MaPolice-Regular.ufo [--ecart-minimal 30]
"""

import argparse
import unicodedata

import pathops
import ufoLib2

from espacer import calibrer, lire_reference

PAS_LIGNE = 10
BORNES = (-180, 40)
BORNES_PONCTUATION = (-100, 30)  # une apostrophe trop enfoncée disparaît (« Lété » au lieu de « L’été »)
SEUIL_VISIBLE = 15
AMORTI_SURFACE = 0.7
FACTEUR_DISTANCE = 0.4

GAUCHES = {
    "capitales": "A F K L P R T V W X Y C D O Q",
    "minuscules": "f r v w y k x a b c e o p",
    "ponctuation": "quoteright quotedblright guillemotleft guilsinglleft",
}
DROITES = {
    "capitales": "A C G J O Q S T U V W Y",
    "minuscules": "a c d e g o q s u v w y",
    "ponctuation": "period comma ellipsis quoteright quotedblright quotesingle quotedbl guillemotright guilsinglright hyphen",
}
PAIRES_A_EVITER = {("C", "C"), ("O", "O"), ("D", "O")}


def chemin_de(police, nom) -> pathops.Path:
    chemin = pathops.Path()
    police[nom].draw(chemin.getPen())
    return chemin


class Profils:
    """Profils gauche/droite de chaque glyphe, ligne par ligne, mis en cache."""

    def __init__(self, police, bas: int = -400, haut: int = 1100):
        self.police, self.bas, self.haut = police, bas, haut
        self.cache: dict[str, dict[int, tuple[float, float]]] = {}

    def de(self, nom: str) -> dict[int, tuple[float, float]]:
        if nom not in self.cache:
            chemin = chemin_de(self.police, nom)
            lignes = {}
            if chemin.bounds != (0, 0, 0, 0):
                gauche, bas, droite, haut = chemin.bounds
                for y in range(int(bas) // PAS_LIGNE * PAS_LIGNE, int(haut) + PAS_LIGNE, PAS_LIGNE):
                    bande = pathops.Path()
                    stylo = bande.getPen()
                    stylo.moveTo((gauche - 10, y))
                    stylo.lineTo((droite + 10, y))
                    stylo.lineTo((droite + 10, y + PAS_LIGNE))
                    stylo.lineTo((gauche - 10, y + PAS_LIGNE))
                    stylo.closePath()
                    coupe = pathops.op(chemin, bande, pathops.PathOp.INTERSECTION)
                    if coupe.bounds != (0, 0, 0, 0):
                        lignes[y] = (coupe.bounds[0], coupe.bounds[2])
            self.cache[nom] = lignes
        return self.cache[nom]


def blanc_de_paire(profils: Profils, gauche: str, droite: str, zone: list[int], profondeurs: tuple[float, float]) -> float:
    """Blanc moyen d'une paire, mesuré comme espacer.py : approches dans la zone + creux plafonnés."""
    pg, pd = profils.de(gauche), profils.de(droite)
    lignes_g, lignes_d = [y for y in zone if y in pg], [y for y in zone if y in pd]
    if not lignes_g or not lignes_d:
        return None
    bord_droit = max(pg[y][1] for y in lignes_g)
    bord_gauche = min(pd[y][0] for y in lignes_d)
    approches = profils.police[gauche].width - bord_droit + bord_gauche
    profondeur_g, profondeur_d = profondeurs
    creux_g = sum(min(bord_droit - pg[y][1], profondeur_g) if y in pg else profondeur_g for y in zone) / len(zone)
    creux_d = sum(min(pd[y][0] - bord_gauche, profondeur_d) if y in pd else profondeur_d for y in zone) / len(zone)
    return approches + creux_g + creux_d


def ecarts(profils: Profils, gauche: str, droite: str) -> dict[int, float]:
    """Écart horizontal entre les deux encres, pour chaque ligne où les deux en ont."""
    chasse = profils.police[gauche].width
    pg, pd = profils.de(gauche), profils.de(droite)
    return {y: chasse + pd[y][0] - pg[y][1] for y in pg.keys() & pd.keys()}


def zone_de(police, gauche: str, droite: str, profils: Profils) -> list[int]:
    for nom in (gauche, droite):
        if categorie(police, nom) == "ponctuation":
            return sorted(profils.de(nom))
    haut = police.info.capHeight if categorie(police, gauche) == categorie(police, droite) == "capitales" else police.info.xHeight
    return list(range(0, int(haut), PAS_LIGNE))


def categorie(police, nom: str) -> str:
    glyphe = police[nom]
    if not glyphe.unicodes:
        return "autre"
    code = unicodedata.category(chr(glyphe.unicodes[0]))
    return {"Lu": "capitales", "Ll": "minuscules"}.get(code, "ponctuation" if code[0] in "PS" else "autre")


def classes_de(police) -> dict[str, list[str]]:
    """Lettre de base → elle-même, ses composés et toutes leurs variantes (e, é, e.alt1, é.ss01…)."""
    classes = {g.name: [g.name] for g in police if not g.components and "." not in g.name}
    for glyphe in police:
        if glyphe.name in classes:
            continue
        racine = glyphe.name.split(".")[0]
        if racine in classes:
            classes[racine].append(glyphe.name)  # variante d'une lettre de base : a.alt1
        elif glyphe.components and glyphe.components[0].baseGlyph.split(".")[0] in classes:
            classes[glyphe.components[0].baseGlyph.split(".")[0]].append(glyphe.name)  # é, é.alt1
    return classes


def main() -> None:
    parseur = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parseur.add_argument("ufo")
    parseur.add_argument("--ecart-minimal", type=float, default=30, help="Distance minimale entre deux encres, ornements compris")
    parseur.add_argument("--minuscules", nargs=2, default=["n:70", "o:50"], help="Mêmes références que pour espacer.py")
    parseur.add_argument("--capitales", nargs=2, default=["H:70", "O:50"], help="Mêmes références que pour espacer.py")
    args = parseur.parse_args()

    police = ufoLib2.Font.open(args.ufo)
    profils = Profils(police)
    profondeur = {cat: calibrer(police, *map(lire_reference, refs))[1]
                  for cat, refs in (("minuscules", args.minuscules), ("capitales", args.capitales))}
    references, distances_ref = {}, {}
    for cat, nom in (("capitales", args.capitales[0].split(":")[0]), ("minuscules", args.minuscules[0].split(":")[0])):
        zone = list(range(0, int(police.info.capHeight if cat == "capitales" else police.info.xHeight), PAS_LIGNE))
        references[cat] = blanc_de_paire(profils, nom, nom, zone, (profondeur[cat], profondeur[cat]))
        distances_ref[cat] = min(v for y, v in ecarts(profils, nom, nom).items() if y in zone)

    gauches = [n for liste in GAUCHES.values() for n in liste.split() if n in police]
    droites = [n for liste in DROITES.values() for n in liste.split() if n in police]
    crenage = {}
    for gauche in gauches:
        for droite in droites:
            if (gauche, droite) in PAIRES_A_EVITER:
                continue
            ref = "capitales" if categorie(police, gauche) == categorie(police, droite) == "capitales" else "minuscules"
            zone = zone_de(police, gauche, droite, profils)
            profondeurs = tuple(profondeur["capitales" if categorie(police, n) == "capitales" else "minuscules"]
                                for n in (gauche, droite))
            blanc = blanc_de_paire(profils, gauche, droite, zone, profondeurs) if zone else None
            if blanc is None:
                continue
            par_surface = (references[ref] - blanc) * AMORTI_SURFACE
            toutes = ecarts(profils, gauche, droite)
            dans_zone = [v for y, v in toutes.items() if y in zone]
            par_distance = min(0.0, (distances_ref[ref] - min(dans_zone)) * FACTEUR_DISTANCE) if dans_zone else 0.0
            bornes = BORNES_PONCTUATION if "ponctuation" in (categorie(police, gauche), categorie(police, droite)) else BORNES
            valeur = max(bornes[0], min(bornes[1], round(min(par_surface, par_distance))))
            if toutes:
                valeur = max(valeur, round(args.ecart_minimal - min(toutes.values())))
            if abs(valeur) >= SEUIL_VISIBLE:
                crenage[(gauche, droite)] = valeur

    classes = classes_de(police)
    police.groups.clear()
    police.kerning.clear()
    for nom in set(g for g, _ in crenage):
        police.groups[f"public.kern1.{nom}"] = classes.get(nom, [nom])
    for nom in set(d for _, d in crenage):
        police.groups[f"public.kern2.{nom}"] = classes.get(nom, [nom])
    for (gauche, droite), valeur in crenage.items():
        police.kerning[(f"public.kern1.{gauche}", f"public.kern2.{droite}")] = valeur
    police.save()

    print(f"{len(crenage)} paires de classes crénées ({len(gauches)} × {len(droites)} examinées).")
    for (gauche, droite), valeur in sorted(crenage.items(), key=lambda e: e[1])[:12]:
        print(f"  {gauche:>14} {droite:<14} {valeur:+d}")


if __name__ == "__main__":
    main()
