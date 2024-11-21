from typing import AsyncGenerator, Dict
from anthropic import AsyncAnthropic
from openai import AsyncOpenAI
from src.core.config import settings, model_settings
from .models import ChatRequest
from src.rag.service import RAGService

class ChatService:
    def __init__(self):
        self._openai_api_key = None
        self._anthropic_api_key = None
        self._openai_client = None
        self._anthropic_client = None
        self.conversations = {}
        self.rag_service = RAGService(openai_api_key=self.openai_api_key)
    
    @property
    def openai_api_key(self):
        return self._openai_api_key

    @openai_api_key.setter
    def openai_api_key(self, value):
        self._openai_api_key = value
        self._openai_client = AsyncOpenAI(api_key=value) if value else None
        if hasattr(self, 'rag_service'):
            self.rag_service = RAGService(openai_api_key=value)
    
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

        try:
            model_config = model_settings.get_model_config(model_name)
            
            async with self.anthropic_client.messages.stream(
                model=model_name,
                max_tokens=model_config["max_tokens"],
                temperature=model_config["temperature"],
                messages=messages
            ) as stream:
                async for text in stream.text_stream:
                    yield text
        except Exception as e:
            yield f"Anthropic 오류: {str(e)}"

    async def _generate_stream_openai(self, messages: list, model_name: str) -> AsyncGenerator[str, None]:
        if not self.openai_client:
            yield "OpenAI API 키가 설정되지 않았습니다."
            return

        try:
            model_config = model_settings.get_model_config(model_name)
            
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
            model_config = model_settings.get_model_config(request.model)
            max_tokens = model_config.get("max_tokens", 4000)
            
            # RAG가 활성화된 경우 시스템 프롬프트에 문서 컨텍스트 추가
            if request.rag_enabled:
                relevant_docs = await self.rag_service.search(
                    query=request.question,
                    top_k=min(model_settings.RAG_TOP_K, max(1, int(max_tokens/1000)))  # 토큰 제한 고려
                )
                context = "\n\n".join([f"참고 문서:\n{doc['content']}" for doc in relevant_docs])
                system_prompt = model_config["system_prompt"].format(context=context)
            else:
                system_prompt = model_config["system_prompt"].format(context="")
            
            # 통합된 시스템 프롬프트 추가
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            # 이전 컨텍스트 추가
            if request.context_enabled and request.conversation_id in self.conversations:
                messages.extend(self.conversations[request.conversation_id])
            
            # 현재 질문 추가
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
            
            if request.context_enabled:
                if request.conversation_id not in self.conversations:
                    self.conversations[request.conversation_id] = []
                    if system_prompt:
                        self.conversations[request.conversation_id].append(
                            {"role": "system", "content": system_prompt}
                        )
                self.conversations[request.conversation_id].extend([
                    {"role": "user", "content": request.question},
                    {"role": "assistant", "content": response_content}
                ])
                
        except Exception as e:
            yield f"오류가 발생했습니다: {str(e)}"