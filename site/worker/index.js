// Serves the built site, accepts contact form posts at /api/contact, and keeps the
// portfolio honest: an hourly cron checks every site in the portfolio and /api/work-status
// reports the ones that are down, so the pages can drop them.
// Every lead is stored in KV. If RESEND_API_KEY and NOTIFY_TO are set, it is also emailed.

const json = (body, status = 200, headers = {}) =>
  new Response(JSON.stringify(body), { status, headers: { 'content-type': 'application/json', ...headers } });

const LIMITS = { name: 200, business: 200, email: 254, phone: 50, site: 300, need: 100, message: 5000 };

// Availability checking. One KV doc holds the result of the last run for every site.
const STATUS_KEY = 'work-status';
const HIDE_AFTER = 2; // consecutive failed hourly checks before an entry comes off the portfolio
const PROBE_TIMEOUT = 15000;

async function send(env, subject, text, replyTo) {
  await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: { authorization: `Bearer ${env.RESEND_API_KEY}`, 'content-type': 'application/json' },
    body: JSON.stringify({
      from: env.NOTIFY_FROM || 'SiteSmyth <leads@sitesmyth.com>',
      to: env.NOTIFY_TO,
      ...(replyTo ? { reply_to: replyTo } : {}),
      subject,
      text,
    }),
  });
}

async function notify(env, lead) {
  const lines = Object.entries(lead).map(([k, v]) => `${k}: ${v}`).join('\n');
  await send(env, `New website lead: ${lead.business}`, lines, lead.email);
}

// Two tries, because one refused connection is usually a blip and not a dead site.
// Returns the HTTP status, or 0 when nothing answered at all.
async function probe(url) {
  let code = 0;
  for (let tries = 0; tries < 2; tries++) {
    try {
      const res = await fetch(url, {
        redirect: 'follow',
        headers: { 'user-agent': 'SiteSmythPortfolioCheck/1.0 (+https://sitesmyth.com/)' },
        signal: AbortSignal.timeout(PROBE_TIMEOUT),
      });
      await res.body?.cancel();
      code = res.status;
      if (code === 200) return code;
    } catch {
      code = 0;
    }
  }
  return code;
}

// The portfolio files in src/data/work/ are the only place a site is listed; the build
// turns them into /work/sites.json and this reads that. The host is ignored by the binding.
async function portfolioSites(env) {
  const res = await env.ASSETS.fetch(new Request('https://sitesmyth.com/work/sites.json'));
  if (!res.ok) throw new Error(`/work/sites.json returned ${res.status}`);
  return res.json();
}

async function checkPortfolio(env) {
  const sites = await portfolioSites(env);
  const before = (await env.STATUS.get(STATUS_KEY, 'json'))?.sites ?? {};
  const checkedAt = new Date().toISOString();
  const after = {};
  const changed = [];

  // All at once, so the run takes one slow site's time rather than the sum of them.
  const results = await Promise.all(sites.map(async ({ slug, url }) => [slug, url, await probe(url)]));

  for (const [slug, url, code] of results) {
    const ok = code === 200;
    const prev = before[slug] ?? {};
    const fails = ok ? 0 : (prev.fails ?? 0) + 1;
    after[slug] = { url, code, ok, fails, checkedAt, lastOkAt: ok ? checkedAt : prev.lastOkAt ?? null };
    const wasHidden = (prev.fails ?? 0) >= HIDE_AFTER;
    if (wasHidden !== fails >= HIDE_AFTER) changed.push({ slug, ...after[slug], hidden: fails >= HIDE_AFTER });
  }

  await env.STATUS.put(STATUS_KEY, JSON.stringify({ updated: checkedAt, sites: after }));
  return changed;
}

// NOTIFY_TO hears about a site dropping off the portfolio or coming back, so the list never
// shrinks quietly. Dropping off is also when the client needs a call.
async function alertChanged(env, changed) {
  const text = changed
    .map((c) =>
      c.hidden
        ? `OFF  ${c.url}\n     ${c.code ? `HTTP ${c.code}` : 'no response'}, failed ${c.fails} checks in a row.\n     Last reachable: ${c.lastOkAt ?? 'not since checks began'}.\n     It is now hidden on sitesmyth.com/work/.`
        : `BACK ${c.url}\n     HTTP 200 again. It is showing on sitesmyth.com/work/ again.`,
    )
    .join('\n\n');
  const off = changed.filter((c) => c.hidden).length;
  const subject = off
    ? `Portfolio: ${off} site${off > 1 ? 's' : ''} unreachable`
    : `Portfolio: ${changed.length} site${changed.length > 1 ? 's' : ''} back up`;
  await send(env, subject, text);
}

export default {
  async scheduled(event, env, ctx) {
    const changed = await checkPortfolio(env);
    if (changed.length && env.RESEND_API_KEY && env.NOTIFY_TO) ctx.waitUntil(alertChanged(env, changed));
  },

  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    // Which portfolio entries to drop. The five minute cache means a visitor reading two
    // pages costs one KV read, and a status change shows up on the next page view after that.
    // An empty list, including when KV has nothing yet, means show everything.
    if (url.pathname === '/api/work-status') {
      if (request.method !== 'GET') return json({ error: 'Use GET.' }, 405);
      const doc = await env.STATUS.get(STATUS_KEY, 'json');
      const sites = Object.entries(doc?.sites ?? {});
      const down = sites.filter(([, s]) => (s.fails ?? 0) >= HIDE_AFTER).map(([slug]) => slug);
      // Every site failing at once is a fault in the checker, not five dead clients.
      const sane = down.length < sites.length ? down : [];
      return json({ updated: doc?.updated ?? null, down: sane }, 200, { 'cache-control': 'public, max-age=300' });
    }

    if (url.pathname !== '/api/contact') return env.ASSETS.fetch(request);
    if (request.method !== 'POST') return json({ error: 'Use POST.' }, 405);

    let data;
    try {
      data = await request.json();
    } catch {
      return json({ error: 'Send the form as JSON.' }, 400);
    }
    // Bots fill the hidden field. Pretend it worked and drop it.
    if (data.company_site) return json({ ok: true });

    const lead = {};
    for (const [k, max] of Object.entries(LIMITS)) lead[k] = String(data[k] ?? '').trim().slice(0, max);
    if (!lead.name || !lead.business || !lead.message || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(lead.email)) {
      return json({ error: 'Name, business, a valid email, and a message are required.' }, 400);
    }
    lead.received = new Date().toISOString();
    lead.host = url.hostname;

    await env.LEADS.put(`lead:${lead.received}:${crypto.randomUUID().slice(0, 8)}`, JSON.stringify(lead));
    if (env.RESEND_API_KEY && env.NOTIFY_TO) ctx.waitUntil(notify(env, lead));
    return json({ ok: true });
  },
};
