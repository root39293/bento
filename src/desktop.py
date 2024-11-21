import webview
import uvicorn
import threading
import sys
import os
from src.main import app

def start_server():
    config = uvicorn.Config(
        app=app,
        host="127.0.0.1",
        port=8000,
        log_level="error",
        loop="asyncio",
        http="h11",
        timeout_keep_alive=0,
        workers=1,
        buffer_size=16384,
    )
    server = uvicorn.Server(config)
    server.run()

if __name__ == '__main__':
    if sys.platform == 'win32':
        webview.platforms.initialize('edgechromium')
        
        os.environ['PYTHONUNBUFFERED'] = '1'
        os.environ['PYTHONASYNCIODEBUG'] = '1'

    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    import time
    time.sleep(1)

    window = webview.create_window(
        title='Bento Chat Assistant',
        url='http://127.0.0.1:8000',
        width=1024,
        height=768,
        resizable=True,
        min_size=(800, 600),
        text_select=True, 
    )
    
    webview.start(debug=True)