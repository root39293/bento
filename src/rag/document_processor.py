import pypdf
import docx2txt
from typing import List
from io import BytesIO
from src.core.config import model_settings

class DocumentProcessor:
    @staticmethod
    def process_pdf(file_content: bytes) -> List[str]:
        pdf = pypdf.PdfReader(BytesIO(file_content))
        return [page.extract_text() for page in pdf.pages]
    
    @staticmethod
    def process_docx(file_content: bytes) -> List[str]:
        text = docx2txt.process(BytesIO(file_content))
        return [text]
    
    @staticmethod
    def process_txt(file_content: bytes) -> List[str]:
        text = file_content.decode('utf-8')
        return [text]
    
    @staticmethod
    def chunk_text(text: str, chunk_size: int = None, overlap: int = None) -> List[str]:
        if not text.strip():
            print("경고: 빈 텍스트가 입력되었습니다")
            return []
        
        chunk_size = chunk_size or model_settings.RAG_CHUNK_SIZE
        overlap = overlap or model_settings.RAG_CHUNK_OVERLAP
        
        print(f"설정값 로드됨 - 청크 크기: {chunk_size}, 오버랩: {overlap}")
        print(f"청크 분할 시작 - 텍스트 길이: {len(text)}")
        
        if len(text) <= chunk_size:
            print("텍스트가 청크 크기보다 작아 단일 청크로 반환")
            return [text]
        
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            print(f"청크 분할 진행 중: {start}/{text_length} ({(start/text_length)*100:.1f}%)")
            
            end = start + chunk_size
            if end > text_length:
                end = text_length
            
            if end < text_length:
                last_period = max(
                    text.rfind('. ', start, end),
                    text.rfind('\n', start, end)
                )
                if last_period > start:
                    end = last_period + 1
            
            current_chunk = text[start:end].strip()
            if current_chunk:
                chunks.append(current_chunk)
            
            if end == text_length:
                break
            
            start = end - overlap
            
            if start >= end:
                print("경고: 청크 분할 중 진행이 없음")
                break
        
        print(f"청크 분할 완료: 총 {len(chunks)}개의 청크 생성됨")
        return chunks