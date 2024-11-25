import chromadb
from chromadb.config import Settings
import os
from .embeddings import EmbeddingModel
from typing import List, Dict
from .models import SearchResult

class DocumentStore:
    def __init__(self, persist_directory: str = "data/chroma", openai_api_key: str = None):
        print(f"DocumentStore 초기화: {persist_directory}")
        os.makedirs(persist_directory, exist_ok=True)
        self.client = chromadb.PersistentClient(path=persist_directory)
        self._embedding_model = None
        self._openai_api_key = openai_api_key
        self._collection = None
    
    @property
    def embedding_model(self):
        if self._embedding_model is None:
            print(f"임베딩 모델 초기화 (API 키 존재: {bool(self._openai_api_key)})")
            self._embedding_model = EmbeddingModel(api_key=self._openai_api_key)
        return self._embedding_model

    @property
    def collection(self):
        if self._collection is None:
            print("Chroma 컬렉션 초기화")
            self._collection = self.client.get_or_create_collection(
                name="documents",
                metadata={"hnsw:space": "cosine"}
            )
        return self._collection

    async def add_documents(self, documents: List[Dict], ids: List[str]):
        print(f"문서 추가 시작: {len(documents)}개")
        if not self._openai_api_key:
            raise ValueError("OpenAI API 키가 설정되지 않았습니다")
        
        texts = [doc["content"] for doc in documents]
        metadatas = [doc["metadata"] for doc in documents]
        
        try:
            # 임베딩 생성
            print("임베딩 생성 시작")
            embeddings = await self.embedding_model.encode(texts)
            print("임베딩 생성 완료")
            
            # 문서 추가
            print("Chroma에 문서 추가 시작")
            self.collection.add(
                documents=texts,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            print("Chroma에 문서 추가 완료")
        except Exception as e:
            print(f"문서 추가 중 오류 발생: {str(e)}")
            raise
    
    async def search(self, query: str, top_k: int = 3) -> List[SearchResult]:
        query_embedding = await self.embedding_model.encode([query])
        
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=top_k
        )
        
        return [
            {
                "content": doc,
                "metadata": metadata,
                "score": float(score)
            }
            for doc, metadata, score in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0]
            )
        ] 

    async def get_documents(self):
        """저장된 모든 문서 메타데이터 조회"""
        try:
            if not self._collection:
                print("컬렉션이 초기화되지 않았습니다")
                self._collection = self.client.get_or_create_collection(
                    name="documents",
                    metadata={"hnsw:space": "cosine"}
                )
            
            results = self._collection.get()
            print(f"조회된 문서 수: {len(results['ids']) if results.get('ids') else 0}")
            
            if not results or not results.get('ids'):
                print("저장된 문서가 없습니다")
                return []
            
            documents = []
            for i in range(len(results['ids'])):
                documents.append({
                    'id': results['ids'][i],
                    'metadata': results['metadatas'][i],
                    'content': results['documents'][i]
                })
            return documents
        except Exception as e:
            print(f"문서 조회 중 오류 발생: {str(e)}")
            return []  # 에러 발생시 빈 리스트 반환 