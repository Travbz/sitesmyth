// Serves the built site and accepts contact form posts at /api/contact.
// Every lead is stored in KV. If RESEND_API_KEY and NOTIFY_TO are set, it is also emailed.

const json = (body, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { 'content-type': 'application/json' } });

const LIMITS = { name: 200, business: 200, email: 254, phone: 50, site: 300, need: 100, message: 5000 };

async function notify(env, lead) {
  const lines = Object.entries(lead).map(([k, v]) => `${k}: ${v}`).join('\n');
  await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: { authorization: `Bearer ${env.RESEND_API_KEY}`, 'content-type': 'application/json' },
    body: JSON.stringify({
      from: env.NOTIFY_FROM || 'SiteSmyth <leads@sitesmyth.com>',
      to: env.NOTIFY_TO,
      reply_to: lead.email,
      subject: `New website lead: ${lead.business}`,
      text: lines,
    }),
  });
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    // One canonical host: www goes to the apex.
    if (url.hostname.startsWith('www.')) {
      url.hostname = url.hostname.slice(4);
      return Response.redirect(url.toString(), 301);
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
