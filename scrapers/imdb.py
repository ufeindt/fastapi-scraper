import re
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel


class ImdbSearchResult(BaseModel):
    title: str
    id: str


class ImdbScraperResult(BaseModel):
    imdb_id: str
    title: str
    image_url: str
    duration: str
    release_year: str
    directors: list[str]
    stars: list[str]
    writers: list[str]
    tags: list[str]
    synopsis: str
    age_rating: str


def search_imdb(title: str, lang: str = "en-US") -> list[ImdbSearchResult]:
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
    title_list_items = title_section.div.next_sibling.ul.find_all("li", recursive=False)

    results = []
    for item in title_list_items:
        title = item.find("a").text
        if id_match := re.search(r"\/title\/(tt[0-9]+)\/", item.find("a").get("href")):
            results.append(
                ImdbSearchResult(
                    title=title,
                    id=id_match.group(1),
                )
            )

    return results


def scrape_imdb(imdb_id: str, lang: str = "en-US") -> ImdbScraperResult:
    html_doc = requests.get(
        f"https://www.imdb.com/title/{imdb_id}/",
        headers={
            "Accept": "text/html",
            "Accept-Language": f"{lang},en;q=0.5",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:141.0) Gecko/20100101 Firefox/141.0",
        },
    )
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
        .div.section.p.text
    )
    age_rating: str = (
        soup.main.div.section.section.find_all("div", recursive=False)[2]
        .section.section.find_all("div", recursive=False)[1]
        .find_all("li")[1]
        .a.text
    )

    return ImdbScraperResult(
        imdb_id=imdb_id,
        title=title,
        image_url=image_url,
        duration=duration,
        release_year=release_year,
        directors=directors,
        stars=stars,
        writers=writers,
        tags=tags,
        synopsis=synopsis,
        age_rating=age_rating,
    )
