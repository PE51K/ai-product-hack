from yandex_gpt import YandexGPT, YandexGPTConfigManagerForAPIKey
from typing import Dict


async def process_message(sem, message, yandex_gpt):
    try:
        async with sem:
            result = await yandex_gpt.get_async_completion(messages=message, temperature=0.5, max_tokens=9999, timeout=100)
            return result
    except Exception as e:
        print(e)
        return ""


async def get_product_description(
        product_type: str,
        product_characteristics: Dict[str, any],
) -> str:
    """
    Create product description using Yandex GPT API.

    Args:
      product_type (str): The type of the product.
      product_characteristics (str): The characteristics of the product.

    Returns:
      str: The generated product description.
    """
    yandex_gpt = YandexGPT(config_manager=YandexGPTConfigManagerForAPIKey())
    description_parts: list[str] = []

    ...

    return description
