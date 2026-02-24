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
python manage.py test                              # Run all tests (24 tests)
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

### Apps

| App | Directory | Purpose |
|-----|-----------|---------|
| `core` | `Zimplixio_site/core/` | Context processors, CSP middleware, sitemaps |
| `pages` | `Zimplixio_site/pages/` | Homepage, About, Contact, Privacy/Cookie Policy |
| `services` | `Zimplixio_site/services/` | Services page (template-only, no models) |
| `showcase` | `Zimplixio_site/showcase/` | Solution showcase gallery & detail pages |
| `metrics` | `Zimplixio_site/metrics/` | NPS score tracking & results page |
| `booking` | `Zimplixio_site/booking/` | Discovery call booking system |

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
| `/zm-admin/` | django.admin | Admin interface |
| `/sitemap.xml` | django.sitemaps | XML sitemap |
| `/robots.txt` | — | TemplateView |

### Key Models

- **`pages.ContactSubmission`** — contact form submissions
- **`showcase.ShowcaseProject`** — case study projects (with `TechTag` M2M and `ShowcaseScreenshot` FK)
- **`metrics.NPSMetric`** — NPS scores (single-active enforcement via `save()` override)
- **`booking.TimeSlot`** — admin-defined weekly available windows
- **`booking.BookingRequest`** — visitor booking requests (pending/confirmed/cancelled)

### Key Dependencies

- `django-environ` — `.env` file configuration
- `whitenoise` — static file serving (CompressedManifestStaticFilesStorage in production)
- `django-ratelimit` — rate limiting on contact and booking form POSTs (5/hr per IP)
- `Pillow` — image field support for showcase uploads
- Tailwind CSS via CDN (development)
- AOS (Animate On Scroll) via unpkg CDN — global scroll-triggered animations

### UI Design System

All pages follow a consistent design language. When creating new pages, follow these conventions:

- **Gradient heroes**: Every page opens with `bg-gradient-to-br from-indigo-700 via-indigo-800 to-gray-900` hero section with ambient blur circles (`bg-white rounded-full blur-3xl` at ~10% opacity)
- **Section subtitle labels**: Uppercase indigo tracking-wider text (`text-indigo-300 font-medium tracking-wider uppercase text-sm`) above headings
- **AOS scroll animations**: All sections use `data-aos="fade-up"` with staggered `data-aos-delay` values (100ms increments). AOS is loaded globally in `base.html` with `once: true, duration: 700, easing: 'ease-out-cubic'`
- **Card styling**: `rounded-2xl border border-gray-200 shadow-sm` with `hover:shadow-md transition-shadow` for interactive cards
- **Section spacing**: Consistent `py-20` for content sections
- **CTA buttons**: `bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700 transition-colors shadow-lg shadow-indigo-600/20`

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
└── booking/                   # book form + booking_success
```

### Static JS Files

| File | Purpose |
|------|---------|
| `static/js/mobile-nav.js` | Hamburger toggle for mobile navigation |
| `static/js/cookie-consent.js` | Cookie banner with localStorage persistence |
| `static/js/faq-accordion.js` | Expand/collapse FAQ items on services page |
| `static/js/timeline.js` | Interactive career timeline on about page |

### Security

- CSP middleware (`core.middleware.ContentSecurityPolicyMiddleware`) — allows self, Tailwind CDN, unpkg.com (for AOS)
- Rate limiting on form POST endpoints (5/hr per IP)
- Production-only settings: HSTS, SSL redirect, secure cookies, CompressedManifestStaticFilesStorage (activated when `DEBUG=False`)
- Admin at `/zm-admin/` (not the default `/admin/`)

### Known Gotchas

- **`{% load static %}` required**: Any template using `{% static %}` tags (e.g., in `extra_js` blocks) must include `{% load static %}` after `{% extends %}`
- **STORAGES setting**: `CompressedManifestStaticFilesStorage` is only enabled when `DEBUG=False` — using it in dev/test without running `collectstatic` causes `ValueError: Missing staticfiles manifest entry`
- **Enterprise references**: Homepage and About page reference IBM, HPE, and Systems X (from Joseph's actual resume) — not PayPal or Intel
