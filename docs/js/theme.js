// Handles the manual light/dark toggle button.
// Initial theme detection (system preference + saved override) happens
// via the inline blocking snippet in each page's <head>, to avoid a
// flash of the wrong theme before this file loads.
(function () {
  var btn = document.getElementById('theme-toggle');
  if (!btn) return;

  btn.addEventListener('click', function () {
    var root = document.documentElement;
    var current = root.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
    var next = current === 'dark' ? 'light' : 'dark';

    root.setAttribute('data-theme', next);

    try {
      localStorage.setItem('theme', next);
    } catch (e) {
      // localStorage unavailable (private mode, etc.) — toggle still
      // works for the current page view, just won't persist.
    }
  });
})();
