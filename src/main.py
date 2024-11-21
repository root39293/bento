from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import sys
from src.chat.router import router as chat_router

def get_static_path():
    """실행 파일 또는 스크립트 위치 기준으로 static 폴더 경로 반환"""
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, 'static')
    else:
        return 'static'

app = FastAPI(
    title='Bento Chat Assistant',
    description='FastAPI based Chatbot Starter Kit',
    version='0.1.0'
)

app.include_router(chat_router, prefix='/api/v1', tags=['chat'])

static_path = get_static_path()
app.mount("/", StaticFiles(directory=static_path, html=True), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)