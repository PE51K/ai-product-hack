import os
import sys
from typing import List
import asyncio

from yandex_gpt import YandexGPT, YandexGPTConfigManagerForAPIKey

# # Определите путь к папке types_definition
# parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# types_definition_dir = os.path.join(parent_dir, 'types_definition')

# # Добавьте этот путь к sys.path
# sys.path.append(types_definition_dir)

# Определите путь к корню проекта
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

# Определите путь к папке types_definition и добавьте его в sys.path
types_definition_dir = os.path.join(root_dir, 'src', 'types_definition')
sys.path.append(types_definition_dir)

# Теперь можно импортировать модули из types_definition
from source_links import SourceLink, SearchResult, TextInfoFromSource
from product_info import ProductInfo


from .search import fetch_search_results
from .xml_parsing import parse_xml_response
# from types_definition.source_links import SourceLink, SearchResult, TextInfoFromSource
# from types_definition.product_info import ProductInfo

# from src.types_definition.source_links import SourceLink, SearchResult, TextInfoFromSource
# from src.types_definition.product_info import ProductInfo


async def process_message(sem, message, yandex_gpt):
    async with sem:
        try:
            # result = await yandex_gpt.get_async_completion(messages=message, temperature=0.0, max_tokens=10, timeout=100)
            result = yandex_gpt.get_sync_completion(messages=message, temperature=0.0, max_tokens=10)
            print(result)
            return result
        except Exception as e:
            print("e")
            return 0.5


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

    # sem = asyncio.Semaphore(10)
    sem = asyncio.Semaphore(1)
    tasks = [process_message(sem, message, yandex_gpt) for message in messages]
    results = await asyncio.gather(*tasks)

    results_float = []

    for result in results:
        try:
            results_float.append(float(result))
        except Exception as e:
            print(e)
            results_float.append(0.5)

    return results_float


async def search_and_rate(product_info: ProductInfo) -> List[SourceLink]:
    base_link = os.getenv("YANDEX_SEARCH_BASE_LINK")
    folder_id = os.getenv("YANDEX_SEARCH_FOLDER_ID")
    api_key = os.getenv("YANDEX_SEARCH_API_KEY")

    query = f"{product_info['brand_name']} {product_info['model_name']} {product_info['part_number']}"

    response = await fetch_search_results(base_link, folder_id, api_key, query)
    # print(response)
    search_results: List[SearchResult] = parse_xml_response(response)

    # Для тестирования 
    # search_results = search_results[:5]
    res_deb = parse_xml_response(response)
    print(res_deb)
    print("len= ", len(res_deb))

    print("begin search_results_rates")
    search_results_rates = await rate_search_results(
        search_results,
        YandexGPT(YandexGPTConfigManagerForAPIKey()),
        asyncio.Semaphore(1)
    )
    print("finish search_results_rates")

    return [
        SourceLink(
            link=search_result["url"],
            confidence_rate=search_result_rate
        ) for search_result, search_result_rate in zip(search_results, search_results_rates)
    ]


if __name__ == "__main__":
    # os.chdir("../../")

    from dotenv import load_dotenv
    load_dotenv("env/.env.yandex_search")
    load_dotenv("env/.env.api_key")

    product_info = ProductInfo(
        brand_name="ACER",
        model_name="CC715-91P-X7V8",
        part_number="NX.C5FER.001"
    )

    import asyncio
    link = asyncio.run(search_and_rate(product_info))
    print(link)
