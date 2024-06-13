import json
import pandas as pd
from typing import Dict, List, Optional, TypedDict
import asyncio
import os
from collections import defaultdict, Counter
from yandex_gpt import YandexGPTConfigManagerForAPIKey, YandexGPT

current_dir = os.path.dirname(os.path.abspath(__file__))


class SourceLink(TypedDict):
    link: str
    confidence_rate: float


class TextInfoFromSource(TypedDict):
    html_text: str
    pdf_texts: Optional[List[str]]
    source: SourceLink


class Characteristics(TypedDict):
    char_dict: Dict
    source: SourceLink


def load_model():
    return YandexGPT(config_manager=YandexGPTConfigManagerForAPIKey())


# Читаем Excel файл и собираем уникальные характеристики в список
def collect_characteristics_list(path: str) -> List[str]:
    df = pd.read_excel(path)
    unique_characteristics = df['Название характеристики'].unique()
    return unique_characteristics.tolist()


# Делим текст на батчи заданного размера
def split_text_to_batches(text: str, batch_size: int) -> List[str]:
    return [text[i:i + batch_size] for i in range(0, len(text), batch_size)]


# Делим список характеристик на батчи заданного размера
def split_characteristics_to_batches(characteristics: List[str], batch_size: int) -> List[List[str]]:
    return [characteristics[i:i + batch_size] for i in range(0, len(characteristics), batch_size)]


# Читаем JSON файл и пробуем разные кодировки
def read_json_file(file_path: str) -> List[TextInfoFromSource]:
    encodings = ['utf-8', 'latin1', 'cp1252']
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as file:
                data = json.load(file)
            print(f"Successfully read the file with {encoding} encoding.")
            return data
        except UnicodeDecodeError as e:
            print(f"Failed to read with {encoding} encoding: {e}")
    raise ValueError("Failed to read the file with any of the tested encodings.")


# Удаляем двойные кавычки из характеристик и создаем словарь для замены старых названий на новые
def remove_double_quotes_and_map(characteristics: List[str]) -> (List[str], Dict[str, str]):
    cleaned_characteristics = []
    mapping = {}
    for char in characteristics:
        cleaned_char = char.lower().replace('"', '').replace("'", '').replace(",", '').replace(";", '')
        mapping[char] = cleaned_char
        cleaned_characteristics.append(cleaned_char)
    return cleaned_characteristics, mapping


# Предобработка характеристик и создание словаря замены названий
def preprocessing_and_map(characteristics: List[str]) -> (List[str], Dict[str, str]):
    characteristics = [x for x in characteristics if isinstance(x, str)]
    characteristics, mapping = remove_double_quotes_and_map(characteristics)
    return characteristics, mapping


# Отправляем запрос к модели Yandex GPT и обрабатываем ответ
async def process_message(sem, message, yandex_gpt):
    try:
        async with sem:
            await asyncio.sleep(0.5)
            result = yandex_gpt.get_sync_completion(messages=message, temperature=0.0, max_tokens=8000)
            print("\n", result)
            return result
    except Exception as e:
        print(e)
        return ""


# Убираем специальные символы из текста
def filter_special_symbols(text: str) -> str:
    return text.replace("\n", " ").replace("\xa0", " ")


# Получаем ответ от модели для конкретного текста и набора характеристик
async def extract_characteristics_from_text(text: str, characteristics: List[str]) -> List[str]:
    yandex_gpt = load_model()

    text_batch_size = 10000
    characteristics_batch_size = 3

    text_batches = split_text_to_batches(text, text_batch_size)
    characteristics_batches = split_characteristics_to_batches(characteristics, characteristics_batch_size)
    messages = []

    for text_batch in text_batches[:]:
        for characteristics_batch in characteristics_batches[:]:
            messages.append([
                {'role': 'system', 'text': (
                    'Ты - технический эксперт в ноутбуках. '
                    f'Список возможных характеристик: {"; ".join([f"\"{characteristic}\"" for characteristic in characteristics_batch])}. '
                    'Из отрывка текстового описания ноутбука выдели упоминаемые характеристики, если они присутствуют в списке возможных характеристик. '
                    "Ищи не только прямые упоминания характеристик, но и косвенные признаки их наличия. "
                    "Для ответа используй точные формулировки из списка возможных характеристик. "
                    'Ответ дай в формате JSON без дополнительных комментариев, используя все характеристики из списка возможных характеристик: {"характеристика1": "значение1", "характеристика2": "значение2", ...}". '
                    'Если информация о характеристике отсутствует в тексте, в качестве значения используй "Нет данных".'
                )},
                {'role': 'user', 'text': (
                    f'Отрывок текста описания ноутбука: "{filter_special_symbols(text_batch)}".'
                )}
            ])

    sem = asyncio.Semaphore(1)
    tasks = [process_message(sem, message, yandex_gpt) for message in messages]
    results = await asyncio.gather(*tasks)

    return results


# Объединяем словари в один
def merge_dicts(dicts: List[Dict]) -> Dict:
    # Создаем словарь для хранения списков значений по каждому ключу
    combined_dict = defaultdict(list)

    # Собираем все значения для каждого ключа из списка словарей
    for d in dicts:
        for key, value in d.items():
            combined_dict[key].append(value)

    # Создаем итоговый словарь, выбирая наиболее частое значение для каждого ключа
    result_dict = {}
    for key, values in combined_dict.items():
        most_common_value, _ = Counter(values).most_common(1)[0]
        result_dict[key] = most_common_value

    return result_dict


