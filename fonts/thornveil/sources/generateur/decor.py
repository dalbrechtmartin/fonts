"""Glyphes décoratifs de Thornveil, à placer autour des logos.

✦ ✧ étoiles en scintillement, ☽ ☾ croissants, ♥ cœur pointu, chauve-souris à ailes festonnées.
La chauve-souris a deux points de code : 🦇 (U+1F987), que certains systèmes affichent avec leur police
emoji en couleur, et U+E000 (zone privée), accès de secours toujours rendu avec Thornveil.
Dans un logo web, ces glyphes sont décoratifs : aria-hidden="true", le nom porté par le texte alternatif.
"""

from primitives import Trou, decaler, echelle, glyphe, transformer

K = 0.5523  # poignées d'un quart de cercle en courbes de Bézier cubiques


def centre(p: dict) -> float:
    return p["hauteur_capitale"] / 2


def ancres(chasse: float, p: dict) -> dict:
    return {"top": (chasse / 2, p["hauteur_capitale"]), "bottom": (chasse / 2, 0)}


def poser(contours: list, demi_largeur: float, p: dict):
    """Décale un dessin centré sur x = 0 pour lui donner ses approches."""
    g = p["approche"]
    chasse = 2 * (demi_largeur + g)
    return decaler(contours, demi_largeur + g, 0), chasse, ancres(chasse, p)


# Étoiles ---------------------------------------------------------------------------------------

def etoile(cy: float, rayon: float, p: dict) -> list:
    """Étoile à 4 branches aux côtés creusés, plus haute que large ; la taille s'épaissit avec la graisse."""
    taille = 0.06 + p["fut"] * 0.0004
    haut, cote = rayon, rayon * 0.72
    return [
        (0, cy + haut),
        ("c", (rayon * taille, cy + rayon * 0.25), (rayon * 0.2, cy + rayon * taille), (cote, cy)),
        ("c", (rayon * 0.2, cy - rayon * taille), (rayon * taille, cy - rayon * 0.25), (0, cy - haut)),
        ("c", (-rayon * taille, cy - rayon * 0.25), (-rayon * 0.2, cy - rayon * taille), (-cote, cy)),
        ("c", (-rayon * 0.2, cy + rayon * taille), (-rayon * taille, cy + rayon * 0.25), (0, cy + haut)),
    ]


@glyphe("uni2726", 0x2726)
def dessiner_etoile_pleine(p):
    rayon = p["hauteur_capitale"] * 0.5
    return poser([etoile(centre(p), rayon, p)], rayon * 0.72, p)


@glyphe("uni2727", 0x2727)
def dessiner_etoile_contour(p):
    rayon = p["hauteur_capitale"] * 0.5
    cy = centre(p)
    interieure = echelle([etoile(cy, rayon, p)], 0.55, 0, cy * 0.45)
    return poser([etoile(cy, rayon, p), Trou(interieure[0])], rayon * 0.72, p)


# Lunes -------------------------------------------------------------------------------------------

def croissant(cy: float, rayon: float, p: dict) -> list:
    """Croissant bombé à droite, cornes pointues à gauche (☽) ; centré sur x = 0."""
    epaisseur = rayon * 0.32 + p["fut"] * 0.5
    creux = rayon - epaisseur  # abscisse du bord intérieur au milieu
    return [
        (0, cy + rayon),
        ("c", (rayon * K, cy + rayon), (rayon, cy + rayon * K), (rayon, cy)),
        ("c", (rayon, cy - rayon * K), (rayon * K, cy - rayon), (0, cy - rayon)),
        ("c", (creux * 0.75, cy - rayon * 0.6), (creux, cy - rayon * 0.35), (creux, cy)),
        ("c", (creux, cy + rayon * 0.35), (creux * 0.75, cy + rayon * 0.6), (0, cy + rayon)),
    ]


@glyphe("uni263D", 0x263D)
def dessiner_premier_quartier(p):
    rayon = p["hauteur_capitale"] * 0.45
    contour = decaler([croissant(centre(p), rayon, p)], -rayon / 2, 0)
    return poser(contour, rayon / 2, p)


@glyphe("uni263E", 0x263E)
def dessiner_dernier_quartier(p):
    rayon = p["hauteur_capitale"] * 0.45
    contour = transformer(decaler([croissant(centre(p), rayon, p)], -rayon / 2, 0), lambda q: (-q[0], q[1]))
    return poser(contour, rayon / 2, p)


