document.addEventListener('DOMContentLoaded', function () {
  var iframe = document.getElementById('demo-iframe');
  var overlay = document.getElementById('demo-loading');
  var buttons = document.querySelectorAll('.demo-toggle');

  if (!iframe) return;

  iframe.addEventListener('load', function () {
    if (overlay) overlay.classList.add('hidden');
  });

  buttons.forEach(function (btn) {
    btn.addEventListener('click', function () {
      var url = btn.dataset.url;
      if (!url || iframe.src === url) return;

      if (overlay) overlay.classList.remove('hidden');
      iframe.src = url;

      buttons.forEach(function (b) {
        b.classList.remove('bg-indigo-600', 'text-white', 'shadow-lg', 'shadow-indigo-600/20');
        b.classList.add('bg-gray-100', 'text-gray-700');
      });
      btn.classList.remove('bg-gray-100', 'text-gray-700');
      btn.classList.add('bg-indigo-600', 'text-white', 'shadow-lg', 'shadow-indigo-600/20');
    });
  });
});
