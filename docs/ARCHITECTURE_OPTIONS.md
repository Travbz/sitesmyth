# SiteSmyth: Architecture Options

Two viable paths forward for site generation. This doc captures the tradeoffs so we can make a deliberate choice.

---

## Context: The Inspiration

SiteSmyth was inspired by a viral post describing a cheap pipeline:

> Use Gemini Flash vision model — pennies to rank 100 sites. Scrape Google Maps with Apify. Find companies that don't have websites. Find them on Facebook, check if they're active, and text them a link to sell them a website. Create a few dozen templates and use Gemini Flash to fill the content and images.

We built SiteSmyth to do exactly this. The discovery and scraping pipeline works well. The problem is site generation quality — fixed HTML templates + Gemini JSON fill produces sites that look cheap and hallucinate content.

Meanwhile, SiteForge (our decommed tool) already solves this problem with Claude Code CLI generating full Astro sites from scratch. The sites are beautiful and accurate. But it costs $2-5/site.

---

## Option A: Gemini Code Builder (cheap, unproven)

**Detailed in**: `GEMINI_BUILDER_ROADMAP.md`

Replace template fill with Gemini 2.5 Flash generating actual Astro source files. Same workflow as SiteForge (scaffold + ghostwritten prompt + image manifest) but Gemini writes the code instead of Claude Code CLI.

| Dimension | Assessment |
|-----------|-----------|
| Cost per site | ~$0.01-0.05 |
| Quality | Unknown — needs testing |
| Risk | Gemini may produce generic/repetitive designs, hallucinate content |
| Speed | 30-60s per site |
| Maintenance | New builder code to maintain |

**Best if**: Gemini Flash can actually produce decent multi-file Astro sites from a prompt. Worth testing before committing to the more expensive path.

---

## Option B: Merge SiteSmyth Discovery into SiteForge (proven, pricier)

Keep SiteSmyth's discovery/scraping pipeline (the part that works) and feed it into SiteForge's proven builder.

### What SiteSmyth contributes
- Google Maps/Places discovery of businesses **without websites**
- Social profile finder (FB/IG from business name)
- Activity checker (is their FB/IG actually active?)
- FB + IG content scraping via Apify
- R2 hosting + Worker serving on subdomains
- Cold outreach (email, IG DM queue)
- Content gate (skip low-content leads)

### What SiteForge contributes
- Claude Code CLI builder (beautiful, unique sites every time)
- Ghostwrite planner (natural first-person prompt from context)
- Image watermarking + categorization
- Site-brief.md workflow (planner → builder handoff)
- Proven Astro + Tailwind output quality
- Build verification (npm run build + retry)

### Integration path

```
SiteSmyth pipeline (keep):
  Discovery (Maps/Places) → Social Finder → Activity Check → Scrape (FB/IG)

SiteForge builder (port):
  Planner (ghostwrite from scraped social content) → Builder (Claude Code CLI)

SiteSmyth hosting + outreach (keep):
  Upload to R2 → Serve via Worker → Email/DM outreach
```

Changes needed:
1. Port `planner.py` and `builder.py` from SiteForge into SiteSmyth
2. Adapt planner context builder for social data (FB captions + IG posts instead of scraped website content)
3. Port `ghostwrite-prompt.md` and `site-brief.md` prompts
4. Add `ANTHROPIC_API_KEY` to config
5. Wire into SiteSmyth pipeline: after scrape → plan → build → upload → outreach
6. Keep Gemini for any vision/scoring tasks (cheap), Claude Code for building (quality)

| Dimension | Assessment |
|-----------|-----------|
| Cost per site | ~$2-5 (Claude Code) |
| Quality | Proven excellent |
| Risk | Low — already works in SiteForge |
| Speed | 3-5 min per site |
| Maintenance | Porting effort, then stable |

**Best if**: We want guaranteed quality now. $1,000/sale easily absorbs $5/site cost. The discovery pipeline is the real value — finding leads with no website but active social is the hard part. Building pretty sites is a solved problem.

---

## Option C: Hybrid (test Gemini first, fallback to SiteForge)

This is the `GEMINI_BUILDER_ROADMAP.md` approach with Phase 4 as the escape hatch.

1. Build the content gate (Phase 1) — useful regardless of builder choice
2. Test Gemini code builder on 5-10 leads
3. If quality is good enough (7/10 pass checklist) → ship Gemini builder
4. If not → port SiteForge builder, already have the scaffold/prompt infrastructure

**Best if**: We want to be cost-efficient but aren't willing to ship bad demos. Adds ~1 week vs going straight to Option B.

---

## Recommendation

**Start with Option C** (hybrid). The content gate is needed no matter what, and testing Gemini costs almost nothing. If Gemini fails the quality bar, pivot to Option B — the planner/prompt infrastructure built for Gemini transfers directly to the Claude Code builder.

The discovery + scraping pipeline is the real competitive advantage. The builder is a commodity — we just need one that's good enough to not embarrass us in cold outreach.