# Cœur ----------------------------------------------------------------------------------------------

@glyphe("heart", 0x2665)
def dessiner_coeur(p):
    """Cœur pointu à deux lobes, pointe aiguë en bas."""
    rayon = p["hauteur_capitale"] * 0.4
    cy = centre(p)
    creux = rayon * (0.42 - p["fut"] * 0.0003)  # le creux du haut se referme un peu en gras
    contour = [
        (0, cy - rayon),
        ("c", (rayon * 0.35, cy - rayon * 0.45), (rayon, cy - rayon * 0.05), (rayon, cy + rayon * 0.4)),
        ("c", (rayon, cy + rayon * 0.75), (rayon * 0.75, cy + rayon * 0.95), (rayon * 0.48, cy + rayon * 0.95)),
        ("c", (rayon * 0.2, cy + rayon * 0.95), (rayon * 0.05, cy + rayon * 0.75), (0, cy + creux)),
        ("c", (-rayon * 0.05, cy + rayon * 0.75), (-rayon * 0.2, cy + rayon * 0.95), (-rayon * 0.48, cy + rayon * 0.95)),
        ("c", (-rayon * 0.75, cy + rayon * 0.95), (-rayon, cy + rayon * 0.75), (-rayon, cy + rayon * 0.4)),
        ("c", (-rayon, cy - rayon * 0.05), (-rayon * 0.35, cy - rayon * 0.45), (0, cy - rayon)),
    ]
    return poser([contour], rayon, p)


# Chauve-souris ----------------------------------------------------------------------------------

# Demi-silhouette droite, du haut de la tête au bas du corps, en unités du rayon.
# Chaque segment : (point d'arrivée) ou ("c", poignée 1, poignée 2, point d'arrivée).
DEMI_CHAUVE_SOURIS = [
    (0.10, 0.48),                                          # pointe de l'oreille
    (0.17, 0.26),                                          # épaule
    ("c", (0.45, 0.30), (0.85, 0.55), (1.25, 0.50)),        # bord d'attaque de l'aile, jusqu'à la pointe
    ("c", (1.10, 0.28), (1.08, 0.10), (1.02, -0.08)),       # feston 1
    ("c", (0.95, 0.12), (0.78, 0.14), (0.70, -0.02)),       # feston 2
    ("c", (0.62, 0.12), (0.46, 0.10), (0.38, -0.10)),       # feston 3
    ("c", (0.30, 0.02), (0.18, -0.12), (0.12, -0.32)),      # flanc
    (0.0, -0.42),                                          # bas du corps
]
HAUT_TETE = (0.0, 0.30)


def symetrie(point):
    return (-point[0], point[1])


def silhouette_chauve_souris(rayon: float, cy: float, envergure: float) -> list:
    """Assemble la demi-silhouette droite et son miroir en un seul contour fermé."""
    def placer(q):
        return (q[0] * rayon * envergure, cy + q[1] * rayon)

    contour = [placer(HAUT_TETE)]
    for segment in DEMI_CHAUVE_SOURIS:
        contour.append(("c", *(placer(q) for q in segment[1:])) if segment[0] == "c" else placer(segment))
    # moitié gauche : mêmes segments parcourus à l'envers, en miroir
    depart = [HAUT_TETE] + [s[3] if s[0] == "c" else s for s in DEMI_CHAUVE_SOURIS]
    for i in range(len(DEMI_CHAUVE_SOURIS) - 1, -1, -1):
        segment, arrivee = DEMI_CHAUVE_SOURIS[i], symetrie(depart[i])
        if segment[0] == "c":
            contour.append(("c", placer(symetrie(segment[2])), placer(symetrie(segment[1])), placer(arrivee)))
        else:
            contour.append(placer(arrivee))
    return contour[:-1]  # le dernier point rejoint le premier : la fermeture du contour suffit


@glyphe("bat", (0x1F987, 0xE000))
def dessiner_chauve_souris(p):
    rayon = p["hauteur_capitale"] * 0.5
    envergure = 1 + p["fut"] * 0.0005  # ailes un peu plus larges en gras, pour garder les festons lisibles
    return poser([silhouette_chauve_souris(rayon, centre(p), envergure)], rayon * 1.25 * envergure, p)
