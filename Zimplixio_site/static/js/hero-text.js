/* Word-by-word H1 reveal */
document.addEventListener('DOMContentLoaded', function () {
  var el = document.querySelector('[data-word-reveal]');
  if (!el) return;

  var html = el.innerHTML;
  // Split on spaces while preserving <br> tags
  var parts = html.split(/(<br[^>]*>|\s+)/);
  var delay = 0;
  var result = '';

  parts.forEach(function (part) {
    if (!part || /^\s+$/.test(part)) {
      result += ' ';
    } else if (/^<br/i.test(part)) {
      result += part;
    } else {
      result += '<span class="word-reveal-item" style="--delay:' + delay + 'ms">' + part + '</span>';
      delay += 80;
    }
  });

  el.innerHTML = result;
  el.removeAttribute('data-aos');
});
