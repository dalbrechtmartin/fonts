"""Diacritiques combinants de Thornveil (chasse nulle, accrochés par ancres).

- Chaque diacritique haut existe en deux tailles : bas de casse, et « .case » plus bas et plus plat
  pour les capitales et les minuscules à ascendante (le composeur choisit selon l'ancre « top »).
- Les ancres « _top », « _bottom », « _ogonek », « _caronalt » s'accrochent aux ancres des lettres ;
  l'ancre « top » d'un diacritique permet d'en empiler un second.
- caroncomb.alt : caron en apostrophe pour ď ť ľ Ľ.
"""

from primitives import Trou, bande, decaler, fut, glyphe, losange, pivoter, trait, transformer

LONGUEUR_ACCENT = 150   # hauteur d'un accent haut en bas de casse
APLATISSEMENT_CASE = 0.72


def ecart_minuscule(p: dict) -> float:
    """Blanc entre la hauteur d'x et l'accent ; grandit avec la graisse pour ne pas coller en Black."""
    return 55 + p["fut"] * 0.35


def ecart_capitale(p: dict) -> float:
    """Plus serré au-dessus des capitales."""
    return 35 + p["fut"] * 0.12


def rayon_point(p: dict) -> float:
    return 30 + p["fut"] * 0.4


def point(cx: float, cy: float, p: dict) -> list:
    r = rayon_point(p)
    return losange(cx, cy, r * 0.85, r)


# Formes des accents hauts : (p, base, longueur) -> contours, posés au-dessus de y = base, centrés sur x = 0

def forme_aigu(p, base, L):
    return [trait((-L * 0.18, base), (L * 0.35, base + L), p["fut"] * 0.6)]


def forme_grave(p, base, L):
    return transformer(forme_aigu(p, base, L), lambda q: (-q[0], q[1]))


def forme_circonflexe(p, base, L):
    largeur = p["fut"] * 0.5
    return [trait((-L * 0.6, base), (0, base + L * 0.85), largeur), trait((L * 0.6, base), (0, base + L * 0.85), largeur)]


def forme_caron(p, base, L):
    return pivoter(forme_circonflexe(p, base, L), 0, base + L * 0.425)


def forme_trema(p, base, L):
    r = rayon_point(p)
    return [point(-r * 1.6, base + r, p), point(r * 1.6, base + r, p)]


def forme_point(p, base, L):
    return [point(0, base + rayon_point(p), p)]


def epaisseur_trait_horizontal(p):
    return p["delie"] * 1.4 + p["fut"] * 0.2


def forme_tilde(p, base, L):
    e = epaisseur_trait_horizontal(p)
    haut, bas = base + L * 0.5 + e, base + e
    return [bande((-L * 0.7, bas), (-L * 0.25, haut), e), bande((-L * 0.3, haut), (L * 0.3, bas), e),
            bande((L * 0.25, bas), (L * 0.7, haut), e)]


def forme_macron(p, base, L):
    e = epaisseur_trait_horizontal(p)
    return [bande((-L * 0.6, base + L * 0.3 + e), (L * 0.6, base + L * 0.3 + e), e)]


def forme_breve(p, base, L):
    e = epaisseur_trait_horizontal(p)
    return [bande((-L * 0.6, base + L * 0.6), (0, base + e), e), bande((0, base + e), (L * 0.6, base + L * 0.6), e)]


def forme_rond(p, base, L):
    # proportionné à la hauteur de l'accent : en Black, le rond du Å restait sous la boîte de ligne
    r = L * 0.4 + p["fut"] * 0.08
    # épaisseur proportionnée au rayon : le trou garde un rayon positif dans toutes les graisses
    e = r * 0.3 + p["fut"] * 0.05
    cy = base + r
    return [losange(0, cy, r, r), Trou(losange(0, cy, r - e * 1.2, r - e))]


def forme_double_aigu(p, base, L):
    return decaler(forme_aigu(p, base, L), -L * 0.35, 0) + decaler(forme_aigu(p, base, L), L * 0.35, 0)


