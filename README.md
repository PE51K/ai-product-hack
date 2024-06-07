# AI Product Hack (Кейс 4)


## Настройка окружения
```shell
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
Для использования YaGPT потребуется добавить также переменные окружения. Подробнее см. [документацию YandexGPT Python](https://yandexgpt-python.readthedocs.io/en/latest/)


## Задача 1 "Выделение характеристик товара"

Данная задача декомпозируется на 3 подзадачи:
1) Поиск и ранжирование релевантных источников информации
2) Парсинг текста с каждого выделенного источника
3) Обработка полученного текста и выделение характеристик товара

Готовые решения на английском:
- [oxylabs.io](https://oxylabs.io/features/adaptive-parser)
- [diffbot.com](https://www.diffbot.com/data/product)

Готовые решения на русском:
- [cs-cart.alexbranding.com](https://cs-cart.alexbranding.com/ru/parsing.html)
- [a-parser.com](https://a-parser.com/a-parser-for-e-commerce/)
- [froxy.com](https://froxy.com/ru/e-commerce-scraper)

### Подробнее о подзадаче 1

Полезные ссылки на источники:
- [Дока API поиска Яндекс](https://yandex.cloud/ru/docs/search-api/)
- [Дока YandexGPT Python](https://yandexgpt-python.readthedocs.io/en/latest/)

Этап 1: получения ссылок на ресурсы. Воможные пути решения (риски):
1) Запрос к API поискового движка (цена)
2) Поиск через таблицу основного ресурса и добавление к ссылке адреса на конкретный ресурс (ограниченный поиск, необходимость ручного заполнения таблицы)

Этап 2: Ранжирование. Воможные пути решения (риски):
1) Через таблицу (ограниченная база знаний)
2) Классификация через LLM (цена, может выдавать недостоверные результаты)
3) Через локальную ML модель (необходимость разметки, может иметь слабые обобщающие свойства)

Формат входных данных ([TypedDict usage](https://peps.python.org/pep-0589/)):
```python
from typing import TypedDict, Optional

class ProductInfo(TypedDict):
    brand_name: str
    model_name: str
    part_number: Optional[int]
```

Формат выходных данных:
```python
from typing import TypedDict

class SourceLink(TypedDict):
    link: str
    confidence_rate: float # от 0 до 1

def get_source_links(product_info: ProductInfo) -> list[SourceLink]:
    ...
    return [source_link_1, source_link_2, ...]
```

Выбранный нами путь решения:
- Поиск самых релевантных источников через Yandex search API
- Ранжирование по доверительности запросами к YandexGPT с заранее заданными критериями оценки от 0 до 1

Куда ещё можно посмотреть (пути развития решения в глубину):
- ?

### Подробнее о подзадаче 2

Полезные ссылки на источники:
- [Извлечение текста из PDF](https://habr.com/ru/companies/ruvds/articles/765246/)
- [Теггинг HTML](https://medium.indix.com/attribute-level-parser-to-extract-product-information-from-html-6ff4e48ae36d)

Этап 1: Парсинг. Воможные выходные данные:
1) Текст из HTML
2) Текст из PDF на сайте
3) Текст из картинок на сайте?
4) Текст из видео на сайте?

Формат входных данных ([TypedDict usage](https://peps.python.org/pep-0589/)):
```python
from typing import TypedDict

class SourceLink(TypedDict):
    link: str
    confidence_rate: float # от 0 до 1

curren_product_source_links: list[SourceLink] = get_source_links(...)
```

Формат выходных данных:
```python
from typing import TypedDict, Optional

class SourceLink(TypedDict):
    link: str
    confidence_rate: float # от 0 до 1

class TextInfoFromSource(TypedDict):
    html_text: str
    pdf_texts: Optional[list[str]] # Может быть несколько PDF на сайте (если реализуется)
    source: SourceLink

def get_product_texts_from_sources(product_source_links: list[SourceLink]) -> list[TextInfoFromSource]:
    ...
    return [text_info_from_source_1, text_info_from_source_2, ...]
```

Выбранный нами путь решения:
- Парсинг текста из HTML
- Обнаружение PDF на сайте, загрузка и парсинг текста из текстовых файлов

Куда ещё можно посмотреть (пути развития решения в глубину):
- Парсинг из PDF с картинками
- Парсинг из видео
- Парсинг из картинок
- Теггинг сайтов для улучшения парсинга HTML

### Подробнее о подзадаче 3

Полезные ссылки на источники:
- [Дока YandexGPT Python](https://yandexgpt-python.readthedocs.io/en/latest/)

Этап 1: извлечение конкретных характеристик из текста. Какие подходы можно применить (риски):
1) Языковая модель (цена, может выдавать недостоверные результаты)
- Разбить текст батчи
- Разделить инфомодели на батчи
- Предобработка данных?
- Постобработка выхода?
2) NER (вопрос разметки (у нас есть данные, но не в том формате, который нужен для NER), может иметь слабые обобшающие результаты)

Этап 2: Совместить результаты с разных источников. Воможные алгоритмы:
1) Максимум по рейтингу доверия
2) Максимум по сумме рейтингов доверий для групп с одинаковыми значениями

Формат входных данных для этапа 1 ([TypedDict usage](https://peps.python.org/pep-0589/)):
```python
from typing import TypedDict, Optional

class SourceLink(TypedDict):
    link: str
    confidence_rate: float # от 0 до 1

class TextInfoFromSource(TypedDict):
    html_text: str
    pdf_texts: Optional[list[str]] # Может быть несколько PDF на сайте (если реализуется)
    source: SourceLink

current_product_texts_from_sources: list[TextInfoFromSource] = get_product_texts_from_sources(...)
```

Формат выходных данных для этапа 1:
```python
from typing import TypedDict

class TextInfoFromSource(TypedDict):
    html_text: str
    pdf_texts: Optional[list[str]] # Может быть несколько PDF на сайте (если реализуется)
    source: SourceLink

class NotebookCharacteristics(TypedDict):
    diagonal_size: float
    ...
    source: SourceLink

def get_product_characteristics_from_sources(product_texts_from_sources: list[TextInfoFromSource]) -> list[NotebookCharacteristics]:
    ...
    return [notebook_characteristics_from_source_1, notebook_characteristics_from_source_2, ...]
```

Формат выходных данных для этапа 2:
```python
from typing import TypedDict, Union

class SourceLink(TypedDict):
    link: str
    confidence_rate: float # от 0 до 1

class FinalNotebookCharacteristics(TypedDict):
    diagonal_size: float
    ...

def get_final_product_characteristics(product_characteristics_from_sources: List[Union[NotebookCharacteristics, TVCharacteristics, ...]]) -> Union(FinalNotebookCharacteristics, FinalTVCharacteristics, ...):
```

Выбранный нами путь решения:
- YandexGPT для получения характеристик из текста
- ?

Куда ещё можно посмотреть (пути развития решения в глубину):
- Предобработка входных данных
- NER
- ChatGPT
- Локальная LLM
