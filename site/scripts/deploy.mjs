// Deploys one design direction as its own Worker on <variant>.sitesmyth.com,
// or the production build (PROD=1, dist/prod) on sitesmyth.com and www.
// Usage: node scripts/deploy.mjs v1 [v2 ...] | node scripts/deploy.mjs prod
import { execSync } from 'node:child_process';
import { writeFileSync, rmSync } from 'node:fs';

const ACCOUNT = 'd05695b603695da0c23608f974cc86a6';
const KV = 'f452c03e790e49a981a15fc7e1c04731';

for (const v of process.argv.slice(2)) {
  const prod = v === 'prod';
  const cfg = {
    name: prod ? 'sitesmyth-site' : `sitesmyth-${v}`,
    main: 'worker/index.js',
    compatibility_date: '2026-09-15',
    account_id: ACCOUNT,
    workers_dev: false,
    assets: { directory: `dist/${v}`, binding: 'ASSETS', not_found_handling: '404-page', run_worker_first: prod ? true : ['/api/*'] }, // prod runs the Worker first for the www redirect
    kv_namespaces: [{ binding: 'LEADS', id: KV }],
    routes: prod
      ? [
          { pattern: 'sitesmyth.com/*', zone_name: 'sitesmyth.com' },
          { pattern: 'www.sitesmyth.com/*', zone_name: 'sitesmyth.com' },
        ]
      : [{ pattern: `${v}.sitesmyth.com/*`, zone_name: 'sitesmyth.com' }],
  };
  const file = `wrangler.${v}.json`;
  writeFileSync(file, JSON.stringify(cfg, null, 2));
  const env = { ...process.env };
  delete env.CLOUDFLARE_API_TOKEN; // use the OAuth login, which has KV + Workers write
  try {
    execSync(`npx wrangler deploy -c ${file}`, { stdio: 'inherit', env });
  } finally {
    rmSync(file);
  }
}
