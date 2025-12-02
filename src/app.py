# app.py
from fastapi import FastAPI, UploadFile, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

import difflib

from .docdiff.diff_engine import build_chunks, extract_lines

app = FastAPI()

templates = Jinja2Templates(directory="src/templates")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        "input.html",         
        {"request": request}
    )

@app.post("/diff-json")
async def diff_json(file_a: UploadFile, file_b: UploadFile):
    lines_a = await extract_lines(file_a)
    lines_b = await extract_lines(file_b)
    chunks = build_chunks(lines_a, lines_b)
    return JSONResponse(chunks)

@app.get("/chunked", response_class=HTMLResponse)
async def chunked(request: Request):
    return templates.TemplateResponse(
        "chunked.html",
        {"request": request}
    )

@app.post("/diff", response_class=HTMLResponse)
async def diff(request: Request, file_a: UploadFile, file_b: UploadFile):
    text_a = await extract_lines(file_a)
    text_b = await extract_lines(file_b)

    diff_maker = difflib.HtmlDiff(wrapcolumn=80)
    table_html = diff_maker.make_table(
        text_a,
        text_b,
        fromdesc=file_a.filename,
        todesc=file_b.filename,
        context=True,
        numlines=3,
    )

    return templates.TemplateResponse(
        "output.html",
        {
            "request": request,
            "file_a": file_a.filename,
            "file_b": file_b.filename,
            "table_html": table_html,
        },
    )
