from .document_store import DocumentStore
from .document_processor import DocumentProcessor
from src.core.config import model_settings
import hashlib
from datetime import datetime
from typing import List, Dict

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
            
            # 현재 타임스탬프를 문서 ID에 포함
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            base_doc_id = f"{filename}_{timestamp}"
            
            # 문서 저장
            documents = []
            ids = []
            for i, chunk in enumerate(chunks):
                # 타임스탬프가 포함된 고유한 ID 생성
                doc_id = hashlib.md5(f"{base_doc_id}_{i}".encode()).hexdigest()
                documents.append({
                    "content": chunk,
                    "metadata": {
                        "source": filename,
                        "chunk_id": i,
                        "timestamp": datetime.now().isoformat(),
                        "status": "completed",
                        "category": "",
                        "description": "",
                        "tags": ""
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

    async def get_documents(self) -> List[Dict]:
        """저장된 모든 문서의 메타데이터 조회 - 원본 문서별로 그룹화"""
        try:
            if not self.document_store._openai_api_key:
                print("API 키가 설정되지 않아 빈 목록을 반환합니다.")
                return []
            
            if not self.document_store.collection:
                print("문서 컬렉션이 초기화되지 않았습니다.")
                return []
            
            results = self.document_store.collection.get()
            if not results or not results.get('ids'):
                print("저장된 문서가 없습니다.")
                return []
            
            # 원본 문서별로 청크를 그룹화
            documents_by_source = {}
            for i, metadata in enumerate(results['metadatas']):
                source = metadata['source']
                if source not in documents_by_source:
                    documents_by_source[source] = {
                        'source': source,
                        'timestamp': metadata['timestamp'],
                        'status': metadata['status'],
                        'category': metadata.get('category', ''),
                        'description': metadata.get('description', ''),
                        'tags': metadata.get('tags', ''),
                        'chunks': []
                    }
                
                documents_by_source[source]['chunks'].append({
                    'id': results['ids'][i],
                    'chunk_id': metadata['chunk_id'],
                    'content': results['documents'][i],
                    'metadata': metadata
                })
            
            # 청크 ID로 정렬하여 반환
            return [
                {
                    'id': list(doc['chunks'])[0]['id'],  # 첫 번째 청크의 ID를 문서 ID로 사용
                    'metadata': {
                        'source': doc['source'],
                        'timestamp': doc['timestamp'],
                        'status': doc['status'],
                        'category': doc['category'],
                        'description': doc['description'],
                        'tags': doc['tags']
                    },
                    'chunks': sorted(doc['chunks'], key=lambda x: x['chunk_id'])
                }
                for doc in documents_by_source.values()
            ]
            
        except Exception as e:
            print(f"문서 조회 중 오류: {str(e)}")
            return []

    async def delete_document(self, document_id: str) -> bool:
        """문서 삭제 - 관련된 모든 청크 삭제"""
        try:
            # 먼저 해당 문서의 정보를 가져옴
            results = self.document_store.collection.get(ids=[document_id])
            if not results['ids']:
                return False
            
            # 원본 파일명 확인
            source_file = results['metadatas'][0]['source']
            print(f"삭제 시작: 문서 '{source_file}'")
            
            # 같은 원본 파일을 가진 모든 청크 검색
            all_results = self.document_store.collection.get()
            chunk_ids_to_delete = []
            
            for i, metadata in enumerate(all_results['metadatas']):
                if metadata['source'] == source_file:
                    chunk_ids_to_delete.append(all_results['ids'][i])
            
            # 모든 관련 청크 삭제
            if chunk_ids_to_delete:
                print(f"삭제할 청크 수: {len(chunk_ids_to_delete)}")
                self.document_store.collection.delete(ids=chunk_ids_to_delete)
                
                # 삭제 확인
                remaining = self.document_store.collection.get(
                    ids=chunk_ids_to_delete
                )
                if not remaining['ids']:
                    print(f"문서 '{source_file}'의 모든 청크가 성공적으로 삭제되었습니다.")
                else:
                    print(f"경고: {len(remaining['ids'])}개의 청크가 삭제되지 않았습니다.")
            
            return True
        except Exception as e:
            print(f"문서 삭제 중 오류: {str(e)}")
            raise

    async def update_document_metadata(self, document_id: str, updates: dict) -> bool:
        """문서 메타데이터 업데이트"""
        try:
            # 현재 문서 정보 조회
            results = self.document_store.collection.get(ids=[document_id])
            if not results['ids']:
                return False
            
            # 현재 메타데이터 가져오기
            current_metadata = results['metadatas'][0]
            
            # 업데이트할 필드만 갱신
            for key, value in updates.items():
                if value is not None:
                    if key == 'tags':
                        # 태그 리스트를 쉼표로 구분된 문자열로 변환
                        current_metadata[key] = ','.join(value) if value else ''
                    else:
                        current_metadata[key] = value
            
            # 메타데이터 업데이트
            self.document_store.collection.update(
                ids=[document_id],
                metadatas=[current_metadata]
            )
            return True
        except Exception as e:
            print(f"메타데이터 업데이트 중 오류: {str(e)}")
            raise