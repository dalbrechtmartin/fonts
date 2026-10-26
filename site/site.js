// Présentation des polices : lit polices.json (généré par tools/polices.py site) et construit une section
// par police à partir des modèles de index.html. Chaque police est chargée sous un nom interne
// (« essai-<id> ») pour ne pas se mélanger avec les polices de l'interface.
(function () {
  'use strict';

  var racine = document.documentElement;
  var annonce = document.getElementById('annonce');
  var BADGES_STATUT = { 'bêta': 'gr-badge--beta', 'stable': 'gr-badge--done', 'retirée': 'gr-badge--retired' };
  var LICENCES = { 'OFL-1.1': 'SIL Open Font License 1.1' };
  var SECTIONS_CHANGELOG = { 'Features': 'Nouveautés', 'Bug Fixes': 'Corrections', 'Performance Improvements': 'Performances' };

  // ---------- Outils ----------
  function creer(balise, attributs, texte) {
    var element = document.createElement(balise);
    Object.keys(attributs || {}).forEach(function (nom) { element.setAttribute(nom, attributs[nom]); });
    if (texte !== undefined) element.textContent = texte;
    return element;
  }
  function trouver(conteneur, selecteur) { return conteneur.querySelector(selecteur); }
  function cloner(idModele) { return document.getElementById(idModele).content.firstElementChild.cloneNode(true); }
  function famille(police) { return '"essai-' + police.id + '"'; }
  function pointDeCode(caractere) { return 'U+' + caractere.codePointAt(0).toString(16).toUpperCase().padStart(4, '0'); }
  function dateLisible(iso) {
    var date = new Date(iso + 'T12:00:00');
    return isNaN(date) ? iso : date.toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' });
  }
  function annoncer(texte) {
    annonce.textContent = texte;
    setTimeout(function () { annonce.textContent = ''; }, 2000);
  }
  function lireReglages() {
    try { return JSON.parse(localStorage.getItem('reglages')) || {}; } catch (erreur) { return {}; }
  }
  function enregistrerReglages(reglages) {
    try { localStorage.setItem('reglages', JSON.stringify(reglages)); } catch (erreur) {}
  }

  // ---------- Accordéon (motif WAI-ARIA, comme le composant Accordion de Grimoire) ----------
  function ouvrir(declencheur, ouvert) {
    var panneau = document.getElementById(declencheur.getAttribute('aria-controls'));
    declencheur.setAttribute('aria-expanded', ouvert ? 'true' : 'false');
    panneau.classList.toggle('is-open', ouvert);
    panneau.inert = !ouvert;
  }
  function activerAccordeon(conteneur) {
    conteneur.querySelectorAll('.gr-accordion__trigger').forEach(function (declencheur) {
      declencheur.addEventListener('click', function () {
        ouvrir(declencheur, declencheur.getAttribute('aria-expanded') !== 'true');
      });
    });
  }

  // ---------- Options : thème, taille du texte, animations, police lisible ----------
  (function options() {
    var fenetre = document.getElementById('options');
    var bouton = document.getElementById('ouvrir-options');
    var interrupteur = trouver(fenetre, '[data-police-lisible]');
    var systemeSombre = window.matchMedia('(prefers-color-scheme: dark)');
    var mouvementReduit = window.matchMedia('(prefers-reduced-motion: reduce)');
    var reglages = lireReglages();

    function appliquer() {
      var sombre = reglages.theme ? reglages.theme === 'dark' : systemeSombre.matches;
      racine.setAttribute('data-theme', sombre ? 'dark' : 'light');
      if (reglages.text && reglages.text !== 'm') racine.setAttribute('data-text', reglages.text);
      else racine.removeAttribute('data-text');
      if (reglages.motion) racine.setAttribute('data-motion', reglages.motion);
      else racine.removeAttribute('data-motion');
      if (reglages.font) racine.setAttribute('data-font', 'lisible');
      else racine.removeAttribute('data-font');
    }
    function afficher() {
      var valeurs = {
        theme: reglages.theme || '',
        text: reglages.text || 'm',
        motion: reglages.motion || (mouvementReduit.matches ? 'reduced' : 'full')
      };
      Object.keys(valeurs).forEach(function (nom) {
        trouver(fenetre, 'input[name="' + nom + '"][value="' + valeurs[nom] + '"]').checked = true;
      });
      interrupteur.setAttribute('aria-checked', reglages.font ? 'true' : 'false');
      interrupteur.previousElementSibling.textContent = reglages.font ? 'Oui' : 'Non';
    }
    function changer(nom, valeur) {
      if (valeur) reglages[nom] = valeur; else delete reglages[nom];
      enregistrerReglages(reglages);
      appliquer();
      afficher();
    }

    fenetre.querySelectorAll('input[type=radio]').forEach(function (choix) {
      choix.addEventListener('change', function () { changer(choix.name, choix.value); });
    });
    interrupteur.addEventListener('click', function () { changer('font', !reglages.font); });
    trouver(fenetre, '[data-reinitialiser]').addEventListener('click', function () {
      reglages = {};
      enregistrerReglages(reglages);
      appliquer();
      afficher();
      annoncer('Options remises par défaut.');
    });
    // Le thème « Système » suit le système en direct
    systemeSombre.addEventListener('change', appliquer);

    bouton.addEventListener('click', function () {
      afficher();
      fenetre.showModal();
      bouton.setAttribute('aria-expanded', 'true');
    });
    fenetre.querySelectorAll('[data-fermer]').forEach(function (fermer) {
      fermer.addEventListener('click', function () { fenetre.close(); });
    });
    fenetre.addEventListener('close', function () {
      bouton.setAttribute('aria-expanded', 'false');
      bouton.focus();
    });
    // Clic sur le fond, hors du panneau : ferme la fenêtre
    fenetre.addEventListener('click', function (evenement) { if (evenement.target === fenetre) fenetre.close(); });
  })();

  activerAccordeon(document.querySelector('[data-accordeon]'));

  // ---------- Polices ----------
  function chargerPolice(police) {
    return Promise.all(police.graisses.map(function (graisse) {
      var fonte = new FontFace('essai-' + police.id, 'url("' + graisse.woff2 + '") format("woff2")',
        { weight: String(graisse.poids), display: 'swap' });
      document.fonts.add(fonte);
      return fonte.load().catch(function () {});
    }));
  }

  function remplirTete(article, police, depot) {
    var nom = trouver(article, '[data-nom]');
    nom.id = police.id + '-titre';
    nom.textContent = police.nom;
    nom.style.fontFamily = famille(police) + ', var(--font-display)';

    var etiquettes = trouver(article, '[data-etiquettes]');
    var version = creer('span', { 'class': 'gr-badge gr-badge--new' });
    version.append(creer('span', { 'class': 'gr-badge__mark', 'aria-hidden': 'true' }, '✦'), 'Version ' + police.version);
    etiquettes.appendChild(creer('li')).appendChild(version);
    if (police.statut) {
      etiquettes.appendChild(creer('li')).appendChild(
        creer('span', { 'class': 'gr-badge ' + (BADGES_STATUT[police.statut] || '') }, police.statut));
    }
    (police.etiquettes || []).forEach(function (etiquette) {
      etiquettes.appendChild(creer('li')).appendChild(creer('span', { 'class': 'gr-chip' }, etiquette));
    });

    trouver(article, '[data-resume]').textContent = police.resume;
    var description = trouver(article, '[data-description]');
    if (police.description) description.textContent = police.description; else description.remove();

    var fiche = trouver(article, '[data-fiche]');
    function ajouterLigne(libelle, valeur) {
      fiche.appendChild(creer('dt', {}, libelle));
      var cellule = fiche.appendChild(creer('dd'));
      if (typeof valeur === 'string') cellule.textContent = valeur; else cellule.appendChild(valeur);
    }
    ajouterLigne('Dessin', police.dessin);
    if (police.origine) {
      var origine = creer('span');
      origine.append('Dérivée de ', creer('a', { href: police.origine.url }, police.origine.nom));
      ajouterLigne('Origine', origine);
    }
    ajouterLigne('Graisses', police.graisses.map(function (graisse) { return graisse.nom + ' (' + graisse.poids + ')'; }).join(', '));
    ajouterLigne('Glyphes', String(Array.from(police.glyphes).length));
    ajouterLigne('Licence', LICENCES[police.licence] || police.licence);
    if (police.nomReserve) ajouterLigne('Nom réservé', '« ' + police.nomReserve + ' » : une version modifiée doit changer de nom');
    if (police.historique.length) ajouterLigne('Mise à jour', dateLisible(police.historique[0].date));
    if (police.usage) ajouterLigne('Usage', police.usage);

    var actions = trouver(article, '[data-actions]');
    var telecharger = creer('a', { 'class': 'gr-btn gr-btn--primary', href: police.telechargement, download: '' });
    telecharger.append(creer('span', { 'class': 'gr-btn__star', 'aria-hidden': 'true' }, '✦'),
      'Télécharger la ' + police.version + ' (zip)',
      creer('span', { 'class': 'gr-btn__star', 'aria-hidden': 'true' }, '✦'));
    actions.append(telecharger,
      creer('a', { 'class': 'gr-btn', href: police.sources }, 'Voir les sources'),
      creer('a', { 'class': 'gr-btn gr-btn--ghost', href: depot + '/releases?q=' + encodeURIComponent(police.id) }, 'Voir toutes les versions'));
  }

  function remplirEssai(article, police) {
    var essai = trouver(article, '[data-essai]');
    var specimen = police.specimen;
    var taillesNettes = (specimen.taillesNettes || []).map(String);
    var sortie = trouver(essai, '[data-sortie]');
    var legende = trouver(essai, '[data-legende]');
    var champTexte = trouver(essai, '[data-champ="texte"]');
    var curseur = trouver(essai, '[data-champ="curseur"]');
    var champTaille = trouver(essai, '[data-champ="taille"]');
    var indicateurNet = trouver(essai, '[data-net]');
    var choixGraisse = trouver(essai, '[data-choix-graisse]');

    ['texte', 'taille'].forEach(function (nom) {
      var id = police.id + '-essai-' + nom;
      trouver(essai, '[data-champ="' + nom + '"]').id = id;
      trouver(essai, '[data-pour="' + nom + '"]').setAttribute('for', id);
    });
    champTexte.value = specimen.texte || specimen.titre || police.nom;
    [curseur, champTaille].forEach(function (champ) {
      champ.min = specimen.tailleMin || 16;
      champ.max = specimen.tailleMax || 128;
    });
    // Sur un écran étroit, on part de la plus petite taille nette (ou de la moitié) pour garder des mots entiers
    var tailleDepart = specimen.tailleParDefaut || 64;
    if (window.matchMedia('(max-width: 40rem)').matches) tailleDepart = Number(taillesNettes[0]) || Math.max(curseur.min, Math.round(tailleDepart / 2));
    curseur.value = champTaille.value = tailleDepart;

    // Graisses en boutons segmentés ; le choix n'apparaît que s'il y en a plusieurs
    police.graisses.forEach(function (graisse, rang) {
      var id = police.id + '-graisse-' + graisse.poids;
      var bouton = creer('input', { type: 'radio', name: police.id + '-graisse', id: id, value: graisse.poids });
      bouton.checked = rang === 0;
      choixGraisse.append(bouton, creer('label', { 'for': id }, graisse.nom));
      bouton.addEventListener('change', afficherEssai);
    });
    if (police.graisses.length < 2) trouver(essai, '[data-graisses-essai]').remove();

    var casesFonctions = (police.fonctions || []).map(function (fonction) {
      var choix = cloner('modele-fonction');
      var caseFonction = trouver(choix, 'input');
      caseFonction.value = fonction.code;
      caseFonction.checked = !!fonction.parDefaut;
      trouver(choix, '.gr-check__label').textContent = fonction.libelle + ' (' + fonction.code + ')';
      trouver(essai, '[data-fonctions]').appendChild(choix);
      caseFonction.addEventListener('change', afficherEssai);
      return caseFonction;
    });
    if (casesFonctions.length) trouver(essai, '[data-fonctions]').hidden = false;

    function graisseChoisie() {
      var choisie = trouver(essai, 'input[name="' + police.id + '-graisse"]:checked');
      return choisie ? police.graisses.find(function (graisse) { return String(graisse.poids) === choisie.value; }) : police.graisses[0];
    }
    function afficherEssai() {
      var taille = Math.min(Number(curseur.max), Math.max(Number(curseur.min), Number(champTaille.value) || Number(curseur.value)));
      var nette = taillesNettes.indexOf(String(taille)) !== -1;
      var graisse = graisseChoisie();
      sortie.textContent = champTexte.value.trim() || 'Tape un texte';
      sortie.style.fontFamily = famille(police);
      sortie.style.fontWeight = graisse.poids;
      sortie.style.fontSize = taille + 'px';
      // Chaque fonction est écrite explicitement : décocher calt doit bien le couper
      sortie.style.fontFeatureSettings = casesFonctions.map(function (caseFonction) {
        return '"' + caseFonction.value + '" ' + (caseFonction.checked ? 1 : 0);
      }).join(', ') || 'normal';
      indicateurNet.textContent = nette ? '✦ net' : '';
      legende.textContent = police.nom + ' · ' + graisse.nom + ' · ' + taille + ' px' + (nette ? ' ✦ net' : '');
    }
    curseur.addEventListener('input', function () { champTaille.value = curseur.value; afficherEssai(); });
    champTaille.addEventListener('input', function () { curseur.value = champTaille.value; afficherEssai(); });
    champTaille.addEventListener('change', function () { champTaille.value = curseur.value; afficherEssai(); });
    champTexte.addEventListener('input', afficherEssai);
    afficherEssai();
  }

  function remplirGraisses(article, police) {
    if (police.graisses.length < 2) { trouver(article, '[data-section-graisses]').remove(); return; }
    var liste = trouver(article, '[data-graisses]');
    police.graisses.forEach(function (graisse) {
      var ligne = liste.appendChild(creer('li'));
      var exemple = creer('span', { 'class': 'graisses__exemple' }, police.specimen.titre || police.nom);
      exemple.style.fontFamily = famille(police);
      exemple.style.fontWeight = graisse.poids;
      ligne.append(creer('span', { 'class': 'gr-meta' }, graisse.nom + ' · ' + graisse.poids), exemple);
    });
  }

  function remplirGlyphes(article, police) {
    var caracteres = Array.from(police.glyphes);
    var grille = trouver(article, '[data-grille]');
    var loupe = trouver(article, '[data-loupe]');
    var codePoint = trouver(article, '[data-code-point]');
    trouver(article, '[data-titre-glyphes]').textContent = 'Glyphes (' + caracteres.length + ')';
    grille.setAttribute('aria-label', 'Glyphes de ' + police.nom);
    grille.style.fontFamily = loupe.style.fontFamily = famille(police);
    var cellules = caracteres.map(function (caractere, rang) {
      var cellule = creer('button', { type: 'button', 'class': 'glyphe', role: 'option', 'aria-selected': 'false',
        'aria-label': caractere + ' (' + pointDeCode(caractere) + ')', tabindex: rang === 0 ? '0' : '-1' }, caractere);
      cellule.addEventListener('click', function () { selectionner(rang, false); });
      grille.appendChild(cellule);
      return cellule;
    });
    var actuel = 0;
    function selectionner(rang, donnerFocus) {
      cellules[actuel].setAttribute('aria-selected', 'false');
      cellules[actuel].tabIndex = -1;
      actuel = rang;
      cellules[rang].setAttribute('aria-selected', 'true');
      cellules[rang].tabIndex = 0;
      if (donnerFocus) cellules[rang].focus();
      loupe.textContent = caracteres[rang];
      codePoint.textContent = pointDeCode(caracteres[rang]);
    }
    // Flèches, Début et Fin pour parcourir la grille
    grille.addEventListener('keydown', function (evenement) {
      var colonnes = Math.max(1, Math.round(grille.clientWidth / cellules[0].offsetWidth));
      var cible = { ArrowRight: actuel + 1, ArrowLeft: actuel - 1, ArrowDown: actuel + colonnes, ArrowUp: actuel - colonnes,
        Home: 0, End: cellules.length - 1 }[evenement.key];
      if (cible === undefined) return;
      evenement.preventDefault();
      selectionner(Math.min(cellules.length - 1, Math.max(0, cible)), true);
    });
    if (cellules.length) selectionner(Math.max(0, caracteres.indexOf('A')), false);
  }

  function remplirCss(article, police) {
    var nomFichier = police.nom.replace(/\s+/g, '');
    var css = police.graisses.map(function (graisse) {
      return '@font-face {\n  font-family: "' + police.nom + '";\n  src: url("fonts/' + nomFichier + '-' + graisse.nom +
        '.woff2") format("woff2");\n  font-weight: ' + graisse.poids + ';\n  font-style: normal;\n  font-display: swap;\n}';
    }).join('\n') + '\n\nh1, h2, h3 {\n  font-family: "' + police.nom + '", Georgia, serif;\n}';
    trouver(article, '[data-css]').textContent = css;
    var copier = trouver(article, '[data-copier]');
    var libelle = trouver(copier, '.gr-code__action-text');
    copier.addEventListener('click', function () {
      navigator.clipboard.writeText(css).then(function () {
        libelle.textContent = 'Copié';
        annoncer('CSS de ' + police.nom + ' copié.');
      }, function () {
        annoncer('Copie impossible : sélectionne le texte à la main.');
      });
      setTimeout(function () { libelle.textContent = 'Copier le CSS'; }, 2000);
    });
  }

  function remplirHistorique(article, police) {
    var accordeon = trouver(article, '[data-historique]');
    police.historique.forEach(function (version, rang) {
      var id = police.id + '-v' + version.version.replace(/\./g, '-');
      var element = cloner('modele-version');
      var declencheur = trouver(element, '.gr-accordion__trigger');
      var panneau = trouver(element, '.gr-accordion__panel');
      var contenu = trouver(element, '.changements');
      declencheur.id = id + '-declencheur';
      declencheur.setAttribute('aria-controls', id + '-panneau');
      panneau.id = id + '-panneau';
      panneau.setAttribute('aria-labelledby', declencheur.id);
      trouver(element, '.gr-accordion__label').textContent = 'Version ' + version.version + ' · ' + dateLisible(version.date);
      version.sections.forEach(function (section) {
        contenu.appendChild(creer('h5', {}, SECTIONS_CHANGELOG[section.titre] || section.titre));
        var liste = contenu.appendChild(creer('ul'));
        // Entrées déjà échappées par tools/polices.py (Markdown limité : code, gras, liens)
        section.entrees.forEach(function (entree) { liste.appendChild(creer('li')).innerHTML = entree; });
      });
      if (version.url) {
        contenu.appendChild(creer('p', { 'class': 'gr-meta' })).appendChild(
          creer('a', { href: version.url }, 'Comparer avec la version précédente'));
      }
      accordeon.appendChild(element);
      if (rang === 0) ouvrir(declencheur, true);
    });
    activerAccordeon(accordeon);
  }

  function construirePolice(police, depot) {
    var article = cloner('modele-police');
    article.id = police.id;
    article.setAttribute('aria-labelledby', police.id + '-titre');
    remplirTete(article, police, depot);
    remplirEssai(article, police);
    remplirGraisses(article, police);
    remplirGlyphes(article, police);
    remplirCss(article, police);
    return article;
  }

  function construireVignette(police) {
    var lien = creer('a', { 'class': 'gr-tile', href: '#' + police.id });
    var apercu = creer('span', { 'class': 'gr-tile__art gr-frame', 'aria-hidden': 'true' }, 'Aa');
    apercu.style.fontFamily = famille(police);
    lien.append(apercu, creer('span', { 'class': 'gr-tile__name' }, police.nom),
      creer('span', { 'class': 'gr-tile__kind' }, 'Version ' + police.version + ' · ' + police.resume));
    var element = creer('li');
    element.appendChild(lien);
    return element;
  }

  fetch('polices.json')
    .then(function (reponse) { if (!reponse.ok) throw new Error(reponse.status); return reponse.json(); })
    .then(function (donnees) {
      var navigation = document.getElementById('navigation');
      var sommaire = document.getElementById('sommaire');
      var conteneur = document.getElementById('polices');
      donnees.polices.forEach(function (police) {
        chargerPolice(police);
        navigation.appendChild(creer('li')).appendChild(creer('a', { href: '#' + police.id }, police.nom));
        sommaire.appendChild(construireVignette(police));
        var article = conteneur.appendChild(construirePolice(police, donnees.depot));
        // L'historique s'ajoute une fois l'article dans la page : ses panneaux se retrouvent par id
        remplirHistorique(article, police);
      });
      var nombreGlyphes = donnees.polices.reduce(function (total, police) { return total + Array.from(police.glyphes).length; }, 0);
      document.getElementById('statistiques').textContent = donnees.polices.length +
        (donnees.polices.length > 1 ? ' polices' : ' police') + ' · ' + nombreGlyphes + ' glyphes au total';
      if (location.hash) {
        var cible = document.getElementById(location.hash.slice(1));
        if (cible) cible.scrollIntoView();
      }
    })
    .catch(function () {
      document.getElementById('statistiques').textContent = 'Impossible de charger la liste des polices. Elles restent disponibles sur GitHub.';
    });
})();
