FROM python:3.11-slim

WORKDIR /app

# Копируем только requirements сначала (для кэша)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код
COPY . .

# Папка для базы данных (SQLite)
VOLUME /app/data

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]