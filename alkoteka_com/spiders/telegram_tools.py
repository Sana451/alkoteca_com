import os

import requests
import logging

logger = logging.getLogger(__name__)

TELEGRAM_DOMAIN = os.getenv("TELEGRAM_DOMAIN", "https://api.telegram.org")
BOT_TOKEN = "7680351688:AAGC7eRCpQNkRkoCVy-4yjQeuG1BDwkSjoE"
CHAT_ID = "1748157760"


def send_file_result(file_name, bot_token=BOT_TOKEN, chat_id=CHAT_ID, caption="Результат парсинга"):
    """Отправляет результирующий файл в Telegram."""
    try:
        with open(file_name, 'rb') as file:
            response = requests.post(
                url=f"{TELEGRAM_DOMAIN}/bot{bot_token}/sendDocument",
                data={
                    "chat_id": chat_id,
                    "caption": caption,
                },
                files={"document": file}
            )
            logger.info(f"Файл {file_name} успешно отправлен.")
            print(f"Файл  {file_name} успешно отправлен.")
            return response.json()
    except FileNotFoundError:
        logger.error(f"Файл {file_name} не найден.")
    except requests.exceptions.RequestException as error:
        logger.error(f"Ошибка при отправке файла: {file_name} {error}")


def send_telegram_log(message="Not message to send but I wanted it too much.", bot_token=BOT_TOKEN, chat_id=CHAT_ID):
    requests.post(
        url=f"{TELEGRAM_DOMAIN}/bot{bot_token}/sendMessage",
        data={
            "chat_id": chat_id,
            "text": message
        }
    )


if __name__ == '__main__':
    send_file_result(file_name=__file__)
    send_telegram_log()
