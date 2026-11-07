"""Outils du dépôt : construire, vérifier, empaqueter et présenter les polices de fonts/<id>/.

Usage (depuis la racine du dépôt) :
  python tools/polices.py lister
  python tools/polices.py construire [id ...]
  python tools/polices.py verifier [id ...]
  python tools/polices.py empaqueter <id> [--sortie dossier]
  python tools/polices.py site [--sortie _site]
  python tools/polices.py npm <id> [--sortie npm]
  python tools/polices.py npm-confiance <id> [--essai]
  python tools/polices.py apercus [id ...]
  python tools/polices.py tag <id>
  python tools/polices.py nouvelle <id> "<Nom>"
"""
import argparse
import datetime
import html
import json
import re
import shutil
import subprocess
import sys
import unicodedata
import zipfile
from pathlib import Path
from urllib.parse import urlparse

import uharfbuzz
from fontTools.ttLib import TTFont
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from PIL import Image, ImageDraw, ImageFont

RACINE = Path(__file__).resolve().parent.parent
POLICES = RACINE / "fonts"
SITE = RACINE / "site"
CONFIG_RELEASE = RACINE / "release-please-config.json"
MANIFESTE_RELEASE = RACINE / ".release-please-manifest.json"
URL_DEPOT = "https://github.com/dalbrechtmartin/fonts"
URL_SITE = "https://polices.danaedev.fr/"
PORTEE_NPM = "@danaedev"
AUTRICE = "Danaé ALBRECHT--MARTIN (https://danaedev.fr)"
WORKFLOW_PUBLICATION = "release-please.yml"
NON_PUBLIEE = "0.0.0"
CLES_OBLIGATOIRES = ("id", "nom", "version", "resume", "dessin", "licence", "graisses", "specimen")
EXTENSIONS = ("otf", "ttf", "woff2")
DOCUMENTS = ("OFL.txt", "OFL-FAQ.txt", "FONTLOG.txt", "AUTHORS.txt", "README.md", "CHANGELOG.md")
# Couleurs des thèmes Parchemin et Crypte de Grimoire (fond, encre, texte secondaire)
THEMES_APERCU = {"clair": ("#f1e9d8", "#1d1822", "#5a4f5f"), "sombre": ("#17141c", "#ece4d8", "#b3a9b8")}
DORURE = "#d4a03a"  # gilding de Grimoire : filets décoratifs
# Filtres « Usage » et « Style » de l'accueil : chaque police en choisit au moins un de chaque liste
USAGES = ("Titres", "Texte courant")
STYLES = ("Avec empattements", "Sans empattements", "Manuscrite", "Pixel", "Gothique")
POLICE_DES_TITRES = "sorcelle"  # titres du site (Grimoire)
MODELES = SITE / "modeles"  # pages du site (Jinja), rendues par la commande site
# Une phrase par langue, qui utilise ses lettres propres : essai et section Langues du site.
# Une langue listée dans police.json doit être ici, et sa phrase entièrement couverte (verifier).
PHRASES_LANGUES = {
    "français": ("fr", "Portez ce vieux whisky au juge blond qui fume\u202f!"),
    "anglais": ("en", "The quick brown fox jumps over the lazy dog."),
    "allemand": ("de", "Victor jagt zwölf Boxkämpfer quer über den großen Sylter Deich."),
    "espagnol": ("es", "El veloz murciélago hindú comía feliz cardillo y kiwi."),
    "polonais": ("pl", "Zażółć gęślą jaźń."),
    "tchèque": ("cs", "Příliš žluťoučký kůň úpěl ďábelské ódy."),
    "roumain": ("ro", "Muzicologă în bej vând whisky și tequila, preț fix."),
    "turc": ("tr", "Pijamalı hasta yağız şoföre çabucak güvendi."),
}
PHRASES_SIGNES = {
    "Alphabet": "ABCDEFGHIJKLMNOPQRSTUVWXYZ abcdefghijklmnopqrstuvwxyz",
    "Chiffres et signes": "0123456789 · 12,50 € · «\u202fOui\u202f!\u202f» — @ & ? (…)",
}


# --- Lecture -------------------------------------------------------------------------------------

def charger(id_police):
    chemin = POLICES / id_police / "police.json"
    if not chemin.exists():
        sys.exit(f"Police inconnue : {id_police} (pas de {chemin.relative_to(RACINE)})")
    police = json.loads(chemin.read_text(encoding="utf-8"))
    police["_dossier"] = chemin.parent
    return police


def tous_les_id():
    return sorted(chemin.parent.name for chemin in POLICES.glob("*/police.json"))


def dossier_compile(police):
    return police["_dossier"] / "dist"


