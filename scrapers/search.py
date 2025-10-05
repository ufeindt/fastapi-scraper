from enum import Enum
from typing import TypedDict

from cachetools import TTLCache, cached

from .exceptions import InvalidTypeException
from .imdb import scrape_imdb_id, search_imdb_title


class SearchType(str, Enum):
    EAN = "ean"
    IMDB_ID = "imdb_id"
    ISBN = "isbn"
    TITLE = "title"


class SearchCategory(str, Enum):
    BOOK = "book"
    MOVIE = "movie"


class SearchTypeDict(TypedDict):
    title: str
    search_type: SearchType


class SearchCategoryDict(TypedDict):
    title: str
    search_category: SearchCategory
    search_types: dict[SearchType, SearchTypeDict]


SEARCH_HIERARCHY: dict[SearchCategory, SearchCategoryDict] = {
    SearchCategory.BOOK: {
        "title": "Book",
        "search_category": SearchCategory.BOOK,
        "search_types": {
            SearchType.ISBN: {"title": "ISBN", "search_type": SearchType.ISBN},
            SearchType.TITLE: {"title": "Title", "search_type": SearchType.TITLE},
        },
    },
    SearchCategory.MOVIE: {
        "title": "Movie",
        "search_category": SearchCategory.MOVIE,
        "search_types": {
            SearchType.EAN: {"title": "EAN", "search_type": SearchType.EAN},
            SearchType.TITLE: {"title": "Title", "search_type": SearchType.TITLE},
            SearchType.IMDB_ID: {"title": "IMDB ID", "search_type": SearchType.IMDB_ID},
        },
    },
}


@cached(cache=TTLCache(maxsize=1024, ttl=600))
def search_query(search_category: SearchCategory, search_type: SearchType, query: str):
    match search_category:
        case SearchCategory.BOOK.value:
            match search_type:
                case SearchType.ISBN.value:
                    raise NotImplementedError("ISBN search not implemented yet")
                case SearchType.TITLE.value:
                    raise NotImplementedError("Movie title search not implemented yet")
                case _:
                    raise InvalidTypeException("Invalid search type")
        case SearchCategory.MOVIE.value:
            match search_type:
                case SearchType.IMDB_ID.value:
                    return scrape_imdb_id(query)
                case SearchType.TITLE.value:
                    matches = search_imdb_title(query)
                    return scrape_imdb_id(matches[0].id)
                case SearchType.EAN.value:
                    raise NotImplementedError("EAN search not implemented yet")
                case _:
                    raise InvalidTypeException("Invalid search type")
        case _:
            raise InvalidTypeException("Invalid search category")
