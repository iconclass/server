from fastapi import Depends, FastAPI, Request, HTTPException, Query, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import clip
import torch
import faiss
import pandas as pd
from PIL import Image
from io import BytesIO
import configparser, os
import databases
import iconclass

config = configparser.ConfigParser()
config.read("mvp.cfg")
cfg = config["main"]

INDEX = faiss.read_index(cfg.get("index_path"))
METADATA = open(cfg.get("filenames")).read().split("\n")
img_db = databases.Database(cfg.get("imgdb_path"))

app = FastAPI(openapi_url="/openapi")
templates = Jinja2Templates(directory="templates")


device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device, jit=False)


@app.get("/icer", response_class=HTMLResponse, include_in_schema=False)
async def homepage(request: Request):
    return templates.TemplateResponse("matches.html", {"request": request})


@app.post("/icerupload")
async def post_upload(request: Request, file: UploadFile = File(...)):
    contents = await file.read()
    image = Image.open(BytesIO(contents)).resize((256, 256))

    image_tensor = preprocess(image)
    image_features = model.encode_image(torch.unsqueeze(image_tensor.to(device), dim=0))
    image_features /= image_features.norm(dim=-1, keepdim=True)
    image_embeddings = image_features.cpu().detach().numpy().astype("float32")

    D, I = INDEX.search(image_embeddings, 16)
    matches = {}
    for d, i in zip(D[0], I[0]):
        matches[i] = float(d)

    filename_ics = await get_ics(matches)
    ics = set()
    for ic_per_filename in filename_ics:
        for ic in ic_per_filename["ic"]:
            ics.add(ic)
    ics = sorted(list(ics))

    return templates.TemplateResponse(
        "matches.html",
        {
            "request": request,
            "ics": filter(None, iconclass.get_list(ics)),
            "filename_ics": reversed(sorted(filename_ics, key=lambda x: x["match"])),
        },
    )


async def get_ics(matches: dict):
    # matches contains a list of tuples with (idx, match_score)
    query = (
        "SELECT * FROM image_ic WHERE idx IN ("
        + ", ".join([str(i) for i in matches.keys()])
        + ")"
    )
    results = await img_db.fetch_all(query)
    filename_ics = [
        {"match": matches[idx], "filename": filename, "ic": ics.split("\n")}
        for filename, idx, ics in results
    ]
    return filename_ics
