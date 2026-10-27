"""Espacement optique automatique par la méthode des surfaces (inspirée de HT Letterspacer).

L'œil juge la quantité de blanc entre deux lettres, pas la distance entre leurs points les plus proches.
Pour chaque côté de chaque lettre, on mesure ligne par ligne le blanc déjà présent dans son profil
(creux d'une ronde, vide sous une barre), plafonné à une profondeur maximale, puis on règle l'approche
pour que « approche + blanc moyen du profil » soit la même cible pour toutes les lettres.

Calibrage : on donne les approches voulues pour une lettre droite et une ronde (n:70 o:50, H:70 O:50) ;
le script cherche la profondeur maximale qui les respecte, puis l'applique à toute la catégorie.
Seule la zone de la ligne de base à la hauteur d'x (minuscules) ou de capitale (capitales) est mesurée :
les ornements au-dessus (accents, oreilles) ne comptent pas.

Ne touche que les lettres dessinées et leurs variantes (a.alt1, o.ss01 : espacées comme leur lettre de base),
pas les composés (relancer composer_accents.py ensuite), ni les chiffres tabulaires, la ponctuation, les symboles.

Usage :
    python espacer.py sources/MaPolice-Regular.ufo [--minuscules n:70 o:50] [--capitales H:70 O:50]
"""

import argparse
import unicodedata

import pathops
import ufoLib2

PAS_LIGNE = 10


def chemin_de(glyphe) -> pathops.Path:
    chemin = pathops.Path()
    glyphe.draw(chemin.getPen())
    return chemin


def profil(chemin: pathops.Path, bas: float, haut: float) -> list[tuple[float, float] | None]:
    """Pour chaque tranche horizontale de la zone : (encre la plus à gauche, encre la plus à droite) ou None."""
    gauche, _, droite, _ = chemin.bounds
    tranches = []
    y = bas
    while y < haut:
        bande = pathops.Path()
        stylo = bande.getPen()
        stylo.moveTo((gauche - 10, y))
        stylo.lineTo((droite + 10, y))
        stylo.lineTo((droite + 10, y + PAS_LIGNE))
        stylo.lineTo((gauche - 10, y + PAS_LIGNE))
        stylo.closePath()
        coupe = pathops.op(chemin, bande, pathops.PathOp.INTERSECTION)
        tranches.append((coupe.bounds[0], coupe.bounds[2]) if coupe.bounds != (0, 0, 0, 0) else None)
        y += PAS_LIGNE
    return tranches


def blanc_moyen(tranches, cote: str, profondeur: float) -> tuple[float, float]:
    """(bord extrême de l'encre, blanc moyen du profil plafonné à la profondeur) pour un côté."""
    avec_encre = [t for t in tranches if t]
    if cote == "gauche":
        bord = min(t[0] for t in avec_encre)
        creux = [min(t[0] - bord, profondeur) if t else profondeur for t in tranches]
    else:
        bord = max(t[1] for t in avec_encre)
        creux = [min(bord - t[1], profondeur) if t else profondeur for t in tranches]
    return bord, sum(creux) / len(creux)


def caractere_de(glyphe, police) -> str | None:
    """Caractère du glyphe, ou de sa lettre de base pour une variante sans Unicode (a.alt1 → a)."""
    if glyphe.unicodes:
        return chr(glyphe.unicodes[0])
    base = glyphe.name.split(".")[0]
    if base != glyphe.name and base in police and police[base].unicodes:
        return chr(police[base].unicodes[0])
    return None


def zone(glyphe, police) -> tuple[float, float]:
    haut = police.info.capHeight if unicodedata.category(caractere_de(glyphe, police)) == "Lu" else police.info.xHeight
    return 0, haut


def calibrer(police, droite: tuple[str, float], ronde: tuple[str, float]) -> tuple[float, float]:
    """(cible, profondeur) telles que la droite et la ronde gardent les approches voulues (côté gauche)."""
    meilleur = None
    for profondeur in range(20, 400, 5):
        mesures = {}
        for nom, _ in (droite, ronde):
            tranches = profil(chemin_de(police[nom]), *zone(police[nom], police))
            mesures[nom] = blanc_moyen(tranches, "gauche", profondeur)[1]
        cible = droite[1] + mesures[droite[0]]
        ecart = abs((cible - mesures[ronde[0]]) - ronde[1])
        if meilleur is None or ecart < meilleur[0]:
            meilleur = (ecart, cible, profondeur)
    return meilleur[1], meilleur[2]


def espacer_glyphe(glyphe, police, cible: float, profondeur: float) -> tuple[int, int]:
    tranches = profil(chemin_de(glyphe), *zone(glyphe, police))
    if not any(tranches):
        return None
    bord_gauche, blanc_gauche = blanc_moyen(tranches, "gauche", profondeur)
    bord_droit, blanc_droit = blanc_moyen(tranches, "droite", profondeur)
    approche_gauche, approche_droite = cible - blanc_gauche, cible - blanc_droit
    decalage = round(approche_gauche - bord_gauche)
    if decalage:
        for contour in glyphe.contours:
            for point in contour.points:
                point.x += decalage
        for ancre in glyphe.anchors:
            ancre.x += decalage
    glyphe.width = round(bord_droit + decalage + approche_droite)
    return round(approche_gauche), round(approche_droite)


def a_espacer(glyphe, police) -> bool:
    caractere = caractere_de(glyphe, police)
    if not caractere or glyphe.components or not glyphe.contours or glyphe.width == 0:
        return False
    return unicodedata.category(caractere) in ("Lu", "Ll")


def lire_reference(texte: str) -> tuple[str, float]:
    nom, valeur = texte.split(":")
    return nom, float(valeur)


def main() -> None:
    parseur = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parseur.add_argument("ufo")
    parseur.add_argument("--minuscules", nargs=2, default=["n:70", "o:50"], metavar=("DROITE:APPROCHE", "RONDE:APPROCHE"))
    parseur.add_argument("--capitales", nargs=2, default=["H:70", "O:50"], metavar=("DROITE:APPROCHE", "RONDE:APPROCHE"))
    args = parseur.parse_args()

    police = ufoLib2.Font.open(args.ufo)
    reglages = {}
    for categorie, references in (("Ll", args.minuscules), ("Lu", args.capitales)):
        cible, profondeur = calibrer(police, *map(lire_reference, references))
        reglages[categorie] = (cible, profondeur)
        print(f"{categorie} : cible {cible:.0f}, profondeur maximale {profondeur}")

    nb = 0
    for glyphe in police:
        if a_espacer(glyphe, police):
            cible, profondeur = reglages[unicodedata.category(caractere_de(glyphe, police))]
            if espacer_glyphe(glyphe, police, cible, profondeur):
                nb += 1
    police.save()
    print(f"{nb} lettres espacées. Relancer composer_accents.py pour mettre à jour les lettres composées.")


if __name__ == "__main__":
    main()
