import webview
import uvicorn
import threading
import sys
import os
from src.main import app

def start_server():
    # uvicorn 설정을 최적화
    config = uvicorn.Config(
        app=app,
        host="127.0.0.1",
        port=8000,
        log_level="error",
        loop="asyncio",
        http="h11",
        timeout_keep_alive=0,
        workers=1,
        buffer_size=16384,  # 버퍼 사이즈 최적화
    )
    server = uvicorn.Server(config)
    server.run()

if __name__ == '__main__':
    # FastAPI 서버 시작 전에 Windows 환경 설정
    if sys.platform == 'win32':
        # Edge WebView2 사용 강제
        webview.platforms.initialize('edgechromium')
        
        # Windows에서의 스트리밍 최적화를 위한 환경 변수 설정
        os.environ['PYTHONUNBUFFERED'] = '1'
        os.environ['PYTHONASYNCIODEBUG'] = '1'

    # FastAPI 서버 백그라운드로 시작
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    # 서버가 완전히 시작될 때까지 잠시 대기
    import time
    time.sleep(1)

    # 웹뷰 윈도우 생성
    window = webview.create_window(
        title='Bento Chat Assistant',
        url='http://127.0.0.1:8000',
        width=1024,
        height=768,
        resizable=True,
        min_size=(800, 600),
        text_select=True,  # 텍스트 선택 가능하도록 설정
    )
    
    # 디버그 모드로 시작
    webview.start(debug=True)