# Known Gotchas

Implementation quirks, removed features, and non-obvious constraints. Read this before touching an area you're unfamiliar with.

---

## Static Files & Build

- **STORAGES setting**: `CompressedManifestStaticFilesStorage` is only enabled when `DEBUG=False` — using it in dev/test without running `collectstatic` causes `ValueError: Missing staticfiles manifest entry`
- **One React bundle for everything**: `static/dist/framework-accordion.js` (built from `frontend/`) drives both the hub-and-spoke diagram and the assessment wizard. Rebuilding with `cd frontend && npm run build` updates both.
- **No tsParticles / no CDN for hero effect**: The hero animation is pure vanilla JS canvas (ImageData pixel writing). The tsParticles CDN was removed. `cdn.jsdelivr.net` was also removed from the CSP `script-src` directive in `core/middleware.py`.

## Templates & Django

- **`{% load static %}` in partials**: `_header.html` includes its own `{% load static %}` at the top — required because partials do not inherit the parent template's loaded tags.
- **Hero particle effect — `#hero-particles` div required**: `particles-hero.js` looks for `<div id="hero-particles">` inside the hero `<section>`. The div must be present with `position:absolute; inset:0; z-index:1; pointer-events:none` (defined in `main.css`). All 9 hero pages have this div. The script listens on `document` (not the canvas) for mousemove since the canvas has `pointer-events:none`.
- **HomePageView cross-app query**: `HomePageView` imports `showcase.ShowcaseProject` to fetch `featured_projects` for the homepage — changes to the showcase model can affect the homepage.
- **Stray characters in project-specific templates**: When editing `detail-simple-forecast.html` or `detail.html` manually, watch for stray characters outside `{% block %}` tags — they will be silently rendered into the page.

## Showcase Detail Templates

- **Inheritance, not conditionals**: Do not add slug-based `{% if project.slug == ... %}` conditionals inside `detail-base.html` for per-project copy. The correct pattern is to override `{% block %}` tags in the project's own template. Add a new entry to `slug_map` in `ShowcaseDetailView.get_template_names()` when adding a new project template.
- **`detail-framework.html` does not extend `detail-base.html`**: The framework page has a completely different structure and is a standalone template. Do not attempt to refactor it to extend the base.
- **Gallery thumbnails**: Use `object-contain` (not `object-cover`) so icon-style images display fully without cropping.
- **Cross-origin iframe CSRF**: Embedded apps (e.g., recomares.com) that use POST-based actions (like Django `set_language`) will fail in the iframe due to third-party cookie blocking. The "Open in new tab" fallback link is provided.
- **Iframe-embedded showcase apps must allow framing**: Any external app added to the showcase with `live_demo_url` must not send `X-Frame-Options: SAMEORIGIN`. Remove `XFrameOptionsMiddleware` from the embedded app's `MIDDLEWARE` setting to allow cross-origin embedding.
- **Showcase carousel clones require N ≥ visible count**: The carousel clones the first/last N slides (3 desktop, 2 tablet, 1 mobile). With only 3 projects it still works, but sparse if fewer.
- **Showcase carousel auto-play pauses on hover/focus**: Stays paused if the user tabs in and doesn't tab out — intentional for accessibility.

## Design System & CSS

