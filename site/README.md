# sitesmyth.com

Astro + Solid. One codebase, four design directions picked by `VARIANT` (v1..v4).
Content lives in `src/data/site.ts`; each theme in `src/themes/<variant>/` supplies fonts, CSS, header, footer, and the home hero.

```
npm install
VARIANT=v2 npm run dev          # one direction locally
npm run build:all               # dist/v1..v4
node scripts/check.mjs          # overflow / h1 / console check (needs the four preview servers)
node scripts/deploy.mjs v1 v2   # deploy to v1.sitesmyth.com, v2.sitesmyth.com
PROD=1 VARIANT=v1 npx astro build && node scripts/deploy.mjs prod   # sitesmyth.com
```

Previews are `noindex`. Production is v1 (Living Blueprint), built with `PROD=1` into `dist/prod`
and served by the `sitesmyth-site` Worker on `sitesmyth.com/*` and `www.sitesmyth.com/*` (www
redirects to the apex). The old R2 `sitesmyth-worker` keeps the wildcard routes for demo subdomains.

`worker/index.js` serves the assets and handles `POST /api/contact`. Leads are stored in the
`sitesmyth-leads` KV namespace. Email alerts turn on when the Worker has `RESEND_API_KEY` and
`NOTIFY_TO` secrets.

Portfolio screenshots: `node scripts/shoot.mjs`, then convert to webp in `public/work/`.
