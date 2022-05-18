import os, sqlite3, random
from fastapi import Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Optional, List, Dict, Text
from pydantic import BaseModel


import iconclass
from markupsafe import Markup
from .main import app
from .util import fill_obj, valid_lang, do_search, get_wikidata

templates = Jinja2Templates(directory="templates")


def get_images(notation: str, size: int = 169) -> List:
    IC_PATH = os.environ.get("IC_PATH", "iconclass.sqlite")
    index_db = sqlite3.connect(IC_PATH)
    cur = index_db.cursor()
    cur.execute(
        "SELECT image, webpage, desc, i.id  FROM images i INNER JOIN images_ic ii ON ii.id = i.id WHERE ii.notation = ?",
        (notation,),
    )
    results = cur.fetchall()
    if len(results) > size:
        return len(results), random.sample(results, size)
    else:
        return len(results), results


def get_object(anid: str):
    IC_PATH = os.environ.get("IC_PATH", "iconclass.sqlite")
    index_db = sqlite3.connect(IC_PATH)
    cur = index_db.cursor()
    cur.execute(
        "SELECT image, webpage, desc FROM images i WHERE i.id = ?",
        (anid,),
    )
    results = cur.fetchall()
    return results


@app.get(
    "/fragments/images/{notation}", response_class=HTMLResponse, include_in_schema=False
)
async def images(request: Request, notation: str):
    SAMPLE_SIZE = 42
    images_count, images_sample = get_images(notation, SAMPLE_SIZE)
    obj = iconclass.get(notation)

    ctx = {
        "request": request,
        "notation": notation,
        "images": images_sample,
        "images_count": images_count,
        "sample_size": SAMPLE_SIZE,
        "obj": fill_obj(obj),
        "lang": "en",
    }
    return templates.TemplateResponse("images_notation.html", ctx)


@app.get(
    "/fragments/object/{anid}",
    response_class=HTMLResponse,
    include_in_schema=False,
)
async def object(request: Request, anid: str):
    # get the object
    results = get_object(anid)
    if len(results) > 0:
        image, webpage, desc = results[0]
    else:
        raise HTTPException(status_code=404, detail=f"Item {anid} not found")
    ctx = {"request": request, "image": image, "url": webpage, "desc": Markup(desc)}
    return templates.TemplateResponse("object_focus.html", ctx)


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
    "/fragments/path/{lang}/{notation}",
    response_class=HTMLResponse,
    include_in_schema=False,
)
async def path(request: Request, lang: str, notation: str):
    lang = valid_lang(lang)
    obj = iconclass.get(notation)
    ctx = {
        "request": request,
        "obj": fill_obj(obj),
        "notation": notation,
        "lang": lang,
    }
    return templates.TemplateResponse("notation_path.html", ctx)


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
    # r = await get_wikidata(notation)
    # wikidatas = r["results"]["bindings"]

    ctx = {
        "request": request,
        "obj": fill_obj(obj),
        "notation": notation,
        "lang": lang,
        "images": images_sample,
        "images_count": images_count,
        "sample_size": SAMPLE_SIZE,
        "wikidatas": [],
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
    RESULT_CAP = 999
    results = do_search(q=q, lang=lang, sort=sort, keys=(keys == "1"), r=r)
    if len(results) < 1 and q and q[0] != '"':
        results = do_search(q=f'"{q}"', lang=lang, sort=sort, keys=(keys == "1"), r=r)
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


class IcerData(BaseModel):
    filename_ics: list
    ics: dict


@app.post(
    "/fragments/icer/{lang}/", response_class=HTMLResponse, include_in_schema=False
)
async def icer_results(request: Request, lang: str, data: IcerData):
    ic_match_list = {}
    for i in data.filename_ics:
        for ic in i["ic"]:
            if ic in ic_match_list and ic_match_list[ic] > i["match"]:
                continue
            else:
                ic_match_list[ic] = i["match"]
    RESULT_CAP = 999
    results = [(match, ic) for ic, match in ic_match_list.items()]
    results_objs = filter(
        None, [iconclass.get(ic) for _, ic in reversed(sorted(results))]
    )
    ctx = {
        "request": request,
        "results": results_objs,
        "total": len(results),
        "q": "this uploaded image",
        "r": "",
        "lang": lang,
        "sort": "rank",
        "include_keys": "1",
        "RESULT_CAP": RESULT_CAP,
    }

    return templates.TemplateResponse("icer_matches.html", ctx)
