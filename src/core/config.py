from functools import lru_cache
from typing import Dict, ClassVar
from pydantic_settings import BaseSettings
import json
import os

class Settings(BaseSettings):
    """애플리케이션 기본 설정"""
    # 앱 설정
    APP_NAME: str = "Bento Chat Assistant"
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    
    # 경로 설정
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DATA_DIR: str = os.path.join(BASE_DIR, "data")
    CONFIG_DIR: str = os.path.join(BASE_DIR, "config")

class ModelSettings(BaseSettings):
    """AI 모델 관련 설정"""
    # 공통 설정
    DEFAULT_MAX_TOKENS: int = 4000
    DEFAULT_TEMPERATURE: float = 0.7
    
    # 사용 가능한 모델 목록 - ClassVar로 선언
    OPENAI_MODELS: ClassVar[Dict[str, str]] = {
        "gpt-4o": "GPT-4"
    }
    
    ANTHROPIC_MODELS: ClassVar[Dict[str, str]] = {
        "claude-3-5-sonnet-20241022": "Claude 3 Sonnet"
    }
    
    # 기본 모델 설정
    DEFAULT_OPENAI_MODEL: str = "gpt-4o"
    DEFAULT_ANTHROPIC_MODEL: str = "claude-3-5-sonnet-20241022"
    
    # 모델별 설정
    MODEL_CONFIGS: ClassVar[Dict] = {
        "gpt-4o": {},
        "claude-3-5-sonnet-20241022": {}
    }
    
    @property
    def available_models(self) -> Dict[str, str]:
        """사용 가능한 모든 모델 목록 반환"""
        return {**self.OPENAI_MODELS, **self.ANTHROPIC_MODELS}
    
    def get_model_config(self, model_name: str) -> Dict:
        """모델별 설정 반환 (기본값 + 모델별 특수 설정)"""
        base_config = {
            "max_tokens": self.DEFAULT_MAX_TOKENS,
            "temperature": self.DEFAULT_TEMPERATURE
        }
        model_specific_config = self.MODEL_CONFIGS.get(model_name, {})
        return {**base_config, **model_specific_config}
    
    def is_openai_model(self, model_name: str) -> bool:
        """OpenAI 모델인지 확인"""
        return model_name in self.OPENAI_MODELS
    
    def is_anthropic_model(self, model_name: str) -> bool:
        """Anthropic 모델인지 확인"""
        return model_name in self.ANTHROPIC_MODELS

class UIConfig:
    """UI 관련 설정"""
    def __init__(self, config_dir: str = None):
        self.config_dir = config_dir or os.path.join(Settings().BASE_DIR, "config")
        self.config_file = os.path.join(self.config_dir, "ui.json")
        self.config = self._load_config()
    
    def _load_config(self) -> dict:
        with open(self.config_file, 'r', encoding='utf-8') as f:
            return json.load(f)

@lru_cache()
def get_settings() -> Settings:
    return Settings()

@lru_cache()
def get_model_settings() -> ModelSettings:
    return ModelSettings()

@lru_cache()
def get_ui_config() -> UIConfig:
    return UIConfig()

# 전역에서 사용할 설정 인스턴스들
settings = get_settings()
model_settings = get_model_settings()
ui_config = get_ui_config()