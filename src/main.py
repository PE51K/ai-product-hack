import streamlit as st
from streamlit_option_menu import option_menu
import json
import asyncio
import logging
import nest_asyncio
import tempfile
import os
import io

from types_definition.product_info import ProductInfo
from types_definition.source_links import SearchResult, SourceLink, TextInfoFromSource
from sources_search.search_and_rate import search_and_rate
from utils.content_retriever import get_source_links_single
from utils.content_retriever import extract_text_from_pdf
from utils.extract_characteristics import get_product_characteristics_from_sources_single
from description_gen.description import get_product_description
from description_gen.summary import get_product_summary, get_summary_from_description
from test_data import laptop_characteristics_json

logging.basicConfig(filename='app.log', level=logging.INFO)


# product_info = ProductInfo(
#     brand_name="ACER",
#     model_name="CC715-91P-X7V8",
#     part_number="NX.C5FER.001"
# )

# source_link = SourceLink(link="https://example.com", confidence_rate=0.8)

# text_info = TextInfoFromSource(
#     html_text="<p>This is some text from the source.</p>",
#     pdf_texts=["Text from PDF 1", "Text from PDF 2"],
#     source=source_link,
# )

# Хранение контекста
if "summary" not in st.session_state:
    st.session_state["summary"] = None
if "product_description" not in st.session_state:
    st.session_state["product_description"] = None
if "results_ready_1_task" not in st.session_state:
    st.session_state["results_ready_1_task"] = False
if "results_ready_2t_task" not in st.session_state:
    st.session_state["results_ready_2t_task"] = False
if "info_model" not in st.session_state:
    st.session_state["info_model"] = None


# Значения по умолчанию
default_product_type = "ноутбук"
default_brand_name = "AQUARIUS"
default_model_name = "CMP NS483 (Исп.2)"
default_part_number = "NS4831524116Q151E90NT2NNNN2"
default_links = "https://www.aq.ru/product/aquarius-cmp-ns483-isp-2/"


async def async_search_and_rate(product_info):
    return await search_and_rate(product_info)


