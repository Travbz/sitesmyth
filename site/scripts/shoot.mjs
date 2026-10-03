// Screenshots portfolio sites into public/work/<slug>-desktop.webp and <slug>-phone.webp.
// Usage: node scripts/shoot.mjs            (every site in src/data/work/)
//        node scripts/shoot.mjs tipsy-trout (just the named slugs)
import { chromium } from 'playwright';
import sharp from 'sharp';
import { readdirSync, readFileSync } from 'node:fs';

const DIR = 'src/data/work';
const want = process.argv.slice(2);
const sites = readdirSync(DIR)
  .filter((f) => f.endsWith('.json'))
  .map((f) => ({ slug: f.slice(0, -5), url: JSON.parse(readFileSync(`${DIR}/${f}`, 'utf8')).url }))
  .filter((s) => !want.length || want.includes(s.slug));

if (want.length && sites.length !== want.length) {
  const found = sites.map((s) => s.slug);
  console.error(`No file in ${DIR} for: ${want.filter((w) => !found.includes(w)).join(', ')}`);
  process.exit(1);
}

const views = {
  desktop: { viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1, out: 1200 },
  phone: { viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, out: 600 },
};

const browser = await chromium.launch();
for (const { slug, url } of sites) {
  for (const [kind, v] of Object.entries(views)) {
    const page = await browser.newPage({ viewport: v.viewport, deviceScaleFactor: v.deviceScaleFactor, reducedMotion: 'reduce' });
    await page.goto(url, { waitUntil: 'networkidle', timeout: 45000 }).catch(() => {});
    await page.waitForTimeout(2500);
    const png = await page.screenshot();
    await sharp(png).resize({ width: v.out }).webp({ quality: 82 }).toFile(`public/work/${slug}-${kind}.webp`);
    await page.close();
  }
  console.log('shot', slug);
}
await browser.close();
