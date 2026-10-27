"""Génère un spécimen HTML autonome (polices intégrées) pour relire et tester la police.

Contenu : texte modifiable, cascade de tailles, styles, axes variables, fonctions OpenType,
langues couvertes, typographie française, paires à risque de confusion, grille des glyphes.
Thèmes Clair / Sombre / Système, accessible au clavier, tailles en rem.

Usage :
    python specimen.py fonts/webfonts/*.woff2 --nom "Ma Police" [--sortie specimen/index.html]
"""

import argparse
import base64
import html
import json
import unicodedata
from pathlib import Path

from fontTools.ttLib import TTFont

# Pangrammes et phrases d'essai, n'apparaissent que si la police couvre la langue
ECHANTILLONS = {
    "fr": ("Français", "Portez ce vieux whisky au juge blond qui fume. Œuvre, cœur, Ève, À bientôt !"),
    "en": ("English", "The quick brown fox jumps over the lazy dog."),
    "de": ("Deutsch", "Victor jagt zwölf Boxkämpfer quer über den großen Sylter Deich."),
    "es": ("Español", "El veloz murciélago hindú comía feliz cardillo y kiwi. ¿Qué tal? ¡Bien!"),
    "pl": ("Polski", "Zażółć gęślą jaźń. Pchnąć w tę łódź jeża lub ośm skrzyń fig."),
    "cs": ("Čeština", "Příliš žluťoučký kůň úpěl ďábelské ódy."),
    "ro": ("Română", "Fumegând hipnotic sașiul azvârle mreje în bălți."),
    "tr": ("Türkçe", "Pijamalı hasta yağız şoföre çabucak güvendi. İstanbul, ılık."),
    "vi": ("Tiếng Việt", "Tiếng Việt có dấu: những chữ ư, ơ, ệ, ặ, ữ phải dễ đọc."),
}
TYPOGRAPHIE_FRANCAISE = "« Vraiment ? » — Oui\u202f! Il est 9\u202fh\u202f30\u202f; l’été coûte 1\u202f250,50\u00a0€."
PAIRES_CONFUSABLES = ("Il1|", "O0o", "rn m", "cl d", "bdpq", "5S 2Z 8B", "6b 9g", "' ’ \" ”", "- – —")
TEXTE_DEPART = "Une police lisible par le plus grand nombre : 0123456789 Il1 O0 rn/m."
FONCTIONS_CONNUES = {
    "liga": "Ligatures", "dlig": "Ligatures facultatives", "smcp": "Petites capitales",
    "c2sc": "Capitales en petites capitales", "onum": "Chiffres elzéviriens", "lnum": "Chiffres alignés",
    "tnum": "Chiffres tabulaires", "pnum": "Chiffres proportionnels", "frac": "Fractions",
    "zero": "Zéro barré", "case": "Formes pour capitales", "sups": "Exposants", "subs": "Indices",
    "ss01": "Jeu stylistique 1", "ss02": "Jeu stylistique 2", "ss03": "Jeu stylistique 3",
    "calt": "Variantes contextuelles", "salt": "Variantes stylistiques", "ordn": "Ordinaux",
    "dnom": "Dénominateurs", "numr": "Numérateurs", "sinf": "Indices scientifiques", "hist": "Formes historiques",
}
# Actives par défaut dans les navigateurs : la case doit apparaître cochée
ACTIVES_PAR_DEFAUT = {"calt", "liga", "clig"}
# Fonctions internes (crénage, accents, ligatures obligatoires, menus de logiciels) : rien à essayer
FONCTIONS_INTERNES = {"kern", "mark", "mkmk", "locl", "ccmp", "aalt", "rlig", "rvrn", "init", "medi", "fina", "isol"}


