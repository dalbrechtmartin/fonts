"""Outils communs du dépôt : compiler, vérifier, empaqueter et présenter les polices.

Usage (depuis la racine du dépôt) :
  python tools/fonts.py list
  python tools/fonts.py build [id ...]           # compile dans fonts/<id>/dist/
  python tools/fonts.py check [id ...]           # contrôles (fichiers, noms, couverture, version)
  python tools/fonts.py package <id> [--out d]   # zip <id>-<version>.zip (TTF, WOFF2, licence, changelog)
  python tools/fonts.py site [--out _site]       # site de présentation (GitHub Pages)
  python tools/fonts.py tag <id>                 # nom du tag git de la version courante
  python tools/fonts.py new <id> "<Nom>"         # nouveau dossier de police, déclaré à release-please

Chaque police vit dans fonts/<id>/ avec un font.json. Si font.json a une clé "build", la commande
est lancée dans le dossier de la police ({dist} = chemin de sortie) ; sinon les fichiers déjà compilés
sont copiés depuis le dossier "prebuilt" (par défaut fonts/<id>/prebuilt/).
"""
import argparse
import html
import json
import re
import shutil
import subprocess
import sys
import unicodedata
import zipfile
from pathlib import Path

from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "fonts"
SITE = ROOT / "site"
RP_CONFIG = ROOT / "release-please-config.json"
RP_MANIFEST = ROOT / ".release-please-manifest.json"
REPO_URL = "https://github.com/dalbrechtmartin/fonts"
UNRELEASED = "0.0.0"
REQUIRED = ("id", "name", "version", "summary", "designer", "license", "styles", "specimen")


# --- Lecture -------------------------------------------------------------------------------------

def load(font_id):
    path = FONTS / font_id / "font.json"
    if not path.exists():
        sys.exit(f"Police inconnue : {font_id} (pas de {path.relative_to(ROOT)})")
    meta = json.loads(path.read_text(encoding="utf-8"))
    meta["_dir"] = path.parent
    return meta


def all_ids():
    return sorted(p.parent.name for p in FONTS.glob("*/font.json"))


def dist_dir(meta):
    return meta["_dir"] / "dist"


def style_file(meta, style, ext):
    return dist_dir(meta) / f"{meta['name'].replace(' ', '')}-{style['name']}.{ext}"


def tag_name(meta):
    return f"{meta['id']}-v{meta['version']}"


# --- build ---------------------------------------------------------------------------------------

def build(meta):
    out = dist_dir(meta)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    if "build" in meta:
        cmd = [sys.executable if part == "python" else part.replace("{dist}", str(out)) for part in meta["build"]]
        print(f"[{meta['id']}] {' '.join(meta['build'])}")
        subprocess.run(cmd, cwd=meta["_dir"], check=True)
    else:
        prebuilt = meta["_dir"] / meta.get("prebuilt", "prebuilt")
        for f in prebuilt.iterdir():
            if f.suffix in (".ttf", ".otf", ".woff2"):
                shutil.copy2(f, out / f.name)
        print(f"[{meta['id']}] fichiers copiés depuis {prebuilt.relative_to(ROOT)}")


# --- check ---------------------------------------------------------------------------------------

