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

// Website elements a client can opt into. One list feeds /services/website-features/,
// the portfolio tags, and the sitesmyth-build skill. "proof" is the WORK slugs whose live
// site has the element; every claim here was checked against that site's code.
export type SiteElement = {
  slug: string;
  name: string;
  what: string;
  runsOn: 'free' | 'service';
  proof: string[];
};

export const ELEMENTS: SiteElement[] = [
  { slug: 'contact-forms', runsOn: 'free', proof: ['respondyr'], name: 'Contact and intake forms',
    what: 'Forms that ask what your business needs to know, save every submission, and email it to you as it arrives. The quote form on this site works this way.' },
  { slug: 'photo-galleries', runsOn: 'free', proof: ['loos-and-sons'], name: 'Photo galleries',
    what: 'Your own job photos, sorted into categories visitors can filter.' },
  { slug: 'menu-pages', runsOn: 'free', proof: ['tipsy-trout'], name: 'Menu pages',
    what: 'Every dish and price as real text with menu markup search engines can read, plus a page for each signature item.' },
  { slug: 'click-to-call', runsOn: 'free', proof: ['loos-and-sons', 'elevation-fire'], name: 'Click-to-call and emergency bars',
    what: 'A call button that stays on screen on phones, and a banner for emergency service.' },
  { slug: 'free-tools', runsOn: 'free', proof: ['respondyr'], name: 'Calculators and free tools',
    what: 'Small tools your customers use right in the browser. They answer a question and bring in search traffic.' },
  { slug: 'blog', runsOn: 'free', proof: ['elevation-fire', 'respondyr'], name: 'A blog',
    what: 'A blog built into your site, ready for you to post articles.' },
  { slug: 'lead-tracking', runsOn: 'free', proof: ['respondyr'], name: 'Visitor and lead tracking',
    what: 'Analytics that show where visitors come from and which pages turn them into leads.' },
  { slug: 'interactive-design', runsOn: 'free', proof: [], name: 'Interactive design',
    what: 'Pages that respond to the cursor, to hover, and to scrolling, built light enough to stay fast. Move your cursor around this page.' },
  { slug: 'immersive-experience', runsOn: 'free', proof: [], name: 'Immersive experience',
    what: 'A site built as a story visitors move through: a hero film that plays once and holds its final frame, and scenes that unfold as you scroll. Custom scene video is produced for your site and adds to the build.' },
  { slug: 'search-markup', runsOn: 'free', proof: ['loos-and-sons', 'elevation-fire', 'tipsy-trout', 'respondyr'], name: 'Search and AI-ready markup',
    what: 'Structured data on every page, so Google and AI search tools read your services and service area correctly.' },
  { slug: 'online-booking', runsOn: 'service', proof: ['loos-and-sons'], name: 'Online booking',
    what: 'Customers book a visit or sign up for a maintenance plan through the scheduling software you already use.' },
  { slug: 'chat-and-text', runsOn: 'service', proof: ['loos-and-sons'], name: 'Chat and text widget',
    what: 'A chat bubble that lets visitors text your business from any page.' },
  { slug: 'job-applications', runsOn: 'service', proof: ['respondyr'], name: 'Job applications with file uploads',
    what: 'Applicants send their answers and a resume, delivered to your inbox.' },
  { slug: 'logins-and-backends', runsOn: 'service', proof: [], name: 'Logins, accounts, and simple backends',
    what: 'Customer logins, member areas, and small databases for sites that need to do more than show pages.' },
];