def forme_virgule_retournee(p, base, L):
    """Virgule retournée au-dessus (ģ letton)."""
    r = rayon_point(p)
    cy = base + L * 0.4
    virgule = [point(0, cy, p), trait((-r * 0.3, cy), (r * 0.5, cy + r * 2.2), p["fut"] * 0.45)]
    return virgule


def accent_haut(nom: str, point_code: int, forme, avec_case: bool = True) -> None:
    """Enregistre un diacritique haut en bas de casse et, s'il sert aux capitales, sa variante « .case »."""

    def construire(p, base, longueur):
        contours = forme(p, base, longueur)
        hauts = [q[1] for c in contours for q in [e if e[0] != "c" else e[3] for e in c]]
        return contours, 0, {"_top": (0, base), "top": (0, max(hauts) + 30)}

    glyphe(nom, point_code)(lambda p: construire(p, p["hauteur_x"] + ecart_minuscule(p), LONGUEUR_ACCENT))
    if avec_case:
        glyphe(f"{nom}.case")(lambda p: construire(p, p["hauteur_capitale"] + ecart_capitale(p),
                                                    LONGUEUR_ACCENT * APLATISSEMENT_CASE))


for _nom, _code, _forme in [
    ("gravecomb", 0x300, forme_grave), ("acutecomb", 0x301, forme_aigu), ("circumflexcomb", 0x302, forme_circonflexe),
    ("tildecomb", 0x303, forme_tilde), ("macroncomb", 0x304, forme_macron), ("brevecomb", 0x306, forme_breve),
    ("dotaccentcomb", 0x307, forme_point), ("dieresiscomb", 0x308, forme_trema), ("ringcomb", 0x30A, forme_rond),
    ("hungarumlautcomb", 0x30B, forme_double_aigu), ("caroncomb", 0x30C, forme_caron),
]:
    accent_haut(_nom, _code, _forme)
accent_haut("uni0312", 0x312, forme_virgule_retournee, avec_case=False)  # ģ seulement, en minuscule


# Accents bas et apostrophe -------------------------------------------------------------------

@glyphe("commaaccentcomb", 0x326)
def dessiner_commaaccentcomb(p):
    """Virgule souscrite (ș ț roumains, ķ ļ ņ ŗ lettons) ; taille limitée pour rester dans la boîte de ligne."""
    r = 25 + p["fut"] * 0.2
    cy = -40 - r
    contours = [losange(0, cy, r * 0.85, r), trait((r * 0.3, cy), (-r * 0.5, cy - r * 2.2), p["fut"] * 0.45)]
    return contours, 0, {"_bottom": (0, 0)}


@glyphe("cedillacomb", 0x327)
def dessiner_cedillacomb(p):
    """Cédille anguleuse : petit fût sous la ligne, crochet vers la gauche."""
    largeur = p["fut"] * 0.5
    e = p["delie"] * 1.5
    contours = [
        fut(-largeur / 2, -125, 20, largeur),
        bande((-85, -140 + e), (largeur / 2, -105 + e), e),
    ]
    return contours, 0, {"_bottom": (0, 0)}


@glyphe("ogonekcomb", 0x328)
def dessiner_ogonekcomb(p):
    """Ogonek : crochet qui descend du pied droit de la lettre et repart vers la droite."""
    largeur = p["fut"] * 0.45
    e = p["delie"] * 1.4
    contours = [
        trait((0, 20), (-35, -115), largeur),
        bande((-35 - largeur / 2, -125 + e), (60, -90 + e), e),
    ]
    return contours, 0, {"_ogonek": (0, 0)}


@glyphe("caroncomb.alt")
def dessiner_caroncomb_alt(p):
    """Caron en apostrophe (ď ť ľ Ľ) : petite virgule dont le haut est à l'ancre."""
    r = rayon_point(p) * 0.7
    cx, cy = r * 0.85, -r
    contours = [losange(cx, cy, r * 0.85, r), trait((cx + r * 0.3, cy), (cx - r * 0.4, cy - r * 2), p["fut"] * 0.4)]
    return contours, 0, {"_caronalt": (0, 0)}
