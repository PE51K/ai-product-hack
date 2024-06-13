FROM python:3.12.2

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем файл requirements.txt в рабочую директорию контейнера
COPY requirements.txt .

# Устанавливаем зависимости, указанные в requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все файлы из текущей директории на хосте в рабочую директорию контейнера
COPY . .

# Открываем порт 8501 для Streamlit
EXPOSE 8501

# Команда для запуска Streamlit приложения
CMD ["streamlit", "run", "src/main.py"]
