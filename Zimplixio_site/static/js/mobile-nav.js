document.addEventListener('DOMContentLoaded', function () {
  const btn = document.getElementById('mobile-menu-btn');
  const menu = document.getElementById('mobile-menu');
  const hamburgerIcon = document.getElementById('hamburger-icon');
  const closeIcon = document.getElementById('close-icon');

  if (!btn || !menu) return;

  btn.addEventListener('click', function () {
    const isOpen = !menu.classList.contains('hidden');
    menu.classList.toggle('hidden');
    hamburgerIcon.classList.toggle('hidden', !isOpen);
    closeIcon.classList.toggle('hidden', isOpen);
    btn.setAttribute('aria-expanded', !isOpen);
  });
});
