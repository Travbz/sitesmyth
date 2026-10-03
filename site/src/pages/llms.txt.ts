// Plain-text summary of SiteSmyth for AI crawlers, generated from site.ts on every build
// so it never drifts from the pages.
import {
  SITE, HOME, SERVICES, ELEMENTS, FEATURE_PAGES, MONTHLY, MONTHLY_GROUPS, MONTHLY_PAGES,
  AI_SEARCH_PAGE, RESPONDYR_PAGE, SERVICES_FAQ, WORK,
} from '../data/site';

const u = (path: string) => `${SITE.url}${path}`;

export function GET() {
  const lines = [
    `# ${SITE.name}`,
    '',
    `> ${SITE.description}`,
    '',
    HOME.lede,
    '',
    '## Website design (one-time projects)',
    '',
    ...SERVICES.map((s) => `- [${s.h1}](${u(`/services/${s.slug}/`)}): ${s.description}`),
    '',
    '## Website features',
    '',
    `- [All website features](${u('/services/website-features/')})`,
    ...ELEMENTS.map((e) => {
      const link = FEATURE_PAGES[e.slug] ? u(`/services/website-features/${e.slug}/`) : u(`/services/website-features/#${e.slug}`);
      return `- [${e.name}](${link}): ${e.what}`;
    }),
    '',
    '## Ongoing marketing (each on its own monthly contract, separate from any website build)',
    '',
    ...Object.entries(MONTHLY_GROUPS).flatMap(([k, g]) => [
      `- [${g.h1}](${u(`/services/${k}/`)}): ${g.description}`,
      ...g.items.map((slug) => {
        const m = MONTHLY.find((x) => x.slug === slug)!;
        return `  - [${MONTHLY_PAGES[slug]?.h1 ?? m.h2}](${u(`/services/${k}/${slug}/`)}): ${m.p}`;
      }),
    ]),
    `- [${AI_SEARCH_PAGE.h1}](${u('/services/ai-search-optimization/')}): ${AI_SEARCH_PAGE.description}`,
    `- [${RESPONDYR_PAGE.h1}](${u('/services/google-reviews-respondyr/')}): ${RESPONDYR_PAGE.description}`,
    '',
    '## Websites we have built',
    '',
    ...WORK.map((w) => `- [${w.name}](${w.url}): ${w.kind}, ${w.place}. ${w.summary}`),
    '',
    '## Questions',
    '',
    ...SERVICES_FAQ.flatMap((f) => [`### ${f.q}`, '', f.a, '']),
    '## Contact',
    '',
    `- [Get a website quote](${u('/contact/')})`,
    `- [How website ownership works](${u('/own-your-website/')})`,
    '',
  ];
  return new Response(lines.join('\n'), { headers: { 'content-type': 'text/plain; charset=utf-8' } });
}
