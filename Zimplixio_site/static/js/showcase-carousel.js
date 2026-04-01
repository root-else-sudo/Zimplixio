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

  function getVisible() {
    if (window.innerWidth < 768) return 1;
    if (window.innerWidth < 1024) return 2;
    return 3;
  }

  function getSlideWidthPercent() {
    return 100 / visible;
  }

  // Build clones for infinite loop
  function setupClones() {
    // Remove existing clones
    track.querySelectorAll('[data-clone]').forEach(function (c) { c.remove(); });

    visible = getVisible();
    var cloneCount = visible;

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

  function goTo(index, animate) {
    if (isTransitioning && animate) return;
    current = index;
    if (animate) isTransitioning = true;
    positionTrack(animate);
  }

  // After transition, check for clone boundary and jump
  track.addEventListener('transitionend', function () {
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
    if (reducedMotion) return;
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

  // Responsive: rebuild clones on resize
  var resizeTimer;
  window.addEventListener('resize', function () {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(function () {
      var newVisible = getVisible();
      if (newVisible !== visible) {
        setupClones();
        startAutoplay();
      }
    }, 200);
  });

  // Initialize
  setupClones();
  startAutoplay();
})();
