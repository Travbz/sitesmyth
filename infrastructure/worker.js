/**
 * Cloudflare Worker — serves sites from R2 based on subdomain.
 * Domain comes from the DOMAIN var in wrangler.toml ([vars]) / Terraform.
 * In service-worker format, [vars] and bindings are exposed as globals.
 * Route: *.<DOMAIN>/*
 * Root (<DOMAIN>, www.<DOMAIN>) → _marketing/
 * {slug}.<DOMAIN> → sites/{slug}/
 */

const MIME = {
  '.html': 'text/html',
  '.css': 'text/css',
  '.js': 'application/javascript',
  '.json': 'application/json',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.webp': 'image/webp',
  '.ico': 'image/x-icon',
  '.svg': 'image/svg+xml',
  '.woff': 'font/woff',
  '.woff2': 'font/woff2',
};

function getContentType(path) {
  const ext = path.replace(/.*\./, '.');
  return MIME[ext] || 'application/octet-stream';
}

addEventListener('fetch', (event) => {
  event.respondWith(handleRequest(event.request));
});

async function handleRequest(request) {
  const url = new URL(request.url);
  const hostname = url.hostname;

  // DOMAIN is injected via wrangler.toml [vars]; fall back to the apex if unset.
  const domain = typeof DOMAIN !== 'undefined' && DOMAIN ? DOMAIN : hostname;

  const isRoot = hostname === domain || hostname === `www.${domain}`;
  const subdomain = hostname.replace(`.${domain}`, '').replace(/^www\./, '');

  let prefix, path;
  if (isRoot || subdomain === 'www' || subdomain === '') {
    prefix = '_marketing';
  } else {
    prefix = `sites/${subdomain}`;
  }

  path = url.pathname === '/' ? '/index.html' : url.pathname;
  const key = `${prefix}${path}`;

  const object = await R2.get(key);
  if (!object) {
    return new Response('Site not found', { status: 404 });
  }

  const headers = new Headers();
  headers.set('Content-Type', getContentType(path));
  headers.set('Cache-Control', 'public, max-age=3600');

  return new Response(object.body, { headers });
}