// Monthly SEO and ad management: its own service and its own monthly contract, separate from
// any website build. Feeds /services/monthly-seo-and-ads/.
export const MONTHLY = [
  { slug: 'search-indexing', h2: 'Getting your site indexed on Google and Bing',
    p: 'A new website does not show up in search until the search engines know it exists. We verify your site in Google Search Console and Bing Webmaster Tools, submit your sitemap to both, link the site to your Google Business Profile, and check that every page gets indexed.' },
  { slug: 'local-seo', h2: 'Ongoing local SEO',
    p: 'Each month we look at which searches bring people to your site, fix what keeps pages from showing up, and add pages for the searches you are missing.' },
  { slug: 'google-ads', h2: 'Google Ads management',
    p: 'Search ads for the services and towns you want more work in, set up and adjusted every month, with tracking that shows which ads turn into leads.' },
  { slug: 'meta-ads', h2: 'Facebook and Instagram ads',
    p: 'Meta ads shown to people in your service area, run and adjusted every month.' },
  { slug: 'ai-search', h2: 'AI search optimization (AEO and GEO)',
    p: 'Make your business easy for ChatGPT, Google AI Overviews, and Copilot to understand and cite, as its own job separate from traditional SEO.' },
];

// One page per searchable feature and per monthly service. Copy states only what the
// portfolio code shows or what is generally true of the work; no invented claims.
export type DetailPage = { title: string; h1: string; description: string; sections: { h2: string; p: string }[] };

export const FEATURE_PAGES: Record<string, DetailPage> = {
  'contact-forms': {
    title: 'Website Contact and Intake Forms for Small Businesses',
    h1: 'Contact and intake forms for small business websites',
    description: 'Website forms that ask what your business needs to know, save every lead, and email it to you the moment it arrives. No form service required.',
    sections: [
      { h2: 'What an intake form does', p: 'A contact form takes a name and a message. An intake form asks what you need before you call back: the service, where the customer is, and how soon they need it. You get a lead you can price instead of a voicemail you have to chase.' },
      { h2: 'How it works on a static site', p: 'The form sends to a small piece of code on the same Cloudflare account as your site. Every submission is saved there and emailed to you with the customer set as the reply-to, so answering a lead is one click. A hidden trap field filters out most spam bots before they reach your inbox.' },
      { h2: 'What it costs to run', p: 'Nothing extra. Saving leads and sending the emails both fit inside free plans at a small business volume.' },
    ],
  },
  'online-booking': {
    title: 'Online Booking on Your Small Business Website',
    h1: 'Online booking for small business websites',
    description: 'Let customers book a visit from your website through the scheduling software you already use, like Housecall Pro, with a book button on every page.',
    sections: [
      { h2: 'Book from any page', p: 'A Book online button sits in the header and in the sticky bar on phones, so a customer who is ready never has to hunt for it. On the Loos & Sons HVAC site it opens their Housecall Pro booking page, and customers enroll in the maintenance plan the same way.' },
      { h2: 'Uses the software you already have', p: 'Booking runs inside your scheduling software, so appointments land on the same calendar your team already works from. We connect the site to it; we do not replace it.' },
      { h2: 'What it costs to run', p: 'Your scheduling software charges its own monthly fee. The website side adds nothing.' },
    ],
  },
  'photo-galleries': {
    title: 'Photo Galleries for Contractor and Small Business Websites',
    h1: 'Photo galleries for small business websites',
    description: 'Show your real work in a photo gallery sorted into categories customers can filter. Your own job photos, not stock.',
    sections: [
      { h2: 'Your work, sorted', p: 'Customers want to see jobs like theirs. A filterable gallery lets them tap a category and see only that kind of work. The Loos & Sons HVAC gallery holds 43 job photos with filters for AC, ductless, furnaces, boilers and radiant, geothermal, water heaters, and service.' },
      { h2: 'Built to stay fast', p: 'Every photo is sized and compressed for the web, so a large gallery does not slow the rest of the site down.' },
      { h2: 'What it costs to run', p: 'Nothing extra. The gallery is part of the site.' },
    ],
  },
  'menu-pages': {
    title: 'Restaurant Menu Pages Google Can Read',
    h1: 'Restaurant and food truck menu pages',
    description: 'Menu pages with every dish and price as real text, menu markup search engines can read, and a page of its own for each signature item.',
    sections: [
      { h2: 'Real text, not a PDF', p: 'A menu posted as a photo or a PDF is hard to read on a phone and invisible to search. A typed menu page loads fast, reads well on any screen, and lets search engines see what you serve and what it costs.' },
      { h2: 'A page for each signature dish', p: 'On The Tipsy Trout Taproom site, each of the six El Pollo dishes has its own page, so someone searching for a dish can land right on it. The menu shows cash and card prices side by side.' },
      { h2: 'Menu markup', p: 'Menu, section, and item markup gives search engines the names and prices on the page in a form they read directly.' },
      { h2: 'What it costs to run', p: 'Nothing extra. Menu pages are part of the site.' },
    ],
  },
  'chat-and-text': {
    title: 'Website Chat and Text Widget for Small Businesses',
    h1: 'Chat and text widgets for small business websites',
    description: 'A chat bubble that lets visitors text your business from any page of your website, through the messaging tool you already use.',
    sections: [
      { h2: 'Text from any page', p: 'Plenty of customers would rather text than call. A chat bubble on every page lets them send a message without leaving the site. Loos & Sons HVAC runs a Podium widget across their whole site.' },
      { h2: 'Messages land where you already work', p: 'Messages go into the messaging tool you already pay for, so your team answers them the same way it answers every other text.' },
      { h2: 'What it costs to run', p: 'The messaging tool charges its own monthly fee. The website side adds nothing.' },
    ],
  },
  'interactive-design': {
    title: 'Interactive Website Design for Small Businesses',
    h1: 'Interactive website design that stays fast',
    description: 'Websites that respond to the cursor, to hover, and to scrolling, built in SolidJS and plain CSS so they stay fast on phones.',
    sections: [
      { h2: 'Pages that react', p: 'Parts of the page respond as visitors move: a highlight that follows the cursor, tiles that answer when touched, headings that draw in as they scroll into view. This site works that way. Move your cursor across it.' },
      { h2: 'Fast first', p: 'The effects sit on top of plain pages. Text and links are there before any effect loads, phones get the same site without cursor effects, and visitors who turn motion off get a still, finished page.' },
      { h2: 'What it costs to run', p: 'Nothing extra. It is part of the build and runs on the same free hosting.' },
    ],
  },
  'immersive-experience': {
    title: 'Immersive Website Design for Small Businesses',
    h1: 'Immersive website design',
    description: 'A website built as a story: a hero film that plays once and holds its final frame, and scenes that unfold as visitors scroll.',
    sections: [
      { h2: 'A site that tells a story', p: 'Instead of a stack of sections, the page moves like a short film. The opening scene plays once and stops on its strongest frame, and later scenes reveal themselves as the visitor scrolls.' },
      { h2: 'Animation that stops', p: 'Every animation plays once and holds. Nothing loops in the background or fights the content for attention, and the page stays readable the whole way down.' },
      { h2: 'What it costs', p: 'Custom scene video is produced for your site, which adds to the build. Once it is made, it runs on the same free hosting as the rest of the site.' },
    ],
  },
};

