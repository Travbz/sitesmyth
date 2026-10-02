import { createSignal, For, Show } from 'solid-js';

type Item = { slug: string; name: string; domain: string; url: string; kind: string; place: string; summary: string };

export default function WorkViewer(props: { items: Item[]; heading?: string }) {
  const [active, setActive] = createSignal(0);
  const [device, setDevice] = createSignal<'desktop' | 'phone'>('desktop');
  const cur = () => props.items[active()];

  // Arrow keys move between tabs, per the WAI-ARIA tabs pattern.
  const onKey = (e: KeyboardEvent) => {
    const n = props.items.length;
    let next = active();
    if (e.key === 'ArrowRight') next = (active() + 1) % n;
    else if (e.key === 'ArrowLeft') next = (active() - 1 + n) % n;
    else return;
    e.preventDefault();
    setActive(next);
    (document.getElementById(`tab-${props.items[next].slug}`) as HTMLButtonElement)?.focus();
  };

  return (
    <div class="viewer">
      <div class="viewer-bar">
        <div class="viewer-tabs" role="tablist" aria-label={props.heading ?? 'Sites we built'} onKeyDown={onKey}>
          <For each={props.items}>
            {(it, i) => (
              <button
                id={`tab-${it.slug}`}
                role="tab"
                aria-selected={active() === i()}
                aria-controls="viewer-panel"
                tabindex={active() === i() ? 0 : -1}
                onClick={() => setActive(i())}
              >
                {it.name}
              </button>
            )}
          </For>
        </div>
        <div class="device-toggle" role="group" aria-label="Preview size">
          <button aria-pressed={device() === 'desktop'} onClick={() => setDevice('desktop')}>Desktop</button>
          <button aria-pressed={device() === 'phone'} onClick={() => setDevice('phone')}>Phone</button>
        </div>
      </div>
      <div id="viewer-panel" role="tabpanel" aria-labelledby={`tab-${cur().slug}`} class="viewer-stage">
        <a class={`viewer-frame ${device()}`} href={cur().url} target="_blank" rel="noopener">
          <Show when={device() === 'desktop'} fallback={
            <img src={`/work/${cur().slug}-phone.webp`} width="600" height="1298" alt={`${cur().name} website on a phone`} />
          }>
            <img src={`/work/${cur().slug}-desktop.webp`} width="1200" height="750" alt={`${cur().name} website on a desktop screen`} />
          </Show>
        </a>
      </div>
      <div class="viewer-caption">
        <div>
          <strong>{cur().name}</strong> <span class="viewer-meta">{cur().kind}, {cur().place}</span>
        </div>
        <a href={cur().url} target="_blank" rel="noopener">Visit {cur().domain}</a>
      </div>
    </div>
  );
}
