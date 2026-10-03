// Adds a site to the portfolio: writes src/data/work/<slug>.json and takes its screenshots.
// Usage: node scripts/add-site.mjs https://example.com ["Business Name"]
// Fill in every TODO in the new file before building; the build refuses to ship a TODO.
import { execFileSync } from 'node:child_process';
import { existsSync, readdirSync, readFileSync, writeFileSync } from 'node:fs';

const [raw, nameArg] = process.argv.slice(2);
if (!raw) {
  console.error('Usage: node scripts/add-site.mjs <url> ["Business Name"]');
  process.exit(1);
}
const url = new URL(raw.includes('://') ? raw : `https://${raw}`);
url.pathname = url.pathname.endsWith('/') ? url.pathname : `${url.pathname}/`;
const domain = url.hostname.replace(/^www\./, '');
const slug = domain.split('.').slice(0, -1).join('-').toLowerCase().replace(/[^a-z0-9-]/g, '-');

const DIR = 'src/data/work';
const file = `${DIR}/${slug}.json`;
if (existsSync(file)) {
  console.error(`${file} already exists. Edit it, or run node scripts/shoot.mjs ${slug} to retake its screenshots.`);
  process.exit(1);
}

// New sites go to the end of the list; change "order" to move one.
const orders = readdirSync(DIR)
  .filter((f) => f.endsWith('.json'))
  .map((f) => JSON.parse(readFileSync(`${DIR}/${f}`, 'utf8')).order ?? 0);
const order = (orders.length ? Math.max(...orders) : 0) + 10;

const entry = {
  order,
  name: nameArg || 'TODO business name',
  url: url.href,
  domain,
  kind: 'TODO what the business is, like "HVAC contractor"',
  place: 'TODO town and state, like "Longmont, Colorado"',
  pages: 'TODO size, like "One page" or "About 40 pages"',
  summary: 'TODO two sentences on what the site does for them',
  built: ['TODO one thing the site has', 'TODO another'],
};
writeFileSync(file, `${JSON.stringify(entry, null, 2)}\n`);
console.log(`wrote ${file}`);

execFileSync('node', ['scripts/shoot.mjs', slug], { stdio: 'inherit' });
console.log(`\nNext: fill in the TODOs in ${file}, then build and deploy.`);
