# app.py
from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import HTMLResponse
import difflib

app = FastAPI()

FORM_HTML = """
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>DocDiff MVP</title>
  </head>
  <body>
    <h1>Compare two documents</h1>
    <form action="/diff" method="post" enctype="multipart/form-data">
      <div>
        <label>Document A: <input type="file" name="file_a" /></label>
      </div>
      <div>
        <label>Document B: <input type="file" name="file_b" /></label>
      </div>
      <button type="submit">Compare</button>
    </form>
  </body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def index():
    return FORM_HTML

@app.post("/diff", response_class=HTMLResponse)
async def diff(file_a: UploadFile, file_b: UploadFile):
    text_a = (await file_a.read()).decode("utf-8", errors="replace").splitlines()
    text_b = (await file_b.read()).decode("utf-8", errors="replace").splitlines()

    diff_maker = difflib.HtmlDiff(wrapcolumn=80)
    table_html = diff_maker.make_table(
        text_a, text_b,
        fromdesc=file_a.filename,
        todesc=file_b.filename,
        context=True,
        numlines=3,
    )

    page = f"""
    <!doctype html>
    <html>
      <head>
        <meta charset="utf-8" />
        <title>Diff: {file_a.filename} vs {file_b.filename}</title>
        <style>
          body {{ font-family: system-ui, sans-serif; }}
          table.diff {{ font-size: 13px; border-collapse: collapse; }}
          .diff_header {{ background: #f6f8fa; }}
          .diff_next {{ background: #fff3bf; }}
          .diff_add {{ background: #e6ffed; }}   /* similar to GitHub green */
          .diff_sub {{ background: #ffeef0; }}   /* similar to GitHub red   */
          td, th {{ border: 1px solid #d0d7de; padding: 2px 4px; }}
        </style>
      </head>
      <body>
        <a href="/">← back</a>
        <h1>Diff</h1>
        {table_html}
      </body>
    </html>
    """
    return HTMLResponse(page)
