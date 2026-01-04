# 프로젝트 라이브러리 및 의존성 정보

## 개요
이 문서는 웹 보안 스캐너 프로젝트에서 사용되는 모든 라이브러리와 의존성 정보를 정리한 것입니다.

---

## 1. 외부 라이브러리 (설치 필요)

### 1.1 HTTP 요청 및 웹 크롤링

#### requests (v2.32.5)
- **설치**: `pip install requests==2.32.5`
- **용도**: HTTP 요청, 세션 관리, 쿠키 처리
- **사용 파일**:
  - `A01/A01_CSRF.py` - CSRF 토큰 검사
  - `A02/A02_check_https.py` - HTTPS 보안 검사
  - `A05/A05_default.py` - 기본 설정 검사
  - `A06/A06_vulnerabilityLibrary.py` - 취약한 라이브러리 검사
  - `A07/A07_session_check.py` - 세션 관리 검사
- **주요 기능**: `requests.get()`, `requests.post()`, `requests.Session()`

#### aiohttp (v3.11.18)
- **설치**: `pip install aiohttp==3.11.18`
- **용도**: 비동기 HTTP 클라이언트/서버
- **사용 파일**:
  - `A04/A04_Rate_Limit.py` - Rate Limiting 검사
- **주요 기능**: 비동기 요청으로 대량 HTTP 요청 처리

#### playwright (v1.55.0)
- **설치**:
  ```bash
  pip install playwright==1.55.0
  playwright install chromium
  ```
- **용도**: 브라우저 자동화, 동적 웹페이지 크롤링
- **사용 파일**:
  - `add_in/crawl2.py` - 웹 크롤링
- **주요 기능**: JavaScript 렌더링, SPA 크롤링, 스크린샷

#### requests-html (v0.10.0)
- **설치**: `pip install requests-html==0.10.0`
- **용도**: HTML 렌더링이 포함된 HTTP 요청
- **주요 기능**: JavaScript 실행 지원

### 1.2 HTML/XML 파싱

#### beautifulsoup4 (v4.13.3)
- **설치**: `pip install beautifulsoup4==4.13.3`
- **용도**: HTML/XML 문서 파싱 및 데이터 추출
- **사용 파일**:
  - `A01/A01_CSRF.py` - HTML 폼 파싱, CSRF 토큰 추출
  - `A02/A02_check_https.py` - 링크 및 리소스 추출
  - `A05/A05_default.py` - 보안 헤더 검사
  - `add_in/crawl2.py` - 웹페이지 구조 분석
- **주요 기능**: `BeautifulSoup()`, `find()`, `find_all()`, `select()`

#### bs4 (v0.0.2)
- **용도**: beautifulsoup4의 wrapper 패키지

### 1.3 SSL/TLS 및 암호화

#### pyOpenSSL (v25.1.0)
- **설치**: `pip install pyOpenSSL==25.1.0`
- **용도**: SSL/TLS 연결, 인증서 검증, 암호화 프로토콜 검사
- **사용 파일**:
  - `A02/A02_check_https.py` - SSL/TLS 보안 검사
- **주요 기능**:
  - SSL 연결 생성 및 검증
  - 인증서 체인 검사
  - 암호화 알고리즘 확인
  - TLS 버전 검사

### 1.4 GUI 프레임워크

#### tkinter
- **설치**: Python 표준 라이브러리 (일부 시스템에서 별도 설치 필요)
  - **Linux**: `sudo apt-get install python3-tk`
  - **macOS**: 기본 포함
  - **Windows**: 기본 포함
- **용도**: GUI 인터페이스 구축
- **사용 파일**:
  - `gui/main_window.py` - 메인 윈도우
  - `gui/views/*.py` - 모든 뷰 컴포넌트
  - `gui/controllers/*.py` - 컨트롤러
- **주요 기능**: 윈도우, 버튼, 레이블, 텍스트박스 등 GUI 요소

