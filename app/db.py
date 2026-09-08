"""Storage. SQLite locally, Postgres on Railway - same code either way."""
import os
import json
import secrets
from datetime import datetime, timezone

from sqlalchemy import (
    create_engine, String, Text, Integer, Boolean, DateTime, select, func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker


def _database_url() -> str:
    url = os.environ.get("DATABASE_URL", "")
    if not url:
        # Local dev: a file next to the repo, not in a temp dir that vanishes.
        here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return f"sqlite:///{os.path.join(here, 'noidea.db')}"
    # Railway/Heroku hand out the legacy postgres:// scheme.
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+psycopg://", 1)
    elif url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


DATABASE_URL = _database_url()
_connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=_connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def _now():
    return datetime.now(timezone.utc)


class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(80), unique=True, index=True)

    name: Mapped[str] = mapped_column(String(120))
    headline: Mapped[str] = mapped_column(String(200), default="")
    location: Mapped[str] = mapped_column(String(120), default="")

    former_life: Mapped[str] = mapped_column(String(120), default="")
    former_life_detail: Mapped[str] = mapped_column(String(200), default="")

    # JSON-encoded lists. Kept as text so SQLite and Postgres behave alike.
    now_doing_json: Mapped[str] = mapped_column(Text, default="[]")
    stack_json: Mapped[str] = mapped_column(Text, default="[]")
    open_to_json: Mapped[str] = mapped_column(Text, default="[]")

    superpower: Mapped[str] = mapped_column(Text, default="")
    still_cant: Mapped[str] = mapped_column(Text, default="")

    link_site: Mapped[str] = mapped_column(String(300), default="")
    link_linkedin: Mapped[str] = mapped_column(String(300), default="")
    link_x: Mapped[str] = mapped_column(String(300), default="")

    # Never rendered to a page. Contact is relayed through a form.
    contact_email: Mapped[str] = mapped_column(String(200), default="")
    # Lets the owner edit or remove their own profile without accounts.
    edit_token: Mapped[str] = mapped_column(String(64), default="")

    plurality: Mapped[int] = mapped_column(Integer, default=1)
    visible: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    # --- convenience accessors ---
    @property
    def now_doing(self):
        return json.loads(self.now_doing_json or "[]")

    @property
    def stack(self):
        return json.loads(self.stack_json or "[]")

    @property
    def open_to(self):
        return json.loads(self.open_to_json or "[]")

    @property
    def hireable(self):
        from .taxonomy import HIREABLE
        return bool(set(self.open_to) & HIREABLE)


class Enquiry(Base):
    """Someone wants to hire someone. Stored so nothing is lost if email fails."""
    __tablename__ = "enquiries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    profile_slug: Mapped[str] = mapped_column(String(80), index=True)
    from_name: Mapped[str] = mapped_column(String(120))
    from_email: Mapped[str] = mapped_column(String(200))
    from_org: Mapped[str] = mapped_column(String(160), default="")
    message: Mapped[str] = mapped_column(Text)
    delivered: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)


def init_db():
    Base.metadata.create_all(engine)


def make_slug(name: str, session) -> str:
    """URL-safe, unique, human-readable."""
    base = "".join(c.lower() if c.isalnum() else "-" for c in name).strip("-")
    while "--" in base:
        base = base.replace("--", "-")
    base = base[:50] or "someone"
    candidate = base
    n = 2
    while session.scalar(select(func.count()).select_from(Profile)
                         .where(Profile.slug == candidate)):
        candidate = f"{base}-{n}"
        n += 1
    return candidate


def new_token() -> str:
    return secrets.token_urlsafe(24)
