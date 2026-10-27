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

  // ---------- Accueil : recherche, filtres, tri, affichage et essai sur tout le catalogue ----------
  (function catalogue() {
    var liste = un('[data-liste]');
    if (!liste) return;
    // Anciens liens (accueil#griffonne, quand toutes les polices étaient sur une page) : vers la page de la police
    if (location.hash) {
      var anciennePolice = un('.carte-police__nom a[href$="/' + CSS.escape(location.hash.slice(1)) + '/"]');
      if (anciennePolice) { location.replace(anciennePolice.href); return; }
    }

    var PAR_PAGE = 24;
    // Critères gardés dans l'adresse ; les listes acceptent plusieurs valeurs (la police doit les avoir toutes)
    var CRITERES_SIMPLES = ['q', 'usage', 'style', 'graisses', 'statut', 'maj'];
    var CRITERES_LISTES = ['langue', 'fonction', 'lecture'];
    var CRITERES_FEUILLE = ['graisses', 'statut', 'maj', 'langue', 'fonction', 'lecture'];
    var titre = un('[data-titre-resultats]');
    var recherche = un('[data-recherche]');
    var texte = un('[data-texte-catalogue]');
    var curseur = un('[data-curseur-catalogue]');
    var champTaille = un('[data-taille-catalogue]');
    var tri = un('[data-tri]');
    var feuille = un('[data-feuille]');
    var boutonFiltres = un('[data-ouvrir-filtres]');
    var actifs = un('[data-filtres-actifs]');
    var aucune = un('[data-aucune]');
    var plus = un('[data-plus]');
    var croix = un('.feuille-filtres__tete svg');
    var maintenant = new Date();
    var mois = maintenant.toISOString().slice(0, 7);
    var annee = mois.slice(0, 4);

    // « coeur » trouve « cœur », « eclat » trouve « Éclat »
    function sansAccents(mot) {
      return mot.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().replace(/œ/g, 'oe').replace(/æ/g, 'ae');
    }
    function valeurs(carte, nom) { var valeur = carte.getAttribute('data-' + nom); return valeur ? valeur.split('|') : []; }
    var polices = tous('.carte-police', liste).map(function (carte) {
      return {
        carte: carte,
        nom: carte.getAttribute('data-nom'),
        mots: sansAccents(carte.getAttribute('data-mots')),
        usage: valeurs(carte, 'usages'),
        style: valeurs(carte, 'styles'),
        langue: valeurs(carte, 'langues'),
        fonction: valeurs(carte, 'fonctions'),
        graisses: Number(carte.getAttribute('data-graisses')),
        statut: carte.getAttribute('data-statut'),
        date: carte.getAttribute('data-date'),
        min: Number(carte.getAttribute('data-taille-min')),
        max: Number(carte.getAttribute('data-taille-max')),
        nettes: valeurs(carte, 'tailles-nettes').map(Number),
        exemple: un('[data-exemple-catalogue]', carte),
        note: un('[data-note]', carte)
      };
    });

    // La police remplit-elle ce critère pour cette valeur ?
    var TESTS = {
      q: function (police, valeur) {
        return sansAccents(valeur).split(/\s+/).every(function (mot) { return police.mots.indexOf(mot) !== -1; });
      },
      usage: function (police, valeur) { return police.usage.indexOf(valeur) !== -1; },
      style: function (police, valeur) { return police.style.indexOf(valeur) !== -1; },
      langue: function (police, valeur) { return police.langue.indexOf(valeur) !== -1; },
      fonction: function (police, valeur) { return police.fonction.indexOf(valeur) !== -1; },
      lecture: function (police) { return police.min <= 16; },
      graisses: function (police, valeur) { return valeur === 'une' ? police.graisses === 1 : police.graisses > 1; },
      statut: function (police, valeur) { return (police.statut === 'stable') === (valeur === 'stable'); },
      maj: function (police, valeur) { return police.date.slice(0, valeur === 'mois' ? 7 : 4) === (valeur === 'mois' ? mois : annee); }
    };
    function convient(police, etat) {
      return CRITERES_SIMPLES.every(function (cle) { return !etat[cle] || TESTS[cle](police, etat[cle]); }) &&
        CRITERES_LISTES.every(function (cle) { return etat[cle].every(function (valeur) { return TESTS[cle](police, valeur); }); });
    }

    // État : lu dans l'adresse, réécrit à chaque changement (le lien garde la recherche)
    var etat = { vue: '', tri: 'recent' };
    var affichees = PAR_PAGE;
    function viderCriteres(cles) {
      cles.forEach(function (cle) { etat[cle] = CRITERES_LISTES.indexOf(cle) !== -1 ? [] : ''; });
    }
    viderCriteres(CRITERES_SIMPLES.concat(CRITERES_LISTES));
    var parametres = new URLSearchParams(location.search);
    CRITERES_SIMPLES.concat(['vue', 'tri']).forEach(function (cle) { if (parametres.get(cle)) etat[cle] = parametres.get(cle).trim(); });
    CRITERES_LISTES.forEach(function (cle) { if (parametres.get(cle)) etat[cle] = parametres.get(cle).split(','); });
    function ecrireAdresse() {
      var nouveaux = new URLSearchParams();
      CRITERES_SIMPLES.forEach(function (cle) { if (etat[cle]) nouveaux.set(cle, etat[cle]); });
      CRITERES_LISTES.forEach(function (cle) { if (etat[cle].length) nouveaux.set(cle, etat[cle].join(',')); });
      if (etat.vue) nouveaux.set('vue', etat.vue);
      if (etat.tri !== 'recent') nouveaux.set('tri', etat.tri);
      var chaine = nouveaux.toString();
      history.replaceState(null, '', location.pathname + (chaine ? '?' + chaine : '') + location.hash);
    }

    // Compteurs : polices du catalogue qui remplissent ce seul critère. Un choix qui ne retient aucune police,
    // ou qui les retient toutes, ne sert à rien : il est masqué (sauf s'il est déjà actif), et son groupe avec lui.
    var choix = tous('[data-choix]');
    var cases = tous('[data-case]');
    function compter(cle, valeur) {
      return polices.filter(function (police) { return TESTS[cle](police, valeur); }).length;
    }
    choix.forEach(function (bouton) {
      var cle = bouton.getAttribute('data-choix');
      var valeur = bouton.getAttribute('data-valeur');
      if (cle === 'vue') return;
      var nombre = valeur ? compter(cle, valeur) : polices.length;
      un('[data-compte]', bouton).textContent = nombre;
      bouton.hidden = !!valeur && (nombre === 0 || nombre === polices.length) && etat[cle] !== valeur;
    });
    cases.forEach(function (caseFiltre) {
      var cle = caseFiltre.getAttribute('data-case');
      var nombre = compter(cle, caseFiltre.value);
      un('[data-compte]', caseFiltre.closest('label')).textContent = nombre;
      caseFiltre.closest('label').hidden = (nombre === 0 || nombre === polices.length) && etat[cle].indexOf(caseFiltre.value) === -1;
    });
    tous('[data-groupe]', feuille).forEach(function (groupe) {
      var utiles = tous('[data-valeur]:not([data-valeur=""]), [data-case]', groupe).filter(function (element) {
        return !(element.closest('label') || element).hidden;
      });
      groupe.hidden = !utiles.length;
    });
    boutonFiltres.hidden = tous('[data-groupe]', feuille).every(function (groupe) { return groupe.hidden; });
    // Beaucoup de langues : les cinq premières, puis « Voir les N autres langues »
    var langues = tous('[data-case="langue"]', feuille).map(function (caseFiltre) { return caseFiltre.closest('label'); })
      .filter(function (label) { return !label.hidden; });
    var autresLangues = un('[data-autres-langues]', feuille);
    if (langues.length > 6) {
      var cachees = langues.slice(5).filter(function (label) { return !un('input', label).checked && etat.langue.indexOf(un('input', label).value) === -1; });
      cachees.forEach(function (label) { label.hidden = true; });
      autresLangues.textContent = 'Voir les ' + cachees.length + ' autres langues';
      autresLangues.hidden = !cachees.length;
      autresLangues.addEventListener('click', function () {
        cachees.forEach(function (label) { label.hidden = false; });
        autresLangues.hidden = true;
        un('input', cachees[0]).focus();
      });
    }

    function libelleDe(element) {
      var texteLibelle = element.matches('[data-choix]') ? un('.bouton-choix__libelle', element) : un('.case-filtre__texte > span', element.closest('label'));
      return texteLibelle.textContent;
    }
    function legendeDe(element) { return un('legend', element.closest('fieldset')).textContent.trim(); }
    function pluriel(nombre, mot) { return nombre + ' ' + mot + (nombre > 1 ? 's' : ''); }

    function afficher(annoncerResultat) {
      var trouvees = polices.filter(function (police) { return convient(police, etat); });
      trouvees.sort(etat.tri === 'nom'
        ? function (a, b) { return a.nom.localeCompare(b.nom, 'fr'); }
        : function (a, b) { return b.date.localeCompare(a.date) || a.nom.localeCompare(b.nom, 'fr'); });
      polices.forEach(function (police) { police.carte.hidden = true; });
      trouvees.forEach(function (police, rang) {
        liste.appendChild(police.carte);
        police.carte.hidden = rang >= affichees;
      });
      liste.classList.toggle('catalogue__liste--cartes', etat.vue === 'cartes');

      // Commandes : reflètent l'état
      recherche.value = etat.q;
      tri.value = etat.tri;
      choix.forEach(function (bouton) {
        var cle = bouton.getAttribute('data-choix');
        bouton.setAttribute('aria-pressed', etat[cle] === bouton.getAttribute('data-valeur') ? 'true' : 'false');
      });
      cases.forEach(function (caseFiltre) { caseFiltre.checked = etat[caseFiltre.getAttribute('data-case')].indexOf(caseFiltre.value) !== -1; });

      // Filtres actifs : un bouton par filtre, qui le retire
      var puces = un('[data-puces]', actifs);
      puces.textContent = '';
      function puce(libelle, retirer) {
        var bouton = document.createElement('button');
        bouton.type = 'button';
        bouton.className = 'gr-btn puce-active';
        bouton.setAttribute('aria-label', 'Retirer le filtre ' + libelle);
        bouton.appendChild(document.createElement('span')).textContent = libelle;
        bouton.appendChild(croix.cloneNode(true));
        bouton.addEventListener('click', function () {
          retirer();
          changer();
          (un('.puce-active', puces) || recherche).focus();
        });
        puces.appendChild(bouton);
      }
      if (etat.q) puce('« ' + etat.q + ' »', function () { etat.q = ''; });
      choix.forEach(function (bouton) {
        var cle = bouton.getAttribute('data-choix');
        var valeur = bouton.getAttribute('data-valeur');
        if (cle === 'vue' || !valeur || etat[cle] !== valeur) return;
        var dansFeuille = feuille.contains(bouton);
        puce((dansFeuille ? legendeDe(bouton) + ' : ' : '') + libelleDe(bouton), function () { etat[cle] = ''; });
      });
      cases.forEach(function (caseFiltre) {
        if (!caseFiltre.checked) return;
        var cle = caseFiltre.getAttribute('data-case');
        puce(libelleDe(caseFiltre), function () {
          etat[cle] = etat[cle].filter(function (valeur) { return valeur !== caseFiltre.value; });
        });
      });
      var nombreFiltres = puces.children.length;
      actifs.hidden = !nombreFiltres;
      var nombreFeuille = CRITERES_FEUILLE.reduce(function (total, cle) {
        return total + (Array.isArray(etat[cle]) ? etat[cle].length : etat[cle] ? 1 : 0);
      }, 0);
      un('[data-libelle-filtres]', boutonFiltres).textContent = 'Plus de filtres' + (nombreFeuille ? ' (' + nombreFeuille + ')' : '');
      un('[data-libelle-appliquer]', feuille).textContent = trouvees.length
        ? 'Afficher ' + pluriel(trouvees.length, 'police') : 'Aucune police';

      // Titre, état vide, « Afficher plus »
      titre.textContent = nombreFiltres
        ? pluriel(trouvees.length, 'police') + ' trouvée' + (trouvees.length > 1 ? 's' : '')
        : pluriel(trouvees.length, 'police');
      aucune.hidden = trouvees.length > 0;
      un('[data-aucune-titre]', aucune).textContent = etat.q
        ? 'Aucune police pour « ' + etat.q + ' ».' : 'Aucune police ne correspond à ces filtres.';
      var visibles = Math.min(affichees, trouvees.length);
      plus.hidden = visibles >= trouvees.length;
      un('[data-progression]', plus).textContent = visibles + ' sur ' + pluriel(trouvees.length, 'police') + ' affichées';
      un('[data-barre]', plus).style.width = (trouvees.length ? 100 * visibles / trouvees.length : 0) + '%';
      un('[data-libelle-plus]', plus).textContent = 'Afficher ' + pluriel(Math.min(PAR_PAGE, trouvees.length - visibles), 'police') + ' de plus';

      if (annoncerResultat) annoncer(titre.textContent + '.');
    }
    function changer() {
      affichees = PAR_PAGE;
      ecrireAdresse();
      afficher(true);
    }

    // Recherche : le résultat suit la frappe, l'annonce attend une courte pause
    var attente = null;
    recherche.addEventListener('input', function () {
      etat.q = recherche.value.trim();
      affichees = PAR_PAGE;
      ecrireAdresse();
      afficher(false);
      clearTimeout(attente);
      attente = setTimeout(function () { annoncer(titre.textContent + '.'); }, 700);
    });
    tri.addEventListener('change', function () { etat.tri = tri.value; changer(); });
    choix.forEach(function (bouton) {
      bouton.addEventListener('click', function () {
        etat[bouton.getAttribute('data-choix')] = bouton.getAttribute('data-valeur');
        changer();
      });
    });
    cases.forEach(function (caseFiltre) {
      caseFiltre.addEventListener('change', function () {
        var cle = caseFiltre.getAttribute('data-case');
        etat[cle] = cases.filter(function (autre) { return autre.getAttribute('data-case') === cle && autre.checked; })
          .map(function (autre) { return autre.value; });
        changer();
      });
    });
    tous('[data-tout-effacer]').forEach(function (bouton) {
      bouton.addEventListener('click', function () {
        viderCriteres(CRITERES_SIMPLES.concat(CRITERES_LISTES));
        changer();
        recherche.focus();
      });
    });
    un('[data-effacer-feuille]', feuille).addEventListener('click', function () { viderCriteres(CRITERES_FEUILLE); changer(); });
    un('[data-afficher-plus]', plus).addEventListener('click', function () {
      var premiere = affichees;
      affichees += PAR_PAGE;
      afficher(false);
      var suivante = tous('.carte-police', liste)[premiere];
      if (suivante) un('.carte-police__nom a', suivante).focus();
    });

    // Feuille « Plus de filtres » : fenêtre modale, fermée par Échap, la croix, le bouton du bas ou un clic à côté
    boutonFiltres.addEventListener('click', function () {
      feuille.showModal();
      boutonFiltres.setAttribute('aria-expanded', 'true');
    });
    feuille.addEventListener('close', function () {
      boutonFiltres.setAttribute('aria-expanded', 'false');
      boutonFiltres.focus();
    });
    feuille.addEventListener('click', function (evenement) { if (evenement.target === feuille) feuille.close(); });
    var aide = un('[data-aide-filtre]', feuille);
    aide.addEventListener('click', function () {
      var ouverte = aide.getAttribute('aria-expanded') !== 'true';
      aide.setAttribute('aria-expanded', ouverte ? 'true' : 'false');
      document.getElementById(aide.getAttribute('aria-controls')).hidden = !ouverte;
    });

    // Essai : un texte et une taille pour toutes les polices, chacune bornée à ses tailles conseillées
    function borner(valeur, min, max) { return Math.min(max, Math.max(min, Math.round(Number(valeur) || min))); }
    function essayer() {
      var taille = borner(champTaille.value, Number(curseur.min), Number(curseur.max));
      polices.forEach(function (police) {
        var affichee = borner(taille, police.min, police.max);
        police.exemple.textContent = texte.value.trim() || police.exemple.getAttribute('data-exemple-catalogue');
        police.exemple.style.fontSize = affichee + 'px';
        police.note.textContent = affichee !== taille
          ? 'Affichée à ' + affichee + ' px : ' + (affichee > taille ? 'taille minimale' : 'taille maximale') + ' de cette police'
          : police.nom + ' · ' + affichee + ' px' + (police.nettes.indexOf(affichee) !== -1 ? ', pixels nets' : '');
        police.note.hidden = false;
      });
    }
    // Écran étroit : une taille plus petite, pour garder des mots entiers
    if (window.matchMedia('(max-width: 40rem)').matches) champTaille.value = curseur.value = 40;
    curseur.addEventListener('input', function () { champTaille.value = curseur.value; essayer(); });
    champTaille.addEventListener('input', function () { curseur.value = champTaille.value; essayer(); });
    champTaille.addEventListener('change', function () {
      champTaille.value = curseur.value = borner(champTaille.value, Number(curseur.min), Number(curseur.max));
      essayer();
    });
    texte.addEventListener('input', essayer);

    tous('[data-outils]').forEach(function (outils) { outils.hidden = false; });
    essayer();
    afficher(false);
  })();

  // ---------- Page des versions : groupes repliables, recherche et type de changement ----------
  (function versions() {
    var filtre = un('[data-filtre-versions]');
    if (!filtre) return;
    var recherche = un('[data-recherche-versions]', filtre);
    var types = tous('[data-type-changement]', filtre);
    var etat = un('[data-etat-versions]', filtre);
    var aucun = un('[data-aucun-changement]');
    var groupes = tous('[data-groupe-versions]');
    var messageInitial = etat.textContent;
    var type = '';

    function ouvrir(groupe, ouvert) {
      var bouton = un('.groupe-versions__bouton', groupe);
      bouton.setAttribute('aria-expanded', ouvert ? 'true' : 'false');
      document.getElementById(bouton.getAttribute('aria-controls')).hidden = !ouvert;
    }
    groupes.forEach(function (groupe) {
      var bouton = un('.groupe-versions__bouton', groupe);
      bouton.addEventListener('click', function () { ouvrir(groupe, bouton.getAttribute('aria-expanded') !== 'true'); });
      // Les versions de travail sont repliées au départ
      if (groupe.hasAttribute('data-replie')) ouvrir(groupe, false);
    });

    // Compteurs : versions qui ont au moins un changement de ce type
    var toutes = tous('[data-version]');
    types.forEach(function (bouton) {
      var valeur = bouton.getAttribute('data-type-changement');
      un('[data-compte]', bouton).textContent = valeur
        ? toutes.filter(function (version) { return un('[data-section="' + valeur + '"]', version); }).length
        : toutes.length;
    });

    function sansAccents(mot) { return mot.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase(); }
    function filtrer() {
      var mots = sansAccents(recherche.value.trim()).split(/\s+/).filter(Boolean);
      var actif = mots.length > 0 || type !== '';
      var trouvees = 0;
      groupes.forEach(function (groupe) {
        var dansGroupe = 0;
        tous('[data-version]', groupe).forEach(function (version) {
          var entreesVisibles = 0;
          tous('[data-section]', version).forEach(function (section) {
            var bonType = !type || section.getAttribute('data-section') === type;
            var visibles = 0;
            tous('li', section).forEach(function (entree) {
              var texteEntree = sansAccents(entree.textContent);
              var garde = bonType && mots.every(function (mot) { return texteEntree.indexOf(mot) !== -1; });
              entree.hidden = !garde;
              if (garde) visibles += 1;
            });
            section.hidden = !visibles;
            section.previousElementSibling.hidden = !visibles;
            entreesVisibles += visibles;
          });
          version.hidden = !entreesVisibles;
          if (entreesVisibles) dansGroupe += 1;
        });
        groupe.hidden = !dansGroupe;
        // Un filtre ouvre les groupes qui ont des résultats ; sans filtre, chacun revient à son état de départ
        ouvrir(groupe, actif ? dansGroupe > 0 : !groupe.hasAttribute('data-replie'));
        trouvees += dansGroupe;
      });
      aucun.hidden = trouvees > 0;
      etat.textContent = actif
        ? (trouvees > 1 ? trouvees + ' versions correspondent.' : trouvees + ' version correspond.')
        : messageInitial;
    }
    recherche.addEventListener('input', filtrer);
    types.forEach(function (bouton) {
      bouton.addEventListener('click', function () {
        type = bouton.getAttribute('data-type-changement');
        types.forEach(function (autre) { autre.setAttribute('aria-pressed', autre === bouton ? 'true' : 'false'); });
        filtrer();
      });
    });
    un('[data-effacer-versions]', aucun).addEventListener('click', function () {
      recherche.value = '';
      types[0].click();
      recherche.focus();
    });
    filtre.hidden = false;
  })();

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
    // Champ vide : l'essai montre le texte du spécimen (celui du texte d'exemple)
    var texteParDefaut = sortie.textContent;

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
      un('[data-compte-glyphes]').textContent = PREMIERS + ' sur ' + cellules.length + ' affichés';
      plus.hidden = false;
      plus.addEventListener('click', function () {
        cellules.forEach(function (cellule) { cellule.hidden = false; });
        visibles = cellules.length;
        plus.hidden = true;
        un('[data-compte-glyphes]').textContent = cellules.length + ' glyphes';
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
