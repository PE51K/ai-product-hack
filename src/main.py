import streamlit as st
import json

from types_definition.product_info import ProductInfo
from types_definition.source_links import SearchResult, SourceLink, TextInfoFromSource
# from sources_search import search_and_rate


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


def search_and_rate(brand_name, model_name, part_number):
    """
    Функция имитирует первый алгоритм, возвращая объект SourceLink.

    Args:
        brand_name (str): Название бренда.
        model_name (str): Название модели.
        part_number (int, optional): Номер детали.

    Returns:
        SourceLink: Объект SourceLink с ссылкой и показателем уверенности.
    """
    return SourceLink(link="https://example.com", confidence_rate=0.8) 


def get_source_links(source_link: SourceLink):
    """
    Функция имитирует второй алгоритм, извлекая текст из HTML и PDF по ссылке из объекта SourceLink.

    Args:
        source_link (SourceLink): Объект SourceLink с ссылкой.

    Returns:
        TextInfoFromSource: Объект TextInfoFromSource с извлеченным текстом.
    """
    html_text = "Извлеченный текст HTML"
    pdf_texts = ["Текст из PDF 1", "Текст из PDF 2"]
    return TextInfoFromSource(html_text=html_text, pdf_texts=pdf_texts, source=source_link)


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


def main():
    # Разделение приложения на разделы с помощью заголовков
    st.title("Визуализация ML-проекта")

    # Раздел для ввода данных пользователем
    with st.form(key="data_input"):
        brand_name = st.text_input("Название бренда")
        model_name = st.text_input("Название модели")
        part_number = st.text_input("Номер детали (опционально)")
        submit_button = st.form_submit_button("Запустить")

    # Раздел для отображения результатов
    with st.expander("Результаты"):
        if submit_button:
            link = search_and_rate(brand_name, model_name, part_number)
            text_info = get_source_links(link)
            info_model = generate_info_model(text_info)

            # st.write(f"Ссылка: {link}")
            # # st.write(f"Уверенность: {confidence_rate:.2f}")
            # st.write(f"HTML-текст: {html_text}")
            # st.write(f"PDF-тексты: {pdf_texts}")
            st.json(info_model)

if __name__ == "__main__":
    main()
