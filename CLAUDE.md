# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Zimplixio is a Django 6.0.2 web application using Python 3.14 for an SMB technology consulting firm. The site includes a homepage, about page (with consultant bios and interactive career timeline), services page, solution showcase gallery, NPS results page, contact form, booking system, and legal pages. A technical specification document exists at the repo root (`Zimplixio_Technical_Development_Specification.docx`).

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
python manage.py test                              # Run all tests (47 tests)
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
| `framework` | `Zimplixio_site/framework/` | AI Adoption Framework page + AI readiness assessment API |

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
| `/showcase/<slug>/` | showcase | ShowcaseDetailView |
| `/results/` | metrics | NPSResultsView |
| `/book/` | booking | BookCallView |
| `/book/success/` | booking | BookingSuccessView |
| `/framework/api/assessment/` | framework | assessment_view (POST, Anthropic API) |
| `/zm-admin/` | django.admin | Admin interface |
| `/sitemap.xml` | django.sitemaps | XML sitemap |
| `/robots.txt` | — | TemplateView |

### Key Models

- **`pages.ContactSubmission`** — contact form submissions (fields: name, email, company, message, submitted_at, is_read)
- **`showcase.TechTag`** — technology labels for project tagging (M2M with ShowcaseProject)
- **`showcase.ShowcaseProject`** — case study projects. Includes `live_demo_url` and `system_design_url` for interactive iframe demos on detail pages
- **`showcase.ShowcaseScreenshot`** — screenshot images linked to a ShowcaseProject (FK)
- **`metrics.NPSMetric`** — NPS scores (single-active enforcement via `save()` override)
- **`booking.TimeSlot`** — admin-defined weekly available windows (day_of_week, start_time, end_time, is_active)
- **`booking.BookingRequest`** — visitor booking requests (pending/confirmed/cancelled)

### Key Dependencies

- `django-environ` — `.env` file configuration
- `whitenoise` — static file serving (CompressedManifestStaticFilesStorage in production)
- `django-ratelimit` — rate limiting on contact and booking form POSTs (5/hr per IP), assessment API (3/hr per IP)
- `Pillow` — image field support for showcase uploads
- `anthropic` — Anthropic Python SDK for AI readiness assessment API calls
- `gunicorn` — WSGI server for production (referenced in `Procfile`, not yet in `Pipfile`)
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

### UI Design System

All pages follow a consistent design language. When creating new pages, follow these conventions:

- **Gradient heroes**: Every page opens with `bg-gradient-to-br from-indigo-700 via-indigo-800 to-gray-900` hero section with ambient blur circles (`bg-white rounded-full blur-3xl` at ~10% opacity)
- **Section subtitle labels**: Uppercase indigo tracking-wider text (`text-indigo-300 font-medium tracking-wider uppercase text-sm`) above headings
- **AOS scroll animations**: All sections use `data-aos="fade-up"` with staggered `data-aos-delay` values (100ms increments). AOS is loaded globally in `base.html` with `once: true, duration: 700, easing: 'ease-out-cubic'`
- **Card styling**: `rounded-2xl border border-gray-200 shadow-sm` with `hover:shadow-md transition-shadow` for interactive cards
- **Section spacing**: Consistent `py-20` for content sections
- **CTA buttons**: `bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700 transition-colors shadow-lg shadow-indigo-600/20`

### Showcase Detail Page — Interactive Demos

The showcase detail page (`templates/showcase/detail.html`) supports interactive iframe demos:

- **Conditional rendering**: The iframe section only appears when `live_demo_url` is set on a `ShowcaseProject`
- **Toggle buttons**: "Live App" (default) + "System Design" (only if `system_design_url` is set), styled like gallery filter pills
- **Iframe sandbox**: `allow-scripts allow-same-origin allow-forms allow-popups` for security
- **Loading overlay**: Spinner shown until iframe fires `load` event, driven by `static/js/demo-iframe.js`
- **Gallery badge**: Projects with `live_demo_url` show a green "Live Demo" badge on gallery cards
- First showcased project: **recomares.com** (e-commerce platform with `/system-design` page)

### About Page — Special Features

The About page (`templates/pages/about.html`) has unique components beyond the standard design system:

