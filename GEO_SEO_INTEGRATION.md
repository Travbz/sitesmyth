# GEO-SEO Audit Integration

## The Tool

[geo-seo-claude](https://github.com/zubair-trabzada/geo-seo-claude) — a Claude Code skill that runs comprehensive GEO (Generative Engine Optimization) and SEO audits. It scores websites for AI search visibility, citability, schema markup, technical SEO, and content quality.

## Why This Matters for SiteSmyth

We're selling $1,000 websites to local businesses that currently have no website at all. Running a GEO-SEO audit on our generated demo sites gives us two things:

1. **Quality gate**: Automated scoring before we send outreach. If a generated site scores poorly, fix it before the prospect sees it.
2. **Sales proof**: Show the prospect their new site's GEO/SEO scores in the outreach email. "Your demo site scores 85/100 for AI search readiness" is a concrete value prop, not just "we made you a pretty page."

## Integration Plan

### Applies to both pipelines

This isn't SiteSmyth-only. **SiteForge already scores existing sites** with Lighthouse + SpyFu before building replacements. Adding geo-seo-claude to both pipelines creates a before/after comparison that neither tool has today.

| Pipeline | Existing site scoring | Demo site scoring |
|----------|----------------------|-------------------|
| **SiteForge** (has-website leads) | Lighthouse + SpyFu + **GEO audit** | **GEO audit** on built demo |
| **SiteSmyth** (no-website leads) | N/A (no existing site) | **GEO audit** on built demo |

For SiteForge leads: "Your current site scores 32/100 for AI search. Our demo scores 87/100." That's a direct, quantifiable improvement that's hard to argue with.

For SiteSmyth leads: "Your business is invisible to AI search. Your demo site scores 85/100." Different angle, same impact.

### When to run

Run the audit up to **three times** depending on pipeline:

```
┌──────────────────────────────────────────────────────────────┐
│  SiteForge (existing sites):                                 │
│    AUDIT #0 → Score prospect's EXISTING site (before)        │
│    Scrape → Build → AUDIT #1 → Fix → Upload → Outreach      │
│    Compare: existing GEO score vs demo GEO score             │
│                                                              │
│  SiteSmyth (no-website leads):                               │
│    Scrape → Build → AUDIT #1 → Fix → Upload → Outreach      │
│    No "before" score — prospect has no site                  │
│                                                              │
│  Both pipelines:                                             │
│    Audit #1 (post-build, pre-upload):                        │
│      Run on local build output (localhost or file://)        │
│      Score the site, flag issues, auto-fix what we can       │
│      Re-build if needed                                      │
│                                                              │
│    Audit #2 (post-upload):                                   │
│      Run on live URL ({slug}.sitesmyth.com)                  │
│      Verify live scores, catch deployment issues             │
│      Include scores in outreach email                        │
└──────────────────────────────────────────────────────────────┘
```

### SiteForge integration (existing sites)

SiteForge already runs Lighthouse + SpyFu in the scorer step. Adding GEO audit alongside:

1. **Scorer step** (`scorer.py`): After Lighthouse/SpyFu, run geo-seo-claude on the prospect's existing URL. Store GEO score in the `scores` table alongside Lighthouse scores.
2. **Planner step** (`planner.py`): Include GEO audit findings in the ghostwrite context — "their current site has no schema markup, blocks AI crawlers, content isn't citable."
3. **Builder step** (`builder.py`): The site-brief.md already includes SEO checklist. Add GEO-specific requirements: citable content blocks, llms.txt, AI crawler access.
4. **Post-build**: Run GEO audit on the demo. Store score.
5. **Emailer step** (`emailer.py`): Include the comparison in the email context so Claude Code can reference real numbers.

This gives SiteForge a massive outreach upgrade — the email goes from "your Lighthouse score is 28" to "your AI search visibility is 32/100, our demo scores 87/100, and AI search traffic converts 4.4x better than organic."

### What geo-seo-claude checks

| Category | Weight | What it covers |
|----------|--------|----------------|
| AI Citability & Visibility | 25% | Content structured for AI citation (134-167 word blocks, fact-rich, self-contained) |
| Brand Authority Signals | 20% | Brand mentions across YouTube, Reddit, LinkedIn, etc. |
| Content Quality & E-E-A-T | 20% | Readability, expertise signals, freshness |
| Technical Foundations | 15% | Core Web Vitals, SSR, security, mobile |
| Structured Data | 10% | JSON-LD schema (LocalBusiness, etc.) |
| Platform Optimization | 10% | ChatGPT, Perplexity, Google AIO readiness |

### What we care about most for demo sites

For businesses with no website, brand authority (20%) will score low regardless — they have no online presence yet. Focus on what we can control:

- **Citability** (25%): Structure content so AI can cite it. Clear answers to "what does this business do?" in citable blocks.
- **Technical** (15%): Fast, mobile-first, proper meta tags, SSL. Astro static output handles most of this.
- **Structured Data** (10%): JSON-LD LocalBusiness schema with real name, address, phone, hours.
- **Content** (20%): E-E-A-T signals — real business info, not generic filler.
- **Platform** (10%): robots.txt allowing AI crawlers, llms.txt file.

That's 80% of the score we can directly influence in the builder.

### Builder integration

Whichever builder wins (Gemini or Claude Code), add these to the build spec:

1. **AI-citable content blocks**: Each section (about, services, contact) should have a self-contained 134-167 word paragraph that directly answers a question like "What does [business] do?" or "What services does [business] offer?"
2. **llms.txt**: Generate a `/llms.txt` file describing the site structure for AI crawlers
3. **AI crawler access**: `robots.txt` explicitly allows GPTBot, ClaudeBot, PerplexityBot, GoogleOther
4. **Schema depth**: Expand JSON-LD beyond basic LocalBusiness — add `sameAs` (social links), `openingHours`, `areaServed`, `hasOfferCatalog` for services
5. **Meta descriptions**: 150-160 chars, written as answers not marketing fluff ("Stone House Saloon is a live music venue in Montrose, CO" not "Welcome to our amazing venue!")

### Outreach integration

**SiteForge (has existing site):**

> Your current website scores **{{existing_geo_score}}/100** for AI search visibility. That means ChatGPT, Perplexity, and Google AI Overviews can barely find your business.
>
> We built a replacement that scores **{{demo_geo_score}}/100**. Same business, same content — just structured so AI search engines can actually cite you.
>
> See it live: {{demo_url}}

**SiteSmyth (no existing site):**

> Right now, {{business_name}} is invisible to AI search — no website means ChatGPT, Perplexity, and Google AI Overviews have nothing to recommend.
>
> We built a demo site that scores **{{demo_geo_score}}/100** for AI search readiness. Your business shows up when people ask AI for recommendations in {{city}}.
>
> See it live: {{demo_url}}

Both reframe the pitch from "we made you a website" to "we made you visible to AI search." The before/after comparison (SiteForge path) is especially powerful — it's a concrete number attached to a concrete problem.

### Minimum score threshold

- **Score >= 70**: Ship the demo, include score in email
- **Score 50-69**: Auto-fix issues (schema, robots.txt, meta tags), re-audit, ship if improved
- **Score < 50**: Flag for manual review or rebuild

## Installation

The tool installs as a Claude Code skill:

```bash
curl -fsSL https://raw.githubusercontent.com/zubair-trabzada/geo-seo-claude/main/install.sh | bash
```

Requires: Python 3.8+, Claude Code CLI, optional Playwright for screenshots.

## Cost

The audit itself runs through Claude Code, so the cost depends on the builder model choice:
- If we're already using Claude Code for building (Option B), the audit adds marginal cost (~$0.50/audit)
- If using Gemini builder (Option A), we'd need Claude Code just for audits — or port the scoring logic to Python and run it standalone without Claude Code

### Standalone scoring option

The repo includes Python scripts (`citability_scorer.py`, `brand_scanner.py`, `fetch_page.py`) that could run independently without Claude Code. We could:
1. Run the Python scoring scripts directly after build
2. Skip the full Claude Code audit
3. Use Gemini Flash to interpret scores and suggest fixes if needed

This keeps cost near zero while still getting the quality gate.

## Market context

From the [geo-seo-claude README](https://github.com/zubair-trabzada/geo-seo-claude):

| Metric | Value |
|--------|-------|
| GEO services market | $850M+ (projected $7.3B by 2031) |
| AI-referred traffic growth | +527% YoY |
| AI traffic conversion vs organic | 4.4x higher |
| Gartner: search traffic drop by 2028 | -50% |
| Brand mentions vs backlinks for AI | 3x stronger |
| Marketers investing in GEO | Only 23% |

GEO agencies charge $2K-$12K/month. We're offering a $1,000 one-time site that's already GEO-optimized. That's a strong angle for outreach — especially to businesses with zero web presence who are invisible to AI search entirely.
