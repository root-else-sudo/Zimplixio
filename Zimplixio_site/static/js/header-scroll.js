/* Header scroll elevation */
(function () {
  var header = document.querySelector('header');
  if (!header) return;

  function onScroll() {
    if (window.scrollY > 20) {
      header.classList.add('header-elevated');
    } else {
      header.classList.remove('header-elevated');
    }
  }

  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll(); // apply on load if already scrolled
})();
