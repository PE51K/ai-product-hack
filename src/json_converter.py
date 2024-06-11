from typing import TypedDict, Optional
import json
import csv

class SourceLink(TypedDict):
    link: str
    confidence_rate: float # от 0 до 1

class TextInfoFromSource(TypedDict):
    html_text: str
    pdf_texts: Optional[list[str]] # Может быть несколько PDF на сайте (если реализуется)
    source: SourceLink

# Для наглядности
# JSON-файл содержит информацию, соответствующую структурам SourceLink и TextInfoFromSource
# [
#     {
#         "html_text": "dasdasdasdasdasd",
#         "pdf_texts": null,
#         "source": {
#             "link": "https://www.acer.com/ac/ru/RU/content/conceptd-model/NX.C5FER.001",
#             "confidence_rate": 1.0
#         }
#     },
#     {
#         "html_text": "dweewfwer",
#         "pdf_texts": null,
#         "source": {
#             "link": "https://digma.ru/catalog/item/3313",
#             "confidence_rate": 1.0
#         }
#     }
# ]

# def create_json_file(source_links: List[Dict]) -> None:
#   """
#   Создает JSON-файл с информацией о веб-страницах.

#   Args:
#     source_links: Список словарей, каждый из которых содержит информацию о веб-странице.
#       - link: URL-адрес веб-страницы.
#       - confidence_rate: Уровень уверенности в извлеченном тексте (от 0.0 до 1.0).

#   Returns:
#     None
#   """

#   # Создаем список объектов TextInfoFromSource
#   text_info_from_sources = []
#   for source_link in source_links:
#     link = source_link["link"]
#     confidence_rate = source_link["confidence_rate"]
#     html_text = "Примерный текст из HTML..."  # Замените на ваш код извлечения текста
#     pdf_texts = None  # Добавьте код извлечения текста из PDF, если необходимо

#     text_info_from_source = {
#       "html_text": html_text,
#       "pdf_texts": pdf_texts,
#       "source": {
#         "link": link,
#         "confidence_rate": confidence_rate
#       }
#     }
#     text_info_from_sources.append(text_info_from_source)

#   # Сохраняем данные в JSON-файл
#   with open("extracted_texts.json", "w", encoding="utf-8") as outfile:
#     import json
#     json.dump(text_info_from_sources, outfile, indent=4)

# # Пример использования
# source_links = [
#   {"link": "https://example.com/article1", "confidence_rate": 0.8},
#   {"link": "https://example.com/article2", "confidence_rate": 0.7},
# ]

# create_json_file(source_links)


with open('extracted_texts.json', 'r', encoding='utf-8') as f:
    json_data = json.load(f)


with open('Links_cleaned.csv', 'r', encoding='utf-8') as f:
    csv_reader = csv.DictReader(f)
    csv_data = list(csv_reader)

new_json_data = {}

# Сопоставить "Ссылка на сайт поставщика/вендора" из CSV с "link" из JSON
for row in csv_data:
    vendor_link = row['Ссылка на сайт поставщика/вендора']
    for item in json_data:
        json_link = item['source']['link']
        if vendor_link == json_link:
            new_json_data[row['Код Товара']] = item
            break

with open('new_data.json', 'w', encoding='utf-8') as f:
    json.dump(new_json_data, f, indent=4)


# Новый JSON-файл будет иметь следующую структуру:
# {
#   "Код Товара_1": {
#     "html_text": "текст из HTML страницы 1",
#     "pdf_texts": null, # или массив с текстами из PDF, если они есть
#     "source": {
#       "link": "https://example.com/article1", # ссылка на страницу 1
#       "confidence_rate": 0.8 # уровень уверенности для страницы 1
#     }
#   },
#   "Код Товара_2": {
#     "html_text": "текст из HTML страницы 2",
#     "pdf_texts": null, # или массив с текстами из PDF, если они есть
#     "source": {
#       "link": "https://example.com/article2", # ссылка на страницу 2
#       "confidence_rate": 0.7 # уровень уверенности для страницы 2
#     }
#   },
#   ...
# }