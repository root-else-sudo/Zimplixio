# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Zimplixio is a Django 6.0.3 web application using Python 3.14 for an SMB technology consulting firm. The site includes a homepage, about page (with consultant bios, values flip cards, and an interactive world map), services page, solution showcase gallery (with live iframe demos of recomares.com and simple-forecast.com), NPS results page, contact form, booking system, and legal pages. A technical specification document exists at the repo root (`Zimplixio_Technical_Development_Specification.docx`). A `README.md` also exists at the repo root for public-facing documentation.

## Development Commands

All commands should be run from `Zimplixio_site/` (where `manage.py` lives). The project uses Pipenv with a `.venv` virtual environment.

```bash
# Activate virtual environment
pipenv shell

# Run development server
python manage.py runserver

# Database
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

# Tests
python manage.py test                              # Run all tests
python manage.py test pages                        # Run tests for a specific app
python manage.py test pages.tests.PageStatusTests  # Run a specific test class
python manage.py test pages.tests.PageStatusTests.test_home_page  # Run a single test

# Deployment check
python manage.py check --deploy
```

## Architecture

- **Django project package**: `Zimplixio_site/Zimplixio_site/` — settings, root URL conf, WSGI/ASGI entry points
- **Database**: SQLite3 (`Zimplixio_site/db.sqlite3`)
- **Templates**: Project-level `Zimplixio_site/templates/` (shared across all apps)
- **Static files**: `Zimplixio_site/static/` (css, js, images)
- **Media uploads**: `Zimplixio_site/media/`
- **Environment config**: `Zimplixio_site/.env` (django-environ)
- **Deployment**: `Procfile` at repo root (Heroku — gunicorn + migrate on release)

### Apps

| App | Directory | Purpose |
|-----|-----------|---------|
| `core` | `Zimplixio_site/core/` | Context processors, CSP middleware, sitemaps |
| `pages` | `Zimplixio_site/pages/` | Homepage, About, Contact, Privacy/Cookie Policy |
| `services` | `Zimplixio_site/services/` | Services page (template-only, no models) |
| `showcase` | `Zimplixio_site/showcase/` | Solution showcase gallery & detail pages |
| `metrics` | `Zimplixio_site/metrics/` | NPS score tracking & results page |
| `booking` | `Zimplixio_site/booking/` | Discovery call booking system |
| `framework` | `Zimplixio_site/framework/` | AI readiness assessment API endpoints only (no page-level views — the framework page is served by `showcase` at `/showcase/ai-adoption-framework/`) |

### URL Map

| URL | App | View |
|-----|-----|------|
| `/` | pages | HomePageView |
| `/about/` | pages | AboutPageView |
| `/contact/` | pages | ContactView |
| `/contact/success/` | pages | ContactSuccessView |
| `/privacy-policy/` | pages | PrivacyPolicyView |
| `/cookie-policy/` | pages | CookiePolicyView |
| `/services/` | services | ServicesPageView |
| `/showcase/` | showcase | ShowcaseGalleryView |
| `/showcase/<slug>/` | showcase | ShowcaseDetailView (slug `ai-adoption-framework` uses custom template `detail-framework.html`) |
| `/results/` | metrics | NPSResultsView |
| `/book/` | booking | BookCallView |
| `/book/success/` | booking | BookingSuccessView |
| `/book/slots/` | booking | available_slots_view (GET, returns time pills for a date) |
| `/book/available-days/` | booking | available_days_view (GET, returns bookable days for a month) |
| **`/framework/api/*`** | **framework — API only** | **No page views; framework page lives at `/showcase/ai-adoption-framework/`** |
| `/framework/api/assessment/` | framework | assessment_view (POST, Anthropic API) |
| `/framework/api/save-lead/` | framework | save_lead_view (POST, saves AssessmentLead + sends email notification) |
| `/zm-admin/` | django.admin | Admin interface |
| `/sitemap.xml` | django.sitemaps | XML sitemap |
| `/robots.txt` | — | TemplateView |

### Key Models

- **`pages.ContactSubmission`** — contact form submissions (fields: name, email, company, message, submitted_at, is_read)
- **`showcase.TechTag`** — technology labels for project tagging (M2M with ShowcaseProject)
- **`showcase.ShowcaseProject`** — case study projects. Includes `live_demo_url` and `system_design_url` for interactive iframe demos on detail pages
- **`showcase.ShowcaseScreenshot`** — screenshot images linked to a ShowcaseProject (FK)
- **`metrics.NPSMetric`** — NPS scores (single-active enforcement via `save()` override)
- **`booking.TimeSlot`** — admin-defined weekly available windows (day_of_week, start_time, end_time, is_active). Managed via `/zm-admin/booking/timeslot/` — this is the only place to configure availability (no external calendar sync).
- **`booking.BookingRequest`** — visitor booking requests (pending/confirmed/cancelled). Confirmed slots are excluded from future availability. Changing status → `confirmed` in admin triggers a visitor confirmation email.
- **`framework.AssessmentLead`** — lead captures from the AI assessment (fields: name, email, submitted_at, readiness_level, answers JSON)

