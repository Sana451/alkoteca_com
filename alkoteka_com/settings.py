import os
from pathlib import Path

BOT_NAME = "alkoteka_com"

SPIDER_MODULES = ["alkoteka_com.spiders"]
NEWSPIDER_MODULE = "alkoteka_com.spiders"

ROBOTSTXT_OBEY = False
HTTPCACHE_ENABLED = False
DOWNLOAD_DELAY = 2.5

CONCURRENT_REQUESTS = int(os.getenv("CONCURRENT_REQUESTS", 1))

REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

HEADLESS = os.getenv("HEADLESS", "False").strip() in ("1", "True", "yes")

PLAYWRIGHT_LAUNCH_OPTIONS = {
    "headless": HEADLESS,
    "timeout": 20 * 1000,
    "args": ["--start-maximized", "--window-size=1920,1080"],
}

PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT = 60 * 1000
DOWNLOAD_TIMEOUT = 15

PLAYWRIGHT_PROCESS_REQUEST_HEADERS = None

SCRAPOXY_MASTER = "http://localhost:8888"
SCRAPOXY_USERNAME = "bsjyeg3tw1atjw0r97bfhs"
SCRAPOXY_PASSWORD = "8d9nbfoni746ze41a5t8n"

SCRAPOXY_MASTER_DOCKER = "http://host.docker.internal:8888"
SCRAPOXY_USERNAME_LINUX_SERVER = "q8typqrlsq6wcnemh57rb"
SCRAPOXY_PASSWORD_LINUX_SERVER = "m7g9755kpebawozdyxu92"

PLAYWRIGHT_CONTEXTS = {
    "default": {
        "viewport": None,
    }
}

SCRAPOXY = os.getenv("SCRAPOXY", "False").strip() in ("1", "True", "yes")
if SCRAPOXY:
    PLAYWRIGHT_CONTEXTS["proxy"] = {
        "server": SCRAPOXY_MASTER,
        # "server": SCRAPOXY_MASTER_DOCKER,
        "username": SCRAPOXY_USERNAME,
        "password": SCRAPOXY_PASSWORD,
    }

ZENROWS_API_KEY = os.getenv("ZENROWS_API_KEY", "")
ZENROWS_PROXY_USERNAME = os.getenv("ZENROWS_PROXY_USERNAME", "")
ZENROWS_PROXY_PASSWORD = os.getenv("ZENROWS_PROXY_PASSWORD", "")

ZENROWS_PROXY = os.getenv("ZENROWS_PROXY", "False").strip() in ("1", "True", "yes")

if ZENROWS_PROXY:
    PLAYWRIGHT_LAUNCH_OPTIONS = {
        "headless": False,
        "proxy": {
            "server": "http://superproxy.zenrows.com:1337",
            "username": ZENROWS_PROXY_USERNAME,
            "password": ZENROWS_PROXY_PASSWORD,
        },
    }

PLAYWRIGHT_CONTEXT_ARGS = {
    "wait_until": "load",
}

BASE_DIR = Path(__file__).resolve().parent.parent

RESULTS_DIR = BASE_DIR / f"{BOT_NAME}/results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

LINKS_DIR = RESULTS_DIR / "links"
LINKS_DIR.mkdir(parents=True, exist_ok=True)

ERRORS_DIR = RESULTS_DIR / "errors"
ERRORS_DIR.mkdir(parents=True, exist_ok=True)

PAGES_DIR = RESULTS_DIR / "pages"
PAGES_DIR.mkdir(parents=True, exist_ok=True)

LOGS_DIR = RESULTS_DIR / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

START_PAGINATOR_URL = ""
LOGIN_URL = ""

DOMAIN = "https://alkoteka.com"
BRAND = ""

LANGUAGE = os.getenv("LANGUAGE", "ru")

LANG_MAP = {
    "ru": (
        "ru",
        "https://alkoteka.com/catalog",
        LINKS_DIR / f"{BOT_NAME}.{BRAND}.{LANGUAGE}.links.csv",
        "",
    ),
}
LANG_PREFIX, START_URL, LINKS_FILE_PATH, SITEMAP_URL = LANG_MAP.get(LANGUAGE)
RESULTS_FILE_PATH = os.getenv("RESULTS_FILE_PATH", RESULTS_DIR / f"{BOT_NAME}.{BRAND}.{LANGUAGE}.csv")

ERRORS_FILE_PATH = ERRORS_DIR / "errors.csv"
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")
PRODUCTION = os.getenv("PRODUCTION", "False").strip() in ("1", "True", "yes")

if PRODUCTION is True:
    LOG_FILE = LOGS_DIR / "logs.txt"
    if LOG_FILE.exists():
        LOG_FILE.write_text("")
    else:
        LOG_FILE.touch()

    PROGRESS_FILE = LOGS_DIR / "logs.txt"
    PROGRESS_FILE.touch(exist_ok=True)

    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    if HEADLESS:
        PLAYWRIGHT_LAUNCH_OPTIONS["headless"] = True

DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
}

HTTP_PROXY = 'http://U9xafG:ga5jh6@186.65.118.126:9983'

headers = {
    'Accept': 'application/json',
    'User-Agent': 'Mozilla/5.0',
    'Referer': 'https://alkoteka.com/catalog/shampanskoe-i-igristoe',
}

cookies = {
    'alkoteka_age_confirm': 'true',
    'alkoteka_geo': 'true',
    'alkoteka_locality': '{"uuid":"4a70f9e0-46ae-11e7-83ff-00155d026416","name":"Краснодар","slug":"krasnodar","longitude":"38.975996","latitude":"45.040216","accented":true}',
}

COOKIES = cookies
windows_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
headers['User-Agent'] = windows_user_agent
headers['sec-ch-ua-platform'] = '"Windows"'
HEADERS = headers

"""
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
"""
