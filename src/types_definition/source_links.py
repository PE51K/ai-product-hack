from typing import TypedDict, Optional


class SearchResult(TypedDict):
    url: str
    domain: str
    title: str


class SourceLink(TypedDict):
    link: str
    confidence_rate: float  # от 0 до 1


class TextInfoFromSource(TypedDict):
    html_text: str
    pdf_texts: Optional[list[str]] # Может быть несколько PDF на сайте (если реализуется)
    source: SourceLink
