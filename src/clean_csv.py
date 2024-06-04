import pandas as pd

# Загрузка данных из CSV файла
file_path = 'Ссылки_combined.csv'
data = pd.read_csv(file_path)

# Определение полностью пустых строк
initial_row_count = len(data)
empty_rows = data[data.isna().all(axis=1)]

# Определение строк, в которых заполнена только одна или две колонки (кроме колонки 'Ссылка на сайт поставщика/вендора')
few_columns_filled_rows = data[(data.notna().sum(axis=1) <= 2) | 
                               ((data.notna().sum(axis=1) == 3) & (data['Ссылка на сайт поставщика/вендора'].isna()))]

# Объединение пустых строк и строк с недостаточным количеством данных
damaged_rows = pd.concat([empty_rows, few_columns_filled_rows])

# Удаление этих строк из исходных данных
cleaned_data = data.drop(damaged_rows.index)

# Подсчет количества удаленных строк
removed_row_count = len(damaged_rows)

# Сохранение очищенных данных в новый файл
cleaned_file_path = 'Links_cleaned.csv'
cleaned_data.to_csv(cleaned_file_path, index=False)

# Вывод информации о удаленных строках
print(f"Removed rows: {removed_row_count}")
print("Removed rows data:")
print(damaged_rows)

# Сохранение удаленных строк в отдельный файл (если требуется)
damaged_file_path = 'Links_damaged.csv'
damaged_rows.to_csv(damaged_file_path, index=False)
