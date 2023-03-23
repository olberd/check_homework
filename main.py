import json
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
            decoded_response = response.json()
            if decoded_response['status'] == 'found':
                lesson_title = decoded_response['new_attempts'][0]['lesson_title']
                lesson_url = decoded_response['new_attempts'][0]['lesson_url']
                is_negative = decoded_response['new_attempts'][0]['is_negative']
                if is_negative:
                    bot.send_message(chat_id=chat_id, text=f'У вас проверили работу "{lesson_title}"\n\n'
                                                           f'К сожалению, в работе нашлись ошибки \n{lesson_url}')
                else:
                    bot.send_message(chat_id=chat_id, text=f'У вас проверили работу "{lesson_title}"\n\n'
                                                           f'Преподавателю всё понравилось, можно приступать к '
                                                           f'следующему уроку!{lesson_url}')

            elif decoded_response['status'] == 'timeout':
                params = {
                   'timestamp': decoded_response['timestamp_to_request'],
                }
                response = requests.get('https://dvmn.org/api/long_polling/', headers=headers, params=payloads)
                response.raise_for_status()
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
