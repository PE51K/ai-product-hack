import streamlit as st
from streamlit_option_menu import option_menu
import json
import asyncio
import logging
import nest_asyncio

from types_definition.product_info import ProductInfo
from types_definition.source_links import SearchResult, SourceLink, TextInfoFromSource
from sources_search.search_and_rate import search_and_rate
from utils.content_retriever import get_source_links_single
from utils.extract_characteristics import get_product_characteristics_from_sources_single

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


async def async_search_and_rate(product_info):
    return await search_and_rate(product_info)


async def main_task1():
    # Разделение приложения на разделы с помощью заголовков
    st.title("AI Product Hack (Кейс 4)")

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

        # product_info = ProductInfo(
        #     brand_name="ACER",
        #     model_name="CC715-91P-X7V8",
        #     part_number="NX.C5FER.001")

        product_info = ProductInfo(
            brand_name="AQUARIUS",
            model_name="CMP NS483 (Исп.2)",
            part_number="NS4831524116Q151E90NT2NNNN2")

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

                # info_model = generate_info_model(text_info)
                info_model = loop.run_until_complete(get_product_characteristics_from_sources_single([text_info]))

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

async def main_task2():
    # Разделение приложения на разделы с помощью заголовков
    st.title("AI Product Hack (Кейс 4)")


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

    # if selected_page == "":
    #     st.write("")
    # elif selected_page == "":
    #     st.write("")
    # else:
    #     st.write("")

    # Стилизация CSS
    menu_style = """
    <style>
        .option_menu {
            background-color: {secondary_color};
            text-align: center;
            padding: 10px 0;
        }

        .option_menu .option_menu-item {
            display: inline-block;
            padding: 10px 15px;
            border-radius: 5px;
            margin: 0 10px;
        }

        .option_menu .option_menu-item a {
            color: white;
            text-decoration: none;
        }

        .option_menu .option_menu-item.is-selected {
            background-color: {primary_color};
        }
    </style>
    """
    st.write(menu_style, unsafe_allow_html=True)


    match selected_page:
        case "Task 1":
            # Enable nest_asyncio
            nest_asyncio.apply()
            asyncio.run(main_task1())
        case "Task 2":
            # st.write("Task 2")
            nest_asyncio.apply()
            asyncio.run(main_task2())
        case "Info":
            pass
        # case _:


if __name__ == "__main__":
    # main()

    from dotenv import load_dotenv
    load_dotenv("env/.env.yandex_search")
    load_dotenv("env/.env.api_key")

    # # Enable nest_asyncio
    # nest_asyncio.apply()

    # asyncio.run(main())

    run_main_menu()