def decrire_police(fichier: Path, indice: int) -> dict:
    police = TTFont(fichier)
    os2, noms = police["OS/2"], police["name"]
    fonctions = sorted({r.FeatureTag for t in ("GSUB", "GPOS") if t in police
                        for r in police[t].table.FeatureList.FeatureRecord} - FONCTIONS_INTERNES)
    noms_fonctions = {}
    for enregistrement in police["GSUB"].table.FeatureList.FeatureRecord if "GSUB" in police else []:
        parametres = enregistrement.Feature.FeatureParams
        if parametres is not None and getattr(parametres, "UINameID", None):
            noms_fonctions[enregistrement.FeatureTag] = noms.getDebugName(parametres.UINameID)
    format_ = "woff2" if fichier.suffix == ".woff2" else "truetype"
    return {
        "famille": f"Specimen{indice}",
        "nom": noms.getDebugName(4),
        "graisse": os2.usWeightClass,
        "italique": bool(os2.fsSelection & 1),
        "source": f"data:font/{fichier.suffix[1:]};base64,{base64.b64encode(fichier.read_bytes()).decode()}",
        "format": format_,
        "axes": [{"tag": a.axisTag, "min": a.minValue, "defaut": a.defaultValue, "max": a.maxValue}
                 for a in police["fvar"].axes] if "fvar" in police else [],
        "fonctions": [{"tag": f, "libelle": noms_fonctions.get(f) or FONCTIONS_CONNUES.get(f, ""),
                       "parDefaut": f in ACTIVES_PAR_DEFAUT} for f in fonctions],
        "caracteres": sorted(police.getBestCmap()),
    }


def couvre(caracteres: set[int], texte: str) -> bool:
    return all(ord(c) in caracteres or c.isspace() for c in texte)


def section_glyphes(caracteres: list[int]) -> str:
    cases = []
    for point_code in caracteres:
        caractere = chr(point_code)
        if unicodedata.category(caractere)[0] in "CZ":
            continue
        nom = unicodedata.name(caractere, f"U+{point_code:04X}").lower()
        cases.append(f'<li><span class="glyphe" aria-hidden="true">{html.escape(caractere)}</span>'
                     f'<span class="code">U+{point_code:04X}</span><span class="visuellement-cache">{html.escape(nom)}</span></li>')
    return "\n".join(cases)


def section_credit(nom: str, credit: str | None) -> str:
    if not credit:
        return ""
    return (f'<section aria-labelledby="titre-credit"><h2 id="titre-credit">Utiliser {html.escape(nom)}</h2>'
            "<p>Libre d’utilisation, y compris commerciale, sous licence SIL Open Font License 1.1. "
            "Une mention fait toujours plaisir :</p>"
            f'<p class="credit" id="credit">{html.escape(credit)}</p>'
            '<button type="button" id="copier-credit">Copier la mention</button> '
            '<span id="statut-credit" role="status" aria-live="polite"></span></section>')


def generer(polices: list[dict], nom: str, texte: str, credit: str | None = None) -> str:
    principale = polices[0]
    caracteres = set(principale["caracteres"])
    faces = "\n".join(
        f'@font-face {{ font-family: "{p["famille"]}"; src: url({p["source"]}) format("{p["format"]}"); font-display: swap; }}'
        for p in polices)
    langues = "\n".join(
        f'<figure class="echantillon"><figcaption>{libelle}</figcaption><p lang="{code}" class="apercu">{html.escape(texte)}</p></figure>'
        for code, (libelle, texte) in ECHANTILLONS.items() if couvre(caracteres, texte))
    paires = "\n".join(f'<li class="apercu paire">{html.escape(p)}</li>' for p in PAIRES_CONFUSABLES if couvre(caracteres, p))
    donnees = json.dumps([{k: v for k, v in p.items() if k not in ("source", "caracteres")} for p in polices])
    return MODELE.format(
        nom=html.escape(nom), faces=faces, famille=principale["famille"], langues=langues,
        typographie_fr=html.escape(TYPOGRAPHIE_FRANCAISE), paires=paires, texte_depart=html.escape(texte),
        glyphes=section_glyphes(principale["caracteres"]), nb_caracteres=len(caracteres), donnees=donnees,
        credit=section_credit(nom, credit))


