(function () {
  'use strict';

  var outer = null;
  var track, panels, dots, counter, progressBar;
  var totalPanels = 0;
  var currentPanel = -1;
  var outerTop = 0;
  var scrollDistance = 0;
  var rafPending = false;

  // Snap-after-pause state
  var snapTimeout = null;
  var isSnapping  = false;

  function setHeight() {
    outer.style.height = (totalPanels * 70) + 'vh';
  }

  function cacheMetrics() {
    outerTop       = outer.getBoundingClientRect().top + window.pageYOffset;
    scrollDistance = outer.offsetHeight - window.innerHeight;
  }

  function getProgress() {
    return Math.max(0, Math.min(1, (window.pageYOffset - outerTop) / scrollDistance));
  }

  // Scroll position that perfectly centres panel i
  function panelScrollTarget(index) {
    return outerTop + (index / (totalPanels - 1)) * scrollDistance;
  }

  function updateUI(index) {
    currentPanel = index;
    counter.textContent = String(index + 1).padStart(2, '0');
    dots.forEach(function (d, i) {
      d.classList.toggle('svc-dot-active', i === index);
    });
    window.dispatchEvent(new CustomEvent('svcPanelChange', { detail: { index: index } }));
  }

  function animatePanelIn(panel) {
    var els = panel.querySelectorAll(
      '.svc-panel-num, .svc-panel-title, .svc-panel-desc, .svc-ghost-num'
    );
    els.forEach(function (el) {
      el.classList.remove('svc-anim');
      void el.offsetWidth; // force reflow to retrigger CSS animation
      el.classList.add('svc-anim');
    });
  }

  function tick() {
    rafPending = false;
    var progress = getProgress();
    track.style.transform = 'translateX(' + (-progress * (totalPanels - 1) * window.innerWidth) + 'px)';
    progressBar.style.width = (progress * 100) + '%';
    var idx = Math.min(Math.floor(progress * totalPanels), totalPanels - 1);
    if (idx !== currentPanel) {
      updateUI(idx);
      animatePanelIn(panels[idx]);
    }
  }

  function snapToNearest() {
    var progress = getProgress();

    // Only snap when the user is inside the section
    if (progress <= 0 || progress >= 1) return;

    var exactPanel  = progress * (totalPanels - 1);
    var nearestPanel = Math.round(exactPanel);
    nearestPanel = Math.max(0, Math.min(totalPanels - 1, nearestPanel));

    // Skip if already sitting cleanly on a panel (within 2% of target)
    if (Math.abs(exactPanel - nearestPanel) < 0.02) return;

    isSnapping = true;
    window.scrollTo({ top: panelScrollTarget(nearestPanel), behavior: 'smooth' });

    // Release snap lock after smooth scroll completes (~600 ms)
    setTimeout(function () { isSnapping = false; }, 650);
  }

  function onScroll() {
    if (rafPending) return;
    rafPending = true;
    requestAnimationFrame(tick);

    // Reset debounce timer on every scroll event
    clearTimeout(snapTimeout);
    if (!isSnapping) {
      snapTimeout = setTimeout(snapToNearest, 220);
    }
  }

  function onResize() {
    if (window.innerWidth < 1024) return;
    setHeight();
    cacheMetrics();
    tick();
  }

  function goToPanel(index) {
    isSnapping = true;
    clearTimeout(snapTimeout);
    window.scrollTo({ top: panelScrollTarget(index), behavior: 'smooth' });
    setTimeout(function () { isSnapping = false; }, 650);
  }

  document.addEventListener('DOMContentLoaded', function () {
    if (window.innerWidth < 1024) return;

    outer = document.getElementById('servicesOuter');
    if (!outer) return;

    track       = document.getElementById('svcPanelsTrack');
    panels      = Array.prototype.slice.call(outer.querySelectorAll('.svc-panel'));
    dots        = Array.prototype.slice.call(outer.querySelectorAll('.svc-nav-dot'));
    counter     = document.getElementById('svcCounterCurrent');
    progressBar = document.getElementById('svcProgressBar');
    totalPanels = panels.length;

    setHeight();
    cacheMetrics();

    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', onResize, { passive: true });

    dots.forEach(function (dot, i) {
      dot.setAttribute('role', 'button');
      dot.setAttribute('tabindex', '0');
      dot.addEventListener('click', function () { goToPanel(i); });
      dot.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); goToPanel(i); }
      });
    });

    updateUI(0);
    animatePanelIn(panels[0]);
    tick();
  });
}());
