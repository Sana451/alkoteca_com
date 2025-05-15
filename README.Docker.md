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