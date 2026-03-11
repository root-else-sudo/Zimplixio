document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.stage-toggle').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var card = btn.closest('.stage-card');
      var content = card.querySelector('.stage-content');
      var chevron = btn.querySelector('.stage-chevron');
      var isOpen = content.classList.contains('open');

      // Close all stages first
      document.querySelectorAll('.stage-content').forEach(function (c) {
        c.classList.remove('open');
        c.style.maxHeight = '0';
      });
      document.querySelectorAll('.stage-chevron').forEach(function (c) {
        c.classList.remove('rotated');
      });
      document.querySelectorAll('.stage-card').forEach(function (c) {
        c.classList.remove('ring-2', 'ring-indigo-200');
      });

      // If it wasn't open, open it
      if (!isOpen) {
        content.classList.add('open');
        content.style.maxHeight = content.scrollHeight + 'px';
        chevron.classList.add('rotated');
        card.classList.add('ring-2', 'ring-indigo-200');
      }
    });
  });
});
