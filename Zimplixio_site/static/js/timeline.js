document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.timeline-toggle').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var details = btn.closest('.timeline-item').querySelector('.timeline-details');
      var chevron = btn.querySelector('.timeline-chevron');
      var isOpen = !details.classList.contains('hidden');

      // Close all others
      document.querySelectorAll('.timeline-details').forEach(function (d) {
        d.classList.add('hidden');
        d.style.maxHeight = '0';
      });
      document.querySelectorAll('.timeline-chevron').forEach(function (c) {
        c.style.transform = '';
      });
      document.querySelectorAll('.timeline-node').forEach(function (n) {
        n.classList.remove('ring-4', 'ring-indigo-200');
      });

      if (!isOpen) {
        details.classList.remove('hidden');
        details.style.maxHeight = details.scrollHeight + 'px';
        chevron.style.transform = 'rotate(180deg)';
        btn.closest('.timeline-item').querySelector('.timeline-node').classList.add('ring-4', 'ring-indigo-200');
      }
    });
  });
});
