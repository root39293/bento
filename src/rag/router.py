from fastapi import APIRouter, HTTPException, File, UploadFile, Depends
from .service import RAGService
from .models import SearchRequest, SearchResult, UpdateDocumentRequest
from typing import List
from src.core.state import chat_service

router = APIRouter(prefix="/documents", tags=["documents"])

def get_rag_service(require_api_key: bool = True):
    """RAG 서비스 의존성 주입을 위한 함수"""
    def _get_service():
        if require_api_key and not chat_service.openai_api_key:
            raise HTTPException(status_code=400, detail="OpenAI API 키가 설정되지 않았습니다")
        return RAGService(openai_api_key=chat_service.openai_api_key)
    return _get_service

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    rag_service: RAGService = Depends(get_rag_service(require_api_key=True))
):
    try:
        if not rag_service.document_store._openai_api_key:
            raise HTTPException(status_code=400, detail="OpenAI API 키가 설정되지 않았습니다")
            
        print(f"파일 업로드 시도: {file.filename}, 타입: {file.content_type}")
        
        if not file.content_type in ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "text/plain"]:
            raise HTTPException(status_code=400, detail="지원하지 않는 파일 형식입니다")
        
        content = await file.read()
        print(f"파일 크기: {len(content)} bytes")
        
        try:
            await rag_service.add_document(
                file_content=content,
                filename=file.filename,
                file_type=file.content_type
            )
            print(f"파일 처리 완료: {file.filename}")
            return {"message": "문서가 성공적으로 업로드되었습니다"}
        except Exception as e:
            print(f"문서 처리 중 오류: {str(e)}")
            raise HTTPException(status_code=500, detail=f"문서 처리 중 오류: {str(e)}")
            
    except Exception as e:
        print(f"업로드 오류: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search", response_model=List[SearchResult])
async def search_documents(
    request: SearchRequest,
    rag_service: RAGService = Depends(get_rag_service(require_api_key=True))
):
    """문서 검색 엔드포인트"""
    try:
        results = await rag_service.search(query=request.query, top_k=request.top_k)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list")
async def list_documents(
    rag_service: RAGService = Depends(get_rag_service(require_api_key=False))
):
    """저장된 문서 목록 조회"""
    try:
        documents = await rag_service.list_documents()
        print(f"문서 목록 조회 결과: {len(documents)}개")
        return {"documents": documents, "count": len(documents)}
    except Exception as e:
        print(f"문서 목록 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"문서 목록 조회 중 오류가 발생했습니다: {str(e)}"
        )

@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    rag_service: RAGService = Depends(get_rag_service(require_api_key=False))
):
    """문서 삭제"""
    try:
        success = await rag_service.delete_document(document_id)
        if success:
            return {"message": "문서가 성공적으로 삭제되었습니다"}
        raise HTTPException(status_code=404, detail="문서를 찾을 수 없습니다")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{document_id}")
async def update_document_metadata(
    document_id: str,
    updates: UpdateDocumentRequest,
    rag_service: RAGService = Depends(get_rag_service(require_api_key=False))
):
    """문서 메타데이터 업데이트"""
    try:
        success = await rag_service.update_document_metadata(
            document_id,
            updates.dict(exclude_unset=True)
        )
        if success:
            return {"message": "문서 메타데이터가 업데이트되었습니다"}
        raise HTTPException(status_code=404, detail="문서를 찾을 수 없습니다")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 