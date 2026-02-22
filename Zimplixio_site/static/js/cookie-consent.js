document.addEventListener('DOMContentLoaded', function () {
  const banner = document.getElementById('cookie-banner');
  const acceptBtn = document.getElementById('cookie-accept');
  const dismissBtn = document.getElementById('cookie-dismiss');

  if (!banner) return;

  // Show banner if no consent recorded
  if (!localStorage.getItem('cookie_consent')) {
    banner.classList.remove('hidden');
  }

  function hideBanner(consent) {
    localStorage.setItem('cookie_consent', consent);
    banner.classList.add('hidden');
  }

  if (acceptBtn) acceptBtn.addEventListener('click', function () { hideBanner('accepted'); });
  if (dismissBtn) dismissBtn.addEventListener('click', function () { hideBanner('dismissed'); });
});
