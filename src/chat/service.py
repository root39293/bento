from typing import AsyncGenerator, Dict
from anthropic import AsyncAnthropic
from openai import AsyncOpenAI
from src.core.config import settings, model_settings
from .models import ChatRequest

class ChatService:
    def __init__(self, openai_api_key: str = None, anthropic_api_key: str = None):
        self._openai_api_key = openai_api_key
        self._anthropic_api_key = anthropic_api_key
        self._openai_client = None
        self._anthropic_client = None
        self.conversations: Dict[str, list] = {}
    
    @property
    def openai_client(self) -> AsyncOpenAI:
        if not self._openai_client and self._openai_api_key:
            self._openai_client = AsyncOpenAI(api_key=self._openai_api_key)
        return self._openai_client
    
    @property
    def anthropic_client(self) -> AsyncAnthropic:
        if not self._anthropic_client and self._anthropic_api_key:
            self._anthropic_client = AsyncAnthropic(api_key=self._anthropic_api_key)
        return self._anthropic_client
    
    @property
    def openai_api_key(self) -> str:
        return self._openai_api_key
    
    @openai_api_key.setter
    def openai_api_key(self, value: str):
        self._openai_api_key = value
        self._openai_client = AsyncOpenAI(api_key=value)
    
    @property
    def anthropic_api_key(self) -> str:
        return self._anthropic_api_key
    
    @anthropic_api_key.setter
    def anthropic_api_key(self, value: str):
        self._anthropic_api_key = value
        self._anthropic_client = AsyncAnthropic(api_key=value)

    async def _generate_stream_anthropic(self, messages: list, model_name: str) -> AsyncGenerator[str, None]:
        if not self.anthropic_client:
            yield "Anthropic API 키가 설정되지 않았습니다."
            return

        model_config = model_settings.get_model_config(model_name)
        
        try:
            async with self.anthropic_client.messages.stream(
                model=model_name,
                max_tokens=model_config["max_tokens"],
                temperature=model_config["temperature"],
                messages=[{"role": m["role"], "content": m["content"]} for m in messages]
            ) as stream:
                async for text in stream.text_stream:
                    yield text
        except Exception as e:
            yield f"Anthropic 오류: {str(e)}"

    async def _generate_stream_openai(self, messages: list, model_name: str) -> AsyncGenerator[str, None]:
        if not self.openai_client:
            yield "OpenAI API 키가 설정되지 않았습니다."
            return

        model_config = model_settings.get_model_config(model_name)
        
        try:
            stream = await self.openai_client.chat.completions.create(
                model=model_name,
                messages=messages,
                max_tokens=model_config["max_tokens"],
                temperature=model_config["temperature"],
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            yield f"OpenAI 오류: {str(e)}"
    
    async def generate_response(self, request: ChatRequest) -> AsyncGenerator[str, None]:
        try:
            messages = []
            if request.context_enabled and request.conversation_id in self.conversations:
                messages.extend(self.conversations[request.conversation_id])
            
            messages.append({"role": "user", "content": request.question})
            
            # 모델에 따라 적절한 생성기 선택
            if model_settings.is_openai_model(request.model):
                generator = self._generate_stream_openai(messages, request.model)
            elif model_settings.is_anthropic_model(request.model):
                generator = self._generate_stream_anthropic(messages, request.model)
            else:
                yield f"지원하지 않는 모델입니다: {request.model}"
                return
            
            response_content = ""
            async for chunk in generator:
                response_content += chunk
                yield chunk
            
            # 대화가 완료된 후 컨텍스트에 저장
            if request.context_enabled:
                if request.conversation_id not in self.conversations:
                    self.conversations[request.conversation_id] = []
                self.conversations[request.conversation_id].extend([
                    {"role": "user", "content": request.question},
                    {"role": "assistant", "content": response_content}
                ])
                
        except Exception as e:
            yield f"오류가 발생했습니다: {str(e)}"