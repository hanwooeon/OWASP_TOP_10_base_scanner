# A05_check_vulnerable.py
import requests
import time
import json
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from add_in.crawl2 import start_crawl2

# 프로젝트 루트 기준 절대 경로 설정
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ETC_PATH = os.path.join(PROJECT_ROOT, "etc", "A05_security_config.json")
USER_INFO_PATH = os.path.join(PROJECT_ROOT, "etc", "user_info.json")

def load_user_info():
    with open(USER_INFO_PATH, "r") as f:
        user_info = json.load(f)
    return user_info

def load_security_config():
    with open(ETC_PATH, "r") as f:
        return json.load(f)


def check_vulnerable_headers(obj_list):
    """details만 반환하는 취약점 검사 함수"""
    from datetime import datetime
    from urllib.parse import urlparse

    # JSON에서 설정 로드
    config = load_security_config()
    vulnerable_headers = config["vulnerable_headers"]
    error_keywords = config["error_keywords"]
    security_headers = config["security_headers"]
    directory_indicators = config["directory_listing_indicators"]

    headers = {
        'User-Agent': 'Mozilla/5.0'
    }

    print(f"크롤링 완료: {len(obj_list)}개의 페이지에서 검사 시작")
    details = []
    seen_vulnerabilities = set()  # (base_url, issue_type) 조합으로 중복 체크

    for idx, obj in enumerate(obj_list, 1):
        page_url = obj.path
        print(f"\n[{idx}] 페이지 검사: {page_url}")

        # URL을 base path로 정규화 (쿼리 문자열 제거)
        parsed = urlparse(page_url)
        base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

        try:
            response = safe_request(page_url, headers, retries=3)

            # 민감한 헤더 검사
            found_headers = {
                k: v for k, v in response.headers.items()
                if k in vulnerable_headers
            }
            if found_headers:
                print(f"  민감한 헤더 발견: {found_headers}")
                vuln_key = (base_url, "sensitive_headers")
                if vuln_key not in seen_vulnerabilities:
                    seen_vulnerabilities.add(vuln_key)
                    details.append({
                        "url": base_url,
                        "method": "GET",
                        "issue": f"민감한 헤더 노출: {list(found_headers.keys())}",
                        "timestamp": datetime.now().isoformat()
                    })

            # 에러 정보 노출 검사
            error_info = check_error_disclosure(response, error_keywords)
            if error_info:
                print(f"  에러 정보 노출: {error_info}")
                vuln_key = (base_url, "error_disclosure")
                if vuln_key not in seen_vulnerabilities:
                    seen_vulnerabilities.add(vuln_key)
                    details.append({
                        "url": base_url,
                        "method": "GET",
                        "issue": f"에러 정보 노출 (상태코드: {error_info['status_code']})",
                        "timestamp": datetime.now().isoformat()
                    })

            # 보안 설정 누락 검사
            additional_issues = perform_additional_checks(response, security_headers, directory_indicators)
            if additional_issues:
                print(f"  추가 보안 이슈: {additional_issues}")
                if 'missing_security_headers' in additional_issues:
                    vuln_key = (base_url, "missing_security_headers")
                    if vuln_key not in seen_vulnerabilities:
                        seen_vulnerabilities.add(vuln_key)
                        details.append({
                            "url": base_url,
                            "method": "GET",
                            "issue": f"보안 헤더 누락: {additional_issues['missing_security_headers']}",
                            "timestamp": datetime.now().isoformat()
                        })

        except Exception as e:
            print(f"  요청 실패: {e}")
            vuln_key = (base_url, "request_failure")
            if vuln_key not in seen_vulnerabilities:
                seen_vulnerabilities.add(vuln_key)
                details.append({
                    "url": base_url,
                    "method": "GET",
                    "issue": f"요청 실패: {str(e)}",
                    "timestamp": datetime.now().isoformat()
                })

    print(f"\n중복 제거 완료: 총 {len(details)}개 고유 취약점 발견")
    return details

# 요청 실패 시 재시도
def safe_request(url, headers, retries=3):
    for attempt in range(retries):
        try:
            return requests.get(url, headers=headers, timeout=10, verify=False)
        except Exception as e:
            if attempt == retries - 1:
                raise
            print(f"  재시도 {attempt+1}/{retries}...")
            time.sleep(1)

# 에러 메시지 또는 시스템 정보 노출 여부
def check_error_disclosure(response, error_keywords):
    if response.status_code < 400:
        return None
    body = response.text.lower()
    return {
        'status_code': response.status_code,
        'keywords': [kw for kw in error_keywords if kw in body]
    } if any(kw in body for kw in error_keywords) else None

# 디렉토리 리스팅 활성화 여부
def perform_additional_checks(response, security_headers, directory_indicators):
    issues = {}
    if response.status_code == 200:
        body = response.text.lower()
        if all(indicator in body for indicator in directory_indicators):
            issues['directory_listing'] = True

    missing = [k for k in security_headers if k not in response.headers]
    if missing:
        issues['missing_security_headers'] = missing
    return issues if issues else None

def run(obj_list):
    """main_test.py에서 호출되는 함수"""
    return check_vulnerable_headers(obj_list)

if __name__ == "__main__":
    user_info = load_user_info()

    web_url = user_info["web_url"]
    print(f"URL 로드됨: {web_url}")
    
    # 크롤링 실행
    print("크롤링 시작...")
    obj_list = start_crawl2(web_url, "", "")
    print(f"크롤링 완료: {len(obj_list)}개 페이지 발견")
    
    # 취약점 검사 실행
    details = check_vulnerable_headers(obj_list)
    
    print(json.dumps(details, indent=2, ensure_ascii=False))
    with open("A05/check_vulnerable", "w", encoding="utf-8") as f:
        json.dump(details, f, indent=2, ensure_ascii=False)