import { defineConfig } from 'astro/config';
import solid from '@astrojs/solid-js';
import sitemap from '@astrojs/sitemap';
import { fileURLToPath } from 'node:url';

// VARIANT picks the design direction (v1..v4). Same pages and copy, different theme.
const variant = process.env.VARIANT || 'v1';

export default defineConfig({
  site: 'https://sitesmyth.com',
  trailingSlash: 'always',
  // The indexable production build gets its own folder so it never overwrites a noindex preview.
  outDir: process.env.PROD === '1' ? './dist/prod' : `./dist/${variant}`,
  integrations: [solid(), sitemap({ filter: (p) => !p.includes('/404') })],
  vite: {
    resolve: {
      alias: { '@theme': fileURLToPath(new URL(`./src/themes/${variant}`, import.meta.url)) },
    },
  },
});
