/**
 * SiteSmyth analytics — inject into generated sites
 * Tracks page views and CTA clicks for prospect proof ("X people viewed your site")
 * Uses Cloudflare Workers Analytics Engine or custom endpoint
 */
(function() {
  var slug = (document.currentScript && document.currentScript.dataset.slug) || (window.location.hostname.split('.')[0]);
  var payload = { slug: slug, t: Date.now(), path: location.pathname };
  // Send beacon (replace with your analytics endpoint)
  if (navigator.sendBeacon) {
    navigator.sendBeacon('https://sitesmyth.com/api/view?' + new URLSearchParams(payload), '');
  }
})();
