// Builds every design direction into dist/v1..v4.
import { execSync } from 'node:child_process';
for (const v of ['v1', 'v2', 'v3', 'v4']) {
  execSync('npx astro build', { stdio: 'inherit', env: { ...process.env, VARIANT: v } });
}