def fichier_graisse(police, graisse, extension):
    return dossier_compile(police) / f"{police['nom'].replace(' ', '')}-{graisse['nom']}.{extension}"


def nom_du_tag(police):
    return f"{police['id']}-v{police['version']}"


def revision_opentype(version):
    """Semver -> révision OpenType (head.fontRevision, « Version 1.000 ») : 0.6.1 -> 0.601, 1.0.0 -> 1.000."""
    majeure, mineure, correctif = (int(partie) for partie in version.split("."))
    return f"{majeure}.{mineure}{correctif:02d}"


def nom_npm(police):
    return f"{PORTEE_NPM}/{police['id']}"


def feuilles_css(police):
    """{fichier: CSS} : une feuille par graisse (400.css, 700.css…) et index.css avec toutes, .woff2 à côté."""
    blocs = {}
    for graisse in police["graisses"]:
        blocs[f"{graisse['poids']}.css"] = (
            f'@font-face {{\n  font-family: "{police["nom"]}";\n'
            f'  src: url("{fichier_graisse(police, graisse, "woff2").name}") format("woff2");\n'
            f'  font-weight: {graisse["poids"]};\n  font-style: normal;\n  font-display: swap;\n}}\n')
    return {"index.css": "\n".join(blocs.values()), **blocs}


def ecrire_webfonts(police, dossier):
    """Copie les .woff2 et écrit leurs feuilles CSS dans dossier (site et paquet npm)."""
    for graisse in police["graisses"]:
        shutil.copy2(fichier_graisse(police, graisse, "woff2"), dossier)
    for nom, css in feuilles_css(police).items():
        (dossier / nom).write_text(css, encoding="utf-8")


# --- construire ----------------------------------------------------------------------------------

def construire(police):
    sortie = dossier_compile(police)
    if sortie.exists():
        shutil.rmtree(sortie)
    sortie.mkdir(parents=True)
    if "construction" in police:
        commande = [sys.executable if partie == "python" else partie.replace("{sortie}", str(sortie))
                    for partie in police["construction"]]
        print(f"[{police['id']}] {' '.join(police['construction'])}")
        subprocess.run(commande, cwd=police["_dossier"], check=True)
    else:
        compilees = police["_dossier"] / police.get("compilees", "compilees")
        for fichier in compilees.rglob("*"):
            if fichier.suffix.lstrip(".") in EXTENSIONS:
                shutil.copy2(fichier, sortie / fichier.name)
                ecrire_revision(sortie / fichier.name, police["version"])
        print(f"[{police['id']}] fichiers copiés depuis {compilees.relative_to(RACINE)}, "
              f"révision {revision_opentype(police['version'])}")


def ecrire_revision(fichier, version):
    """Écrit la version de police.json dans une police fournie compilée : head.fontRevision, noms 3 et 5."""
    fonte = TTFont(fichier)
    revision = revision_opentype(version)
    fonte["head"].fontRevision = float(revision)
    for nom in fonte["name"].names:
        if nom.nameID in (3, 5):
            nom.string = re.sub(r"\d+\.\d{3}", revision, nom.toUnicode(), count=1)
    fonte.save(fichier)


# --- verifier ------------------------------------------------------------------------------------

