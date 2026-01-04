#!/usr/bin/env python3
"""
보안 취약점 검사 HTML 보고서 생성기
ZAP Report 구조를 참고하여 효율적인 프레젠테이션 제공
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any


class SecurityReportGenerator:
    """보안 취약점 검사 결과를 HTML 보고서로 생성"""

    RISK_LEVELS = {
        "CRITICAL": {"priority": 1, "color": "#d32f2f", "bg": "#ffebee"},
        "HIGH": {"priority": 2, "color": "#f57c00", "bg": "#fff3e0"},
        "MEDIUM": {"priority": 3, "color": "#fbc02d", "bg": "#fffde7"},
        "LOW": {"priority": 4, "color": "#388e3c", "bg": "#e8f5e9"},
        "INFO": {"priority": 5, "color": "#1976d2", "bg": "#e3f2fd"}
    }

    VULNERABILITY_NAMES = {
        "A01": "Broken Access Control",
        "A01-01": "CSRF (Cross-Site Request Forgery) 취약점",
        "A02": "Cryptographic Failures",
        "A02-01": "약한 암호화 알고리즘 사용",
        "A02-02": "취약한 SSL/TLS 설정",
        "A03": "Injection",
        "A03-01": "SQL Injection",
        "A03-02": "Command Injection",
        "A03-03": "XSS (Cross-Site Scripting)",
        "A04": "Insecure Design",
        "A04-01": "Rate Limiting 부재",
        "A04-02": "파일 시스템 접근 제어 취약점",
        "A04-03": "권한 우회 취약점",
        "A05": "Security Misconfiguration",
        "A05-01": "보안 헤더 누락",
        "A05-02": "디렉토리 리스팅 활성화",
        "A06": "Vulnerable and Outdated Components",
        "A06-01": "취약한 라이브러리 사용",
        "A07": "Identification and Authentication Failures",
        "A07-01": "Session Hijacking",
        "A07-02": "세션 관리 취약점",
        "A08": "Software and Data Integrity Failures",
        "A08-01": "무결성 검증 부재",
        "A09": "Security Logging and Monitoring Failures",
        "A09-01": "로깅 부재",
        "A10": "Server-Side Request Forgery",
        "A10-01": "SSRF 취약점"
    }

    # 취약점별 상세 정보
    VULNERABILITY_INFO = {
        "A01-01": {
            "description": "CSRF(Cross-Site Request Forgery)는 공격자가 사용자의 의지와 무관하게 공격자가 의도한 행위를 특정 웹사이트에 요청하게 만드는 공격입니다. 사용자가 인증된 상태에서 악의적인 요청이 실행되어 계정 정보 변경, 금전 거래 등의 피해가 발생할 수 있습니다.",
            "solution": "• CSRF 토큰을 모든 상태 변경 요청에 포함시키십시오\n• SameSite 쿠키 속성을 설정하십시오 (SameSite=Strict 또는 Lax)\n• 중요한 작업에 대해 재인증을 요구하십시오\n• Referer 헤더를 검증하십시오\n• Double Submit Cookie 패턴을 사용하십시오",
            "references": ["https://owasp.org/www-community/attacks/csrf", "https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html"],
            "cwe": "CWE-352: Cross-Site Request Forgery (CSRF)"
        },
        "A03-01": {
            "description": "SQL Injection은 악의적인 SQL 쿼리를 삽입하여 데이터베이스를 조작하는 공격입니다. 공격자는 인증 우회, 데이터 유출, 데이터 변조, 삭제 등을 수행할 수 있습니다.",
            "solution": "• Prepared Statements (매개변수화된 쿼리)를 사용하십시오\n• Stored Procedures를 사용하십시오\n• 입력값 검증 및 화이트리스트 방식을 적용하십시오\n• 최소 권한 원칙으로 데이터베이스 계정을 운영하십시오\n• ORM(Object-Relational Mapping)을 사용하십시오",
            "references": ["https://owasp.org/www-community/attacks/SQL_Injection", "https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html"],
            "cwe": "CWE-89: SQL Injection"
        },
        "A03-02": {
            "description": "Command Injection은 운영체제 명령어를 실행할 수 있는 취약점입니다. 공격자는 시스템 명령어를 주입하여 서버를 완전히 장악할 수 있습니다.",
            "solution": "• 사용자 입력을 시스템 명령어에 직접 사용하지 마십시오\n• 안전한 API를 사용하십시오 (예: subprocess 대신 라이브러리 함수)\n• 입력값 검증 및 화이트리스트를 적용하십시오\n• 특수문자를 이스케이프 처리하십시오\n• 최소 권한으로 프로세스를 실행하십시오",
            "references": ["https://owasp.org/www-community/attacks/Command_Injection", "https://cheatsheetseries.owasp.org/cheatsheets/OS_Command_Injection_Defense_Cheat_Sheet.html"],
            "cwe": "CWE-78: OS Command Injection"
        },
        "A03-03": {
            "description": "XSS(Cross-Site Scripting)는 악의적인 스크립트를 웹 페이지에 삽입하여 사용자의 브라우저에서 실행시키는 공격입니다. 쿠키 탈취, 세션 하이재킹, 피싱 등의 피해가 발생할 수 있습니다.",
            "solution": "• 출력 시 HTML 인코딩/이스케이프를 적용하십시오\n• Content Security Policy (CSP)를 설정하십시오\n• HttpOnly 플래그를 쿠키에 설정하십시오\n• 입력값 검증 및 살균(sanitization)을 수행하십시오\n• 안전한 JavaScript 라이브러리를 사용하십시오",
            "references": ["https://owasp.org/www-community/attacks/xss/", "https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html"],
            "cwe": "CWE-79: Cross-site Scripting (XSS)"
        },
        "A04-01": {
            "description": "Rate Limiting이 없으면 공격자가 무제한으로 요청을 보낼 수 있어 브루트포스 공격, 서비스 거부(DoS), 자원 고갈 등이 발생할 수 있습니다.",
            "solution": "• IP 기반 요청 제한을 구현하십시오\n• 계정별 요청 제한을 설정하십시오\n• 실패한 로그인 시도 횟수를 제한하십시오\n• CAPTCHA를 추가하십시오\n• 지수 백오프(exponential backoff)를 적용하십시오",
            "references": ["https://owasp.org/www-community/controls/Blocking_Brute_Force_Attacks", "https://cheatsheetseries.owasp.org/cheatsheets/Denial_of_Service_Cheat_Sheet.html"],
            "cwe": "CWE-307: Improper Restriction of Excessive Authentication Attempts"
        },
        "A04-02": {
            "description": "파일 시스템 접근 제어가 부적절하면 공격자가 민감한 파일에 접근하거나 수정할 수 있습니다. 설정 파일, 백업 파일, 로그 파일 등이 노출될 수 있습니다.",
            "solution": "• 파일 및 디렉토리 권한을 최소화하십시오 (예: 644, 755)\n• 웹 서버 사용자 권한을 제한하십시오\n• 민감한 파일을 웹 루트 밖에 배치하십시오\n• .htaccess 또는 nginx 설정으로 접근을 차단하십시오\n• 정기적으로 파일 권한을 점검하십시오",
            "references": ["https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/02-Configuration_and_Deployment_Management_Testing/09-Test_File_Permission"],
            "cwe": "CWE-732: Incorrect Permission Assignment for Critical Resource"
        },
        "A04-03": {
            "description": "권한 우회 취약점은 인증 없이 또는 낮은 권한으로 보호된 리소스에 접근할 수 있는 취약점입니다. URL 직접 접근, 파라미터 조작 등으로 발생합니다.",
            "solution": "• 모든 요청에 대해 서버 측에서 권한을 검증하십시오\n• 세션 기반 접근 제어를 구현하십시오\n• 객체 수준 권한 검사를 수행하십시오\n• 예측 가능한 URL/ID를 피하십시오\n• Deny by default 정책을 적용하십시오",
            "references": ["https://owasp.org/www-project-top-ten/2017/A5_2017-Broken_Access_Control", "https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html"],
            "cwe": "CWE-639: Authorization Bypass Through User-Controlled Key"
        },
        "A05-01": {
            "description": "보안 헤더가 누락되면 다양한 공격에 취약해집니다. X-Frame-Options, X-Content-Type-Options, CSP 등의 헤더가 없으면 클릭재킹, MIME 스니핑, XSS 등의 공격을 받을 수 있습니다.",
            "solution": "• Content-Security-Policy 헤더를 설정하십시오\n• X-Frame-Options: DENY 또는 SAMEORIGIN을 설정하십시오\n• X-Content-Type-Options: nosniff를 설정하십시오\n• Strict-Transport-Security (HSTS)를 설정하십시오\n• X-XSS-Protection: 1; mode=block을 설정하십시오",
            "references": ["https://owasp.org/www-project-secure-headers/", "https://cheatsheetseries.owasp.org/cheatsheets/HTTP_Headers_Cheat_Sheet.html"],
            "cwe": "CWE-693: Protection Mechanism Failure"
        },
        "A05-02": {
            "description": "디렉토리 리스팅이 활성화되어 있으면 공격자가 서버의 파일 구조를 파악하고 민감한 파일을 찾을 수 있습니다.",
            "solution": "• 웹 서버 설정에서 디렉토리 리스팅을 비활성화하십시오\n• Options -Indexes (Apache) 또는 autoindex off (Nginx)를 설정하십시오\n• 모든 디렉토리에 index.html 파일을 배치하십시오\n• 민감한 디렉토리에 접근 제한을 설정하십시오",
            "references": ["https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/02-Configuration_and_Deployment_Management_Testing/04-Review_Old_Backup_and_Unreferenced_Files_for_Sensitive_Information"],
            "cwe": "CWE-548: Information Exposure Through Directory Listing"
        },
        "A06-01": {
            "description": "취약한 버전의 라이브러리나 프레임워크를 사용하면 알려진 취약점을 통해 공격받을 수 있습니다. 공격자는 공개된 exploit을 사용하여 쉽게 시스템을 침투할 수 있습니다.",
            "solution": "• 정기적으로 의존성을 업데이트하십시오\n• 취약점 스캐너를 사용하십시오 (npm audit, pip-audit 등)\n• 사용하지 않는 라이브러리를 제거하십시오\n• 보안 패치를 즉시 적용하십시오\n• 신뢰할 수 있는 소스에서만 라이브러리를 다운로드하십시오",
            "references": ["https://owasp.org/www-project-top-ten/2017/A9_2017-Using_Components_with_Known_Vulnerabilities", "https://cheatsheetseries.owasp.org/cheatsheets/Vulnerable_Dependency_Management_Cheat_Sheet.html"],
            "cwe": "CWE-1035: Using Components with Known Vulnerabilities"
        }
    }

    def __init__(self, results_file: str):
        """
        Args:
            results_file: 검사 결과 JSON 파일 경로
        """
        self.results_file = results_file
        self.results_data = self._load_results()
        self.report_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _load_results(self) -> Dict[str, Any]:
        """검사 결과 JSON 파일 로드"""
        try:
            with open(self.results_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            raise Exception(f"결과 파일 로드 실패: {e}")

    def _get_vulnerability_name(self, vuln_id: str) -> str:
        """취약점 ID에 대한 이름 반환"""
        return self.VULNERABILITY_NAMES.get(vuln_id, vuln_id)

    # def _determine_risk_level(self, vuln_id: str, details: Any) -> str:
    #     """취약점 위험도 결정"""
    #     # 세부 데이터에 risk_level이 있으면 사용
    #     if isinstance(details, dict) and "risk_level" in details:
    #         return details["risk_level"]
        
    #     # 취약점 타입별 기본 위험도 # 삭제 
    #     risk_mapping = {
    #         "A01": "High",
    #         "A02-01": "High",
    #         "A02-02": "High",
    #         "A03-01": "Critical",
    #         "A03-02": "Critical",
    #         "A03-03": "High",
    #         "A04-01": "Medium",
    #         "A04-02": "High",
    #         "A04-03": "High",
    #         "A05-01": "Medium",
    #         "A05-02": "Low",
    #         "A06": "High",
    #         "A07": "High",
    #         "A08": "Medium",
    #         "A09": "Medium",
    #         "A10": "Critical"
    #     }
    #     return risk_mapping.get(vuln_id, "Medium")

    def _count_vulnerabilities(self) -> Dict[str, int]:
        """위험도별 취약점 개수 집계"""
        counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFO": 0}

        # 새로운 JSON 구조 (categories 형식) 처리
        if "categories" in self.results_data:
            categories = self.results_data.get("categories", {})

            for category_id, category_data in categories.items():
                tests = category_data.get("tests", [])

                for test in tests:
                    details = test.get("details", [])

                    # details가 없거나 빈 리스트면 건너뛰기
                    if not details or len(details) == 0:
                        continue

                    # 위험도 결정 - test 자체의 risk_level을 우선 사용
                    test_id = test.get("test_id", "")
                    test_risk_level = test.get("risk_level", "")

                    if test_risk_level:
                        # test에 risk_level이 있으면 사용 (대문자로 정규화)
                        risk_level = test_risk_level.upper()
                        # 유효한 키인지 확인하고, 없으면 MEDIUM으로 기본 설정
                        if risk_level not in counts:
                            risk_level = "MEDIUM"
                    else:
                        # 없으면 MEDIUM으로 기본 설정
                        risk_level = "MEDIUM"

                    # details 개수만큼 카운트
                    counts[risk_level] += len(details)
        # else:
        #     # 기존 구조 지원 (하위 호환성)
        #     for vuln_id, details in self.results_data.items():
        #         if not details or details == []:
        #             continue

        #         risk_level = self._determine_risk_level(vuln_id, details)

        #         # 리스트인 경우 개수만큼 카운트
        #         if isinstance(details, list):
        #             counts[risk_level] += len(details)
        #         else:
        #             counts[risk_level] += 1

        return counts

    def _build_executive_summary(self) -> str:
        """요약 대시보드 생성"""
        counts = self._count_vulnerabilities()
        total = sum(counts.values())

        # Critical, High, Medium만 표시
        display_risks = ["CRITICAL", "HIGH", "MEDIUM"]

        cards_html = ""
        for risk in display_risks:
            count = counts.get(risk, 0)

            # 개수가 0이어도 표시 (Critical, High, Medium은 항상 보여주기)
            color = self.RISK_LEVELS[risk]["color"]
            bg = self.RISK_LEVELS[risk]["bg"]

            cards_html += f"""
            <div class="summary-card" style="background: {bg}; border-left: 4px solid {color};">
                <div class="card-title" style="color: {color};">{risk}</div>
                <div class="card-count">{count}</div>
            </div>
            """

        return f"""
        <div class="executive-summary">
            <h2>검사 요약</h2>
            <div class="summary-stats">
                <div class="summary-card total">
                    <div class="card-title">총 취약점</div>
                    <div class="card-count">{total}</div>
                </div>
                {cards_html}
            </div>
        </div>
        """

    def _group_vulnerabilities(self) -> Dict[str, List[Dict[str, Any]]]:
        """취약점을 카테고리별로 그룹화"""
        grouped = {}

        for vuln_id, details in self.results_data.items():
            if not details or details == []:
                continue

            # 카테고리 추출 (A01, A02, ...)
            category = vuln_id.split('-')[0]

            if category not in grouped:
                grouped[category] = []

            # risk_level = self._determine_risk_level(vuln_id, details)
            vuln_name = self._get_vulnerability_name(vuln_id)

            # URL 리스트 추출
            urls = []
            if isinstance(details, list):
                for item in details:
                    if isinstance(item, dict):
                        if "url" in item:
                            urls.append(item["url"])
                        elif "path" in item:
                            urls.append(item["path"])
                        elif "file" in item:
                            urls.append(item["file"])
                    elif isinstance(item, str):
                        urls.append(item)
            elif isinstance(details, dict):
                if "url" in details:
                    urls.append(details["url"])

            grouped[category].append({
                "id": vuln_id,
                "name": vuln_name,
                # "risk_level": risk_level,
                "count": len(urls) if urls else 1,
                "urls": urls,
                "details": details
            })

        # 각 카테고리 내에서 위험도순 정렬
        for category in grouped:
            grouped[category].sort(
                key=lambda x: self.RISK_LEVELS[x["risk_level"]]["priority"]
            )

        return grouped

    def _build_vulnerability_details(self) -> str:
        """상세 취약점 정보 생성 - 각 detail마다 개별 박스로 표시"""

        if not self.results_data:
            return "<p>발견된 취약점이 없습니다.</p>"

        html = "<div class='vulnerability-details'>"

        # categories 구조로 데이터 파싱
        categories = self.results_data.get("categories", {})

        # 카테고리별로 정렬하여 표시
        for category_id in sorted(categories.keys()):
            category_data = categories[category_id]
            category_name = category_data.get("category_name", category_id)
            tests = category_data.get("tests", [])

            if not tests:
                continue

            html += f"""
            <div class="category-section">
                <h3>{category_id}: {category_name}</h3>
            """

            # 각 테스트별로 처리
            for test in tests:
                test_id = test.get("test_id", "")
                risk_level = test.get("risk_level", "unknown")
                test_name = test.get("test_name", "")
                details = test.get("details", [])

                # details가 없거나 빈 리스트면 건너뛰기 (발견되지 않은 취약점)
                if not details or len(details) == 0:
                    continue

                # 취약점 정보 가져오기
                vuln_info = self.VULNERABILITY_INFO.get(test_id, {})
                vuln_name = self.VULNERABILITY_NAMES.get(test_id, test_name)
                description = vuln_info.get("description", "")
                solution = vuln_info.get("solution", "")
                references = vuln_info.get("references", [])
                cwe = vuln_info.get("cwe", "")

                # 위험도 결정
                # risk_level = self._determine_risk_level(test_id, details)
                risk_color = self.RISK_LEVELS[risk_level]["color"]
                risk_bg = self.RISK_LEVELS[risk_level]["bg"]

                html += f"""
                <div class="vulnerability-item" style="border-left: 4px solid {risk_color};">
                    <div class="vuln-header">
                        <span class="vuln-name">{vuln_name}</span>
                        <span class="risk-badge" style="background: {risk_bg}; color: {risk_color};">
                            {risk_level}
                        </span>
                    </div>
                    <div class="vuln-count">발견된 인스턴스: {len(details)}개</div>
                """

                # 일반 취약점 정보 섹션 (접을 수 있음)
                if description or solution or references or cwe:
                    refs_html = ""
                    if references:
                        refs_links = "".join([f'<li><a href="{ref}" target="_blank">{ref}</a></li>' for ref in references])
                        refs_html = f"""
                        <div class="vuln-info-section">
                            <h5>참고 자료</h5>
                            <ul class="reference-list">
                                {refs_links}
                            </ul>
                        </div>
                        """

                    cwe_html = ""
                    if cwe:
                        cwe_html = f"""
                        <div class="vuln-info-section">
                            <h5>CWE</h5>
                            <p>{cwe}</p>
                        </div>
                        """

                    html += f"""
                    <div class="toggle-info-button" onclick="toggleSection('info-{test_id}')">
                        ▼ 취약점 설명 보기
                    </div>
                    <div id="info-{test_id}" class="vuln-general-info" style="display: none;">
                        <div class="vuln-info-section">
                            <h5>설명</h5>
                            <p>{description}</p>
                        </div>
                        <div class="vuln-info-section">
                            <h5>해결 방안</h5>
                            <p style="white-space: pre-line;">{solution}</p>
                        </div>
                        {cwe_html}
                        {refs_html}
                    </div>
                    """

                # 각 detail마다 개별 파란색 박스 생성
                html += '<div class="details-container">'
                for idx, detail in enumerate(details[:100]):  # 최대 100개까지만
                    detail_id = f"{test_id}-detail-{idx}"

                    # A06 라이브러리 취약점의 경우 package를 제목으로 사용
                    if test_id.startswith("A06"):
                        location = detail.get("package", "N/A")
                    else:
                        location = detail.get("location", detail.get("url", "N/A"))

                    # detail 내용을 JSON 형식으로 정리
                    detail_content = self._format_detail_content(detail, test_id)

                    html += f"""
                    <div class="detail-box">
                        <div class="detail-header" onclick="toggleSection('{detail_id}')">
                            <span class="detail-number">#{idx + 1}</span>
                            <span class="detail-location">{location}</span>
                            <span class="detail-toggle">▼</span>
                        </div>
                        <div id="{detail_id}" class="detail-content" style="display: none;">
                            {detail_content}
                        </div>
                    </div>
                    """

                if len(details) > 100:
                    html += f'<div class="more-details">... 외 {len(details) - 100}개 더 있음</div>'

                html += '</div>'  # details-container 종료
                html += '</div>'  # vulnerability-item 종료

            html += "</div>"  # category-section 종료

        html += "</div>"
        return html

    def _clean_value(self, value):
        """값에서 개행 문자 제거"""
        if isinstance(value, str):
            # 개행 문자를 공백으로 대체
            return value.replace('\n', ' ').replace('\r', ' ').strip()
        elif isinstance(value, list):
            return [self._clean_value(v) for v in value]
        elif isinstance(value, dict):
            return {k: self._clean_value(v) for k, v in value.items()}
        return value

    def _format_detail_content(self, detail: dict, test_id: str = "") -> str:
        """detail 내용을 HTML로 포맷팅"""
        html = ""

        # 먼저 detail의 모든 값을 정리
        clean_detail = self._clean_value(detail)

        # A06 라이브러리 취약점의 경우
        if test_id.startswith("A06"):
            important_keys = ["package", "id", "version", "ecosystem", "description"]

            for key, value in clean_detail.items():
                if key in important_keys and value:
                    if key == "package":
                        html += f"<div class='detail-field'><strong>패키지:</strong> {value}</div>"
                    elif key == "id":
                        html += f"<div class='detail-field'><strong>취약점 ID:</strong> {value}</div>"
                    elif key == "version":
                        version_str = ", ".join(value) if isinstance(value, list) else value
                        html += f"<div class='detail-field'><strong>영향받는 버전:</strong> {version_str}</div>"
                    elif key == "ecosystem":
                        html += f"<div class='detail-field'><strong>에코시스템:</strong> {value}</div>"
                    elif key == "description" and value:
                        html += f"<div class='detail-field'><strong>상세:</strong> {value}</div>"

            # 나머지 정보
            other_info = {k: v for k, v in clean_detail.items() if k not in important_keys and v}
        else:
            # 일반 취약점
            important_keys = ["severity", "description", "timestamp", "location", "url"]

            for key, value in clean_detail.items():
                if key in important_keys and value:
                    if key == "timestamp":
                        html += f"<div class='detail-field'><strong>발견 시간:</strong> {value}</div>"
                    elif key == "severity":
                        html += f"<div class='detail-field'><strong>심각도:</strong> {value}</div>"
                    elif key == "description":
                        html += f"<div class='detail-field'><strong>상세:</strong> {value}</div>"
                    elif key in ["location", "url"]:
                        html += f"<div class='detail-field'><strong>위치:</strong> {value}</div>"

            # 나머지 정보
            other_info = {k: v for k, v in clean_detail.items() if k not in important_keys and v}

        # 추가 정보가 있으면 표시
        if other_info:
            import json
            other_info_json = json.dumps(other_info, indent=2, ensure_ascii=False)
            html += f"""
            <div class="detail-field">
                <strong>추가 정보:</strong>
                <pre class="detail-json">{other_info_json}</pre>
            </div>
            """

        return html if html else "<p>상세 정보 없음</p>"

    def _build_css(self) -> str:
        """CSS 스타일 생성"""
        return """
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: #f5f5f5;
                padding: 20px;
                line-height: 1.6;
            }

            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                border-radius: 8px;
                overflow: hidden;
            }

            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }

            .header h1 {
                font-size: 2em;
                margin-bottom: 10px;
            }

            .header .timestamp {
                opacity: 0.9;
                font-size: 0.9em;
            }

            .content {
                padding: 30px;
            }

            .executive-summary {
                margin-bottom: 40px;
            }

            .executive-summary h2 {
                color: #333;
                margin-bottom: 20px;
                font-size: 1.5em;
            }

            .summary-stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 15px;
                margin-bottom: 30px;
            }

            .summary-card {
                padding: 20px;
                border-radius: 8px;
                text-align: center;
                transition: transform 0.2s;
            }

            .summary-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            }

            .summary-card.total {
                background: #e8eaf6;
                border-left: 4px solid #3f51b5;
            }

            .card-title {
                font-size: 0.9em;
                font-weight: 600;
                margin-bottom: 10px;
                text-transform: uppercase;
            }

            .card-count {
                font-size: 2.5em;
                font-weight: bold;
            }

            .vulnerability-details h2 {
                color: #333;
                margin-bottom: 20px;
                font-size: 1.5em;
            }

            .category-section {
                margin-bottom: 30px;
            }

            .category-section h3 {
                color: #555;
                margin-bottom: 15px;
                padding-bottom: 10px;
                border-bottom: 2px solid #e0e0e0;
            }

            .vulnerability-item {
                background: white;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 20px;
                margin-bottom: 15px;
                transition: box-shadow 0.2s;
            }

            .vulnerability-item:hover {
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }

            .vuln-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 10px;
            }

            .vuln-name {
                font-size: 1.1em;
                font-weight: 600;
                color: #333;
            }

            .risk-badge {
                padding: 5px 15px;
                border-radius: 20px;
                font-size: 0.85em;
                font-weight: 600;
                text-transform: uppercase;
            }

            .vuln-count {
                color: #666;
                margin-bottom: 10px;
                font-size: 0.9em;
            }

            .url-section {
                margin-top: 15px;
            }

            .toggle-button {
                background: #f5f5f5;
                border: 1px solid #ddd;
                padding: 8px 15px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 0.9em;
                transition: background 0.2s;
                width: 100%;
                text-align: left;
            }

            .toggle-button:hover {
                background: #e0e0e0;
            }

            .vuln-detail-info {
                margin: 15px 0;
                padding: 15px;
                background: #f9f9f9;
                border-radius: 4px;
                border-left: 3px solid #2196f3;
            }

            .vuln-info-section {
                margin-bottom: 15px;
            }

            .vuln-info-section h5 {
                color: #2196f3;
                font-size: 1em;
                margin-bottom: 8px;
                font-weight: 600;
            }

            .vuln-info-section p {
                color: #555;
                line-height: 1.6;
                margin: 0;
            }

            .reference-list {
                list-style: none;
                padding-left: 0;
            }

            .reference-list li {
                margin-bottom: 5px;
            }

            .reference-list a {
                color: #2196f3;
                text-decoration: none;
                word-break: break-all;
            }

            .reference-list a:hover {
                text-decoration: underline;
            }

            .url-list {
                margin-top: 10px;
                padding-left: 20px;
                max-height: 300px;
                overflow-y: auto;
                background: #fafafa;
                border-radius: 4px;
                padding: 15px;
            }

            .url-list li {
                margin-bottom: 5px;
                color: #555;
                word-break: break-all;
            }

            /* 취약점 일반 정보 스타일 */
            .toggle-info-button {
                background: #f5f5f5;
                border: 1px solid #ddd;
                padding: 10px 15px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 0.9em;
                margin: 10px 0;
                transition: background 0.2s;
                display: inline-block;
            }

            .toggle-info-button:hover {
                background: #e0e0e0;
            }

            .vuln-general-info {
                margin: 15px 0;
                padding: 15px;
                background: #f9f9f9;
                border-radius: 4px;
                border-left: 3px solid #ff9800;
            }

            /* Detail 박스 컨테이너 */
            .details-container {
                margin-top: 20px;
            }

            /* 개별 Detail 박스 - 파란색 테마 */
            .detail-box {
                background: #fff;
                border: 1px solid #e3f2fd;
                border-left: 4px solid #2196f3;
                border-radius: 6px;
                margin-bottom: 12px;
                overflow: hidden;
                transition: all 0.2s;
            }

            .detail-box:hover {
                box-shadow: 0 2px 8px rgba(33, 150, 243, 0.2);
                border-left-width: 6px;
            }

            .detail-header {
                background: linear-gradient(to right, #e3f2fd, #ffffff);
                padding: 12px 15px;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: space-between;
                transition: background 0.2s;
            }

            .detail-header:hover {
                background: linear-gradient(to right, #bbdefb, #e3f2fd);
            }

            .detail-number {
                background: #2196f3;
                color: white;
                padding: 4px 10px;
                border-radius: 12px;
                font-size: 0.85em;
                font-weight: 600;
                margin-right: 10px;
                min-width: 40px;
                text-align: center;
            }

            .detail-location {
                flex: 1;
                color: #1976d2;
                font-size: 0.95em;
                font-weight: 500;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
            }

            .detail-toggle {
                color: #2196f3;
                font-size: 0.9em;
                margin-left: 10px;
            }

            .detail-content {
                padding: 15px;
                background: #fafafa;
                border-top: 1px solid #e3f2fd;
            }

            .detail-field {
                margin-bottom: 10px;
                line-height: 1.6;
            }

            .detail-field strong {
                color: #1976d2;
                display: inline-block;
                min-width: 100px;
            }

            .detail-json {
                background: #263238;
                color: #aed581;
                padding: 10px;
                border-radius: 4px;
                font-size: 0.85em;
                overflow-x: auto;
                margin-top: 5px;
                white-space: pre-wrap;
                word-wrap: break-word;
            }

            .more-details {
                text-align: center;
                padding: 15px;
                color: #666;
                font-style: italic;
                background: #f5f5f5;
                border-radius: 4px;
                margin-top: 10px;
            }

            .footer {
                background: #f5f5f5;
                padding: 20px;
                text-align: center;
                color: #666;
                font-size: 0.9em;
                border-top: 1px solid #e0e0e0;
            }
        </style>
        """

    def _build_javascript(self) -> str:
        """JavaScript 코드 생성"""
        return """
        <script>
            function toggleSection(sectionId) {
                const section = document.getElementById(sectionId);
                const button = event.target;

                if (section.style.display === 'none' || section.style.display === '') {
                    section.style.display = 'block';

                    // 화살표 변경
                    if (button.textContent.includes('▶')) {
                        button.textContent = button.textContent.replace('▶', '▼');
                    }
                    // 버튼 텍스트 변경
                    if (button.textContent.includes('보기')) {
                        button.textContent = button.textContent.replace('▼', '▲').replace('보기', '숨기기');
                    }
                } else {
                    section.style.display = 'none';

                    // 화살표 변경
                    if (button.textContent.includes('▼')) {
                        button.textContent = button.textContent.replace('▼', '▶');
                    }
                    // 버튼 텍스트 변경
                    if (button.textContent.includes('숨기기')) {
                        button.textContent = button.textContent.replace('▲', '▼').replace('숨기기', '보기');
                    }
                }
            }
        </script>
        """

    def generate_report(self, output_file: str = None) -> str:
        """HTML 보고서 생성

        Args:
            output_file: 출력 파일 경로 (None이면 자동 생성)

        Returns:
            생성된 보고서 파일 경로
        """
        if output_file is None:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            output_file = f"results/security_report_{timestamp}.html"

        # results 디렉토리가 없으면 생성
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        # HTML 빌드
        html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>보안 취약점 검사 보고서</title>
    {self._build_css()}
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>보안 취약점 검사 보고서</h1>
            <div class="timestamp">검사 일시: {self.report_timestamp}</div>
        </div>

        <div class="content">
            {self._build_executive_summary()}

            <h2>상세 취약점 정보</h2>
            {self._build_vulnerability_details()}
        </div>

        <div class="footer">
            <p>이 보고서는 자동으로 생성되었습니다.</p>
            <p>보고서 생성 시간: {self.report_timestamp}</p>
        </div>
    </div>

    {self._build_javascript()}
</body>
</html>"""

        # 파일 저장
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"[✓] 보고서 생성 완료: {output_file}")
        return output_file


def generate_report_from_file(results_file: str, output_file: str = None) -> str:
    """결과 파일로부터 HTML 보고서 생성

    Args:
        results_file: 검사 결과 JSON 파일 경로
        output_file: 출력 파일 경로 (None이면 자동 생성)

    Returns:
        생성된 보고서 파일 경로
    """
    generator = SecurityReportGenerator(results_file)
    return generator.generate_report(output_file)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("사용법: python report_generator.py <결과파일.json> [출력파일.html]")
        sys.exit(1)

    results_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        report_path = generate_report_from_file(results_file, output_file)
        print(f"\n보고서가 생성되었습니다: {report_path}")
    except Exception as e:
        print(f"오류 발생: {e}")
        sys.exit(1)