---

## 2. Python 표준 라이브러리 (설치 불필요)

### 2.1 네트워크 및 웹
- **socket** - 저수준 네트워크 인터페이스
- **urllib.parse** - URL 파싱 및 조작
- **http.cookies** - HTTP 쿠키 처리

### 2.2 데이터 처리
- **json** - JSON 인코딩/디코딩
- **csv** - CSV 파일 처리
- **re** - 정규표현식
- **dataclasses** - 데이터 클래스 (Python 3.7+)

### 2.3 시스템 및 파일
- **os** - 운영체제 인터페이스
- **sys** - 시스템 파라미터 및 함수
- **pathlib** - 객체 지향 파일 경로

### 2.4 비동기 및 동시성
- **asyncio** - 비동기 I/O 프레임워크
- **threading** - 스레드 기반 병렬 처리

### 2.5 유틸리티
- **datetime** - 날짜 및 시간 처리
- **time** - 시간 관련 함수
- **logging** - 로깅 시스템
- **argparse** - 커맨드라인 인자 파싱
- **typing** - 타입 힌트

---

## 3. 프로젝트 내부 모듈

### 3.1 보안 검사 모듈 (OWASP Top 10)
- **A01** - Broken Access Control (CSRF 검사)
  - `A01_CSRF.py` - CSRF 토큰 검증
  - `A01_integration.py` - 통합 테스트

- **A02** - Cryptographic Failures
  - `A02_check_https.py` - HTTPS 보안 검사
  - `A02_check_cryptographic.py` - 암호화 검사
  - `A02_integration.py` - 통합 테스트

- **A03** - Injection
  - `A03_Injection.py` - 일반 인젝션 검사
  - `A03_sqli.py` - SQL 인젝션 검사
  - `A03_xss.py` - XSS 검사
  - `A03_integration.py` - 통합 테스트

- **A04** - Insecure Design
  - `A04_Rate_Limit.py` - Rate Limiting 검사
  - `A04_Insufficien_access_control.py` - 접근 제어 검사
  - `A04_Permission_bypass.py` - 권한 우회 검사
  - `A04_integration.py` - 통합 테스트

- **A05** - Security Misconfiguration
  - `A05_Port_Security.py` - 포트 보안 검사
  - `A05_default.py` - 기본 설정 검사
  - `A05_check_vulnerable.py` - 취약한 설정 검사
  - `A05_integration.py` - 통합 테스트

- **A06** - Vulnerable and Outdated Components
  - `A06_vulnerabilityLibrary.py` - 취약한 라이브러리 검사
  - `DependencyfilesParser.py` - 의존성 파일 파싱
  - `A06_integration.py` - 통합 테스트

- **A07** - Identification and Authentication Failures
  - `A07_session_check.py` - 세션 관리 검사
  - `A07_integration.py` - 통합 테스트

- **A09** - Security Logging and Monitoring Failures
- **A10** - Server-Side Request Forgery (SSRF)
  - `ProtocolHandler.py` - 프로토콜 핸들러
  - `ssrf.py` - SSRF 검사