def verifier(police):
    erreurs = []
    id_police = police["id"]
    for cle in CLES_OBLIGATOIRES:
        if cle not in police:
            erreurs.append(f"police.json : clé « {cle} » manquante")
    if id_police != police["_dossier"].name:
        erreurs.append(f"police.json : id « {id_police} » ≠ dossier « {police['_dossier'].name} »")
    if not re.fullmatch(r"\d+\.\d+\.\d+", police.get("version", "")):
        erreurs.append(f"police.json : version « {police.get('version')} » n'est pas au format x.y.z")
    for document in ("OFL.txt", "CHANGELOG.md", "README.md"):
        if not (police["_dossier"] / document).exists():
            erreurs.append(f"{document} manquant")
    if (police["_dossier"] / "CHANGELOG.md").exists():
        publiees = {version["version"] for version in historique(police)}
        for version in police.get("notes", {}):
            if version not in publiees:
                erreurs.append(f"police.json : notes pour la version {version}, absente du CHANGELOG")

    chemin = f"fonts/{id_police}"
    config = json.loads(CONFIG_RELEASE.read_text(encoding="utf-8"))
    manifeste = json.loads(MANIFESTE_RELEASE.read_text(encoding="utf-8"))
    if chemin not in config.get("packages", {}):
        erreurs.append(f"absente de {CONFIG_RELEASE.name}")
    if manifeste.get(chemin) != police.get("version"):
        erreurs.append(f"{MANIFESTE_RELEASE.name} dit {manifeste.get(chemin)}, police.json dit {police.get('version')}")

    for cle, permises in (("usages", USAGES), ("styles", STYLES)):
        choisies = police.get(cle, [])
        if not choisies:
            erreurs.append(f"police.json : « {cle} » vide (au choix : {', '.join(permises)})")
        for valeur in choisies:
            if valeur not in permises:
                erreurs.append(f"police.json : {cle} « {valeur} » inconnu (au choix : {', '.join(permises)})")

    texte_specimen = police["specimen"].get("titre", "") + police["specimen"].get("texte", "")
    for langue in police.get("langues", []):
        if langue in PHRASES_LANGUES:
            texte_specimen += PHRASES_LANGUES[langue][1]
        else:
            erreurs.append(f"police.json : langue « {langue} » sans phrase d'exemple dans PHRASES_LANGUES")
    for fonction in police.get("fonctions", []):
        for cle in ("libelle", "description", "exemple"):
            if cle not in fonction:
                erreurs.append(f"police.json : fonction {fonction.get('code')} sans « {cle} »")
        texte_specimen += fonction.get("exemple", "")
    for graisse in police.get("graisses", []):
        for extension in ("ttf", "woff2"):
            fichier = fichier_graisse(police, graisse, extension)
            if not fichier.exists():
                erreurs.append(f"{fichier.relative_to(RACINE)} manquant (lancer : python tools/polices.py construire {id_police})")
                continue
            if extension == "woff2":
                continue
            fonte = TTFont(fichier)
            famille = fonte["name"].getDebugName(16) or fonte["name"].getDebugName(1)
            if famille != police["nom"]:
                erreurs.append(f"{fichier.name} : famille « {famille} » ≠ « {police['nom']} »")
            if fonte["OS/2"].usWeightClass != graisse["poids"]:
                erreurs.append(f"{fichier.name} : graisse {fonte['OS/2'].usWeightClass} ≠ {graisse['poids']}")
            absents = sorted({car for car in texte_specimen if not car.isspace() and ord(car) not in fonte.getBestCmap()})
            if absents:
                erreurs.append(f"{fichier.name} : glyphes absents du spécimen : {' '.join(absents)}")
            # construire écrit la version de police.json dans chaque police : un écart est une erreur
            attendue = revision_opentype(police["version"])
            if f"{fonte['head'].fontRevision:.3f}" != f"{float(attendue):.3f}":
                erreurs.append(f"{fichier.name} : révision {fonte['head'].fontRevision:.3f} ≠ {attendue}"
                               f" (version {police['version']}), à reconstruire")
    for erreur in erreurs:
        print(f"[{id_police}] ERREUR : {erreur}")
    if not erreurs:
        print(f"[{id_police}] OK ({police['version']}, {len(police['graisses'])} graisse(s))")
    return not erreurs


# --- empaqueter ----------------------------------------------------------------------------------

def empaqueter(police, sortie):
    sortie.mkdir(parents=True, exist_ok=True)
    racine_archive = f"{police['id']}-{police['version']}"
    archive = sortie / f"{racine_archive}.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zip_police:
        for graisse in police["graisses"]:
            for extension in EXTENSIONS:
                fichier = fichier_graisse(police, graisse, extension)
                if fichier.exists():
                    zip_police.write(fichier, f"{racine_archive}/{extension}/{fichier.name}")
        # Feuilles prêtes à servir avec les .woff2
        for nom, css in feuilles_css(police).items():
            zip_police.writestr(f"{racine_archive}/woff2/{nom}", css)
        for document in DOCUMENTS:
            if (police["_dossier"] / document).exists():
                zip_police.write(police["_dossier"] / document, f"{racine_archive}/{document}")
    print(f"-> {archive.relative_to(RACINE) if archive.is_relative_to(RACINE) else archive}")
    return archive


# --- site ----------------------------------------------------------------------------------------

def markdown_en_ligne(texte):
    texte = html.escape(texte, quote=False)
    texte = re.sub(r"`([^`]+)`", r"<code>\1</code>", texte)
    texte = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", texte)
    return re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', texte)


