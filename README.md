# Bento Chat Assistant

FastAPI 기반 AI 챗봇 스타터킷

## 기술 스택

- Backend: FastAPI (Python 3.12)
- Frontend: Vanilla JavaScript, TailwindCSS
- AI: OpenAI API, Anthropic API
- Package Manager: Poetry

## 시작하기

의존성 설치
~~~bash
poetry install
~~~

서버 실행
~~~bash
poetry run uvicorn src.main:app --reload
~~~

브라우저에서 접속
~~~
http://localhost:8000
~~~

## TODO 목록

### 1. 필수 기능 개선
- [ ] 문서 관리 기본 기능
  - 업로드된 문서 목록 보기
  - 문서 삭제 기능
  - 간단한 문서 설명 추가 기능
- [ ] 대화 관리 필수 기능
  - 대화 내보내기 (TXT 형식)
  - 대화 제목 설정

### 2. 안정성 강화
- [ ] 기본적인 에러 처리
  - 사용자가 이해하기 쉬운 에러 메시지
  - API 키 만료/오류 처리
  - 문서 업로드 실패 처리
- [ ] 간단한 로깅 시스템
  - 기본적인 에러 로깅
  - 중요 작업 로깅

### 3. 사용자 경험
- [ ] 로딩 상태 표시
  - 문서 처리중 표시
  - 대화 생성중 표시
- [ ] 간단한 설정 기능
  - 모델 선택 UI 개선
  - 기본 청크 사이즈 조절

### 4. 문서화
- [ ] 기본 사용 설명서
  - 설치 가이드 보완
  - 주요 기능 사용법
  - 자주 발생하는 문제 해결 가이드

### 5. 성능 관련
- [ ] 기본적인 메모리 관리
  - 대화 히스토리 제한
  - 문서 크기 제한