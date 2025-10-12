import re
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel

from scrapers.exceptions import NotFoundException


class ImdbSearchResult(BaseModel):
    id: str
    title: str


class ImdbScraperResult(BaseModel):
    imdb_id: str
    imdb_url: str
    age_rating: str
    directors: list[str]
    duration: str
    image_url: str
    release_year: str
    stars: list[str]
    synopsis: str
    tags: list[str]
    title: str
    writers: list[str]


def search_imdb_title(title: str, lang: str = "en-US") -> list[ImdbSearchResult]:
    html_doc = requests.get(
        f"https://www.imdb.com/find/?q={quote(title)}",
        headers={
            "Accept": "text/html",
            "Accept-Language": f"{lang},en;q=0.5",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:141.0) Gecko/20100101 Firefox/141.0",
        },
    )
    soup = BeautifulSoup(html_doc.text, "html.parser")
    title_section = soup.find_all(
        "section", attrs={"data-testid": "find-results-section-title"}
    )[0]
    try:
        title_list_items = title_section.div.next_sibling.ul.find_all(
            "li", recursive=False
        )
        results = []
        for item in title_list_items:
            title = item.find("a").text
            if id_match := re.search(
                r"\/title\/(tt[0-9]+)\/", item.find("a").get("href")
            ):
                results.append(
                    ImdbSearchResult(
                        id=id_match.group(1),
                        title=title,
                    )
                )

        return results
    except AttributeError:
        raise NotFoundException("Item not found") from None


def scrape_imdb_id(imdb_id: str, lang: str = "en-US") -> ImdbScraperResult:
    imdb_url = f"https://www.imdb.com/title/{imdb_id}/"
    html_doc = requests.get(
        imdb_url,
        headers={
            "Accept": "text/html",
            "Accept-Language": f"{lang},en;q=0.5",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:141.0) Gecko/20100101 Firefox/141.0",
        },
    )
    if html_doc.status_code != 200:
        raise NotFoundException("Item not found")

    try:
        soup = BeautifulSoup(html_doc.text, "html.parser")
        title: str = soup.h1.span.text
        image_url: str = soup.main.img.get("src")
        duration: str = (
            soup.main.div.section.section.find_all("div", recursive=False)[2]
            .section.section.find_all("div", recursive=False)[1]
            .find_all("li")[2]
            .text
        )
        release_year: str = (
            soup.main.div.section.section.find_all("div", recursive=False)[2]
            .section.section.find_all("div", recursive=False)[1]
            .find_all("li")[0]
            .a.text
        )
        directors: list[str] = [
            a.text
            for a in soup.find(
                lambda tag: tag.name == "li"
                and tag.find(["a", "span"], string=re.compile("Directors?"))
            ).ul.find_all("a")
        ]
        stars: list[str] = [
            a.text
            for a in soup.find(
                lambda tag: tag.name == "li"
                and tag.find(["a", "span"], string=re.compile("Stars?"))
            ).ul.find_all("a")
        ]
        writers: list[str] = [
            a.text
            for a in soup.find(
                lambda tag: tag.name == "li"
                and tag.find(["a", "span"], string=re.compile("Writers?"))
            ).ul.find_all("a")
        ]
        tags: list[str] = [
            a.text
            for a in soup.main.div.section.section.find_all("div", recursive=False)[2]
            .section.section.find_all("div", recursive=False)[2]
            .find_all("div", recursive=False)[1]
            .div.section.div.find_all("a")
        ]
        synopsis: str = (
            soup.main.div.section.section.find_all("div", recursive=False)[2]
            .section.section.find_all("div", recursive=False)[2]
            .find_all("div", recursive=False)[1]
            .div.section.p.find_all("span", recursive=False)[1]
            .text
        )
        age_rating: str = (
            soup.main.div.section.section.find_all("div", recursive=False)[2]
            .section.section.find_all("div", recursive=False)[1]
            .find_all("li")[1]
            .a.text
        )
    except AttributeError:
        raise NotFoundException("Item not found") from None

    return ImdbScraperResult(
        imdb_id=imdb_id,
        imdb_url=imdb_url,
        age_rating=age_rating,
        directors=directors,
        duration=duration,
        image_url=image_url,
        release_year=release_year,
        stars=stars,
        synopsis=synopsis,
        tags=tags,
        title=title,
        writers=writers,
    )
