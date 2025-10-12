import re

import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel

from scrapers.exceptions import NotFoundException


class AmazonSeEanSearchResult(BaseModel):
    asin: str
    ean: str


class AmazonSeAsinScrapResult(BaseModel):
    asin: str
    ean: str | None
    title: str | None
    image_url: str | None
    description: str | None
    run_time: str | None
    director: str | None
    actors: str | None
    studio: str | None
    release_date: str | None
    language: str | None
    subtitles: str | None
    audio_format: str | None
    number_of_discs: str | None


def search_amazon_se_ean(ean: str) -> AmazonSeEanSearchResult:
    search_doc = requests.get(
        f"https://www.amazon.se/s?k={ean}",
        headers={
            "Accept": "text/html",
            "Accept-Language": "en-US,en;q=0.5",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:141.0) Gecko/20100101 Firefox/141.0",
        },
    )
    search_soup = BeautifulSoup(search_doc.text, "html.parser")
    if list_item_tag := search_soup.find("div", attrs={"role": "listitem"}):
        return AmazonSeEanSearchResult(asin=list_item_tag.attrs["data-asin"], ean=ean)
    else:
        raise NotFoundException("EAN not found")


def scrape_amazon_se_asin(asin: str, ean: str | None = None):
    scrape_doc = requests.get(
        f"https://www.amazon.se/dp/{asin}",
        headers={
            "Accept": "text/html",
            "Accept-Language": "en-US,en;q=0.5",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:141.0) Gecko/20100101 Firefox/141.0",
        },
    )
    scrape_soup = BeautifulSoup(scrape_doc.text, "html.parser")

    title_tag = scrape_soup.find("h1", attrs={"id": "title"})
    title = title_tag.text.strip() if title_tag else None

    image_tag = scrape_soup.find("img", attrs={"id": "landingImage"})
    image_url = image_tag.attrs["src"] if image_tag else None

    description_tag = scrape_soup.find("div", attrs={"id": "productDescription"})
    description = description_tag.text.strip() if description_tag else None

    description_fields = (
        "run time",
        "director",
        "actors",
        "studio",
        "release date",
        "language",
        "subtitles",
        "audio format",
        "number of discs",
    )
    description_data = {}
    if details_div := scrape_soup.find(
        "div", attrs={"id": "detailBullets_feature_div"}
    ):
        for field in description_fields:
            field_key = field.replace(" ", "_")
            if field_tag := details_div.find(
                "span", string=re.compile(rf"{field}", re.IGNORECASE)
            ):
                value_tag = field_tag.find_next("span")
                description_data[field_key] = (
                    value_tag.text.strip() if value_tag else None
                )
            else:
                description_data[field_key] = None

    return AmazonSeAsinScrapResult(
        asin=asin,
        ean=ean,
        title=title,
        image_url=image_url,
        description=description,
        run_time=description_data.get("run_time"),
        director=description_data.get("directors"),
        actors=description_data.get("actors"),
        studio=description_data.get("studio"),
        release_date=description_data.get("release_date"),
        language=description_data.get("language"),
        subtitles=description_data.get("subtitles"),
        audio_format=description_data.get("audio_format"),
        number_of_discs=description_data.get("number_of_discs"),
    )
