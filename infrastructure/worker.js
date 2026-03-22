/**
 * Cloudflare Worker — serves sites from R2 based on subdomain
 * Route: *.sitesmyth.com/*
 * Root (sitesmyth.com, www.sitesmyth.com) → _marketing/
 * {slug}.sitesmyth.com → sites/{slug}/
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

  const isRoot = hostname === 'sitesmyth.com' || hostname === 'www.sitesmyth.com';
  const subdomain = hostname.replace('.sitesmyth.com', '').replace('www.', '');

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
