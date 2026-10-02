import { chromium } from 'playwright';
const sites = {
  'loos-and-sons': 'https://loosandsonshvac.com/',
  'elevation-fire': 'https://elevationfireprotection.com/',
  'tipsy-trout': 'https://tipsytrouttaproom.com/',
  'v-sandoval': 'https://vsandovalcleaning.com/',
  'respondyr': 'https://respondyr.com/',
};
const b = await chromium.launch();
for (const [slug, url] of Object.entries(sites)) {
  for (const [kind, vp] of [['desktop', { width: 1440, height: 900 }], ['phone', { width: 390, height: 844 }]]) {
    const p = await b.newPage({ viewport: vp, deviceScaleFactor: kind === 'phone' ? 2 : 1, reducedMotion: 'reduce' });
    await p.goto(url, { waitUntil: 'networkidle', timeout: 45000 }).catch(() => {});
    await p.waitForTimeout(2500);
    await p.screenshot({ path: `public/work/${slug}-${kind}.png` });
    await p.close();
  }
  console.log('shot', slug);
}
await b.close();