- **Consultant bio card**: Photo placeholder with initials, certifications list, LinkedIn link, expertise pills, education details
- **Interactive career timeline**: Expand/collapse nodes driven by `static/js/timeline.js`, with CSS `max-height` transitions and gradient accent line
- **Stat cards**: Animated gradient-text numbers (17+ years, 20+ apps, etc.)
- Real data from Joseph Ugalde's resume (HPE, IBM, MICIT, Systems X career path). A second consultant bio is planned.

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
├── services/                  # services page with tier cards + FAQ accordion
├── showcase/                  # gallery (filterable) + detail pages
├── metrics/                   # NPS results page
├── booking/                   # book form + booking_success
└── framework/                 # AI adoption framework page + assessment
```

### Static JS Files

| File | Purpose |
|------|---------|
| `static/js/mobile-nav.js` | Hamburger toggle for mobile navigation |
| `static/js/cookie-consent.js` | Cookie banner with localStorage persistence |
| `static/js/faq-accordion.js` | Expand/collapse FAQ items on services page |
| `static/js/timeline.js` | Interactive career timeline on about page |
| `static/js/demo-iframe.js` | Iframe loading overlay + toggle buttons on showcase detail page |
| `static/js/framework-accordion.js` | Expand/collapse stage cards on AI framework page |
| `static/js/framework-assessment.js` | Form wizard, API call, loading animation, report rendering for AI assessment |

### Other Static Files

| File | Purpose |
|------|---------|
| `static/css/main.css` | Custom styles (smooth scrolling, focus styles, accordion transitions) |
| `static/css/framework.css` | Framework-specific styles: callout boxes, accordion transitions, report blocks, badges, print rules |
| `static/manifest.json` | PWA web app manifest with Zimplixio branding |

### Security

- CSP middleware (`core.middleware.ContentSecurityPolicyMiddleware`) — `default-src 'self'`; `script-src` allows `'unsafe-inline' 'unsafe-eval'` + Tailwind CDN + unpkg.com; `style-src` allows `'unsafe-inline'` + unpkg.com + fonts.googleapis.com; `font-src 'self'` + fonts.gstatic.com; `img-src 'self' data:`; `frame-src https:`; `frame-ancestors 'none'`
- Rate limiting on form POST endpoints (5/hr per IP)
- Production-only settings: HSTS, SSL redirect, secure cookies, CompressedManifestStaticFilesStorage (activated when `DEBUG=False`)
- Admin at `/zm-admin/` (not the default `/admin/`)

### AI Adoption Framework (Embedded in Showcase)

The framework content is embedded directly in the showcase detail page at `/showcase/ai-adoption-framework/` via a custom template (`templates/showcase/detail-framework.html`). The standalone page at `/framework/` no longer exists.

- **Custom template routing**: `ShowcaseDetailView.get_template_names()` returns `detail-framework.html` when `slug == 'ai-adoption-framework'`; `get_context_data()` injects `stages` from `framework.content.STAGES` and `api_available`
- **Page structure**: Hero (with "Try the Assessment" scroll button) → Core Philosophy → Framework Accordion (6 stages) → Closing Quote → Case Study sections → CTA Panel → Assessment wizard
- **Fonts**: DM Serif Display + DM Sans loaded via Google Fonts in `{% block extra_head %}`
- **Content source**: `framework/content.py` — all stage content hardcoded as Python dicts with `body_html` rendered via `|safe`
- **Assessment API**: `POST /framework/api/assessment/` — rate-limited 3/hr per IP, calls `claude-sonnet-4-6`, returns structured JSON report
- **Prompt engineering**: `framework/prompts.py` — system prompt encodes full framework + strict JSON schema; user prompt interpolates 8 answers
- **No models**: The framework app has no database models — content is in `content.py`, the showcase gallery entry is created via data migration
- **Environment variable**: `ANTHROPIC_API_KEY` in `.env` — assessment returns 503 if empty

### Known Gotchas

- **`{% load static %}` required**: Any template using `{% static %}` tags (e.g., in `extra_js` blocks) must include `{% load static %}` after `{% extends %}`
- **STORAGES setting**: `CompressedManifestStaticFilesStorage` is only enabled when `DEBUG=False` — using it in dev/test without running `collectstatic` causes `ValueError: Missing staticfiles manifest entry`
- **Enterprise references**: Homepage and About page reference IBM, HPE, and Systems X (from Joseph's actual resume) — not PayPal or Intel
- **Cross-origin iframe CSRF**: Embedded apps (e.g., recomares.com) that use POST-based actions (like Django `set_language`) will fail in the iframe due to third-party cookie blocking. This is a browser limitation — fix requires `SameSite=None` on the embedded app's cookies. The "Open in new tab" fallback link is provided.
- **Gallery thumbnails**: Use `object-contain` (not `object-cover`) so icon-style images display fully without cropping
- **HomePageView cross-app query**: `HomePageView` imports `showcase.ShowcaseProject` to fetch `featured_projects` for the homepage — changes to the showcase model can affect the homepage
- **gunicorn not in Pipfile**: The `Procfile` references gunicorn for Heroku deployment, but it is not yet listed as a dependency in `Pipfile` — add it before deploying
