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

export const WORK: Work[] = [
  {
    slug: 'loos-and-sons',
    name: 'Loos & Sons HVAC',
    url: 'https://loosandsonshvac.com/',
    domain: 'loosandsonshvac.com',
    kind: 'HVAC contractor',
    place: 'Longmont, Colorado',
    pages: 'About 40 pages',
    summary:
      'Their old site went down for good. The rebuild gave every system they work on its own page and gave each town they drive to a page written for that town.',
    built: [
      'A page for each service, from furnace repair to geothermal',
      'Twenty town pages, each written about that town',
      'An Xcel Energy heat pump rebate page',
      'A filterable gallery of real job photos',
    ],
  },
  {
    slug: 'elevation-fire',
    name: 'Elevation Fire Protection',
    url: 'https://elevationfireprotection.com/',
    domain: 'elevationfireprotection.com',
    kind: 'Fire sprinkler contractor',
    place: 'Denver, Colorado',
    pages: 'About 40 pages',
    summary:
      'A commercial fire sprinkler contractor working across Colorado and Wyoming. The site is built around the searches building owners and general contractors actually run.',
    built: [
      'Service pages for installation, inspection, testing, and repair',
      'Location pages for the areas they cover',
      'Pages aimed at specific Denver searches, like fire pump testing',
      'A blog with over twenty articles',
    ],
  },
  {
    slug: 'tipsy-trout',
    name: 'The Tipsy Trout Taproom',
    url: 'https://tipsytrouttaproom.com/',
    domain: 'tipsytrouttaproom.com',
    kind: 'Taproom and food truck',
    place: 'Delta, Colorado',
    pages: '8 pages',
    summary:
      'A beach bar a long way from any beach. The site leans into that with a 1970s surf look, and the food truck menu got real pages with real prices.',
    built: [
      'A custom retro surf design',
      'A full menu page for the El Pollo truck',
      'Its own page for each signature dish',
      'Menu item schema so search engines read the prices',
    ],
  },
  {
    slug: 'v-sandoval',
    name: 'V Sandoval Cleaning',
    url: 'https://vsandovalcleaning.com/',
    domain: 'vsandovalcleaning.com',
    kind: 'House cleaning',
    place: 'Montrose, Colorado',
    pages: 'One page',
    summary:
      'A single landing page that says what they clean, where they go, and how to book. Sometimes one good page is the whole job.',
    built: [
      'One focused landing page',
      'Services and service towns in plain view',
      'A booking call to action on every screen',
    ],
  },
  {
    slug: 'respondyr',
    name: 'Respondyr',
    url: 'https://respondyr.com/',
    domain: 'respondyr.com',
    kind: 'Software company',
    place: 'Review management software',
    pages: 'Over 100 pages',
    summary:
      'The marketing site for a review management product. Feature pages, free tools, and a blog that publishes every week.',
    built: [
      'Feature and pricing pages',
      'Free tools that bring in search traffic',
      'A blog with seventy-plus posts',
    ],
  },
];

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

export type Industry = {
  slug: string;
  short: string;
  title: string;
  h1: string;
  description: string;
  intro: string;
  needs: { h: string; p: string }[];
  examples: string[];
};

export const INDUSTRIES: Industry[] = [
  {
    slug: 'hvac-companies',
    short: 'HVAC companies',
    title: 'HVAC Website Design',
    h1: 'Website design for HVAC companies',
    description:
      'HVAC websites with a page for every system you service and every town you drive to. Built to bring in calls, and owned by you.',
    intro:
      'People search for HVAC help when something stops working. They search by the problem and by their town, and the company with a page for both gets the call.',
    needs: [
      { h: 'A page per system', p: 'Furnaces, AC, heat pumps, boilers, water heaters. Each one is its own search, so each one gets its own page.' },
      { h: 'Town pages that say something', p: 'Older homes in one town, new builds in the next, mountain propane in a third. The page should know the difference.' },
      { h: 'Rebates and emergencies', p: 'Utility rebate pages and emergency service pages catch people who are ready to book today.' },
      { h: 'Your real job photos', p: 'A gallery of your own work does more for trust than any stock photo.' },
    ],
    examples: ['loos-and-sons'],
  },
  {
    slug: 'fire-protection-contractors',
    short: 'Fire protection',
    title: 'Fire Sprinkler Contractor Website Design',
    h1: 'Website design for fire sprinkler and fire protection contractors',
    description:
      'Websites for fire sprinkler contractors that rank for inspections, testing, and installation searches, built for property managers and general contractors.',
    intro:
      'Your customers are property managers, facility teams, and general contractors. They search for a specific job, like an annual inspection or a fire pump test, in a specific city.',
    needs: [
      { h: 'Pages for each inspection and test', p: 'Annual inspections, pump testing, backflow, and repairs are separate searches with separate buyers.' },
      { h: 'Coverage you can prove', p: 'Location pages for the regions you work, written for the buildings and codes there.' },
      { h: 'A path for general contractors', p: 'Builders looking for a sprinkler sub need to see your project experience fast.' },
      { h: 'Articles that answer code questions', p: 'A blog that answers what facility managers ask keeps bringing them back.' },
    ],
    examples: ['elevation-fire'],
  },
  {
    slug: 'restaurants-and-bars',
    short: 'Restaurants and bars',
    title: 'Restaurant and Bar Website Design',
    h1: 'Websites for restaurants, bars, and food trucks',
    description:
      'Restaurant and bar websites with real menu pages, prices, and hours, designed to feel like your place. Built fast for people deciding where to eat right now.',
    intro:
      'Someone deciding where to eat has a phone in one hand and about thirty seconds. They want the menu, the prices, and where you are.',
    needs: [
      { h: 'A menu people can read', p: 'Real text, not a PDF or a photo of a printed menu, so it works on a phone and shows up in search.' },
      { h: 'Pages for signature dishes', p: 'People search for the dish they are craving. A page for your best items catches those searches.' },
      { h: 'A look that matches the room', p: 'Your site should feel like walking in the door, not like every other restaurant template.' },
      { h: "What's on this week", p: 'Events, live music, and specials, in a place that is easy to keep up to date.' },
    ],
    examples: ['tipsy-trout'],
  },
  {
    slug: 'cleaning-companies',
    short: 'Cleaning businesses',
    title: 'Website Design for Cleaning Businesses',
    h1: 'Website design for house cleaning businesses',
    description:
      'A clean, simple website for house cleaning and janitorial businesses that shows your services, the towns you cover, and how to book.',
    intro:
      'Inviting someone into your home takes trust. A clear, professional site that says exactly what you do earns that trust before the first call.',
    needs: [
      { h: 'Services spelled out', p: 'Deep cleans, routine visits, move-in and move-out, and short-term rentals each mean something different to the customer.' },
      { h: 'The towns you cover', p: 'Customers want to know you come to them before they reach out.' },
      { h: 'Booking up front', p: 'A clear way to book on every screen, because that is the whole point of the visit.' },
    ],
    examples: ['v-sandoval'],
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
  lede: 'We build fast websites that show up in search, then hand them over. Your domain, your code, and your hosting stay in your name, so the site is yours the day it launches.',
};
