/* Eviulon Library: optional human navigation convenience.
 * Normal PHP links, page text, canonical URLs and crawler endpoints work without JS.
 */
(() => {
  'use strict';
  const KEY = 'eviulon:reader:pending:v1';
  const reader = document.querySelector('.reader-main .reading-surface');
  if (!reader) return;

  // Only ordinary reader Previous / Next links participate. Never intercept links.
  document.querySelectorAll('.reader-main .nav-mode a.nav-link[href]').forEach(link => {
    link.addEventListener('click', event => {
      // Let modified clicks (open new tab/window) behave natively.
      if (event.defaultPrevented || event.button !== 0 ||
          event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      const target = new URL(link.href, location.href);
      if (target.origin !== location.origin) return;
      try {
        sessionStorage.setItem(KEY, JSON.stringify({
          path: target.pathname,
          y: Math.round(-reader.getBoundingClientRect().top),
          saved: Date.now()
        }));
      } catch (_) { /* Navigation stays available without storage. */ }
    });
  });

  let state;
  try {
    const raw = sessionStorage.getItem(KEY);
    if (!raw) return;
    state = JSON.parse(raw);
    // One-shot storage: no stale restoration on unrelated visits or browser Back.
    sessionStorage.removeItem(KEY);
  } catch (_) { return; }
  if (!state || state.path !== location.pathname || location.hash ||
      !Number.isFinite(state.y) || Math.abs(state.y) > 1000000 ||
      Date.now() - state.saved > 60000 || state.saved > Date.now() + 1000) return;

  // Offset relative to the top of the reading surface, robust to header changes.
  // Avoid the site's smooth-scroll rule during one-time position restoration.
  requestAnimationFrame(() => requestAnimationFrame(() => {
    const previous = document.documentElement.style.scrollBehavior;
    document.documentElement.style.scrollBehavior = 'auto';
    const top = reader.getBoundingClientRect().top + window.scrollY + state.y;
    window.scrollTo(0, Math.max(0, top));
    requestAnimationFrame(() => { document.documentElement.style.scrollBehavior = previous; });
  }));
})();