### Key Dependencies

- `django-environ` — `.env` file configuration
- `whitenoise` — static file serving (CompressedManifestStaticFilesStorage in production)
- `django-ratelimit` — rate limiting on contact and booking form POSTs (5/hr per IP), assessment API (3/hr per IP)
- `Pillow` — image field support for showcase uploads
- `anthropic` — Anthropic Python SDK for AI readiness assessment API calls
- `@xyflow/react` (v12) — React Flow library for hub-and-spoke diagram in framework accordion (bundled into `static/dist/framework-accordion.js`)
- `react` v19 + `react-dom` v19 — UI library for the framework accordion bundle
- `gunicorn` — WSGI server for production (referenced in `Procfile` and declared in `Pipfile`)
- Tailwind CSS via CDN (development)
- AOS (Animate On Scroll) via unpkg CDN — global scroll-triggered animations

### Forms

- **`pages.forms.ContactForm`** — contact page submission form
- **`booking.forms.BookingForm`** — discovery call booking form

### Admin Configuration

All models have customized admin classes. Admin site branding is set in root `urls.py`:
- `admin.site.site_header = 'Zimplixio Administration'`
- `admin.site.site_title = 'Zimplixio Admin'`
- `admin.site.index_title = 'Site Management'`

`framework/admin.py` registers `AssessmentLeadAdmin` with list display (name, email, readiness_level, submitted_at), filters, search, and readonly fields for submitted_at and answers.

### UI Design System

All pages follow a consistent design language. When creating new pages, follow these conventions:

- **Gradient heroes**: Every page opens with `bg-gradient-to-br from-indigo-700 via-indigo-800 to-gray-900` hero section with ambient blur circles (`bg-white rounded-full blur-3xl` at ~10% opacity)
- **Section subtitle labels**: Uppercase indigo tracking-wider text (`text-indigo-300 font-medium tracking-wider uppercase text-sm`) above headings
- **AOS scroll animations**: All sections use `data-aos="fade-up"` with staggered `data-aos-delay` values (100ms increments). AOS is loaded globally in `base.html` with `once: true, duration: 700, easing: 'ease-out-cubic'`
- **Card styling**: `rounded-2xl border border-gray-200 shadow-sm` with `hover:shadow-md transition-shadow` for interactive cards
- **Section spacing**: Consistent `py-20` for content sections
- **CTA buttons**: `bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700 transition-colors shadow-lg shadow-indigo-600/20`
- **Dark mode**: Tailwind `darkMode: 'class'` — the `dark` class is toggled on `<html>` by `dark-mode.js`. Preference is persisted in `localStorage` and applied on page load (inline script in `<head>`) to prevent FOUC. Use `dark:` variants on all new UI elements. Common pairings: `bg-white dark:bg-gray-900`, `text-gray-900 dark:text-white`, `border-gray-200 dark:border-gray-700`, `bg-gray-50 dark:bg-gray-800`. Toggle button uses `.dark-mode-toggle` class; icons use `.dark-mode-moon` (visible in light) and `.dark-mode-sun` (visible in dark, starts `hidden`).

### Showcase Detail Page — Interactive Demos

The showcase detail page (`templates/showcase/detail.html`) supports interactive iframe demos:

- **Conditional rendering**: The iframe section only appears when `live_demo_url` is set on a `ShowcaseProject`
- **Toggle buttons**: "Live App" (default) + "System Design" (only if `system_design_url` is set), styled like gallery filter pills
- **Iframe sandbox**: `allow-scripts allow-same-origin allow-forms allow-popups` for security
- **Loading overlay**: Spinner shown until iframe fires `load` event, driven by `static/js/demo-iframe.js`
- **Gallery badge**: Projects with `live_demo_url` show a green "Live Demo" badge on gallery cards
- **Showcased projects with live iframes**: **recomares.com** (e-commerce, has `/system-design` toggle) and **simple-forecast.com** (LSS forecasting, no system design page). Simple Forecast order=2, created via migration `0007`.

### About Page — Special Features

The About page (`templates/pages/about.html`) has unique components beyond the standard design system:

