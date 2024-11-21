from openai import AsyncOpenAI
from typing import List

class EmbeddingModel:
    def __init__(self, api_key: str = None):
        if not api_key:
            self.client = None
        else:
            self.client = AsyncOpenAI(api_key=api_key)
        self.model = "text-embedding-3-small"
    
    async def encode(self, texts: List[str]) -> List[List[float]]:
        if not self.client:
            raise ValueError("OpenAI API 키가 설정되지 않았습니다")
        if not isinstance(texts, list):
            texts = [texts]
        
        try:
            print(f"임베딩 생성 시작: {len(texts)} 개의 텍스트")
            response = await self.client.embeddings.create(
                model=self.model,
                input=texts
            )
            print("임베딩 생성 완료")
            return [embedding.embedding for embedding in response.data]
        except Exception as e:
            print(f"임베딩 생성 중 오류 발생: {str(e)}")
            raise 