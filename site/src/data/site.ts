// Every fact on the site lives here. Pages read from this file only.

export const SITE = {
  name: 'SiteSmyth',
  url: 'https://sitesmyth.com',
  tagline: 'Small business websites you own outright',
  description:
    'SiteSmyth builds fast, search-ready websites for small businesses, from one-page landing pages to full sites with service, city, and menu pages. Your GitHub, your Cloudflare, your domain.',
};

export type Work = {
  slug: string;
  name: string;
  url: string;
  domain: string;
  kind: string;
  place: string;
  pages: string;
  summary: string;
  built: string[];
};

// One file per site in src/data/work/<slug>.json. Add a site with
// `node scripts/add-site.mjs <url>`; the file name is the slug.
const workFiles = import.meta.glob<Omit<Work, 'slug'> & { order: number }>('./work/*.json', { eager: true, import: 'default' });

export const WORK: Work[] = Object.entries(workFiles)
  .map(([path, w]) => ({ slug: path.slice(path.lastIndexOf('/') + 1, -5), ...w }))
  .sort((a, b) => a.order - b.order)
  .map(({ order, ...w }) => {
    // A scaffolded entry that was never filled in must not reach the live site.
    if (JSON.stringify(w).includes('TODO')) throw new Error(`src/data/work/${w.slug}.json still has TODO text`);
    return w;
  });

export type Service = {
  slug: string;
  nav: string;
  title: string; // <title>
  h1: string;
  description: string; // meta description
  intro: string;
  forWho: string;
  includes: string[];
  examples: string[]; // WORK slugs
  faqs: { q: string; a: string }[];
};

export const SERVICES: Service[] = [
  {
    slug: 'landing-page-design',
    nav: 'Landing pages',
    title: 'Landing Page Design for Small Businesses',
    h1: 'Landing page design for small businesses',
    description:
      'A one-page website that tells customers what you do, where you work, and how to reach you. Fast, mobile-first, and yours to keep.',
    intro:
      'Plenty of businesses need one page, done well. It says what you do and where you do it, it loads fast on a phone, and it makes calling or booking the obvious next step.',
    forWho:
      'New businesses, businesses with no site at all, and anyone whose site is a Facebook page.',
    includes: [
      'One page, written about your business, not filled from a template',
      'Built for phones first, since that is where most local customers find you',
      'Title, description, and business schema so Google knows what you are',
      'A contact form or click-to-call, whichever your customers use',
      'Your domain connected to your own Cloudflare account',
    ],
    examples: ['v-sandoval'],
    faqs: [
      {
        q: 'Is one page enough to show up on Google?',
        a: 'For your business name and a few core searches, often yes. If you want to rank for each service or each town separately, those need their own pages, and the site can grow into that later.',
      },
      {
        q: 'Can it grow into a bigger site later?',
        a: 'Yes. It is built the same way the larger sites are, so adding service or city pages later does not mean starting over.',
      },
      {
        q: 'What do I need to have ready?',
        a: 'Your services, the towns you cover, your phone number, and any photos of your work. If you have a logo, great. If not, we can work around it.',
      },
    ],
  },
  {
    slug: 'multi-page-websites',
    nav: 'Full websites',
    title: 'Custom Multi-Page Websites for Small Businesses',
    h1: 'Custom multi-page websites for service businesses and restaurants',
    description:
      'Full small business websites with a page for every service, menu item, or location. Hand-built, fast, and handed over to you when it is done.',
    intro:
      'When you do a dozen different jobs, one page cannot rank for all of them. A full site gives each service its own page, written for the people searching for it.',
    forWho:
      'Contractors with many services, restaurants with a real menu, and businesses that cover several towns.',
    includes: [
      'A page for each service, each with its own heading, questions, and photos',
      'Menu pages with real prices for restaurants and food trucks',
      'Gallery pages built from your own job photos',
      'Structured data on every page so search engines read it correctly',
      'A sitemap, clean URLs, and fast load times on every page',
    ],
    examples: ['loos-and-sons', 'elevation-fire', 'tipsy-trout'],
    faqs: [
      {
        q: 'How many pages do I need?',
        a: 'Usually one per service you want customers to find, plus the basics: home, about, and contact. We work that out together before anything gets built.',
      },
      {
        q: 'Can I add pages myself later?',
        a: 'Yes. The site lives in your own GitHub account, so you or anyone you hire can change it.',
      },
      {
        q: 'Do you write the content?',
        a: 'Yes, from what you tell us about your work. You review it before it goes live, and nothing gets published that you have not confirmed is true.',
      },
    ],
  },
  {
    slug: 'local-seo-pages',
    nav: 'Local SEO pages',
    title: 'Service Area and City Pages for Local SEO',
    h1: 'Service area pages that help local customers find you',
    description:
      'City and service area pages written for each town you serve, so your business shows up when people search nearby. No copy-paste doorway pages.',
    intro:
      'If you drive to twenty towns, people in each of those towns are searching for someone like you. A good city page answers for that town, with details that are actually about that town.',
    forWho:
      'Contractors and home service businesses that cover a region, not a single address.',
    includes: [
      'A page for each town you serve, each one written for that town',
      'Pages for searches with real buying intent, like rebates or emergency service',
      'Internal links between services and towns so search engines see the full picture',
      'Schema that tells Google your service area',
    ],
    examples: ['loos-and-sons', 'elevation-fire'],
    faqs: [
      {
        q: 'Why not use one template and swap the town name?',
        a: 'Google treats those as doorway pages and they tend to drag a site down. Every city page here is written about that town: its housing, its weather, its rules.',
      },
      {
        q: 'How many towns should get a page?',
        a: 'The ones you actually serve and want work from. A shorter list of real pages beats a long list of thin ones.',
      },
    ],
  },
  {
    slug: 'website-redesign',
    nav: 'Redesigns',
    title: 'Website Redesign: Move Off Wix, GoDaddy, or WordPress',
    h1: 'Website redesign and migration off Wix, GoDaddy, or WordPress',
    description:
      'Rebuild a slow, broken, or locked-in website as a fast site you own. Your domain, your content, and your search rankings move with you.',
    intro:
      'Website builders are easy until the site breaks, the monthly bill goes up, or you want to leave. A rebuild moves you to a site you own, on hosting that is yours.',
    forWho:
      'Businesses stuck on a site they cannot change, a builder they keep paying for, or a WordPress install nobody maintains.',
    includes: [
      'A new design built around how your customers find you',
      'Your existing content, cleaned up and carried over',
      'Your domain moved to your own Cloudflare account, with email records kept intact',
      'Redirects from old URLs so you keep what you have earned in search',
    ],
    examples: ['loos-and-sons', 'elevation-fire'],
    faqs: [
      {
        q: 'Will my email stop working when the domain moves?',
        a: 'No. Your email records get copied over before anything switches, so mail keeps flowing.',
      },
      {
        q: 'Will I lose my Google rankings?',
        a: 'Old addresses get redirected to the matching new pages, which is how rankings carry over. A faster site with better pages usually helps from there.',
      },
    ],
  },
];

