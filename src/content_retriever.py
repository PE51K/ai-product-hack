from typing import TypedDict, Optional, List
import requests
from bs4 import BeautifulSoup
import os
import PyPDF2
from PyPDF2 import errors
import re
import csv
from urllib3.exceptions import SSLError  # Импортируем SSLError
from pathlib import Path
from functools import lru_cache
import json

class SourceLink(TypedDict):
    link: str
    confidence_rate: float

class TextInfoFromSource(TypedDict):
    html_text: str
    pdf_texts: Optional[List[str]]
    source: SourceLink

def download_file(url: str, dest_folder: str, timeout: int = 10) -> str:
    """Downloads a file from URL to the given folder."""

    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)

    filename = url.split("/")[-1]  # Извлечь имя файла из URL-адреса
    file_path = os.path.join(dest_folder, url.split('/')[-1])

    # Проверить, существует ли файл в папке назначения
    if os.path.exists(file_path):
        print(f"Файл '{filename}' уже существует, пропускаем загрузку.")
        return file_path

    try:
        # response = requests.get(url, timeout=timeout, verify=False)
        response = requests.get(url, stream=True, timeout=timeout, verify=False)
        response.raise_for_status()  # Raise an exception for unsuccessful download
    except requests.exceptions.RequestException as e:
        if isinstance(e, SSLError):  # Проверка на ошибку сертификата
            print(f"Error downloading file: {e} (SSL certificate issue)")
        else:
            print(f"Error downloading file: {e}")
        return None

    # Проверка на пустой ответ
    if not response.content:
        print(f"Error downloading file: Empty response (URL: {url})")
        return None
    
    filename = os.path.join(dest_folder, url.split('/')[-1])

    try:
        with open(filename, 'wb') as file:
            file.write(response.content)
    except OSError as e:
        # Обработка ошибки
        print(f"Ошибка загрузки файла: {e}")
        return None
    
    return filename