def historique(police):
    """CHANGELOG.md (format release-please) -> [{version, date, url, sections: [{titre, entrees}]}]."""
    versions = []
    for ligne in (police["_dossier"] / "CHANGELOG.md").read_text(encoding="utf-8").splitlines():
        if entete := re.match(r"^##\s+\[?([\d.]+)\]?(?:\(([^)]+)\))?\s*\(([\d-]+)\)", ligne):
            versions.append({"version": entete[1], "url": entete[2], "date": entete[3], "sections": []})
        elif (section := re.match(r"^###\s+(.+)", ligne)) and versions:
            versions[-1]["sections"].append({"titre": section[1].strip(), "entrees": []})
        elif (entree := re.match(r"^\*\s+(.+)", ligne)) and versions and versions[-1]["sections"]:
            versions[-1]["sections"][-1]["entrees"].append(markdown_en_ligne(entree[1]))
    # Notes en français de police.json (facultatives) : remplacent les messages de commit d'une version
    notes = police.get("notes", {})
    for version in versions:
        if version["version"] in notes:
            version["sections"] = [{"titre": titre, "entrees": [markdown_en_ligne(entree) for entree in entrees]}
                                   for titre, entrees in notes[version["version"]].items()]
    return versions


# Titres des sections du CHANGELOG (release-please) en français, et leur nom au pluriel pour les résumés
TITRES_SECTIONS = {"Features": "Nouveautés", "Bug Fixes": "Corrections", "Performance Improvements": "Performances"}


def resumer_versions(versions):
    """Ajoute à chaque version son type (selon le numéro), sa date courte et le compte de ses changements."""
    publiques = [version for version in versions if not version["version"].startswith("0.")]
    for version in versions:
        majeure, mineure, corrective = (int(nombre) for nombre in version["version"].split("."))
        if majeure == 0:
            version["type"] = "Version de travail"
        elif mineure == corrective == 0:
            version["type"] = "Majeure" + (" · première version publique" if version is publiques[-1] else "")
        elif corrective == 0:
            version["type"] = "Mineure"
        else:
            version["type"] = "Correctif"
        for section in version["sections"]:
            section["titre"] = TITRES_SECTIONS.get(section["titre"], section["titre"])
        version["date_courte"] = date_courte(version["date"]) if version["date"] else ""
        version["compte"] = ", ".join(f"{len(section['entrees'])} {section['titre'].lower()}"
                                      if len(section["entrees"]) > 1
                                      else f"1 {section['titre'].lower().removesuffix('s')}"
                                      for section in version["sections"] if section["entrees"])
    return versions


def glyphes(police):
    fonte = TTFont(fichier_graisse(police, police["graisses"][0], "ttf"))
    # Contrôles, espaces et séparateurs exclus de la grille
    return "".join(chr(code) for code in sorted(fonte.getBestCmap())
                   if unicodedata.category(chr(code))[0] not in "CZ")


def differences_opentype(police, code):
    """Positions des caractères de l'exemple dont le dessin change avec la fonction (les autres à leur défaut)."""
    fichier = fichier_graisse(police, police["graisses"][0], "ttf")
    fonte = uharfbuzz.Font(uharfbuzz.Face(uharfbuzz.Blob.from_file_path(str(fichier))))
    exemple = next(fonction for fonction in police["fonctions"] if fonction["code"] == code)["exemple"]

    def dessins(actif):
        reglage = {fonction["code"]: bool(fonction.get("parDefaut")) for fonction in police["fonctions"]}
        reglage[code] = actif
        tampon = uharfbuzz.Buffer()
        tampon.add_codepoints([ord(caractere) for caractere in exemple])
        tampon.guess_segment_properties()
        uharfbuzz.shape(fonte, tampon, reglage)
        # Grappe = rang du caractère (add_codepoints) ; une grappe peut porter plusieurs glyphes
        par_grappe = {}
        for info in tampon.glyph_infos:
            par_grappe.setdefault(info.cluster, []).append(info.codepoint)
        return par_grappe

    sans, avec = dessins(False), dessins(True)
    return sorted(rang for rang in set(sans) | set(avec) if sans.get(rang) != avec.get(rang))


def nom_unicode(caractere):
    return unicodedata.name(caractere, "").capitalize() or point_de_code(caractere)


def point_de_code(caractere):
    return f"U+{ord(caractere):04X}"


def kilo_octets(chemin):
    return max(1, round(chemin.stat().st_size / 1024))


def date_courte(iso):
    annee, mois, jour = iso.split("-")
    return f"{jour}/{mois}/{annee}"


