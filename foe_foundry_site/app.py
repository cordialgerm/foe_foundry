from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .routes import powers, stats


@asynccontextmanager
async def lifespan(app):
    # re-index powers
    powers.whoosh.clean_index()
    powers.whoosh.index_powers()
    yield
    # cleanup on shutdown
    powers.whoosh.clean_index()


app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",
    "http://localhost:3001",
    "https://cordialgerm87.pythonanywhere.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_origin_regex=r"^https?://localhost.*$",
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(stats.router)
app.include_router(powers.router)

build_dir = Path(__file__).parent.parent / "foe_foundry_ui" / "build"

# Sets the templates directory to the `build` folder from `npm run build`
# this is where you'll find the index.html file.
templates = Jinja2Templates(directory=build_dir)

# Mounts the `static` folder within the `build` folder to the `/static` route.
app.mount("/static", StaticFiles(directory=f"{build_dir}/static"), "static")
app.mount("/img", StaticFiles(directory=f"{build_dir}/img"), "img")


# Defines a route handler for `/*` essentially.
# NOTE: this needs to be the last route defined b/c it's a catch all route
@app.get("/{rest_of_path:path}")
async def react_app(req: Request, rest_of_path: str):
    return templates.TemplateResponse("index.html", {"request": req})
