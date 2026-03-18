document.addEventListener('DOMContentLoaded', function () {
  // Animate the vertical timeline line on scroll
  var timelineLine = document.querySelector('.timeline-line');
  if (timelineLine) {
    timelineLine.classList.add('timeline-grow');
  }

  document.querySelectorAll('.timeline-toggle').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var item = btn.closest('.timeline-item');
      var details = item.querySelector('.timeline-details');
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
        n.classList.remove('timeline-node--active');
      });

      if (!isOpen) {
        details.classList.remove('hidden');
        details.style.maxHeight = details.scrollHeight + 'px';
        chevron.style.transform = 'rotate(180deg)';
        // Apply glow to the node in this item
        item.querySelector('.timeline-node').classList.add('timeline-node--active');
      }
    });
  });
});
