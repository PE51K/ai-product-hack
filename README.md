## Описание

**AI Product Hack** - это проект, направленный на автоматическое выделение характеристик товара с использованием ИИ и различных источников данных.

## Оглавление

* [Введение](#введение)
* [Функциональные возможности](#функциональные-возможности)
* [Установка и настройка](#установка-и-настройка)
* [Использование](#использование)
* [Документация](#документация)
* [Вклад](#вклад)
* [Лицензия](#лицензия)
* [Контакты](#контакты)

## Введение

... (мотивация, проблема, решение)

## Функциональные возможности

* ... (перечислить ключевые функции)
* ... (описать примеры использования)

## Установка и настройка

### Требования

- Docker должен быть установлен на вашей машине. [Инструкция по установке Docker](https://docs.docker.com/get-docker/)

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

### Установка

1. Clone the repository:
    ```shell
    git clone https://github.com/
    ```
2. Navigate to the project directory:
    ```shell
    cd ai-product-hack
    ```
3. Install the dependencies:
    ```shell
    pip install -r requirements.txt
    ```
    или
    ```shell
    pip install -r requirements_streamlit-data-viz.txt
    ```

## Использование
Пожалуйста, введите данные для распознавания. В полях приведены данные для примера, но вы можете указать ваши собственные. Результатом обработки будет JSON-файл, который можно будет скачать.

### Запуск приложения

```shell
streamlit run src/main.py


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

#  "Название проекта ...."

## Описание

**Название проекта** - это ..., которое ... (описание функциональности).

## Оглавление

* [Введение](#введение)
* [Функциональные возможности](#функциональные-возможности)
* [Установка и настройка](#установка-и-настройка)
* [Использование](#использование)
* [Документация](#документация)
* [Вклад](#вклад)
* [Лицензия](#лицензия)
* [Контакты](#контакты)

## Введение

... (мотивация, проблема, решение)

## Функциональные возможности

* ... (перечислить ключевые функции)
* ... (описать примеры использования)

### Установка

## Требования

- Docker должен быть установлен на вашей машине. [Инструкция по установке Docker](https://docs.docker.com/get-docker/)

#### Построение Docker образа

1. Откройте терминал и перейдите в директорию проекта `ai-product-hack`:
    ```
    cd path/to/ai-product-hack
    ```

2. Постройте Docker образ, используя команду:
    ```
    docker build -t my-streamlit-app .
    ```

## Запуск Docker контейнера

1. Запустите контейнер, используя команду:
    ```
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

1. ... (команды для установки)
2. ... (инструкции)

## Использование

### Запуск приложения

... (описание запуска)

### Интерфейс пользователя

... (краткий обзор интерфейса)

### Пример использования

... (пошаговый пример)

## Структура

**Модули:**

* ``: Содержит функции для обработки данных, таких как загрузка, очистка и предобработка.
* ``: Содержит функции для создания элементов интерфейса Streamlit.
* ``: Содержит функции для реализации логики работы приложения, включая алгоритмы и модели машинного обучения.
* `utils`: Содержит вспомогательные функции и конфигурации.

**Классы:**

* ``: Представляет объект для обработки данных.
* ``: Представляет объект для создания интерфейса Streamlit.
* ` `: Координирует работу модулей и компонентов приложения.

**Архитектура:**

**Документация API:**

[Ссылка на документацию API](https://...)


## Предварительная структура
```
ai_product_hack_app/
├── .gitignore
├── README.md
├── requirements.txt
├── setup.py
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── pages/
│   │   ├── __init__.py
│   │   ├── page1.py
│   │   └── page2.py
│   ├── components/
│   │   ├── __init__.py
│   │   └── custom_component.py
│   ├── types_definition/    
│   │   ├── __init__.py           
│   │   ├── product_info.py                                 
│   │   └── source_link.py 
│   ├── utils/
│   │   ├── __init__.py
│   │   └── helper_functions.py
└── tests/
    ├── __init__.py
    └── test_app.py
```

<details><summary><b> How to install and run the application</b></summary>

1. Clone the repository:
    ```
    git clone https://github.com/
    ```
2. Navigate to the project directory:
    ```
    cd ai-product-hack
    ```
3. Install the dependencies:
    ```
    pip install -r requirements.txt
    ```
    or
    ```
    pip install -r requirements_streamlit-data-viz.txt
    ```
## Usage

Run the application:
```
streamlit run src/main.py
```