- **Founder cards** (`/* === Founder Cards === */` block in `main.css`): Two side-by-side mini horizontal cards displayed in a `grid grid-cols-1 md:grid-cols-2 gap-6` layout inside `max-w-7xl`. Each card uses CSS grid (`grid-template-columns: 260px 1fr`) — photo on the left (fixed `260px` column, `object-fit: cover`, fills the full card height), content on the right. The content panel (`founder-content-panel`) contains: name/title (`founder-meta-block`), LinkedIn button (`founder-linkedin-btn`), story-driven bio (`founder-bio`), and a blue left-border accent quote (`founder-accent`). No `.founder-card--reverse` variant — both cards use the same photo-left layout. Photos at `static/images/joseph.jpg` and `static/images/maria-jose.png`. Full light/dark mode support. AOS `fade-up` staggered entrance.
- **Values flip cards** (`/* === Values Flip Cards === */` block in `main.css`): Three 3D flip cards in a `values-grid` (`repeat(3, 1fr)`) below a timeline track with animated connecting line. Front face shows a faded large number, category tag label, value title, and "Click to reveal" hint. Back face shows an indigo gradient with eyebrow, bold headline, and description body. Interaction: CSS `:hover` + JS `.is-flipped` class toggle on click/tap. Keyboard accessible (`tabindex="0"`, `role="button"`, Enter/Space triggers flip, `:focus-visible` ring). `aria-hidden` toggled on back face. `prefers-reduced-motion` shows/hides faces without animation. Mobile: single column, `height: 300px`, timeline track hidden. Three icon nodes above the cards (eye, trophy, shield SVGs) animate with glow + pulse ring when the corresponding card is hovered or clicked — JS `.is-hovered` class controlled by `mouseenter`/`mouseleave` on cards and nodes.
- Real data from Joseph Ugalde's resume (HPE, IBM, PayPal, Intel career path). Maria Jose Espinoza (Co-Founder & Process Optimization and Automation Consultant) is the second founder card.
- **Interactive world map**: See "About Page — World Map" section below.

### Template Structure

```
templates/
├── base.html                  # HTML5 skeleton, Tailwind CDN, AOS global, Schema.org JSON-LD
├── robots.txt
├── partials/
│   ├── _header.html           # Sticky nav with hamburger menu
│   ├── _footer.html
│   ├── _cookie_banner.html
│   ├── _meta_tags.html        # Open Graph / Twitter Card meta
│   ├── _nps_badge.html        # NPS score badge (conditional)
│   └── _cta_section.html      # Reusable CTA block with gradient bg
├── pages/                     # home, about, contact, contact_success, privacy/cookie policy
├── services/                  # services page with tabbed interface + FAQ accordion
├── showcase/                  # gallery (filterable) + detail pages
├── metrics/                   # NPS results page
├── booking/                   # book form + booking_success
├── emails/                    # transactional HTML email templates
│   ├── booking_visitor_received.html    # sent on form submit (acknowledgement)
│   ├── booking_admin_notification.html  # sent to admin on new booking
│   └── booking_visitor_confirmed.html   # sent when admin confirms a booking
└── framework/                 # AI adoption framework page + assessment
```

### Static JS Files

