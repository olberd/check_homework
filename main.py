import json
import textwrap
import time
import requests
import telegram
import os
import argparse
from dotenv import load_dotenv


def check_homework(chat_id):
    load_dotenv()
    devman_token = os.getenv('DEVMAN_TOKEN')
    bot_token = os.getenv('BOT_TOKEN')

    bot = telegram.Bot(token=bot_token)
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
            continue
        except requests.exceptions.ConnectionError:
            time.sleep(10)
            continue


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Высылает уведомления о проверке работ в Телеграмм')
    parser.add_argument('chat_id', type=int, help='Введите chat_id')
    args = parser.parse_args()
    check_homework(args.chat_id)