// Respondyr is Travis's own company: always disclose it as a sister company (FTC endorsement
// rules). Plan contents checked against Respondyr's plans.ts; no dollar figures.
export const RESPONDYR_PAGE: DetailPage = {
  title: 'Google Review Responses and Map Rankings with Respondyr',
  h1: 'Google review responses and map rankings with Respondyr',
  description: 'Our sister company Respondyr answers every Google review in your voice and helps your business climb the map results. We recommend it for every local business.',
  sections: [
    { h2: 'Your website and the map are two different races', p: 'A well-built website helps you rank in the regular search results. The map results are driven by your Google Business Profile, and reviews are a big part of it. Google\'s own guidance on improving local ranking tells businesses to respond to their reviews.' },
    { h2: 'What Respondyr does', p: 'Every plan answers each new Google review automatically, in your voice. Higher plans add review requests to happy customers, reports on what customers are saying, rank tracking on the map, and suggestions for your Google Business Profile.' },
    { h2: 'How it fits with your website', p: 'We build the site that turns a visit into a call. Respondyr keeps the profile that earns the visit active. Together they cover both the regular results and the map, which is why we recommend it to every local client.' },
    { h2: 'Prefer a one-time consult?', p: 'If you would rather not use Respondyr, we also do one-off consults on your Google Business Profile and reviews. Ask for one through the quote form.' },
  ],
};

