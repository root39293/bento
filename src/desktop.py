import webview
import uvicorn
import threading
import sys
import os
import time
import requests
from requests.exceptions import ConnectionError

if getattr(sys, 'frozen', False):
    application_path = sys._MEIPASS
else:
    application_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

static_path = os.path.join(application_path, 'static')
os.environ['STATIC_PATH'] = static_path

from src.main import app

def start_server():
    config = uvicorn.Config(
        app=app,
        host="127.0.0.1",
        port=8000,
        log_level="info",
        loop="asyncio",
        http="h11",
        timeout_keep_alive=0,
        workers=1,
    )
    server = uvicorn.Server(config)
    server.run()

def wait_for_server():
    print("서버 시작 대기 중...")
    max_attempts = 50
    attempts = 0
    while attempts < max_attempts:
        try:
            response = requests.get('http://127.0.0.1:8000')
            print("서버 시작됨!")
            return True
        except ConnectionError:
            attempts += 1
            time.sleep(0.1)
    print("서버 시작 실패!")
    return False

if __name__ == '__main__':
    print("애플리케이션 시작...")
    
    if sys.platform == 'win32':
        os.environ['PYTHONUNBUFFERED'] = '1'
        os.environ['PYTHONASYNCIODEBUG'] = '1'

    print("서버 스레드 시작...")
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    if wait_for_server():
        print("웹뷰 생성 중...")
        window = webview.create_window(
            title='Bento Chat Assistant',
            url='http://127.0.0.1:8000',
            width=1440,
            height=900,
            resizable=True,
            min_size=(1280, 768),
            text_select=True,
            x=None,
            y=None,
        )
        print("웹뷰 시작...")
        webview.start(debug=False)
    else:
        print("서버 시작 실패로 프로그램을 종료합니다.")
        sys.exit(1)