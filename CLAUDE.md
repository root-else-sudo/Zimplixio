# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**Scope note:** this file covers what is *non-obvious* — conventions, constraints, and decisions you would otherwise get wrong. Anything derivable from the code in one command (URL map, model fields, file inventories, template tree) is deliberately not duplicated here; read it from the source instead, which is always current.

## Project Overview

Zimplixio is a Django 6.0.4 web application on Python 3.14.3 for an SMB technology consulting firm. Pages: homepage, about (consultant bios, values flip cards, interactive world map), services, solution showcase gallery with live iframe demos, NPS results, contact form, booking system, and legal pages. `README.md` at the repo root is the public-facing documentation.

## Development Commands

`manage.py` lives in `Zimplixio_site/`, but the virtualenv is at the **repo root** — so from `Zimplixio_site/` the interpreter is `../.venv/bin/python`. Standard Django commands otherwise (`runserver`, `migrate`, `makemigrations`, `createsuperuser`, `test`, `check --deploy`).

```bash
cd Zimplixio_site
../.venv/bin/python manage.py test        # full suite (50 tests)
../.venv/bin/python manage.py check
```

The React bundle is built separately: `cd frontend && npm run build`.

## Architecture

- **Django project package**: `Zimplixio_site/Zimplixio_site/` — settings, root URL conf, WSGI/ASGI entry points
- **Database**: PostgreSQL via `DATABASE_URL`. Persistent connections are enabled in `settings/base.py` (`CONN_MAX_AGE`, `CONN_HEALTH_CHECKS`) and the Railway Postgres service must sit in the **same region** as the web service. Both are load-bearing for response time — see `docs/GOTCHAS.md` before changing either
- **Templates**: project-level `Zimplixio_site/templates/` (shared across all apps; no per-app template dirs in use)
- **Static files**: `Zimplixio_site/static/`
- **Media uploads**: local disk in dev, **Cloudflare R2** in production — see "Media Storage"
- **Environment config**: `Zimplixio_site/.env` (django-environ, gitignored). There is no `.env.example` — a fresh clone cannot boot until one is written, since `SECRET_KEY`, `DEBUG`, and `ALLOWED_HOSTS` have no defaults
- **Settings**: `settings/base.py` (shared), `dev.py`, `prod.py` (Railway — HSTS, SSL redirect, secure cookies, R2). Selected by `DJANGO_SETTINGS_MODULE` in `.env`
- **Deployment**: `railway.toml` (frontend build) + `start.sh` (collectstatic → migrate → gunicorn, 2 workers)
- **Migrations**: squashed to `0001_initial` in every app except `booking` (which has `0002`, `0003`). Showcase projects and tech tags are admin-managed data, not fixtures

### Apps

| App | Purpose |
|-----|---------|
| `core` | Context processors, CSP middleware, sitemaps |
| `pages` | Homepage, About, Services, Contact, Privacy/Cookie Policy |
| `showcase` | Showcase gallery & detail pages — **also serves the AI framework page** |
| `metrics` | NPS score tracking & results page |
| `booking` | Discovery call booking system |
| `framework` | **API endpoints only** — no page views. The framework page lives at `/showcase/ai-adoption-framework/` |

### Model behavior worth knowing

Field lists are in `*/models.py`. What is not obvious from reading them:

- **`metrics.NPSMetric`** — enforces a single active row via a `save()` override
- **`booking.TimeSlot`** — the *only* source of booking availability. No external calendar sync; with no active rows the calendar shows no selectable days
- **`booking.BookingRequest`** — `confirm()` and `cancel()` save the model *and* send visitor email. `BookingRequestAdmin.save_model()` calls them on status transitions and deliberately skips `super().save_model()`
- **`showcase.ShowcaseProject`** — `live_demo_url` drives both the iframe demo section and the gallery "Live Demo" badge

### Key Dependencies