def fiche_du_site(police, sortie, base):
    """Ce que les pages et le JavaScript du site savent d'une police (copie les webfonts et le zip dans sortie)."""
    id_police = police["id"]
    dossier_web = sortie / "fonts" / id_police
    dossier_web.mkdir(parents=True)
    ecrire_webfonts(police, dossier_web)
    archive = empaqueter(police, sortie / "downloads")
    graisses = [{**graisse, "woff2": f"{base}fonts/{id_police}/{fichier_graisse(police, graisse, 'woff2').name}",
                 "ko": kilo_octets(fichier_graisse(police, graisse, "woff2"))}
                for graisse in police["graisses"]]
    fonctions = [{"parDefaut": False, **fonction, "differences": differences_opentype(police, fonction["code"])}
                 for fonction in police.get("fonctions", [])]
    versions = resumer_versions(historique(police))
    fiche = {cle: valeur for cle, valeur in police.items()
             if not cle.startswith("_") and cle not in ("construction", "compilees", "notes")}
    # Clés facultatives de police.json : présentes pour les modèles (StrictUndefined signale les fautes de frappe)
    for cle in ("statut", "description", "origine", "nomReserve", "usage"):
        fiche.setdefault(cle, None)
    fiche.setdefault("langues", [])
    fiche["specimen"] = {"titre": None, "texte": None, "tailleMin": None, "tailleMax": None,
                         "tailleParDefaut": None, "taillesNettes": [], **police["specimen"]}
    fiche.update({
        "graisses": graisses,
        "fonctions": fonctions,
        "glyphes": [{"caractere": car, "nom": nom_unicode(car), "code": point_de_code(car)} for car in glyphes(police)],
        "historique": versions,
        "date": date_courte(versions[0]["date"]) if versions else "",
        # Accueil : tri par date et filtre « Mise à jour » (dernière version), « dernière ajoutée » (première)
        "date_iso": versions[0]["date"] if versions else "",
        "date_ajout": versions[-1]["date"] if versions else "",
        "telechargement": f"{base}downloads/{archive.name}",
        "ko_zip": kilo_octets(archive),
        "css": f"{URL_SITE}fonts/{id_police}/index.css",
        "npm": nom_npm(police),
        "sources": f"{URL_DEPOT}/tree/main/fonts/{id_police}",
        "page": f"{base}{id_police}/",
        "phrases": [{"langue": langue, "lang": PHRASES_LANGUES[langue][0], "texte": PHRASES_LANGUES[langue][1]}
                    for langue in police.get("langues", []) if langue in PHRASES_LANGUES],
        "signes": [{"libelle": libelle, "texte": texte} for libelle, texte in PHRASES_SIGNES.items()],
    })
    return fiche


def groupes_de_versions(versions):
    """Versions regroupées par version majeure, la plus récente d'abord."""
    groupes = []
    for version in versions:
        majeure = version["version"].split(".")[0]
        if not groupes or groupes[-1]["majeure"] != majeure:
            groupes.append({"majeure": majeure, "versions": []})
        groupes[-1]["versions"].append(version)
    return groupes


def json_dans_page(donnees):
    # Dans <script type="application/json"> : « </ » fermerait la balise
    return json.dumps(donnees, ensure_ascii=False).replace("</", "<\\/")


