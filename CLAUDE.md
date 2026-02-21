# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Zimplixio is a Django 6.0.2 web application using Python 3.14. It currently has a single app (`website`) that is scaffolded but not yet implemented. A technical specification document exists at the repo root (`Zimplixio_Technical_Development_Specification.docx`).

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
python manage.py test                  # Run all tests
python manage.py test website          # Run tests for the website app
python manage.py test website.tests.TestClassName.test_method  # Run a single test
```

## Architecture

- **Django project package**: `Zimplixio_site/Zimplixio_site/` — settings, root URL conf, WSGI/ASGI entry points
- **Main app**: `Zimplixio_site/website/` — the primary application (models, views, templates, tests)
- **Database**: SQLite3 (`Zimplixio_site/db.sqlite3`)
- **WSGI entry**: `Zimplixio_site.wsgi.application`
- **ASGI entry**: `Zimplixio_site.asgi.application`

The project follows standard Django MTV (Model-Template-View) conventions. URL routing starts in `Zimplixio_site/urls.py` which currently only maps `/admin/`.
