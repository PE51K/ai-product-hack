from typing import TypedDict


class SearchResult(TypedDict):
    url: str
    domain: str
    title: str


class SourceLink(TypedDict):
    link: str
    confidence_rate: float  # от 0 до 1
