import os
import pandas as pd
from typing import Dict, List, Set

def load_excel_files_from_folder(folder_path: str) -> Dict[str, Dict[str, pd.DataFrame]]:
    excel_data = {} # Словарь для хранения данных из Excel-файлов
    
    # Получаем список всех файлов в указанной папке
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.xlsx') or file_name.endswith('.xls'):
            file_path = os.path.join(folder_path, file_name)
            try:
                # Читаем все листы из Excel файла в словарь DataFrame-ов
                sheets = pd.read_excel(file_path, sheet_name=None)
                excel_data[file_name] = sheets # Добавляем DataFrame-ы в словарь под ключом - имя файла
            except Exception as e:
                print(f"Error reading {file_name}: {e}")

    return excel_data


def print_excel_files_data(excel_files_data: Dict[str, Dict[str, pd.DataFrame]]):
    for file_name, sheets in excel_files_data.items():
        print(f"Data from {file_name}:")
        for sheet_name, df in sheets.items():
            print(f"Sheet: {sheet_name}")
            print(df.columns.tolist())  # Выводит список названий колонок текущего листа
            print(df.head())


def check_columns_consistency(excel_files_data: Dict[str, Dict[str, pd.DataFrame]]) -> bool:
    # Переменная для хранения имен столбцов первого встреченного DataFrame
    first_df_columns: List[str] = None

    # Итерация по значениям внешнего словаря (словарям листов для каждого файла)
    for sheets in excel_files_data.values():
        for df in sheets.values():
        # Если это первый встреченный DataFrame, сохраняем его имена столбцов
            if first_df_columns is None:
                first_df_columns = df.columns.tolist()
            # Сравниваем имена столбцов текущего DataFrame с сохраненными
            else:
                if set(df.columns) != set(first_df_columns):
                    # Если имена столбцов не совпадают, возвращаем False
                    return False

    # Если цикл завершается без обнаружения несоответствий, все DataFrames имеют одинаковые имена столбцов
    return True

# old
# def combine_dataframes(excel_files_data: Dict[str, Dict[str, pd.DataFrame]]) -> pd.DataFrame:
#     combined_df = pd.DataFrame()
#     for sheets in excel_files_data.values():
#         for df in sheets.values():
#             combined_df = pd.concat([combined_df, df], ignore_index=True)
#     return combined_df

def combine_dataframes(excel_files_data: Dict[str, Dict[str, pd.DataFrame]], common_columns: Set[str]) -> pd.DataFrame:
    combined_df = pd.DataFrame()
    for sheets in excel_files_data.values():
        for df in sheets.values():
            if common_columns.issubset(df.columns):
                combined_df = pd.concat([combined_df, df[list(common_columns)]], ignore_index=True)
    return combined_df

def find_common_columns_within_file(excel_files_data: Dict[str, Dict[str, pd.DataFrame]]) -> Dict[str, Set[str]]:
    common_columns = {}
    for file_name, sheets in excel_files_data.items():
        all_columns = [set(df.columns) for df in sheets.values()]
        if all_columns:
            common_columns[file_name] = set.intersection(*all_columns)
    return common_columns

def read_and_display_csv(file_path: str):
    try:
        # Чтение CSV файла в DataFrame
        df = pd.read_csv(file_path)
        
        # Вывод заголовков колонок
        print("Columns:")
        print(df.columns.tolist())
        
        # Вывод 10 случайных строк
        print("\n10 Random Rows:")
        print(df.sample(n=10))
        
    except Exception as e:
        print(f"Error reading {file_path}: {e}")

if __name__ == "__main__":

    import sys
    # Изменение кодировки стандартного вывода на utf-8
    sys.stdout.reconfigure(encoding='utf-8')

    # Указываем путь к папке с Excel файлами
    folder_path = 'excel_files'


    # excel_files_data.items() возвращает словарь, где:
    # Ключи: Имена файлов Excel (строки).
    # Значения: Словари, где:
    # Ключи: Имена листов Excel (строки).
    # Значения: Объекты pd.DataFrame, содержащие данные с соответствующего листа.
    # Предположим, что `excel_files_data` содержит данные из двух Excel-файлов:
    # 'file1.xlsx' и 'file2.xlsx'.

    # excel_files_data = {
    #     'file1.xlsx': {
    #         'Sheet1': pd.DataFrame([[1, 2, 3], [4, 5, 6]]),
    #         'Sheet2': pd.DataFrame([[7, 8, 9], [10, 11, 12]]),
    #     },
    #     'file2.xlsx': {
    #         'Data1': pd.DataFrame([[13, 14, 15], [16, 17, 18]]),
    #         'Data2': pd.DataFrame([[19, 20, 21], [22, 23, 24]]),
    #     }
    # }
    excel_files_data = load_excel_files_from_folder(folder_path)

    # # Пример: выводим первые несколько строк каждого листа каждого загруженного Excel файла
    # for file_name, sheets in excel_files_data.items():
    #     print(f"Data from {file_name}:")
    #     for sheet_name, df in sheets.items():
    #         print(f"Sheet: {sheet_name}")
    #         print(df.columns.tolist()) # - выводит список названий колонок текущего листа.
    #         print(df.head())


    # Вывод информации о загруженных данных
    print_excel_files_data(excel_files_data)


    # Проверка соответствия колонок
    if check_columns_consistency(excel_files_data):
        # Объединение всех DataFrame-ов в один
        combined_df = combine_dataframes(excel_files_data)
        print("Combined DataFrame:")
        print(combined_df)
    else:
        print("Columns in the Excel sheets are not consistent. Unable to combine DataFrames.")

    # Columns in the Excel sheets are not consistent. Unable to combine DataFrames.


    # Найдем общие колонки внутри каждого файла и выведем их
    common_columns = find_common_columns_within_file(excel_files_data)
    for file_name, columns in common_columns.items():
        print(f"Common columns in {file_name}: {columns}")

    # Common columns in Ссылки.xlsx: 
    # {'Бренд', 'Группа товаров', 'Модель', 'PartNumber/Артикул Производителя', 
    # 'Ситилинк - Полное Наименование', 'Код Товара', 'Ссылка на сайт поставщика/вендора'}

    # Объединение всех DataFrame-ов по общим колонкам
    if common_columns:
        for file_name, columns in common_columns.items():
            combined_df = combine_dataframes(excel_files_data, columns)
            if not combined_df.empty:
                output_file = f"{file_name.split('.')[0]}_combined.csv"
                combined_df.to_csv(output_file, index=False, encoding='utf-8')
                print(f"Combined DataFrame saved to {output_file}")
            else:
                print(f"No data to combine for file {file_name}.")
    else:
        print("No common columns found. Unable to combine DataFrames.")


    csv_file_path = 'Ссылки_combined.csv'
    
    # Чтение и вывод данных из CSV файла
    read_and_display_csv(csv_file_path)
    