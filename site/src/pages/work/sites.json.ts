import type { APIRoute } from 'astro';
import { WORK } from '../../data/site';

// The availability cron reads this to learn which sites to check, so src/data/work/
// stays the only place a portfolio site is listed.
export const GET: APIRoute = () =>
  new Response(JSON.stringify(WORK.map((w) => ({ slug: w.slug, url: w.url }))), {
    headers: { 'content-type': 'application/json' },
  });
