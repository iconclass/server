from fastapi import Depends, FastAPI, Request, HTTPException, Query
from fastapi.responses import (
    HTMLResponse,
    RedirectResponse,
)
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jinja2 import Markup
from .shortcodes import apply_shortcodes

from fastapi.middleware.cors import CORSMiddleware
import iconclass
import os
import urllib.parse
import markdown
from .util import (
    fill_obj,
    valid_lang,
    do_search,
    LANGUAGES,
    get_random_notations,
    get_wikidata,
)
from .models import *

from .config import ORIGINS, HELP_PATH, SITE_URL


app = FastAPI(openapi_url="/openapi")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from .fragments import *
from .am import *
from .metabotnik import *
from .lod import *
from .sparql import *


@app.get("/json")
async def json_list(notation: List[str] = Query(None)):
    objs = iconclass.get_list(notation)
    return {"result": objs, "requested": notation}


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def homepage(request: Request):
    return templates.TemplateResponse("homepage.html", {"request": request})


@app.get("/wikidatasample", response_class=HTMLResponse, include_in_schema=False)
async def wikidatasample(notation: str, request: Request):
    r = await get_wikidata(notation)
    return templates.TemplateResponse(
        "wikidata.html",
        {"request": request, "notation": notation, "results": r["results"]["bindings"]},
    )


def aimg(*args, **kwargs):
    return f'<img src="https://iconclass.org/iiif/2/{args[0]}.jpg/full/full/0/default.jpg"/>'


def pdf(*args, **kwargs):
    if len(args) > 1:
        return f'<a target="read" href="{SITE_URL}/read/{args[0]}.pdf">{args[1]}</a>'
    else:
        return f'<a target="read" href="{SITE_URL}/read/{args[0]}.pdf">full text</a>'


@app.get("/read/{filename}", response_class=HTMLResponse, include_in_schema=False)
async def read(request: Request, filename: str):
    return templates.TemplateResponse(
        "read.html", {"request": request, "filename": filename}
    )


@app.get("/help/{page}", response_class=HTMLResponse, include_in_schema=False)
async def help(request: Request, page: str):
    infilepath = os.path.join(HELP_PATH, f"{page}.md")
    if not os.path.exists(infilepath):
        raise HTTPException(status_code=404, detail=f"Page [{page}] not found")
    md = markdown.Markdown(
        output_format="html5", extensions=["nl2br", "meta", "attr_list", "tables"]
    )
    html = md.convert(open(infilepath).read())
    out2, _ = apply_shortcodes(html, {"aimg": aimg, "pdf": pdf})

    return templates.TemplateResponse(
        "help.html", {"request": request, "content": Markup(out2)}
    )


@app.get("/random", response_class=RedirectResponse)
async def random() -> RedirectResponse:
    results = get_random_notations()
    u = urllib.parse.quote(results[0])
    return RedirectResponse(f"/en/{u}")


@app.get("/search", response_class=HTMLResponse, include_in_schema=False)
async def search(
    request: Request,
    q: str,
    r: Optional[str] = "",
    lang: Optional[str] = "en",
    sort: Optional[str] = "rank",
    keys: Optional[str] = "0",
):
    results = do_search(q=q, lang=lang, sort=sort, keys=(keys == "1"))
    # Properly filter in case of bogus notations
    results_objs = filter(None, [iconclass.get(o) for o in results[:999]])
    ctx = {
        "request": request,
        "results": results_objs,
        "total": len(results),
        "q": q,
        "r": r,
        "lang": lang,
        "sort": sort,
        "include_keys": keys,
    }
    return templates.TemplateResponse("search.html", ctx)


@app.get("/api/search")
async def api_search(
    q: str,
    r: Optional[str] = "",
    lang: Optional[str] = "en",
    size: Optional[int] = 999,
    page: Optional[int] = 1,
    sort: Optional[str] = "rank",
    keys: Optional[str] = "0",
):
    notations = do_search(q=q, r=r, lang=lang, sort=sort, keys=(keys == "1"))
    return {"result": notations[:size], "total": len(notations)}


@app.get("/browse/{lang}", response_class=HTMLResponse, include_in_schema=False)
async def browse(request: Request, lang: str):
    lang = valid_lang(lang)
    results = get_random_notations()
    u = urllib.parse.quote(results[0])
    return RedirectResponse(f"/{lang}/{u}")


@app.get("/{lang}/{notation}", response_class=HTMLResponse, include_in_schema=False)
async def lang_notation(
    request: Request,
    lang: str,
    notation: str,
    q: Optional[str] = "",
    k: Optional[str] = "",
):
    lang = valid_lang(lang)
    if notation != "_":
        obj = iconclass.get(notation)
        fill_obj(obj)
    else:
        obj = {}
    ctx = {
        "request": request,
        "lang": lang,
        "language": LANGUAGES.get(lang, "English"),
        "notation": notation,
        "obj": obj,
        "q": q,
        "k": k,
    }
    return templates.TemplateResponse("browse.html", ctx)


@app.get("/showcase", response_class=HTMLResponse, include_in_schema=False)
async def showcase(request: Request):
    return templates.TemplateResponse("showcase.html", {"request": request})


@app.get("/{notation}", response_class=HTMLResponse)
async def notation(request: Request, notation: str):
    if notation[0] in "0123456789":
        return RedirectResponse(f"/en/{notation}")
