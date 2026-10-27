# Polices

Les polices d'écriture que je dessine : sources, versions, changelog et spécimens.

**Site : <https://polices.danaedev.fr/>** (essai en ligne, glyphes, CSS à copier, téléchargement, historique).

| Police | Style | Licence |
| --- | --- | --- |
| [Griffonne](fonts/griffonne/) | Pinceau irrégulier où chaque lettre cache un chat ; GF Latin Core, `calt` `ss01` `case` `zero` | OFL 1.1 |
| [Sorcelle](fonts/sorcelle/) | Pixel « lombarde arrondie », 3 graisses, GF Latin Core, pour les titres | OFL 1.1 |
| [Tendrille](fonts/tendrille/) | Semi-manuscrite romantique à la plume, points et fins de mots en cœur ; GF Latin Core, `calt` `case` `tnum` `zero` `ss01` `ss02` `ss04` `ss05` | OFL 1.1 |
| [Tendrille Texte](fonts/tendrille-texte/) | La sobre de Tendrille, pour les petites tailles et la malvoyance ; GF Latin Core | OFL 1.1 |

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="fonts/griffonne/images/apercu-sombre.png">
  <img src="fonts/griffonne/images/apercu-clair.png" alt="Le mot Griffonne écrit au pinceau, lettres coiffées d'oreilles de chat avec des yeux dans les panses, suivi de la phrase « L'été, la petite chatte grimpe au balcon ! ».">
</picture>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="fonts/sorcelle/images/apercu-sombre.png">
  <img src="fonts/sorcelle/images/apercu-clair.png" alt="Le mot Sorcelle en lettres pixel de style lombarde, suivi de la ligne « Danaé Albrecht--Martin ✦ Projets · Créations · Réseaux ».">
</picture>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="fonts/tendrille/images/apercu-sombre.png">
  <img src="fonts/tendrille/images/apercu-clair.png" alt="Le mot Tendrille en écriture manuscrite à la plume, suivi de la phrase « Mon cœur, l’été à Noël » dit Yvon à Paul, où les points des i et la fin des mots dessinent de petits cœurs.">
</picture>

