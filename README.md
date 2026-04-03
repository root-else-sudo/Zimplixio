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
- **About Page** — Consultant bio, interactive career timeline, and animated stat cards
- **Services Page** — Tier cards and FAQ accordion
- **NPS Results Page** — Live NPS metric display
- **Dark Mode** — Full site dark mode toggle with FOUC prevention
- **PWA** — Web app manifest for installability

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Django 6.0.2, Python 3.14 |
| Database | SQLite3 (dev) |
| Frontend framework | Tailwind CSS (CDN), AOS animations |
| React bundle | React 19, Vite, @xyflow/react v12 |
| AI | Anthropic Claude (`claude-sonnet-4-6`) |
| Static files | WhiteNoise (CompressedManifestStaticFilesStorage in prod) |
| Rate limiting | django-ratelimit |
| Image handling | Pillow |
| Config | django-environ |
| WSGI | Gunicorn |
| Deployment | Heroku |

---

## Project Structure

```
Zimplixio/
├── Procfile                        # Heroku release + web commands
├── Pipfile                         # Python dependencies
├── frontend/                       # React source (Vite)
│   └── src/
│       ├── components/             # FlowHub, StageModal, AssessmentWizard, etc.
│       └── data/                   # stages.ts, questions.ts
└── Zimplixio_site/
    ├── manage.py
    ├── Zimplixio_site/             # Django project package (settings, urls, wsgi)
    ├── core/                       # Context processors, CSP middleware, sitemaps
    ├── pages/                      # Homepage, About, Contact, legal pages
    ├── services/                   # Services page
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
- Node.js (for rebuilding the React bundle)

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
# Edit .env — set SECRET_KEY, DEBUG=True, ANTHROPIC_API_KEY

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

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | Yes | Django secret key |
| `DEBUG` | Yes | `True` for dev, `False` for prod |
| `ALLOWED_HOSTS` | Yes | Comma-separated list of allowed hosts |
| `ANTHROPIC_API_KEY` | No | Enables the AI readiness assessment (returns 503 if absent) |
| `EMAIL_BACKEND` | No | Defaults to console backend in dev |
| `EMAIL_HOST` | No | SMTP host for transactional emails |
| `EMAIL_HOST_USER` | No | SMTP username |
| `EMAIL_HOST_PASSWORD` | No | SMTP password |
| `DEFAULT_FROM_EMAIL` | No | Sender address for outbound emails |
| `LEAD_NOTIFICATION_EMAIL` | No | Recipient for assessment lead notifications |

---

## Deployment (Heroku)

The `Procfile` handles the full release pipeline:

```
release: cd frontend && npm ci && npm run build && cd ../Zimplixio_site && python manage.py migrate --noinput && python manage.py collectstatic --noinput
web: cd Zimplixio_site && gunicorn Zimplixio_site.wsgi --bind 0.0.0.0:$PORT
```

On every deploy: frontend is rebuilt, migrations run, static files are collected, then Gunicorn starts.

> **Note:** `gunicorn` is declared in `Pipfile` and installed via `pipenv install`.

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
