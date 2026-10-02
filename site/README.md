# sitesmyth.com

Astro + Solid. One codebase, four design directions picked by `VARIANT` (v1..v4).
Content lives in `src/data/site.ts`; each theme in `src/themes/<variant>/` supplies fonts, CSS, header, footer, and the home hero.

```
npm install
VARIANT=v2 npm run dev          # one direction locally
npm run build:all               # dist/v1..v4
node scripts/check.mjs          # overflow / h1 / console check (needs the four preview servers)
node scripts/deploy.mjs v1 v2   # deploy to v1.sitesmyth.com, v2.sitesmyth.com
```

Previews are `noindex`. Build with `PROD=1` for the indexable production site.

`worker/index.js` serves the assets and handles `POST /api/contact`. Leads are stored in the
`sitesmyth-leads` KV namespace. Email alerts turn on when the Worker has `RESEND_API_KEY` and
`NOTIFY_TO` secrets.

Portfolio screenshots: `node scripts/shoot.mjs`, then convert to webp in `public/work/`.
