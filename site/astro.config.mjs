import { defineConfig } from 'astro/config';
import solid from '@astrojs/solid-js';
import sitemap from '@astrojs/sitemap';
import { fileURLToPath } from 'node:url';

// VARIANT picks the design direction (v1..v4). Same pages and copy, different theme.
const variant = process.env.VARIANT || 'v1';

export default defineConfig({
  site: 'https://sitesmyth.com',
  trailingSlash: 'always',
  outDir: `./dist/${variant}`,
  integrations: [solid(), sitemap({ filter: (p) => !p.includes('/404') })],
  vite: {
    resolve: {
      alias: { '@theme': fileURLToPath(new URL(`./src/themes/${variant}`, import.meta.url)) },
    },
  },
});
