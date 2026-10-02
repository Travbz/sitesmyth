import { createSignal, Show } from 'solid-js';

// Flips one portfolio screenshot between desktop and phone.
export default function ShotToggle(props: { slug: string; name: string; url: string }) {
  const [phone, setPhone] = createSignal(false);
  return (
    <div class="shot">
      <div class="device-toggle" role="group" aria-label={`${props.name} preview size`}>
        <button aria-pressed={!phone()} onClick={() => setPhone(false)}>Desktop</button>
        <button aria-pressed={phone()} onClick={() => setPhone(true)}>Phone</button>
      </div>
      <a class={`viewer-frame ${phone() ? 'phone' : 'desktop'}`} href={props.url} target="_blank" rel="noopener" aria-label={`Visit the ${props.name} website`}>
        <Show when={phone()} fallback={
          <img src={`/work/${props.slug}-desktop.webp`} width="1200" height="750" alt={`${props.name} home page on a desktop screen`} loading="lazy" decoding="async" />
        }>
          <img src={`/work/${props.slug}-phone.webp`} width="600" height="1298" alt={`${props.name} home page on a phone`} decoding="async" />
        </Show>
      </a>
    </div>
  );
}
