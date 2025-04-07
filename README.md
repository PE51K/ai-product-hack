**Description**

This repository contains a prototype service for recognizing product “infomodels” and generating descriptions and summaries based on them.

The prototype was developed during the **AI Product Hack** hackathon by the **ЭЯЙ** team.

## Table of Contents

- [Problem](#problem)
- [Hackathon Tasks](#hackathon-tasks)
- [Prototype Features](#prototype-features)
- [Installation and Setup](#installation-and-setup)
- [Usage](#usage)
- [Task Analytics](#task-analytics)

## Problem

Сitilink aims to provide its customers with as much product information (content) as possible.

A product page must contain complete information about the item, including technical specifications and a marketing description.

Manual completion takes a long time. Generative technologies can quickly and efficiently fill in product pages.

## Hackathon Tasks

**Filling the infomodel**:  
Based on a sample infomodel and product name, you need to create a filled infomodel with all possible information.

**Generating a description**:  
Based on the infomodel, compose a compelling, traffic-driving product description.

## Prototype Features

- Searching and ranking information sources
- Parsing HTML pages and PDF files found within them
- Extracting structured data in the form of an infomodel
- Exporting the infomodel to JSON
- Generating a description
- Generating a summary

## Installation and Setup

### Requirements

- Docker installed on your machine. [Docker installation guide](https://docs.docker.com/get-docker/)  
- Git installed. [Git installation guide](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)  
- You must obtain an API key and a catalog number in Yandex Cloud to use the YandexGPT API.  
  [Instructions for obtaining an API key](https://yandex.cloud/ru/docs/foundation-models/quickstart/yandexgpt#api_1)  
- You also need an API key and a catalog number in Yandex Cloud for the Yandex Search API.  
  [Getting started guide](https://yandex.cloud/ru/docs/search-api/quickstart);  
  [Instructions for obtaining an API key](https://yandex.cloud/ru/docs/search-api/operations/auth)

#### Environment Configuration
1. Clone the repository:
   ```shell
   git clone https://github.com/PE51K/ai-product-hack
   ```

2. Configure environment variables:

   In the file [env/env.api_key](env/env.api_key), you need to specify:
   - YANDEX_GPT_MODEL_TYPE – the model type: yandexgpt
   - YANDEX_GPT_CATALOG_ID – Yandex Cloud catalog ID
   - YANDEX_GPT_API_KEY – API key

   In the file [env/env.yandex_search](env/.env.yandex_search), you need to specify:
   - YANDEX_SEARCH_BASE_LINK – Yandex Search API address
   - YANDEX_SEARCH_FOLDER_ID – Yandex Cloud catalog ID
   - YANDEX_SEARCH_API_KEY – API key

#### Building the Docker Image

1. Open a terminal and go to the `ai-product-hack` project directory:
   ```shell
   cd path/to/ai-product-hack
   ```

2. Build the Docker image using the following command:
   ```shell
   docker build -t my-streamlit-app .
   ```

### Running the Docker Container

1. Run the container using this command:
   ```shell
   docker run -p 8501:8501 my-streamlit-app
   ```

Your Streamlit application is now available at `http://localhost:8501`.

## Key Dockerfile Commands

- `FROM python:3.12.2`: Uses the official Python 3.12.2 image as the base.
- `WORKDIR /app`: Sets the working directory inside the container.
- `COPY requirements.txt .`: Copies `requirements.txt` into the container.
- `RUN pip install --no-cache-dir -r requirements.txt`: Installs dependencies.
- `COPY . .`: Copies all project files into the container.
- `EXPOSE 8501`: Opens port 8501 for access to the application.
- `CMD ["streamlit", "run", "src/main.py"]`: Launches the Streamlit application.

### Local Usage

1. Clone the repository:
   ```shell
   git clone https://github.com/PE51K/ai-product-hack
   ```
2. Navigate to the project directory:
   ```shell
   cd path/to/ai-product-hack
   ```
3. Install dependencies:
   ```shell
   pip install -r requirements.txt
   ```

## Usage
The prototype is available at `http://158.160.168.3:8501`.

All necessary user information is available in the Streamlit prototype interface.

Test data to check the Streamlit application is located in the [test_data](test_data) directory.

<br>

## Task Analytics

### Task 1: “Extracting Product Specifications”

This task is divided into three subtasks:
1. Searching and ranking relevant information sources
2. Parsing text from each identified source
3. Processing the extracted text and identifying product specifications

#### More About Subtask 1

Stage 1: Acquiring resource links. Possible approaches:
1) Querying a search engine API  
2) Searching through the main resource table and appending a specific resource URL

Stage 2: Ranking
1) Via a table
2) Classification via LLM

Input data format ([TypedDict usage](https://peps.python.org/pep-0589/)):
```python
from typing import TypedDict, Optional

class ProductInfo(TypedDict):
    brand_name: str
    model_name: str
    part_number: Optional[int]
```

Output data format:
```python
from typing import TypedDict

class SourceLink(TypedDict):
    link: str
    confidence_rate: float  # from 0 to 1

def get_source_links(product_info: ProductInfo) -> list[SourceLink]:
    ...
    return [source_link_1, source_link_2, ...]
```

#### More About Subtask 2

Stage 1: Parsing. Possible outputs:
1) Text from HTML
2) Text from PDF found on the site
3) Text from images on the site?
4) Text from videos on the site?

Input data format ([TypedDict usage](https://peps.python.org/pep-0589/)):
```python
from typing import TypedDict

class SourceLink(TypedDict):
    link: str
    confidence_rate: float  # from 0 to 1

current_product_source_links: list[SourceLink] = get_source_links(...)
```

Output data format:
```python
from typing import TypedDict, Optional

class SourceLink(TypedDict):
    link: str
    confidence_rate: float  # from 0 to 1

class TextInfoFromSource(TypedDict):
    html_text: str
    pdf_texts: Optional[list[str]]  # There may be multiple PDFs on the site (if implemented)
    source: SourceLink

def get_product_texts_from_sources(product_source_links: list[SourceLink]) -> list[TextInfoFromSource]:
    ...
    return [text_info_from_source_1, text_info_from_source_2, ...]
```

#### More About Subtask 3

Stage 1: Extract specific characteristics from the text. Possible approaches:
1) Language model
   - Split the text into batches
   - Split the infomodel into batches
   - Data preprocessing?
   - Postprocessing the output?
2) NER

Stage 2: Combine results from different sources. Possible algorithms:
1) Maximum by confidence rating
2) Maximum by the sum of confidence ratings for groups with identical values

Input data format for Stage 1 ([TypedDict usage](https://peps.python.org/pep-0589/)):
```python
from typing import TypedDict, Optional

class SourceLink(TypedDict):
    link: str
    confidence_rate: float  # from 0 to 1

class TextInfoFromSource(TypedDict):
    html_text: str
    pdf_texts: Optional[list[str]]  # There may be multiple PDFs on the site (if implemented)
    source: SourceLink

current_product_texts_from_sources: list[TextInfoFromSource] = get_product_texts_from_sources(...)
```

Output data format for Stage 1:
```python
from typing import TypedDict

class TextInfoFromSource(TypedDict):
    html_text: str
    pdf_texts: Optional[list[str]]  # There may be multiple PDFs on the site (if implemented)
    source: SourceLink

class NotebookCharacteristics(TypedDict):
    diagonal_size: float
    ...
    source: SourceLink

def get_product_characteristics_from_sources(product_texts_from_sources: list[TextInfoFromSource]) -> list[NotebookCharacteristics]:
    ...
    return [notebook_characteristics_from_source_1, notebook_characteristics_from_source_2, ...]
```

Output data format for Stage 2:
```python
from typing import TypedDict, Union

class SourceLink(TypedDict):
    link: str
    confidence_rate: float  # from 0 to 1

class FinalNotebookCharacteristics(TypedDict):
    diagonal_size: float
    ...

def get_final_product_characteristics(product_characteristics_from_sources: List[Union[NotebookCharacteristics, TVCharacteristics, ...]]) -> Union(FinalNotebookCharacteristics, FinalTVCharacteristics, ...):
```

### Task 2: “Composing the Description and Summary”

Possible approaches:
1) Using GPT API
2) A local LLM (if confidentiality is a priority)

Input data format:
```python
from typing import TypedDict, Union

class SourceLink(TypedDict):
    link: str
    confidence_rate: float  # from 0 to 1

class FinalNotebookCharacteristics(TypedDict):
    diagonal_size: float
    ...

class ProductInfo(TypedDict):
    brand_name: str
    model_name: str
    part_number: Optional[int]

input: (List[SourceLink], FinalNotebookCharacteristics, ProductInfo) = ...
```
