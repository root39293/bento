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
        if chunk_size is None:
            chunk_size = model_settings.RAG_CHUNK_SIZE
        if overlap is None:
            overlap = model_settings.RAG_CHUNK_OVERLAP
        
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + chunk_size
            if end > text_length:
                end = text_length
            chunks.append(text[start:end])
            start = end - overlap
            
        return chunks