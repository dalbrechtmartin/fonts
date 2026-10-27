// Réglages appliqués avant le premier rendu (thème, taille du texte, animations, police lisible) : à charger dans <head>
(function () {
  var reglages = {};
  try { reglages = JSON.parse(localStorage.getItem('reglages')) || {}; } catch (erreur) {}
  var racine = document.documentElement;
  var sombre = reglages.theme ? reglages.theme === 'dark' : window.matchMedia('(prefers-color-scheme: dark)').matches;
  racine.setAttribute('data-theme', sombre ? 'dark' : 'light');
  if (reglages.text && reglages.text !== 'm') racine.setAttribute('data-text', reglages.text);
  if (reglages.motion) racine.setAttribute('data-motion', reglages.motion);
  if (reglages.font) racine.setAttribute('data-font', 'lisible');
})();
