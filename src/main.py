import streamlit as st
import json

# Функция-заглушка 
def get_link_and_confidence_rate(brand_name, model_name, part_number):
    """
    Функция имитирует первый алгоритм, возвращая ссылку и показатель уверенности.

    Args:
        brand_name (str): Название бренда.
        model_name (str): Название модели.
        part_number (int, optional): Номер детали.

    Returns:
        tuple: Ссылка (str) и показатель уверенности (float).
    """
    return "https://example.com", 0.8  # Пример

# Функция-заглушка 
def process_html_and_pdf(link):
    """
    Функция имитирует второй алгоритм, извлекая текст из HTML и PDF по ссылке.

    Args:
        link (str): Ссылка на источник.

    Returns:
        tuple: Извлеченный текст HTML (str) и список текстов PDF (list[str]).
    """
    return "Извлеченный текст HTML", ["Текст из PDF 1", "Текст из PDF 2"]  # Пример

# Функция-заглушка 
def generate_info_model(html_text, pdf_texts):
    """
    Функция имитирует третий алгоритм, генерируя JSON-инфомодель на основе текста.

    Args:
        html_text (str): Извлеченный текст HTML.
        pdf_texts (list[str]): Список текстов PDF.

    Returns:
        str: JSON-строка, представляющая инфомодель продукта.
    """
    info_model = {
        "характеристика1": "значение1",
        "характеристика2": "значение2",
        # ...
    }
    return json.dumps(info_model)

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
        link, confidence_rate = get_link_and_confidence_rate(brand_name, model_name, part_number)
        html_text, pdf_texts = process_html_and_pdf(link)
        info_model = generate_info_model(html_text, pdf_texts)

        st.write(f"Ссылка: {link}")
        st.write(f"Уверенность: {confidence_rate:.2f}")
        st.write(f"HTML-текст: {html_text}")
        st.write(f"PDF-тексты: {pdf_texts}")
        st.json(info_model)