| File | Purpose |
|------|---------|
| `static/js/mobile-nav.js` | Hamburger toggle for mobile navigation |
| `static/js/cookie-consent.js` | Cookie banner with localStorage persistence |
| `static/js/faq-accordion.js` | Expand/collapse FAQ items on services page |
| `static/js/demo-iframe.js` | Iframe loading overlay + toggle buttons on showcase detail page |
| `static/js/dark-mode.js` | Dark mode toggle with smooth transition (enables `body.transitions-enabled` after first paint to avoid FOUC) |
| `static/js/header-scroll.js` | Adds `.header-elevated` box-shadow to `<header>` when `scrollY > 20` |
| `static/js/logo-magnetic.js` | Magnetic cursor effect on `.logo-magnetic` elements (logo + Book a Call button) — lerp-based rAF loop, STRENGTH=0.28, EASE=0.1 |
| `static/js/hero-text.js` | Word-by-word H1 reveal on `[data-word-reveal]` elements — splits into `<span class="word-reveal-item">` with staggered CSS animation |
| `static/js/counter-anim.js` | IntersectionObserver counter animation on `[data-counter]` elements — ease-out-cubic count from 0 to `data-target`. Supports `data-pad` for zero-padded output and `data-suffix`. Handles both `DOMContentLoaded` and already-loaded states (safe to load at end of body). Used on about page stats. |
| `static/js/particles-hero.js` | **Twisted Particle Stream** — custom canvas ImageData animation (no WebGL, no external lib). 20,000 particles across 6 twisted ribbon surfaces with perspective projection simulating 3D depth. Mouse movement tilts the camera (±1.2 rad Y, ±0.65 rad X). Present on all hero sections. |
| `static/js/booking-wizard.js` | Calendly-like 3-step booking wizard — state machine driving calendar grid (step 1), time pills (step 2), and contact form (step 3). Fetches available days and slots from JSON API endpoints. Populates hidden `requested_date`/`requested_time` inputs before form submission. |
| `static/js/showcase-carousel.js` | Netflix-style infinite-loop carousel for Featured Solutions on homepage. Vanilla JS IIFE — clones first/last N slides for seamless wrapping, `translateX` percentage-based positioning, CSS transitions. Auto-play (5s, pauses on hover/focus), left/right arrow + keyboard navigation. Responsive: 1 card mobile, 2 tablet, 3 desktop. Rebuilds clones on resize. `prefers-reduced-motion` disables auto-play. |
| `static/js/world-map.js` | Interactive world map on the About page — D3 v7 + TopoJSON IIFE. Three-state machine: `'world'` (orthographic globe), `'flat'` (Natural Earth world map), `'us'` (US bounding-box zoom). See "About Page — World Map" section. |
| `static/js/timeline.js` | **Unused — do not load.** Legacy interactive career timeline for the About page. The "The Journey" section was removed; `timeline.js` is no longer referenced in any template. File kept on disk but serves no purpose. |
| `static/js/services-scroll.js` | Horizontal scroll-pinned panel controller for the services page (desktop ≥1024px only). Translates vertical scroll into `translateX` on `#svcPanelsTrack`. Includes snap-after-pause: after 220ms of no scrolling, `snapToNearest()` smoothly scrolls to the nearest panel. Uses `isSnapping` guard to prevent feedback loops during programmatic scroll. `goToPanel(index)` is called by nav dot clicks. Does not initialize on mobile — the tabbed layout takes over instead. |

### Other Static Files

| File | Purpose |
|------|---------|
| `static/css/main.css` | Custom styles — see inline `/* === Section Name === */` comments for component groupings. Covers hero animations, showcase cards/carousel, PDCA section, founder cards, values flip cards, services tabbed interface, services scroll panels, services widget grids (p01–p05), What to Expect timeline, world map, credential logos, and dark mode form inputs. |
| `static/css/framework.css` | Framework-specific styles: callout boxes, accordion transitions, report blocks, badges, print rules, stage node icon hover animations (`icon-trace`, `icon-scan-line`, `icon-flow-node`, `icon-data-stream`, `icon-trend-line`, etc.), `prefers-reduced-motion` overrides |
| `static/dist/framework-accordion.js` | Bundled React + React Flow component — hub-and-spoke diagram with animated edges, custom nodes, stage modals; used by `detail-framework.html` |
| `static/dist/framework-accordion.css` | Extracted CSS from the React bundle (React Flow base styles + custom animations) — linked in `detail-framework.html` |
| `static/images/logo.svg` | Zimplixio banner logo — used in `_header.html` nav. ViewBox cropped to content area; fixed width/height removed so CSS controls sizing (`h-14 w-auto` in nav) |
| `static/images/favicon.png` | Site favicon — circular icon PNG with transparent background, sourced from `cropped_circle_image.png`. Linked in `base.html` as `<link rel="icon" type="image/png">` |
| `static/images/Paypal.svg` | PayPal logo SVG — used in homepage credentials section |
| `static/images/IBM.svg` | IBM logo SVG — used in homepage credentials section |
| `static/images/HPE.svg` | HPE logo SVG (white text, green icon) — used in homepage credentials section |
| `static/images/Intel.svg` | Intel logo SVG — used in homepage credentials section |
| `static/images/joseph.jpg` | Joseph Ugalde photo — used in About page founder card |
| `static/images/maria-jose.png` | Maria Jose Espinoza photo — used in About page founder card |
| `static/manifest.json` | PWA web app manifest with Zimplixio branding |

### Security

- CSP middleware (`core.middleware.ContentSecurityPolicyMiddleware`) — `default-src 'self'`; `script-src` allows `'unsafe-inline' 'unsafe-eval'` + Tailwind CDN + unpkg.com; `style-src` allows `'unsafe-inline'` + unpkg.com + fonts.googleapis.com; `font-src 'self'` + fonts.gstatic.com; `img-src 'self' data:`; `frame-src https:`; `frame-ancestors 'none'`
- Rate limiting on form POST endpoints (5/hr per IP)
- Production-only settings: HSTS, SSL redirect, secure cookies, CompressedManifestStaticFilesStorage (activated when `DEBUG=False`)
- Admin at `/zm-admin/` (not the default `/admin/`)

