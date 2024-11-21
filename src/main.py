from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from src.chat.router import router as chat_router
from src.rag.router import router as rag_router

app = FastAPI()

app.include_router(chat_router, prefix="/api/v1")
app.include_router(rag_router, prefix="/api/v1")

app.mount("/", StaticFiles(directory="static", html=True), name="static")