def product_input_interface():
    # if "summary" not in st.session_state:
    #     st.session_state["summary"] = None

    with st.form(key='product_form'):

        # product_type = st.text_input('Тип продукта')
        # brand_name = st.text_input('Название бренда')
        # model_name = st.text_input('Модель (как она написана официальным производителем)')
        # part_number = st.text_input('Парт-номер производителя (если есть)')

        # # JSON файл с характеристиками товара
        # characteristics_json = st.file_uploader('Характеристики товара', type=['json'])

        # # Набор ссылок на известные ресурсы про товар в интернете
        # links = st.text_area('Набор ссылок на известные ресурсы про товар в интернете')

        # Поля с заданными значениями по умолчанию
        product_type = st.text_input(
            'Тип продукта', value=default_product_type)
        brand_name = st.text_input('Название бренда', value=default_brand_name)
        model_name = st.text_input(
            'Модель (как она написана официальным производителем)', value=default_model_name)
        part_number = st.text_input(
            'Парт-номер производителя (если есть)', value=default_part_number)
        # Поле для загрузки JSON файла с характеристиками товара
        characteristics_json = st.file_uploader(
            'Характеристики товара', type=['json'])
        # Набор ссылок на известные ресурсы про товар в интернете
        links = st.text_area(
            'Набор ссылок на известные ресурсы про товар в интернете', value=default_links)

        # PDF с маркетинговыми материалами и инструкцией пользователя
        data_files = st.file_uploader(
            'PDF с маркетинговыми материалами и инструкцией пользователя (если есть)', accept_multiple_files=True, type=['pdf', 'txt'])

        submit_button_task2 = st.form_submit_button(label='Запустить')
        show_downloaded_files_button_2 = st.form_submit_button(
            label='Показать введенные данные')
        # load_test_data_button = st.form_submit_button(label='Подгрузить тестовые данные')
        # Место для вывода сообщений

        characteristics = {}

        # if st.button('Показать введенные данные'):
        if show_downloaded_files_button_2:
            if characteristics_json is not None:
                print("characteristics_json", characteristics_json)
                characteristics = json.load(characteristics_json)
            else:
                characteristics = {}

            st.write("### Введенные данные:")
            st.write(f"**Тип продукта:** {product_type}")
            st.write(f"**Название бренда:** {brand_name}")
            st.write(f"**Модель:** {model_name}")
            st.write(f"**Парт-номер производителя:** {part_number}")
            st.write(f"**Ссылки на известные ресурсы:**\n{links}")
            if characteristics_json is not None:
                st.write("**Характеристики товара:**")
                st.json(characteristics)

            # if data_files:
            #     try:
            #         st.write("**Загруженные файлы:**")
            #         for data_file in data_files:
            #             st.write(data_file.name)
            #             # Отобразить содержимое текстовых файлов
            #             if data_file.type == "text/plain":
            #                 content = data_file.read().decode("utf-8")
            #                 # st.text(content)
            #                 st.text_area(f"Содержимое txt файла {data_file.name}", value=content, height=300)
            #             elif data_file.type == "application/pdf":
            #                 pdf_bytes = data_file.read()
            #                 # Создаем временный файл
            #                 with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_pdf:
            #                     temp_pdf.write(pdf_bytes)
            #                     temp_pdf_path = temp_pdf.name
            #                 extracted_text = extract_text_from_pdf(temp_pdf_path)
            #                 # print(extracted_text)
            #                 st.text_area(f"Содержимое PDF файла {data_file.name}", value=extracted_text, height=300)
            #                 # print("remove data files")
            #                 # os.remove(temp_pdf_path)
            #     except Exception as e:
            #         logging.error(f"Ошибка загрузки фаилов: {str(e)}")
            #         st.error(f"Ошибка: {str(e)}")

    # Раздел для отображения результатов
    with st.expander("Результаты задача2"):
        if submit_button_task2:
            try:
                data_file_content = []

                for data_file in data_files:
                    st.write(data_file.name)
                    # Отобразить содержимое текстовых файлов
                    if data_file.type == "text/plain":
                        content = data_file.read().decode("utf-8")
                        # st.text(content)
                        data_file_content.append(content)

                    elif data_file.type == "application/pdf":
                        pdf_bytes = data_file.read()
                        # Создаем временный файл
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_pdf:
                            temp_pdf.write(pdf_bytes)
                            temp_pdf_path = temp_pdf.name
                        extracted_text = extract_text_from_pdf(temp_pdf_path)
                        data_file_content.append(extracted_text)
                        # print(extracted_text)
                        # st.text_area(f"Содержимое PDF файла {data_file.name}", value=extracted_text, height=300)
                        # print("remove data files")
                        # os.remove(temp_pdf_path)
                
                # for elem1 in data_file_content:
                #     print(" data_file_content  ", data_file_content)

                product_brand = brand_name
                product_name = model_name
                loop = asyncio.get_event_loop()

                product_description = get_product_description(
                    product_type, product_brand, product_name, characteristics, data_file_content)
                print("product_description  !!!", product_description)

                st.session_state["product_description"] = product_description
                # print("product_description  !!!", st.session_state["product_description"])

                summary = get_summary_from_description(product_description)
                # print("summary", summary)
                st.session_state["summary"] = summary

                st.session_state["results_ready_2t_task"] = True
                st.success(
                    "Результаты успешно обработаны. Нажмите на 'Показать результаты' для отображения.")
            except TimeoutError:
                logging.error("Превышено время ожидания Yandex GPT.")
                st.error("Превышено время ожидания Yandex GPT.")

            except Exception as e:
                logging.error(f"Ошибка: {str(e)}")
                st.error(f"Ошибка: {str(e)}")

        # Кнопка для отображения результатов
        if st.session_state["results_ready_2t_task"] == True and st.button("Показать результаты"):

            # st.json(st.session_state["summary"])
            st.text_area(f"Саммари маркетингового описания товара: ", value=st.session_state["summary"], height=300)
            st.text_area(f"Описание товара: ", value=st.session_state["product_description"], height=300)
            
        else:
            st.warning("Идет обработка данных, подождите.")

        if st.session_state["results_ready_2t_task"] == True:
            try:
                json_data = json.dumps(
                    st.session_state["summary"], indent=4, ensure_ascii=False)
            except Exception as e:
                json_data = json.dumps(st.session_state["summary"], indent=4)
                logging.error(f"Ошибка: {str(e)}")
                st.error(f"Ошибка: {str(e)}")

            filename = st.text_input(
                "Введите имя файла:", value="results_task2.json")

            # Конвертация данных в JSON строку
            json_bytes = io.BytesIO(json_data.encode('utf-8'))

            st.download_button(
                label="Сохранить результаты задача 2",
                data=json_bytes,
                file_name=filename,
                mime='application/json'
            )
        else:
            st.warning("Идет обработка данных, подождите.")


