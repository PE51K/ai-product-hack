import streamlit as st
import json
import asyncio
import logging
import nest_asyncio

from types_definition.product_info import ProductInfo
from types_definition.source_links import SearchResult, SourceLink, TextInfoFromSource
from sources_search.search_and_rate import search_and_rate
from utils.content_retriever import get_source_links_single

logging.basicConfig(filename='app.log', level=logging.INFO)

product_info = ProductInfo(
    brand_name="ACER",
    model_name="CC715-91P-X7V8",
    part_number="NX.C5FER.001"
)

source_link = SourceLink(link="https://example.com", confidence_rate=0.8)

text_info = TextInfoFromSource(
    html_text="<p>This is some text from the source.</p>",
    pdf_texts=["Text from PDF 1", "Text from PDF 2"],
    source=source_link,
)


# def search_and_rate(brand_name, model_name, part_number):
#     """
#     Функция имитирует первый алгоритм, возвращая объект SourceLink.

#     Args:
#         brand_name (str): Название бренда.
#         model_name (str): Название модели.
#         part_number (int, optional): Номер детали.

#     Returns:
#         SourceLink: Объект SourceLink с ссылкой и показателем уверенности.
#     """
#     return SourceLink(link="https://example.com", confidence_rate=0.8) 


# def get_source_links(source_link: SourceLink):
#     """
#     Функция имитирует второй алгоритм, извлекая текст из HTML и PDF по ссылке из объекта SourceLink.

#     Args:
#         source_link (SourceLink): Объект SourceLink с ссылкой.

#     Returns:
#         TextInfoFromSource: Объект TextInfoFromSource с извлеченным текстом.
#     """
#     html_text = "Извлеченный текст HTML"
#     pdf_texts = ["Текст из PDF 1", "Текст из PDF 2"]
#     return TextInfoFromSource(html_text=html_text, pdf_texts=pdf_texts, source=source_link)


def generate_info_model(text_info: TextInfoFromSource):
    """
    Функция имитирует генерацию JSON-инфомодели продукта на основе извлеченного текста.

    Args:
        text_info (TextInfoFromSource): Объект TextInfoFromSource с извлеченным текстом.

    Returns:
        str: JSON-строка, представляющая инфомодель продукта.
    """
    # html_text = text_info.html_text
    # pdf_texts = text_info.pdf_texts

    # # Извлечение информации из текста
    # info_model = {}

    # # Пример извлечения характеристик из HTML-текста
    # for match in re.finditer(r"<p>(.*?)</p>", html_text):
    #     text = match.group(1)
    #     if ":" in text:
    #         key, value = text.split(":")
    #         info_model[key.strip()] = value.strip()

    # # Пример извлечения характеристик из PDF-текстов
    # for pdf_text in pdf_texts:
    #     pass
    #     # ... (Логика извлечения информации из pdf_text)
    #     # ... (Обновление info_model)

    # ... (Дополнительная логика извлечения информации)

    info_model = {
        "характеристика1": "значение1",
        "характеристика2": "значение2",
        # ...
    }

    # Преобразование info_model в JSON
    json_model = json.dumps(info_model, indent=4)

    return json_model

async def async_search_and_rate(product_info):
    return await search_and_rate(product_info)


async def main():
    # Разделение приложения на разделы с помощью заголовков
    st.title("Визуализация ML-проекта")

    # Раздел для ввода данных пользователем
    with st.form(key="data_input"):
        brand_name = st.text_input("Название бренда")
        model_name = st.text_input("Название модели")
        part_number = st.text_input("Номер детали (опционально)")
        submit_button = st.form_submit_button("Запустить")

        # # Для проверки 
        # brand_name = "TCL"
        # model_name = "20 SE"
        # part_number = "T671H-2ALCRU12"

        # product_info = ProductInfo(
        #     brand_name=brand_name,
        #     model_name=model_name,
        #     part_number=part_number)

        product_info = ProductInfo(
            brand_name="ACER",
            model_name="CC715-91P-X7V8",
            part_number="NX.C5FER.001")

    # Раздел для отображения результатов
    with st.expander("Результаты"):
        if submit_button:
            try:
                # link = await search_and_rate(product_info)
                # link = asyncio.get_event_loop().run_until_complete(search_and_rate(product_info))
                loop = asyncio.get_event_loop()
                links = loop.run_until_complete(async_search_and_rate(product_info))
                print("begin get_source_links_single(link)")
                text_info = get_source_links_single(links[0])
                # text_info = get_source_links_single(link)
                print("finish get_source_links_single(link)")
                print("text_info ", text_info)
                info_model = generate_info_model(text_info)

                st.json(info_model)

                print(info_model)

                st.session_state["info_model"] = info_model
                st.session_state["results_ready"] = True
                st.success("Результаты успешно обработаны. Нажмите на 'Показать результаты' для отображения.")
            except TimeoutError:
                logging.error("Превышено время ожидания Yandex GPT.")
                st.error("Превышено время ожидания Yandex GPT.")

            except Exception as e:
                logging.error(f"Ошибка: {str(e)}")
                st.error(f"Ошибка: {str(e)}")

        # Кнопка для отображения результатов
        if st.button("Показать результаты"):
            if st.session_state.get("results_ready", False):
                st.json(st.session_state["info_model"])
            else:
                st.warning("Сначала выполните обработку данных.")

if __name__ == "__main__":
    # main()

    from dotenv import load_dotenv
    load_dotenv("env/.env.yandex_search")
    load_dotenv("env/.env.api_key")

    # Enable nest_asyncio
    nest_asyncio.apply()

    asyncio.run(main())
