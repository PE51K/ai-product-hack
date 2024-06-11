from yandex_gpt import YandexGPT, YandexGPTConfigManagerForAPIKey
from typing import Dict, List


def get_product_summary(
        product_type: str,
        product_brand: str,
        product_name: str,
        product_characteristics: Dict[str, any],
        pdf_texts: List[str]
) -> str:
    """
    Create product summary using Yandex GPT API.

    Args:
      product_type (str): The type of the product.
      product_brand (str): The brand of the product.
      product_name (str): The model name of the product.
      product_characteristics (Dict[str, any]): The characteristics of the product.
      pdf_texts (List[str]): Texts extracted from PDF documents related to the product.

    Returns:
      str: The generated product summary.
    """
    yandex_gpt = YandexGPT(config_manager=YandexGPTConfigManagerForAPIKey())

    system_prompt = (
        """
        Задача: Создать краткое маркетинговое описание товара (саммари), преследующее цель SEO оптимизации и улучшения поиска товара для клиента.
    
        Требования к содержанию:
        1. Краткость и емкость: Саммари должно быть кратким, но содержательным. Объем текста - не более 2-3 предложений.
        2. Фокус на ключевые преимущества: Выделить одно-два ключевых преимущества товара.
        3. SEO-оптимизация: Включить ключевые слова, которые помогут улучшить поиск товара.
        4. Ясность и понятность: Текст должен быть понятным и легко читаемым.
        5. Избегать лишней информации: Не включать подробности, которые могут отвлекать от основных преимуществ.
        6. Призыв к действию: Включить призыв к действию, чтобы мотивировать клиента на покупку или изучение товара.
    
        Пример саммари: 
        "Ноутбук Apple MacBook Pro 2024 с процессором Apple M2 и 16 ГБ оперативной памяти обеспечивает высокую производительность и длительное время автономной работы. Идеальный выбор для профессионалов и творческих людей."
        """
    )

    def format_characteristics(characteristics: Dict[str, any]) -> str:
        formatted_characteristics = ""
        for key, value in characteristics.items():
            formatted_characteristics += f"- {key}: {value}\n"
        return formatted_characteristics

    def format_pdf_texts(pdf_texts: List[str]) -> str:
        formatted_pdf_texts = ""
        for index, text in enumerate(pdf_texts):
            formatted_pdf_texts += f"Текст из дополнительного документа {index + 1}:\n{text}\n\n"
        return formatted_pdf_texts

    product_characteristics_formatted = format_characteristics(product_characteristics)
    pdf_texts_formatted = format_pdf_texts(pdf_texts)

    user_prompt_template = (
        """
        Тип товара: {product_type}
        Бренд: {product_brand}
        Модель: {product_name}
        Характеристики:
        {product_characteristics}
        {pdf_texts}
        """
    )

    user_prompt = user_prompt_template.format(
        product_type=product_type,
        product_brand=product_brand,
        product_name=product_name,
        product_characteristics=product_characteristics_formatted,
        pdf_texts=pdf_texts_formatted
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    summary = yandex_gpt.get_sync_completion(messages=messages, temperature=0.5, max_tokens=300)

    return summary


def get_summary_from_description(
        product_description: str
) -> str:
    """
    Create product summary using Yandex GPT API based on a detailed product description.

    Args:
      product_description (str): The detailed product description.

    Returns:
      str: The generated product summary.
    """
    yandex_gpt = YandexGPT(config_manager=YandexGPTConfigManagerForAPIKey())

    # Generate system prompt for summarization
    system_prompt = (
        """
        Роль: Вы являетесь экспертом по маркетингу и написанию качественных текстов для описания продуктов. Ваша задача - создать краткое маркетинговое описание товара (саммари), преследующее цель SEO оптимизации и улучшения поиска товара для клиента.
    
        Задача: Создать краткое маркетинговое описание товара (саммари), основываясь на предоставленном детальном описании товара.
    
        Требования к содержанию:
        1. Краткость и емкость: Саммари должно быть кратким, но содержательным. Объем текста - не более 2-3 предложений.
        2. Фокус на ключевые преимущества: Выделить одно-два ключевых преимущества товара.
        3. SEO-оптимизация: Включить ключевые слова, которые помогут улучшить поиск товара.
        4. Ясность и понятность: Текст должен быть понятным и легко читаемым.
        5. Избегать лишней информации: Не включать подробности, которые могут отвлекать от основных преимуществ.
        6. Призыв к действию: Включить призыв к действию, чтобы мотивировать клиента на покупку или изучение товара.
    
        Пример саммари: 
        "Ноутбук Apple MacBook Pro 2024 с процессором Apple M2 и 16 ГБ оперативной памяти обеспечивает высокую производительность и длительное время автономной работы. Идеальный выбор для профессионалов и творческих людей."
        """
    )

    user_prompt = f"Детальное описание продукта:\n\n{product_description}"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    summary = yandex_gpt.get_sync_completion(messages=messages, temperature=0.5, max_tokens=300)

    return summary
    