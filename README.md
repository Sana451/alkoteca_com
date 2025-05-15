# 📦 Alkoteka.com Scraper

Этот проект — Scrapy-паук для парсинга товаров с сайта **alkoteka.com**. Результаты сохраняются в JSON и CSV, с логированием и обработкой ошибок.

## 🛠 Установка и запуск

### 1. Клонируйте репозиторий

```bash
git clone https://github.com/Sana451/alkoteca_com.git
cd alkoteka_com
```

### 2. Создайте и активируйте виртуальное окружение (опционально, но рекомендуется)

```bash
python -m venv .venv
source .venv/bin/activate  # для Linux/macOS
# или
.venv\Scripts\activate  # для Windows
```

### 3. Установите зависимости

```bash
pip install -r requirements.txt
```

### 4. Запуск парсера

```bash
scrapy crawl alkoteka_com -O alkoteka_com/results/alkoteka_com.$BRAND.$LANGUAGE.json
```

Для более точной настройкм можно использовать каоманду:

```bash
export CONCURRENT_REQUESTS=1 && \
export LOG_LEVEL=INFO && \
export LANGUAGE=ru && \
export BRAND='' && \
export PRODUCTION=True && \
export HEADLESS=False && \
export SCRAPOXY=False && \
export ZENROWS_PROXY=False && \
export SPIDER_NAME=alkoteka_com_spider && \
export RESULTS_FILE_PATH=alkoteka_com/results/alkoteka_com.$BRAND.$LANGUAGE.json && \

scrapy crawl $SPIDER_NAME -O $RESULTS_FILE_PATH
```

По завершению парсинга данные будут сохранены в папке `alkoteka_com/results`.

## ⚙ Структура проекта

- `alkoteka_com/spiders/alkoteka_com_spider.py` — основной Scrapy-паук
- `results/` — выходные данные (`.json`, `.csv`, `.links.csv`)
- `pipelines.py`, `middlewares.py` — дополнительная обработка
- `logging_telegram_mixin.py` — логирование в Telegram (если используется)

## 🐳 Docker (опционально)

Если вы хотите запускать проект в контейнере:

### Building and running application

Запустите парсинг последовательно выполнив следующие команды:

```console
COMPOSE_BAKE=true docker compose build --no-cache
```

## Языки настраиваются строкой export LANGUAGE="...", варианты: en, de

# Запуск на сбор продуктов (headed режим в docker)

```console
docker compose run --rm --remove-orphans \
  -e TELEGRAM_DOMAIN="http://51.195.63.110:8081" \
  -e PRODUCTION="True" \
  -e SCRAPOXY="False" \
  -e CONCURRENT_REQUESTS="1" \
  -e HEADLESS="False" \
  -e LANGUAGE="ru" \
  -e BRAND="" \
  -e LOG_LEVEL="INFO" \
  -e RESULTS_FILE_PATH="/app/alkoteka_com/results/alkoteka_com.${BRAND}.${LANGUAGE}.JSON" \
  -e SPIDER_NAME="alkoteka_com_spider" \
  parser
```

