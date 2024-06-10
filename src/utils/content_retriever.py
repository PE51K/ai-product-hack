from typing import TypedDict, Optional, List
import requests
from bs4 import BeautifulSoup
import os
import sys
import PyPDF2
from PyPDF2 import errors
import re
import csv
from urllib3.exceptions import SSLError  # Импортируем SSLError
from pathlib import Path
from functools import lru_cache
import json
from urllib.parse import urljoin

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'types_definition'))
sys.path.append(parent_dir)

from product_info import ProductInfo
from source_links import SearchResult, SourceLink, TextInfoFromSource



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
        except PyPDF2.errors.DependencyError:
            # raise ValueError(f"Не удалось открыть PDF-файл: {pdf_path}")
            print(f"Не удалось открыть/обработать PDF-файл: {pdf_path}")
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
        # TO DO Вероятно это картинка тогда нужно попробовать обработать картинку?
        print(f"В извлеченном тексте нет символов, кроме пробелов: {pdf_path}")
        return None

    return text


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


            for a_tag in soup.find_all('a', href=True):
                # Extract the href value from the <a> tag
                href = a_tag['href']
                # Check if the link ends with .pdf (i.e., it's a PDF file)
                if href.lower().endswith('.pdf'):
                    print(href)


            # Find and download PDFs
            pdf_texts = [] # to store texts from PDF files
            for a_tag in soup.find_all('a', href=True):
                # Extract the href value from the <a> tag
                href = a_tag['href']
                # Check if the link ends with .pdf (i.e., it's a PDF file)
                if href.lower().endswith('.pdf'):

                    # Form the complete URL for the PDF file
                    pdf_url = href if href.startswith('http') else urljoin(link, href)

                    # if not href.startswith('http'):
                    #     pdf_url = urljoin(link, href)


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


if __name__ == "__main__":

    # Пример входных данных для теста
    test_source_link_html = SourceLink(
        link="https://fplusmobile.ru/catalog/senior/ezzy_5c_black/", 
        confidence_rate=0.8
    )

    test_source_link_pdf = SourceLink(
        link="https://fplusmobile.ru/catalog/senior/ezzy_trendy_1_white/",  
        confidence_rate=0.8
    )

    # Функция для тестирования
    def test_get_source_links_single():
        html_text_info = get_source_links_single(test_source_link_html)
        print("HTML Text:", html_text_info['html_text'])
        print("PDF Texts:", html_text_info['pdf_texts'])
        print("Source:", html_text_info['source'])

        pdf_text_info = get_source_links_single(test_source_link_pdf)
        print("HTML Text:", pdf_text_info['html_text'])
        print("PDF Texts:", pdf_text_info['pdf_texts'])
        print("Source:", pdf_text_info['source'])

    # Запуск тестов
    test_get_source_links_single()
