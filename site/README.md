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
and served by the `sitesmyth-site` Worker on `sitesmyth.com/*` and `www.sitesmyth.com/*` (www serves the
same site; every page's canonical tag points at the apex). The old R2 `sitesmyth-worker` keeps the wildcard routes for demo subdomains.

`worker/index.js` serves the assets and handles `POST /api/contact`. Leads are stored in the
`sitesmyth-leads` KV namespace. Email alerts turn on when the Worker has `RESEND_API_KEY` and
`NOTIFY_TO` secrets.

## Portfolio availability

A client can take their site down or let a domain lapse, which would leave a dead link and a
screenshot of nothing on the portfolio. The production Worker's cron checks for that every hour.

- It reads `/work/sites.json`, which the build generates from `src/data/work/*.json`, so adding a
  site to the portfolio is still the only thing you have to do.
- It requests each site, twice if the first try fails, and stores the result under the `work-status`
  key in the same KV namespace as the leads.
- An entry comes off the portfolio after **two** consecutive hourly checks that did not return 200,
  so a site has to be down for an hour or two, not for one bad minute.
- `GET /api/work-status` returns the slugs to drop. `WorkStatus.astro` calls it and removes those
  entries from `/work/` and from the service pages, along with any section left empty. Pages stay
  static assets, so visiting the site never touches a client's server and never waits on one.
- Nothing hides when the status is missing, the call fails, or every site reads as down at once.
  A listing that is an hour stale beats an empty portfolio.
- When an entry drops off or comes back, `NOTIFY_TO` gets an email naming the site and its last
  reachable time. The portfolio never shrinks quietly.

Entries carry no status field; availability is runtime state and lives only in KV, so
`scripts/add-site.mjs` needs no change and a new site shows up straight away rather than waiting
for its first check.

Known limit: the `CollectionPage` schema on `/work/` is built at build time, so a down site stays
in its `hasPart` list until the next deploy. Fixing that means rendering those pages in the Worker
instead of serving them as static assets.

To run a check by hand:

```
node scripts/deploy.mjs prod        # the cron is part of the prod Worker config
npx wrangler tail sitesmyth-site    # watch a scheduled run
```

Locally, `npx wrangler dev -c wrangler.prod.json --test-scheduled` then `curl localhost:8787/__scheduled`
runs it once. Add `/__scheduled` to `run_worker_first` in that config first, or the asset router answers it.

## Add a site to the portfolio

```
node scripts/add-site.mjs https://newclient.com "New Client Name"
```

That writes `src/data/work/newclient.json` and saves desktop and phone screenshots to `public/work/`.
Fill in every `TODO` in the new file (the build refuses to ship one), then build and deploy production.
Sites are listed by their `order` number; new ones go last. Retake screenshots any time with
`node scripts/shoot.mjs` (all sites) or `node scripts/shoot.mjs <slug>` (one site).