Chaque version publiée a son zip (TTF, WOFF2, OTF quand la police en a un, licence, changelog) dans les
[releases](https://github.com/dalbrechtmartin/fonts/releases).

## Utiliser une police sur un site

Chaque police a un `index.css` (toutes les graisses) et une feuille par graisse (`400.css`, `700.css`…).

- Sans rien installer, depuis le site :

  ```css
  @import url("https://polices.danaedev.fr/fonts/sorcelle/index.css");
  ```

- Avec npm (paquets `@danaedev/<id>`) :

  ```bash
  npm i @danaedev/sorcelle
  ```

  ```js
  import "@danaedev/sorcelle";          // toutes les graisses
  import "@danaedev/sorcelle/700.css";  // seulement Bold
  ```

## Lancer en local

```bash
python -m venv .venv
source .venv/Scripts/activate            # PowerShell : .venv\Scripts\Activate.ps1
pip install -r requirements.txt
python tools/polices.py construire       # compile chaque police dans fonts/<id>/dist/
python tools/polices.py site             # génère _site/ : pages, polices.json, polices, CSS, zips, image de partage, sitemap
python tools/polices.py npm sorcelle     # prépare le paquet npm dans npm/sorcelle/
python -m http.server 8000 --directory _site
```

Puis ouvrir <http://localhost:8000/> : les liens du site partent du chemin de `URL_SITE` (`tools/polices.py`), ici la
racine du domaine.

Tester l'image servie en production (nginx, port 8080) :

```bash
docker build -t polices .
docker run --rm -p 8080:8080 polices
```

## Vérifier

```bash
python tools/polices.py verifier         # toutes les polices, ou : verifier sorcelle
```

Contrôle les clés de `police.json` (dont `usages` et `styles`, parmi les listes `USAGES` et `STYLES`), la licence, le
changelog, la famille et la graisse de chaque fichier, les glyphes du spécimen, la révision écrite dans la police et
l'accord avec `.release-please-manifest.json`. Code de sortie 1 en cas d'erreur.

### Hooks Git

Une fois par poste, depuis la racine (Node 20 ou plus) :

```bash
npm install                              # lefthook et commitlint, puis installe les hooks
pip install -r requirements-dev.txt      # ruff
winget install Gitleaks.Gitleaks         # macOS : brew install gitleaks
```

À chaque commit : `ruff check` sur les fichiers Python indexés et `gitleaks` (secrets) ; le message doit suivre
Conventional Commits (`commitlint`). Lint de tout le dépôt : `ruff check .`.

## Déploiement

Le site est servi par une image Docker (`Dockerfile` : construction Python, puis nginx non root sur le port 8080,
`nginx/`) que Dokploy reconstruit à chaque push :

| Environnement | Branche   | Particularité                  |
| ------------- | --------- | ------------------------------ |
| Recette       | `develop` | Protégée par mot de passe      |
| Production    | `main`    | `polices.danaedev.fr`         |

nginx ajoute les en-têtes de sécurité et autorise les autres sites à charger `/fonts/` (CORS), pour les `@import`.

Versions et paquets passent par GitHub Actions, sans variable ni secret :

- [`ci.yml`](.github/workflows/ci.yml) : `construire`, `verifier` et `site` à chaque push et PR vers `main` et `develop`
  (sauf les PR de version, vérifiées au push).
- [`release-please.yml`](.github/workflows/release-please.yml) : ouvre la PR de version, crée la release, y joint le zip et publie le paquet npm (trusted publishing, sans secret).

Réglages du dépôt en place :

- `main` protégée : PR obligatoire, ni push forcé ni suppression, règle appliquée aussi aux admins ;
- Actions avec les droits en écriture et l'autorisation de créer des PR (nécessaire à release-please).

## Maintenance

### Publier une nouvelle version

Chaque police a sa propre version (semver), son `CHANGELOG.md` et ses tags (`griffonne-v1.0.0`), gérés par
[release-please](https://github.com/googleapis/release-please) à partir des [Conventional Commits](https://www.conventionalcommits.org/fr/).

1. Travailler sur `develop`. C'est le dossier touché qui désigne la police ; le type fixe la version :
   - `feat(sorcelle): …` → mineure (0.6.0 → 0.7.0) ;
   - `fix(sorcelle): …` → correctif (0.6.0 → 0.6.1) ;
   - `feat(sorcelle)!: …` → majeure (mineure tant qu'on est en 0.x) ;
   - `refactor`, `docs`, `chore`, `ci` → pas de version.
2. Ouvrir une PR `develop` → `main`, avec un titre libre (un titre `feat(…)` serait compté comme un commit de plus
   dans le CHANGELOG), et la fusionner une fois la CI verte.
3. release-please ouvre une PR par police modifiée (version dans `police.json`, manifeste, `CHANGELOG.md`).
   Sa CI n'est pas lancée (`paths-ignore` de `ci.yml`) : lancer `construire` et `verifier` sur sa branche.
4. Avant de la fusionner, décrire la version en français pour le site dans `police.json` de sa branche, clé `notes`
   (`{"1.2.0": {"Nouveautés": ["…"], "Corrections": ["…"]}}`). Sans note, le site affiche les messages de commit ;
   `verifier` refuse une note pour une version absente du CHANGELOG.
5. La fusionner : tag, release et zip, puis le site se met à jour. Deux PR de version ouvertes ensemble entrent en
   conflit sur le manifeste après la première fusion : intégrer `main` dans la seconde et garder les deux versions.

La version écrite dans les fichiers de police vient toujours de `police.json` : `construire` l'écrit aussi dans les
polices fournies compilées (Griffonne), et `verifier` refuse un écart.

### Ajouter une police

```bash
python tools/polices.py nouvelle <id> "<Nom>"
```

Crée `fonts/<id>/` (police.json, CHANGELOG, README, OFL.txt) et la déclare à release-please en `0.0.0` : non publiée,
absente du site. La commande affiche ensuite les étapes : compléter `police.json` (dont `usages` et `styles`, qui
alimentent les filtres de l'accueil, `langues`, affichées sur le site avec une phrase par langue tirée de
`PHRASES_LANGUES`, et pour chaque fonction OpenType `libelle`, `description` et un `exemple` court : le site y marque
les signes qui changent, calculés avec HarfBuzz), ajouter les fichiers compilés dans `compilees/` (ou une commande
`construction`), vérifier, puis committer `feat(<id>): première version`.

### Publier une police sur npm pour la première fois

npm ne permet de déclarer la publication depuis GitHub Actions (trusted publishing) que pour un paquet qui existe déjà :

1. être membre de l'organisation npm `danaedev`, avec la 2FA activée, et connectée (`npm login`) ;
2. publier la première version à la main :

   ```bash
   python tools/polices.py npm <id>
   npm publish ./npm/<id> --access public
   ```

3. autoriser `release-please.yml` à publier le paquet (`npm trust github`, 2FA demandée ; `--essai` pour voir sans
   rien changer) :

   ```bash
   python tools/polices.py npm-confiance <id>
   ```

Les versions suivantes partent ensuite avec la release. La première doit arriver dans les 2 jours, sinon l'autorisation
expire : `npm trust list @danaedev/<id>`, `npm trust revoke @danaedev/<id> --id=<id-confiance>`, puis la recréer.

Les images du README d'une police se régénèrent avec `python tools/polices.py apercus <id>`.

### Dépendances

Dependabot propose chaque semaine, sur `develop`, les mises à jour pip et GitHub Actions.

## Structure

```
fonts/<id>/        une police : police.json, CHANGELOG.md, OFL.txt, README.md, sources et scripts
tools/polices.py   construire, vérifier, empaqueter, site, paquet npm, aperçus, nouvelle police
site/modeles/      pages du site (Jinja) : accueil, une page par police, ses versions, 404 ; rendues par la commande site
site/              CSS, interactions (site.js) et copie du design system Grimoire
Dockerfile         image du site : construction des polices et du site, puis nginx
nginx/             configuration nginx : cache, CORS de /fonts/, en-têtes de sécurité
```

## Licences

- **Polices** : [SIL Open Font License 1.1](https://openfontlicense.org), voir le `OFL.txt` de chaque police.
- **Code** (outils, site) : [BSD 3-Clause](LICENSE).
- **Grimoire** (`site/grimoire/`, `site/icones.svg`) : design system de mon portfolio ; polices Alegreya et Atkinson
  Hyperlegible (OFL) chargées depuis Google Fonts, icônes [Phosphor](https://phosphoricons.com/) (MIT).
