from fastapi import Depends, FastAPI, Request, HTTPException, Query, status
from fastapi.responses import (
    HTMLResponse,
    RedirectResponse,
    Response,
    JSONResponse,
    PlainTextResponse,
)
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jinja2 import Markup
from .shortcodes import apply_shortcodes

from fastapi.middleware.cors import CORSMiddleware
import iconclass
import sqlite3
import os
import urllib.parse
from datetime import timedelta
import markdown
from .util import fill_obj, valid_lang, do_search, LANGUAGES, get_random_notations
from .models import *

from .config import ORIGINS, HELP_PATH


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


@app.get("/json")
async def json_list(notation: List[str] = Query(None)):
    objs = iconclass.get_list(notation)
    return {"result": objs, "requested": notation}


@app.get("/", response_class=HTMLResponse)
async def homepage(request: Request):
    return templates.TemplateResponse("homepage.html", {"request": request})


def aimg(*args, **kwargs):
    return f'<img src="https://test.iconclass.org/iiif/2/{args[0]}.jpg/full/full/0/default.jpg"/>'


def pdf(*args, **kwargs):
    return f'<a target="read" href="/read/{args[0]}.pdf">{args[1]}</a>'


@app.get("/read/{filename}", response_class=HTMLResponse)
async def read(request: Request, filename: str):
    return templates.TemplateResponse(
        "read.html", {"request": request, "filename": filename}
    )


@app.get("/help/{page}", response_class=HTMLResponse)
async def help(request: Request, page: str):
    infilepath = os.path.join(HELP_PATH, f"{page}.md")
    if not os.path.exists(infilepath):
        raise HTTPException(status_code=404, detail=f"Page [{page}] not found")
    md = markdown.Markdown(
        output_format="html5", extensions=["nl2br", "meta", "attr_list"]
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


# if request.META.get("HTTP_ACCEPT").find("application/rdf+xml") > -1:
#     response = HttpResponseRedirect("/" + urllib.quote(notation) + ".rdf")
#     response.status_code = 303
#     return response

# https://json-ld.org/
# https://github.com/digitalbazaar/pyld
@app.get("/{notation}.jsonld", response_model=JSONLD, response_model_exclude_unset=True)
async def notation_jsonld(notation: str):
    if notation == "ICONCLASS":
        # skos:hasTopConcept
        obj = {
            "@context": {
                "skos": "http://www.w3.org/2004/02/skos/core#",
                "uri": "@id",
                "type": "@type",
                "lang": "@language",
                "value": "@value",
                "graph": "@graph",
                "prefLabel": "skos:prefLabel",
            },
            "uri": "https://iconclass.org/rdf/2021/09/",
            "type": "http://www.w3.org/2004/02/skos/core#ConceptScheme",
        }
    else:
        obj = iconclass.get(notation)
    tmp = {
        "@context": {
            "skos": "http://www.w3.org/2004/02/skos/core#",
            "dc": "http://purl.org/dc/elements/1.1/",
            "uri": "@id",
            "type": "@type",
            "lang": "@language",
            "value": "@value",
            "graph": "@graph",
            "prefLabel": "skos:prefLabel",
            "altLabel": "skos:altLabel",
            "broader": "skos:broader",
            "narrower": "skos:narrower",
            "related": "skos:related",
            "inScheme": "skos:inScheme",
        },
        "graph": [
            {
                "uri": f"https://iconclass.org/{urllib.parse.quote(notation)}",
                "type": "skos:Concept",
                "inScheme": "https://iconclass.org/rdf/2021/09/",
                "skos:notation": notation,
                "prefLabel": [
                    {"lang": lang, "value": txt}
                    for lang, txt in obj.get("txt", {}).items()
                ],
                "dc:subject": [
                    {"lang": lang, "value": kw}
                    for lang, kws in obj.get("kw", {}).items()
                    for kw in kws
                ],
            },
            {"uri": "https://iconclass.org/rdf/2021/09/", "type": "skos:ConceptScheme"},
        ],
    }
    tmp_graph = tmp["graph"][0]
    if "p" in obj and len(obj["p"]) > 1:
        tmp_graph["broader"] = {
            "uri": f"https://iconclass.org/{urllib.parse.quote(obj['p'][-2])}"
        }
    if "c" in obj:
        tmp_graph["narrower"] = [
            {"uri": f"https://iconclass.org/{urllib.parse.quote(c)}"}
            for c in obj.get("c", [])
        ]
    if "r" in obj:
        tmp_graph["related"] = [
            {"uri": f"https://iconclass.org/{urllib.parse.quote(r)}"}
            for r in obj.get("r", [])
        ]
    return JSONResponse(tmp)


@app.get("/{notation}.jskos", response_model=JSKOS, response_model_exclude_unset=True)
async def notation_jskos(notation: str):
    if notation == "ICONCLASS":
        tmp = {
            "@context": "https://gbv.github.io/jskos/context.json",
            "definition": {
                "en": ["Subject classification for cultural heritage content"]
            },
            "identifier": [
                "http://bartoc.org/en/node/459",
                "http://www.wikidata.org/entity/Q1502787",
            ],
            "namespace": "https://iconclass.org/",
            "notation": ["IC"],
            "prefLabel": {
                "en": "ICONCLASS",
            },
            "type": ["http://www.w3.org/2004/02/skos/core#ConceptScheme"],
            "uri": "https://iconclass.org/",
            "topConcepts": [{"uri": f"https://iconclass.org/{x}"} for x in range(10)],
        }
        return JSONResponse(tmp)
    else:
        obj = iconclass.get(notation)
    tmp = {
        "@context": "https://gbv.github.io/jskos/context.json",
        "uri": f"https://iconclass.org/{urllib.parse.quote(notation)}",
        "type": ["http://www.w3.org/2004/02/skos/core#Concept"],
        "prefLabel": obj.get("txt", {}),
        "altLabel": obj.get("kw", {}),
        "notation": [notation],
    }
    if "p" in obj:
        tmp["ancestors"] = [
            {"uri": f"https://iconclass.org/{urllib.parse.quote(p)}"}
            for p in obj.get("p", [None])[:-1]
        ]
    if "c" in obj:
        tmp["narrower"] = [
            {"uri": f"https://iconclass.org/{urllib.parse.quote(c)}"}
            for c in obj.get("c", [])
        ]
    if "r" in obj:
        tmp["related"] = [
            {"uri": f"https://iconclass.org/{urllib.parse.quote(r)}"}
            for r in obj.get("r", [])
        ]
    return JSONResponse(tmp)


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


@app.get(
    "/{notation}.fat", response_model=FilledNotation, response_model_exclude_unset=True
)
async def notation_fat(notation: str):
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

    return fill_obj(obj)


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


@app.get("/browse/{lang}", response_class=HTMLResponse)
async def browse(request: Request, lang: str):
    lang = valid_lang(lang)
    results = get_random_notations()
    u = urllib.parse.quote(results[0])
    return RedirectResponse(f"/{lang}/{u}")


@app.get("/{lang}/{notation}", response_class=HTMLResponse)
async def lang_notation(request: Request, lang: str, notation: str):
    lang = valid_lang(lang)
    ctx = {
        "request": request,
        "lang": lang,
        "language": LANGUAGES.get(lang, "English"),
        "notation": notation,
    }
    return templates.TemplateResponse("browse.html", ctx)


@app.get("/showcase", response_class=HTMLResponse)
async def showcase(request: Request):
    return templates.TemplateResponse("showcase.html", {"request": request})