### AI Adoption Framework (Embedded in Showcase)

The framework content is served at `/showcase/ai-adoption-framework/` via a custom template (`templates/showcase/detail-framework.html`). `framework/urls.py` routes the assessment API and save-lead endpoints.

- **Custom template routing**: `ShowcaseDetailView.get_template_names()` returns `detail-framework.html` when `slug == 'ai-adoption-framework'`; `get_context_data()` injects `api_available`
- **Page structure**: Hero (with "Try the Assessment" scroll button) → Core Philosophy → Framework Accordion (6 stages, React Flow) → Closing Quote → CTA Panel → Assessment wizard
- **Framework accordion**: React + React Flow component mounted on `<div id="framework-root">`. Hub-and-spoke diagram with `HubNode` (center AI circle, pulse/orbit animations), `StageNode` (6 stage circles with icons, idle animations), `GradientEdge` (animated dot spokes). Clicking a node opens a `StageModal` portal overlay with full stage content. Tech stack: React, Vite, `@xyflow/react` v12.
- **StageNode design**: All 6 nodes are 152px fixed circles. Inactive state: `#0f1628` navy bg, `rgba(37,99,235,0.4)` border. Active state: blue gradient + scale(1.1). Icon color: `#60a5fa` inactive, `white` active. Below each node: stage name label at 16px, weight 600 (700 when active). Inside the circle: icon (72px) + sequential number (`01`–`06`) via `NODE_STEP` map — no "STEP" eyebrow, no text-shadow glow. Orbit/pulse rings shown only when inactive; float animation on icon when inactive.
- **StageIcons design**: All icons use `viewBox="0 0 36 36"`, derive `primary/secondary/accent/fill` from a `color` prop via `deriveColors()` helper. Icons: `IconReadiness` (circuit clipboard + scan line), `IconWorkflows` (branching pipeline), `IconGovernance` (shield + circuit grid), `IconDataProtection` (lock + data streams), `IconPeople` (network of person nodes), `IconROI` (3 ascending columns + spark line + upward arrow). CSS hover animations on `.stage-node-circle:hover .icon-*` classes defined in `framework.css`.
- **StageModal header labels**: `STAGE_BADGE` map in `StageModal.tsx` — `'0':'Step 1'`, `'1':'Step 2'`, `'2':'Step 3'`, `'3':'Step 4'`, `'P':'Step 5'`, `'M':'Step 6'`.
- **React source**: `frontend/src/` — diagram components: `FlowHub.tsx`, `HubNode.tsx`, `StageNode.tsx`, `StageIcons.tsx`, `GradientEdge.tsx`, `StageModal.tsx`, `FrameworkAccordion.tsx`. Modal sub-components: `DualColumn.tsx`, `Callout.tsx`, `ComparisonTable.tsx`. Assessment wizard components: `AssessmentWizard.tsx`, `WizardQuestion.tsx`, `LoadingScreen.tsx`, `ContactForm.tsx`, `AssessmentReport.tsx`. Hook: `frontend/src/hooks/useIsMobile.ts`. Data: `frontend/src/data/stages.ts` (diagram), `frontend/src/data/questions.ts` (8 wizard questions). Types: `frontend/src/types/assessment.ts`. Build with `cd frontend && npm run build`.
- **Fonts**: DM Serif Display + DM Sans loaded via Google Fonts in `{% block extra_head %}`
- **Content source (React)**: `frontend/src/data/stages.ts` — canonical data for the React Flow component. Defines TypeScript interfaces (`Stage`, `Column`, `Callout`, `Table`) and the `STAGES` array with structured fields (`intro`, `columns`, `callouts`, `tables`). `StageModal` renders this structured data. All 6 stages use `type: 'step'` — the `'ongoing'` type is no longer used and would trigger a different (purple) color palette in `StageNode`.
- **Assessment API**: `POST /framework/api/assessment/` — rate-limited 3/hr per IP, calls `claude-sonnet-4-6`, returns structured JSON report (`readiness_level`, `readiness_summary`, `priority_stage`, `top_risks`, `first_30_days`, `one_line_verdict`)
- **Assessment user flow**: 8-question wizard (React, mounted on `#assessment-root`) → loading screen (API call) → contact capture form (name + email) → lead saved + email notification sent → report revealed. The "Start Assessment" button dispatches a `assessmentStart` custom DOM event that the React wizard listens for.
- **Lead capture**: `POST /framework/api/save-lead/` — rate-limited 10/h per IP, validates name + email (blocks disposable domains, suspicious local-parts), saves `AssessmentLead`, sends email notification to `LEAD_NOTIFICATION_EMAIL` (`joe.ugalde@zimplixio.com`). Recipient is server-side only, never exposed to the client.
- **Lead model**: `framework.AssessmentLead` — viewable at `/zm-admin/framework/assessmentlead/`
- **Prompt engineering**: `framework/prompts.py` — `build_system_prompt()` encodes full framework + strict JSON schema; `build_user_prompt(answers)` interpolates 8 user answers
- **Environment variables**: `ANTHROPIC_API_KEY` (assessment returns 503 if empty); `EMAIL_BACKEND`, `EMAIL_HOST`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL` for lead notifications. In dev, `EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend` prints emails to terminal.
- **Tech tags**: "React" and "Vite" added to the showcase project via migration `showcase/migrations/0006_add_react_vite_tags_to_framework.py`



### About Page — World Map

The "The gap we saw" section of the About page contains an interactive world map in the right `lg:col-span-3` of a `lg:grid-cols-4` layout inside `max-w-7xl`.

**Files**

| File | Role |
|------|------|
| `static/js/world-map.js` | Main IIFE component (~500 lines) |
| `static/css/main.css` | Map styles appended at bottom (`/* === World Map === */`) |
| `static/data/world-110m.json` | World TopoJSON (CC0, world-atlas v2) |
| `static/data/us-10m.json` | US states TopoJSON (CC0, us-atlas v3) |
| `templates/pages/about.html` | Section markup + `extra_js` block |

CDN scripts in `extra_js`: D3 v7 and TopoJSON v3 from `unpkg.com`. Data URLs injected via `data-world-url` / `data-us-url` attributes on `#world-map-container` using `{% static %}` tags.

