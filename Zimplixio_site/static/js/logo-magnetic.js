/* Zimplixio — Magnetic element effect */
(function () {
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.logo-magnetic').forEach(function (el) {
      var targetX = 0, targetY = 0;
      var currentX = 0, currentY = 0;
      var rafId = null;
      var active = false;
      var STRENGTH = 0.28;
      var EASE = 0.1;

      function tick() {
        currentX += (targetX - currentX) * EASE;
        currentY += (targetY - currentY) * EASE;

        el.style.transform = 'translate(' + currentX.toFixed(2) + 'px, ' + currentY.toFixed(2) + 'px)';

        if (!active && Math.abs(targetX - currentX) < 0.05 && Math.abs(targetY - currentY) < 0.05) {
          el.style.transform = '';
          rafId = null;
          return;
        }

        rafId = requestAnimationFrame(tick);
      }

      function start() {
        if (!rafId) rafId = requestAnimationFrame(tick);
      }

      el.addEventListener('mousemove', function (e) {
        var rect = el.getBoundingClientRect();
        targetX = (e.clientX - (rect.left + rect.width  / 2)) * STRENGTH;
        targetY = (e.clientY - (rect.top  + rect.height / 2)) * STRENGTH;
        active = true;
        start();
      });

      el.addEventListener('mouseleave', function () {
        active = false;
        targetX = 0;
        targetY = 0;
        start();
      });
    });
  });
})();
