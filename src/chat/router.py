from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import Dict
from .models import ChatRequest, ChatResponse
from .service import ChatService
from anthropic import AsyncAnthropic
from pydantic import BaseModel
from src.core.config import settings, model_settings

class APIKeyRequest(BaseModel):
    api_type: str  # 'openai' 또는 'anthropic'
    api_key: str

router = APIRouter()
chat_service = ChatService()

@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """스트리밍 응답을 위한 엔드포인트"""
    # 모델 유효성 검사
    if not model_settings.is_openai_model(request.model) and not model_settings.is_anthropic_model(request.model):
        raise HTTPException(status_code=400, detail=f"지원하지 않는 모델입니다: {request.model}")

    async def generate():
        async for chunk in chat_service.generate_response(request):
            yield chunk

    return StreamingResponse(
        generate(),
        media_type='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'text/event-stream',
        }
    )

@router.post("/chat/set-api-key")
async def set_api_key(request: APIKeyRequest):
    """API 키 설정 엔드포인트"""
    try:
        if request.api_type == "openai":
            chat_service.openai_api_key = request.api_key
        elif request.api_type == "anthropic":
            chat_service.anthropic_api_key = request.api_key
        else:
            raise HTTPException(status_code=400, detail="지원하지 않는 API 타입입니다")
        
        return {"status": "success", "message": "API 키가 성공적으로 설정되었습니다"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chat/models")
async def get_available_models():
    """사용 가능한 모델 목록 반환"""
    return {
        "models": model_settings.available_models,
        "default_models": {
            "openai": next(iter(model_settings.OPENAI_MODELS), None),  # 첫 번째 OpenAI 모델을 기본값으로
            "anthropic": next(iter(model_settings.ANTHROPIC_MODELS), None)  # 첫 번째 Anthropic 모델을 기본값으로
        }
    }