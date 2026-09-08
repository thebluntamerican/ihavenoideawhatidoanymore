"""ihavenoideawhatidoanymore.com

A directory of plural people: specific former job, no current job title.
"""
import os
import json
import time
import random
import logging
from collections import defaultdict
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import select, func

from . import taxonomy as tax
from .db import (SessionLocal, Profile, Enquiry, init_db, make_slug,
                 new_token, DATABASE_URL)
from . import mailer

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("noidea")

HERE = os.path.dirname(os.path.abspath(__file__))
SITE_URL = os.environ.get("SITE_URL", "http://localhost:8000")

@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    log.info("Database ready: %s", DATABASE_URL.split("@")[-1])
    yield


app = FastAPI(title="I Have No Idea What I Do Anymore",
              docs_url=None, redoc_url=None, lifespan=lifespan)
app.mount("/static", StaticFiles(directory=os.path.join(HERE, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(HERE, "templates"))


# --- light spam defence: honeypot + per-IP rate limit ------------------------
_hits = defaultdict(list)


def _rate_ok(request: Request, bucket: str, limit: int, window: int = 3600) -> bool:
    ip = (request.headers.get("x-forwarded-for", "").split(",")[0].strip()
          or (request.client.host if request.client else "?"))
    key = f"{bucket}:{ip}"
    now = time.time()
    _hits[key] = [t for t in _hits[key] if now - t < window]
    if len(_hits[key]) >= limit:
        return False
    _hits[key].append(now)
    return True


# Fields that can hold several values. `dict(form)` collapses these to the last
# value, which silently unticks every box when a submission fails validation.
_MULTI = ("now_doing", "stack", "open_to")


def _form_data(form) -> dict:
    """Re-render-safe view of a submitted form."""
    data = {k: v for k, v in form.items() if k not in _MULTI}
    for key in _MULTI:
        data[key] = form.getlist(key)
    return data


def _ctx(request: Request, **kw):
    base = {"request": request, "tax": tax, "site_url": SITE_URL}
    base.update(kw)
    return base


# --- pages -------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    with SessionLocal() as s:
        total = s.scalar(select(func.count()).select_from(Profile)
                         .where(Profile.visible.is_(True))) or 0
        recent = s.scalars(
            select(Profile).where(Profile.visible.is_(True))
            .order_by(Profile.created_at.desc()).limit(6)
        ).all()
    return templates.TemplateResponse(request, "index.html", _ctx(
        request, total=total, recent=recent))


@app.get("/directory", response_class=HTMLResponse)
def directory(request: Request, was: str = "", does: str = "",
              open_to: str = "", q: str = ""):
    with SessionLocal() as s:
        stmt = select(Profile).where(Profile.visible.is_(True))
        if was:
            stmt = stmt.where(Profile.former_life == was)
        rows = s.scalars(stmt.order_by(Profile.created_at.desc())).all()

    # The list-valued filters live in JSON columns, so filter them in Python.
    # The directory is small by design; this stays fast for a long time.
    if does:
        rows = [p for p in rows if does in p.now_doing]
    if open_to:
        rows = [p for p in rows if open_to in p.open_to]
    if q:
        needle = q.lower()
        rows = [p for p in rows if needle in " ".join([
            p.name, p.headline, p.former_life, p.superpower, p.location,
            " ".join(p.now_doing), " ".join(p.stack),
        ]).lower()]

    return templates.TemplateResponse(request, "directory.html", _ctx(
        request, profiles=rows, was=was, does=does, open_to=open_to, q=q,
        count=len(rows),
    ))


@app.get("/p/{slug}", response_class=HTMLResponse)
def profile_page(request: Request, slug: str, sent: int = 0):
    with SessionLocal() as s:
        p = s.scalar(select(Profile).where(Profile.slug == slug,
                                           Profile.visible.is_(True)))
    if not p:
        raise HTTPException(404, "No such profile")
    label, blurb = tax.plurality_label(p.plurality)
    return templates.TemplateResponse(request, "profile.html", _ctx(
        request, p=p, plurality_label=label, plurality_blurb=blurb, sent=sent,
    ))


@app.get("/join", response_class=HTMLResponse)
def join_form(request: Request):
    return templates.TemplateResponse(request, "join.html", _ctx(request, errors=[], data={}))


@app.post("/join", response_class=HTMLResponse)
async def join_submit(request: Request):
    form = await request.form()

    # Honeypot: a field hidden from humans. Bots fill it in.
    if form.get("website_url"):
        return RedirectResponse("/directory", status_code=303)

    if not _rate_ok(request, "join", limit=5):
        return templates.TemplateResponse(request, "join.html", _ctx(
            request, errors=["Slow down a moment - too many submissions from here."],
            data=_form_data(form)), status_code=429)

    name = (form.get("name") or "").strip()
    email = (form.get("contact_email") or "").strip()
    now_doing = [v for v in form.getlist("now_doing") if v in tax.NOW_DOING]
    open_to = [v for v in form.getlist("open_to") if v in tax.OPEN_TO]
    stack = [v for v in form.getlist("stack") if v in tax.STACK]

    errors = []
    if len(name) < 2:
        errors.append("We need a name to put on the profile.")
    if "@" not in email or "." not in email.split("@")[-1]:
        errors.append("That email doesn't look right - it's how people reach you.")
    if not now_doing:
        errors.append("Pick at least one thing you actually do now.")
    if not open_to:
        errors.append("Tell us what you're open to, even if it's nothing.")
    if errors:
        return templates.TemplateResponse(request, "join.html", _ctx(
            request, errors=errors, data=_form_data(form)), status_code=400)

    with SessionLocal() as s:
        p = Profile(
            slug=make_slug(name, s),
            name=name[:120],
            headline=(form.get("headline") or "").strip()[:200],
            location=(form.get("location") or "").strip()[:120],
            former_life=(form.get("former_life") or "").strip()[:120],
            former_life_detail=(form.get("former_life_detail") or "").strip()[:200],
            now_doing_json=json.dumps(now_doing),
            stack_json=json.dumps(stack),
            open_to_json=json.dumps(open_to),
            superpower=(form.get("superpower") or "").strip()[:600],
            still_cant=(form.get("still_cant") or "").strip()[:600],
            link_site=(form.get("link_site") or "").strip()[:300],
            link_linkedin=(form.get("link_linkedin") or "").strip()[:300],
            link_x=(form.get("link_x") or "").strip()[:300],
            contact_email=email[:200],
            edit_token=new_token(),
            plurality=tax.plurality_score(now_doing),
        )
        s.add(p)
        s.commit()
        slug, token = p.slug, p.edit_token
        mailer.send(email, "You're in the directory",
                    mailer.welcome_email(p))

    return RedirectResponse(f"/joined/{slug}?token={token}", status_code=303)


@app.get("/joined/{slug}", response_class=HTMLResponse)
def joined(request: Request, slug: str, token: str = ""):
    with SessionLocal() as s:
        p = s.scalar(select(Profile).where(Profile.slug == slug))
    if not p or token != p.edit_token:
        raise HTTPException(404, "No such profile")
    label, blurb = tax.plurality_label(p.plurality)
    return templates.TemplateResponse(request, "joined.html", _ctx(
        request, p=p, token=token, plurality_label=label, plurality_blurb=blurb))


@app.post("/contact/{slug}", response_class=HTMLResponse)
async def contact(request: Request, slug: str):
    form = await request.form()
    if form.get("website_url"):
        return RedirectResponse(f"/p/{slug}", status_code=303)
    if not _rate_ok(request, "contact", limit=10):
        raise HTTPException(429, "Too many messages from this address for now.")

    with SessionLocal() as s:
        p = s.scalar(select(Profile).where(Profile.slug == slug,
                                           Profile.visible.is_(True)))
        if not p:
            raise HTTPException(404, "No such profile")
        if not p.hireable:
            raise HTTPException(403, "This person isn't taking work enquiries.")

        e = Enquiry(
            profile_slug=slug,
            from_name=(form.get("from_name") or "").strip()[:120],
            from_email=(form.get("from_email") or "").strip()[:200],
            from_org=(form.get("from_org") or "").strip()[:160],
            message=(form.get("message") or "").strip()[:4000],
        )
        if len(e.from_name) < 2 or "@" not in e.from_email or len(e.message) < 10:
            raise HTTPException(400, "Please add your name, a real email, and a message.")

        e.delivered = mailer.send(
            p.contact_email,
            f"{e.from_name} wants to hire you",
            mailer.enquiry_email(p, e),
            reply_to=e.from_email,
        )
        s.add(e)
        s.commit()

    return RedirectResponse(f"/p/{slug}?sent=1", status_code=303)


@app.get("/edit/{slug}", response_class=HTMLResponse)
def edit_form(request: Request, slug: str, token: str = ""):
    with SessionLocal() as s:
        p = s.scalar(select(Profile).where(Profile.slug == slug))
    if not p or not token or token != p.edit_token:
        raise HTTPException(404, "That edit link isn't valid.")
    data = {
        "name": p.name, "headline": p.headline, "location": p.location,
        "former_life": p.former_life, "former_life_detail": p.former_life_detail,
        "now_doing": p.now_doing, "stack": p.stack, "open_to": p.open_to,
        "superpower": p.superpower, "still_cant": p.still_cant,
        "link_site": p.link_site, "link_linkedin": p.link_linkedin,
        "link_x": p.link_x, "contact_email": p.contact_email,
    }
    return templates.TemplateResponse(request, "join.html", _ctx(
        request, errors=[], data=data, editing=p, token=token))


@app.post("/edit/{slug}", response_class=HTMLResponse)
async def edit_submit(request: Request, slug: str):
    form = await request.form()
    token = form.get("token") or ""
    with SessionLocal() as s:
        p = s.scalar(select(Profile).where(Profile.slug == slug))
        if not p or not token or token != p.edit_token:
            raise HTTPException(404, "That edit link isn't valid.")

        if form.get("delete_me") == "yes":
            p.visible = False
            s.commit()
            return RedirectResponse("/?gone=1", status_code=303)

        now_doing = [v for v in form.getlist("now_doing") if v in tax.NOW_DOING]
        if not now_doing:
            raise HTTPException(400, "Pick at least one thing you do now.")
        p.name = (form.get("name") or p.name).strip()[:120]
        p.headline = (form.get("headline") or "").strip()[:200]
        p.location = (form.get("location") or "").strip()[:120]
        p.former_life = (form.get("former_life") or "").strip()[:120]
        p.former_life_detail = (form.get("former_life_detail") or "").strip()[:200]
        p.now_doing_json = json.dumps(now_doing)
        p.stack_json = json.dumps([v for v in form.getlist("stack") if v in tax.STACK])
        p.open_to_json = json.dumps([v for v in form.getlist("open_to") if v in tax.OPEN_TO])
        p.superpower = (form.get("superpower") or "").strip()[:600]
        p.still_cant = (form.get("still_cant") or "").strip()[:600]
        p.link_site = (form.get("link_site") or "").strip()[:300]
        p.link_linkedin = (form.get("link_linkedin") or "").strip()[:300]
        p.link_x = (form.get("link_x") or "").strip()[:300]
        email = (form.get("contact_email") or "").strip()
        if "@" in email:
            p.contact_email = email[:200]
        p.plurality = tax.plurality_score(now_doing)
        s.commit()
    return RedirectResponse(f"/p/{slug}", status_code=303)


# --- the toy -----------------------------------------------------------------
@app.get("/api/title")
def random_title():
    """Mint an absurd job title. Powers the slot machine on the homepage."""
    was = random.choice(tax.FORMER_LIVES)
    return JSONResponse({
        "was": was,
        "title": (random.choice(tax.TITLE_PREFIX) + was
                  + random.choice(tax.TITLE_SUFFIX)),
        "doing": random.sample(tax.NOW_DOING, 3),
    })


@app.get("/healthz")
def healthz():
    return {"ok": True}


# Starlette 1.6 stopped deriving HEAD from GET, so every page answered 405 to a
# HEAD request - which is what most uptime monitors and link crawlers send
# first. Mirror GET onto HEAD for every route; the server still omits the body.
for _route in app.routes:
    _methods = getattr(_route, "methods", None)
    if _methods and "GET" in _methods:
        _methods.add("HEAD")
