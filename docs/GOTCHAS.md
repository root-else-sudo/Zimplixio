# Known Gotchas

Implementation quirks, removed features, and non-obvious constraints. Read this before touching an area you're unfamiliar with.

**Division of labour with `CLAUDE.md`:** that file describes how the project is *put together* — architecture, conventions, what to follow. This file records *traps* — things that will bite you, decisions that look like mistakes but aren't, and features deliberately removed. Where both touch the same subject, `CLAUDE.md` states the rule and this file explains the failure mode behind it.

---

## Static Files & Build

- **STORAGES setting — production uses the NON-manifest backend**: `settings/prod.py` sets `staticfiles` to `whitenoise.storage.CompressedStaticFilesStorage`, not the `Manifest` variant. This is deliberate but was never a design decision — it was swapped in during Railway deploy troubleshooting (commit `6ee21d0`) and kept because it works. Trade-off: without the manifest, filenames are not content-hashed, so WhiteNoise cannot mark assets immutable and serves them with its default `max-age=60` instead of a year. Returning visitors re-fetch CSS/JS (including the React bundle) roughly every minute. Do not "fix" the docs by switching the backend — restoring `CompressedManifestStaticFilesStorage` may break the build, since it fails `collectstatic` with `ValueError: Missing staticfiles manifest entry` if any template or CSS file references a static file that does not exist. If you do restore it, verify `collectstatic` passes first.
- **One React bundle for everything**: `static/dist/framework-accordion.js` (built from `frontend/`) drives both the hub-and-spoke diagram and the assessment wizard. Rebuilding with `cd frontend && npm run build` updates both.
- **No tsParticles / no CDN for hero effect**: The hero animation is pure vanilla JS canvas (ImageData pixel writing). The tsParticles CDN was removed. `cdn.jsdelivr.net` was also removed from the CSP `script-src` directive in `core/middleware.py`.

## Media Storage (Cloudflare R2)

- **Media does not travel between environments**: a showcase image uploaded locally does not exist in production, and vice versa — the two environments write to entirely different backends. `MEDIA_ROOT`/`MEDIA_URL` in `base.py` look authoritative but are unused in prod, since `STORAGES['default']` overrides the backend.
- **Do not re-hardcode the R2 domain in the CSP**: it was hardcoded in `core/middleware.py` until it was made to derive from `settings.AWS_S3_CUSTOM_DOMAIN`. Rotating the bucket while only updating the env var would then have left every image silently blocked, visible as broken images with nothing but a console CSP violation. The helper tolerates the value with or without a scheme and strips a trailing slash, so both `pub-xxx.r2.dev` and `https://pub-xxx.r2.dev/` work.
- **Dev allows no R2 images in CSP**: `AWS_S3_CUSTOM_DOMAIN` is only defined in `prod.py`, so in dev `img-src` is just `'self' data:` — correct, since dev serves media from disk. If you point a local instance at the production bucket, set `AWS_S3_CUSTOM_DOMAIN` locally too or every image will be blocked.
- **R2 env vars have no defaults**: `prod.py` calls `env('R2_ACCESS_KEY_ID')` etc. with no fallback, so a missing variable raises `ImproperlyConfigured` at startup and the app will not boot. Intentional (fail loud), but it means `settings/prod.py` cannot be loaded locally without the full R2 credential set.
- **Nothing cleans up R2 objects**: uploads are never overwritten (`AWS_S3_FILE_OVERWRITE = False` suffixes same-name files) and deleting a `ShowcaseScreenshot` row does not delete the object in the bucket. Orphans accumulate silently.
- **Media is world-readable**: `public-read` ACL with unsigned, unexpiring URLs. Do not put anything non-public behind these fields.

## Database & Performance

- **`CONN_MAX_AGE` must stay set — it is worth ~800ms per request**: `settings/base.py` sets `CONN_MAX_AGE` (default 600, overridable via env) and `CONN_HEALTH_CHECKS = True`. Django's default of `0` opens and tears down a PostgreSQL connection on *every* request. Before this was set, any request touching the database cost ~800ms more than one that did not — identically for JSON endpoints and template renders, so it was clearly connection setup rather than query time. Do not remove these lines or "simplify" them away.
- **The Railway web service and Postgres service must be in the same region**: they were originally split (web in US East / Virginia, Postgres in EU West), so every query crossed the Atlantic at ~85ms per round trip. Page cost scaled with query count — visible as `/contact/` ~192ms vs `/showcase/` ~370ms of database overhead. Moving Postgres to the web service's region removed it entirely. If page loads ever regress site-wide, check region alignment first.
- **Measured impact of the two fixes together** (median, warm connection, `/showcase/` → `/contact/` range): originally 793–1074ms per page → 258–436ms after `CONN_MAX_AGE` → **60–115ms after region alignment**, a 10–16× improvement. Database-attributable overhead is now within measurement noise (−11ms to +44ms against a ~71ms no-DB baseline).
- **How to re-measure**: compare an endpoint that touches the DB against one that does not. `/book/slots/` with no `date` param returns `400` before reaching the ORM, and `/static/css/main.css` is served by WhiteNoise without a Django view — either works as a no-DB baseline. `/book/slots/?date=<future>` runs real queries with no template, which separates database cost from template rendering.
- **`site_context` re-queries `NPSMetric` on every template render**: in `core/context_processors.py`, `cache.set(NPS_CACHE_KEY, active, …)` stores `None` when no active metric exists, and a cached `None` is indistinguishable from a cache miss — so the query runs every time. Harmless now that the database is same-region (~2ms), but it is why *every* page hit the database during the latency investigation. Fix by caching a sentinel if it ever matters again.

