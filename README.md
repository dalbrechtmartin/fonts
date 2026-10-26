# Polices

Les polices d'écriture que je dessine, réunies dans un seul dépôt : sources, outils de compilation,
versions, changelog et un site de présentation.

**Site : <https://dalbrechtmartin.github.io/fonts/>** (essai en ligne, glyphes, CSS à copier, téléchargement, historique).

## Polices

| Police | Version | Style | Licence |
| --- | --- | --- | --- |
| [Sorcelle](fonts/sorcelle/) | voir [`CHANGELOG`](fonts/sorcelle/CHANGELOG.md) | Pixel « lombarde arrondie », 3 graisses, pour les titres | OFL 1.1 |

Chaque version publiée a son zip (TTF + WOFF2 + licence + changelog) dans les
[releases](https://github.com/dalbrechtmartin/fonts/releases).

## Stack

- Compilation : [fontTools](https://github.com/fonttools/fonttools) + [Pillow](https://python-pillow.org/) (Python), WOFF2 via [brotli](https://github.com/google/brotli).
- Site : HTML, CSS et JavaScript sans dépendance, habillé avec mon design system **Grimoire** (copie dans [`site/grimoire/`](site/grimoire/)).
- CI/CD : [GitHub Actions](.github/workflows/) compile et vérifie toutes les polices à chaque push/PR,
  [release-please](.github/workflows/release-please.yml) gère les versions et les `CHANGELOG.md` police par police,
  [Pages](.github/workflows/pages.yml) publie le site, [Dependabot](.github/dependabot.yml) garde les dépendances à jour.

## Structure

```
fonts/
  <id>/                  une police par dossier
    font.json            nom, version, graisses, commande de build, textes du spécimen
    CHANGELOG.md         historique (tenu par release-please)
    OFL.txt              licence de la police
    README.md            notes de conception
    ...                  sources (planche, scripts, UFO, etc.)
    dist/                fichiers compilés (non versionnés)
tools/fonts.py           build, contrôles, zip, site, nouvelle police
site/                    page de présentation (lit fonts.json généré)
release-please-config.json, .release-please-manifest.json
```

## Installer

```bash
python -m venv .venv
# PowerShell : .venv\Scripts\Activate.ps1   |   Git Bash : source .venv/Scripts/activate
pip install -r requirements.txt
```

## Commandes

```bash
python tools/fonts.py list                 # polices et versions
python tools/fonts.py build [id ...]       # compile dans fonts/<id>/dist/
python tools/fonts.py check [id ...]       # noms, graisses, couverture du spécimen, version
python tools/fonts.py package <id>         # release/<id>-<version>.zip
python tools/fonts.py site                 # génère _site/ (fonts.json + polices + zips)
python -m http.server 8000 --directory _site   # puis http://localhost:8000
```

`check` vérifie entre autres que la version de `font.json` est la même que dans `.release-please-manifest.json`.

## Versions et changelog

Même principe que [λLens](https://github.com/dalbrechtmartin/Yonsei-Lab-Internship) : commits
[Conventional Commits](https://www.conventionalcommits.org/fr/) et [release-please](https://github.com/googleapis/release-please),
ici en **monorepo** : chaque police a sa propre version (semver), son `CHANGELOG.md` et ses tags (`sorcelle-v0.6.0`).

1. Travailler sur `develop` (ou une branche), avec des commits du type :
   - `feat(sorcelle): ajoute les lettres grecques` → version mineure (0.6.0 → 0.7.0)
   - `fix(sorcelle): referme la panse du g` → correctif (0.6.0 → 0.6.1)
   - `feat(sorcelle)!: ...` ou `BREAKING CHANGE:` → majeure (mineure tant qu'on est en 0.x)
   - `chore:`, `docs:`, `ci:` → pas de nouvelle version

   C'est le **dossier** touché par le commit qui décide de la police concernée ; le scope `(sorcelle)` sert à la lecture.
2. Fusionner dans `main` (PR `develop` → `main`).
3. release-please ouvre une PR « chore(main): release sorcelle 0.7.0 » qui met à jour `font.json`,
   le manifest et `CHANGELOG.md`. Une PR par police modifiée.
4. Fusionner cette PR : release-please crée le tag et la release GitHub, la CI y attache le zip compilé
   à la nouvelle version, et le site se met à jour.

La version écrite dans les fichiers de police vient de `font.json` : ne pas la changer à la main.

## Ajouter une police

```bash
python tools/fonts.py new <id> "<Nom>"
```

Crée `fonts/<id>/` (font.json, CHANGELOG, README, OFL.txt) et la déclare à release-please, en version `0.0.0`
(non publiée, absente du site). Ensuite :

1. Remplir `font.json` (résumé, graisses, spécimen) et la ligne Copyright de `OFL.txt`.
2. Soit mettre les `.ttf` et `.woff2` déjà compilés dans `fonts/<id>/prebuilt/`
   (nommés `<Nom sans espaces>-<Graisse>.ttf`), soit ajouter une commande `"build"` à `font.json`
   (`{dist}` = dossier de sortie, voir Sorcelle).
3. `python tools/fonts.py build <id> && python tools/fonts.py check <id>`
4. Committer avec `feat(<id>): première version` : la release PR proposera la 0.1.0.

Pour une police qui a déjà un historique, mettre directement sa version dans `font.json` et dans
`.release-please-manifest.json`, écrire son `CHANGELOG.md`, puis créer le tag `<id>-v<version>`
pour que release-please reparte de là.

## Licences

- **Polices** : [SIL Open Font License 1.1](https://openfontlicense.org), voir le `OFL.txt` de chaque police.
  Utilisation libre, y compris commerciale ; une police ne se vend pas seule et garde ses crédits.
- **Code** (outils, site) : [BSD 3-Clause](LICENSE).
- **Grimoire** (`site/grimoire/`) : design system de mon portfolio ; polices Alegreya et Atkinson Hyperlegible
  (OFL) chargées depuis Google Fonts, icônes [Phosphor](https://phosphoricons.com/) (MIT).
