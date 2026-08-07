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
    // Must match the track transform and panelScrollTarget(), both of which map
    // progress across (totalPanels - 1) gaps. Using totalPanels here instead made the
    // counter and dots disagree with the panel actually on screen, so a small scroll
    // snapped to a different panel than the one highlighted.
    var idx = Math.round(progress * (totalPanels - 1));
    idx = Math.max(0, Math.min(totalPanels - 1, idx));
    if (idx !== currentPanel) {
      updateUI(idx);
      animatePanelIn(panels[idx]);
    }
  }

  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Hold the snap lock until scrolling actually settles, rather than guessing a
  // duration. A fixed timer released mid-animation on long scrolls, letting a second
  // snap fire on top of the first.
  function scrollToAndLock(target) {
    isSnapping = true;
    window.scrollTo({ top: target, behavior: reduceMotion ? 'auto' : 'smooth' });

    var lastY = null, stillFrames = 0, started = Date.now();
    (function poll() {
      var y = window.pageYOffset;
      var arrived = Math.abs(y - target) < 2;
      var stalled = lastY !== null && Math.abs(y - lastY) < 0.5 && ++stillFrames > 3;
      if (arrived || stalled || Date.now() - started > 1500) {
        isSnapping = false;
        return;
      }
      lastY = y;
      requestAnimationFrame(poll);
    }());
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

    scrollToAndLock(panelScrollTarget(nearestPanel));
  }

  function onScroll() {
    if (rafPending) return;
    rafPending = true;
    requestAnimationFrame(tick);

    // Reset debounce timer on every scroll event. 220ms fired mid-gesture, since
    // trackpad momentum has natural micro-pauses; 450ms lets a scroll finish first.
    clearTimeout(snapTimeout);
    if (!isSnapping) {
      snapTimeout = setTimeout(snapToNearest, 450);
    }
  }

  function onResize() {
    if (window.innerWidth < 1024) return;
    setHeight();
    cacheMetrics();
    tick();
  }

  function goToPanel(index) {
    clearTimeout(snapTimeout);
    scrollToAndLock(panelScrollTarget(index));
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