def site(sortie):
    if sortie.exists():
        shutil.rmtree(sortie)
    shutil.copytree(SITE, sortie, ignore=shutil.ignore_patterns(MODELES.name))
    base = urlparse(URL_SITE).path
    catalogue = []
    for id_police in tous_les_id():
        police = charger(id_police)
        if police["version"] == NON_PUBLIEE:
            print(f"[{id_police}] pas encore publiée : absente du site")
            continue
        catalogue.append(fiche_du_site(police, sortie, base))

    modeles = Environment(loader=FileSystemLoader(MODELES), autoescape=True, undefined=StrictUndefined,
                          trim_blocks=True, lstrip_blocks=True)
    modeles.filters["json"] = json_dans_page
    commun = {"base": base, "url_site": URL_SITE, "depot": URL_DEPOT, "catalogue": catalogue,
              "usages": USAGES, "styles": STYLES}

    def rendre(modele, chemin, **valeurs):
        chemin.parent.mkdir(parents=True, exist_ok=True)
        chemin.write_text(modeles.get_template(modele).render(**commun, **valeurs), encoding="utf-8")

    ajouts = [police["date_ajout"] for police in catalogue if police["date_ajout"]]
    rendre("accueil.html", sortie / "index.html", derniere_ajout=date_courte(max(ajouts)) if ajouts else "")
    for police in catalogue:
        rendre("police.html", sortie / police["id"] / "index.html", police=police)
        rendre("versions.html", sortie / police["id"] / "versions" / "index.html", police=police,
               groupes=groupes_de_versions(police["historique"]))
    rendre("404.html", sortie / "404.html")
    image_partage(sortie / "partage.png", catalogue)
    plan_du_site(sortie / "sitemap.xml", catalogue)
    if base == "/":
        fichiers_de_racine(sortie)
    (sortie / "polices.json").write_text(json.dumps({"depot": URL_DEPOT, "polices": catalogue},
                                                    ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"-> {sortie} ({len(catalogue)} police(s))")


def image_partage(chemin, catalogue):
    """Aperçu des liens partagés (Open Graph, 1200 × 630) : titre du site, puis le nom de chaque police dans sa police."""
    fond, encre, discret = THEMES_APERCU["clair"]
    image = Image.new("RGB", (1200, 630), fond)
    dessin = ImageDraw.Draw(image)
    # Double filet doré des cadres de Grimoire
    for retrait, epaisseur in ((24, 4), (36, 2)):
        dessin.rectangle((retrait, retrait, 1199 - retrait, 629 - retrait), outline=DORURE, width=epaisseur)
    def fichier_regular(fiche):
        police = charger(fiche["id"])
        return str(fichier_graisse(police, police["graisses"][0], "ttf"))

    titres = next((fiche for fiche in catalogue if fiche["id"] == POLICE_DES_TITRES), catalogue[0])
    fichier_titres = fichier_regular(titres)
    dessin.text((600, 230), "Mes polices", font=ImageFont.truetype(fichier_titres, 129), fill=encre, anchor="mm")
    # Au plus trois noms, chacun dans sa police, séparés par une étoile
    noms = [(fiche["nom"], ImageFont.truetype(fichier_regular(fiche), 64)) for fiche in catalogue[:3]]
    separateur = ("  ✦  ", ImageFont.truetype(fichier_titres, 43))
    morceaux = [morceau for nom in noms for morceau in (nom, separateur)][:-1]
    largeurs = [dessin.textlength(texte, font=fonte) for texte, fonte in morceaux]
    x = 600 - sum(largeurs) / 2
    for (texte, fonte), largeur in zip(morceaux, largeurs, strict=True):
        dessin.text((x, 400), texte, font=fonte, fill=DORURE if fonte is separateur[1] else encre, anchor="lm")
        x += largeur
    total = f"{len(catalogue)} police{'s' if len(catalogue) > 1 else ''} libre{'s' if len(catalogue) > 1 else ''} · licence OFL"
    dessin.text((600, 520), total, font=ImageFont.truetype(fichier_titres, 43), fill=discret, anchor="mm")
    image.save(chemin, optimize=True)


def fichiers_de_racine(sortie):
    """robots.txt et security.txt : seulement quand le site est à la racine de son domaine."""
    (sortie / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {URL_SITE}sitemap.xml\n", encoding="utf-8")
    # Expire un an après la publication : chaque mise en ligne le renouvelle
    expiration = (datetime.date.today() + datetime.timedelta(days=365)).isoformat()
    (sortie / ".well-known").mkdir(exist_ok=True)
    (sortie / ".well-known" / "security.txt").write_text(
        f"Contact: mailto:contact@danaedev.fr\nExpires: {expiration}T00:00:00.000Z\nPreferred-Languages: fr, en\n"
        f"Canonical: {URL_SITE}.well-known/security.txt\n", encoding="utf-8")


def plan_du_site(chemin, catalogue):
    """sitemap.xml : l'accueil, puis la page et les versions de chaque police, datées de leur dernière version."""
    def entree(adresse, date):
        return f"  <url>\n    <loc>{adresse}</loc>" + (f"\n    <lastmod>{date}</lastmod>" if date else "") + "\n  </url>\n"

    dates = {police["id"]: next((version["date"] for version in police["historique"] if version["date"]), "")
             for police in catalogue}
    entrees = entree(URL_SITE, max(dates.values(), default=""))
    for police in catalogue:
        entrees += entree(f"{URL_SITE}{police['id']}/", dates[police["id"]])
        entrees += entree(f"{URL_SITE}{police['id']}/versions/", dates[police["id"]])
    chemin.write_text('<?xml version="1.0" encoding="UTF-8"?>\n'
                      '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                      f"{entrees}</urlset>\n", encoding="utf-8")


# --- npm -----------------------------------------------------------------------------------------

def paquet_npm(police, sortie):
    """Dossier prêt pour `npm publish` : feuilles CSS, .woff2, licence, changelog, README et package.json."""
    dossier = sortie / police["id"]
    if dossier.exists():
        shutil.rmtree(dossier)
    dossier.mkdir(parents=True)
    ecrire_webfonts(police, dossier)
    for document in ("OFL.txt", "CHANGELOG.md"):
        shutil.copy2(police["_dossier"] / document, dossier)
    nom = nom_npm(police)
    paquet = {
        "name": nom,
        "version": police["version"],
        "description": police["resume"],
        "keywords": ["font", "webfont", "font-face", "woff2", *police.get("etiquettes", [])],
        "homepage": URL_SITE,
        "bugs": f"{URL_DEPOT}/issues",
        "repository": {"type": "git", "url": f"git+{URL_DEPOT}.git", "directory": f"fonts/{police['id']}"},
        "license": police["licence"],
        "author": AUTRICE,
        "style": "index.css",
        "exports": {".": "./index.css", "./*.css": "./*.css", "./*.woff2": "./*.woff2",
                    "./package.json": "./package.json"},
        "sideEffects": ["*.css"],
        "files": ["*.css", "*.woff2", "OFL.txt", "CHANGELOG.md"],
    }
    (dossier / "package.json").write_text(json.dumps(paquet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    graisses = "\n".join(f"| {graisse['nom']} | {graisse['poids']} | `{nom}/{graisse['poids']}.css` |"
                         for graisse in police["graisses"])
    (dossier / "README.md").write_text(f"""# {police["nom"]}

{police["resume"]} Licence OFL 1.1, par {AUTRICE.split(" (")[0]}.

[Essai, glyphes et spécimen]({URL_SITE}) · [Sources]({URL_DEPOT}/tree/main/fonts/{police["id"]})

## Installer

```bash
npm i {nom}
```

## Utiliser

```js
import "{nom}";            // toutes les graisses
import "{nom}/{police["graisses"][-1]["poids"]}.css";  // une seule
```

```css
h1 {{
  font-family: "{police["nom"]}", Georgia, serif;
}}
```

Sans bundler : `@import url("https://cdn.jsdelivr.net/npm/{nom}@{police["version"]}/index.css");`

| Graisse | Poids | Feuille |
| --- | --- | --- |
{graisses}

{police.get("usage", "")}
""", encoding="utf-8")
    print(f"-> {dossier.relative_to(RACINE) if dossier.is_relative_to(RACINE) else dossier}")
    return dossier


def confiance_npm(police, essai):
    """Autorise le workflow de release à publier le paquet (trusted publishing) ; npm demande la 2FA."""
    commande = [shutil.which("npm") or "npm", "trust", "github", nom_npm(police), "--file", WORKFLOW_PUBLICATION,
                "--repo", URL_DEPOT.removeprefix("https://github.com/"), "--allow-publish"]
    if essai:
        commande.append("--dry-run")
    print(" ".join(["npm", *commande[1:]]), flush=True)
    subprocess.run(commande, check=True)


# --- apercus -------------------------------------------------------------------------------------

def apercus(police):
    """Images du README en version claire et sombre : nom de la police puis texte du spécimen."""
    fichier = fichier_graisse(police, police["graisses"][0], "ttf")
    tailles = police["specimen"].get("taillesNettes") or [40, 96]
    grande, petite = max(tailles), min(tailles)
    dossier = police["_dossier"] / "images"
    dossier.mkdir(exist_ok=True)
    lignes = [(police["nom"], ImageFont.truetype(str(fichier), grande)),
              (police["specimen"]["texte"], ImageFont.truetype(str(fichier), petite))]
    boites = [ImageDraw.Draw(Image.new("RGB", (1, 1))).textbbox((0, 0), texte, font=fonte) for texte, fonte in lignes]
    marge = petite
    largeur = max(boite[2] for boite in boites) + 2 * marge
    hauteur = sum(boite[3] for boite in boites) + 3 * marge
    for theme, (fond, encre, discret) in THEMES_APERCU.items():
        image = Image.new("RGB", (largeur, hauteur), fond)
        dessin = ImageDraw.Draw(image)
        dessin.text((marge, marge), lignes[0][0], font=lignes[0][1], fill=encre)
        dessin.text((marge, 2 * marge + boites[0][3]), lignes[1][0], font=lignes[1][1], fill=discret)
        chemin = dossier / f"apercu-{theme}.png"
        image.save(chemin, optimize=True)
        print(f"-> {chemin.relative_to(RACINE)}")


# --- nouvelle ------------------------------------------------------------------------------------

def nouvelle(id_police, nom):
    dossier = POLICES / id_police
    if dossier.exists():
        sys.exit(f"{dossier.relative_to(RACINE)} existe déjà")
    if not re.fullmatch(r"[a-z0-9-]+", id_police):
        sys.exit("id : minuscules, chiffres et tirets seulement")
    (dossier / "compilees").mkdir(parents=True)
    police = {
        "id": id_police,
        "nom": nom,
        "version": NON_PUBLIEE,
        "statut": "brouillon",
        "resume": "",
        "description": "",
        "dessin": "Danaé ALBRECHT--MARTIN",
        "licence": "OFL-1.1",
        "etiquettes": [],
        "usages": [],
        "styles": [],
        "graisses": [{"nom": "Regular", "poids": 400}],
        "compilees": "compilees",
        "specimen": {"titre": nom, "texte": "Portez ce vieux whisky au juge blond qui fume",
                     "tailleMin": 16, "tailleMax": 128, "tailleParDefaut": 72, "taillesNettes": []},
        "usage": "",
    }
    (dossier / "police.json").write_text(json.dumps(police, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (dossier / "CHANGELOG.md").write_text("# Changelog\n", encoding="utf-8")
    (dossier / "README.md").write_text(f"# {nom}\n\nÀ décrire.\n", encoding="utf-8")
    # Texte de l'OFL repris de Jacquard 24, avec ma ligne de copyright à la place de la sienne
    licence = (POLICES / "sorcelle" / "sources" / "OFL.txt").read_text(encoding="utf-8").split("\n", 1)[1]
    (dossier / "OFL.txt").write_text(f"Copyright 2026 Danaé ALBRECHT--MARTIN (https://danaedev.fr)\n{licence}",
                                     encoding="utf-8")
    config = json.loads(CONFIG_RELEASE.read_text(encoding="utf-8"))
    config["packages"][f"fonts/{id_police}"] = {
        "component": id_police, "package-name": id_police,
        "extra-files": [{"type": "json", "path": "police.json", "jsonpath": "$.version"}]}
    CONFIG_RELEASE.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifeste = json.loads(MANIFESTE_RELEASE.read_text(encoding="utf-8"))
    manifeste[f"fonts/{id_police}"] = NON_PUBLIEE
    MANIFESTE_RELEASE.write_text(json.dumps(manifeste, indent=2) + "\n", encoding="utf-8")
    print(f"-> {dossier.relative_to(RACINE)} créé. À faire :\n"
          f"   1. remplir police.json (dont usages et styles) et la ligne Copyright de OFL.txt ;\n"
          f"   2. mettre les .ttf/.woff2 dans compilees/ (ou une commande \"construction\") ;\n"
          f"   3. python tools/polices.py construire {id_police} && python tools/polices.py verifier {id_police}\n"
          f"   Le site l'affichera après sa première version (commit « feat({id_police}): … », puis release PR).")


# --- Ligne de commande ---------------------------------------------------------------------------

def main():
    analyseur = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commandes = analyseur.add_subparsers(dest="commande", required=True)
    commandes.add_parser("lister")
    for nom_commande in ("construire", "verifier", "apercus"):
        commandes.add_parser(nom_commande).add_argument("ids", nargs="*")
    commande_empaqueter = commandes.add_parser("empaqueter")
    commande_empaqueter.add_argument("id")
    commande_empaqueter.add_argument("--sortie", type=Path, default=RACINE / "release")
    commandes.add_parser("site").add_argument("--sortie", type=Path, default=RACINE / "_site")
    commande_npm = commandes.add_parser("npm")
    commande_npm.add_argument("id")
    commande_npm.add_argument("--sortie", type=Path, default=RACINE / "npm")
    commande_confiance = commandes.add_parser("npm-confiance")
    commande_confiance.add_argument("id")
    commande_confiance.add_argument("--essai", action="store_true", help="montrer sans rien changer (--dry-run)")
    commandes.add_parser("tag").add_argument("id")
    commande_nouvelle = commandes.add_parser("nouvelle")
    commande_nouvelle.add_argument("id")
    commande_nouvelle.add_argument("nom")
    arguments = analyseur.parse_args()

    if arguments.commande == "lister":
        for id_police in tous_les_id():
            police = charger(id_police)
            print(f"{id_police:16} {police['version']:8} {police['nom']}")
    elif arguments.commande == "construire":
        for id_police in arguments.ids or tous_les_id():
            construire(charger(id_police))
    elif arguments.commande == "verifier":
        resultats = [verifier(charger(id_police)) for id_police in arguments.ids or tous_les_id()]
        sys.exit(0 if all(resultats) else 1)
    elif arguments.commande == "empaqueter":
        empaqueter(charger(arguments.id), arguments.sortie.resolve())
    elif arguments.commande == "site":
        site(arguments.sortie.resolve())
    elif arguments.commande == "npm":
        paquet_npm(charger(arguments.id), arguments.sortie.resolve())
    elif arguments.commande == "npm-confiance":
        confiance_npm(charger(arguments.id), arguments.essai)
    elif arguments.commande == "apercus":
        for id_police in arguments.ids or tous_les_id():
            apercus(charger(id_police))
    elif arguments.commande == "tag":
        print(nom_du_tag(charger(arguments.id)))
    elif arguments.commande == "nouvelle":
        nouvelle(arguments.id, arguments.nom)


if __name__ == "__main__":
    main()
