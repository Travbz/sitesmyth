import { createSignal, onCleanup, onMount, Show } from 'solid-js';

// Site-wide drafting layer, mounted once per page.
// A CAD crosshair follows the pointer everywhere. Over a measurable part of
// the page it reads out that part's size and the part gets registration ticks.
// Fine pointers only; reduced motion keeps the measuring but drops easing.
const MEASURE = '.svc, .work-item .viewer-frame, .owned, .step, .need, .ind-list a, .board, .faq details, .field input, .field textarea, .field select, .btn';

export default function Drafting() {
  const [on, setOn] = createSignal(false);
  const [x, setX] = createSignal(0);
  const [y, setY] = createSignal(0);
  const [dims, setDims] = createSignal('');

  onMount(() => {
    const fine = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
    if (!fine) return;
    let raf = 0;
    let last: PointerEvent | null = null;
    let measured: HTMLElement | null = null;
    const root = document.documentElement;

    const paint = () => {
      raf = 0;
      const e = last;
      if (!e) return;
      root.style.setProperty('--cx', `${e.clientX}px`);
      root.style.setProperty('--cy', `${e.clientY}px`);
      setX(Math.round(e.clientX));
      setY(Math.round(e.clientY + window.scrollY));
      const el = (e.target as Element | null)?.closest?.(MEASURE) as HTMLElement | null;
      if (measured && measured !== el) measured.removeAttribute('data-measured');
      measured = el;
      if (el) {
        el.setAttribute('data-measured', '');
        const r = el.getBoundingClientRect();
        setDims(`${Math.round(r.width)} × ${Math.round(r.height)}`);
      } else {
        setDims('');
      }
    };
    const move = (e: PointerEvent) => {
      last = e;
      setOn(true);
      if (!raf) raf = requestAnimationFrame(paint);
    };
    const leave = () => {
      setOn(false);
      measured?.removeAttribute('data-measured');
      measured = null;
    };
    document.addEventListener('pointermove', move, { passive: true });
    document.documentElement.addEventListener('pointerleave', leave);
    onCleanup(() => {
      cancelAnimationFrame(raf);
      document.removeEventListener('pointermove', move);
      document.documentElement.removeEventListener('pointerleave', leave);
    });
  });

  return (
    <Show when={on()}>
      <div class="crosshair" aria-hidden="true">
        <span class="crosshair-x" />
        <span class="crosshair-y" />
        <span class="crosshair-read">
          <Show when={dims()} fallback={<>X {x()}  Y {y()}</>}>W × H  {dims()}</Show>
        </span>
      </div>
    </Show>
  );
}
