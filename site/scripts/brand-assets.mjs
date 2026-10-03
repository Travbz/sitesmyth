// Renders SiteSmyth's share card (public/og.png, 1200x630) and app icon
// (public/apple-touch-icon.png, 180x180) in the Blueprint style, with the site's real font.
// Rerun after a brand change: node scripts/brand-assets.mjs
import { chromium } from 'playwright';
import { readFileSync } from 'node:fs';

// Embedded as a data URL: a page set from a string cannot load file:// fonts.
const font = readFileSync(new URL('../node_modules/@fontsource-variable/space-grotesk/files/space-grotesk-latin-wght-normal.woff2', import.meta.url)).toString('base64');
const base = `
  @font-face { font-family: 'SG'; src: url(data:font/woff2;base64,${font}) format('woff2'); font-weight: 300 700; }
  * { margin: 0; box-sizing: border-box; }
  body {
    font-family: 'SG', sans-serif; color: #fff; background: #123a5e;
    background-image: linear-gradient(rgba(168,201,228,.10) 1px, transparent 1px), linear-gradient(90deg, rgba(168,201,228,.10) 1px, transparent 1px);
    background-size: 40px 40px;
  }
  .slash { color: #e8604c; }
`;
const card = `<html><head><style>${base}
  body { width: 1200px; height: 630px; padding: 72px 80px; display: flex; flex-direction: column; justify-content: space-between;
    box-shadow: inset 0 0 0 18px #123a5e, inset 0 0 0 20px rgba(168,201,228,.45); }
  .mark { font-size: 120px; font-weight: 700; letter-spacing: -0.02em; line-height: 1; }
  .tag { font-size: 48px; font-weight: 500; line-height: 1.15; max-width: 1040px; margin-top: 28px; }
  .foot { display: flex; justify-content: space-between; align-items: flex-end; font-size: 26px; letter-spacing: .14em; color: #a8c9e4; }
  .dim { width: 360px; height: 14px; border-left: 2px solid #e8604c; border-right: 2px solid #e8604c;
    background: linear-gradient(#e8604c, #e8604c) center / 100% 2px no-repeat; }
</style></head><body>
  <div><div class="mark">SiteSmyth <span class="slash">/</span></div>
  <div class="tag">Small business websites you own outright</div></div>
  <div class="foot"><span>SITESMYTH.COM</span><span class="dim"></span></div>
</body></html>`;
const icon = `<html><head><style>${base}
  body { width: 180px; height: 180px; display: grid; place-items: center; font-weight: 700; font-size: 104px; letter-spacing: -0.04em; line-height: 1; }
</style></head><body><div>S<span class="slash">/</span></div></body></html>`;

const browser = await chromium.launch();
for (const [html, w, h, out] of [[card, 1200, 630, 'public/og.png'], [icon, 180, 180, 'public/apple-touch-icon.png']]) {
  const page = await browser.newPage({ viewport: { width: w, height: h } });
  await page.setContent(html, { waitUntil: 'load' });
  await page.evaluate(async () => { await document.fonts.load('700 100px SG'); await document.fonts.load('500 48px SG'); await document.fonts.ready; });
  await page.screenshot({ path: out });
  await page.close();
  console.log('wrote', out);
}
await browser.close();
