import textwrap
import time
import requests
import telegram
import os
import argparse
from dotenv import load_dotenv
import logging


logger = logging.getLogger("Telegram logger")


class TgLogsHandler(logging.Handler):
    def __init__(self, bot, chat_id):
        super().__init__()
        self.bot = bot
        self.chat_id = chat_id

    def emit(self, record):
        log_entry = self.format(record)
        self.bot.send_message(chat_id=self.chat_id, text=log_entry)


def check_homework(devman_token, bot, chat_id, logger):
    params = None
    while True:
        try:
            headers = {
                'Authorization': devman_token,

            }
            response = requests.get('https://dvmn.org/api/long_polling/', headers=headers, params=params, timeout=60)
            response.raise_for_status()
            review_info = response.json()
            if review_info['status'] == 'found':
                lesson_title = review_info['new_attempts'][0]['lesson_title']
                lesson_url = review_info['new_attempts'][0]['lesson_url']
                is_negative = review_info['new_attempts'][0]['is_negative']
                if is_negative:
                    text = textwrap.dedent(f'''\
                    У вас проверили работу "{lesson_title}"

                    К сожалению, в работе нашлись ошибки
                    {lesson_url}''')

                    bot.send_message(chat_id=chat_id, text=text)
                else:
                    text = textwrap.dedent(f'''\
                    У вас проверили работу "{lesson_title}"

                    Преподавателю всё понравилось, можно приступать к следующему уроку!
                    {lesson_url}''')
                    bot.send_message(chat_id=chat_id, text=text)

            elif review_info['status'] == 'timeout':
                params = {
                   'timestamp': review_info['timestamp_to_request'],
                }

        except requests.exceptions.ReadTimeout:
            time.sleep(10)
            continue
        except requests.exceptions.ConnectionError:
            time.sleep(10)
            continue
        except Exception as err:
            logger.exception(err)


def main():
    load_dotenv()
    devman_token = os.getenv('DEVMAN_TOKEN')
    bot_token = os.getenv('BOT_TOKEN')

    bot = telegram.Bot(token=bot_token)

    parser = argparse.ArgumentParser(description='Высылает уведомления о проверке работ в Телеграмм')
    parser.add_argument('chat_id', type=int, help='Введите chat_id')
    args = parser.parse_args()
    chat_id = args.chat_id
    logger.setLevel(logging.INFO)
    logger.addHandler(TgLogsHandler(bot, chat_id))
    logger.info('Бот запустился')
    check_homework(devman_token, bot, chat_id, logger)


if __name__ == '__main__':
    main()