- `django-environ` — `.env` configuration
- `whitenoise` — static serving (`CompressedStaticFilesStorage` in production — non-manifest, see `docs/GOTCHAS.md`)
- `django-ratelimit` — all keyed on IP with `block=False`: contact and booking POSTs 5/hr, assessment API 10/hr, save-lead 3/hr
- `django-storages` + `boto3` — S3-compatible backend pointed at Cloudflare R2 in production
- `anthropic` — SDK for the AI readiness assessment
- `react` 19 + `@xyflow/react` v12 + Vite — framework accordion bundle
- `gunicorn` — production WSGI server, started by `start.sh`
- Tailwind CSS via `cdn.tailwindcss.com` — **all environments including production**. It is a runtime compiler, not a stylesheet: it compiles CSS in the browser on every page load, which is why CSP `script-src` needs `'unsafe-eval'`. Migrating it to a build step is open work
- AOS (Animate On Scroll) via unpkg CDN

## Media Storage

Production overrides the default storage backend entirely — `MEDIA_ROOT`/`MEDIA_URL` in `base.py` are unused there.

| Environment | `STORAGES['default']` | Uploads land in |
|---|---|---|
| dev | Django default `FileSystemStorage` | `Zimplixio_site/media/` |
| prod | `storages.backends.s3boto3.S3Boto3Storage` | **Cloudflare R2** |

Only `showcase` has `ImageField`s (project thumbnail, architecture diagram, screenshot).

**R2 environment variables** (production only, read in `settings/prod.py`):

| Variable | Maps to |
|---|---|
| `R2_ACCESS_KEY_ID` | `AWS_ACCESS_KEY_ID` |
| `R2_SECRET_ACCESS_KEY` | `AWS_SECRET_ACCESS_KEY` |
| `R2_BUCKET_NAME` | `AWS_STORAGE_BUCKET_NAME` |
| `R2_ENDPOINT_URL` | `AWS_S3_ENDPOINT_URL` |
| `R2_PUBLIC_DOMAIN` | `AWS_S3_CUSTOM_DOMAIN` |

`core/middleware.py` derives the CSP `img-src` entry from `AWS_S3_CUSTOM_DOMAIN`, so `R2_PUBLIC_DOMAIN` is the single source of truth — do not hardcode the domain. See `docs/GOTCHAS.md` for the ACL, overwrite, and cleanup behaviour of these buckets before storing anything new in them.

## UI Design System

Follow these conventions when building new UI:

- **Gradient heroes**: `bg-gradient-to-br from-indigo-700 via-indigo-800 to-gray-900` with ambient blur circles (`bg-white rounded-full blur-3xl`, ~10% opacity)
- **Section subtitle labels**: `text-indigo-300 font-medium tracking-wider uppercase text-sm` above headings
- **AOS scroll animations**: `data-aos="fade-up"` with staggered `data-aos-delay` in 100ms increments. Initialized globally in `base.html` (`once: true, duration: 700, easing: 'ease-out-cubic'`)
- **Cards**: `rounded-2xl border border-gray-200 shadow-sm` + `hover:shadow-md transition-shadow`
- **Section spacing**: `py-20`
- **CTA buttons**: `bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700 transition-colors shadow-lg shadow-indigo-600/20`
- **Dark mode**: Tailwind `darkMode: 'class'`; the `dark` class is toggled on `<html>` by `dark-mode.js` and applied pre-paint by an inline script to avoid FOUC. Use `dark:` variants on everything new — common pairings `bg-white dark:bg-gray-900`, `text-gray-900 dark:text-white`, `border-gray-200 dark:border-gray-700`, `bg-gray-50 dark:bg-gray-800`

Note the `indigo` scale is remapped to a navy/electric-blue palette in `base.html` — see `docs/GOTCHAS.md`. Never introduce raw blue hex values.

## Showcase Detail Pages — Template Architecture

Per-project flexibility comes from **template inheritance, not conditionals**:

- **`detail-base.html`** — the single structural source of truth (hero, Quick Facts strip, content sections, iframe demo, CTA), with `{% block %}` tags for every customizable string and generic defaults so unknown projects still render sensibly
- **`detail.html`** (e-commerce) and **`detail-simple-forecast.html`** — thin overrides that extend the base and replace only the blocks they need
- **`detail-framework.html`** — fully custom, does **not** extend the base. The framework page has a different structure (React components, assessment wizard). Do not refactor it to extend the base
- **Routing**: `ShowcaseDetailView.get_template_names()` maps slug → template via a `slug_map` dict, falling back to `detail-base.html`. To add a project with custom copy, add a map entry and a `detail-{slug}.html`

Never add `{% if project.slug == ... %}` branches to `detail-base.html`. Override a block instead. Block names and their defaults are visible by grepping `{% block` in the base template.

**Interactive iframe demos**: the section only renders when `live_demo_url` is set; a "System Design" toggle appears only if `system_design_url` is also set. Sandbox is `allow-scripts allow-same-origin allow-forms allow-popups`, and `demo-iframe.js` drives the loading overlay.

## About Page — World Map

An interactive D3 v7 + TopoJSON map in the "The gap we saw" section. Sources: `static/js/world-map.js`, `static/data/world-110m.json`, `static/data/us-10m.json`. D3 and TopoJSON load from unpkg; data URLs are injected via `data-world-url` / `data-us-url` on `#world-map-container`.

Three-state machine (`state.view`): `'world'` (orthographic globe, the default) → `'flat'` (Natural Earth) → `'us'` (bounding-box zoom), with mouse-out returning to the globe after 600ms.

**Critical constraints — read `world-map.js` before changing:**
- `zoomToUS` uses hardcoded continental US corners (`[-125,50]` → `[-66,24]`). **Do not switch to `path.bounds(nation)`** — Alaska and Hawaii inflate the box and break the zoom
- `clipAngle(90)` must be restored before the reverse morph, and country paths must be redrawn after `clipAngle(null)` or polar countries stay clipped
- Country pins and US city pins share one unified click handler in `drawWorld` (touch and desktop)

## Notable Static Files

Most of `static/js/` is self-describing by filename. The ones with non-obvious behavior:

| File | Why it's non-obvious |
|---|---|
| `particles-hero.js` | Custom canvas ImageData animation — no WebGL, no library. 20,000 particles across 6 twisted ribbon surfaces; mouse tilts the camera. Requires a `<div id="hero-particles">` inside the hero section |
| `booking-wizard.js` | 3-step wizard state machine. Auto-detects the visitor's timezone and converts Eastern slot times for display; populates hidden `requested_date`, `requested_time`, `visitor_timezone` inputs |
| `services-scroll.js` | Desktop-only (≥1024px) scroll-pinned horizontal panels with snap-after-pause and an `isSnapping` reentrancy guard. Mobile uses a separate tabbed layout in the same template |
| `showcase-carousel.js` | Infinite-loop carousel that clones first/last N slides; rebuilds clones on resize |
| `world-map.js` | See "About Page — World Map" |

Other assets worth flagging: `static/css/main.css` is organized by `/* === Section === */` comments; `static/images/HPE.svg` was edited to use white text (invisible on white backgrounds — this is intentional); `static/images/logo.svg` has no fixed width/height so CSS controls sizing; and **`static/dist/*` is gitignored build output**, absent from a fresh clone until `npm run build` runs.

## Security

- CSP middleware (`core.middleware.ContentSecurityPolicyMiddleware`) — `default-src 'self'`; `script-src` allows `'unsafe-inline' 'unsafe-eval'` + Tailwind CDN + unpkg.com; `style-src` allows `'unsafe-inline'` + unpkg.com + fonts.googleapis.com; `font-src 'self'` + fonts.gstatic.com; `img-src 'self' data:` + the R2 domain in production; `frame-src https:`; `frame-ancestors 'none'`
- Rate limiting on form POST endpoints (see Key Dependencies for exact rates)
- Production-only: HSTS, SSL redirect, secure cookies (`DEBUG=False`)
- Admin at `/zm-admin/`, not the default `/admin/`

