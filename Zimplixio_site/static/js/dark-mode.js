/* Zimplixio — Dark Mode Toggle */
(function () {
  function toggleTheme() {
    var isDark = document.documentElement.classList.toggle('dark');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
    updateIcons(isDark);
  }

  function updateIcons(isDark) {
    document.querySelectorAll('.dark-mode-sun').forEach(function (el) {
      el.classList.toggle('hidden', !isDark);
    });
    document.querySelectorAll('.dark-mode-moon').forEach(function (el) {
      el.classList.toggle('hidden', isDark);
    });
    document.querySelectorAll('.dark-mode-toggle').forEach(function (btn) {
      btn.setAttribute('aria-pressed', isDark ? 'true' : 'false');
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    var isDark = document.documentElement.classList.contains('dark');
    updateIcons(isDark);

    // Enable smooth transitions after first paint to prevent FOUC
    requestAnimationFrame(function () {
      document.body.classList.add('transitions-enabled');
    });

    document.querySelectorAll('.dark-mode-toggle').forEach(function (btn) {
      btn.addEventListener('click', toggleTheme);
    });
  });
})();
