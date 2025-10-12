import os
from typing import Annotated, Union

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from scrapers import (
    SearchType,
    search_query,
)
from scrapers.exceptions import InvalidTypeException, NotFoundException
from scrapers.search import SEARCH_HIERARCHY, SearchCategory

app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_middleware(GZipMiddleware)


def validate_api_key(api_key: str) -> str:
    if api_key != os.getenv("API_KEY"):
        raise HTTPException(status_code=401, detail="Invalid API key")
    return api_key


@app.get("/{api_key}/", response_class=HTMLResponse)
async def index(request: Request, api_key: str = Depends(validate_api_key)):
    return templates.TemplateResponse(
        name="base.html",
        request=request,
        context={
            "api_key": api_key,
            "search_categories": SEARCH_HIERARCHY.values(),
        },
    )


@app.get("/{api_key}/{search_category}", response_class=HTMLResponse)
async def search_category(
    request: Request,
    search_category: SearchCategory,
    api_key: str = Depends(validate_api_key),
    hx_request: Annotated[Union[str, None], Header()] = None,
):
    return templates.TemplateResponse(
        name="search.html" if hx_request else "base.html",
        request=request,
        context={
            "api_key": api_key,
            "search_category": search_category,
            "search_categories": SEARCH_HIERARCHY.values(),
            "search_types": SEARCH_HIERARCHY.get(search_category, {})
            .get("search_types")
            .values(),
        },
    )


@app.get("/{api_key}/{search_category}/{search_type}", response_class=HTMLResponse)
async def search(
    request: Request,
    search_category: SearchCategory,
    search_type: SearchType,
    query: str | None = None,
    api_key: str = Depends(validate_api_key),
    hx_request: Annotated[Union[str, None], Header()] = None,
):
    template = "base.html"
    search_type_dict = SEARCH_HIERARCHY.get(search_category, {}).get("search_types", {})

    context = {
        "api_key": api_key,
        "search_type": search_type,
        "search_types": search_type_dict.values(),
        "search_type_title": search_type_dict.get(search_type, {}).get("title"),
        "search_categories": SEARCH_HIERARCHY.values(),
        "search_category": search_category,
    }
    if query:
        if hx_request:
            template = "result.html"
        try:
            context["url"] = request.url
            context["result"] = search_query(
                search_category, search_type, query
            ).model_dump()
        except (InvalidTypeException, NotFoundException, NotImplementedError) as e:
            context["error"] = str(e)
        except Exception:
            context["error"] = "Internal Error"
    elif hx_request:
        template = "search.html"

    return templates.TemplateResponse(
        name=template,
        request=request,
        context=context,
    )
