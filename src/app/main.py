from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import iconclass
import sqlite3
import os
import urllib.parse
from .util import fill_obj
from .models import *

app = FastAPI(openapi_url="/openapi")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=RedirectResponse)
async def index() -> RedirectResponse:
    SQL = "select notation from notations ORDER BY RANDOM() LIMIT 1"
    IC_INDEX_PATH = os.environ.get("IC_PATH", "iconclass.sqlite")
    cur = sqlite3.connect(IC_INDEX_PATH).cursor()
    try:
        results = [x[0] for x in cur.execute(SQL)]
    except sqlite3.OperationalError:
        results = ["0"]
    u = urllib.parse.quote(results[0])
    return RedirectResponse(f"/en/{u}")


# if request.META.get("HTTP_ACCEPT").find("application/rdf+xml") > -1:
#     response = HttpResponseRedirect("/" + urllib.quote(notation) + ".rdf")
#     response.status_code = 303
#     return response


@app.get("/{notation}.json", response_model=Notation, response_model_exclude_unset=True)
async def notation_json(notation: str):
    if notation == "ICONCLASS":
        obj = {
            "txt": {},
            "c": [str(x) for x in range(10)],
            "n": "ICONCLASS",
            "kw": {},
            "p": [],
        }
    else:
        obj = iconclass.get(notation)
    return obj


@app.get("/{notation}.rdf", response_class=Response)
async def notation_rdf(request: Request, notation: str):
    if notation in ("scheme", "ICONCLASS"):
        SKOSRDF = """<?xml version="1.0" encoding="UTF-8"?>
<rdf:RDF
    xmlns:skos="http://www.w3.org/2004/02/skos/core#"
    xmlns:dc="http://purl.org/dc/elements/1.1/"
    xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
    <skos:ConceptScheme rdf:about="https://iconclass.org/rdf/2021/09/">
        <dc:title>ICONCLASS</dc:title>
        <dc:description>Iconclass is a subject-specific multilingual classification system. It is a hierarchically ordered collection of definitions of objects, people, events and abstract ideas that serve as the subject of an image. Art historians, researchers and curators use it to describe, classify and examine the subject of images represented in various media such as paintings, drawings, photographs and texts.</dc:description>
        <dc:creator>Henri van de Waal</dc:creator>
        <skos:hasTopConcept rdf:resource="https://iconclass.org/ICONCLASS"/>
   </skos:ConceptScheme>
</rdf:RDF>"""
        return Response(content=SKOSRDF, media_type="application/xml")
    else:
        obj = iconclass.get(notation)
        return templates.TemplateResponse(
            "rdf.html", {"obj_list": [obj], "request": request}
        )


@app.get("/search", response_class=HTMLResponse)
async def search(
    request: Request,
    q: str,
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
        "lang": lang,
        "sort": sort,
        "include_keys": keys,
    }
    return templates.TemplateResponse("search.html", ctx)


@app.get("/api/search")
async def api_search(
    q: str,
    lang: Optional[str] = "en",
    size: Optional[int] = 999,
    page: Optional[int] = 1,
    sort: Optional[str] = "rank",
    keys: Optional[str] = "0",
):
    notations = do_search(q=q, lang=lang, sort=sort, keys=(keys == "1"))
    return {"result": notations[:size], "total": len(notations)}


def do_search(q: str, lang: str, sort: str, keys: bool):
    if lang not in ("en", "de"):
        lang = "en"
    IC_INDEX_PATH = os.environ.get("IC_INDEX_PATH", "iconclass_index.sqlite")
    index_db = sqlite3.connect(IC_INDEX_PATH)
    index_db.enable_load_extension(True)
    index_db.load_extension("/usr/local/lib/fts5stemmer")
    cur = index_db.cursor()

    if keys:
        SQL = f"SELECT notation FROM {lang} WHERE text MATCH ? order by {sort}"
    else:
        SQL = f"SELECT notation FROM {lang} WHERE is_key=0 AND text MATCH ? order by {sort}"
    try:
        results = [x[0] for x in cur.execute(SQL, (q,))]
    except sqlite3.OperationalError:
        results = []
    return results


@app.get("/{lang}/{notation}", response_class=HTMLResponse)
async def browse(request: Request, lang: str, notation: str):
    if lang not in ("en", "de", "fr", "it", "pt", "nl", "pl", "zh", "fi", "ja"):
        lang = "en"
    obj = iconclass.get(notation)
    if not obj:
        raise HTTPException(status_code=404, detail=f"Notation {notation} not found")
    tops = [iconclass.get(t) for t in "0 1 2 3 4 5 6 7 8 9".split()]
    ctx = {
        "request": request,
        "lang": lang,
        "obj": fill_obj(obj),
        "notation": notation,
        "tops": tops,
    }
    return templates.TemplateResponse("browse.html", ctx)
