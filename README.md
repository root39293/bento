# Bento Chat Assistant

FastAPI 기반의 로컬 실행 가능한 AI 챗봇 스타터킷입니다. OpenAI와 Anthropic의 AI 모델을 활용하여 대화형 인터페이스를 제공하며, RAG(Retrieval-Augmented Generation) 기능을 통해 사용자의 문서를 참조한 응답이 가능합니다.

## 주요 기능

- 다중 AI 모델 지원
  - OpenAI: GPT-4
  - Anthropic: Claude 3 Sonnet
- RAG(Retrieval-Augmented Generation) 지원
  - PDF, DOCX, TXT 문서 처리
  - 문서 기반 질의응답
- 실시간 스트리밍 응답
- 대화 컨텍스트 관리
- 데스크톱 애플리케이션 지원 (Windows, MacOS)

## 기술 스택

- Backend
  - FastAPI (Python 3.12)
  - ChromaDB (벡터 데이터베이스)
  - PyPDF, docx2txt (문서 처리)
- Frontend
  - Vanilla JavaScript
  - TailwindCSS
- AI/ML
  - OpenAI API (GPT-4, text-embedding-3-small)
  - Anthropic API (Claude 3)
- 개발 도구
  - Poetry (패키지 관리)
  - PyInstaller (데스크톱 앱 빌드)

## 시작하기

### 필수 요구사항

- Python 3.10 이상
- Poetry
- OpenAI API 키 (필수)
- Anthropic API 키 (선택)

### 설치 방법

1. 저장소 클론
~~~bash
git clone https://github.com/yourusername/bento-chat-assistant.git
cd bento-chat-assistant
~~~

2. Poetry 설치 (미설치 시)
~~~bash
curl -sSL https://install.python-poetry.org | python3 -
~~~

3. 의존성 설치
~~~bash
poetry install
~~~

### 실행 방법

#### 개발 서버 실행
~~~bash
poetry run uvicorn src.main:app --reload
~~~

#### 데스크톱 앱 빌드

Windows:
~~~bash
poetry run python build_win.py
~~~

MacOS:
~~~bash
poetry run python build_mac.py
~~~

빌드된 실행 파일은 `dist` 디렉토리에서 찾을 수 있습니다.

### 사용 방법

1. 웹 브라우저에서 접속 (개발 서버)
~~~
http://localhost:8000
~~~

2. API 키 설정
   - OpenAI API 키 입력 (필수)
   - Anthropic API 키 입력 (선택)

3. 대화 시작
   - 모델 선택 (GPT-4 또는 Claude 3)
   - 컨텍스트 활성화 여부 선택
   - RAG 활성화 여부 선택

4. RAG 사용 시
   - 문서 업로드 (PDF, DOCX, TXT 지원)
   - RAG 활성화 후 문서 기반 질의응답 가능

## 프로젝트 구조

~~~
bento-chat-assistant/
├── src/
│   ├── chat/           # 채팅 관련 모듈
│   ├── core/           # 핵심 설정 및 상태 관리
│   ├── rag/            # RAG 관련 모듈
│   ├── desktop.py      # 데스크톱 앱 진입점
│   └── main.py         # FastAPI 앱 진입점
├── static/             # 프론트엔드 파일
├── config/             # 설정 파일
├── data/              # 데이터 저장소
├── build_win.py       # Windows 빌드 스크립트
├── build_mac.py       # MacOS 빌드 스크립트
└── pyproject.toml     # Poetry 설정
~~~

## 환경 설정

### config/app_config.json
~~~json
{
    "app": {
        "name": "Bento Chat Assistant",
        "version": "0.1.0",
        "environment": "development"
    },
    "models": {
        "default_models": {
            "openai": "gpt-4o",
            "anthropic": "claude-3-5-sonnet-20241022"
        }
    },
    "rag": {
        "chunk_size": 1000,
        "chunk_overlap": 200,
        "embedding_model": "text-embedding-3-small",
        "top_k": 3
    }
}
~~~

## 개발 예정 기능

### 1. 문서 관리 개선
- [ ] 업로드된 문서 목록 보기
- [ ] 문서 삭제 기능
- [ ] 문서 메타데이터 관리
- [ ] 문서 처리 상태 표시

### 2. 대화 관리 강화
- [ ] 대화 내보내기 (TXT, JSON)
- [ ] 대화 제목 설정
- [ ] 대화 히스토리 브라우징
- [ ] 대화 검색 기능

### 3. 안정성 강화
- [ ] 종합적인 에러 처리
  - API 키 유효성 검증
  - 문서 업로드 제한 및 검증
  - 네트워크 오류 처리
- [ ] 로깅 시스템 구현
  - 에러 로그 관리
  - 사용자 활동 로그
  - 성능 모니터링

### 4. UI/UX 개선
- [ ] 로딩 상태 표시
- [ ] 반응형 디자인 개선
- [ ] 다크 모드 지원
- [ ] 키보드 단축키 지원

### 5. 성능 최적화
- [ ] 메모리 사용량 최적화
- [ ] 대화 컨텍스트 제한
- [ ] 문서 청크 크기 동적 조정
- [ ] 임베딩 캐싱