def str_to_dict(string: str) -> Dict:
    string = string.replace('"', '').replace("'", '').replace("{", "").replace("}", "").replace("\n", " ")

    splited_string = string.split(", ")

    res_dict = {}
    for item in splited_string:
        try:
            key, value = item.split(": ")
            res_dict[key] = value
        except Exception as e:
            pass

    return res_dict


# Обрабатываем ответ модели и приводим к нужному формату словаря
async def process_model_answer(text: str, characteristics: List[str]) -> Dict:
    # Получаем ответ от модели для конкретного текста и набора характеристик
    answer: List[str] = await extract_characteristics_from_text(text, characteristics)
    # Преобразуем строковые представления словарей в настоящие словари
    dicts = [str_to_dict(x) for x in answer if x]
    print(dicts)
    # Преобразуем строковые представления словарей в настоящие словари
    final_dict = merge_dicts(dicts)
    print(final_dict)
    return final_dict


# Возвращаем старые названия характеристик из словаря
def map_old_names_to_characteristics(old_to_new_mapping: Dict[str, str], dict_characteristics: Dict) -> Dict:
    old_to_characteristics = {}
    for old_name, new_name in old_to_new_mapping.items():
        if new_name in dict_characteristics:
            old_to_characteristics[old_name] = dict_characteristics[new_name]
    return old_to_characteristics


# Получаем характеристики по номеру части
async def get_characteristics_by_part_number(part_number: int) -> Dict:
    part_number = str(part_number)

    # Загружаем текст
    json_file_path = os.path.join(current_dir, '..', 'new_data.json')

    # text_json = read_json_file(r'D:\github\notebooks\new_data.json'))
    # Читаем JSON-файл
    text_json = read_json_file(json_file_path)

    text = text_json[part_number]['html_text']

    # Вычленяем confidence_rate и ссылку
    confidence_rate = text_json[part_number]['source']['confidence_rate']
    url = text_json[part_number]['source']['confidence_rate']

    # Загружаем характеристики
    path_characteristics = os.path.join(current_dir, '..', 'laptop.xlsx')
    # path_characteristics = r'D:\github\notebooks\laptop.xlsx'
    characteristics = collect_characteristics_list(path_characteristics)

    characteristics, mapping = preprocessing_and_map(characteristics)

    # Вывод ответа модели
    # Получаем ответ модели для текста и характеристик
    answer = await process_model_answer(text, characteristics)
    # Возвращаем старые названия характеристик в соответствии с исходным словарем
    result = map_old_names_to_characteristics(mapping, answer)

    return result


# переделать изменить, сделать для списка
async def get_product_characteristics_from_sources_single(product_texts_from_sources: list[TextInfoFromSource]):
    # выбираем один продукт пока (TODO)
    product_info = product_texts_from_sources[0]

    # # Извлекаем рейтинг уверенности и URL источника для заданного номера детали
    # confidence_rate = text_json[part_number]['source']['confidence_rate']
    # url = text_json[part_number]['source']['link']

    text = product_info['html_text']  # Если используется html_text для обработки

    # Извлекаем рейтинг уверенности и URL источника для текущего продукта
    confidence_rate = product_info['source']['confidence_rate']
    url = product_info['source']['link']

    # Определяем путь к Excel-файлу с характеристиками
    path_characteristics = os.path.join(current_dir, '..', 'laptop.xlsx')

    # Читаем Excel-файл и собираем уникальные характеристики в список
    characteristics = collect_characteristics_list(path_characteristics)
    # print(characteristics)

    # Предобрабатываем характеристики и создаем словарь замены старых названий на новые
    characteristics, mapping = preprocessing_and_map(characteristics)
    # print(mapping)

    # Получаем ответ модели для текста и характеристик
    answer = await process_model_answer(text, characteristics)

    # Возвращаем старые названия характеристик в соответствии с исходным словарем
    final_characteristics = map_old_names_to_characteristics(mapping, answer)

    # Формируем финальный словарь с характеристиками и метаданными источника
    result = {
        "characteristics": final_characteristics,
        "source": {
            "link": url,
            "confidence_rate": confidence_rate
        }
    }

    return result


# # Главная функция для запуска скрипта старая
# def main():
#     # part_number = 1383001  # Пример номера части
#     # part_number = 1497691  # Пример номера части
#     part_number = 2008797
#     result = asyncio.run(get_characteristics_by_part_number(part_number))
#     print(result)


# Главная функция для тестирования  скрипта get_product_characteristics_from_sources_single
def main():
    # part_number = 1383001
    # part_number = 1497691
    part_number = 2008797
    part_number = str(part_number)

    # Загружаем текст
    json_file_path = os.path.join(current_dir, '..', 'new_data.json')
    text_json = read_json_file(json_file_path)

    text = text_json[part_number]['html_text']
    pdf_texts = text_json[part_number]['pdf_texts']

    # Вычленяем confidence_rate и ссылку
    confidence_rate = text_json[part_number]['source']['confidence_rate']
    url = text_json[part_number]['source']['confidence_rate']

    text_info_list = []

    # Создаем объект TextInfoFromSource
    product_texts_from_sources = TextInfoFromSource(
        html_text=text,
        pdf_texts=pdf_texts,  # Если PDF текстов нет, можно оставить None
        source=SourceLink(
            link=url,
            confidence_rate=confidence_rate
        )
    )
    text_info_list.append(product_texts_from_sources)

    result = asyncio.run(get_product_characteristics_from_sources_single(text_info_list))
    print(result)


if __name__ == "__main__":
    # os.chdir("../../")

    from dotenv import load_dotenv
    print(load_dotenv("env/.env.yandex_search"))
    print(load_dotenv("env/.env.api_key"))

    main()