## AI Adoption Framework

Served at `/showcase/ai-adoption-framework/` by `showcase`, using the custom `detail-framework.html`. The `framework` app provides only API endpoints.

- **Accordion**: React + React Flow mounted on `#framework-root` — `HubNode` centre, 6 `StageNode` circles, `GradientEdge` spokes, `StageModal` portal on click
- **React source**: `frontend/src/`. `data/stages.ts` is the canonical diagram content (the `Stage`/`Column`/`Callout`/`Table` interfaces and the `STAGES` array that `StageModal` renders); `data/questions.ts` holds the 8 assessment questions. All 6 stages use `type: 'step'` — the unused `'ongoing'` type triggers a purple palette in `StageNode`, do not use it
- **Assessment flow**: 8-question wizard on `#assessment-root` → API call → contact capture → lead saved + admin email → report revealed. The "Start Assessment" button dispatches an `assessmentStart` DOM event the wizard listens for
- **Assessment API**: `POST /framework/api/assessment/` calls `claude-sonnet-4-6` and returns a structured JSON report. Returns 503 when `ANTHROPIC_API_KEY` is empty
- **Lead capture**: `POST /framework/api/save-lead/` validates name + email (blocks disposable domains), saves an `AssessmentLead`, emails `LEAD_NOTIFICATION_EMAIL`
- **Prompts**: `framework/prompts.py` — `build_system_prompt()` encodes the framework and a strict JSON schema; `build_user_prompt(answers)` interpolates the answers

## Booking Email Flow

`booking/services.py` — `BookingEmailService`, all methods `fail_silently=False` so SMTP errors reach the logger.

| Trigger | Method | Recipient |
|---|---|---|
| Visitor submits form | `send_visitor_received()` | Visitor |
| Visitor submits form | `send_admin_notification()` | `LEAD_NOTIFICATION_EMAIL` |
| Admin sets status → `confirmed` | `send_visitor_confirmed()` | Visitor |
| Admin sets status → `cancelled` | `send_visitor_cancelled()` | Visitor |

**Timezone handling**: `BOOKING_TIMEZONE = 'America/New_York'` in `base.py` is canonical — slot times are stored and returned as Eastern. `_build_context()` builds both `time_str` (Eastern, used by the admin template) and `visitor_time_str` (converted via `format_time_in_tz()` in `booking/utils.py`, used by visitor templates), falling back to Eastern when `visitor_timezone` is empty.

**Template design**: all templates use fully inline styles and table layouts for Gmail, with `bgcolor` fallbacks since Gmail strips CSS gradients. Logos are referenced by absolute URL.

**Double-booking gap**: `available_slots_view` filters confirmed times at read time, but there is no database constraint — two pending requests for the same slot can both be confirmed. Known and deferred.

## Environment Variables

Beyond the R2 set above: `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `DATABASE_URL` (no defaults — the app will not boot without them); `CONN_MAX_AGE` (defaults to 600); `ANTHROPIC_API_KEY`; `EMAIL_BACKEND`/`EMAIL_HOST`/`EMAIL_HOST_USER`/`EMAIL_HOST_PASSWORD`/`DEFAULT_FROM_EMAIL` (Microsoft 365 SMTP in production, console backend in dev); `LEAD_NOTIFICATION_EMAIL`; `ZOOM_MEETING_URL`; `SITE_URL` (absolute links in admin emails). `BOOKING_TIMEZONE` is hardcoded in `base.py`, not an env var.

## Known Gotchas

See [`docs/GOTCHAS.md`](docs/GOTCHAS.md) for implementation quirks, removed features, and non-obvious constraints.
