import os, sqlite3, random
from fastapi import Request, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Optional, List, Dict, Text

import iconclass
from .main import app
from .util import fill_obj, valid_lang, do_search, get_wikidata

templates = Jinja2Templates(directory="templates")


def get_images(notation: str, size: int = 169) -> List:
    IC_PATH = os.environ.get("IC_PATH", "iconclass.sqlite")
    index_db = sqlite3.connect(IC_PATH)
    cur = index_db.cursor()
    cur.execute(
        "SELECT image, webpage, desc FROM images i INNER JOIN images_ic ii ON ii.id = i.id WHERE ii.notation = ?",
        (notation,),
    )
    results = cur.fetchall()
    if len(results) > size:
        return len(results), random.sample(results, size)
    else:
        return len(results), results


@app.get(
    "/fragments/simple/{lang}/{notation}",
    response_class=HTMLResponse,
    include_in_schema=False,
)
async def simple(request: Request, lang: str, notation: str):
    lang = valid_lang(lang)
    obj = iconclass.get(notation)
    ctx = {
        "request": request,
        "obj": fill_obj(obj),
        "notation": notation,
        "lang": lang,
    }
    return templates.TemplateResponse("notation_simple.html", ctx)


@app.get(
    "/fragments/focus/{lang}/{notation}",
    response_class=HTMLResponse,
    include_in_schema=False,
)
async def focus(request: Request, lang: str, notation: str):
    lang = valid_lang(lang)
    obj = iconclass.get(notation)
    SAMPLE_SIZE = 42
    images_count, images_sample = get_images(notation, SAMPLE_SIZE)
    r = await get_wikidata(notation)
    wikidatas = r["results"]["bindings"]

    ctx = {
        "request": request,
        "obj": fill_obj(obj),
        "notation": notation,
        "lang": lang,
        "images": images_sample,
        "images_count": images_count,
        "sample_size": SAMPLE_SIZE,
        "wikidatas": wikidatas,
    }
    return templates.TemplateResponse("notation_focus.html", ctx)


@app.get(
    "/fragments/search/{lang}/", response_class=HTMLResponse, include_in_schema=False
)
async def search(
    request: Request,
    lang: str,
    q: str,
    sort: Optional[str] = "rank",
    keys: Optional[str] = "0",
    r: Optional[str] = "",
):
    if lang not in ("en", "de"):
        lang = "en"  # for now we can only search in en/de until we index all

    RESULT_CAP = 999
    results = do_search(q=q, lang=lang, sort=sort, keys=(keys == "1"), r=r)
    # Properly filter in case of bogus notations
    results_objs = filter(None, [iconclass.get(o) for o in results[:RESULT_CAP]])
    ctx = {
        "request": request,
        "results": results_objs,
        "total": len(results),
        "q": q,
        "r": r,
        "lang": lang,
        "sort": sort,
        "include_keys": keys,
        "RESULT_CAP": RESULT_CAP,
    }

    return templates.TemplateResponse("search_fragment.html", ctx)
