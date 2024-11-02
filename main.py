import json
import yaml
import time
from datetime import datetime

import requests
from pydub import AudioSegment
from pydub.playback import play

import telegram
import asyncio


def check_api(url, cookies):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers, cookies=cookies)
    return json.loads(response.text)


def play_sound(file_path):
    sound = AudioSegment.from_file(file_path, format="mp3", parameters=["-loglevel", "panic"])
    play(sound)


def read_config(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
            return config
    except FileNotFoundError:
        print(f"Error: {file_path} 파일을 찾을 수 없습니다.")
        return None
    except yaml.YAMLError as e:
        print(f"Error: YAML 파일 파싱 중 오류가 발생했습니다. {e}")
        return None


async def send_telegram_message(api_key, chat_id, message):
    bot = telegram.Bot(token=api_key)
    await bot.send_message(chat_id=chat_id, text=message)


def print_and_send_telegram_message(message):
    config = read_config("config.yml")
    telegram_api_key = config['telegram_api_key']
    telegram_chat_id = config['telegram_chat_id']
    print(message)
    asyncio.run(send_telegram_message(telegram_api_key, telegram_chat_id, message))


def main():
    config = read_config("config.yml")
    cookie = config['cookie']
    check_interval = config['check_interval_seconds']  # 초 단위로 체크 주기 설정 (예: 60초)
    target_date = config['target_date']
    telegram_api_key = config['telegram_api_key']
    telegram_chat_id = config['telegram_chat_id']

    print(f"설정된 쿠키(JSESSIONID): {cookie}")
    print(f"설정된 체크 주기: {check_interval}초")
    print(f"설정된 대상 날짜: {target_date}")
    print(f"텔레그램 api_key: {telegram_api_key}")
    print(f"텔레그램 chat_id: {telegram_chat_id}")

    api_url = f"https://www.sciencecenter.go.kr/scipia/schedules/priceList?SEMESTER_CD=SM110062233270000034&COURSE_CD=CS110062233270000190&DAY={target_date}"
    cookies = {
        'JSESSIONID': cookie
    }
    sound_file = "alert-109578.mp3"  # 알림음 파일 경로

    print_and_send_telegram_message("API 모니터링을 시작합니다...")
    while True:
        try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            data = check_api(api_url, cookies)

            if data["LectureList"] and len(data["LectureList"]) > 0:
                current_vacancy = data["LectureList"][0]["VACANCY_CNT"]

                print_and_send_telegram_message(f"[{now}] 현재 잔여석: {current_vacancy}")

                if current_vacancy >= 1:
                    print_and_send_telegram_message(f"[{now}] 잔여석이 1 이상입니다!")
                    play_sound(sound_file)
            else:
                print_and_send_telegram_message(f"[{now}] LectureList가 비어있거나 존재하지 않습니다.")
        except Exception as e:
            print_and_send_telegram_message(f"[{now}] 오류 발생: {e}")

        time.sleep(check_interval)


if __name__ == "__main__":
    main()