### 3.2 GUI 모듈
- **gui/main_window.py** - 메인 윈도우
- **gui/report_generator.py** - 리포트 생성
- **gui/views/** - 뷰 컴포넌트
  - `results_view.py` - 결과 화면
  - `dast_view.py` - DAST 스캔 화면
  - `add_view.py` - 추가 기능 화면
  - `settings_manager.py` - 설정 관리
- **gui/controllers/** - 컨트롤러
  - `scan_controller.py` - 스캔 제어
  - `results_controller.py` - 결과 제어
  - `add_controller.py` - 추가 기능 제어
  - `config_manager.py` - 설정 관리
- **gui/components/** - UI 컴포넌트
  - `ui_components.py` - 재사용 가능한 UI 요소
- **gui/utils/** - 유틸리티
  - `utils.py` - 일반 유틸리티
  - `format_utils.py` - 포맷 유틸리티

### 3.3 추가 기능 모듈
- **add_in/crawl2.py** - 고급 웹 크롤링
- **add_in/data_management.py** - 데이터 관리

### 3.4 테스트 및 유틸리티
- **test/** - 테스트 파일들
- **main_test.py** - 메인 테스트 스크립트
- **run_monitor.py** - 모니터링 실행 스크립트

---

## 4. 설치 가이드

### 4.1 전체 설치
```bash
# 1. 프로젝트 클론 또는 다운로드
cd /home/ruqos/Desktop/project

# 2. 가상환경 생성 (선택사항이지만 권장)
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate  # Windows

# 3. 필수 라이브러리 설치
pip install -r requirements.txt

# 4. Playwright 브라우저 설치
playwright install chromium

# 5. tkinter 설치 (Linux만 해당)
sudo apt-get install python3-tk
```

### 4.2 개별 설치
```bash
pip install requests==2.32.5
pip install aiohttp==3.11.18
pip install beautifulsoup4==4.13.3
pip install pyOpenSSL==25.1.0
pip install playwright==1.55.0
playwright install chromium
```

### 4.3 설치 확인
```bash
# Python 버전 확인 (3.7 이상 권장)
python --version

# 설치된 패키지 확인
pip list

# 특정 라이브러리 버전 확인
pip show requests beautifulsoup4 playwright aiohttp pyOpenSSL
```

---

## 5. 라이브러리별 사용 통계

| 라이브러리 | 사용 파일 수 | 주요 용도 | 중요도 |
|-----------|------------|---------|--------|
| requests | 5+ | HTTP 요청, 세션 관리 | 필수 |
| beautifulsoup4 | 4+ | HTML 파싱 | 필수 |
| pyOpenSSL | 1 | SSL/TLS 검사 | 필수 |
| playwright | 1 | 동적 크롤링 | 중요 |
| aiohttp | 1 | 비동기 요청 | 중요 |
| tkinter | 10+ | GUI | 필수 (GUI 사용시) |

---

## 6. 버전 호환성

### Python 버전
- **최소**: Python 3.7
- **권장**: Python 3.10 이상
- **이유**: dataclasses, typing 기능 사용

### 운영체제
- **Linux**: 완전 지원 (Ubuntu 20.04+, Debian 10+ 테스트됨)
- **macOS**: 완전 지원
- **Windows**: 지원 (일부 경로 관련 수정 필요할 수 있음)

---

## 7. 문제 해결

### tkinter 설치 오류
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# Fedora
sudo dnf install python3-tkinter

# macOS (Homebrew)
brew install python-tk
```

### Playwright 브라우저 다운로드 실패
```bash
# 프록시 환경에서
HTTPS_PROXY=http://proxy:port playwright install chromium

# 수동 설치
python -m playwright install chromium
```

### SSL 인증서 오류
```bash
# 인증서 업데이트
pip install --upgrade certifi
```

---

## 8. 라이선스 정보

| 라이브러리 | 라이선스 |
|-----------|---------|
| requests | Apache 2.0 |
| aiohttp | Apache 2.0 |
| beautifulsoup4 | MIT |
| playwright | Apache 2.0 |
| pyOpenSSL | Apache 2.0 |

---

## 9. 업데이트 이력

- **2025-11-03**: 초기 문서 생성
  - requests 2.32.5
  - aiohttp 3.11.18
  - beautifulsoup4 4.13.3
  - playwright 1.55.0
  - pyOpenSSL 25.1.0

---

## 10. 참고 자료

- [requests 문서](https://requests.readthedocs.io/)
- [aiohttp 문서](https://docs.aiohttp.org/)
- [Beautiful Soup 문서](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Playwright Python 문서](https://playwright.dev/python/)
- [pyOpenSSL 문서](https://www.pyopenssl.org/)
