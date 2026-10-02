import { onCleanup, onMount } from 'solid-js';

type P = { x: number; y: number; vx: number; vy: number; life: number; max: number; r: number; g: number };

// Forge sparks: one burst when the headline lands, then drifting embers.
// Moving the pointer through the hero stirs a few more. Decoration only:
// skipped entirely for reduced motion, paused when the hero leaves the screen.
export default function Sparks() {
  let canvas: HTMLCanvasElement | undefined;
  let raf = 0;

  onMount(() => {
    if (!canvas) return;
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    const ctx = canvas.getContext('2d');
    const host = canvas.closest('.hero') as HTMLElement | null;
    if (!ctx || !host) return;

    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    let w = 0, h = 0;
    const size = () => {
      const r = host.getBoundingClientRect();
      w = r.width; h = r.height;
      canvas!.width = w * dpr; canvas!.height = h * dpr;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    };
    size();
    const ro = new ResizeObserver(size);
    ro.observe(host);

    const parts: P[] = [];
    const MAX = 140;
    const spawn = (x: number, y: number, n: number, heat: number) => {
      for (let i = 0; i < n && parts.length < MAX; i++) {
        const a = Math.random() * Math.PI * 2;
        const s = heat * (0.4 + Math.random());
        parts.push({
          x, y,
          vx: Math.cos(a) * s,
          vy: Math.sin(a) * s - heat * 0.8,
          life: 0,
          max: 40 + Math.random() * 50,
          r: 0.8 + Math.random() * 1.6,
          g: 0.05,
        });
      }
    };

    // the strike: a burst where the headline sits, timed to its slam-in
    const strike = () => {
      const head = host.querySelector('h1');
      const hr = head?.getBoundingClientRect();
      const hostR = host.getBoundingClientRect();
      const x = hr ? hr.left - hostR.left + hr.width * 0.35 : w * 0.3;
      const y = hr ? hr.top - hostR.top + hr.height : h * 0.4;
      spawn(x, y, 60, 4.5);
    };
    const t = setTimeout(strike, 620);

    // ambient embers rise from the bottom edge
    let tick = 0;
    const ambient = () => {
      if (tick % 18 === 0 && parts.length < MAX - 20) {
        parts.push({
          x: Math.random() * w, y: h + 4,
          vx: (Math.random() - 0.5) * 0.3,
          vy: -(0.4 + Math.random() * 0.7),
          life: 0, max: 160 + Math.random() * 120,
          r: 0.7 + Math.random() * 1.2,
          g: 0,
        });
      }
    };

    let running = true;
    const io = new IntersectionObserver(([e]) => {
      running = e.isIntersecting;
      if (running && !raf) raf = requestAnimationFrame(frame);
    });
    io.observe(host);

    const fine = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
    let lastStir = 0;
    const stir = (e: PointerEvent) => {
      const now = performance.now();
      if (now - lastStir < 90) return;
      lastStir = now;
      const r = host.getBoundingClientRect();
      spawn(e.clientX - r.left, e.clientY - r.top, 2, 1.6);
    };
    if (fine) host.addEventListener('pointermove', stir, { passive: true });

    const frame = () => {
      raf = 0;
      if (!running || document.hidden) return;
      tick++;
      ambient();
      ctx.clearRect(0, 0, w, h);
      for (let i = parts.length - 1; i >= 0; i--) {
        const p = parts[i];
        p.life++;
        p.x += p.vx; p.y += p.vy;
        p.vy += p.g; // burst sparks fall; embers keep floating
        p.vx = p.vx * 0.99 + (p.g === 0 ? Math.sin((tick + p.y) * 0.02) * 0.01 : 0);
        const k = 1 - p.life / p.max;
        if (k <= 0 || p.y > h + 8 || p.y < -8) { parts.splice(i, 1); continue; }
        // hot core cooling through orange to dull red
        const g = Math.floor(120 + 135 * k);
        ctx.globalAlpha = Math.min(1, k * 1.6);
        ctx.fillStyle = `rgb(255, ${g}, ${Math.floor(40 * k)})`;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r * (0.6 + k * 0.6), 0, Math.PI * 2);
        ctx.fill();
      }
      ctx.globalAlpha = 1;
      raf = requestAnimationFrame(frame);
    };
    raf = requestAnimationFrame(frame);

    const vis = () => { if (!document.hidden && running && !raf) raf = requestAnimationFrame(frame); };
    document.addEventListener('visibilitychange', vis);

    onCleanup(() => {
      cancelAnimationFrame(raf);
      clearTimeout(t);
      ro.disconnect();
      io.disconnect();
      document.removeEventListener('visibilitychange', vis);
      if (fine) host.removeEventListener('pointermove', stir);
    });
  });

  return <canvas class="sparks" ref={canvas} aria-hidden="true" />;
}