MODELE = """<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{nom} — spécimen</title>
<style>
{faces}
:root {{
  --fond: #f7f6f3; --surface: #ffffff; --texte: #1d1c1a; --texte-doux: #55524c; --bordure: #d6d3cc;
  --accent: #3b4fc4; --focus: #3b4fc4;
  --espace-1: .25rem; --espace-2: .5rem; --espace-3: .75rem; --espace-4: 1rem; --espace-6: 1.5rem; --espace-8: 2rem; --espace-12: 3rem;
  --rayon: .5rem; --duree: 150ms;
  color-scheme: light;
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    --fond: #1b1b1d; --surface: #26262a; --texte: #ecebe8; --texte-doux: #b3b0aa; --bordure: #45454b;
    --accent: #9eabff; --focus: #9eabff; color-scheme: dark;
  }}
}}
:root[data-theme="dark"] {{
  --fond: #1b1b1d; --surface: #26262a; --texte: #ecebe8; --texte-doux: #b3b0aa; --bordure: #45454b;
  --accent: #9eabff; --focus: #9eabff; color-scheme: dark;
}}
* {{ box-sizing: border-box; }}
:root {{ padding-top: env(safe-area-inset-top, 0px); padding-bottom: env(safe-area-inset-bottom, 0px); }}
html {{ scroll-padding-top: env(safe-area-inset-top, 0px); }}
body {{ margin: 0; background: var(--fond); color: var(--texte); font: 1rem/1.5 system-ui, sans-serif; }}
[hidden] {{ display: none !important; }}
.visuellement-cache {{ position: absolute; width: 1px; height: 1px; overflow: hidden; clip-path: inset(50%); white-space: nowrap; }}
.lien-evitement {{ position: absolute; left: var(--espace-4); top: -4rem; background: var(--surface); padding: var(--espace-3); z-index: 2; }}
.lien-evitement:focus {{ top: var(--espace-4); }}
:focus-visible {{ outline: 2px solid var(--focus); outline-offset: 2px; }}
header, main {{ max-width: 72rem; margin: 0 auto; padding: var(--espace-6) var(--espace-4); }}
header {{ display: flex; flex-wrap: wrap; gap: var(--espace-4); align-items: end; justify-content: space-between; }}
h1 {{ font-family: "{famille}", system-ui; font-size: 2.5rem; line-height: 1.1; margin: 0; }}
h2 {{ font-size: 1.25rem; margin: var(--espace-12) 0 var(--espace-4); }}
section {{ border-top: 1px solid var(--bordure); }}
fieldset {{ border: 1px solid var(--bordure); border-radius: var(--rayon); padding: var(--espace-3); margin: 0; min-width: 0; }}  /* sinon un fieldset refuse de rétrécir sous son contenu (débordement à 320 px) */
legend {{ padding: 0 var(--espace-2); color: var(--texte-doux); }}
.segmente {{ display: flex; flex-wrap: wrap; gap: var(--espace-1); }}
.segmente label {{ display: inline-flex; align-items: center; min-height: 2.75rem; padding: 0 var(--espace-3); border-radius: var(--rayon); cursor: pointer; }}
.segmente input {{ position: absolute; opacity: 0; }}
.segmente input:checked + span {{ font-weight: 700; text-decoration: underline; text-underline-offset: .3em; }}
.segmente label:has(input:checked) {{ background: var(--surface); box-shadow: inset 0 0 0 1px var(--bordure); }}
.segmente label:has(input:focus-visible) {{ outline: 2px solid var(--focus); }}
.controles {{ display: grid; gap: var(--espace-4); grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr)); margin-bottom: var(--espace-6); }}
.reglage {{ display: grid; grid-template-columns: 1fr 5rem; gap: var(--espace-2); align-items: center; }}
.reglage label {{ grid-column: 1 / -1; color: var(--texte-doux); }}
input[type="range"] {{ min-height: 2.75rem; accent-color: var(--accent); cursor: pointer; }}
input[type="number"], select {{ min-height: 2.75rem; font: inherit; color: inherit; background: var(--surface); border: 1px solid var(--bordure); border-radius: var(--rayon); padding: 0 var(--espace-2); }}
.cases {{ display: flex; flex-wrap: wrap; gap: var(--espace-2) var(--espace-4); }}
.cases label {{ display: inline-flex; gap: var(--espace-2); align-items: center; min-height: 2.75rem; cursor: pointer; }}
.apercu {{ font-family: var(--famille-active), system-ui; overflow-wrap: anywhere; }}
.editable {{ font-size: var(--taille, 2rem); line-height: 1.4; min-height: 6rem; padding: var(--espace-4); background: var(--surface); border: 1px solid var(--bordure); border-radius: var(--rayon); }}
.cascade p {{ margin: var(--espace-2) 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
.cascade span {{ display: inline-block; width: 4rem; color: var(--texte-doux); font: .875rem system-ui; }}
.echantillon {{ margin: 0 0 var(--espace-6); }}
.echantillon figcaption {{ color: var(--texte-doux); font-size: .875rem; }}
.echantillon p {{ font-size: 1.5rem; margin: var(--espace-1) 0 0; }}
.paires {{ list-style: none; padding: 0; display: grid; gap: var(--espace-3); grid-template-columns: repeat(auto-fill, minmax(10rem, 1fr)); }}
.paire {{ font-size: 1rem; padding: var(--espace-3); background: var(--surface); border: 1px solid var(--bordure); border-radius: var(--rayon); letter-spacing: .05em; }}
.grille {{ list-style: none; padding: 0; display: grid; grid-template-columns: repeat(auto-fill, minmax(4.5rem, 1fr)); border-top: 1px solid var(--bordure); border-left: 1px solid var(--bordure); }}
.grille li {{ background: var(--surface); display: grid; place-items: center; padding: var(--espace-2) 0; border-right: 1px solid var(--bordure); border-bottom: 1px solid var(--bordure); }}
.glyphe {{ font-family: var(--famille-active); font-size: 2rem; line-height: 1.3; }}
.code {{ font: .75rem ui-monospace, monospace; color: var(--texte-doux); }}
.deux-themes {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr)); gap: var(--espace-4); }}
.credit {{ padding: var(--espace-3) var(--espace-4); background: var(--surface); border: 1px solid var(--bordure); border-radius: var(--rayon); font-family: ui-monospace, monospace; overflow-wrap: anywhere; }}
button {{ min-height: 2.75rem; padding: 0 var(--espace-4); font: inherit; color: var(--fond); background: var(--accent); border: 0; border-radius: var(--rayon); cursor: pointer; }}
.deux-themes p {{ margin: 0; padding: var(--espace-4); border-radius: var(--rayon); font-size: 1rem; }}
.sur-clair {{ background: #ffffff; color: #1d1c1a; }}
.sur-sombre {{ background: #1b1b1d; color: #ecebe8; }}
</style>
</head>
<body>
<a class="lien-evitement" href="#contenu">Aller au contenu</a>
<header>
  <div><p class="code">{nb_caracteres} caractères</p><h1>{nom}</h1></div>
  <fieldset class="segmente"><legend>Thème</legend>
    <label><input type="radio" name="theme" value="light"><span>Clair</span></label>
    <label><input type="radio" name="theme" value="dark"><span>Sombre</span></label>
    <label><input type="radio" name="theme" value="system" checked><span>Système</span></label>
  </fieldset>
</header>
<main id="contenu">
  <section aria-labelledby="titre-essai"><h2 id="titre-essai">Essayer</h2>
    <div class="controles">
      <div class="reglage"><label for="style">Style</label><select id="style" style="grid-column: 1 / -1"></select></div>
      <div class="reglage"><label for="taille-curseur">Taille du texte (px)</label>
        <input id="taille-curseur" type="range" min="12" max="160" value="32">
        <input id="taille-champ" type="number" min="12" max="160" value="32" aria-label="Taille du texte en pixels"></div>
      <div id="axes" class="controles" style="margin: 0"></div>
    </div>
    <fieldset id="fonctions" class="cases" hidden><legend>Fonctions OpenType</legend></fieldset>
    <p class="apercu editable" contenteditable="true" spellcheck="false" aria-label="Texte d’essai modifiable">{texte_depart}</p>
  </section>
  <section aria-labelledby="titre-cascade"><h2 id="titre-cascade">Cascade de tailles</h2>
    <div class="cascade apercu" id="cascade"></div></section>
  <section aria-labelledby="titre-themes"><h2 id="titre-themes">Petits corps sur fond clair et sombre</h2>
    <p>Les traits fins s’amincissent ou bavent sur fond sombre : comparer à 16 px et 12 px.</p>
    <div class="deux-themes">
      <p class="apercu sur-clair">{texte_depart}<br><small>{texte_depart}</small></p>
      <p class="apercu sur-sombre">{texte_depart}<br><small>{texte_depart}</small></p>
    </div></section>
  <section aria-labelledby="titre-confusion"><h2 id="titre-confusion">Paires à ne pas confondre</h2>
    <p>Chaque groupe doit rester distinct à 16 px, même en plissant les yeux.</p>
    <ul class="paires">{paires}</ul></section>
  <section aria-labelledby="titre-fr"><h2 id="titre-fr">Typographie française</h2>
    <p class="apercu echantillon" style="font-size: 1.5rem" lang="fr">{typographie_fr}</p></section>
  <section aria-labelledby="titre-langues"><h2 id="titre-langues">Langues couvertes</h2>{langues}</section>
  <section aria-labelledby="titre-glyphes"><h2 id="titre-glyphes">Glyphes</h2>
    <ul class="grille">{glyphes}</ul></section>
  {credit}
</main>
<script>
const POLICES = {donnees};
const racine = document.documentElement;
const etat = {{ police: POLICES[0], axes: {{}}, fonctions: new Set() }};

function lireTheme() {{ try {{ return localStorage.getItem("theme") || "system"; }} catch {{ return "system"; }} }}
function appliquerTheme(theme) {{
  if (theme === "system") delete racine.dataset.theme; else racine.dataset.theme = theme;
  try {{ localStorage.setItem("theme", theme); }} catch {{}}
}}
document.querySelectorAll('input[name="theme"]').forEach((bouton) => {{
  bouton.checked = bouton.value === lireTheme();
  bouton.addEventListener("change", () => appliquerTheme(bouton.value));
}});
appliquerTheme(lireTheme());

function appliquerPolice() {{
  const police = etat.police;
  racine.style.setProperty("--famille-active", `"${{police.famille}}"`);
  const variation = Object.entries(etat.axes).map(([tag, v]) => `"${{tag}}" ${{v}}`).join(", ");
  // Chaque fonction est pilotée explicitement (1 ou 0) : calt, actif par défaut, peut être coupé
  const fonctions = police.fonctions.map((f) => `"${{f.tag}}" ${{etat.fonctions.has(f.tag) ? 1 : 0}}`).join(", ");
  document.querySelectorAll(".apercu, .glyphe").forEach((element) => {{
    element.style.fontWeight = police.axes.length ? "" : police.graisse;
    element.style.fontStyle = police.italique ? "italic" : "normal";
    element.style.fontVariationSettings = variation || "normal";
    element.style.fontFeatureSettings = fonctions || "normal";
  }});
}}

function reglageSynchronise(conteneur, id, libelle, min, max, valeur, pas, auChangement) {{
  const bloc = document.createElement("div");
  bloc.className = "reglage";
  bloc.innerHTML = `<label for="${{id}}">${{libelle}}</label>
    <input id="${{id}}" type="range" min="${{min}}" max="${{max}}" step="${{pas}}" value="${{valeur}}">
    <input type="number" min="${{min}}" max="${{max}}" step="${{pas}}" value="${{valeur}}" aria-label="${{libelle}}, valeur">`;
  const [curseur, champ] = bloc.querySelectorAll("input");
  const synchroniser = (source, cible) => source.addEventListener("input", () => {{ cible.value = source.value; auChangement(Number(source.value)); }});
  synchroniser(curseur, champ); synchroniser(champ, curseur);
  conteneur.append(bloc);
}}

function construireReglagesPolice() {{
  const conteneurAxes = document.getElementById("axes");
  const conteneurFonctions = document.getElementById("fonctions");
  conteneurAxes.replaceChildren();
  conteneurFonctions.querySelectorAll("label").forEach((l) => l.remove());
  etat.axes = {{}}; etat.fonctions.clear();
  for (const axe of etat.police.axes) {{
    etat.axes[axe.tag] = axe.defaut;
    reglageSynchronise(conteneurAxes, `axe-${{axe.tag}}`, `Axe ${{axe.tag}}`, axe.min, axe.max, axe.defaut, 1,
      (valeur) => {{ etat.axes[axe.tag] = valeur; appliquerPolice(); }});
  }}
  for (const fonction of etat.police.fonctions) {{
    if (fonction.parDefaut) etat.fonctions.add(fonction.tag);
    const libelle = document.createElement("label");
    libelle.innerHTML = `<input type="checkbox" value="${{fonction.tag}}"${{fonction.parDefaut ? " checked" : ""}}> ${{fonction.libelle}} <span class="code">${{fonction.tag}}</span>`.replace("> <", "><");
    libelle.querySelector("input").addEventListener("change", (evenement) => {{
      evenement.target.checked ? etat.fonctions.add(fonction.tag) : etat.fonctions.delete(fonction.tag);
      appliquerPolice();
    }});
    conteneurFonctions.append(libelle);
  }}
  conteneurFonctions.hidden = etat.police.fonctions.length === 0;
  appliquerPolice();
}}

const choixStyle = document.getElementById("style");
POLICES.forEach((police, indice) => choixStyle.add(new Option(police.nom, indice)));
choixStyle.addEventListener("change", () => {{ etat.police = POLICES[choixStyle.value]; construireReglagesPolice(); }});

const editable = document.querySelector(".editable");
const tailleCurseur = document.getElementById("taille-curseur"), tailleChamp = document.getElementById("taille-champ");
const appliquerTaille = (px) => editable.style.setProperty("--taille", `${{px / 16}}rem`);
tailleCurseur.addEventListener("input", () => {{ tailleChamp.value = tailleCurseur.value; appliquerTaille(tailleCurseur.value); }});
tailleChamp.addEventListener("input", () => {{ tailleCurseur.value = tailleChamp.value; appliquerTaille(tailleChamp.value); }});

const cascade = document.getElementById("cascade");
for (const px of [12, 14, 16, 20, 24, 32, 48, 64, 96]) {{
  const ligne = document.createElement("p");
  ligne.style.fontSize = `${{px / 16}}rem`;
  ligne.innerHTML = `<span>${{px}} px</span>`;
  ligne.append(document.createTextNode(editable.textContent));
  cascade.append(ligne);
}}
editable.addEventListener("input", () => cascade.querySelectorAll("p").forEach((ligne) => {{ ligne.lastChild.textContent = editable.textContent; }}));

construireReglagesPolice();

const boutonCredit = document.getElementById("copier-credit");
if (boutonCredit) {{
  boutonCredit.addEventListener("click", async () => {{
    const statut = document.getElementById("statut-credit");
    try {{
      await navigator.clipboard.writeText(document.getElementById("credit").textContent);
      statut.textContent = "Mention copiée.";
    }} catch {{
      statut.textContent = "Copie impossible : sélectionnez le texte ci-dessus.";
    }}
  }});
}}
</script>
</body>
</html>
"""


def main() -> None:
    parseur = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parseur.add_argument("polices", nargs="+", type=Path)
    parseur.add_argument("--nom", required=True)
    parseur.add_argument("--sortie", type=Path, default=Path("specimen/index.html"))
    parseur.add_argument("--texte", default=TEXTE_DEPART, help="Texte d’essai (utile tant que l’alphabet est incomplet)")
    parseur.add_argument("--credit", help="Mention à copier par qui utilise la police (facultative pour l’OFL)")
    args = parseur.parse_args()

    polices = [decrire_police(f, i) for i, f in enumerate(sorted(args.polices))]
    polices.sort(key=lambda p: (p["italique"], p["graisse"]))
    args.sortie.parent.mkdir(parents=True, exist_ok=True)
    args.sortie.write_text(generer(polices, args.nom, args.texte, args.credit), encoding="utf-8")
    print(f"Spécimen : {args.sortie.resolve()} ({args.sortie.stat().st_size // 1024} Ko)")


if __name__ == "__main__":
    main()
