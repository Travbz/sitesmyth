import { createSignal, Show } from 'solid-js';

type Field = 'name' | 'business' | 'email' | 'message';
const REQUIRED: Record<Field, string> = {
  name: 'Enter your name.',
  business: 'Enter your business name.',
  email: 'Enter an email address so we can reply.',
  message: 'Tell us a little about what you need.',
};

export default function ContactForm() {
  const [errors, setErrors] = createSignal<Partial<Record<Field, string>>>({});
  const [state, setState] = createSignal<'idle' | 'sending' | 'sent' | 'error'>('idle');
  let form!: HTMLFormElement;

  const check = (name: Field, value: string) => {
    let msg = '';
    if (!value.trim()) msg = REQUIRED[name];
    else if (name === 'email' && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value.trim())) msg = 'That email address looks incomplete. Check it and try again.';
    setErrors((e) => ({ ...e, [name]: msg || undefined }));
    return !msg;
  };

  const onBlur = (e: FocusEvent) => {
    const el = e.target as HTMLInputElement;
    if (el.name in REQUIRED) check(el.name as Field, el.value);
  };

  const submit = async (e: SubmitEvent) => {
    e.preventDefault();
    const data = Object.fromEntries(new FormData(form)) as Record<string, string>;
    const bad = (Object.keys(REQUIRED) as Field[]).filter((f) => !check(f, data[f] ?? ''));
    if (bad.length) {
      (form.elements.namedItem(bad[0]) as HTMLElement)?.focus();
      return;
    }
    setState('sending');
    try {
      const res = await fetch('/api/contact', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify(data),
      });
      if (!res.ok) throw new Error(String(res.status));
      setState('sent');
    } catch {
      setState('error');
    }
  };

  const err = (f: Field) => errors()[f];
  const field = (f: Field) => ({
    name: f,
    id: `f-${f}`,
    required: true,
    'aria-invalid': err(f) ? true : undefined,
    'aria-describedby': err(f) ? `e-${f}` : undefined,
    onBlur,
  });

  return (
    <Show
      when={state() !== 'sent'}
      fallback={
        <div class="status" role="status">
          <strong>Message sent.</strong> Thanks for reaching out. You will hear back by email.
        </div>
      }
    >
      <form class="form" ref={form} onSubmit={submit} novalidate>
        <div class="field">
          <label for="f-name">Your name</label>
          <input {...field('name')} autocomplete="name" />
          <Show when={err('name')}><p class="err" id="e-name">{err('name')}</p></Show>
        </div>
        <div class="field">
          <label for="f-business">Business name</label>
          <input {...field('business')} autocomplete="organization" />
          <Show when={err('business')}><p class="err" id="e-business">{err('business')}</p></Show>
        </div>
        <div class="field">
          <label for="f-email">Email</label>
          <input {...field('email')} type="email" autocomplete="email" inputmode="email" />
          <Show when={err('email')}><p class="err" id="e-email">{err('email')}</p></Show>
        </div>
        <div class="field">
          <label for="f-phone">Phone <span class="hint">(optional)</span></label>
          <input id="f-phone" name="phone" type="tel" autocomplete="tel" inputmode="tel" />
        </div>
        <div class="field">
          <label for="f-site">Current website <span class="hint">(if you have one)</span></label>
          <input id="f-site" name="site" type="url" inputmode="url" placeholder="https://" />
        </div>
        <div class="field">
          <label for="f-need">What are you looking for?</label>
          <select id="f-need" name="need">
            <option>Not sure yet</option>
            <option>A one-page website</option>
            <option>A full website with service or menu pages</option>
            <option>Pages for the towns I serve</option>
            <option>A redesign of my current site</option>
            <option>Monthly SEO or ads for my business</option>
            <option>A one-off Google Business Profile and reviews consult</option>
          </select>
        </div>
        <div class="field">
          <label for="f-message">Tell us about your business</label>
          <p class="hint" id="h-message">What you do, where you work, and anything you want the site to do.</p>
          <textarea {...field('message')} aria-describedby={err('message') ? 'e-message h-message' : 'h-message'} />
          <Show when={err('message')}><p class="err" id="e-message">{err('message')}</p></Show>
        </div>
        <div class="hp" aria-hidden="true">
          <label for="f-company">Leave this empty</label>
          <input id="f-company" name="company_site" tabindex="-1" autocomplete="off" />
        </div>
        <Show when={state() === 'error'}>
          <p class="err" role="alert">The message did not send. Check your connection and press send again.</p>
        </Show>
        <div>
          <button class="btn btn-primary" type="submit" disabled={state() === 'sending'}>
            {state() === 'sending' ? 'Sending…' : 'Send message'}
          </button>
        </div>
      </form>
    </Show>
  );
}
