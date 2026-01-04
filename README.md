# 🛡️ OWASP Top 10 기반 웹 보안 취약점 스캐너

OWASP Top 10을 기반으로 한 자동화된 웹 애플리케이션 보안 취약점 검사 도구입니다.

## 📋 목차

- [주요 기능](#주요-기능)
- [지원하는 취약점](#지원하는-취약점)
- [시스템 요구사항](#시스템-요구사항)
- [설치 방법](#설치-방법)
- [사용 방법](#사용-방법)
- [프로젝트 구조](#프로젝트-구조)
- [문제 해결](#문제-해결)

## ✨ 주요 기능

### 🖥️ 직관적인 GUI 인터페이스
- Tkinter 기반의 사용자 친화적인 그래픽 인터페이스
- 실시간 검사 진행 상황 모니터링
- 취약점 결과 시각화 및 필터링

### 📊 포괄적인 보안 검사
- OWASP Top 10 기반 자동화된 취약점 검사
- 정적 코드 분석 (SAST)
- 동적 웹 애플리케이션 검사 (DAST)
- 의존성 라이브러리 취약점 검사

### 📄 상세한 보고서 생성
- HTML 형식의 전문적인 보안 보고서
- 취약점별 상세 설명 및 해결 방안 제공
- 위험도 분류 (CRITICAL, HIGH, MEDIUM, LOW, INFO)

### 🔍 자동 크롤링 및 파일 수집
- 웹 애플리케이션 자동 크롤링
- 소스 코드 파일 자동 수집
- 의존성 파일 자동 분석

## 🎯 지원하는 취약점

### A01: Broken Access Control (접근 제어 취약점)
- ✅ CSRF (Cross-Site Request Forgery) 검사
- ✅ 수직적 권한 우회 검사

### A02: Cryptographic Failures (암호화 실패)
- ✅ 약한 암호화 알고리즘 검사
- ✅ SSL/TLS 보안 설정 검증
- ✅ HTTPS 사용 여부 확인

### A03: Injection (인젝션)
- ✅ SQL Injection 검사
- ✅ Command Injection 검사
- ✅ XSS (Cross-Site Scripting) 검사

### A04: Insecure Design (안전하지 않은 설계)
- ✅ Rate Limiting 부재 검사
- ✅ 파일 시스템 접근 제어 검사
- ✅ 권한 우회 취약점 검사

### A05: Security Misconfiguration (보안 설정 오류)
- ✅ 보안 헤더 누락 검사
- ✅ 디렉토리 리스팅 활성화 검사
- ✅ 포트 보안 설정 검사

### A06: Vulnerable and Outdated Components (취약한 컴포넌트)
- ✅ 취약한 라이브러리/의존성 검사
- ✅ npm, pip, composer 패키지 취약점 검사
- ✅ OSV (Open Source Vulnerabilities) 데이터베이스 연동

### A07: Identification and Authentication Failures (인증 실패)
- ✅ 세션 관리 취약점 검사
- ✅ Session Hijacking 검사

## 💻 시스템 요구사항

### 운영 체제
- Linux (Ubuntu 20.04 이상 권장)

### Python
- Python 3.8 이상 (Python 3.10 권장)

### 필수 패키지
- Tkinter (GUI)
- requests (HTTP 요청)
- aiohttp (비동기 HTTP)
- BeautifulSoup4 (HTML 파싱)
- Playwright (브라우저 자동화)
- pyOpenSSL (SSL/TLS 검증)

## 🚀 설치 방법

### 1. 저장소 클론

```bash
git clone https://github.com/yourusername/OWASP_TOP_10_base_scanner.git
cd OWASP_TOP_10_base_scanner
```

### 2. Python 가상 환경 생성 (권장)

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# 또는
venv\Scripts\activate  # Windows
```

### 3. 의존성 설치

```bash
pip install -r requirements.txt
```

### 4. Playwright 브라우저 설치

```bash
playwright install chromium
```

### 5. 설정 파일 준비

프로젝트 루트에 `etc` 디렉토리가 자동으로 생성되며, 필요한 설정 파일들이 초기화됩니다.

## 📖 사용 방법

### GUI 모드 (권장)

```bash
python3 test_gui_safe.py
```

#### 사용 단계:

1. **설정 탭에서 대상 URL 입력**
   - 검사할 웹 애플리케이션 URL 입력
   - 로그인이 필요한 경우 인증 정보 입력

2. **프로젝트 폴더 선택**
   - "폴더 선택" 버튼으로 소스 코드 위치 지정
   - 자동으로 파일 수집 및 분석 시작

3. **검사 실행**
   - "검사" 탭에서 검사할 항목 선택
   - "검사 시작" 버튼 클릭

4. **결과 확인**
   - "결과" 탭에서 발견된 취약점 확인
   - 취약점 클릭 시 상세 정보 표시
   - "보고서 생성" 버튼으로 HTML 보고서 생성

### CLI 모드

```bash
python3 main_test.py --project-path /path/to/your/project
```

#### CLI 옵션:

```bash
# 프로젝트 경로 지정
python3 main_test.py --project-path /var/www/html

# 특정 검사만 실행
python3 main_test.py --tests A01,A03,A06

# 보고서 생성
python3 main_test.py --generate-report
```

## 📁 프로젝트 구조

```
OWASP_TOP_10_base_scanner/
├── A01/                    # A01 검사 모듈
│   ├── A01_CSRF.py        # CSRF 검사
│   └── A01_integration.py # A01 통합 모듈
├── A02/                    # A02 검사 모듈
│   ├── A02_check_cryptographic.py
│   ├── A02_check_https.py
│   └── A02_integration.py
├── A03/                    # A03 검사 모듈
│   ├── A03_sqli.py        # SQL Injection
│   ├── A03_xss.py         # XSS
│   ├── A03_Injection.py   # Command Injection
│   └── A03_integration.py
├── A04/                    # A04 검사 모듈
│   ├── A04_Rate_Limit.py
│   ├── A04_Permission_bypass.py
│   ├── A04_Insufficien_access_control.py
│   └── A04_integration.py
├── A05/                    # A05 검사 모듈
│   ├── A05_check_vulnerable.py
│   ├── A05_default.py
│   ├── A05_Port_Security.py
│   └── A05_integration.py
├── A06/                    # A06 검사 모듈
│   ├── A06_vulnerabilityLibrary.py
│   ├── DependencyfilesParser.py
│   └── A06_integration.py
├── A07/                    # A07 검사 모듈
│   ├── A07_session_check.py
│   └── A07_integration.py
├── gui/                    # GUI 모듈
│   ├── main_window.py     # 메인 윈도우
│   ├── report_generator.py # 보고서 생성기
│   ├── views/             # 뷰 컴포넌트
│   │   ├── dast_view.py
│   │   ├── results_view.py
│   │   └── settings_view.py
│   └── controllers/       # 컨트롤러
│       ├── dast_controller.py
│       └── results_controller.py
├── add_in/                 # 유틸리티 모듈
│   ├── crawl2.py          # 웹 크롤러
│   └── data_management.py # 파일 수집
├── etc/                    # 설정 파일
│   ├── user_info.json     # 사용자 설정
│   └── results.json       # 검사 결과
├── report/                 # HTML 보고서 저장
├── results/                # 검사 결과 저장
├── main_test.py           # CLI 실행 파일
├── test_gui_safe.py       # GUI 실행 파일
├── requirements.txt       # Python 의존성
├── README.md              # 이 파일
├── SEGFAULT_FIX.md        # 세그먼트 오류 해결 문서
└── LIBRARIES.md           # 라이브러리 정보
```

## 🔧 설정 파일

### etc/user_info.json

```json
{
  "URL": "http://example.com",
  "ID": "",
  "PW": "",
  "Web_Dir": "/path/to/project",
  "Port": 80
}
```

#### 설정 항목:
- **URL**: 검사 대상 웹 애플리케이션 URL
- **ID**: 로그인 ID (필요한 경우)
- **PW**: 로그인 비밀번호 (필요한 경우)
- **Web_Dir**: 소스 코드 프로젝트 경로
- **Port**: 검사 대상 포트 (기본값: 80)

## 📊 보고서 생성

검사 완료 후 HTML 형식의 상세 보고서가 `report/` 디렉토리에 생성됩니다.

### 보고서 내용:
- ✅ 요약 대시보드 (총 취약점 개수, 위험도별 분류)
- ✅ 취약점 상세 정보 (위치, 설명, 해결 방안)
- ✅ CWE 매핑 및 참고 자료 링크
- ✅ 인터랙티브 UI (클릭하여 상세 정보 펼치기/접기)

### 보고서 예시:

```
보안 취약점 검사 보고서
검사 일시: 2025-11-03 13:55:23

검사 요약
├── 총 취약점: 42개
├── CRITICAL: 5개
├── HIGH: 12개
├── MEDIUM: 18개
└── LOW: 7개

상세 취약점 정보
A01: Broken Access Control
  ├── CSRF (Cross-Site Request Forgery) 취약점
  │   ├── 위험도: HIGH
  │   ├── 발견된 인스턴스: 3개
  │   └── 위치: /login.php, /admin/update.php, ...
  ...
```

## 🐛 문제 해결

### 자주 발생하는 문제

#### 1. Segmentation Fault (세그먼트 오류)

대량의 취약점 데이터를 로드할 때 발생할 수 있습니다.

**해결 방법:**
- 최신 버전 사용 (이미 수정됨)
- 자세한 내용은 [SEGFAULT_FIX.md](SEGFAULT_FIX.md) 참조

#### 2. Playwright 브라우저 실행 오류

```
Error: browserType.launch: Executable doesn't exist
```

**해결 방법:**
```bash
playwright install chromium
```

#### 3. Tkinter 설치 오류 (Linux)

```
ModuleNotFoundError: No module named '_tkinter'
```

**해결 방법:**
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# Fedora/RHEL
sudo dnf install python3-tkinter
```

#### 4. 권한 오류

```
PermissionError: [Errno 13] Permission denied
```

**해결 방법:**
```bash
# 폴더 권한 확인
chmod 755 /path/to/project

# 실행 권한 부여
chmod +x test_gui_safe.py
```

#### 5. 메모리 부족 오류

대량의 취약점 발견 시 메모리 부족 오류가 발생할 수 있습니다.

**해결 방법:**
- GUI에서는 최대 1000개 항목만 표시됩니다
- 전체 데이터는 "보고서 생성" 기능 사용
- 필터 기능으로 특정 카테고리만 확인

### 디버그 모드

```bash
# 상세 로그 출력
python3 -u test_gui_safe.py 2>&1 | tee debug.log

# GDB 디버깅 (크래시 발생 시)
gdb python3
(gdb) run test_gui_safe.py
(gdb) bt  # 백트레이스 확인
```

### 데이터 보안:

- 검사 결과 파일(`etc/results.json`)에 민감한 정보 포함 가능
- 보고서 파일 공유 시 민감 정보 제거 필수
- 로그인 정보는 암호화하여 저장 권장

## 📝 변경 로그

### v1.1.0 (2025-11-03)
- ✅ GUI 메모리 누수 및 세그먼트 오류 수정
- ✅ 대량 데이터 처리 안정성 개선
- ✅ 배치 처리 및 메모리 보호 기능 추가
- ✅ HTML 보고서 생성 기능 개선

### v1.0.0 (2025-10-15)
- ✅ 초기 릴리스
- ✅ OWASP Top 10 기반 취약점 검사
- ✅ GUI 및 CLI 모드 지원
- ✅ HTML 보고서 생성 기능