**Three-state interaction**

| State | `state.view` | How to enter | How to exit |
|-------|-------------|--------------|-------------|
| Orthographic globe | `'world'` | Page load | Click any country pin or Americas landmass |
| Flat world map (Natural Earth) | `'flat'` | Morph animation completes | Click US country or US pin → zoom; or mouse-out (600ms) → globe |
| US bounding-box zoom | `'us'` | Click US in flat state | Click outside US states → zoom back to flat; or mouse-out → globe |

**Globe state details**
- Drag SVG to rotate freely (drag handler on `ctx.svg`)
- `globeVisible(proj, lon, lat)` great-circle check controls pin show/hide — never uses `clipAngle` return value alone (avoids edge-case ocean pins)
- All 29 country pins are created on load; back-hemisphere pins hidden via `opacity:0` + `translate(-9999,-9999)`

**Country pins (`CONTINENTAL` array — 29 entries)**
Americas: United States, Canada, Mexico, Costa Rica, Argentina, Brasil  
Europe: Belgium, France, Germany, Ireland, Netherlands, Romania, Spain, Switzerland, United Kingdom  
Africa: Egypt, South Africa  
Asia: India, Indonesia, Japan, Vietnam, Philippines, Bangladesh, UAE, Taiwan, Israel, Qatar, Singapore  
Pacific: Australia

**US city pins (`CITIES` array — 12 entries)**  
Atlanta GA, Miami FL, Houston TX, Los Angeles CA, Detroit MI, New York NY, Chicago IL, New Orleans LA, Boston MA, Newark NJ, Charlotte NC, Portland OR

**Key technical details**
- `makeInterpolatedProjection(rawA, rawB)` blends `geoOrthographicRaw` and `geoNaturalEarth1Raw` via `alpha(t)` using `geoProjectionMutator`
- `clipAngle(90)` set at globe init; `clipAngle(null)` called after flat morph completes; `clipAngle(90)` restored before reverse morph
- Country paths redrawn with `ctx.g.selectAll('.map-country').attr('d', ctx.path)` after `clipAngle(null)` — required or polar countries stay clipped
- `zoomToUS` uses hardcoded continental US corners (`[-125,50]` → `[-66,24]`) to compute the bounding box — **do not switch back to `path.bounds(nation)`** as Alaska + Hawaii inflate the box and produce a near-useless zoom
- Pin shapes: `PIN_LG` (continental, tip at origin, ~19px tall) and `PIN_SM` (city, ~13px tall) — SVG path strings, filled red (`#ef4444`) via `.attr('fill', ...)`
- `setupTouch` function was removed; touch and desktop share one unified `ctx.svg.on('click', ...)` handler in `drawWorld`

### Known Gotchas

