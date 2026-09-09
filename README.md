# ihavenoideawhatidoanymore.com

**The platform for forward-deployed operators.**

A directory of people who added AI to a job they still have — the CMO who now
prototypes the product, the CFO running finance from a terminal, the retention
lead building the flows she used to brief out. Companies haven't restructured
around these people, so there is nowhere obvious for them to find each other.

Members post a profile, say what they also do on top of the job, and can be
contacted about work without publishing their email address.

**Live:** https://www.ihavenoideawhatidoanymore.com

**Picking this up cold? Read [`docs/handoff-2026-09-09.md`](docs/handoff-2026-09-09.md) first** — it
carries the settled positioning and the traps that cost real time.

## Run it locally

```bash
uv venv --python 3.12
uv pip install fastapi "uvicorn[standard]" jinja2 sqlalchemy python-multipart
.venv/bin/python seed.py                    # optional: six example profiles
.venv/bin/uvicorn app.main:app --reload
```

Then open http://127.0.0.1:8000

With no environment variables set it uses a local SQLite file (`noidea.db`) and
prints emails to the console instead of sending them. That's the whole local
setup — nothing else to configure.

## Deploy to Railway

1. Push this repo to GitHub.
2. New Railway project → Deploy from GitHub repo. It detects Python and uses
   `railway.json` (health check on `/healthz`).
3. Add a **Postgres** database to the project. Railway injects `DATABASE_URL`
   automatically and the app picks it up — no code change.
4. Set these variables on the service:
   - `SITE_URL` = `https://ihavenoideawhatidoanymore.com`
   - `RESEND_API_KEY` = your Resend key
   - `MAIL_FROM` = `hello@ihavenoideawhatidoanymore.com`
5. Settings → Networking → Custom Domain → add the domain, then create the CNAME
   Railway shows you at your registrar. Create it **DNS-only** if your registrar
   proxies (Cloudflare's orange cloud breaks the certificate issue).

Tables are created on startup, so the first deploy needs no migration step.

Without `RESEND_API_KEY` the site still works end to end — enquiries are saved
to the database, they just aren't emailed. Verify the domain in Resend before
launch or messages will silently fail to deliver.

## How it's put together

```
app/
  main.py       routes, validation, spam defence
  db.py         SQLAlchemy models; SQLite locally, Postgres in production
  taxonomy.py   the vocabulary of the site - job titles, what people add on
                top, the plurality score. Edit this first; everything derives
                from it. NB `former_life` holds the CURRENT job title; the name
                is historical and kept to avoid a migration.
  mailer.py     Resend relay, falls back to console logging
  templates/    Jinja2
  static/       one stylesheet (there is no JavaScript)
docs/
  video-scripts.md   three films, shot by shot
seed.py         six invented example profiles for local development
```

### Design decisions worth knowing

**Nobody's email is ever rendered.** `contact_email` is only read by the mailer.
The contact form posts to the server, which sends the message on with the
sender's address as reply-to. Scrapers get nothing.

**No accounts, no passwords.** Each profile gets a random `edit_token`. The edit
link is emailed and shown once on the confirmation page. Losing it means losing
edit access, which the page says plainly.

**Deletes are soft.** "Take me off the site" sets `visible = False`. The row
survives so an accidental click is recoverable from the database.

**The plurality score is derived, never entered.** It's the count of things
someone ticked BEYOND their job title, capped at 10. It means nothing, which is the joke, but it gives
every profile a headline number and makes the cards scannable.

**Spam defence is deliberately light**: a honeypot field plus a per-IP rate
limit held in memory. Good enough for a fun site; if it gets attention, move the
rate limit to the database or Redis, since in-memory state resets on redeploy
and doesn't span multiple instances.

**Directory filtering happens in Python**, not SQL, because the list fields are
JSON columns. Fine for hundreds of profiles. Past a few thousand, move
`former_life` filtering to SQL (already indexed by query) and add a proper
join table for the rest.

## Before you launch

- [ ] Delete the seeded example people (`rm noidea.db`, or delete the rows in
      production — they are invented, and they say so in `seed.py`)
- [ ] Verify the sending domain in Resend
- [ ] Add a privacy line saying what you store: name, profile content, and an
      email address used only to forward messages
- [ ] Decide whether you want to see profiles before they go live; right now
      they publish instantly
