# SiteSmyth: Gemini Code Builder — Test Roadmap

## Problem

The current generator produces bad sites:
- **Template fill**: A fixed HTML template + Gemini JSON output = zero design personality
- **Content hallucination**: Gemini gets 3 Facebook captions and invents "Sturgis Rally" for a Montrose bar
- **No content gate**: We build demo sites for leads with barely any social content, wasting API credits and sending ugly demos

SiteForge solved this with Claude Code CLI (~$2-5/site) building each site from scratch. That works but it's expensive at scale. This roadmap tests whether **Gemini 2.5 Flash + a coding tool workflow** can match that quality at 1/10th the cost.

## Hypothesis

If we give Gemini Flash the same workflow SiteForge gives Claude Code — empty Astro scaffold, ghostwritten prompt, image manifest, and the ability to write files — it can produce sites that are good enough to send as demos. If not, we fall back to SiteForge's Claude Code approach.

---

## Phase 1: Content Gate (skip bad leads)

**Goal**: Don't waste time generating sites for leads with no usable social content. Instead, send a "no-demo" email linking them to sitesmyth.com.

### 1a. Scoring scraped content

After the scrape step, score each lead:

```
content_score = (
    num_captions * 2
    + num_images * 1
    + (10 if has_bio else 0)
    + (5 if has_address else 0)
    + (5 if has_phone else 0)
)
```

- **Score >= 15**: Proceed to site generation (enough content for a real demo)
- **Score < 15**: Mark as `low_content`, skip generation, send no-demo email instead

### 1b. No-demo email template

For low-content leads, send a simpler outreach email:

> Subject: A website for {{business_name}}?
>
> Hi — I build websites for local businesses like {{business_name}}.
>
> I'd love to put together a free demo site for you. Check out what I do at sitesmyth.com and reply if you're interested.

No demo link, no site to maintain. Just a feeler email.

### 1c. Pipeline changes

- Add `content_score` column to `leads` table
- After scrape step: compute score, update lead
- Generate step: filter `WHERE content_score >= 15`
- Outreach step: send no-demo template for `low_content` leads, demo template for `hosted` leads

---

## Phase 2: Gemini Code Builder (replace template fill)

**Goal**: Replace `content_generator.py` + `site_builder.py` (JSON fill + HTML template) with a Gemini-powered builder that writes actual Astro site files, following SiteForge's proven workflow.

### 2a. Planner (ghostwrite prompt from social content)

Port SiteForge's planner pattern, adapted for social-only data:

1. Gather context:
   - Business metadata (name, category, address, phone, city)
   - Scraped captions (FB + IG), sorted by engagement
   - Image manifest (filename, source, basic description)
   - Google Maps data (rating, review count, hours if available)

2. Gemini Flash generates a **ghostwritten prompt** — a natural first-person request as if the owner is asking for a website. 300-500 words.

3. Save to `site-data/{slug}/site-brief.md`

**Prompt for Gemini (system)**:
```
You are ghostwriting a prompt that a small business owner will use to
ask an AI to build their website. Write as the owner — first person,
conversational. "I run X, we do Y, I need a site that..."

Include: who they are, what they do, their real services (from the
social posts), their address/phone, and what kind of vibe their brand
has. Do NOT invent services or details not in the provided content.

Output ONLY the ghostwritten prompt. No preamble.
```

### 2b. Scaffold + Builder

1. **Scaffold**: Create empty Astro project (same as SiteForge):
   - `package.json`, `astro.config.mjs`, `tailwind.config.mjs`
   - `public/images/` (copy scraped images, watermarked "DEMO")
   - `src/pages/`, `src/layouts/`, `src/components/` (empty)

2. **Builder prompt**: Combine the ghostwritten brief with a technical spec:
   - Site-brief.md (the ghostwritten prompt)
   - Image manifest (categorized: hero, team, portfolio, etc.)
   - SEO checklist (title, meta, JSON-LD, alt text, robots.txt)
   - Design guidance (industry-appropriate palette, varied layouts)

3. **Gemini generates file contents**: Instead of Claude Code CLI writing files, Gemini Flash returns a structured response with file contents:

```json
{
  "files": [
    {"path": "src/layouts/Layout.astro", "content": "..."},
    {"path": "src/pages/index.astro", "content": "..."},
    {"path": "src/pages/about.astro", "content": "..."},
    {"path": "src/pages/contact.astro", "content": "..."},
    {"path": "src/components/Hero.astro", "content": "..."},
    {"path": "src/components/Footer.astro", "content": "..."},
    {"path": "public/robots.txt", "content": "..."}
  ]
}
```

