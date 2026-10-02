// Every page, every variant, phone and desktop: horizontal overflow, console errors, one h1.
import { chromium } from 'playwright';
import { readdirSync, statSync } from 'node:fs';
import { join } from 'node:path';
const pages = (dir, base = '') => readdirSync(dir).flatMap((f) => {
  const p = join(dir, f);
  if (statSync(p).isDirectory()) return pages(p, `${base}/${f}`);
  return f === 'index.html' ? [`${base}/`] : [];
});
const b = await chromium.launch();
let bad = 0;
for (const [i, v] of ['v1', 'v2', 'v3', 'v4'].entries()) {
  const port = 8731 + i;
  for (const path of pages(`dist/${v}`)) {
    for (const width of [375, 1280]) {
      const pg = await b.newPage({ viewport: { width, height: 800 } });
      const errs = [];
      pg.on('pageerror', (e) => errs.push(e.message));
      pg.on('console', (m) => m.type() === 'error' && errs.push(m.text()));
      await pg.goto(`http://localhost:${port}${path}`, { waitUntil: 'networkidle' });
      const r = await pg.evaluate(() => ({
        over: document.documentElement.scrollWidth - innerWidth,
        h1: document.querySelectorAll('h1').length,
      }));
      if (r.over > 0 || r.h1 !== 1 || errs.length) { bad++; console.log(v, width, path, JSON.stringify(r), errs.join(' | ')); }
      await pg.close();
    }
  }
}
console.log(bad ? `${bad} problems` : 'all clean');
await b.close();