- **STORAGES setting**: `CompressedManifestStaticFilesStorage` is only enabled when `DEBUG=False` — using it in dev/test without running `collectstatic` causes `ValueError: Missing staticfiles manifest entry`
- **Enterprise references**: Homepage and About page reference PayPal, IBM, HPE, and Intel (from Joseph's updated resume). Systems X was a previous employer no longer listed.
- **Cross-origin iframe CSRF**: Embedded apps (e.g., recomares.com) that use POST-based actions (like Django `set_language`) will fail in the iframe due to third-party cookie blocking. This is a browser limitation — fix requires `SameSite=None` on the embedded app's cookies. The "Open in new tab" fallback link is provided.
- **Gallery thumbnails**: Use `object-contain` (not `object-cover`) so icon-style images display fully without cropping
- **HomePageView cross-app query**: `HomePageView` imports `showcase.ShowcaseProject` to fetch `featured_projects` for the homepage — changes to the showcase model can affect the homepage
- **One React bundle for everything**: `static/dist/framework-accordion.js` (built from `frontend/`) drives both the hub-and-spoke diagram and the assessment wizard. Rebuilding with `cd frontend && npm run build` updates both.
- **Stage `type: 'ongoing'` activates purple palette**: `StageNode.tsx` uses `isOngoing` to switch to a purple color scheme. All 6 stages currently use `type: 'step'`. Do not change any stage to `type: 'ongoing'` unless you intend to visually distinguish it with the purple treatment.
- **Stage node numbers — no glow, no eyebrow**: The number badge inside each node shows only the sequential number (`01`–`06`) via `NODE_STEP`. There is no "STEP" label above it and no `textShadow` glow effect. Do not re-add these.
- **React Flow scroll blocking**: `FlowHub.tsx` sets `preventScrolling={false}` on the `<ReactFlow>` component. Without this, React Flow intercepts wheel events and calls `preventDefault()` even when zoom is disabled, causing scroll jank on the framework page. Do not remove this prop.
- **Logo SVG sizing**: `static/images/logo.svg` has no fixed `width`/`height` attributes (removed so CSS controls size). The viewBox is cropped to the content area (`278 337 1656 426`). If the logo looks wrong, check these two things first.
- **`{% load static %}` in partials**: `_header.html` includes its own `{% load static %}` at the top — required because partials do not inherit the parent template's loaded tags.
- **Hero particle effect — `#hero-particles` div required**: `particles-hero.js` looks for `<div id="hero-particles">` inside the hero `<section>`. The div must be present with `position:absolute; inset:0; z-index:1; pointer-events:none` (defined in `main.css`). All 9 hero pages have this div. The script listens on `document` (not the canvas) for mousemove since the canvas has `pointer-events:none`.
- **No tsParticles / no CDN for hero effect**: The hero animation is pure vanilla JS canvas (ImageData pixel writing). The tsParticles CDN was removed. `cdn.jsdelivr.net` was also removed from the CSP `script-src` directive in `core/middleware.py`.
- **Color palette — Tailwind `indigo` remapped**: The `indigo` color scale in `base.html` Tailwind config is overridden to a navy/electric-blue palette (`indigo-600 = #2563eb`, `indigo-800 = #0f2044`, `indigo-900 = #0a1628`). This cascades sitewide — do not add new raw hex values for blue; use `indigo-*` classes.
- **`.logo-magnetic` on multiple elements**: The magnetic effect uses `querySelectorAll('.logo-magnetic')` with independent state per element. Applied to the logo `<a>` and desktop "Book a Call" button in `_header.html`. Do not apply to the mobile "Book a Call" (inside the dropdown menu).
- **Booking wizard — availability is DB-only**: There is no Google Calendar / external calendar sync. Availability comes entirely from `TimeSlot` records in the admin. Create at least one active `TimeSlot` or the calendar will show no selectable days.
- **Booking wizard — `requested_date`/`requested_time` are hidden inputs**: The wizard populates these via JS before form submission. If JS is disabled the form cannot be submitted — this is by design (the wizard requires JS).
- **Booking confirmation email triggers on admin save**: `BookingRequestAdmin.save_model()` detects the `pending → confirmed` transition and sends `booking_visitor_confirmed.html`. This works for both the detail change form and `list_editable` inline saves.
- **Zoom call link is hardcoded in confirmation email**: `templates/emails/booking_visitor_confirmed.html` contains a fixed Zoom link. Update this template if the meeting link changes.
- **PDCA section — no GSAP, no JS file**: The PDCA section is pure CSS + AOS only. Do not add JS animation libraries (e.g. GSAP) — all motion is handled via CSS keyframes and AOS entrance animations. `cdnjs.cloudflare.com` is not in the CSP `script-src` allowlist.
- **PDCA description reveal is hover-only on desktop**: `.pdca-desc` uses `max-height: 0` → `max-height: 200px` on `:hover`. On mobile (≤767px), descriptions are always visible via CSS override. No JS fallback for touch devices on desktop — descriptions auto-reveal on card tap via `:hover` on touch browsers.
- **Showcase carousel clones require N ≥ visible count**: The carousel clones the first/last N slides (where N = visible count: 3 desktop, 2 tablet, 1 mobile). With only 3 projects, the carousel still works because clones fill the gaps. If reduced to fewer than the visible count, the layout may look sparse.
- **Showcase carousel auto-play pauses on hover/focus**: Auto-play resumes on `mouseleave`/`focusout`. If the user tabs into a card and doesn't tab out, auto-play stays paused indefinitely — this is intentional for accessibility.
- **HPE logo has white text**: The HPE SVG (`static/images/HPE.svg`) was modified to use `fill:#ffffff` for text paths. The green icon element (`fill:#00b188`) was not changed. If the logo appears invisible on white backgrounds, this is why.
- **Credential logo sizing is per-file**: PayPal/IBM/HPE use `.credential-logo-xl` (280×104px) and Intel uses default `.credential-logo` (140×52px) because the SVGs have different native aspect ratios. Adjust these classes if logos are swapped.
- **Iframe-embedded showcase apps must allow framing**: Any external app added to the showcase with `live_demo_url` must not send `X-Frame-Options: SAMEORIGIN` (Django's default via `XFrameOptionsMiddleware`). Remove `XFrameOptionsMiddleware` from the embedded app's `MIDDLEWARE` setting to allow cross-origin embedding. Simple Forecast required this fix before its iframe would load on zimplixio.com.
- **Values flip cards — hover + click both trigger flip**: The 3D flip fires on CSS `:hover` (desktop) AND on the `.is-flipped` JS class (click/tap). Both paths call `rotateY(180deg)` on `.values-flip-inner`. Do not remove either — hover gives instant desktop response; `.is-flipped` makes it work on touch. The `aria-hidden` attribute on `.values-back` is toggled by the JS click handler to match the flipped state.
- **Services page has two layouts that coexist**: Desktop (≥1024px) uses a scroll-pinned horizontal panel layout (`.svc-scroll-root`, `#servicesOuter`, `#svcPanelsTrack`) driven by `services-scroll.js`. Mobile uses a tabbed layout (`.svc-tab-root`, `.z-*` classes) with an inline `zSwitch(index)` function. Both layouts live in `services.html` — the scroll layout is hidden on mobile via CSS and JS returns early if `innerWidth < 1024`. Do not use AOS on either section.
- **Services page CSS uses five naming prefixes**: Each section has its own namespace — `svc-*` (scroll panel chrome: progress bar, dots, counter), `z-*` (mobile tabbed layout), `vis-*` (deliverable bullet lists shared across both layouts), `p01-*` through `p05-*` (animated widget grids in each scroll panel right column), `wte-*` (What to Expect timeline section). These are intentionally separate; do not mix them.
- **Services scroll panels — widget color variants use modifier classes**: Inline `style` attributes were removed from widget elements. Colors are expressed as BEM-style modifier classes defined in `main.css`: e.g. `.p01-ms-dot--blue/teal/purple`, `.p03-w2-process--success`, `.p03-adf-connector--success`, `.p05-dim-score--good/warn/poor/info`, `.p05-member-fill--green/blue/teal`, `.p05-member-level--green/blue/teal`. Add new color variants as modifier classes, not inline styles.
- **Services page — What to Expect section**: A 4-step horizontal timeline below the scroll panels, driven by a vanilla JS `IntersectionObserver` (no GSAP). The section uses `wte-*` CSS classes. Animation fires once on scroll-enter: eyebrow → title → nodes pop in (spring easing) → connectors → content fades up → progress line grows → badge appears. Timing is staggered at 400ms, 900ms, 1400ms, 1900ms per step; line completes at 2100ms. All styles live in the `/* === What to Expect Timeline === */` block at the end of `main.css`.
- **Services page — no Pricing Signal section**: The pricing signal section was removed. Do not re-add it.
- **About page no longer has `timeline.js`**: The interactive career timeline section ("The Journey") was removed. `static/js/timeline.js` is no longer loaded in `about.html` and is not referenced anywhere. The file still exists on disk but is unused.
- **Founder cards have no `--reverse` variant**: Both founder cards (Joseph and Maria Jose) use the same photo-left layout. There is no `.founder-card--reverse` class in the HTML or CSS — it was removed when the layout switched from full-width stacked to side-by-side mini horizontal.
