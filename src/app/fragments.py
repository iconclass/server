from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import iconclass
from .main import app
from .util import fill_obj, valid_lang

templates = Jinja2Templates(directory="templates")


@app.get("/fragments/focus/{lang}/{notation}", response_class=HTMLResponse)
async def focus(request: Request, lang: str, notation: str):
    lang = valid_lang(lang)
    obj = iconclass.get(notation)
    ctx = {"request": request, "obj": fill_obj(obj), "notation": notation, "lang": lang}
    return templates.TemplateResponse("notation_focus.html", ctx)