export const STEPS = [
  { h: 'Tell us about the business', p: 'What you do, who you do it for, and where. Send photos of your work if you have them.' },
  { h: 'You set up your accounts', p: 'A GitHub account, a Cloudflare account, and your domain, all in your name. We walk you through it and you add us as a collaborator.' },
  { h: 'We build the site', p: 'You get a private preview link, review every page, and ask for changes until it is right.' },
  { h: 'You pay, it launches, it is yours', p: 'The site goes live on your domain. The code, the hosting, and the domain were yours from the start, so nothing depends on us.' },
];

export const OWNED = [
  { what: 'Your domain', detail: 'Registered in your name, so it can never be held over you.' },
  { what: 'Your GitHub', detail: 'Every line of the site lives in a repository you own.' },
  { what: 'Your Cloudflare', detail: 'Hosting runs on your own account. Most small sites fit in the free plan.' },
];

export const HOME = {
  title: 'Small Business Website Design You Own',
  description:
    'Fast, search-ready websites for small businesses, from one-page sites to full sites with service, city, and menu pages. Your domain, your GitHub, your Cloudflare.',
  h1: 'Small business websites you own outright',
  lede: 'SiteSmyth designs and builds websites for local businesses, then hands them over. Your domain, your code, and your hosting are in your name from day one.',
  body: [
    'Some businesses need one clean page that says what they do and how to reach them. Others need a page for each service, each town they drive to, or each item on the menu, so customers searching for any of those find them. We build both, fast and ready for search.',
    'Before any work starts, you open your own accounts and add us to them. We build the site inside those accounts. When the job is paid, there is nothing to transfer, because it was yours the whole time.',
  ],
  explore: [
    { href: '/work/', label: 'See the sites we have built' },
    { href: '/services/', label: 'What we build' },
    { href: '/own-your-website/', label: 'How the handoff works' },
  ],
};