## Templates & Django

- **`{% load static %}` in partials**: `_header.html` includes its own `{% load static %}` at the top — required because partials do not inherit the parent template's loaded tags.
- **Hero particle effect — `#hero-particles` div required**: `particles-hero.js` looks for `<div id="hero-particles">` inside the hero `<section>`, styled `position:absolute; inset:0; z-index:1; pointer-events:none` in `main.css`. Ten templates carry it, including `404.html`. The script listens for mousemove on `document` rather than the canvas, precisely because the canvas has `pointer-events:none` — moving that listener onto the canvas silently kills the parallax.
- **HomePageView cross-app query**: `HomePageView` imports `showcase.ShowcaseProject` to fetch `featured_projects` for the homepage — changes to the showcase model can affect the homepage.
- **Stray characters in project-specific templates**: When editing `detail-simple-forecast.html` or `detail.html` manually, watch for stray characters outside `{% block %}` tags — they will be silently rendered into the page.

## Showcase Detail Templates

- **Gallery thumbnails**: Use `object-contain` (not `object-cover`) so icon-style images display fully without cropping.
- **Cross-origin iframe CSRF**: Embedded apps (e.g., recomares.com) that use POST-based actions (like Django `set_language`) will fail in the iframe due to third-party cookie blocking. The "Open in new tab" fallback link is provided.
- **Iframe-embedded showcase apps must allow framing**: Any external app added to the showcase with `live_demo_url` must not send `X-Frame-Options: SAMEORIGIN`. Remove `XFrameOptionsMiddleware` from the embedded app's `MIDDLEWARE` setting to allow cross-origin embedding.
- **Showcase carousel clones require N ≥ visible count**: The carousel clones the first/last N slides (3 desktop, 2 tablet, 1 mobile). With only 3 projects it still works, but sparse if fewer.
- **Showcase carousel auto-play pauses on hover/focus**: Stays paused if the user tabs in and doesn't tab out — intentional for accessibility.

## Design System & CSS

- **Color palette — Tailwind `indigo` remapped**: The `indigo` color scale in `base.html` Tailwind config is overridden to a navy/electric-blue palette (`indigo-600 = #2563eb`, `indigo-800 = #0f2044`, `indigo-900 = #0a1628`). Do not add raw hex values for blue; use `indigo-*` classes.
- **Logo SVG sizing**: `static/images/logo.svg` has no fixed `width`/`height` attributes (removed so CSS controls size). The viewBox is cropped to the content area (`278 337 1656 426`).
- **HPE logo is `HPE-v2.svg`, not `HPE.svg`**: The text paths originally used `fill:#ffffff`, which was invisible on the light homepage background. They are now `fill:#1f2937` (the green icon element, `fill:#00b188`, was never changed). The file was **renamed** as part of that fix because static assets carry no content hash — see "Renaming a static asset is the only cache bust" below.
- **Renaming a static asset is the only reliable cache bust**: WhiteNoise runs `CompressedStaticFilesStorage` (non-manifest), so a static file's URL never changes when its bytes do. Cloudflare then serves it with `cache-control: public, max-age=14400`. Chrome revalidates on a hard refresh, but **Safari does not** — it keeps decoded `<img>` SVGs in a per-process memory cache above the network layer, which the Web Inspector's "Disable Caches" checkbox does not clear. A visitor who loaded the old bytes keeps them indefinitely. When you change a static asset's *appearance*, rename the file and update its `{% static %}` references; editing in place is not enough.
- **Credential logo sizing is per-file**: PayPal/IBM/HPE use `.credential-logo-xl` (280×104px) and Intel uses `.credential-logo` (140×52px) because the SVGs have different native aspect ratios.
- **`.logo-magnetic` on multiple elements**: Applied to the logo `<a>` and desktop "Book a Call" button in `_header.html`. Do not apply to the mobile "Book a Call" (inside the dropdown menu).
- **PDCA section — no GSAP, no JS file**: Pure CSS + AOS only. Do not add JS animation libraries — `cdnjs.cloudflare.com` is not in the CSP `script-src` allowlist.
- **PDCA description reveal is hover-only on desktop**: `.pdca-desc` uses `max-height: 0` → `max-height: 200px` on `:hover`. On mobile (≤767px), descriptions are always visible via CSS override.

