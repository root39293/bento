from functools import lru_cache
from typing import Dict
from pydantic_settings import BaseSettings
import os
import json

def load_json_config(filename: str) -> dict:
    """JSON 설정 파일 로드"""
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'config', filename)
    print(f"설정 파일 경로: {config_path}")  # 디버깅용 로그
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            print(f"설정 파일 로드 성공: {filename}")  # 디버깅용 로그
            return config
    except Exception as e:
        print(f"설정 파일 로드 실패 ({filename}): {str(e)}")  # 디버깅용 로그
        return {}

# 설정 파일 로드
app_config_json = load_json_config('app_config.json')

class Settings(BaseSettings):
    """애플리케이션 기본 설정"""
    APP_NAME: str = app_config_json.get('app', {}).get('name', "Bento Chat Assistant")
    VERSION: str = app_config_json.get('app', {}).get('version', "0.1.0")
    ENVIRONMENT: str = app_config_json.get('app', {}).get('environment', "development")
    
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    CONFIG_DIR: str = os.path.join(BASE_DIR, "config")

class ModelSettings(BaseSettings):
    """AI 모델 관련 설정"""
    _models_config = app_config_json.get('models', {})
    _rag_config = app_config_json.get('rag', {})
    
    # 모델 설정
    OPENAI_MODELS: Dict = _models_config.get('openai', {})
    ANTHROPIC_MODELS: Dict = _models_config.get('anthropic', {})
    
    # RAG 설정
    RAG_CHUNK_SIZE: int = _rag_config.get('chunk_size', 1000)
    RAG_CHUNK_OVERLAP: int = _rag_config.get('chunk_overlap', 200)
    RAG_EMBEDDING_MODEL: str = _rag_config.get('embedding_model', 'text-embedding-3-small')
    RAG_TOP_K: int = _rag_config.get('top_k', 3)
    RAG_PERSIST_DIRECTORY: str = _rag_config.get('persist_directory', 'data/chroma')
    RAG_SIMILARITY_THRESHOLD: float = _rag_config.get('similarity_threshold', 0.7)
    RAG_SYSTEM_PROMPT_TEMPLATE: str = _rag_config.get(
        'system_prompt_template', 
        "다음 문서들을 참고하여 답변해주세요:\n\n{context}"
    )
    
    @property
    def available_models(self) -> Dict[str, str]:
        """사용 가능한 모델 목록 반환"""
        models = {}
        for model_id, config in self.OPENAI_MODELS.items():
            models[model_id] = config['name']
        for model_id, config in self.ANTHROPIC_MODELS.items():
            models[model_id] = config['name']
        return models
    
    def get_model_config(self, model_name: str) -> Dict:
        """모델별 설정 반환"""
        if self.is_openai_model(model_name):
            return self.OPENAI_MODELS[model_name]
        elif self.is_anthropic_model(model_name):
            return self.ANTHROPIC_MODELS[model_name]
        return {}
    
    def is_openai_model(self, model_name: str) -> bool:
        return model_name in self.OPENAI_MODELS
    
    def is_anthropic_model(self, model_name: str) -> bool:
        return model_name in self.ANTHROPIC_MODELS
    
    @property
    def rag_config(self) -> Dict:
        """RAG 설정 반환"""
        return {
            "chunk_size": self.RAG_CHUNK_SIZE,
            "chunk_overlap": self.RAG_CHUNK_OVERLAP,
            "embedding_model": self.RAG_EMBEDDING_MODEL,
            "top_k": self.RAG_TOP_K,
            "persist_directory": self.RAG_PERSIST_DIRECTORY,
            "similarity_threshold": self.RAG_SIMILARITY_THRESHOLD,
            "system_prompt_template": self.RAG_SYSTEM_PROMPT_TEMPLATE
        }

@lru_cache()
def get_settings() -> Settings:
    return Settings()

@lru_cache()
def get_model_settings() -> ModelSettings:
    return ModelSettings()

# 전역에서 사용할 설정 인스턴스들
settings = get_settings()
model_settings = get_model_settings()