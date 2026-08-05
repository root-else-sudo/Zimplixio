# Known Gotchas

Implementation quirks, removed features, and non-obvious constraints. Read this before touching an area you're unfamiliar with.

---

## Static Files & Build

- **STORAGES setting — production uses the NON-manifest backend**: `settings/prod.py` sets `staticfiles` to `whitenoise.storage.CompressedStaticFilesStorage`, not the `Manifest` variant. This is deliberate but was never a design decision — it was swapped in during Railway deploy troubleshooting (commit `6ee21d0`) and kept because it works. Trade-off: without the manifest, filenames are not content-hashed, so WhiteNoise cannot mark assets immutable and serves them with its default `max-age=60` instead of a year. Returning visitors re-fetch CSS/JS (including the React bundle) roughly every minute. Do not "fix" the docs by switching the backend — restoring `CompressedManifestStaticFilesStorage` may break the build, since it fails `collectstatic` with `ValueError: Missing staticfiles manifest entry` if any template or CSS file references a static file that does not exist. If you do restore it, verify `collectstatic` passes first.
- **One React bundle for everything**: `static/dist/framework-accordion.js` (built from `frontend/`) drives both the hub-and-spoke diagram and the assessment wizard. Rebuilding with `cd frontend && npm run build` updates both.
- **No tsParticles / no CDN for hero effect**: The hero animation is pure vanilla JS canvas (ImageData pixel writing). The tsParticles CDN was removed. `cdn.jsdelivr.net` was also removed from the CSP `script-src` directive in `core/middleware.py`.

## Media Storage (Cloudflare R2)

- **Dev and prod store uploads in completely different places**: dev writes to local disk (`Zimplixio_site/media/`), prod writes to a Cloudflare R2 bucket via `S3Boto3Storage`. `MEDIA_ROOT`/`MEDIA_URL` in `base.py` still point at the local path — they are simply not used in prod, since `STORAGES['default']` overrides the backend. A showcase image uploaded locally does not exist in production, and vice versa.
- **The CSP `img-src` domain is derived, not hardcoded**: `core/middleware.py` builds the R2 entry in the CSP `img-src` directive from `settings.AWS_S3_CUSTOM_DOMAIN`, which `prod.py` sets from the `R2_PUBLIC_DOMAIN` env var. `R2_PUBLIC_DOMAIN` is the single source of truth — rotating the bucket or its public domain only requires changing that one variable. Do not re-hardcode the domain in the middleware (it was, until it was derived). The helper tolerates the value being set with or without a scheme and strips any trailing slash, so both `pub-xxx.r2.dev` and `https://pub-xxx.r2.dev/` work.
- **Dev allows no R2 images in CSP**: `AWS_S3_CUSTOM_DOMAIN` is only defined in `prod.py`, so in dev the `img-src` directive is just `'self' data:` — correct, since dev serves media from local disk. If you point a local instance at the production bucket, also set `AWS_S3_CUSTOM_DOMAIN` locally or every R2 image will be silently blocked by CSP.
- **R2 env vars have no defaults**: `prod.py` calls `env('R2_ACCESS_KEY_ID')` etc. with no fallback, so a missing variable raises `ImproperlyConfigured` at startup and the app will not boot. This is intentional (fail loud), but it means prod settings cannot be loaded locally without the full R2 credential set — relevant when testing anything under `settings/prod.py`.
- **Uploaded media is public and permanently addressable**: `AWS_DEFAULT_ACL = 'public-read'` and `AWS_QUERYSTRING_AUTH = False` mean media URLs are unsigned, unexpiring, and readable by anyone with the link. Do not use these fields for anything non-public.
- **Same-name uploads do not overwrite**: `AWS_S3_FILE_OVERWRITE = False`, so re-uploading a file with an existing name creates a suffixed copy (`image_a1b2c3.png`) rather than replacing it. Old files are never cleaned up automatically — deleting a `ShowcaseScreenshot` row does not delete the object in R2.

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
- **Zoom call link is env-driven, not hardcoded**: `booking_visitor_confirmed.html` renders `{{ zoom_url }}`, injected by `BookingEmailService.send_visitor_confirmed()` from `settings.ZOOM_MEETING_URL` (`settings/base.py`). To change the meeting link, update the `ZOOM_MEETING_URL` env var — do not edit the template. The setting defaults to `''`, so if the env var is missing the email still sends with an empty `href` and a dead "Join Zoom Meeting" button, with no error raised.

## Content

- **Enterprise references**: Homepage and About page reference PayPal, IBM, HPE, and Intel (from Joseph's resume). "Systems X" was a previous employer no longer listed.
- **Results page hidden from UI**: The `/results/` page and URL are intact, but all nav links (header desktop, header mobile, footer) and the NPS badge (`_nps_badge.html`) are hidden until enough client data exists. Restore by re-adding the links and uncommenting `_nps_badge.html`.
