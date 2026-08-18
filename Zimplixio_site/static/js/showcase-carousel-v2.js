(function () {
  var reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  var carousel = document.querySelector('.showcase-carousel');
  if (!carousel) return;

  var track = carousel.querySelector('.showcase-track');
  var viewport = carousel.querySelector('.showcase-viewport');
  var leftBtn = carousel.querySelector('.showcase-arrow-left');
  var rightBtn = carousel.querySelector('.showcase-arrow-right');

  if (!track || !viewport) return;

  var realSlides = Array.from(track.children);
  var totalReal = realSlides.length;
  if (totalReal === 0) return;

  var autoplayDelay = parseInt(carousel.dataset.autoplay, 10) || 5000;
  var isTransitioning = false;
  var current = 0;
  var visible = 3;
  var timer = null;
  var isStatic = false;

  function getVisible() {
    if (window.innerWidth < 768) return 1;
    if (window.innerWidth < 1024) return 2;
    return 3;
  }

  function getSlideWidthPercent() {
    return 100 / visible;
  }

  function clearClones() {
    track.querySelectorAll('[data-clone]').forEach(function (c) { c.remove(); });
  }

  // Build clones for infinite loop
  function setupClones() {
    clearClones();

    // Never clone more slides than exist. The loops below already cap themselves at
    // totalReal, so using `visible` here made `current` (set to cloneCount at the end)
    // point past the slides that were actually prepended: a filtered gallery with one
    // project translated the track clean off-screen and rendered a blank section, and
    // a two-project gallery opened on the wrong card.
    var cloneCount = Math.min(visible, totalReal);

    // Clone last N → prepend
    for (var i = totalReal - 1; i >= Math.max(0, totalReal - cloneCount); i--) {
      var clone = realSlides[i].cloneNode(true);
      clone.setAttribute('data-clone', 'true');
      clone.setAttribute('aria-hidden', 'true');
      // Remove links in clones to avoid duplicate navigation
      var links = clone.querySelectorAll('a');
      links.forEach(function (a) {
        a.addEventListener('click', function (e) { e.preventDefault(); });
      });
      track.insertBefore(clone, track.firstChild);
    }

    // Clone first N → append
    for (var j = 0; j < Math.min(cloneCount, totalReal); j++) {
      var clone2 = realSlides[j].cloneNode(true);
      clone2.setAttribute('data-clone', 'true');
      clone2.setAttribute('aria-hidden', 'true');
      var links2 = clone2.querySelectorAll('a');
      links2.forEach(function (a) {
        a.addEventListener('click', function (e) { e.preventDefault(); });
      });
      track.appendChild(clone2);
    }

    // Start at the first real slide (after prepended clones)
    current = cloneCount;
    positionTrack(false);
  }

  function positionTrack(animate) {
    var slideW = getSlideWidthPercent();
    var allSlides = track.children;
    var totalSlides = allSlides.length;

    // Set each slide width
    for (var i = 0; i < totalSlides; i++) {
      allSlides[i].style.flex = '0 0 ' + slideW + '%';
    }

    var offset = -(current * slideW);

    if (animate && !reducedMotion) {
      track.style.transition = 'transform 0.5s cubic-bezier(0.25, 1, 0.5, 1)';
    } else {
      track.style.transition = 'none';
    }

    track.style.transform = 'translateX(' + offset + '%)';
    updateCenter();
  }

  // A loop only means anything when a card is off-screen. Once every project already
  // fits, sliding just rotates duplicates through the visible slots — most obviously
  // with a single filtered result, which otherwise cycles the same card forever. Lay
  // them out statically instead: no clones, no transform, no autoplay, no arrows.
  function setupStatic() {
    clearClones();
    stopAutoplay();
    isStatic = true;
    current = 0;
    carousel.classList.add('showcase-carousel-static');
    track.style.transition = 'none';
    track.style.transform = 'none';
    realSlides.forEach(function (slide) {
      // Drop the inline width positionTrack() may have set, so the static width in
      // main.css applies. Slot widths are a carousel concern; a static row sizes its
      // cards to read deliberately rather than to divide the viewport.
      slide.style.flex = '';
      slide.classList.remove('is-center');
    });
  }

  // Chooses the layout for the current breakpoint. Re-run whenever `visible` changes,
  // since the same project count can be static on desktop and a real carousel on mobile.
  function render() {
    visible = getVisible();
    if (totalReal <= visible) {
      setupStatic();
    } else {
      isStatic = false;
      carousel.classList.remove('showcase-carousel-static');
      setupClones();
      startAutoplay();
    }
  }

  function goTo(index, animate) {
    if (isStatic) return;
    if (isTransitioning && animate) return;
    current = index;
    if (animate) isTransitioning = true;
    positionTrack(animate);
  }

  // After transition, check for clone boundary and jump
  track.addEventListener('transitionend', function () {
    if (isStatic) return;
    isTransitioning = false;
    var cloneCount = Math.min(visible, totalReal);

    if (current < cloneCount) {
      // We're in the prepended clones — jump to equivalent real slide
      current = current + totalReal;
      positionTrack(false);
    } else if (current >= totalReal + cloneCount) {
      // We're in the appended clones — jump to equivalent real slide
      current = current - totalReal;
      positionTrack(false);
    }
  });

  // Navigation arrows
  if (leftBtn) {
    leftBtn.addEventListener('click', function () {
      goTo(current - 1, true);
      restartAutoplay();
    });
  }
  if (rightBtn) {
    rightBtn.addEventListener('click', function () {
      goTo(current + 1, true);
      restartAutoplay();
    });
  }

  // Center card emphasis
  function updateCenter() {
    var allSlides = track.children;
    for (var i = 0; i < allSlides.length; i++) {
      allSlides[i].classList.remove('is-center');
    }
    // Center is the middle of the visible window
    var centerIndex = current + Math.floor(visible / 2);
    if (visible % 2 === 0) centerIndex = current; // for even, highlight first
    if (allSlides[centerIndex]) {
      allSlides[centerIndex].classList.add('is-center');
    }
  }

  // Auto-play
  function startAutoplay() {
    if (reducedMotion || isStatic) return;
    stopAutoplay();
    timer = setInterval(function () {
      goTo(current + 1, true);
    }, autoplayDelay);
  }

  function stopAutoplay() {
    if (timer) {
      clearInterval(timer);
      timer = null;
    }
  }

  function restartAutoplay() {
    stopAutoplay();
    startAutoplay();
  }

  carousel.addEventListener('mouseenter', stopAutoplay);
  carousel.addEventListener('mouseleave', startAutoplay);
  carousel.addEventListener('focusin', stopAutoplay);
  carousel.addEventListener('focusout', startAutoplay);

  // Keyboard navigation on arrows
  carousel.addEventListener('keydown', function (e) {
    if (e.key === 'ArrowLeft') {
      goTo(current - 1, true);
      restartAutoplay();
    } else if (e.key === 'ArrowRight') {
      goTo(current + 1, true);
      restartAutoplay();
    }
  });

  // Responsive: re-lay out on resize. Goes through render() rather than setupClones()
  // so a breakpoint change can also switch between static and carousel layouts.
  var resizeTimer;
  window.addEventListener('resize', function () {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(function () {
      if (getVisible() !== visible) render();
    }, 200);
  });

  // Initialize
  render();
})();
