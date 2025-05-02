from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from foe_foundry_data.powers import clean_power_index, index_powers

from .routes import powers


@asynccontextmanager
async def lifespan(app):
    # re-index powers
    clean_power_index()
    index_powers()
    yield
    # cleanup on shutdown
    clean_power_index()


app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",
    "http://localhost:3001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1).*$",  # allow localhost* and 127.0.0.1*
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(powers.router)

site_dir = Path(__file__).parent.parent / "site"

# Mounts the static site folder create by mkdocs
app.mount("/", StaticFiles(directory=site_dir, html=True), name="site")
