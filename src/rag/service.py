from .document_store import DocumentStore
from .document_processor import DocumentProcessor
from src.core.config import model_settings
import hashlib
from datetime import datetime

class RAGService:
    def __init__(self, openai_api_key: str = None):
        print(f"RAGService 초기화 (API 키 존재: {bool(openai_api_key)})")
        self.document_store = DocumentStore(
            persist_directory=model_settings.RAG_PERSIST_DIRECTORY,
            openai_api_key=openai_api_key
        )
        self.processor = DocumentProcessor()
        self.config = model_settings.rag_config
    
    async def add_document(self, file_content: bytes, filename: str, file_type: str):
        try:
            print(f"1. 파일 처리 시작: {filename}")
            # 파일 처리
            if file_type == "application/pdf":
                texts = self.processor.process_pdf(file_content)
            elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                texts = self.processor.process_docx(file_content)
            elif file_type == "text/plain":
                texts = self.processor.process_txt(file_content)
            else:
                raise ValueError("지원하지 않는 파일 형식입니다")
            
            print(f"2. 텍스트 추출 완료: {len(texts)} 개의 텍스트")
            
            # 청크 분할
            chunks = []
            for text in texts:
                chunks.extend(self.processor.chunk_text(text))
            
            print(f"3. 청크 분할 완료: {len(chunks)} 개의 청크")
            
            # 문서 저장
            documents = []
            ids = []
            for i, chunk in enumerate(chunks):
                doc_id = hashlib.md5(f"{filename}_{i}".encode()).hexdigest()
                documents.append({
                    "content": chunk,
                    "metadata": {
                        "source": filename,
                        "chunk_id": i,
                        "timestamp": datetime.now().isoformat()
                    }
                })
                ids.append(doc_id)
            
            print(f"4. 문서 저장 시작: {len(documents)} 개의 문서")
            await self.document_store.add_documents(documents, ids)
            print("5. 문서 저장 완료")
            
        except Exception as e:
            print(f"문서 처리 중 오류 발생: {str(e)}")
            raise
    
    async def search(self, query: str, top_k: int = None):
        if top_k is None:
            top_k = self.config["top_k"]
        return await self.document_store.search(query, top_k) 