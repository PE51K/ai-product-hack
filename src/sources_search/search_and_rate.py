import os
from typing import List

from src.sources_search.search import fetch_search_results
from src.sources_search.xml_parsing import parse_xml_response
from src.types import ProductInfo, SourceLink, SearchResult


def rate_search_result(search_result: SearchResult) -> float:
    return 1.0


async def search_and_rate(product_info: ProductInfo) -> List[SourceLink]:
    base_link = os.getenv("YANDEX_SEARCH_BASE_LINK")
    folder_id = os.getenv("YANDEX_SEARCH_FOLDER_ID")
    api_key = os.getenv("YANDEX_SEARCH_API_KEY")

    query = f"{product_info['brand_name']} {product_info['model_name']} {product_info['part_number']}"

    response = await fetch_search_results(base_link, folder_id, api_key, query)
    search_results: List[SearchResult] = parse_xml_response(response)
    return [
        SourceLink(
            link=search_result["url"],
            confidence_rate=rate_search_result(search_result)
        ) for search_result in search_results
    ]


if __name__ == "__main__":
    os.chdir("../../")

    from dotenv import load_dotenv
    load_dotenv("env/.env.yandex_search")

    product_info = ProductInfo(
        brand_name="ACER",
        model_name="CC715-91P-X7V8",
        part_number="NX.C5FER.001"
    )

    import asyncio
    print(asyncio.run(search_and_rate(product_info)))
