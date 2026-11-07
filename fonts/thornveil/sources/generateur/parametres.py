"""Décisions chiffrées d'Thornveil (documentation/specification.md) : une seule source de vérité.

Seules les deux graisses extrêmes sont saisies ; toute autre graisse, dont le maître Regular,
est obtenue par interpolation linéaire.
"""

METRIQUES = {
    "hauteur_x": 520,
    "hauteur_capitale": 700,
    "ascendante": 770,
    "descendante": -230,
    "depassement_pointe": 12,
    "ligne_haut": 1000,   # typo = hhea ; (1000 - 300) / 2 = 350 = capitale / 2
    "ligne_bas": -300,
}

GRAISSE_MIN, GRAISSE_DEFAUT, GRAISSE_MAX = 300, 400, 900
MAITRES_EXTREMES = {
    GRAISSE_MIN: {
        "fut": 80,            # fût bas de casse
        "delie": 30,          # délié de construction, jamais sous 30 (favicon)
        "ornement": 18,       # délié des épines et paraphes
        "contrepoincon": 125, # blanc entre les fûts de n
        "epine": 120,         # longueur d'une épine par défaut
        "approche": 45,       # point de départ, recalculé par espacer.py
    },
    GRAISSE_MAX: {
        "fut": 200,
        "delie": 50,
        "ornement": 26,
        "contrepoincon": 200,
        "epine": 155,
        "approche": 45,
    },
}
COUPE_FIXE = 40               # part fixe de la taille en losange : visible même en Light
RAPPORT_COUPE = 0.4           # part proportionnelle au fût
RAPPORT_FUT_CAPITALE = 1.08   # les capitales paraissent sinon plus maigres

# Règle des hauteurs : épines droites en haut, épines gauches plus bas.
# Deux épines voisines (la droite d'une lettre, la gauche de la suivante) ne se font jamais face.
# La fraction s'applique à la hauteur d'x (minuscules, même à ascendante) ou de capitale.
HAUTEUR_EPINE = {1: 0.7, -1: 0.45}

NOMS_MAITRES = {GRAISSE_MIN: "Light", GRAISSE_DEFAUT: "Regular", GRAISSE_MAX: "Black"}
INSTANCES = {"Light": 300, "Regular": 400, "Medium": 500, "Bold": 700, "Black": 900}


def parametres(graisse: int) -> dict[str, float]:
    """Interpole linéairement les paramètres entre les deux graisses extrêmes."""
    t = (graisse - GRAISSE_MIN) / (GRAISSE_MAX - GRAISSE_MIN)
    bas, haut = MAITRES_EXTREMES[GRAISSE_MIN], MAITRES_EXTREMES[GRAISSE_MAX]
    p = {cle: bas[cle] + t * (haut[cle] - bas[cle]) for cle in bas}
    p["fut_capitale"] = p["fut"] * RAPPORT_FUT_CAPITALE
    return p | METRIQUES
