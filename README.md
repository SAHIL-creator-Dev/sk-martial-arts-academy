# S.K Martial Arts Academy — Website

A Django website for S.K Martial Arts Academy (Renbukai Karate-Do Federation India).
Pure advertisement/information site — no admission form or data collection beyond
an optional contact message.

## What's included
- **Home** — hero section with a YouTube video embed, program highlights,
  featured tournaments/updates, and instructor previews
- **About** — dojo story, affiliations, and the 8-belt grading legend
- **Classes** — batch schedules
- **Updates** — separate **Tournaments** (upcoming + past results) and
  **Class Updates** (schedule changes, grading results, news) sections
- **Contact** — address, instructor info, and a simple inquiry form
- **Admin panel** (`/admin/`) — manage everything below with no coding:
  - Class Programs (batches)
  - Instructors (with photo upload)
  - Tournaments (mark `is_featured` to show on the home page)
  - Class Updates (mark `is_featured` to show on the home page)
  - **Site Settings** — paste a YouTube URL here to change the hero video,
    and edit the hero tagline, without touching any code
  - Contact messages sent through the site

## Design
Dark "dojo" theme with a signature **belt-stripe motif** (white → black)
used as a recurring divider throughout the site.

## Running it locally
```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
Visit http://127.0.0.1:8000 for the site and http://127.0.0.1:8000/admin/ to manage content.

A demo admin login was used during local development and has been removed from this repository for security reasons.

Create an admin/superuser locally with:

```bash
python manage.py createsuperuser
```

Do NOT commit credentials or database files to version control. Keep secrets (e.g. DJANGO_SECRET_KEY) in environment variables or a secure secret store.

## Setting the hero video
1. Log into `/admin/`
2. Open **Site Settings**
3. Paste the academy's YouTube link (any format — watch link, share link, or
   embed link all work) into **Hero video url**, save
4. It appears automatically in the home page hero — no placeholder swap needed

## Adding tournaments & class updates
- **Tournaments** → title, date, location, description. Tick **is_featured**
  to also show it on the home page. Anything with a future date appears
  under "Upcoming"; past dates automatically move to "Past Results" on
  the Updates page.
- **Class Updates** → title, date, body text. Tick **is_featured** for it
  to also appear on the home page.

## Adding real content
1. **Class Programs** → add real batches (name, age group, schedule, description)
2. **Instructors** → add Sempai/Sensei profiles with photos
3. Replace the placeholder kanji mark in `templates/core/base.html` with
   the academy's actual logo image once uploaded, and adjust colors in
   `static/core/css/style.css` for an exact brand match if needed.

## Deploying
This is a standard Django project — deployable to Railway, Render,
PythonAnywhere, or any host that supports Django + SQLite/Postgres. Set
`DEBUG = False` and a proper `SECRET_KEY`/`ALLOWED_HOSTS` in
`skacademy/settings.py` before going live.
