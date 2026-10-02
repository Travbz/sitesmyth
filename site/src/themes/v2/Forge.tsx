import { onCleanup, onMount } from 'solid-js';

type P = { x: number; y: number; vx: number; vy: number; life: number; max: number; r: number; g: number };
type Fire = { host: HTMLElement; canvas: HTMLCanvasElement; ctx: CanvasRenderingContext2D; w: number; h: number; parts: P[]; on: boolean; tick: number };

// Site-wide forge layer, mounted once per page.
// Every hero, page header, and CTA band gets its own ember canvas; headlines
// land with a spark burst. Tiles carry an ember glow that follows the pointer.
// Reduced motion skips the canvases; off-screen fires pause.
const FIRE_HOSTS = '.hero, .page-head, .cta-band';
const GLOW = '.svc, .work-item, .owned-row, .step, .need, .faq details, .ind-list li, .viewer-frame';

export default function Forge() {
  onMount(() => {
    const still = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const fine = window.matchMedia('(hover: hover) and (pointer: fine)').matches;

    // pointer-following ember glow on tiles (CSS reads --mx / --my)
    let glowEl: HTMLElement | null = null;
    let pending: PointerEvent | null = null;
    let glowRaf = 0;
    const glow = () => {
      glowRaf = 0;
      const e = pending;
      if (!e) return;
      const el = (e.target as Element | null)?.closest?.(GLOW) as HTMLElement | null;
      if (glowEl && glowEl !== el) glowEl.removeAttribute('data-hot');
      glowEl = el;
      if (!el) return;
      const r = el.getBoundingClientRect();
      el.style.setProperty('--mx', `${e.clientX - r.left}px`);
      el.style.setProperty('--my', `${e.clientY - r.top}px`);
      el.setAttribute('data-hot', '');
    };
    const onMove = (e: PointerEvent) => {
      pending = e;
      if (!glowRaf) glowRaf = requestAnimationFrame(glow);
      if (!still) stir(e);
    };
    if (fine) document.addEventListener('pointermove', onMove, { passive: true });

    if (still) {
      onCleanup(() => document.removeEventListener('pointermove', onMove));
      return;
    }

    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const fires: Fire[] = [];
    const MAX = 120;

    const spawn = (f: Fire, x: number, y: number, n: number, heat: number) => {
      for (let i = 0; i < n && f.parts.length < MAX; i++) {
        const a = Math.random() * Math.PI * 2;
        const s = heat * (0.4 + Math.random());
        f.parts.push({ x, y, vx: Math.cos(a) * s, vy: Math.sin(a) * s - heat * 0.8, life: 0, max: 40 + Math.random() * 50, r: 0.8 + Math.random() * 1.6, g: 0.05 });
      }
    };

    const size = (f: Fire) => {
      const r = f.host.getBoundingClientRect();
      f.w = r.width; f.h = r.height;
      f.canvas.width = f.w * dpr; f.canvas.height = f.h * dpr;
      f.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    };
    const ro = new ResizeObserver((entries) => {
      for (const en of entries) {
        const f = fires.find((x) => x.host === en.target);
        if (f) size(f);
      }
    });
    const io = new IntersectionObserver((entries) => {
      for (const en of entries) {
        const f = fires.find((x) => x.host === en.target);
        if (f) f.on = en.isIntersecting;
      }
      kick();
    });

    document.querySelectorAll<HTMLElement>(FIRE_HOSTS).forEach((host) => {
      const canvas = document.createElement('canvas');
      canvas.className = 'sparks';
      canvas.setAttribute('aria-hidden', 'true');
      host.prepend(canvas);
      const ctx = canvas.getContext('2d');
      if (!ctx) return;
      const f: Fire = { host, canvas, ctx, w: 0, h: 0, parts: [], on: true, tick: 0 };
      size(f);
      fires.push(f);
      ro.observe(host);
      io.observe(host);
    });

    // the strike: headlines that slam in get a burst where they land
    const strikes = fires
      .filter((f) => !f.host.classList.contains('cta-band'))
      .map((f) => setTimeout(() => {
        const head = f.host.querySelector('h1');
        const hr = head?.getBoundingClientRect();
        const r = f.host.getBoundingClientRect();
        const x = hr ? hr.left - r.left + Math.min(hr.width, 520) * 0.35 : f.w * 0.3;
        const y = hr ? hr.top - r.top + hr.height : f.h * 0.4;
        spawn(f, x, y, f.host.classList.contains('hero') ? 60 : 36, 4.2);
        kick();
      }, 620));

    let lastStir = 0;
    function stir(e: PointerEvent) {
      const now = performance.now();
      if (now - lastStir < 90) return;
      lastStir = now;
      for (const f of fires) {
        const r = f.host.getBoundingClientRect();
        if (e.clientX >= r.left && e.clientX <= r.right && e.clientY >= r.top && e.clientY <= r.bottom) {
          spawn(f, e.clientX - r.left, e.clientY - r.top, 2, 1.6);
          kick();
        }
      }
    }

    let raf = 0;
    const kick = () => { if (!raf && !document.hidden) raf = requestAnimationFrame(frame); };
    const frame = () => {
      raf = 0;
      if (document.hidden) return;
      let any = false;
      for (const f of fires) {
        if (!f.on) continue;
        any = true;
        f.tick++;
        // ambient embers rise from the floor of each fire
        const rate = f.host.classList.contains('hero') ? 18 : 30;
        if (f.tick % rate === 0 && f.parts.length < MAX - 20) {
          f.parts.push({ x: Math.random() * f.w, y: f.h + 4, vx: (Math.random() - 0.5) * 0.3, vy: -(0.4 + Math.random() * 0.7), life: 0, max: 160 + Math.random() * 120, r: 0.7 + Math.random() * 1.2, g: 0 });
        }
        const { ctx, parts } = f;
        ctx.clearRect(0, 0, f.w, f.h);
        for (let i = parts.length - 1; i >= 0; i--) {
          const p = parts[i];
          p.life++;
          p.x += p.vx; p.y += p.vy;
          p.vy += p.g;
          p.vx = p.vx * 0.99 + (p.g === 0 ? Math.sin((f.tick + p.y) * 0.02) * 0.01 : 0);
          const k = 1 - p.life / p.max;
          if (k <= 0 || p.y > f.h + 8 || p.y < -8) { parts.splice(i, 1); continue; }
          ctx.globalAlpha = Math.min(1, k * 1.6);
          ctx.fillStyle = `rgb(255, ${Math.floor(120 + 135 * k)}, ${Math.floor(40 * k)})`;
          ctx.beginPath();
          ctx.arc(p.x, p.y, p.r * (0.6 + k * 0.6), 0, Math.PI * 2);
          ctx.fill();
        }
        ctx.globalAlpha = 1;
      }
      if (any) raf = requestAnimationFrame(frame);
    };
    kick();
    document.addEventListener('visibilitychange', kick);

    onCleanup(() => {
      cancelAnimationFrame(raf);
      cancelAnimationFrame(glowRaf);
      strikes.forEach(clearTimeout);
      ro.disconnect();
      io.disconnect();
      document.removeEventListener('visibilitychange', kick);
      document.removeEventListener('pointermove', onMove);
      fires.forEach((f) => f.canvas.remove());
    });
  });

  return null;
}
