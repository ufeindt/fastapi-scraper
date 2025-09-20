from fastapi import FastAPI, Request
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from scrapers.imdb import scrape_imdb

app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_middleware(GZipMiddleware)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("base.html", request=request)


@app.get("/imdb/{imdb_id}", response_class=HTMLResponse)
async def imdb_details(request: Request, imdb_id: str):
    result = scrape_imdb(imdb_id)
    return templates.TemplateResponse(
        name="base.html",
        request=request,
        context={"content_template": "imdb-details.html", "result": result},
    )