def check(meta):
    errors, warnings = [], []
    fid = meta["id"]
    for key in REQUIRED:
        if key not in meta:
            errors.append(f"font.json : clé « {key} » manquante")
    if meta.get("id") != meta["_dir"].name:
        errors.append(f"font.json : id « {meta.get('id')} » ≠ dossier « {meta['_dir'].name} »")
    if not re.fullmatch(r"\d+\.\d+\.\d+", meta.get("version", "")):
        errors.append(f"font.json : version « {meta.get('version')} » n'est pas au format x.y.z")
    for name in ("OFL.txt", "CHANGELOG.md", "README.md"):
        if not (meta["_dir"] / name).exists():
            errors.append(f"{name} manquant")

    # Déclarée à release-please, à la même version
    path = f"fonts/{fid}"
    config = json.loads(RP_CONFIG.read_text(encoding="utf-8"))
    manifest = json.loads(RP_MANIFEST.read_text(encoding="utf-8"))
    if path not in config.get("packages", {}):
        errors.append(f"absente de {RP_CONFIG.name}")
    if manifest.get(path) != meta.get("version"):
        errors.append(f"{RP_MANIFEST.name} dit {manifest.get(path)}, font.json dit {meta.get('version')}")

    sample = meta["specimen"].get("headline", "") + meta["specimen"].get("sample", "")
    for style in meta.get("styles", []):
        for ext in ("ttf", "woff2"):
            f = style_file(meta, style, ext)
            if not f.exists():
                errors.append(f"{f.relative_to(ROOT)} manquant (lancer : python tools/fonts.py build {fid})")
                continue
            if ext == "woff2":
                continue
            font = TTFont(f)
            family = font["name"].getDebugName(16) or font["name"].getDebugName(1)
            if family != meta["name"]:
                errors.append(f"{f.name} : famille « {family} » ≠ « {meta['name']} »")
            if font["OS/2"].usWeightClass != style["weight"]:
                errors.append(f"{f.name} : graisse {font['OS/2'].usWeightClass} ≠ {style['weight']}")
            cmap = font.getBestCmap()
            missing = sorted({c for c in sample if not c.isspace() and ord(c) not in cmap})
            if missing:
                errors.append(f"{f.name} : glyphes absents du spécimen : {' '.join(missing)}")
            unique_id = font["name"].getDebugName(3) or ""
            if meta["version"] not in unique_id:
                warnings.append(f"{f.name} : version {meta['version']} absente du nom unique « {unique_id} »")
    for w in warnings:
        print(f"[{fid}] attention : {w}")
    for e in errors:
        print(f"[{fid}] ERREUR : {e}")
    if not errors:
        print(f"[{fid}] OK ({meta['version']}, {len(meta['styles'])} graisse(s))")
    return not errors


# --- package -------------------------------------------------------------------------------------

def package(meta, out):
    out.mkdir(parents=True, exist_ok=True)
    stem = f"{meta['id']}-{meta['version']}"
    archive = out / f"{stem}.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as z:
        for style in meta["styles"]:
            for ext in ("ttf", "woff2"):
                f = style_file(meta, style, ext)
                z.write(f, f"{stem}/{ext}/{f.name}")
        for name in ("OFL.txt", "README.md", "CHANGELOG.md"):
            z.write(meta["_dir"] / name, f"{stem}/{name}")
    print(f"-> {archive.relative_to(ROOT) if archive.is_relative_to(ROOT) else archive}")
    return archive


# --- site ----------------------------------------------------------------------------------------

def inline_md(text):
    text = html.escape(text, quote=False)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', text)
    return text


def changelog(meta):
    """CHANGELOG.md (format release-please) -> [{version, date, url, sections: [{title, items}]}]."""
    releases = []
    for line in (meta["_dir"] / "CHANGELOG.md").read_text(encoding="utf-8").splitlines():
        if m := re.match(r"^##\s+\[?([\d.]+)\]?(?:\(([^)]+)\))?\s*\(([\d-]+)\)", line):
            releases.append({"version": m[1], "url": m[2], "date": m[3], "sections": []})
        elif (m := re.match(r"^###\s+(.+)", line)) and releases:
            releases[-1]["sections"].append({"title": m[1].strip(), "items": []})
        elif (m := re.match(r"^\*\s+(.+)", line)) and releases and releases[-1]["sections"]:
            # release-please ajoute « ([abc1234](lien)) » : on le garde comme lien vers le commit
            releases[-1]["sections"][-1]["items"].append(inline_md(m[1]))
    return releases


def glyphs(meta):
    font = TTFont(style_file(meta, meta["styles"][0], "ttf"))
    chars = []
    for cp in sorted(font.getBestCmap()):
        ch = chr(cp)
        if unicodedata.category(ch)[0] in "CZ":     # contrôles, espaces, séparateurs
            continue
        chars.append(ch)
    return "".join(chars)


def site(out):
    if out.exists():
        shutil.rmtree(out)
    shutil.copytree(SITE, out)
    catalog = []
    for fid in all_ids():
        meta = load(fid)
        if meta["version"] == UNRELEASED:
            print(f"[{fid}] pas encore publiée : absente du site")
            continue
        target = out / "fonts" / fid
        target.mkdir(parents=True)
        files = []
        for style in meta["styles"]:
            f = style_file(meta, style, "woff2")
            shutil.copy2(f, target / f.name)
            files.append({**style, "woff2": f"fonts/{fid}/{f.name}"})
        archive = package(meta, out / "downloads")
        entry = {k: v for k, v in meta.items() if not k.startswith("_") and k not in ("build", "prebuilt")}
        entry.update({
            "styles": files,
            "glyphs": glyphs(meta),
            "changelog": changelog(meta),
            "download": f"downloads/{archive.name}",
            "release": f"{REPO_URL}/releases/tag/{tag_name(meta)}",
            "source": f"{REPO_URL}/tree/main/fonts/{fid}",
        })
        catalog.append(entry)
    (out / "fonts.json").write_text(json.dumps({"repo": REPO_URL, "fonts": catalog}, ensure_ascii=False, indent=1),
                                    encoding="utf-8")
    print(f"-> {out} ({len(catalog)} police(s))")


