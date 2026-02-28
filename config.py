import os

from dotenv import load_dotenv
from flask_caching import Cache
from sqlalchemy import create_engine

load_dotenv()

# ── Banco de dados ───────────────────────────────────────────────────────────

DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=2,
    max_overflow=2,
    connect_args={"options": "-c timezone=America/Sao_Paulo"},
)

# ── Autenticação (Basic Auth via dash-auth) ──────────────────────────────────

DASHBOARD_USER = os.environ.get("DASHBOARD_USER", "admin")
DASHBOARD_PASSWORD = os.environ["DASHBOARD_PASSWORD"]

AUTH_USERS = {DASHBOARD_USER: DASHBOARD_PASSWORD}

# ── Cache ────────────────────────────────────────────────────────────────────

CACHE_TTL = int(os.environ.get("CACHE_TTL", "300"))

cache = Cache(config={"CACHE_TYPE": "SimpleCache", "CACHE_DEFAULT_TIMEOUT": CACHE_TTL})