## Services Page

- **Two layouts coexist**: Desktop (≥1024px) uses a scroll-pinned horizontal panel layout driven by `services-scroll.js`. Mobile uses a tabbed layout with an inline `zSwitch(index)` function. Both live in `services.html`. Do not use AOS on either section.
- **Five CSS naming prefixes**: `svc-*` (scroll panel chrome), `z-*` (mobile tabbed layout), `vis-*` (deliverable bullet lists), `p01-*`–`p05-*` (animated widget grids), `wte-*` (What to Expect timeline). Do not mix them.
- **Widget color variants use modifier classes**: Colors are BEM-style modifier classes in `main.css` (e.g. `.p01-ms-dot--blue/teal/purple`). Do not use inline styles.
- **No Pricing Signal section**: It was removed. Do not re-add it.

## About Page

- **Founder cards have no `--reverse` variant**: Both cards use photo-left layout. There is no `.founder-card--reverse` class in the HTML or CSS.
- **Values flip cards — hover + click both trigger flip**: CSS `:hover` (desktop) AND JS `.is-flipped` class (click/tap). Do not remove either — hover gives instant desktop response; `.is-flipped` makes it work on touch.

## AI Adoption Framework (React)

- **Stage node numbers — no glow, no eyebrow**: Only the sequential number (`01`–`06`) via `NODE_STEP`. No "STEP" label above it, no `textShadow` glow. Do not re-add these.
- **React Flow scroll blocking**: `FlowHub.tsx` sets `preventScrolling={false}` on `<ReactFlow>`. Without this, React Flow intercepts wheel events and causes scroll jank. Do not remove this prop.

## Booking

- **`requested_date`/`requested_time` are hidden inputs**: Populated by JS before form submission. If JS is disabled the form cannot be submitted — this is by design.
- **Zoom call link is env-driven, not hardcoded**: `booking_visitor_confirmed.html` renders `{{ zoom_url }}`, injected by `BookingEmailService.send_visitor_confirmed()` from `settings.ZOOM_MEETING_URL` (`settings/base.py`). To change the meeting link, update the `ZOOM_MEETING_URL` env var — do not edit the template. The setting defaults to `''`, so if the env var is missing the email still sends with an empty `href` and a dead "Join Zoom Meeting" button, with no error raised.

## Cloudflare Edge

The site is proxied through Cloudflare in front of Railway (`server: cloudflare`, `cf-ray`, `cf-cache-status` in every response). Almost everything passes through untouched, with one exception:

- **Production `/robots.txt` does not match the repo — this is expected, not a stale deploy**: Cloudflare's managed robots.txt / AI Crawl Control feature *prepends* ~50 lines to the response after Django has rendered it: a Content Signals Policy preamble, `Content-Signal: search=yes,ai-train=no,use=reference`, and `Disallow: /` for nine AI crawlers (Amazonbot, Applebot-Extended, Bytespider, CCBot, ClaudeBot, CloudflareBrowserRenderingCrawler, Google-Extended, GPTBot, meta-externalagent). The repo's own two rules survive verbatim at the bottom. Nothing in the codebase produces or is overridden by that block — to change it, use the Cloudflare dashboard, not `templates/robots.txt`.
- **Only robots.txt is modified**: verified — HTML pages contain no Cloudflare-injected scripts and no `/cdn-cgi/` references, and `sitemap.xml` is pure Django output. Do not assume other production/repo differences have the same explanation.
- **The merged file has two `User-agent: *` groups**: Cloudflare's (`Allow: /`) and the repo's (`Disallow: /zm-admin/`). RFC 9309 requires compliant crawlers to merge duplicate groups and Google does, but a crawler that honours only the first match would ignore the admin rule. Low impact — the admin is behind authentication, and `robots.txt` is a crawling hint, not access control.
- **Blocking those AI crawlers is a Cloudflare default, not a project decision**: it keeps the site out of AI training data but also out of AI-assistant answers. Worth revisiting deliberately if AI-surfaced discoverability matters for lead generation.

## Content

- **Enterprise references**: Homepage and About page reference PayPal, IBM, HPE, and Intel (from Joseph's resume). "Systems X" was a previous employer no longer listed.
- **Results page hidden from UI, but still in the sitemap**: The `/results/` page and URL are intact, but all nav links (header desktop, header mobile, footer) and the NPS badge (`_nps_badge.html`) are hidden until enough client data exists. Restore by re-adding the links and uncommenting `_nps_badge.html`. Note `core/sitemaps.py` still lists `/results/` at priority 0.8, so search engines are pointed at a page hidden from the site's own navigation.
- **`/zm-admin/` is published in `robots.txt`**: the admin was moved off the default `/admin/` path for obscurity, but `templates/robots.txt` names it in a world-readable file, which cancels most of that benefit. Removing the `Disallow` line would restore it — crawlers cannot meaningfully index a login-walled page anyway.
