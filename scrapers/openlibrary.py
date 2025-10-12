import os
from typing import Any

import requests
from cachetools import TTLCache, cached
from pydantic import BaseModel

from .exceptions import NotFoundException

if not (admin_email := os.getenv("ADMIN_EMAIL")):
    raise Exception("ADMIN_EMAIL is not set")

HEADERS = {
    "User-Agent": f"fastapi-scraper/0.1.0 ({admin_email})",
}


class OpenLibraryBookSearchResult(BaseModel):
    image_url: str
    title: str | None
    subtitle: str | None
    isbn_10: list[str] | None
    isbn_13: list[str] | None
    authors: list[str]
    publish_date: str | None
    number_of_pages: int | None
    publishers: list[str]
    subjects: list[str]


@cached(cache=TTLCache(maxsize=1024, ttl=600))
def fetch_by_key(key: str) -> dict[str, Any] | None:
    url = f"https://openlibrary.org{key}.json"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        return None


@cached(cache=TTLCache(maxsize=1024, ttl=600))
def fetch_book_data(isbn: str) -> OpenLibraryBookSearchResult:
    url = f"https://openlibrary.org/isbn/{isbn}.json"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        result = response.json()
    else:
        raise NotFoundException("ISBN not found")

    work_data = {}
    if works := result.get("works"):
        if work_key := works[0].get("key"):
            work_data = fetch_by_key(work_key) or {}

    author_names = []
    if authors := (work_data.get("authors") or result.get("authors")):
        for author in authors:
            if author_key := (author.get("author", {}).get("key") or author.get("key")):
                if author_data := fetch_by_key(author_key):
                    author_names.append(author_data.get("personal_name"))

    return OpenLibraryBookSearchResult(
        image_url=f"https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg",
        title=work_data.get("title") or result.get("title"),
        subtitle=work_data.get("subtitle") or result.get("subtitle"),
        isbn_10=result.get("isbn_10"),
        isbn_13=result.get("isbn_13"),
        authors=author_names,
        publish_date=result.get("publish_date"),
        number_of_pages=result.get("number_of_pages"),
        publishers=result.get("publishers", []),
        subjects=work_data.get("subjects", []) or result.get("subjects", []),
    )
