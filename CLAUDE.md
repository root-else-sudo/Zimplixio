# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Zimplixio is a Django 6.0.3 web application using Python 3.14 for an SMB technology consulting firm. The site includes a homepage, about page (with consultant bios, values flip cards, and an interactive world map), services page, solution showcase gallery (with live iframe demos of recomares.com and simple-forecast.com), NPS results page, contact form, booking system, and legal pages. A `README.md` exists at the repo root for public-facing documentation.

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
- **Database**: PostgreSQL (configured via `DATABASE_URL` in `.env`)
- **Templates**: Project-level `Zimplixio_site/templates/` (shared across all apps)
- **Static files**: `Zimplixio_site/static/` (css, js, images)
- **Media uploads**: `Zimplixio_site/media/`
- **Environment config**: `Zimplixio_site/.env` (django-environ, gitignored).
- **Settings**: Split into `settings/base.py` (shared), `settings/dev.py` (local), `settings/prod.py` (Railway — enforces HSTS, SSL redirect, secure cookies). Controlled by `DJANGO_SETTINGS_MODULE` in `.env`.
- **Deployment**: `railway.toml` (build command) + `start.sh` (collectstatic → migrate → gunicorn)

### Apps

| App | Directory | Purpose |
|-----|-----------|---------|
| `core` | `Zimplixio_site/core/` | Context processors, CSP middleware, sitemaps |
| `pages` | `Zimplixio_site/pages/` | Homepage, About, Services, Contact, Privacy/Cookie Policy |
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
| `/services/` | pages | ServicesPageView |
| `/showcase/` | showcase | ShowcaseGalleryView |
| `/showcase/<slug>/` | showcase | ShowcaseDetailView — template routed by slug map in `get_template_names()`: `e-commerce` → `detail.html`, `simple-forecast` → `detail-simple-forecast.html`, `ai-adoption-framework` → `detail-framework.html`, unknown slugs → `detail-base.html` |
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
- **`booking.BookingRequest`** — visitor booking requests (pending/confirmed/cancelled). Fields include `visitor_timezone` (IANA string, e.g. `America/Los_Angeles`, captured from visitor's browser at booking time). Confirmed slots are excluded from future availability. Changing status → `confirmed` in admin triggers a visitor confirmation email. Changing status → `cancelled` triggers a visitor cancellation email. Both are handled via `confirm()` and `cancel()` instance methods which save the model and call `BookingEmailService`.
- **`framework.AssessmentLead`** — lead captures from the AI assessment (fields: name, email, submitted_at, readiness_level, answers JSON)

### Key Dependencies

- `django-environ` — `.env` file configuration
- `whitenoise` — static file serving (CompressedManifestStaticFilesStorage in production)
- `django-ratelimit` — rate limiting on contact and booking form POSTs (5/hr per IP), assessment API (3/hr per IP)
- `Pillow` — image field support for showcase uploads
- `anthropic` — Anthropic Python SDK for AI readiness assessment API calls
- `@xyflow/react` (v12) — React Flow library for hub-and-spoke diagram in framework accordion (bundled into `static/dist/framework-accordion.js`)
- `react` v19 + `react-dom` v19 — UI library for the framework accordion bundle
- `gunicorn` — WSGI server for production (declared in `Pipfile`, started via `start.sh`)
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

### Showcase Detail Page — Template Architecture

Detail pages use a Django template inheritance system for per-project flexibility without duplication:

- **`templates/showcase/detail-base.html`** — single structural source of truth. Contains the full page layout (hero, Quick Facts strip, all content sections, iframe demo, CTA) with `{% block %}` tags for every customizable string. Generic defaults are used so any unknown future project renders sensibly.
- **`templates/showcase/detail.html`** — thin e-commerce (recomares) override. Extends `detail-base.html` and overrides section title/label blocks only.
- **`templates/showcase/detail-simple-forecast.html`** — thin simple-forecast override. Extends `detail-base.html` and overrides only the blocks it needs.
- **`templates/showcase/detail-framework.html`** — fully custom template for AI Adoption Framework. Does not extend `detail-base.html` — the framework page has a completely different structure (React components, assessment wizard, no standard content sections).
- **Template routing**: `ShowcaseDetailView.get_template_names()` uses a `slug_map` dict. Add a new entry to the map + create `detail-{slug}.html` for any new project needing custom titles.

**Available `{% block %}` tags in `detail-base.html`** (with generic defaults):

| Block | Default |
|-------|---------|
| `hero_subtitle` | *(empty)* |
| `section_problem_label` | `The Challenge` |
| `section_problem_heading` | `The Scenario` |
| `section_decision_label` | `Our Strategy` |
| `section_decision_heading` | `The Approach` |
| `section_solution_label` | `What We Built` |
| `section_solution_heading` | `The Solution` |
| `section_results_label` | `The Impact` |
| `section_results_heading` | `The Outcome` |
| `demo_hint` | *(empty)* — text below toggle buttons in iframe section |

**Quick Facts strip**: All detail pages (including `detail-framework.html`) show a strip below the hero with Industry, Tech Stack pills, and Live Demo availability on a single row (`flex items-start gap-x-10`, no wrapping). `detail-framework.html` hardcodes the Live Demo indicator since the framework project has no `live_demo_url`.

**Interactive iframe demos**:
- The iframe section only appears when `live_demo_url` is set on a `ShowcaseProject`
- **Toggle buttons**: "Live App" (default) + "System Design" (only if `system_design_url` is set)
- **Iframe sandbox**: `allow-scripts allow-same-origin allow-forms allow-popups` for security
- **Loading overlay**: Spinner shown until iframe fires `load` event, driven by `static/js/demo-iframe.js`
- **Gallery badge**: Projects with `live_demo_url` show a green "Live Demo" badge on gallery cards
- **Showcased projects with live iframes**: **recomares.com** (e-commerce, has `/system-design` toggle) and **simple-forecast.com** (LSS forecasting, no system design page). Simple Forecast order=2, created via migration `0007`.

### About Page — Special Features

The About page (`templates/pages/about.html`) has unique components beyond the standard design system:

- **Meet the Team section**: Currently hidden with `{% comment %}{% endcomment %}` tags in `templates/pages/about.html` (lines 66–131). Remove those tags to restore it.
- **Founder cards** (`/* === Founder Cards === */` in `main.css`): CSS grid layout (`grid-template-columns: 260px 1fr`), photo left, content right. Both cards use the same photo-left layout — no reverse variant. Photos at `static/images/joseph.jpg` and `static/images/maria-jose.png`.
- **Values flip cards** (`/* === Values Flip Cards === */` in `main.css`): Three 3D flip cards. CSS `:hover` + JS `.is-flipped` toggle on click/tap. Keyboard accessible (`tabindex="0"`, `role="button"`, Enter/Space triggers flip). `prefers-reduced-motion` disables animation. Icon nodes above cards animate via `.is-hovered` class on `mouseenter`/`mouseleave`.
- **Interactive world map**: See "About Page — World Map" section below.

### Template Structure

```
templates/
├── base.html                  # HTML5 skeleton, Tailwind CDN, AOS global, Schema.org JSON-LD
├── 404.html                   # Custom "Page not found" error page
├── 500.html                   # Custom "Server error" page (self-contained — no context processors)
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
├── showcase/
│   ├── gallery.html           # filterable project gallery
│   ├── detail-base.html       # BASE template — full layout with {% block %} tags, generic defaults
│   ├── detail.html            # e-commerce (recomares) override — extends detail-base.html
│   ├── detail-simple-forecast.html  # simple-forecast override — extends detail-base.html
│   └── detail-framework.html  # AI framework — fully custom, does NOT extend detail-base.html
├── metrics/                   # NPS results page
├── booking/                   # book form + booking_success
├── emails/                    # transactional HTML email templates
│   ├── booking_visitor_received.html    # sent on form submit (acknowledgement)
│   ├── booking_admin_notification.html  # sent to admin on new booking (includes direct admin link)
│   ├── booking_visitor_confirmed.html   # sent when admin confirms a booking
│   ├── booking_visitor_cancelled.html   # sent when admin cancels a booking
│   └── framework_lead_notification.html # sent to admin when an AI assessment lead is captured
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
| `static/js/particles-hero.js` | **Twisted Particle Stream** — custom canvas ImageData animation (no WebGL, no external lib). 20,000 particles across 6 twisted ribbon surfaces with perspective projection simulating 3D depth. Mouse movement tilts the camera (±1.2 rad Y, ±0.65 rad X). Present on all hero sections. |
| `static/js/booking-wizard.js` | Calendly-like 3-step booking wizard — state machine driving calendar grid (step 1), time pills (step 2), and contact form (step 3). Fetches available days and slots from JSON API endpoints. Auto-detects visitor's browser timezone via `Intl.DateTimeFormat().resolvedOptions().timeZone` and converts Eastern slot times to visitor's local time before display (e.g. "10:00 AM EDT" → "7:00 AM PDT"). Populates hidden `requested_date`, `requested_time`, and `visitor_timezone` inputs before form submission. |
| `static/js/showcase-carousel.js` | Netflix-style infinite-loop carousel for Featured Solutions on homepage. Vanilla JS IIFE — clones first/last N slides for seamless wrapping, `translateX` percentage-based positioning, CSS transitions. Auto-play (5s, pauses on hover/focus), left/right arrow + keyboard navigation. Responsive: 1 card mobile, 2 tablet, 3 desktop. Rebuilds clones on resize. `prefers-reduced-motion` disables auto-play. |
| `static/js/world-map.js` | Interactive world map on the About page — D3 v7 + TopoJSON IIFE. Three-state machine: `'world'` (orthographic globe), `'flat'` (Natural Earth world map), `'us'` (US bounding-box zoom). See "About Page — World Map" section. |
| `static/js/services-scroll.js` | Horizontal scroll-pinned panel controller for the services page (desktop ≥1024px only). Translates vertical scroll into `translateX` on `#svcPanelsTrack`. Includes snap-after-pause: after 220ms of no scrolling, `snapToNearest()` smoothly scrolls to the nearest panel. Uses `isSnapping` guard to prevent feedback loops during programmatic scroll. `goToPanel(index)` is called by nav dot clicks. Does not initialize on mobile — the tabbed layout takes over instead. |

### Other Static Files

| File | Purpose |
|------|---------|
| `static/css/main.css` | Custom styles — see inline `/* === Section Name === */` comments for component groupings. Covers hero animations, showcase cards/carousel, PDCA section, about page transitions and gradients, NPS score number, founder cards, values flip cards, services tabbed interface, services scroll panels, services widget grids (p01–p05), What to Expect timeline, world map, credential logos, and dark mode form inputs. |
| `static/css/framework.css` | Framework-specific styles: callout boxes, accordion transitions, report blocks, badges, print rules, stage node icon hover animations (`icon-trace`, `icon-scan-line`, `icon-flow-node`, `icon-data-stream`, `icon-trend-line`, etc.), `prefers-reduced-motion` overrides |
| `static/dist/framework-accordion.js` | Bundled React + React Flow component — hub-and-spoke diagram with animated edges, custom nodes, stage modals; used by `detail-framework.html` |
| `static/dist/framework-accordion.css` | Extracted CSS from the React bundle (React Flow base styles + custom animations) — linked in `detail-framework.html` |
| `static/images/logo.svg` | Zimplixio banner logo — used in `_header.html` nav. ViewBox cropped to content area; fixed width/height removed so CSS controls sizing (`h-14 w-auto` in nav) |
| `static/images/favicon.png` | Site favicon — circular icon PNG with transparent background. Linked in `base.html` as `<link rel="icon" type="image/png">` |
| `static/images/Paypal.svg` | PayPal logo SVG — used in homepage credentials section |
| `static/images/IBM.svg` | IBM logo SVG — used in homepage credentials section |
| `static/images/HPE.svg` | HPE logo SVG (white text, green icon) — used in homepage credentials section |
| `static/images/Intel.svg` | Intel logo SVG — used in homepage credentials section |
| `static/images/joseph.jpg` | Joseph Ugalde photo — used in About page founder card |
| `static/images/maria-jose.png` | Maria Jose Espinoza photo — used in About page founder card |
| `static/images/zimplixio-icon.png` | Zimplixio icon PNG (988×1012px, transparent) — used in email template headers |
| `static/images/zimplixio-wordmark.png` | Zimplixio dark wordmark PNG (2217×596px, transparent) — used in email template footers |
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
- **Framework accordion**: React + React Flow component mounted on `<div id="framework-root">`. Hub-and-spoke diagram — `HubNode` (center), 6 `StageNode` circles, `GradientEdge` spokes. Clicking a node opens a `StageModal` portal. Tech stack: React 19, Vite, `@xyflow/react` v12. Build with `cd frontend && npm run build` — output goes to `static/dist/`.
- **React source**: `frontend/src/` — all component, data, hook, and type files. Key data files: `data/stages.ts` (diagram content), `data/questions.ts` (8 assessment questions). All 6 stages use `type: 'step'` — the unused `'ongoing'` type triggers a purple palette in `StageNode`, do not use it.
- **Fonts**: DM Serif Display + DM Sans loaded via Google Fonts in `{% block extra_head %}`
- **Content source (React)**: `frontend/src/data/stages.ts` — canonical data for the React Flow component. Defines TypeScript interfaces (`Stage`, `Column`, `Callout`, `Table`) and the `STAGES` array with structured fields (`intro`, `columns`, `callouts`, `tables`). `StageModal` renders this structured data. All 6 stages use `type: 'step'` — the `'ongoing'` type is no longer used and would trigger a different (purple) color palette in `StageNode`.
- **Assessment API**: `POST /framework/api/assessment/` — rate-limited 10/hr per IP, calls `claude-sonnet-4-6`, returns structured JSON report (`readiness_level`, `readiness_summary`, `priority_stage`, `top_risks`, `first_30_days`, `one_line_verdict`)
- **Assessment user flow**: 8-question wizard (React, mounted on `#assessment-root`) → loading screen (API call) → contact capture form (name + email) → lead saved + email notification sent → report revealed. The "Start Assessment" button dispatches a `assessmentStart` custom DOM event that the React wizard listens for.
- **Lead capture**: `POST /framework/api/save-lead/` — rate-limited 3/hr per IP, validates name + email (blocks disposable domains, suspicious local-parts), saves `AssessmentLead`, sends email notification to `LEAD_NOTIFICATION_EMAIL` (set via env var, server-side only, never exposed to the client).
- **Lead model**: `framework.AssessmentLead` — viewable at `/zm-admin/framework/assessmentlead/`
- **Prompt engineering**: `framework/prompts.py` — `build_system_prompt()` encodes full framework + strict JSON schema; `build_user_prompt(answers)` interpolates 8 user answers
- **Environment variables**: `ANTHROPIC_API_KEY` (assessment returns 503 if empty); `EMAIL_BACKEND`, `EMAIL_HOST`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL` for transactional email (Microsoft 365 SMTP in production: `smtp.office365.com` port 587); `LEAD_NOTIFICATION_EMAIL` for admin booking/lead notifications (e.g. `joe.ugalde@zimplixio.com`); `ZOOM_MEETING_URL` for the Zoom link in confirmation emails; `SITE_URL` for building absolute links in admin notification emails (dev: `http://localhost:8000`, prod: `https://zimplixio.com`). In dev, `EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend` prints emails to terminal. `DEFAULT_FROM_EMAIL=team@zimplixio.com` in all environments. `BOOKING_TIMEZONE` is hardcoded to `'America/New_York'` in `settings/base.py` (not an env var).
- **Tech tags**: "React" and "Vite" added to the showcase project via migration `showcase/migrations/0006_add_react_vite_tags_to_framework.py`



### About Page — World Map

The "The gap we saw" section of the About page contains an interactive world map in the right `lg:col-span-3` of a `lg:grid-cols-4` layout inside `max-w-7xl`.

**Files**: `static/js/world-map.js` (D3 v7 + TopoJSON IIFE), `static/data/world-110m.json`, `static/data/us-10m.json`. D3 and TopoJSON loaded via unpkg CDN in `extra_js`. Data URLs injected via `data-world-url` / `data-us-url` attributes on `#world-map-container`.

**Three-state interaction**

| State | `state.view` | How to enter | How to exit |
|-------|-------------|--------------|-------------|
| Orthographic globe | `'world'` | Page load | Click any country pin or Americas landmass |
| Flat world map (Natural Earth) | `'flat'` | Morph animation completes | Click US country or US pin → zoom; or mouse-out (600ms) → globe |
| US bounding-box zoom | `'us'` | Click US in flat state | Click outside US states → zoom back to flat; or mouse-out → globe |

**Critical constraints — do not change without reading `world-map.js` first**
- `zoomToUS` uses hardcoded continental US corners (`[-125,50]` → `[-66,24]`) — **do not switch to `path.bounds(nation)`**: Alaska + Hawaii inflate the box and break the zoom
- `clipAngle(90)` must be restored before the reverse morph; country paths must be redrawn after `clipAngle(null)` or polar countries stay clipped
- 29 country pins (`CONTINENTAL` array) + 12 US city pins (`CITIES` array) — touch and desktop share one unified click handler in `drawWorld`

### Booking Email Flow

`booking/services.py` — `BookingEmailService` handles all transactional emails for the booking system. All methods use `fail_silently=False` so SMTP errors propagate to the logger.

| Trigger | Method | Recipient | Template |
|---------|--------|-----------|----------|
| Visitor submits booking form | `send_visitor_received()` | Visitor | `booking_visitor_received.html` |
| Visitor submits booking form | `send_admin_notification()` | `LEAD_NOTIFICATION_EMAIL` | `booking_admin_notification.html` |
| Admin changes status → `confirmed` | `send_visitor_confirmed()` | Visitor | `booking_visitor_confirmed.html` |
| Admin changes status → `cancelled` | `send_visitor_cancelled()` | Visitor | `booking_visitor_cancelled.html` |

**Timezone-aware context**: `_build_context()` builds both `time_str` (Eastern, for admin) and `visitor_time_str` (converted to visitor's IANA timezone via `format_time_in_tz()` in `booking/utils.py`). Visitor email templates use `{{ visitor_time_str }}`; admin template uses `{{ time_str }} ET`. Falls back to Eastern if `visitor_timezone` is empty.

**Admin notification email** includes a direct deep-link button to the booking change page: `{SITE_URL}/zm-admin/booking/bookingrequest/{id}/change/`. Requires `SITE_URL` to be set correctly in the environment. Also shows visitor's `booking.visitor_timezone` as a reference row.

**Admin hook**: `BookingRequestAdmin.save_model()` intercepts status changes. Transitioning to `confirmed` calls `obj.confirm()`; transitioning to `cancelled` calls `obj.cancel()`. Both methods save the model and fire the appropriate email. `super().save_model()` is NOT called in these cases (the model save happens inside `confirm()`/`cancel()`).

**Email template design**: All 4 templates use fully inline styles + table-based layout for Gmail compatibility. Header cells also include `bgcolor="#0f2044"` as a gradient fallback (Gmail strips CSS gradients). Logo assets referenced via absolute URLs (`https://zimplixio.com/static/images/zimplixio-icon.png` and `zimplixio-wordmark.png`).

**Canonical timezone**: `BOOKING_TIMEZONE = 'America/New_York'` in `settings/base.py`. Slot times are stored and returned as Eastern. `format_time_in_tz()` in `booking/utils.py` uses Python's `zoneinfo` stdlib to convert to any IANA timezone.

**Double-booking protection**: The `available_slots_view` filters out already-confirmed times before presenting them to visitors. No database-level unique constraint exists — two simultaneous pending requests for the same slot can both be confirmed by the admin.

### Known Gotchas

See [`docs/GOTCHAS.md`](docs/GOTCHAS.md) for the full list of implementation quirks, removed features, and non-obvious constraints.