@lru_cache()
def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extracts text content from a PDF file at the given path.
    Args:
        pdf_path (str): Путь к PDF-файлу.

    Returns:
        str: Извлеченный текст из PDF-файла.
    """
    if pdf_path is None:
        print("Не указан путь к PDF-файлу")
        return None

    if not os.path.exists(pdf_path):
        print(f"Файл PDF не найден: {pdf_path}")
        return None

    if not pdf_path.endswith(".pdf"):
        print(f"Неверный формат файла: {pdf_path}")
        return None

    text = ""
    with open(pdf_path, 'rb') as file:
        try:
            reader = PyPDF2.PdfReader(file)
        except PyPDF2.errors.PdfReadError:
            # raise ValueError(f"Не удалось открыть PDF-файл: {pdf_path}")
            print(f"Не удалось открыть PDF-файл: {pdf_path}")
            return None

        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text += page.extract_text() + "\n"

    if not text:
        print(f"Из PDF-файла не удалось извлечь текст: {pdf_path}")
        return None

    # Проверка, что текст не содержит только пробелы
    if re.search(r"[^\s]", text):
        # Вывод текста и его длины
        # print(f"Извлеченный текст:\n{text}")
        print(f"Длина текста: {len(text)} символов")
    else:
        print(f"В извлеченном тексте нет символов, кроме пробелов: {pdf_path}")
        return None

    return text

def get_source_links(product_source_links: List[SourceLink]) -> List[TextInfoFromSource]:
    """
    Fetches and parses text content from a list of product source links, including
    both HTML text and text extracted from any downloadable PDF files found on the pages.

    Args:
      product_source_links (List[SourceLink]): A list of dictionaries containing
          information about product source links, including the 'link' key with the URL.

    Returns:
      List[TextInfoFromSource]: A list of TextInfoFromSource objects containing
          extracted text information from each source link. Each object contains:
              - html_text (str): The extracted text content from the HTML page.
              - pdf_texts (List[str], optional): A list of text content extracted
                  from downloaded PDF files found on the page (None if no PDFs found).
              - source (SourceLink): The original source link information.
    """
    results = []

    total_links = len(product_source_links)
    processed_links = 0
    
    for source_link in product_source_links:
        processed_links += 1
        print(f"Обработано: {processed_links}/{total_links}", end="\r")
        # Extract the link from the current source
        link = source_link['link']
        print(link)

        try:
            if link.lower().endswith('.pdf'):
                # Handle link as a PDF directly
                pdf_url = link
                pdf_path = download_file(pdf_url, 'downloads', 60)
                pdf_text = extract_text_from_pdf(pdf_path)
                text_info = TextInfoFromSource(
                  html_text=None,  # No HTML content for a direct PDF link
                  pdf_texts=[pdf_text],
                  source=source_link
                )

            else:
                # Make an HTTP request to the specified link
                response = requests.get(link)
                # Create a BeautifulSoup object to parse the HTML content of the page
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract all text from the HTML, using newline as separator and stripping extra spaces
                html_text = soup.get_text(separator="\n", strip=True)
                
                # Find and download PDFs
                pdf_texts = [] # to store texts from PDF files
                for a_tag in soup.find_all('a', href=True):
                    # Extract the href value from the <a> tag
                    href = a_tag['href']
                    # Check if the link ends with .pdf (i.e., it's a PDF file)
                    if href.lower().endswith('.pdf'):
                        # Form the complete URL for the PDF file
                        pdf_url = href if href.startswith('http') else link + href
                        # Download the PDF file and save it to the specified directory
                        pdf_path = download_file(pdf_url, 'downloads', 60)
                        # Extract text from the downloaded PDF file
                        pdf_text = extract_text_from_pdf(pdf_path)
                        pdf_texts.append(pdf_text)
                
                # Create a dictionary with information about the HTML and PDF texts
                text_info = TextInfoFromSource(
                    html_text=html_text,
                    pdf_texts=pdf_texts if pdf_texts else None,
                    source=source_link
                )
        except requests.exceptions.RequestException as e:
            print(f"Error downloading content from {link}: {e}")
            # Создать пустой объект TextInfoFromSource с сообщением об ошибке
            text_info = TextInfoFromSource(
                html_text=f"Error downloading content: {e}",
                pdf_texts=None,
                source=source_link
            )

        results.append(text_info)
    
    return results

def get_source_links_single(source_link: SourceLink) -> TextInfoFromSource:

    # Extract the link from the current source
    link = source_link['link']
    print(link)

    try:
        if link.lower().endswith('.pdf'):
            # Handle link as a PDF directly
            pdf_url = link
            pdf_path = download_file(pdf_url, 'downloads', 60)
            pdf_text = extract_text_from_pdf(pdf_path)
            text_info = TextInfoFromSource(
              html_text=None,  # No HTML content for a direct PDF link
              pdf_texts=[pdf_text],
              source=source_link
            )

        else:
            # Make an HTTP request to the specified link
            response = requests.get(link)
            # Create a BeautifulSoup object to parse the HTML content of the page
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract all text from the HTML, using newline as separator and stripping extra spaces
            html_text = soup.get_text(separator="\n", strip=True)
            
            # Find and download PDFs
            pdf_texts = [] # to store texts from PDF files
            for a_tag in soup.find_all('a', href=True):
                # Extract the href value from the <a> tag
                href = a_tag['href']
                # Check if the link ends with .pdf (i.e., it's a PDF file)
                if href.lower().endswith('.pdf'):
                    # Form the complete URL for the PDF file
                    pdf_url = href if href.startswith('http') else link + href
                    # Download the PDF file and save it to the specified directory
                    pdf_path = download_file(pdf_url, 'downloads', 60)
                    # Extract text from the downloaded PDF file
                    pdf_text = extract_text_from_pdf(pdf_path)
                    pdf_texts.append(pdf_text)
            
            # Create a dictionary with information about the HTML and PDF texts
            text_info = TextInfoFromSource(
                html_text=html_text,
                pdf_texts=pdf_texts if pdf_texts else None,
                source=source_link
            )
    except requests.exceptions.RequestException as e:
        print(f"Error downloading content from {link}: {e}")
        # Создать пустой объект TextInfoFromSource с сообщением об ошибке
        text_info = TextInfoFromSource(
            html_text=f"Error downloading content: {e}",
            pdf_texts=None,
            source=source_link
        )

    
    return text_info


def save_to_csv(texts, filename="extracted_texts.csv"):
    """
    Saves the list of TextInfoFromSource objects (`texts`) to a CSV file.

    Args:
      texts (List[TextInfoFromSource]): The list of text information objects to save.
      filename (str, optional): The name of the CSV file to create. Defaults to "extracted_texts.csv".
    """

    # Check if the file exists
    if os.path.exists(filename):
        # Delete the existing file to overwrite it
        os.remove(filename)

    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['link', 'confidence_rate', 'html_text', 'pdf_texts']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=";")

        # Write the header row
        writer.writeheader()

        for text_info in texts:
            # Обработка возможного отсутствия ключа 'pdf_texts'
            pdf_texts = text_info.get('pdf_texts', [])  # Пустой список по умолчанию
            if pdf_texts is None:
                pdf_texts = []  # Обеспечить наличие списка, даже если 'pdf_texts' отсутствует

            # # Объединение элементов 'pdf_texts' в строку с разделителем '\n'
            # pdf_texts_joined = ",".join(pdf_texts)

            default_text = "Текст не извлечен"
            pdf_texts_joined = ",".join([text or default_text for text in pdf_texts])

            # Create a dictionary with the data to write
            data = {
              'link': text_info['source']['link'],
              'confidence_rate': text_info['source']['confidence_rate'],
              'html_text': text_info['html_text'],
              'pdf_texts': pdf_texts_joined
            }

            # Write the data row
            writer.writerow(data)


def read_links_from_csv(file_path: str, max_rows: int = None) -> List[SourceLink]:
    """
    Reads links from a CSV file and returns them as a list of SourceLink objects.

    Args:
      file_path (str): The path to the CSV file.
      max_rows (int, optional): The maximum number of rows to read. Defaults to None (read all rows).

    Returns:
      List[SourceLink]: A list of SourceLink objects.
    """
    links = []
    with open(file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        for i, row in enumerate(reader):
            if max_rows is not None and i >= max_rows:
                break
            link = row['Ссылка на сайт поставщика/вендора']
            confidence_rate = 1.0  # Default confidence rate
            links.append(SourceLink(link=link, confidence_rate=confidence_rate))
    return links

def save_to_json(texts, filename="extracted_texts.json"):
    """
    Saves the list of TextInfoFromSource objects (`texts`) to a JSON file.

    Args:
    texts (List[TextInfoFromSource]): The list of text information objects to save.
    filename (str, optional): The name of the JSON file to create. Defaults to "extracted_texts.json".
    """

    # Обработать случай пустого списка texts (во избежание ошибки сериализации JSON)
    if not texts:
      texts = []

    # Преобразовать список TextInfoFromSource в список словарей
    json_data = [text_info.__dict__ for text_info in texts]

    # Сохранить данные в JSON файл
    with open(filename, 'w', encoding='utf-8') as outfile:
        json.dump(json_data, outfile, indent=4)  # Параметр indent для форматирования

    print(f"Данные успешно сохранены в файл: {filename}")


if __name__ == "__main__":
    # print("test")


    input_csv_path = "Links_cleaned.csv"
    # product_source_links = read_links_from_csv(input_csv_path)
    product_source_links = read_links_from_csv(input_csv_path, max_rows=2)


    # texts = get_source_links(product_source_links)
    # save_to_csv(texts)
    # print("Finished processing and saving extracted texts to CSV.")


    import concurrent.futures

    # Use ThreadPoolExecutor for multithreaded processing
    with concurrent.futures.ThreadPoolExecutor(max_workers=1000) as executor:
        results = executor.map(get_source_links_single, product_source_links)

    # Process the results
    text_info_from_sources = []
    for result in results:
        if result is not None:
            text_info_from_sources.append(result)
    
    save_to_csv(text_info_from_sources)
    print("Finished processing and saving extracted texts to CSV.")