4. **Write files + build**: Write each file to the scaffold, run `npm install && npm run build`. If build fails, send the error back to Gemini for a fix attempt (max 2 retries).

### 2c. Why this might work

- Gemini 2.5 Flash is good at code generation (Astro/Tailwind are well-represented in training data)
- The ghostwritten prompt forces Gemini to understand the business before generating code
- Structured JSON output with file paths is more reliable than asking Gemini to use CLI tools
- The build step (Astro compile) catches errors — bad code won't ship
- Cost: ~$0.01-0.05/site vs ~$2-5/site with Claude Code

### 2d. Why this might NOT work

- Gemini may produce generic/repetitive designs across sites
- Context window pressure: ghostwritten prompt + image manifest + technical spec + all file contents in one response is a lot
- No iterative refinement — Claude Code can look at what it built and fix issues; Gemini gets one shot (plus retries)
- Tailwind CDN vs proper Astro+Tailwind integration may trip it up

---

## Phase 3: Evaluation

### 3a. Test matrix

Run the builder on 5-10 leads with varying content quality:

| Lead | Category | Content Score | FB Posts | IG Posts | Images |
|------|----------|--------------|----------|----------|--------|
| A    | Restaurant | 30+ | 10+ | 5+ | 8+ |
| B    | Plumber | 20-30 | 5-10 | 0 | 3-5 |
| C    | Bar | 15-20 | 3-5 | 2-3 | 2-3 |
| D    | Salon | 15+ | 0 | 10+ | 5+ |
| E    | Various | <15 | 1-2 | 0 | 0-1 |

Lead E should be caught by the content gate and get the no-demo email.

### 3b. Quality checklist (per generated site)

- [ ] Site builds without errors (`npm run build` succeeds)
- [ ] Content is factually accurate (no hallucinated services/locations)
- [ ] Design looks professional (not a homework template)
- [ ] Each site feels unique (not cookie-cutter)
- [ ] Images are used appropriately (hero, gallery, not broken)
- [ ] Mobile responsive
- [ ] Contact info is correct (address, phone)
- [ ] JSON-LD schema present
- [ ] Meta tags (title, description) are real, not placeholder
- [ ] Footer has SiteSmyth branding + CTA

### 3c. Decision criteria

**Ship Gemini builder if**: 7/10 sites pass the quality checklist, content is accurate, and designs don't look identical.

**Fall back to Claude Code if**: Sites are generic/ugly, content keeps hallucinating, or build failures exceed 30%.

---

## Phase 4: If Gemini Fails — Claude Code Fallback

Port SiteForge's builder directly:
- `claude -p {prompt} --allowedTools Edit,Write,Bash --model sonnet --max-turns 30`
- Same scaffold, same prompts, proven quality
- Higher cost ($2-5/site) but $1,000/sale covers it easily
- Already battle-tested in SiteForge

---

## Implementation Order

```
Week 1:
  ├── Phase 1: Content gate + no-demo email
  │   ├── Add content_score to DB
  │   ├── Score leads after scrape
  │   ├── No-demo email template
  │   └── Pipeline routing (score >= 15 → generate, else → no-demo email)
  │
  └── Phase 2a: Planner (ghostwrite prompt)
      ├── Port ghostwrite system prompt (adapted for social data)
      ├── Build context from scraped content + metadata
      └── Save site-brief.md per lead

Week 2:
  ├── Phase 2b: Gemini code builder
  │   ├── Scaffold generator (empty Astro project)
  │   ├── Image watermarking + manifest
  │   ├── Builder prompt (brief + spec + manifest)
  │   ├── Gemini structured output → file writer
  │   └── Build + retry loop
  │
  └── Phase 3: Evaluate on 5-10 real leads
      ├── Run pipeline end-to-end
      ├── Score against quality checklist
      └── Ship or pivot to Phase 4

Week 3 (if needed):
  └── Phase 4: Claude Code fallback
      ├── Port SiteForge builder.py
      ├── Wire into SiteSmyth pipeline
      └── Re-evaluate
```

## Cost Comparison

| Approach | Per-Site Cost | Quality | Speed |
|----------|-------------|---------|-------|
| Current (Gemini JSON + template) | ~$0.001 | Bad | 10s |
| Gemini Code Builder (this test) | ~$0.01-0.05 | TBD | 30-60s |
| Claude Code (SiteForge) | ~$2-5 | Great | 3-5 min |

At $1,000/sale, even the Claude Code approach is viable. But if Gemini can get 80% of the quality at 1% of the cost, that's the winner for cold outreach demos.
