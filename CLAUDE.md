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
- **`booking.TimeSlot`** — admin-defined weekly available windows (day_of_week, start_time, end_time, is_active)
- **`booking.BookingRequest`** — visitor booking requests (pending/confirmed/cancelled)
- **`framework.AssessmentLead`** — lead captures from the AI assessment (fields: name, email, submitted_at, readiness_level, answers JSON)

### Key Dependencies

- `django-environ` — `.env` file configuration
- `whitenoise` — static file serving (CompressedManifestStaticFilesStorage in production)
- `django-ratelimit` — rate limiting on contact and booking form POSTs (5/hr per IP), assessment API (3/hr per IP)
- `Pillow` — image field support for showcase uploads
- `anthropic` — Anthropic Python SDK for AI readiness assessment API calls
- `@xyflow/react` (v12) — React Flow library for hub-and-spoke diagram in framework accordion (bundled into `static/dist/framework-accordion.js`)
- `react` v19 + `react-dom` v19 — UI library for the framework accordion bundle
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

`framework/admin.py` registers `AssessmentLeadAdmin` with list display (name, email, readiness_level, submitted_at), filters, search, and readonly fields for submitted_at and answers.

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

### Other Static Files

| File | Purpose |
|------|---------|
| `static/css/main.css` | Custom styles (smooth scrolling, focus styles, accordion transitions) |
| `static/css/framework.css` | Framework-specific styles: callout boxes, accordion transitions, report blocks, badges, print rules |
| `static/dist/framework-accordion.js` | Bundled React + React Flow component — hub-and-spoke diagram with animated edges, custom nodes, stage modals; used by `detail-framework.html` |
| `static/dist/framework-accordion.css` | Extracted CSS from the React bundle (React Flow base styles + custom animations) — linked in `detail-framework.html` |
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
- **React source**: `frontend/src/` — diagram components: `FlowHub.tsx`, `HubNode.tsx`, `StageNode.tsx`, `StageIcons.tsx`, `GradientEdge.tsx`, `StageModal.tsx`, `FrameworkAccordion.tsx`. Modal sub-components: `DualColumn.tsx`, `Callout.tsx`, `ComparisonTable.tsx`. Assessment wizard components: `AssessmentWizard.tsx`, `WizardQuestion.tsx`, `LoadingScreen.tsx`, `ContactForm.tsx`, `AssessmentReport.tsx`. Hook: `frontend/src/hooks/useIsMobile.ts`. Data: `frontend/src/data/stages.ts` (diagram), `frontend/src/data/questions.ts` (8 wizard questions). Types: `frontend/src/types/assessment.ts`. Build with `cd frontend && npm run build`.
- **Fonts**: DM Serif Display + DM Sans loaded via Google Fonts in `{% block extra_head %}`
- **Content source (React)**: `frontend/src/data/stages.ts` — canonical data for the React Flow component. Defines TypeScript interfaces (`Stage`, `Column`, `Callout`, `Table`) and the `STAGES` array with structured fields (`intro`, `columns`, `callouts`, `tables`). `StageModal` renders this structured data.
- **Assessment API**: `POST /framework/api/assessment/` — rate-limited 3/hr per IP, calls `claude-sonnet-4-6`, returns structured JSON report (`readiness_level`, `readiness_summary`, `priority_stage`, `top_risks`, `first_30_days`, `one_line_verdict`)
- **Assessment user flow**: 8-question wizard (React, mounted on `#assessment-root`) → loading screen (API call) → contact capture form (name + email) → lead saved + email notification sent → report revealed. The "Start Assessment" button dispatches a `assessmentStart` custom DOM event that the React wizard listens for.
- **Lead capture**: `POST /framework/api/save-lead/` — rate-limited 10/h per IP, validates name + email (blocks disposable domains, suspicious local-parts), saves `AssessmentLead`, sends email notification to `LEAD_NOTIFICATION_EMAIL` (`joe.ugalde@zimplixio.com`). Recipient is server-side only, never exposed to the client.
- **Lead model**: `framework.AssessmentLead` — viewable at `/zm-admin/framework/assessmentlead/`
- **Prompt engineering**: `framework/prompts.py` — `build_system_prompt()` encodes full framework + strict JSON schema; `build_user_prompt(answers)` interpolates 8 user answers
- **Environment variables**: `ANTHROPIC_API_KEY` (assessment returns 503 if empty); `EMAIL_BACKEND`, `EMAIL_HOST`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL` for lead notifications. In dev, `EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend` prints emails to terminal.
- **Tech tags**: "React" and "Vite" added to the showcase project via migration `showcase/migrations/0006_add_react_vite_tags_to_framework.py`

### Known Gotchas

- **`{% load static %}` required**: Any template using `{% static %}` tags (e.g., in `extra_js` blocks) must include `{% load static %}` after `{% extends %}`
- **STORAGES setting**: `CompressedManifestStaticFilesStorage` is only enabled when `DEBUG=False` — using it in dev/test without running `collectstatic` causes `ValueError: Missing staticfiles manifest entry`
- **Enterprise references**: Homepage and About page reference IBM, HPE, and Systems X (from Joseph's actual resume) — not PayPal or Intel
- **Cross-origin iframe CSRF**: Embedded apps (e.g., recomares.com) that use POST-based actions (like Django `set_language`) will fail in the iframe due to third-party cookie blocking. This is a browser limitation — fix requires `SameSite=None` on the embedded app's cookies. The "Open in new tab" fallback link is provided.
- **Gallery thumbnails**: Use `object-contain` (not `object-cover`) so icon-style images display fully without cropping
- **HomePageView cross-app query**: `HomePageView` imports `showcase.ShowcaseProject` to fetch `featured_projects` for the homepage — changes to the showcase model can affect the homepage
- **gunicorn not in Pipfile**: The `Procfile` references gunicorn for Heroku deployment, but it is not yet listed as a dependency in `Pipfile` — add it before deploying
- **Assessment wizard is pure React**: The wizard on the framework page is fully React (`AssessmentWizard` mounted on `#assessment-root`). There is no vanilla JS fallback. The "Start Assessment" button uses `onclick="document.dispatchEvent(new CustomEvent('assessmentStart'))"` to signal the React component.
- **One React bundle for everything**: `static/dist/framework-accordion.js` (built from `frontend/`) drives both the hub-and-spoke diagram and the assessment wizard. Rebuilding with `cd frontend && npm run build` updates both.
