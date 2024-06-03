# import os
# import csv

# def check_files(folder_path):
# 	"""
# 	Проверяет,  открылись ли и скачались ли все CSV-файлы в папке.

# 	Args:
# 	  folder_path (str): Путь к папке с CSV-файлами.

# 	Returns:
# 	  bool: True, если все файлы открылись и скачались успешно, False - в противном случае.
# 	"""

# 	success = True
# 	for filename in os.listdir(folder_path):
# 		if filename.endswith('.csv'):
# 			file_path = os.path.join(folder_path, filename)
# 			try:
# 				with open(file_path, 'r') as csvfile:
# 				    # Прочитать несколько строк, чтобы проверить наличие данных
# 				    csv.reader(csvfile)
# 			except Exception as e:
# 				print(f"Ошибка при открытии файла: {file_path}. Ошибка: {e}")
# 				success = False
# 				break

# 	return success

# def parse_csv_file(file_path):
# 	"""
# 	Парсит CSV-файл и возвращает данные в виде списка словарей.

# 	Args:
# 	  file_path (str): Путь к CSV-файлу.

# 	Returns:
# 	  List[Dict]: Список словарей, где каждый словарь представляет собой строку из CSV-файла.
# 	"""

# 	data = []
# 	with open(file_path, 'r') as csvfile:
# 		reader = csv.DictReader(csvfile)
# 		for row in reader:
# 		    data.append(row)
# 	return data


# folder_path = "example_csv"

# if check_files(folder_path):
# 	print("Все CSV-файлы открыты и скачаны успешно.")

# 	for filename in os.listdir(folder_path):
# 		if filename.endswith('.csv'):
# 			file_path = os.path.join(folder_path, filename)
# 			parsed_data = parse_csv_file(file_path)
# 			print(f"Данные из файла {filename}:")
# 			print(parsed_data)
# else:
# 	print("Ошибка при открытии или скачивании CSV-файлов.")





# import os
# import pandas as pd

# def load_csv_files_from_folder(folder_path):
#     csv_data = {}
    
#     # Получаем список всех файлов в указанной папке
#     for file_name in os.listdir(folder_path):
#         if file_name.endswith('.csv'):
#             file_path = os.path.join(folder_path, file_name)
#             # Читаем CSV файл в DataFrame
#             df = pd.read_csv(file_path, encoding='cp1252')
#             # Сохраняем DataFrame в словаре
#             csv_data[file_name] = df
    
#     return csv_data

# # def load_csv_files_from_folder(folder_path):
# #     csv_data = {}
# #     encoding_list = ['utf-8', 'latin1', 'iso-8859-1', 'cp1252']
    
# #     # Получаем список всех файлов в указанной папке
# #     for file_name in os.listdir(folder_path):
# #         if file_name.endswith('.csv'):
# #             file_path = os.path.join(folder_path, file_name)
# #             # Пробуем прочитать CSV файл с различными кодировками
# #             for encoding in encoding_list:
# #                 try:
# #                     df = pd.read_csv(file_path, encoding=encoding)
# #                     csv_data[file_name] = df
# #                     break  # Выход из цикла, если чтение прошло успешно
# #                 except UnicodeDecodeError:
# #                     continue  # Пробуем следующую кодировку
# #                 except Exception as e:
# #                     print(f"Error reading {file_name} with {encoding} encoding: {e}")
# #                     break

# #     return csv_data


# # Указываем путь к папке с CSV файлами
# folder_path = 'example_csv'
# csv_files_data = load_csv_files_from_folder(folder_path)

# # Пример: выводим первые несколько строк каждого загруженного DataFrame
# for file_name, df in csv_files_data.items():
#     print(f"Data from {file_name}:")
#     print(df.head())


import os
import pandas as pd

def load_excel_files_from_folder(folder_path):
    excel_data = {}
    
    # Получаем список всех файлов в указанной папке
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.xlsx') or file_name.endswith('.xls'):
            file_path = os.path.join(folder_path, file_name)
            try:
                # Читаем все листы из Excel файла в словарь DataFrame-ов
                sheets = pd.read_excel(file_path, sheet_name=None)
                excel_data[file_name] = sheets
            except Exception as e:
                print(f"Error reading {file_name}: {e}")

    return excel_data

# Указываем путь к папке с Excel файлами
folder_path = 'excel_files'
excel_files_data = load_excel_files_from_folder(folder_path)

# Пример: выводим первые несколько строк каждого листа каждого загруженного Excel файла
for file_name, sheets in excel_files_data.items():
    print(f"Data from {file_name}:")
    for sheet_name, df in sheets.items():
        print(f"Sheet: {sheet_name}")
        print(df.head())