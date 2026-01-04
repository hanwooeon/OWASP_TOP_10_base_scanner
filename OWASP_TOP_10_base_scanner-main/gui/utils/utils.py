"""
유틸리티 함수들
공통으로 사용되는 기능들을 모아둔 모듈
"""
import json
import os
from tkinter import messagebox

USER_INFO_PATH = "etc/user_info.json"
RESULTS_PATH = "etc/test_results.json"
JSON_RESULTS_PATH = "etc/json_test_results.json"

def load_user_info():
    """사용자 정보 로드"""
    try:
        with open(USER_INFO_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        # 기본 설정 생성
        default_config = {
            "web_url": "",
            "login_url": "",
            "login_data": {}
        }
        save_user_info(default_config)
        return default_config
    except json.JSONDecodeError as e:
        messagebox.showerror("설정 오류", f"설정 파일을 읽을 수 없습니다: {e}")
        return {}

def save_user_info(user_info):
    """사용자 정보 저장"""
    try:
        # etc 디렉토리가 없으면 생성
        os.makedirs(os.path.dirname(USER_INFO_PATH), exist_ok=True)
        
        with open(USER_INFO_PATH, "w", encoding="utf-8") as f:
            json.dump(user_info, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        messagebox.showerror("저장 오류", f"설정을 저장할 수 없습니다: {e}")
        return False

def save_test_results(results):
    """테스트 결과 저장"""
    try:
        os.makedirs(os.path.dirname(RESULTS_PATH), exist_ok=True)
        
        with open(RESULTS_PATH, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"결과 저장 실패: {e}")
        return False

def load_test_results():
    """테스트 결과 로드"""
    try:
        if os.path.exists(RESULTS_PATH):
            with open(RESULTS_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print(f"결과 로드 실패: {e}")
    return []

def save_json_test_result(url, timestamp, json_result):
    """JSON 형식 테스트 결과 저장"""
    try:
        if not url or not timestamp or not json_result:
            print("JSON 결과 저장: 필수 데이터가 누락되었습니다")
            return False
            
        # 기존 결과 로드
        results = []
        if os.path.exists(JSON_RESULTS_PATH):
            try:
                with open(JSON_RESULTS_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        results = data
            except json.JSONDecodeError:
                print("기존 JSON 파일이 손상되었습니다. 새로 시작합니다.")
                results = []
        
        # 새 결과 추가
        new_result = {
            "url": url,
            "timestamp": timestamp,
            "result": json_result
        }
        
        results.append(new_result)
        
        # 최대 100개 결과만 유지
        if len(results) > 100:
            results = results[-100:]
        
        # 저장
        os.makedirs(os.path.dirname(JSON_RESULTS_PATH), exist_ok=True)
        with open(JSON_RESULTS_PATH, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
            
        print(f"JSON 결과 저장 완료: {len(results)}개 항목")
        return True
        
    except Exception as e:
        print(f"JSON 결과 저장 실패: {e}")
        return False

def load_json_test_results():
    """JSON 테스트 결과 로드"""
    try:
        if os.path.exists(JSON_RESULTS_PATH):
            with open(JSON_RESULTS_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print(f"JSON 결과 로드 실패: {e}")
    return []

def validate_url(url):
    """URL 유효성 검사"""
    if not url:
        return False, "URL을 입력해주세요."
        
    if not url.startswith(("http://", "https://")):
        return False, "URL은 http:// 또는 https://로 시작해야 합니다."
        
    # 기본적인 URL 형식 검사
    import re
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
    if not url_pattern.match(url):
        return False, "올바른 URL 형식이 아닙니다."
        
    return True, ""

def format_timestamp(timestamp_str):
    """타임스탬프 포맷팅"""
    try:
        from datetime import datetime
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return timestamp_str

def calculate_risk_score(results):
    """위험도 점수 계산"""
    if not isinstance(results, dict):
        return 0
        
    summary = results.get("summary", {})
    risk_dist = summary.get("risk_distribution", {})
    
    # 위험도별 가중치
    weights = {
        "CRITICAL": 10,
        "HIGH": 7,
        "MEDIUM": 4, 
        "LOW": 2,
        "INFO": 1
    }
    
    total_score = 0
    for level, count in risk_dist.items():
        if level in weights:
            total_score += count * weights[level]
            
    return total_score

def get_risk_level_color(risk_level):
    """위험도별 색상 반환"""
    colors = {
        "CRITICAL": "#8B0000",  # 어두운 빨강
        "HIGH": "#DC143C",      # 빨강
        "MEDIUM": "#FF8C00",    # 주황
        "LOW": "#FFD700",       # 노랑
        "INFO": "#4169E1",      # 파랑
        "": "#808080"           # 회색 (위험도 없음)
    }
    return colors.get(risk_level, "#808080")

def truncate_text(text, max_length=50):
    """텍스트 자르기"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def ensure_directory(file_path):
    """파일 경로의 디렉토리가 존재하는지 확인하고 생성"""
    directory = os.path.dirname(file_path)
    if directory:
        os.makedirs(directory, exist_ok=True)