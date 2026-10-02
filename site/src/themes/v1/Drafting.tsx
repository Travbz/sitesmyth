import { createSignal, onMount, Show } from 'solid-js';

// CAD crosshair that follows the pointer across the drafting board.
// Decorative only: fine pointers get it, touch and reduced motion skip it.
export default function Drafting() {
  const [on, setOn] = createSignal(false);
  const [pos, setPos] = createSignal({ x: 0, y: 0 });
  let board: HTMLDivElement | undefined;
  let raf = 0;

  onMount(() => {
    const fine = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
    const still = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (!fine || still || !board) return;
    const host = board.closest('.hero') as HTMLElement | null;
    if (!host) return;
    const move = (e: PointerEvent) => {
      if (raf) return;
      raf = requestAnimationFrame(() => {
        raf = 0;
        const r = host.getBoundingClientRect();
        const x = e.clientX - r.left;
        const y = e.clientY - r.top;
        host.style.setProperty('--cx', `${x}px`);
        host.style.setProperty('--cy', `${y}px`);
        setPos({ x: Math.round(x), y: Math.round(y) });
      });
    };
    host.addEventListener('pointermove', move, { passive: true });
    host.addEventListener('pointerenter', () => setOn(true));
    host.addEventListener('pointerleave', () => setOn(false));
  });

  return (
    <div class="crosshair-host" ref={board} aria-hidden="true">
      <Show when={on()}>
        <span class="crosshair-x" />
        <span class="crosshair-y" />
        <span class="crosshair-read">{pos().x} , {pos().y}</span>
      </Show>
    </div>
  );
}