# --- new -----------------------------------------------------------------------------------------

def new(fid, name):
    folder = FONTS / fid
    if folder.exists():
        sys.exit(f"{folder.relative_to(ROOT)} existe déjà")
    if not re.fullmatch(r"[a-z0-9-]+", fid):
        sys.exit("id : minuscules, chiffres et tirets seulement")
    (folder / "prebuilt").mkdir(parents=True)
    meta = {
        "id": fid,
        "name": name,
        "version": UNRELEASED,
        "status": "brouillon",
        "summary": "",
        "description": "",
        "designer": "Danaé Albrecht--Martin",
        "license": "OFL-1.1",
        "tags": [],
        "styles": [{"name": "Regular", "weight": 400}],
        "prebuilt": "prebuilt",
        "specimen": {"headline": name, "sample": "Portez ce vieux whisky au juge blond qui fume",
                     "minSize": 16, "maxSize": 128, "defaultSize": 72, "crispSizes": []},
        "usage": "",
    }
    (folder / "font.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (folder / "CHANGELOG.md").write_text("# Changelog\n", encoding="utf-8")       # rempli par release-please
    (folder / "README.md").write_text(f"# {name}\n\nÀ décrire.\n", encoding="utf-8")
    # Texte OFL repris de Jacquard 24, avec ma ligne de copyright à la place de la sienne
    ofl = (FONTS / "sorcelle" / "sources" / "OFL.txt").read_text(encoding="utf-8").split("\n", 1)[1]
    (folder / "OFL.txt").write_text(f"Copyright 2026 Danaé Albrecht--Martin (https://danaedev.fr)\n{ofl}",
                                    encoding="utf-8")
    config = json.loads(RP_CONFIG.read_text(encoding="utf-8"))
    config["packages"][f"fonts/{fid}"] = {"component": fid, "package-name": fid,
                                          "extra-files": [{"type": "json", "path": "font.json",
                                                           "jsonpath": "$.version"}]}
    RP_CONFIG.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest = json.loads(RP_MANIFEST.read_text(encoding="utf-8"))
    manifest[f"fonts/{fid}"] = UNRELEASED     # le premier commit « feat » donnera 0.1.0
    RP_MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"-> {folder.relative_to(ROOT)} créé. À faire : remplir font.json, OFL.txt (ligne Copyright),\n"
          f"   mettre les .ttf/.woff2 dans prebuilt/ (ou une commande \"build\"), puis :\n"
          f"   python tools/fonts.py build {fid} && python tools/fonts.py check {fid}\n"
          f"   Le site l'affichera après sa première version (commit « feat({fid}): … », puis release PR).")


# --- CLI -----------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list")
    for cmd in ("build", "check"):
        sub.add_parser(cmd).add_argument("ids", nargs="*")
    p = sub.add_parser("package")
    p.add_argument("id")
    p.add_argument("--out", type=Path, default=ROOT / "release")
    sub.add_parser("site").add_argument("--out", type=Path, default=ROOT / "_site")
    sub.add_parser("tag").add_argument("id")
    p = sub.add_parser("new")
    p.add_argument("id")
    p.add_argument("name")
    args = parser.parse_args()

    if args.cmd == "list":
        for fid in all_ids():
            meta = load(fid)
            print(f"{fid:16} {meta['version']:8} {meta['name']}")
    elif args.cmd == "build":
        for fid in args.ids or all_ids():
            build(load(fid))
    elif args.cmd == "check":
        results = [check(load(fid)) for fid in args.ids or all_ids()]
        sys.exit(0 if all(results) else 1)
    elif args.cmd == "package":
        package(load(args.id), args.out.resolve())
    elif args.cmd == "site":
        site(args.out.resolve())
    elif args.cmd == "tag":
        print(tag_name(load(args.id)))
    elif args.cmd == "new":
        new(args.id, args.name)


if __name__ == "__main__":
    main()
