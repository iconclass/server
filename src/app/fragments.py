import os, sqlite3, random
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Optional, List, Dict, Text

import iconclass
from .main import app
from .util import fill_obj, valid_lang

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


@app.get("/fragments/focus/{lang}/{notation}", response_class=HTMLResponse)
async def focus(request: Request, lang: str, notation: str):
    lang = valid_lang(lang)
    obj = iconclass.get(notation)
    images_count, images_sample = get_images(notation, 9)
    ctx = {
        "request": request,
        "obj": fill_obj(obj),
        "notation": notation,
        "lang": lang,
        "images": images_sample,
        "images_count": images_count,
    }
    return templates.TemplateResponse("notation_focus.html", ctx)
