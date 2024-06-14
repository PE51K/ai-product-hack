## Описание

Данный репозиторий содержит прототип сервиса для распознавания товарных инфомоделей и генерации описаний и саммари на их основе. 

Прототип был разработан в рамках хакатона **AI Product Hack** командой **ЭЯЙ**.

## Оглавление

* [Проблема](#Проблема)
* [Задачи кейса](#Задачи-кейса)
* [Функциональные возможности](#Функциональные-возможности-прототипа)
* [Установка и настройка](#установка-и-настройка)
* [Использование](#использование)
* [Аналитика по задачам](#аналитика-по-задачам)

## Проблема

Ситилинк стремиться предоставить максимальную информацию по товару (контент) для своих покупателей. 

Карточка товара должна содержать в себе полную информацию о товаре включая технические характеристики и маркетинговое описание товара.

Ручное заполнение долгое. Генеративные технологии могут быстро, качественно заполнять карточки товара.

## Задачи кейса

**Заполнение инфомодели**: 
Необходимо по образцу инфомодели и названию товара составить заполненную инфомодель со всей возможной информацией.

**Генерация описания**:
Необходимо по инфомодели составить грамотное продающее описание, привлекающее траффик.

## Функциональные возможности прототипа

- Поиск и ранжирование источников информации
- Парсинг HTML страниц и PDF внутри страниц
- Извлечение структурированной информации в виде инфомодели
- Выгрузка инфомодели в формате JSON
- Генерация описания
- Генерация саммари

## Установка и настройка

### Требования

- Docker должен быть установлен на вашей машине. [Инструкция по установке Docker](https://docs.docker.com/get-docker/)
- Git также должен быть установлен. [Инструкция по установке Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
- Вы должны получить API ключ и номер каталога в Yandex Cloud для использования YandexGPT API.
[Инструкция по получению API ключа](https://yandex.cloud/ru/docs/foundation-models/quickstart/yandexgpt#api_1)
- Также необходимо получить API ключ и номер каталога в Yandex Cloud для Yandex Search API. 
[Инструкция по началу работы](https://yandex.cloud/ru/docs/search-api/quickstart);
[Инструкция по получению API ключа](https://yandex.cloud/ru/docs/search-api/operations/auth)

#### Настройка окружения
1. Скопируйте репозиторий:
```shell
git clone https://github.com/PE51K/ai-product-hack
```

2. Настройте переменные окружения:

В файле [env/env.api_key](env/env.api_key) вам нужно указать:
- YANDEX_GPT_MODEL_TYPE - тип модели: yandexgpt
- YANDEX_GPT_CATALOG_ID - ID каталога в Yandex Cloud
- YANDEX_GPT_API_KEY - API ключ

В файле [env/env.yandex_search](env/.env.yandex_search) вам нужно указать:
- YANDEX_SEARCH_BASE_LINK - адрес API Yandex Search
- YANDEX_SEARCH_FOLDER_ID - ID каталога в Yandex Cloud
- YANDEX_SEARCH_API_KEY - API ключ


#### Построение Docker образа

1. Откройте терминал и перейдите в директорию проекта `ai-product-hack`:
    ```shell
    cd path/to/ai-product-hack
    ```

2. Постройте Docker образ, используя команду:
    ```shell
    docker build -t my-streamlit-app .
    ```

### Запуск Docker контейнера

1. Запустите контейнер, используя команду:
    ```shell
    docker run -p 8501:8501 my-streamlit-app
    ```

Теперь ваше Streamlit приложение доступно по адресу `http://localhost:8501`.

## Основные команды в Dockerfile

- `FROM python:3.12.2`: Использует официальный образ Python 3.12.2 как базовый.
- `WORKDIR /app`: Устанавливает рабочую директорию внутри контейнера.
- `COPY requirements.txt .`: Копирует файл `requirements.txt` в контейнер.
- `RUN pip install --no-cache-dir -r requirements.txt`: Устанавливает зависимости.
- `COPY . .`: Копирует все файлы проекта в контейнер.
- `EXPOSE 8501`: Открывает порт 8501 для доступа к приложению.
- `CMD ["streamlit", "run", "src/main.py"]`: Запускает Streamlit приложение.

### Локальное использование

1. Клонируйте репозиторий:
    ```shell
    git clone https://github.com/PE51K/ai-product-hack
    ```
2. Перейдите в директорию проекта:
    ```shell
    cd path/to/ai-product-hack
    ```
3. Установите зависимости:
    ```shell
    pip install -r requirements.txt
    ```

## Использование
Протоип доступен по адресу `http://158.160.168.3:8501`.

Вся необходимая пользовательская информация доступна в интерфейсе прототипа Streamlit. 

Тестовые данные для проверки работы Streamlit приложения находятся в директории [test_data](test_data).

<br>

## Аналитика по задачам

## Задача 1 "Выделение характеристик товара"

Данная задача декомпозируется на 3 подзадачи:
1) Поиск и ранжирование релевантных источников информации
2) Парсинг текста с каждого выделенного источника
3) Обработка полученного текста и выделение характеристик товара

### Подробнее о подзадаче 1

Этап 1: получения ссылок на ресурсы. Воможные пути решения:
1) Запрос к API поискового движка
2) Поиск через таблицу основного ресурса и добавление к ссылке адреса на конкретный ресурс 

Этап 2: Ранжирование
1) Через таблицу
2) Классификация через LLM

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


### Подробнее о подзадаче 2

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


### Подробнее о подзадаче 3

Этап 1: извлечение конкретных характеристик из текста. Какие подходы можно применить:
1) Языковая модель
- Разбить текст батчи
- Разделить инфомодели на батчи
- Предобработка данных?
- Постобработка выхода?
2) NER

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

## Задача 2 "Построение описания и саммари"

Воможные пути решения:
1) Использования API GPT
2) Локальная LLM (если важна конфиденциальность)

Формат входных данных:
```python
from typing import TypedDict, Union

class SourceLink(TypedDict):
    link: str
    confidence_rate: float # от 0 до 1

class FinalNotebookCharacteristics(TypedDict):
    diagonal_size: float
    ...

class ProductInfo(TypedDict):
    brand_name: str
    model_name: str
    part_number: Optional[int]

input: (List[SourceLink], FinalNotebookCharacteristics, ProductInfo) = ...
```
