"""Géométrie partagée de la planche (extract.py et build.py)."""

PX = 30                 # 1 pixel de la police = 30 unités (grille de Jacquard 24)
COLS = 12               # caractères par ligne de planche
CELL_W = 48             # largeur d'une case, en pixels (Œ et Æ compris)
LABEL_H = 12            # bandeau d'étiquette en haut de chaque case
ASC_PX = 36             # place au-dessus de la ligne de base (accents des capitales)
DESC_PX = 10            # place sous la ligne de base
CELL_H = LABEL_H + ASC_PX + DESC_PX
ORIGIN_X = 4            # marge gauche : la colonne 0 du glyphe est à x0 + ORIGIN_X

# Couleurs des repères (tout ce qui n'est pas noir pur est ignoré par build.py)
GUIDE_BASE = (230, 80, 120, 255)    # ligne de base
GUIDE_CAP = (90, 160, 230, 255)     # hauteur des capitales
GUIDE_XH = (120, 200, 140, 255)     # hauteur des minuscules
GUIDE_LABEL = (150, 150, 150, 255)  # étiquettes et chasse d'origine

CHARSET = (
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "abcdefghijklmnopqrstuvwxyz"
    "0123456789"
    "ÀÂÄÇÉÈÊËÎÏÔÖÙÛÜŸŒÆ"
    "àâäçéèêëîïôöùûüÿœæ"
    ".,;:!?'’\"«»()[]-–—…&@#%*/+=_<>§©"
    "✦"
)


def cell_origin(index):
    """Coin gauche de la case et ordonnée de sa ligne de base sur la planche."""
    col, row = index % COLS, index // COLS
    x0 = col * CELL_W
    base_y = row * CELL_H + LABEL_H + ASC_PX
    return x0, base_y
