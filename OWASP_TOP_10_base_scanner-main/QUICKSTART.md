# 🚀 빠른 시작 가이드

OWASP Top 10 웹 보안 취약점 스캐너를 빠르게 시작하는 방법입니다.

## ⚡ 5분 안에 시작하기

### 1단계: 설치 (2분)

```bash
# 저장소 클론
git clone https://github.com/yourusername/OWASP_TOP_10_base_scanner.git
cd OWASP_TOP_10_base_scanner

# 의존성 설치
pip install -r requirements.txt

# Playwright 브라우저 설치
playwright install chromium
```

### 2단계: GUI 실행 (1분)

```bash
python3 test_gui_safe.py
```

### 3단계: 검사 실행 (2분)

1. **설정 탭**에서 대상 URL 입력 (예: `http://localhost:8080`)
2. **프로젝트 폴더 선택** (소스 코드 위치)
3. **검사 탭**으로 이동하여 **검사 시작** 클릭
4. **결과 탭**에서 발견된 취약점 확인

## 📸 스크린샷으로 보는 사용법

### 1. 설정 화면
```
┌──────────────────────────────────────┐
│  설정                                 │
├──────────────────────────────────────┤
│  대상 URL: [http://localhost:8080] │
│  로그인 ID: [            ]          │
│  비밀번호:  [            ]          │
│  포트:      [80          ]          │
│                                      │
│  프로젝트 폴더: [/var/www/html    ] │
│  [폴더 선택] [저장]                 │
└──────────────────────────────────────┘
```

### 2. 검사 화면
```
┌──────────────────────────────────────┐
│  검사                                 │
├──────────────────────────────────────┤
│  ☑ A01: Broken Access Control       │
│  ☑ A02: Cryptographic Failures      │
│  ☑ A03: Injection                   │
│  ☑ A04: Insecure Design             │
│  ☑ A05: Security Misconfiguration   │
│  ☑ A06: Vulnerable Components       │
│  ☑ A07: Auth Failures               │
│                                      │
│  [검사 시작] [중지]                  │
│                                      │
│  진행 상황: ████████░░░░ 67%        │
└──────────────────────────────────────┘
```

### 3. 결과 화면
```
┌────────────────────────────────────────────────────┐
│  결과                                               │
├────────────────────────────────────────────────────┤
│  검사 결과 목록                                     │
│  ┌────────────────────────┬─────────────────────┐ │
│  │ 검사 시간              │ 검사 대상           │ │
│  ├────────────────────────┼─────────────────────┤ │
│  │ 2025-11-03 13:55:23   │ http://localhost   │ │
│  │ 2025-11-02 10:30:15   │ http://example.com │ │
│  └────────────────────────┴─────────────────────┘ │
│                                                    │
│  [새로고침]                                        │
└────────────────────────────────────────────────────┘
```

## 🎯 주요 사용 시나리오

### 시나리오 1: 로컬 웹 애플리케이션 검사

```bash
# 1. 웹 서버 실행 (예: PHP 내장 서버)
cd /var/www/html
php -S localhost:8080

# 2. 스캐너 실행
python3 test_gui_safe.py

# 3. 설정
# - URL: http://localhost:8080
# - 프로젝트 폴더: /var/www/html

# 4. 검사 시작
```

### 시나리오 2: 원격 웹사이트 검사

```bash
# 1. 스캐너 실행
python3 test_gui_safe.py

# 2. 설정
# - URL: https://example.com
# - 프로젝트 폴더: (소스 코드가 있다면 선택)

# 3. 동적 검사만 실행 (소스 코드 없이)
```

### 시나리오 3: CLI로 자동화 검사

```bash
# 1. 설정 파일 수정
nano etc/user_info.json

# 2. CLI 실행
python3 main_test.py --project-path /var/www/html

# 3. 보고서 확인
ls -l report/
```

## ✅ 체크리스트

검사를 시작하기 전에 확인하세요:

- [ ] Python 3.8 이상 설치 확인: `python3 --version`
- [ ] 필수 패키지 설치 완료: `pip list | grep requests`
- [ ] Playwright 브라우저 설치: `playwright install chromium`
- [ ] Tkinter 설치 (Linux): `python3 -c "import tkinter"`
- [ ] 대상 웹 애플리케이션 실행 중
- [ ] 검사 권한 확인 (본인 소유 또는 허가받은 시스템)

## 🔍 첫 검사 결과 이해하기

