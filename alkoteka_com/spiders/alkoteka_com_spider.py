from time import time
from urllib.parse import urlencode
import scrapy
from scrapy.utils.project import get_project_settings
from scrapy import signals

from .logging_telegram_mixin import LoggingTelegramMixin
from .csv_tools import read_row_from_csv_file

dict_settings = get_project_settings()


class AlkotekaComSpider(scrapy.Spider, LoggingTelegramMixin):
    name = "alkoteka_com_spider"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_url = dict_settings.get("START_URL")
        self.links_file_path = dict_settings.get("LINKS_FILE_PATH")
        self.login_url = dict_settings.get("LOGIN_URL")
        self.login = dict_settings.get("LOGIN")
        self.password = dict_settings.get("PASSWORD")
        self.cart_url = dict_settings.get("CART_URL")
        self.log_file = dict_settings.get("LOG_FILE")
        self.production = dict_settings.get("PRODUCTION")
        self.results_file_path = dict_settings.get("RESULTS_FILE_PATH")
        self.errors_file_path = dict_settings.get("ERRORS_FILE_PATH")
        self.domain = dict_settings.get("DOMAIN")
        self.headers = dict_settings.get("HEADERS", {})
        self.cookies = dict_settings.get("COOKIES", {})
        self.progress_bar = None
        self.progress_checkpoints = [1, 5, 50, 1000] + [i * 2000 for i in range(100)]
        self.sent_progress_checkpoints = set()
        self.last_sent_time = 0
        self.send_interval = 30 * 60
        # Ленивое чтение ссылок
        self._links = None
        # Открытие progress_file, если путь указан
        progress_file_path = dict_settings.get("PROGRESS_FILE")
        if progress_file_path:
            try:
                self.progress_file = open(progress_file_path, "a", encoding="utf-8")
            except FileNotFoundError:
                self.logger.error(f"Progress file path not found: {progress_file_path}")
                self.progress_file = None
        else:
            self.progress_file = None

        self.lang_prefix = dict_settings.get("LANG_PREFIX")
        self.is_logged_in = False
        self.start_page_num = 1

    @property
    def links(self):
        """Ленивая загрузка ссылок из CSV файла."""
        if self._links is None:
            if not self.links_file_path:
                self.logger.warning("LINKS_FILE_PATH is not set in dict_settings!")
                self._links = []
            else:
                try:
                    self._links = read_row_from_csv_file(self.links_file_path)
                except FileNotFoundError:
                    self.logger.error(
                        f"LINKS_FILE_PATH file not found: {self.links_file_path}"
                    )
                    self._links = []
        return self._links

    def start_requests(self):
        self.logger.info("Start_requests\n")

        self._links = self.links[:]
        for url in self.links[:]:
            if "http" in url:
                root_category_slug = url.split("/")[-1]

                params = {
                    'city_uuid': '4a70f9e0-46ae-11e7-83ff-00155d026416',  # Краснодар
                    'page': str(self.start_page_num),
                    'per_page': '500',
                    'root_category_slug': root_category_slug,
                }
                url = f'https://alkoteka.com/web-api/v1/product?{urlencode(params)}'
                self.logger.info(url)

                yield scrapy.Request(
                    url,
                    callback=self.parse,
                    cb_kwargs={"root_category_slug": root_category_slug},
                    headers=self.headers,
                    cookies=self.cookies
                )
                self.logger.info("End Start_requests\n")

    def parse(self, response, root_category_slug):
        self.logger.info("Start Parse\n")
        try:
            data = response.json()
            self.logger.info("JSON in response\n")
        except Exception:
            self.logger.warning("Not JSON in response\n")
            data = {}

        if data:
            results = data.get("results", [])
            self.logger.info(f"Found {len(results)} in JSON")
            for product_json in results:
                yield self.parse_json_product(json_obj=product_json)

            if len(results) >= 500:
                self.start_page_num += 1

                params = {
                    'city_uuid': '4a70f9e0-46ae-11e7-83ff-00155d026416',  # Краснодар
                    'page': str(self.start_page_num),
                    'per_page': '500',
                    'root_category_slug': root_category_slug,
                }
                url = f'https://alkoteka.com/web-api/v1/product?{urlencode(params)}'

                self.logger.info(f"Go to page number {self.start_page_num}\n for {root_category_slug}")

                yield scrapy.Request(
                    url,
                    callback=self.parse,
                    cb_kwargs={"root_category_slug": root_category_slug},
                    headers=self.headers,
                    cookies=self.cookies
                )

            self.logger.info("End Parse\n")

    @staticmethod
    def parse_json_product(json_obj):

        # Получить цвет и объем из filter_labels (если есть)
        color = ""
        volume = ""
        for f in json_obj.get("filter_labels", []):
            if f.get("filter", "") == "cvet":
                color = f.get("title", "")
            elif f.get("filter", "") == "obem":
                volume = f.get("title", "")

        # Формируем title
        title = json_obj.get("name", "")
        # Добавляем цвет и объем, если их нет в названии
        if color and color not in title:
            title += f", {color}"
        if volume and volume not in title:
            title += f", {volume}"

        # Цена и скидка
        price_current = float(json_obj.get("price", 0))
        prev_price = json_obj.get("prev_price", "")
        price_original = float(prev_price) if prev_price is not None else price_current
        sale_tag = ""
        if prev_price and price_current < price_original:
            discount = round((price_original - price_current) / price_original * 100)
            sale_tag = f"Скидка {discount}%"

        # Иерархия разделов
        section = []
        if "category" in json_obj and json_obj.get("category", {}):
            parent = json_obj.get("category", {}).get("parent", {})
            if parent and parent.get("name", ""):
                section.append(parent.get("name"))
            if json_obj.get("category", {}).get("name", ""):
                section.append(json_obj.get("category", {}).get("name"))

        # Маркетинговые теги
        marketing_tags = json_obj.get("marketing_tags", "")

        # В наличии
        in_stock = bool(json_obj.get("available", False))
        count = int(json_obj.get("quantity_total", 0))

        # Метаданные
        metadata = {
            "__description": "",
            "Артикул": str(json_obj.get("vendor_code", "")),
            "Код товара": str(json_obj.get("vendor_code", "")),
            "Цвет": color,
            "Объем": volume,
            "Подназвание": json_obj.get("subname", ""),
            "Статус": json_obj.get("status", "")
        }

        # Подсчёт вариантов (цвет и объем — считаем за варианты)
        variants = 0
        if color:
            variants += 1
        if volume:
            variants += 1

        result = {
            "timestamp": int(time()),
            "RPC": str(json_obj.get("vendor_code", "")),
            "url": json_obj.get("product_url", ""),
            "title": title,
            "marketing_tags": marketing_tags,
            "brand": json_obj.get("brand", ""),
            "section": section,
            "price_data": {
                "current": price_current,
                "original": price_original,
                "sale_tag": sale_tag
            },
            "stock": {
                "in_stock": in_stock,
                "count": count
            },
            "assets": {
                "main_image": json_obj.get("image_url", ""),
                "set_images": json_obj.get("set_images", ""),
                "view360": json_obj.get("view360", ""),
                "video": json_obj.get("video", "")
            },
            "metadata": metadata,
            "variants": variants
        }

        return result

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(AlkotekaComSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.engine_started, signal=signals.engine_started)
        crawler.signals.connect(spider.spider_error, signal=signals.spider_error)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        crawler.signals.connect(spider.feed_exporter_closed, signal=signals.feed_exporter_closed)
        crawler.signals.connect(spider.engine_stopped, signal=signals.engine_stopped)
        return spider
