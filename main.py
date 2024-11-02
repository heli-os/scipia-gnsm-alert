import json
import time
from datetime import datetime

import requests
from pydub import AudioSegment
from pydub.playback import play


def check_api(url, cookies):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers, cookies=cookies)
    return json.loads(response.text)


def play_sound(file_path):
    sound = AudioSegment.from_file(file_path, format="mp3", parameters=["-loglevel", "panic"])
    play(sound)


def get_session_id():
    with open('cookie.txt', 'r') as f:
        return f.read().strip()


def main():
    target_date = '20241109'

    api_url = f"https://www.sciencecenter.go.kr/scipia/schedules/priceList?SEMESTER_CD=SM110062233270000034&COURSE_CD=CS110062233270000190&DAY={target_date}"
    cookies = {
        'JSESSIONID': get_session_id()
    }
    check_interval = 10  # 초 단위로 체크 주기 설정 (예: 60초)
    sound_file = "alert-109578.mp3"  # 알림음 파일 경로

    print("API 모니터링을 시작합니다...")
    while True:
        try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            data = check_api(api_url, cookies)

            if data["LectureList"] and len(data["LectureList"]) > 0:
                current_vacancy = data["LectureList"][0]["VACANCY_CNT"]

                print(f"[{now}] 현재 잔여석: {current_vacancy}")

                if current_vacancy >= 1:
                    print(f"[{now}] 잔여석이 1 이상입니다!")
                    play_sound(sound_file)
            else:
                print(f"[{now}] LectureList가 비어있거나 존재하지 않습니다.")

        except Exception as e:
            print(f"[{now}] 오류 발생: {e}")

        time.sleep(check_interval)


if __name__ == "__main__":
    main()