async def main_task1():
    # Разделение приложения на разделы с помощью заголовков
    st.title("AI Product Hack (Кейс 4)")

    # Раздел для ввода данных пользователем
    with st.form(key="data_input"):
        # brand_name = st.text_input("Название бренда")
        # model_name = st.text_input("Название модели")
        # part_number = st.text_input("Парт-номер производителя (опционально)")
        # submit_button = st.form_submit_button("Запустить")

        brand_name = st.text_input("Название бренда", value="AQUARIUS")
        model_name = st.text_input(
            "Название модели", value="CMP NS483 (Исп.2)")
        part_number = st.text_input(
            "Парт-номер производителя (опционально)", value="NS4831524116Q151E90NT2NNNN2")
        submit_button = st.form_submit_button("Запустить")

        # # Для проверки
        # brand_name = "TCL"
        # model_name = "20 SE"
        # part_number = "T671H-2ALCRU12"

        product_info = ProductInfo(
            brand_name=brand_name,
            model_name=model_name,
            part_number=part_number)

        # product_info = ProductInfo(
        #     brand_name="ACER",
        #     model_name="CC715-91P-X7V8",
        #     part_number="NX.C5FER.001")

        # product_info = ProductInfo(
        #     brand_name="AQUARIUS",
        #     model_name="CMP NS483 (Исп.2)",
        #     part_number="NS4831524116Q151E90NT2NNNN2")

    # Раздел для отображения результатов
    with st.expander("Результаты"):
        if submit_button:
            try:
                # link = await search_and_rate(product_info)
                # link = asyncio.get_event_loop().run_until_complete(search_and_rate(product_info))
                loop = asyncio.get_event_loop()
                links = loop.run_until_complete(
                    async_search_and_rate(product_info))
                # print("begin get_source_links_single(link)")
                text_info = get_source_links_single(links[0])
                # text_info = get_source_links_single(link)
                # print("finish get_source_links_single(link)")
                print("text_info ", text_info)

                # info_model = generate_info_model(text_info)
                info_model = loop.run_until_complete(
                    get_product_characteristics_from_sources_single([text_info]))

                # st.json(info_model)

                st.session_state["info_model"] = info_model
                st.session_state["results_ready_1_task"] = True
                st.success(
                    "Результаты успешно обработаны. Нажмите на 'Показать результаты' для отображения.")
            except TimeoutError:
                logging.error("Превышено время ожидания Yandex GPT.")
                st.error("Превышено время ожидания Yandex GPT.")

            except Exception as e:
                logging.error(f"Ошибка: {str(e)}")
                st.error(f"Ошибка: {str(e)}")

        # Кнопка для отображения результатов
        if st.session_state["results_ready_1_task"] == True and st.button("Показать результаты"):
            st.json(st.session_state["info_model"])
        else:
            st.warning("Идет обработка данных, подождите.")

        # Кнопка сохранения
        if st.session_state["results_ready_1_task"] == True and st.button("Сохранить результаты"):
            try:
                json_data = json.dumps(
                    st.session_state["info_model"], indent=4, ensure_ascii=False)
            except Exception as e:
                json_data = json.dumps(
                    st.session_state["info_model"], indent=4)
                logging.error(f"Ошибка: {str(e)}")
                st.error(f"Ошибка: {str(e)}")

            filename = st.text_input(
                "Введите имя файла:", value="results_task1.json")

            with open(filename, "w") as f:
                f.write(json_data)

            st.success(f"Результаты успешно сохранены в файл '{filename}'.")
        else:
            st.warning("Идет обработка данных, подождите.")


def main_task2():
    st.title("AI Product Hack (Кейс 4)")
    product_input_interface()


def run_main_menu():
    primary_color = "#007bff"
    secondary_color = "#6c757d"

    # Создание списка названий страниц
    page_names = ["Task 1", "Task 2", "Info"]

    # Создание меню
    with st.sidebar:
        # Создание меню с помощью option_menu
        selected_page = option_menu(
            menu_title="Navigation",
            # menu_title=None,
            options=page_names,
            icons=["filter", "filter", "info"],
        )

    match selected_page:
        case "Task 1":
            # Enable nest_asyncio
            nest_asyncio.apply()
            asyncio.run(main_task1())
        case "Task 2":
            # st.write("Task 2")

            # nest_asyncio.apply()
            # asyncio.run(main_task2())

            main_task2()
        case "Info":
            pass
        # case _:


if __name__ == "__main__":

    from dotenv import load_dotenv
    load_dotenv("env/.env.yandex_search")
    load_dotenv("env/.env.api_key")

    # # Enable nest_asyncio
    # nest_asyncio.apply()

    # asyncio.run(main())

    run_main_menu()
