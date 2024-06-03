from typing import TypedDict, Optional, List
import requests
from bs4 import BeautifulSoup
import os
import PyPDF2

class SourceLink(TypedDict):
    link: str
    confidence_rate: float

class TextInfoFromSource(TypedDict):
    html_text: str
    pdf_texts: Optional[List[str]]
    source: SourceLink

def download_file(url: str, dest_folder: str) -> str:
    """Downloads a file from URL to the given folder."""
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)

    response = requests.get(url)
    filename = os.path.join(dest_folder, url.split('/')[-1])
    
    with open(filename, 'wb') as file:
        file.write(response.content)
    
    return filename

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extracts text content from a PDF file at the given path.
    """
    text = ""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text += page.extract_text() + "\n"
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
    
    for source_link in product_source_links:
        # Extract the link from the current source
        link = source_link['link']
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
                pdf_path = download_file(pdf_url, 'downloads')
                # Extract text from the downloaded PDF file
                pdf_text = extract_text_from_pdf(pdf_path)
                pdf_texts.append(pdf_text)
        
        # Create a dictionary with information about the HTML and PDF texts
        text_info = TextInfoFromSource(
            html_text=html_text,
            pdf_texts=pdf_texts if pdf_texts else None,
            source=source_link
        )
        results.append(text_info)
    
    return results



if __name__ == "__main__":

    # Пример использования функции
    product_source_links = [
        # {"link": "https://consumer.huawei.com/kz/phones/y5p/specs/", "confidence_rate": 0.9},
        {"link": "https://static.digma.ru/data/download/manuals/EVE-14-C414-ID-1795672_manual_2022-08-03.pdf", "confidence_rate": 0.9},
        # {"link": "https://example.org", "confidence_rate": 0.8}
    ]

    texts = get_source_links(product_source_links)

    import sys
    # Изменение кодировки стандартного вывода на utf-8
    sys.stdout.reconfigure(encoding='utf-8')

    for text_info in texts:
        print(text_info)
