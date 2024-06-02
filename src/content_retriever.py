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
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)

    response = requests.get(url)
    filename = os.path.join(dest_folder, url.split('/')[-1])
    
    with open(filename, 'wb') as file:
        file.write(response.content)
    
    return filename

def extract_text_from_pdf(pdf_path: str) -> str:
    text = ""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text += page.extract_text() + "\n"
    return text

def get_source_links(product_source_links: List[SourceLink]) -> List[TextInfoFromSource]:
    results = []
    
    for source_link in product_source_links:
        link = source_link['link']
        response = requests.get(link)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract text from HTML
        html_text = soup.get_text(separator="\n", strip=True)
        
        # Find and download PDFs
        pdf_texts = []
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            if href.lower().endswith('.pdf'):
                pdf_url = href if href.startswith('http') else link + href
                pdf_path = download_file(pdf_url, 'downloads')
                pdf_text = extract_text_from_pdf(pdf_path)
                pdf_texts.append(pdf_text)
        
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
        {"link": "https://consumer.huawei.com/kz/phones/y5p/specs/", "confidence_rate": 0.9},
        # {"link": "https://example.org", "confidence_rate": 0.8}
    ]

    texts = get_source_links(product_source_links)

    import sys
    # Изменение кодировки стандартного вывода на utf-8
    sys.stdout.reconfigure(encoding='utf-8')

    for text_info in texts:
        print(text_info)