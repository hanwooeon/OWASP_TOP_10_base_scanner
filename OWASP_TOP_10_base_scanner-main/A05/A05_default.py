import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import json
import os

# 프로젝트 루트 기준 절대 경로 설정
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USER_INFO_PATH = os.path.join(PROJECT_ROOT, "etc", "user_info.json")
ACCOUNTS_FILE = os.path.join(PROJECT_ROOT, "etc", "A05_accounts_copy.txt")

def load_user_info():
    with open(USER_INFO_PATH, "r") as f:
        return json.load(f)

def load_accounts():
    """계정 파일에서 브루트포스용 계정 목록 로드"""
    accounts = []
    try:
        with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if ':' in line:
                    username, password = line.strip().split(':', 1)
                    accounts.append({"username": username.strip(), "password": password.strip()})
    except Exception as e:
        print(f"[!] 계정 파일 로딩 실패: {e}")
    return accounts

def simple_login_form_finder(url):
    """로그인 폼 찾기 함수"""
    try:
        print(f"로그인 폼 검색 중: {url}")
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 패스워드 필드가 있는 폼 찾기
        login_forms = soup.find_all('form')
        for form in login_forms:
            if form.find('input', {'type': 'password'}):
                inputs = {}
                action = form.get('action', '')
                
                # 모든 input 필드 수집
                for input_tag in form.find_all('input'):
                    name = input_tag.get('name', '')
                    input_type = input_tag.get('type', 'text')
                    value = input_tag.get('value', '')
                    if name:
                        inputs[name] = input_type if not value else value
                
                print(f"로그인 폼 발견: {url}")
                return {
                    'action': action,
                    'inputs': inputs
                }
    except Exception as e:
        print(f"로그인 폼 찾기 실패: {e}")
    
    return None

def extract_form_fields(inputs):
    """폼 필드에서 사용자명, 비밀번호, 제출 버튼 필드 추출"""
    form_data = {
        "username_field": None,
        "password_field": None,
        "submit_field": None,
        "submit_value": None
    }

    # 필드 타입과 이름으로 식별
    for name, field_type in inputs.items():
        name_lower = name.lower()
        
        # 패스워드 필드 찾기
        if field_type == "password":
            form_data["password_field"] = name
        # 사용자명 필드 찾기 (일반적인 패턴)
        elif any(keyword in name_lower for keyword in ["user", "login", "email", "id"]) and field_type in ["text", "email"]:
            form_data["username_field"] = name
        # 제출 버튼 찾기
        elif field_type == "submit" or any(keyword in name_lower for keyword in ["submit", "login", "signin"]):
            form_data["submit_field"] = name
            form_data["submit_value"] = "Login"  # 기본값
    
    # 사용자명 필드가 없으면 첫 번째 텍스트 필드 사용
    if not form_data["username_field"]:
        for name, field_type in inputs.items():
            if field_type in ["text", "email"] and name != form_data["password_field"]:
                form_data["username_field"] = name
                break

    # 히든 필드 추출
    hidden_fields = {
        name: value if value != "hidden" else ""
        for name, value in inputs.items()
        if value == "hidden" or "hidden" in name.lower()
    }

    return form_data, hidden_fields

def attempt_login(session, post_url, account, form_data, hidden_fields):
    """단일 계정으로 로그인 시도"""
    payload = {}
    
    # 필수 필드 확인 후 추가
    if form_data["username_field"]:
        payload[form_data["username_field"]] = account["username"]
    if form_data["password_field"]:
        payload[form_data["password_field"]] = account["password"]
    
    if not payload:
        print(" [!] 유효한 로그인 필드를 찾을 수 없습니다.")
        return False

    if form_data["submit_field"] and form_data["submit_value"]:
        payload[form_data["submit_field"]] = form_data["submit_value"]

    payload.update(hidden_fields)

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": post_url,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    print(f" [*] 시도 중: {account['username']} / {account['password']}")
    response = session.post(post_url, data=payload, headers=headers, allow_redirects=True)
    time.sleep(1.0)

    soup = BeautifulSoup(response.text, "html.parser")
    final_url = response.url.lower()

    # 로그인 실패 조건 확인
    if soup.find("form", {"id": "login_form"}):
        print(f" [-] 로그인 실패 (로그인 폼 유지): {account}\n")
        return False

    if any(keyword in final_url for keyword in ["login", "signin", "adminlogin"]):
        print(f" [-] 로그인 실패 (URL 유지): {account}\n")
        return False

    print(f" [+] 로그인 성공: {account}")
    print(f" [+] 최종 URL: {response.url}\n")
    return True

def run_brute_force_attack(login_form, login_url):
    """브루트포스 공격 실행"""
    accounts = load_accounts()
    
    if not accounts:
        print(f"[!] 계정 파일이 비어있거나 존재하지 않습니다: {ACCOUNTS_FILE}")
        return False, None

    inputs = login_form.get("inputs", {})
    if not inputs:
        print(" [!] 로그인 입력 필드가 없습니다.")
        return False, None

    form_data, hidden_fields = extract_form_fields(inputs)
    post_url = urljoin(login_url, login_form["action"])

    print(f"\n[+] 분석 완료 → 요청 URL: {post_url}")
    print(f"    사용자명 필드: {form_data['username_field']}")
    print(f"    비밀번호 필드: {form_data['password_field']}")
    print(f"    제출 필드: {form_data['submit_field']}")
    print(f"    Hidden 필드: {hidden_fields if hidden_fields else '없음'}\n")

    session = requests.Session()
    
    for account in accounts:
        if attempt_login(session, post_url, account, form_data, hidden_fields):
            return True, account  # 성공한 계정 정보 반환
    
    return False, None

def start_brute_force_scan(config):
    """details만 반환하는 브루트포스 공격 함수"""
    from datetime import datetime
    
    # config에서 login_url 사용
    login_url = config.get("login_url")
    
    # 로그인 폼 찾기
    login_form = simple_login_form_finder(login_url)
    if not login_form:
        print("로그인 폼을 찾을 수 없습니다.")
        return []
    
    # 브루트포스 공격 실행
    success, found_account = run_brute_force_attack(login_form, login_url)
    
    # details 생성
    details = []
    if success and found_account:
        details.append({
            "url": login_url,
            "method": "POST",
            "issue": f"약한 계정 발견 (ID: {found_account['username']}, PW: {found_account['password']})",
            "timestamp": datetime.now().isoformat()
        })
    else:
        details.append({
            "url": login_url,
            "method": "POST",
            "issue": "약한 계정이 발견되지 않음",
            "timestamp": datetime.now().isoformat()
        })
    
    return details

def run(config):
    """main_test.py에서 호출되는 함수"""
    return start_brute_force_scan(config)

if __name__ == "__main__":
    try:
        config = load_user_info()
        details = start_brute_force_scan(config)
        
        print(json.dumps(details, indent=2, ensure_ascii=False))
        with open("./default.json", "w", encoding="utf-8") as f:
            json.dump(details, f, indent=2, ensure_ascii=False)
        
    except Exception as e:
        print(f"오류 발생: {e}")