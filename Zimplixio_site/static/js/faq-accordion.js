document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.faq-toggle').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var content = btn.nextElementSibling;
      var chevron = btn.querySelector('.faq-chevron');
      var isOpen = !content.classList.contains('hidden');

      // Close all others
      document.querySelectorAll('.faq-content').forEach(function (c) { c.classList.add('hidden'); });
      document.querySelectorAll('.faq-chevron').forEach(function (c) { c.style.transform = ''; });
      document.querySelectorAll('.faq-toggle').forEach(function (b) { b.setAttribute('aria-expanded', 'false'); });

      if (!isOpen) {
        content.classList.remove('hidden');
        chevron.style.transform = 'rotate(180deg)';
        btn.setAttribute('aria-expanded', 'true');
      }
    });
  });
});
