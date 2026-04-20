# Zimplixio

The official website for **Zimplixio**, an SMB technology consulting firm. Built with Django 6 and Python 3.14, the site serves as both a marketing platform and a live showcase of client work — featuring an interactive solution gallery, a discovery call booking system, an AI-powered readiness assessment, and a contact pipeline.

**Live site:** [zimplixio.com](https://zimplixio.com)

---

## Features

- **Homepage** — Hero with animated particle canvas, featured showcase projects, NPS score badge, and CTA
- **Solution Showcase** — Filterable gallery of case studies with live iframe demos (recomares.com, simple-forecast.com) and interactive system design views
- **AI Adoption Framework** — 6-stage methodology navigator (React + React Flow) paired with an 8-question AI readiness assessment powered by Claude
- **Booking System** — Calendly-style 3-step wizard (calendar → time slot → contact form) backed by admin-managed availability
- **Contact Form** — Rate-limited submission pipeline with admin read-tracking
- **About Page** — Founder bios, values flip cards, interactive world map, and career stats
- **Services Page** — Scroll-pinned panel layout (desktop) with tabbed interface (mobile) and FAQ accordion
- **NPS Results Page** — Live NPS metric display
- **Dark Mode** — Full site dark mode toggle with FOUC prevention
- **PWA** — Web app manifest for installability

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Django 6.0.3, Python 3.14 |
| Database | PostgreSQL |
| Frontend framework | Tailwind CSS (CDN), AOS animations |
| React bundle | React 19, Vite, @xyflow/react v12 |
| AI | Anthropic Claude (`claude-sonnet-4-6`) |
| Static files | WhiteNoise (CompressedManifestStaticFilesStorage in prod) |
| Rate limiting | django-ratelimit |
| Image handling | Pillow |
| Config | django-environ |
| WSGI | Gunicorn |
| Deployment | Railway |

---

## Project Structure

```
Zimplixio/
├── Procfile                        # Railway release + web commands
├── Pipfile                         # Python dependencies
├── Pipfile.lock                    # Pinned dependency versions
├── frontend/                       # React source (Vite)
│   └── src/
│       ├── components/             # FlowHub, StageModal, AssessmentWizard, etc.
│       └── data/                   # stages.ts, questions.ts
└── Zimplixio_site/
    ├── manage.py
    ├── .env.example                # Environment variable reference (copy to .env)
    ├── Zimplixio_site/             # Django project package (settings, urls, wsgi)
    │   └── settings/
    │       ├── base.py             # Shared settings
    │       ├── dev.py              # Local development overrides
    │       └── prod.py             # Production hardening (HSTS, SSL, etc.)
    ├── core/                       # Context processors, CSP middleware, sitemaps
    ├── pages/                      # Homepage, About, Services, Contact, legal pages
    ├── showcase/                   # Solution gallery & detail pages
    ├── metrics/                    # NPS score tracking
    ├── booking/                    # Discovery call booking wizard
    ├── framework/                  # AI Adoption Framework + assessment API
    ├── templates/                  # Project-level templates (all apps)
    ├── static/                     # CSS, JS, images, React dist bundle
    └── media/                      # Uploaded thumbnails, screenshots, diagrams
```

---

## Getting Started

### Prerequisites

- Python 3.14
- Pipenv
- PostgreSQL (local instance)
- Node.js (only needed to rebuild the React bundle)

### Local Setup

```bash
# 1. Clone the repo
git clone <repo-url>
cd Zimplixio

# 2. Install Python dependencies
pipenv install
pipenv shell

# 3. Configure environment
cp Zimplixio_site/.env.example Zimplixio_site/.env
# Edit .env — fill in SECRET_KEY, DATABASE_URL, and ANTHROPIC_API_KEY at minimum

# 4. Run migrations
cd Zimplixio_site
python manage.py migrate

# 5. Create a superuser (for admin access)
python manage.py createsuperuser

# 6. Start the dev server
python manage.py runserver
```

The site will be available at `http://localhost:8000`. Admin at `http://localhost:8000/zm-admin/`.

### Rebuilding the React Bundle

The framework accordion and AI assessment wizard are bundled from `frontend/src/`:

```bash
cd frontend
npm install
npm run build
```

The built files are written to `Zimplixio_site/static/dist/` and served by Django.

### Running Tests

```bash
cd Zimplixio_site
python manage.py test                              # All tests
python manage.py test pages                        # Single app
python manage.py test showcase.tests.ShowcaseTests # Single class
```

---

## Environment Variables

See `.env.example` for the full reference with descriptions and dev/prod guidance.

| Variable | Required | Description |
|----------|----------|-------------|
| `DJANGO_SETTINGS_MODULE` | Yes | `Zimplixio_site.settings.dev` locally, `Zimplixio_site.settings.prod` on Railway |
| `SECRET_KEY` | Yes | Django secret key — generate a fresh one for production |
| `DEBUG` | Yes | `True` for dev, `False` for prod |
| `ALLOWED_HOSTS` | Yes | Comma-separated list of allowed hosts |
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `ANTHROPIC_API_KEY` | No | Enables the AI readiness assessment (returns 503 if absent) |
| `ZOOM_MEETING_URL` | No | Zoom link included in booking confirmation emails |
| `EMAIL_BACKEND` | No | Defaults to console backend in dev |
| `EMAIL_HOST` | No | SMTP host for transactional emails |
| `EMAIL_HOST_USER` | No | SMTP username |
| `EMAIL_HOST_PASSWORD` | No | SMTP password |
| `DEFAULT_FROM_EMAIL` | No | Sender address for outbound emails |
| `LEAD_NOTIFICATION_EMAIL` | No | Recipient for assessment lead notifications |

---

## Deployment (Railway)

The `Procfile` handles the full release pipeline:

```
release: cd frontend && npm ci && npm run build && cd ../Zimplixio_site && DJANGO_SETTINGS_MODULE=Zimplixio_site.settings.prod python manage.py migrate --noinput && DJANGO_SETTINGS_MODULE=Zimplixio_site.settings.prod python manage.py collectstatic --noinput
web: cd Zimplixio_site && DJANGO_SETTINGS_MODULE=Zimplixio_site.settings.prod gunicorn Zimplixio_site.wsgi --bind 0.0.0.0:$PORT
```

On every deploy: the React bundle is rebuilt, migrations run, static files are collected, then Gunicorn starts.

All environment variables are configured in the Railway dashboard under **Variables** — no `.env` file is used on the server.

---

## Admin

The admin interface is available at `/zm-admin/` (not the default `/admin/`).

Key admin tasks:

- **Showcase** — Create/edit case study projects, upload thumbnails and screenshots, manage tech tags
- **Booking** — Configure available time slots (`TimeSlot`), review and confirm booking requests (`BookingRequest`). Confirming a booking triggers a visitor confirmation email.
- **Metrics** — Set the active NPS score
- **Contact** — Read and track contact form submissions
- **Framework leads** — View AI assessment leads with readiness levels and answers

---

## License

Private — all rights reserved. © Zimplixio.
