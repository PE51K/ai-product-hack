import os
from typing import List
import asyncio

from yandex_gpt import YandexGPT, YandexGPTConfigManagerForAPIKey

from .search import fetch_search_results
from .xml_parsing import parse_xml_response
from types_definition import ProductInfo, SourceLink, SearchResult


async def process_message(sem, message, yandex_gpt):
    async with sem:
        result = await yandex_gpt.get_async_completion(messages=message, temperature=0.0, max_tokens=10, timeout=100)
        print(result)
        return result


async def rate_search_results(search_results: List[SearchResult], yandex_gpt, sem) -> List[float]:
    messages = [[
        {
            "role": "system",
            "text": "".join([
                "You are technical expert. ",
                "Rate given search result's trustfulness from 0 to 1 following given rules: ",
                "rate 1.0: the official website of the manufacturer (Russia); ",
                "rate: 0.9: the manufacturer website in another language or in another country; ",
                "rate: 0.7: the official distributor's website; ",
                "rate: 0.5: the official online store of the manufacturer / ",
                "brand reviews from the official website / ",
                "online store of the manufacturer / ",
                "distributor packaging photo; ",
                "rate: 0.3: online store or forum. ",
                "give only float number without additional comments as answer. ",
            ])
        },
        {
            "role": "user",
            "text": "".join([
                f"Search result: {search_result['title']}; ",
                f"Domain: {search_result['domain']}; ",
                f"URL: {search_result['url']}",
            ])
        }
    ] for search_result in search_results]

    sem = asyncio.Semaphore(10)
    tasks = [process_message(sem, message, yandex_gpt) for message in messages]
    results = await asyncio.gather(*tasks)

    return [float(result) for result in results]


async def search_and_rate(product_info: ProductInfo) -> List[SourceLink]:
    base_link = os.getenv("YANDEX_SEARCH_BASE_LINK")
    folder_id = os.getenv("YANDEX_SEARCH_FOLDER_ID")
    api_key = os.getenv("YANDEX_SEARCH_API_KEY")

    query = f"{product_info['brand_name']} {product_info['model_name']} {product_info['part_number']}"

    response = await fetch_search_results(base_link, folder_id, api_key, query)
    # print(response)
    search_results: List[SearchResult] = parse_xml_response(response)


    res_deb = parse_xml_response(response)
    print(res_deb)
    print("len= ", len(res_deb))

    search_results_rates = await rate_search_results(
        search_results,
        YandexGPT(YandexGPTConfigManagerForAPIKey()),
        asyncio.Semaphore(1)
    )

    return [
        SourceLink(
            link=search_result["url"],
            confidence_rate=search_result_rate
        ) for search_result, search_result_rate in zip(search_results, search_results_rates)
    ]


if __name__ == "__main__":
    os.chdir("../../")

    from dotenv import load_dotenv
    load_dotenv("env/.env.yandex_search")
    load_dotenv("env/.env.api_key")

    product_info = ProductInfo(
        brand_name="ACER",
        model_name="CC715-91P-X7V8",
        part_number="NX.C5FER.001"
    )

    import asyncio
    print(asyncio.run(search_and_rate(product_info)))
