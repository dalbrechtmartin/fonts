// Interactions du site des polices. Les pages sont déjà complètes en HTML (générées par tools/polices.py site) :
// ce script ajoute seulement les options, les onglets, l'essai, la grille des glyphes, le vérificateur de langue,
// les copies, le menu des sections et le bouton « Haut ». Chaque partie ne s'active que si sa page la contient.
(function () {
  'use strict';

  var racine = document.documentElement;
  var annonce = document.getElementById('annonce');
  racine.classList.add('js');

  // ---------- Outils ----------
  function tous(selecteur, conteneur) { return Array.prototype.slice.call((conteneur || document).querySelectorAll(selecteur)); }
  function un(selecteur, conteneur) { return (conteneur || document).querySelector(selecteur); }
  function animationsReduites() {
    var reglage = racine.getAttribute('data-motion');
    if (reglage) return reglage !== 'full';
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
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
  // Copie dans le presse-papiers : le libellé du bouton dit le résultat pendant 2 s, et il est annoncé
  function copier(bouton, texte, reussite) {
    var libelle = un('[data-libelle]', bouton) || bouton;
    var initial = libelle.textContent;
    navigator.clipboard.writeText(texte).then(function () {
      libelle.textContent = reussite + ' ✓';
      annoncer(reussite + '.');
    }, function () {
      annoncer('Copie impossible : sélectionne le texte à la main.');
    });
    setTimeout(function () { libelle.textContent = initial; }, 2000);
  }

  // ---------- Options : thème, taille du texte, animations, police lisible ----------
  (function options() {
    var fenetre = document.getElementById('options');
    var bouton = document.getElementById('ouvrir-options');
    var interrupteur = un('[data-police-lisible]', fenetre);
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
        un('input[name="' + nom + '"][value="' + valeurs[nom] + '"]', fenetre).checked = true;
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

    tous('input[type=radio]', fenetre).forEach(function (choix) {
      choix.addEventListener('change', function () { changer(choix.name, choix.value); });
    });
    interrupteur.addEventListener('click', function () { changer('font', !reglages.font); });
    un('[data-reinitialiser]', fenetre).addEventListener('click', function () {
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
    tous('[data-fermer]', fenetre).forEach(function (fermer) {
      fermer.addEventListener('click', function () { fenetre.close(); });
    });
    fenetre.addEventListener('close', function () {
      bouton.setAttribute('aria-expanded', 'false');
      bouton.focus();
    });
    // Clic sur le fond, hors du panneau : ferme la fenêtre
    fenetre.addEventListener('click', function (evenement) { if (evenement.target === fenetre) fenetre.close(); });
  })();

  // ---------- Accordéons (motif WAI-ARIA, comme le composant Accordion de Grimoire) ----------
  tous('[data-accordeon] .gr-accordion__trigger').forEach(function (declencheur) {
    declencheur.addEventListener('click', function () {
      var ouvert = declencheur.getAttribute('aria-expanded') !== 'true';
      var panneau = document.getElementById(declencheur.getAttribute('aria-controls'));
      declencheur.setAttribute('aria-expanded', ouvert ? 'true' : 'false');
      panneau.classList.toggle('is-open', ouvert);
      panneau.inert = !ouvert;
    });
  });

  // ---------- Bouton « Haut » (BackToTop de Grimoire) et menu des sections ----------
  (function defilement() {
    var haut = document.getElementById('haut-de-page');
    var menu = un('[data-menu-sections]');
    var liens = menu ? tous('a[href^="#"]', menu) : [];
    var liste = menu ? un('ul', menu) : null;
    var actuel = null;
    var enAttente = false;

    function mettreAJour() {
      enAttente = false;
      var page = document.documentElement;
      var max = page.scrollHeight - page.clientHeight;
      haut.classList.toggle('is-shown', page.scrollTop > 400);
      haut.style.setProperty('--progress', String(max > 0 ? page.scrollTop / max : 0));
      if (!menu) return;
      // Section en cours : la dernière dont le haut est passé sous le menu
      var limite = menu.getBoundingClientRect().bottom + 48;
      var trouve = null;
      liens.forEach(function (lien) {
        var section = document.getElementById(lien.hash.slice(1));
        if (section && section.getBoundingClientRect().top <= limite) trouve = lien;
      });
      if (trouve === actuel) return;
      if (actuel) actuel.removeAttribute('aria-current');
      actuel = trouve;
      if (!actuel) return;
      actuel.setAttribute('aria-current', 'location');
      // Mobile : le menu défile de côté pour montrer la section en cours (sans faire défiler la page)
      if (liste.scrollWidth > liste.clientWidth) liste.scrollLeft = actuel.parentNode.offsetLeft - liste.offsetLeft - 16;
    }
    window.addEventListener('scroll', function () {
      if (!enAttente) { enAttente = true; requestAnimationFrame(mettreAJour); }
    }, { passive: true });
    mettreAJour();

    un('button', haut).addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: animationsReduites() ? 'auto' : 'smooth' });
      var titre = document.getElementById('titre');
      if (titre) titre.focus({ preventScroll: true });
    });
  })();

  // ---------- Onglets en boutons segmentés (système d'exploitation, façon d'utiliser sur un site) ----------
  function systemeProbable() {
    var plateforme = ((navigator.userAgentData && navigator.userAgentData.platform) || navigator.platform || '') + ' ' + navigator.userAgent;
    if (/Mac|iPhone|iPad/i.test(plateforme)) return 'macOS';
    if (/Linux/i.test(plateforme) && !/Android/i.test(plateforme)) return 'Linux';
    if (/Win/i.test(plateforme)) return 'Windows';
    return null;
  }
  tous('[data-onglets]').forEach(function (groupe) {
    var boutons = tous('[data-onglet]', groupe);
    var panneaux = boutons.map(function (bouton) { return document.getElementById(bouton.getAttribute('aria-controls')); });
    function choisir(valeur) {
      boutons.forEach(function (bouton, rang) {
        var choisi = bouton.getAttribute('data-onglet') === valeur;
        bouton.setAttribute('aria-pressed', choisi ? 'true' : 'false');
        panneaux[rang].hidden = !choisi;
      });
    }
    boutons.forEach(function (bouton) {
      bouton.addEventListener('click', function () { choisir(bouton.getAttribute('data-onglet')); });
    });
    groupe.hidden = false;
    var defaut = boutons[0].getAttribute('data-onglet');
    if (groupe.getAttribute('data-onglets') === 'systeme') {
      var detecte = systemeProbable();
      if (detecte) {
        defaut = detecte;
        un('[data-systeme-auto]').hidden = false;
      }
    }
    choisir(defaut);
  });

  // ---------- Accueil : un texte pour toutes les polices ----------
  var texteCatalogue = un('[data-texte-catalogue]');
  if (texteCatalogue) {
    // Anciens liens (accueil#griffonne, quand toutes les polices étaient sur une page) : vers la page de la police
    if (location.hash) {
      var anciennePolice = un('.carte-police__nom a[href$="/' + CSS.escape(location.hash.slice(1)) + '/"]');
      if (anciennePolice) location.replace(anciennePolice.href);
    }
    texteCatalogue.addEventListener('input', function () {
      tous('[data-exemple-catalogue]').forEach(function (exemple) {
        exemple.textContent = texteCatalogue.value.trim() || exemple.getAttribute('data-exemple-catalogue');
      });
    });
  }

  // ---------- Page d'une police ----------
  var donneesPage = document.getElementById('donnees-police');
  if (!donneesPage) return;
  var police = JSON.parse(donneesPage.textContent);
  var jeuGlyphes = new Set(Array.from(police.glyphes));

  // Essai : texte, taille, graisse, exemples par langue, fonctions OpenType, lien à partager
  (function essai() {
    var bloc = un('[data-essai]');
    var sortie = un('[data-sortie]', bloc);
    var champTexte = un('[data-texte]', bloc);
    var curseur = un('[data-curseur]', bloc);
    var champTaille = un('[data-taille]', bloc);
    var exemples = tous('[data-exemple]', bloc);
    var cases = tous('[data-fonction]', bloc);
    var extraits = tous('[data-extrait]');
    var texteParDefaut = champTexte.value;

    function bornee(valeur) {
      return Math.min(Number(curseur.max), Math.max(Number(curseur.min), Math.round(Number(valeur) || Number(curseur.value))));
    }
    // Chaque fonction est écrite explicitement : décocher calt doit bien le couper
    function reglageOpenType() {
      return cases.map(function (caseFonction) { return '"' + caseFonction.value + '" ' + (caseFonction.checked ? 1 : 0); }).join(', ');
    }
    // Pour le CSS à copier : seulement ce qui diffère du réglage par défaut de la police
    function ecartsOpenType() {
      return cases.filter(function (caseFonction) {
        return caseFonction.checked !== (police.parDefaut.indexOf(caseFonction.value) !== -1);
      }).map(function (caseFonction) { return '"' + caseFonction.value + '" ' + (caseFonction.checked ? 1 : 0); });
    }
    function afficher() {
      var exemple = exemples.filter(function (bouton) { return bouton.getAttribute('data-exemple') === champTexte.value; })[0];
      var graisse = un('[data-graisse]:checked', bloc);
      sortie.textContent = champTexte.value.trim() ? champTexte.value : texteParDefaut;
      sortie.lang = exemple ? exemple.getAttribute('data-lang') : 'fr';
      sortie.style.fontSize = bornee(champTaille.value) + 'px';
      sortie.style.fontWeight = graisse ? graisse.value : '';
      if (cases.length) sortie.style.fontFeatureSettings = reglageOpenType();
      exemples.forEach(function (bouton) { bouton.setAttribute('aria-pressed', bouton === exemple ? 'true' : 'false'); });
      cases.forEach(function (caseFonction) {
        un('[data-etat-fonction]', caseFonction.closest('li')).textContent = caseFonction.checked ? 'activée' : 'désactivée';
      });
      var ecarts = ecartsOpenType();
      extraits.forEach(function (code) {
        var modele = code.getAttribute('data-extrait');
        var ligne = modele.slice(modele.lastIndexOf('\n', modele.indexOf('<FSS>')) + 1);
        var retrait = /^\s*/.exec(ligne)[0];
        code.textContent = modele.replace('<FSS>', ecarts.length ? '\n' + retrait + 'font-feature-settings: ' + ecarts.join(', ') + ';' : '');
      });
    }

    curseur.addEventListener('input', function () { champTaille.value = curseur.value; afficher(); });
    champTaille.addEventListener('input', function () { curseur.value = bornee(champTaille.value); afficher(); });
    champTaille.addEventListener('change', function () { champTaille.value = bornee(champTaille.value); afficher(); });
    champTexte.addEventListener('input', afficher);
    tous('[data-graisse]', bloc).forEach(function (choix) { choix.addEventListener('change', afficher); });
    cases.forEach(function (caseFonction) { caseFonction.addEventListener('change', afficher); });
    exemples.forEach(function (bouton) {
      bouton.addEventListener('click', function () {
        champTexte.value = bouton.getAttribute('data-exemple');
        afficher();
        // Fondu court quand le texte change d'un coup (aucun avec les animations réduites)
        sortie.classList.remove('est-nouveau');
        if (!animationsReduites()) { void sortie.offsetWidth; sortie.classList.add('est-nouveau'); }
      });
    });

    // Le lien garde l'essai : texte, taille et fonctions dans l'adresse
    // Écran étroit : on part de la moitié de la taille par défaut, pour garder des mots entiers
    if (window.matchMedia('(max-width: 40rem)').matches) champTaille.value = curseur.value = bornee(Number(curseur.value) / 2);
    var parametres = new URLSearchParams(location.search);
    if (parametres.has('texte')) champTexte.value = parametres.get('texte');
    if (parametres.has('taille')) champTaille.value = curseur.value = bornee(parametres.get('taille'));
    if (parametres.has('fonctions')) {
      var actives = parametres.get('fonctions').split(',');
      cases.forEach(function (caseFonction) { caseFonction.checked = actives.indexOf(caseFonction.value) !== -1; });
    }
    var partager = un('[data-partager]', bloc);
    partager.addEventListener('click', function () {
      var adresse = new URL(location.href);
      adresse.hash = 'essayer';
      adresse.search = new URLSearchParams({
        texte: champTexte.value,
        taille: String(bornee(champTaille.value)),
        fonctions: cases.filter(function (caseFonction) { return caseFonction.checked; }).map(function (caseFonction) { return caseFonction.value; }).join(',')
      }).toString();
      copier(partager, adresse.href, 'Lien copié');
    });
    afficher();
  })();

  // Aide « Qu'est-ce qu'une fonction OpenType ? » : reste ouverte jusqu'à fermeture, Échap la ferme
  (function aideOpenType() {
    var bouton = un('[data-aide-ot]');
    if (!bouton) return;
    var aide = document.getElementById(bouton.getAttribute('aria-controls'));
    function ouvrir(ouverte, rendreFocus) {
      aide.hidden = !ouverte;
      bouton.setAttribute('aria-expanded', ouverte ? 'true' : 'false');
      if (rendreFocus) bouton.focus();
    }
    bouton.addEventListener('click', function () { ouvrir(aide.hidden, false); });
    un('[data-fermer-aide-ot]', aide).addEventListener('click', function () { ouvrir(false, true); });
    [bouton, aide].forEach(function (element) {
      element.addEventListener('keydown', function (evenement) {
        if (evenement.key === 'Escape' && !aide.hidden) { evenement.preventDefault(); ouvrir(false, true); }
      });
    });
  })();

  // Glyphes : grille parcourable au clavier (flèches, Début, Fin), loupe et copie
  (function glyphes() {
    var grille = un('[data-grille]');
    var cellules = tous('.glyphe', grille);
    var loupe = un('[data-loupe]');
    var nom = un('[data-loupe-nom]');
    var code = un('[data-loupe-code]');
    var actuel = 0;
    // Beaucoup de glyphes : les premiers seulement, le reste derrière « Afficher les N autres glyphes »
    var PREMIERS = 65;
    var visibles = cellules.length;
    var plus = un('[data-plus-glyphes]');
    if (cellules.length > PREMIERS + 13) {
      visibles = PREMIERS;
      cellules.slice(PREMIERS).forEach(function (cellule) { cellule.hidden = true; });
      un('[data-libelle]', plus).textContent = 'Afficher les ' + (cellules.length - PREMIERS) + ' autres glyphes';
      plus.hidden = false;
      plus.addEventListener('click', function () {
        cellules.forEach(function (cellule) { cellule.hidden = false; });
        visibles = cellules.length;
        plus.hidden = true;
        selectionner(PREMIERS, true);
        annoncer(cellules.length + ' glyphes affichés.');
      });
    }
    function selectionner(rang, donnerFocus) {
      cellules[actuel].setAttribute('aria-selected', 'false');
      cellules[actuel].tabIndex = -1;
      actuel = rang;
      cellules[rang].setAttribute('aria-selected', 'true');
      cellules[rang].tabIndex = 0;
      if (donnerFocus) cellules[rang].focus();
      loupe.textContent = cellules[rang].textContent;
      nom.textContent = cellules[rang].getAttribute('data-nom');
      code.textContent = cellules[rang].getAttribute('data-code');
    }
    cellules.forEach(function (cellule, rang) {
      cellule.addEventListener('click', function () { selectionner(rang, false); });
    });
    grille.addEventListener('keydown', function (evenement) {
      var colonnes = Math.max(1, Math.round(grille.clientWidth / cellules[0].offsetWidth));
      var cible = { ArrowRight: actuel + 1, ArrowLeft: actuel - 1, ArrowDown: actuel + colonnes, ArrowUp: actuel - colonnes,
        Home: 0, End: visibles - 1 }[evenement.key];
      if (cible === undefined) return;
      evenement.preventDefault();
      selectionner(Math.min(visibles - 1, Math.max(0, cible)), true);
    });
    var depart = cellules.map(function (cellule) { return cellule.textContent; }).indexOf('A');
    selectionner(Math.max(0, depart), false);
    var bouton = un('[data-copier-glyphe]');
    bouton.addEventListener('click', function () { copier(bouton, cellules[actuel].textContent, 'Caractère copié'); });
  })();

  // Vérifier un mot : chaque lettre existe-t-elle dans la police ?
  (function verificateur() {
    var bloc = un('[data-verificateur]');
    if (!bloc) return;
    var champ = un('[data-verif-texte]', bloc);
    var resultat = un('[data-verif-resultat]', bloc);
    var apercu = un('[data-verif-apercu]', bloc);
    var exempleApercu = apercu.textContent;
    var messageVide = resultat.textContent;
    var ICONES = {
      complet: '<svg class="gr-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12l5 5 9-10"/></svg>',
      incomplet: '<svg class="gr-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 4l9 16H3z"/><path d="M12 10v4M12 17v.5"/></svg>'
    };
    champ.addEventListener('input', function () {
      var texte = champ.value.normalize('NFC');
      var manquants = Array.from(new Set(Array.from(texte).filter(function (caractere) {
        return !/\s/.test(caractere) && !jeuGlyphes.has(caractere);
      })));
      apercu.textContent = texte.trim() ? texte : exempleApercu;
      resultat.classList.toggle('est-complet', !!texte.trim() && !manquants.length);
      resultat.classList.toggle('est-incomplet', manquants.length > 0);
      if (!texte.trim()) { resultat.textContent = messageVide; return; }
      var message = manquants.length
        ? (manquants.length > 1 ? 'Il manque ' + manquants.length + ' caractères : ' : 'Il manque 1 caractère : ') + manquants.join(' ') + '. Ils s’afficheront dans une police de secours.'
        : 'Toutes les lettres sont disponibles.';
      resultat.innerHTML = ICONES[manquants.length ? 'incomplet' : 'complet'];
      resultat.appendChild(document.createElement('span')).textContent = message;
    });
  })();

  // Copies : code pour un site, mention de l'autrice
  tous('[data-copier-code]').forEach(function (bouton) {
    bouton.addEventListener('click', function () {
      copier(bouton, un('code', bouton.closest('.gr-code')).textContent, 'Code copié');
    });
  });
  var boutonCredit = un('[data-copier-credit]');
  if (boutonCredit) {
    boutonCredit.addEventListener('click', function () { copier(boutonCredit, un('[data-credit]').textContent, 'Mention copiée'); });
  }
})();
