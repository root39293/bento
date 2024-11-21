from fastapi import APIRouter, HTTPException, File, UploadFile, Depends
from .service import RAGService
from .models import SearchRequest, SearchResult
from typing import List

router = APIRouter(prefix="/documents", tags=["documents"])

def get_rag_service():
    """RAG 서비스 의존성 주입을 위한 함수"""
    return RAGService()

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    rag_service: RAGService = Depends(get_rag_service)
):
    try:
        print(f"파일 업로드 시도: {file.filename}, 타입: {file.content_type}")
        
        if not file.content_type in ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "text/plain"]:
            raise HTTPException(status_code=400, detail="지원하지 않는 파일 형식입니다")
        
        content = await file.read()
        print(f"파일 크기: {len(content)} bytes")
        
        await rag_service.add_document(
            file_content=content,
            filename=file.filename,
            file_type=file.content_type
        )
        print(f"파일 처리 완료: {file.filename}")
        
        return {"message": "문서가 성공적으로 업로드되었습니다"}
    except Exception as e:
        print(f"업로드 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search", response_model=List[SearchResult])
async def search_documents(
    request: SearchRequest,
    rag_service: RAGService = Depends(get_rag_service)
):
    """문서 검색 엔드포인트"""
    try:
        results = await rag_service.search(query=request.query, top_k=request.top_k)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 