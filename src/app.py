# app.py
from fastapi import FastAPI, UploadFile, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from docx import Document
from io import BytesIO
import difflib

app = FastAPI()

# Adjust this if your templates live somewhere else
templates = Jinja2Templates(directory="src/templates")

async def extract_lines(upload:UploadFile) -> list[str]:
    raw = await upload.read()
    filename = (upload.filename)

    if filename.endswith(".docx"):
        doc = Document(BytesIO(raw))
        return [p.text for p in doc.paragraphs]
    else:
        return raw.decode("utf-8", errors="replace").splitlines()

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        "input.html",          # or "input.html" if you kept that name
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