- **Color palette — Tailwind `indigo` remapped**: The `indigo` color scale in `base.html` Tailwind config is overridden to a navy/electric-blue palette (`indigo-600 = #2563eb`, `indigo-800 = #0f2044`, `indigo-900 = #0a1628`). Do not add raw hex values for blue; use `indigo-*` classes.
- **Logo SVG sizing**: `static/images/logo.svg` has no fixed `width`/`height` attributes (removed so CSS controls size). The viewBox is cropped to the content area (`278 337 1656 426`).
- **HPE logo has white text**: The HPE SVG (`static/images/HPE.svg`) was modified to use `fill:#ffffff` for text paths. The green icon element (`fill:#00b188`) was not changed. If the logo appears invisible on white backgrounds, this is why.
- **Credential logo sizing is per-file**: PayPal/IBM/HPE use `.credential-logo-xl` (280×104px) and Intel uses `.credential-logo` (140×52px) because the SVGs have different native aspect ratios.
- **`.logo-magnetic` on multiple elements**: Applied to the logo `<a>` and desktop "Book a Call" button in `_header.html`. Do not apply to the mobile "Book a Call" (inside the dropdown menu).
- **PDCA section — no GSAP, no JS file**: Pure CSS + AOS only. Do not add JS animation libraries — `cdnjs.cloudflare.com` is not in the CSP `script-src` allowlist.
- **PDCA description reveal is hover-only on desktop**: `.pdca-desc` uses `max-height: 0` → `max-height: 200px` on `:hover`. On mobile (≤767px), descriptions are always visible via CSS override.

## Services Page

- **Two layouts coexist**: Desktop (≥1024px) uses a scroll-pinned horizontal panel layout driven by `services-scroll.js`. Mobile uses a tabbed layout with an inline `zSwitch(index)` function. Both live in `services.html`. Do not use AOS on either section.
- **Five CSS naming prefixes**: `svc-*` (scroll panel chrome), `z-*` (mobile tabbed layout), `vis-*` (deliverable bullet lists), `p01-*`–`p05-*` (animated widget grids), `wte-*` (What to Expect timeline). Do not mix them.
- **Widget color variants use modifier classes**: Colors are BEM-style modifier classes in `main.css` (e.g. `.p01-ms-dot--blue/teal/purple`). Do not use inline styles.
- **No Pricing Signal section**: It was removed. Do not re-add it.

## About Page

- **`timeline.js` is unused**: The "The Journey" section was removed. `static/js/timeline.js` is no longer loaded in `about.html`. File exists on disk but serves no purpose.
- **Founder cards have no `--reverse` variant**: Both cards use photo-left layout. There is no `.founder-card--reverse` class in the HTML or CSS.
- **Values flip cards — hover + click both trigger flip**: CSS `:hover` (desktop) AND JS `.is-flipped` class (click/tap). Do not remove either — hover gives instant desktop response; `.is-flipped` makes it work on touch.

## AI Adoption Framework (React)

- **Stage `type: 'ongoing'` activates purple palette**: All 6 stages use `type: 'step'`. Do not change any stage to `type: 'ongoing'` unless you intend the purple visual treatment.
- **Stage node numbers — no glow, no eyebrow**: Only the sequential number (`01`–`06`) via `NODE_STEP`. No "STEP" label above it, no `textShadow` glow. Do not re-add these.
- **React Flow scroll blocking**: `FlowHub.tsx` sets `preventScrolling={false}` on `<ReactFlow>`. Without this, React Flow intercepts wheel events and causes scroll jank. Do not remove this prop.

## Booking

- **Availability is DB-only**: No Google Calendar or external calendar sync. Availability comes entirely from `TimeSlot` records in the admin. Create at least one active `TimeSlot` or the calendar will show no selectable days.
- **`requested_date`/`requested_time` are hidden inputs**: Populated by JS before form submission. If JS is disabled the form cannot be submitted — this is by design.
- **Confirmation email triggers on admin save**: `BookingRequestAdmin.save_model()` detects the `pending → confirmed` transition and sends the confirmation email.
- **Zoom call link is hardcoded**: `templates/emails/booking_visitor_confirmed.html` contains a fixed Zoom link. Update this template if the meeting link changes.

## Content

- **Enterprise references**: Homepage and About page reference PayPal, IBM, HPE, and Intel (from Joseph's resume). "Systems X" was a previous employer no longer listed.
- **Results page hidden from UI**: The `/results/` page and URL are intact, but all nav links (header desktop, header mobile, footer) and the NPS badge (`_nps_badge.html`) are hidden until enough client data exists. Restore by re-adding the links and uncommenting `_nps_badge.html`.
