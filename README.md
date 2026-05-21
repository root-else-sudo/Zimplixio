# Zimplixio

The official website for **Zimplixio**, an SMB technology consulting firm. Built with Django 6 and Python 3.14, the site serves as both a marketing platform and a live showcase of client work — featuring an interactive solution gallery, a discovery call booking system, an AI-powered readiness assessment, and a contact pipeline.

**Live site:** [zimplixio.com](https://zimplixio.com)

---

## Features

- **Homepage** — Hero with animated particle canvas, featured showcase carousel, NPS score badge, and CTA
- **Solution Showcase** — Filterable gallery of case studies with live iframe demos (recomares.com, simple-forecast.com) and interactive system design views
- **AI Adoption Framework** — 6-stage methodology navigator (React + React Flow) paired with an 8-question AI readiness assessment powered by Claude
- **Booking System** — Calendly-style 3-step wizard (calendar → time slot → contact form) with admin-managed availability and full email notification flow
- **Contact Form** — Rate-limited submission pipeline with admin read-tracking
- **About Page** — Values flip cards, interactive world map, and career stats
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
| Frontend | Tailwind CSS (CDN), AOS animations |
| React bundle | React 19, Vite, @xyflow/react v12 |
| AI | Anthropic Claude (`claude-sonnet-4-6`) |
| Media storage | Cloudflare R2 (via django-storages) |
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
├── railway.toml                    # Railway build + start commands
├── start.sh                        # Production startup: collectstatic → migrate → gunicorn
├── Pipfile                         # Python dependencies
├── Pipfile.lock                    # Pinned dependency versions
├── docs/                           # Project documentation
│   └── GOTCHAS.md                  # Implementation quirks and non-obvious constraints
├── frontend/                       # React source (Vite)
│   └── src/
│       ├── components/             # FlowHub, StageModal, AssessmentWizard, etc.
│       └── data/                   # stages.ts, questions.ts
└── Zimplixio_site/
    ├── manage.py
    ├── .env                        # Environment variables (gitignored — create manually)
    ├── Zimplixio_site/             # Django project package (settings, urls, wsgi)
    │   └── settings/
    │       ├── base.py             # Shared settings
    │       ├── dev.py              # Local development overrides
    │       └── prod.py             # Production hardening (HSTS, SSL, etc.)
    ├── core/                       # Context processors, CSP middleware, sitemaps
    ├── pages/                      # Homepage, About, Services, Contact, legal pages
    ├── showcase/                   # Solution gallery & detail pages
    ├── metrics/                    # NPS score tracking
    ├── booking/                    # Discovery call booking wizard + email flow
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

# 2. Create the virtual environment inside the project folder
export PIPENV_VENV_IN_PROJECT=1
pipenv --python /path/to/python3.14 install
pipenv shell

# 3. Create and configure the environment file
# Create Zimplixio_site/.env — see Environment Variables section below for required keys

# 4. Run migrations
cd Zimplixio_site
python manage.py migrate

# 5. Create a superuser (for admin access)
python manage.py createsuperuser

# 6. Start the dev server
python manage.py runserver
```

The site will be available at `http://localhost:8000`. Admin at `http://localhost:8000/zm-admin/`.

> **Email in dev:** `EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend` prints all outbound emails to the terminal instead of sending them. This is the default and requires no SMTP setup locally.

### Rebuilding the React Bundle

The framework accordion and AI assessment wizard are bundled from `frontend/src/`:

```bash
cd frontend
npm install
npm run build
```

Built files are written to `Zimplixio_site/static/dist/` and served by Django.

### Running Tests

```bash
cd Zimplixio_site
python manage.py test                              # All tests
python manage.py test pages                        # Single app
python manage.py test showcase.tests.ShowcaseTests # Single class
```

---

## Environment Variables

Create `Zimplixio_site/.env` with the following variables:

### Core

| Variable | Required | Dev value | Description |
|----------|----------|-----------|-------------|
| `DJANGO_SETTINGS_MODULE` | Yes | `Zimplixio_site.settings.dev` | Use `settings.prod` on Railway |
| `SECRET_KEY` | Yes | Any string | Generate a long random key for production |
| `DEBUG` | Yes | `True` | Always `False` in production |
| `ALLOWED_HOSTS` | Yes | `localhost,127.0.0.1` | Comma-separated hostnames |
| `DATABASE_URL` | Yes | `postgres://...` | PostgreSQL connection string |

### Email (Microsoft 365)

| Variable | Dev value | Prod value | Description |
|----------|-----------|------------|-------------|
| `EMAIL_BACKEND` | `django.core.mail.backends.console.EmailBackend` | `django.core.mail.backends.smtp.EmailBackend` | Console prints to terminal; SMTP sends real emails |
| `EMAIL_HOST` | `smtp.office365.com` | `smtp.office365.com` | Microsoft 365 SMTP server |
| `EMAIL_PORT` | `587` | `587` | STARTTLS port |
| `EMAIL_USE_TLS` | `True` | `True` | Required for Office 365 |
| `EMAIL_HOST_USER` | `team@zimplixio.com` | `team@zimplixio.com` | Sending mailbox |
| `EMAIL_HOST_PASSWORD` | *(mailbox password)* | *(mailbox password)* | Microsoft 365 mailbox password |
| `DEFAULT_FROM_EMAIL` | `team@zimplixio.com` | `team@zimplixio.com` | From address on all outbound emails |

### Business Settings

| Variable | Required | Description |
|----------|----------|-------------|
| `LEAD_NOTIFICATION_EMAIL` | No | Receives admin notifications for new booking requests (e.g. `joe.ugalde@zimplixio.com`) |
| `ZOOM_MEETING_URL` | No | Zoom link included in booking confirmation emails sent to visitors |
| `SITE_URL` | No | Base URL used to build absolute links in emails. Dev: `http://localhost:8000`. Prod: `https://zimplixio.com` |
| `ANTHROPIC_API_KEY` | No | Enables AI readiness assessment — returns 503 if absent |

### Cloudflare R2 (Media Storage)

| Variable | Description |
|----------|-------------|
| `R2_ACCESS_KEY_ID` | R2 API access key |
| `R2_SECRET_ACCESS_KEY` | R2 API secret |
| `R2_BUCKET_NAME` | R2 bucket name |
| `R2_ENDPOINT_URL` | R2 S3-compatible endpoint URL |
| `R2_PUBLIC_DOMAIN` | Public domain for serving media files |

---

## Booking Flow

The booking system handles the full discovery call lifecycle:

1. **Visitor submits booking** (`/book/`) → acknowledgement email sent to visitor + notification email sent to `LEAD_NOTIFICATION_EMAIL`
2. **Admin reviews** at `/zm-admin/booking/bookingrequest/` — notification email includes a direct link to the booking record
3. **Admin confirms** by changing status to `Confirmed` → confirmation email sent to visitor with Zoom link

Available time slots are configured via `TimeSlot` records in the admin (`/zm-admin/booking/timeslot/`).

---

## Deployment (Railway)

Deployment is configured via `railway.toml` and `start.sh`:

**Build** (`railway.toml`):
```
cd frontend && npm install && npm run build
```

**Start** (`start.sh`):
```
collectstatic → migrate → gunicorn
```

All environment variables are set in the Railway dashboard under **Variables** — no `.env` file is used on the server. See the Environment Variables section above for the full list with production values.

---

## Admin

The admin interface is at `/zm-admin/` (not the default `/admin/`).

| Section | Purpose |
|---------|---------|
| **Showcase** | Create/edit case study projects, upload media, manage tech tags |
| **Booking → TimeSlots** | Configure weekly availability windows |
| **Booking → BookingRequests** | Review pending requests, confirm to trigger visitor email |
| **Metrics** | Set the active NPS score |
| **Contact** | Read and track contact form submissions |
| **Framework → AssessmentLeads** | View AI assessment leads with readiness levels and answers |

---

## License

Private — all rights reserved. © Zimplixio.