### 위험도 분류
- 🔴 **CRITICAL**: 즉시 수정 필요 (시스템 완전 침투 가능)
- 🟠 **HIGH**: 빠른 시일 내 수정 필요 (심각한 보안 위협)
- 🟡 **MEDIUM**: 계획된 수정 필요 (보안 취약점)
- 🟢 **LOW**: 개선 권장 (경미한 취약점)
- 🔵 **INFO**: 참고 정보

### 주요 취약점 유형

1. **CSRF (Cross-Site Request Forgery)**
   - 공격자가 사용자 권한으로 악의적 요청 실행
   - 해결: CSRF 토큰 추가, SameSite 쿠키 설정

2. **SQL Injection**
   - 데이터베이스 쿼리 조작
   - 해결: Prepared Statement 사용

3. **XSS (Cross-Site Scripting)**
   - 악성 스크립트 삽입
   - 해결: 입력값 검증, 출력 이스케이프

4. **취약한 라이브러리**
   - 알려진 취약점이 있는 오래된 라이브러리 사용
   - 해결: 라이브러리 업데이트

## 📊 보고서 활용하기

### HTML 보고서 생성

```bash
# GUI에서:
결과 탭 → 검사 결과 더블클릭 → "보고서 생성" 버튼

# 생성된 파일:
report/security_report_2025-11-03_13-55-23.html
```

### 보고서 공유하기

```bash
# 웹 브라우저로 열기
firefox report/security_report_*.html

# 팀원에게 공유 (민감 정보 확인 필수!)
# 1. 보고서에서 민감한 URL/경로 제거
# 2. 로그인 정보 등 삭제 확인
# 3. 이메일 또는 슬랙으로 전송
```

## 💡 팁과 트릭

### 성능 최적화

```bash
# 1. 특정 카테고리만 검사
# GUI: 검사 탭에서 원하는 항목만 체크

# 2. 결과 필터링
# 결과 탭: 필터 드롭다운에서 A01, A03 등 선택

# 3. 대량 데이터 처리
# - 1000개 이상 취약점 발견 시 자동으로 제한
# - 전체 데이터는 HTML 보고서로 확인
```

### 문제 해결 빠른 참조

| 문제 | 해결 방법 |
|------|----------|
| `ModuleNotFoundError: tkinter` | `sudo apt-get install python3-tk` |
| `playwright not found` | `playwright install chromium` |
| Segmentation fault | [SEGFAULT_FIX.md](SEGFAULT_FIX.md) 참조 |
| 검사 중 멈춤 | 네트워크/방화벽 확인 |
| 취약점이 너무 많음 | 필터 사용 또는 보고서 생성 |

## 🎓 다음 단계

검사를 성공적으로 완료했다면:

1. 📖 [README.md](README.md) - 전체 기능 및 상세 사용법
2. 🔧 [SEGFAULT_FIX.md](SEGFAULT_FIX.md) - 기술적 이슈 해결
3. 📚 [LIBRARIES.md](LIBRARIES.md) - 사용된 라이브러리 정보
4. 🛡️ OWASP Top 10 공식 문서 - https://owasp.org/Top10/

## ❓ 자주 묻는 질문 (FAQ)

**Q: 검사에 얼마나 걸리나요?**
A: 웹 애플리케이션 크기에 따라 다르지만, 일반적으로 5-30분 소요됩니다.

**Q: 소스 코드 없이도 검사 가능한가요?**
A: 네! 동적 검사(DAST)는 URL만으로도 가능합니다. 단, 소스 코드가 있으면 더 정확한 검사가 가능합니다.

**Q: 프로덕션 환경에서 사용해도 되나요?**
A: 가능하지만 주의가 필요합니다. 검사 중 서비스 부하가 발생할 수 있으므로 테스트 환경에서 먼저 검증하세요.

**Q: 자동으로 취약점을 수정해주나요?**
A: 아니요. 이 도구는 취약점을 **발견**하고 **보고**하는 역할을 합니다. 수정은 개발자가 직접 해야 합니다.

**Q: 상용 도구와 비교하면?**
A: 교육 및 기본 검사 목적으로 좋습니다. 전문적인 검사는 Burp Suite, OWASP ZAP 등 상용 도구 사용을 권장합니다.

## 📞 도움이 필요하신가요?

- 🐛 버그 리포트: [GitHub Issues](https://github.com/yourusername/OWASP_TOP_10_base_scanner/issues)
- 💬 질문: [Discussions](https://github.com/yourusername/OWASP_TOP_10_base_scanner/discussions)
- 📧 이메일: your.email@example.com

---

**즐거운 보안 검사 되세요!** 🛡️
