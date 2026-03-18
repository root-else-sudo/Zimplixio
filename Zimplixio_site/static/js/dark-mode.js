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
  }

  document.addEventListener('DOMContentLoaded', function () {
    var isDark = document.documentElement.classList.contains('dark');
    updateIcons(isDark);

    document.querySelectorAll('.dark-mode-toggle').forEach(function (btn) {
      btn.addEventListener('click', toggleTheme);
    });
  });
})();