export const MONTHLY_PAGES: Record<string, DetailPage> = {
  'search-indexing': {
    title: 'Get Your Website Indexed on Google and Bing',
    h1: 'Website indexing on Google and Bing',
    description: 'We verify your site in Google Search Console and Bing Webmaster Tools, submit your sitemap to both, and check that every page gets indexed.',
    sections: [
      { h2: 'Why a new site does not show up', p: 'Search engines find new sites slowly on their own. Until a page is indexed it cannot appear in results, no matter how good it is.' },
      { h2: 'What we do', p: 'We verify your site in Google Search Console and Bing Webmaster Tools, submit your sitemap to both, link the site to your Google Business Profile, and check each page until every page you want found is indexed.' },
      { h2: 'Why Bing matters too', p: 'Bing runs its own search results, and its index also feeds Microsoft Copilot. Skipping it leaves those searches to someone else.' },
    ],
  },
  'local-seo': {
    title: 'Ongoing Local SEO for Small Businesses',
    h1: 'Ongoing local SEO for small businesses',
    description: 'Monthly local SEO: see which searches bring customers in, fix what keeps pages from ranking, and add pages for the searches you are missing.',
    sections: [
      { h2: 'Ranking is not a one-time job', p: 'Competitors publish new pages, search habits shift, and rankings slip. Staying ranked takes steady work.' },
      { h2: 'What happens each month', p: 'We look at which searches bring people to your site, fix what keeps pages from showing up, and add pages for the searches you are missing, like a service or a town you do not have a page for yet.' },
    ],
  },
  'google-ads': {
    title: 'Google Ads Management for Small Businesses',
    h1: 'Google Ads management for small businesses',
    description: 'Google search ads for the services and towns you want more work in, set up and adjusted every month, with tracking that shows which ads become leads.',
    sections: [
      { h2: 'Ads where customers are searching', p: 'Search ads put your business at the top of the results for the services and towns you choose, at the moment someone searches for them.' },
      { h2: 'Managed every month', p: 'We set up the campaigns, then adjust keywords, budgets, and ads every month based on what turns into leads.' },
      { h2: 'Tracking that shows what works', p: 'Conversion tracking shows which ads lead to form submissions, so your budget moves toward what works.' },
      { h2: 'Ad spend', p: 'What you spend on clicks is paid to Google directly, separate from the management fee.' },
    ],
  },
  'meta-ads': {
    title: 'Facebook and Instagram Ads for Local Businesses',
    h1: 'Facebook and Instagram ads for local businesses',
    description: 'Meta ads shown to people in your service area, set up and adjusted every month.',
    sections: [
      { h2: 'Reach people before they search', p: 'Search ads catch people who are already looking. Facebook and Instagram ads reach people in your area before they need you, so yours is the name they remember when they do.' },
      { h2: 'Managed every month', p: 'We set up campaigns aimed at your service area and adjust them every month based on results.' },
      { h2: 'Ad spend', p: 'Ad spend is paid to Meta directly, separate from the management fee.' },
    ],
  },
  'ai-search': {
    title: 'AI Search Optimization (AEO and GEO) for Small Businesses',
    h1: 'AI search optimization (AEO and GEO) for small businesses',
    description: 'Help AI search tools like ChatGPT, Google AI Overviews, and Copilot understand and cite your business, as its own job separate from traditional SEO.',
    sections: [
      { h2: 'Search is not just a list of links anymore', p: 'More people ask an AI tool for a recommendation instead of scrolling results. Those tools answer from what they can read and trust about your business.' },
      { h2: 'What the work covers', p: 'Structured data that spells out your services and service area, pages written so each section answers one question on its own, a plain-text summary of the business for AI crawlers, and business details that match everywhere they appear online.' },
      { h2: 'How it differs from SEO', p: 'Traditional SEO aims for a ranking position. AI search work aims to make yours the business an AI tool names when someone asks. The two overlap, and we treat them as separate jobs.' },
    ],
  },
};

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
