from add_in.crawl2 import start_crawl2
from A01.A01_integration import BrokenAccessControl
from A02.A02_integration import CryptographicFailures
from A03.A03_integration import Injection
from A04.A04_integration import InsecureDesign
from A05.A05_integration import SecurityMisconfiguration
from A06.A06_integration import VulnerableComponents
from A07.A07_integration import IDAuthFail
from add_in.data_management import file_collection
import asyncio
import json
import os


# 프로젝트 루트 기준 절대 경로 설정
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(PROJECT_ROOT, "etc", "user_info.json")
RESULTS_PATH = os.path.join(PROJECT_ROOT, "etc", "results.json")
MANAGE_DATA = os.path.join(PROJECT_ROOT, "add_in", "manage_data.json")  # data_management로 수집한 파일들
SAMPLE_PATH = os.path.join(PROJECT_ROOT, "etc", "test_A06_sample.json")


def read_config():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)
    
def sample_path():
   with open(SAMPLE_PATH, "r") as f:
       return json.load(f)

# def load_data():
#     """GUI에서 추가한 파일들 로드 (data.json)"""
#     try:
#         with open(ADD_DATA, "r", encoding="utf-8") as f:
#             return json.load(f)
#     except FileNotFoundError:
#         return {"source_files": [], "dependency_files": []}

def collect_and_save_project_files(project_path=None):
    """
    프로젝트 폴더 스캔 및 manage_data.json 생성

    경로 우선순위:
    1. CLI 인자로 전달된 project_path
    2. user_info.json의 Web_Dir (GUI에서 폴더 선택 시 자동 업데이트됨)
    """
    # 프로젝트 경로 결정
    if project_path is None:
        # user_info.json의 Web_Dir 사용
        try:
            config = read_config()
            project_path = config.get("Web_Dir")
            if project_path:
                print(f"📁 user_info.json Web_Dir 사용: {project_path}")
        except Exception as e:
            print(f"⚠️ user_info.json 읽기 실패: {e}")

    # 프로젝트 경로가 결정되지 않은 경우
    if not project_path:
        print(f"❌ 프로젝트 경로를 결정할 수 없습니다.")
        print(f"   1. CLI: python main_test.py --project-path /path/to/project")
        print(f"   2. GUI에서 폴더 선택 (user_info.json의 Web_Dir 자동 업데이트)")
        print(f"   3. user_info.json의 Web_Dir 직접 설정")
        return {"source_files": [], "dependency_files": []}

    # 프로젝트 폴더가 존재하는지 확인
    if not os.path.exists(project_path):
        print(f"⚠️ 프로젝트 폴더를 찾을 수 없습니다: {project_path}")
        return {"source_files": [], "dependency_files": []}

    print(f"🔍 프로젝트 폴더 스캔 중: {project_path}")

    # data_management.py의 file_collection 함수 사용
    collected_data = file_collection(project_path)

    # manage_data.json에 저장
    with open(MANAGE_DATA, "w", encoding="utf-8") as f:
        json.dump(collected_data, f, indent=2, ensure_ascii=False)

    file_count = len(collected_data.get("source_files", []))
    dep_count = len(collected_data.get("dependency_files", []))
    print(f"✅ 프로젝트 스캔 완료: {file_count}개 소스 파일, {dep_count}개 의존성 파일")

    # 수집된 데이터와 사용된 프로젝트 경로 함께 반환
    collected_data["_project_path"] = project_path
    return collected_data

def load_manage_data():
    """manage_data.json에서 프로젝트 파일들 로드"""
    try:
        with open(MANAGE_DATA, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("⚠️ manage_data.json이 없습니다. 프로젝트 스캔을 먼저 수행합니다.")
        return collect_and_save_project_files()

def load_clean_results_template():
    """깨끗한 results.json 템플릿 로드"""
    with open(RESULTS_PATH, "r", encoding='utf-8') as f:
        return json.load(f)

def normalize_details(category_id, test_id, raw_details):
    """
    검사 파일에서 온 details에 추가 필드를 병합
    - 검사 파일의 기존 데이터는 그대로 유지
    - 공통 필드(timestamp 등)를 추가
    """
    if not raw_details:
        return []

    from datetime import datetime

    details = []

    for item in raw_details:
        # 검사 파일에서 온 데이터를 복사 (원본 유지)
        detail = dict(item)

        # timestamp가 없으면 현재 시간 추가
        if 'timestamp' not in detail:
            detail['timestamp'] = datetime.now().isoformat()

        # 공통 필드 정규화
        # location 필드 통일 (url, path, file 등을 location으로)
        if 'location' not in detail:
            detail['location'] = (
                detail.get('url') or
                detail.get('path') or
                detail.get('file') or
                'N/A'
            )
            # 원본 필드 제거 (중복 방지)
            detail.pop('url', None)
            detail.pop('path', None)
            detail.pop('file', None)

        # description 필드 통일 (issue, description 등을 description으로)
        if 'description' not in detail:
            detail['description'] = (
                detail.get('issue') or
                'No description'
            )
            # 원본 필드 제거 (중복 방지)
            detail.pop('issue', None)

        details.append(detail)

    return details


def merge_results(results_json, module_result, category_id=None, test_id=None):
    """개별 모듈 결과를 통합 results에 병합 (표준화 적용)"""

    if not module_result:
        return results_json

    # module_result가 details 배열인 경우
    if isinstance(module_result, list) and category_id and test_id:
        # 표준화 적용
        normalized_details = normalize_details(category_id, test_id, module_result)

        for final_test in results_json["categories"][category_id]["tests"]:
            if final_test["test_id"] == test_id:
                final_test["details"] = normalized_details
                break
    else:
        # 기존 전체 JSON 구조인 경우 (다른 모듈들)
        for cat_id, category_data in module_result["categories"].items():
            for test in category_data["tests"]:
                if test.get("vulnerable_items", 0) > 0 or test.get("details"):
                    # 표준화 적용
                    test["details"] = normalize_details(
                        cat_id,
                        test["test_id"],
                        test.get("details", [])
                    )

                    # results_json에서 같은 test_id 찾아서 업데이트
                    for final_test in results_json["categories"][cat_id]["tests"]:
                        if final_test["test_id"] == test["test_id"]:
                            final_test.update(test)
                            break

    return results_json

def calculate_final_summary(results, web_url=None, project_path=None):
    """
    최종 요약 정보 계산

    Args:
        results: 결과 JSON 객체
        web_url: 검사 대상 URL (선택)
        project_path: 검사 대상 프로젝트 폴더 경로 (선택)
    """
    from datetime import datetime

    total_tests = 0
    total_vulnerabilities = 0
    risk_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFO": 0}

    for category in results["categories"].values():
        for test in category["tests"]:
            if test.get("vulnerable_items", 0) > 0 or test.get("details"):
                total_tests += 1
                total_vulnerabilities += test.get("vulnerable_items", 0)
                risk_level = test.get("risk_level", "")
                if risk_level and risk_level in risk_counts:
                    risk_counts[risk_level] += 1

    results["summary"]["total_tests"] = total_tests
    results["summary"]["total_vulnerabilities"] = total_vulnerabilities
    results["summary"]["risk_distribution"] = risk_counts

    # 검사 시간 추가 (타임스탬프)
    results["summary"]["scan_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 검사 대상 추가 (URL 또는 폴더)
    if web_url:
        results["summary"]["target_url"] = web_url
    if project_path:
        results["summary"]["target_folder"] = project_path


def main_security_test(gui_callback=None):
    """
    통합 보안 테스트 실행 함수
    1. 크롤링 (웹 페이지 수집)
    2. data_management 실행 (소스 코드 수집)
    3. 모든 A01~A05 테스트 수행
    results.json 형식으로 통합된 결과 반환
    """
    # 테스트 대상 URL 설정
    login_path = ""  # 필요시 로그인 경로 설정
    login_data = {}  # 필요시 로그인 데이터 설정

    config = read_config()
    web_url = config["web_url"]

    print(f"\n{'='*60}")
    print(f"통합 보안 취약점 검사 시작")
    print(f"대상 URL: {web_url}")
    print(f"{'='*60}")

    # 1. 깨끗한 results.json 템플릿 로드
    results_json = load_clean_results_template()

    # 2. 크롤링 수행 (웹 페이지 수집)
    print(f"\n{'='*60}")
    print(f"🌐 1단계: 웹 크롤링")
    print(f"{'='*60}")
    obj_list = start_crawl2(web_url, login_path, login_data)
    print(f"✅ 크롤링 완료: {len(obj_list)}개 페이지 발견")

    # 3. 프로젝트 폴더 스캔 (data_management 실행)
    print(f"\n{'='*60}")
    print(f"📁 2단계: 프로젝트 소스 코드 수집")
    print(f"{'='*60}")

    # GUI에서 추가한 폴더 또는 기본 경로(WEB/PrestaShop) 스캔
    manage_data = collect_and_save_project_files()
    source_files = manage_data.get("source_files", [])
    dependency_files = manage_data.get("dependency_files", [])

    project_path = manage_data.get("_project_path")  # 사용된 프로젝트 경로 추출

    print(f"✅ 소스 코드 수집 완료: {len(source_files)}개 파일")

    # 4. 보안 취약점 검사 시작
    print(f"\n{'='*60}")
    print(f"🔍 3단계: 보안 취약점 검사")
    print(f"{'='*60}")

    # A01 - CSRF 취약점 검사
    print(f"\n[A01] Broken Access Control 검사...")
    try:
        a01_checker = BrokenAccessControl()

        print(f"    A01-1: CSRF 검사...")
        a01_csrf = a01_checker.csrf_run(obj_list, config)
        print(a01_csrf)
        # exit(-1)
        results_json = merge_results(results_json, a01_csrf, "A01", "A01-01")

        
        if gui_callback:
            gui_callback(results_json)

        print(f"    → A01 CSRF 검사 완료")
    except Exception as e:
        print(f"    → A01 취약점 검사 실패: {e}")
    
    # 4. A02 - 암호화 취약점 검사
    print(f"\nA02 - Cryptographic Failures 검사...")
    a02_checker = CryptographicFailures()

    # A02-1: 암호화 알고리즘 검사
    try:
        print(f"    A02-1: 취약한 암호화 알고리즘 검사...")
        a02_crypto = a02_checker.check_cryptographic_run(source_files)
        results_json = merge_results(results_json, a02_crypto, "A02", "A02-01")

        if gui_callback:
            gui_callback(results_json)

        print(f"    → A02-1 암호화 알고리즘 검사 완료")
    except Exception as e:
        print(f"    → A02-1 암호화 알고리즘 검사 실패: {e}")

    # A02-2: HTTPS 보안 검사
    try:
        print(f"    A02-2: HTTPS 보안 검사...")
        a02_https = a02_checker.check_https_run(web_url)
        results_json = merge_results(results_json, a02_https, "A02", "A02-02")

        if gui_callback:
            gui_callback(results_json)

        print(f"    → A02-2 HTTPS 보안 검사 완료")
    except Exception as e:
        print(f"    → A02-2 HTTPS 보안 검사 실패: {e}")
    
    #5. A03 - 인젝션 취약점 검사
    print(f"\n A03 - Injection 검사...")
    a03_checker = Injection()

    # A03-1: XSS 검사
    try:
        print(f"    A03-1: XSS 취약점 검사...")
        a03_xss = a03_checker.xss_run(source_files)
        results_json = merge_results(results_json, a03_xss, "A03", "A03-01")

        if gui_callback:
            gui_callback(results_json)

        print(f"    → A03-1 XSS 검사 완료")
    except Exception as e:
        print(f"    → A03-1 XSS 검사 실패: {e}")

    # A03-2: SQL Injection 검사
    try:
        print(f"    A03-2: SQL Injection 취약점 검사...")
        a03_sqli = a03_checker.sqli_run(source_files)
        results_json = merge_results(results_json, a03_sqli, "A03", "A03-02")

        if gui_callback:
            gui_callback(results_json)

        print(f"    → A03-2 SQL Injection 검사 완료")
    except Exception as e:
        print(f"    → A03-2 SQL Injection 검사 실패: {e}")

    # A03-3: Command Injection 검사
    try:
        print(f"    A03-3: Command Injection 취약점 검사...")
        a03_command = a03_checker.command_injection_run(source_files)
        results_json = merge_results(results_json, a03_command, "A03", "A03-03")

        if gui_callback:
            gui_callback(results_json)

        print(f"    → A03-3 Command Injection 검사 완료")
    except Exception as e:
        print(f"    → A03-3 Command Injection 검사 실패: {e}")

    # 6. A04 - 접근 제어 취약점 검사
    print(f"\n A04 - 접근 제어 취약점 검사...")
    a04_checker = InsecureDesign()

    # A04-1: Rate Limiting 검사
    try:
        print(f"    A04-1: Rate Limiting 검사...")
        a04_rate = a04_checker.rate_limit_run(obj_list, config)
        results_json = merge_results(results_json, a04_rate, "A04", "A04-01")

        if gui_callback:
            gui_callback(results_json)

        print(f"    → A04-1 Rate Limiting 검사 완료")
    except Exception as e:
        print(f"    → A04-1 Rate Limiting 검사 실패: {e}")

    # A04-2: 접근 제어 검사
    try:
        print(f"    A04-2: 접근 제어 취약점 검사...")
        web_directory = config.get("Web_Dir", config.get("web_directory", ""))
        a04_access = a04_checker.access_control_run(web_directory)
        results_json = merge_results(results_json, a04_access, "A04", "A04-02")

        if gui_callback:
            gui_callback(results_json)

        print(f"    → A04-2 접근 제어 검사 완료")
    except Exception as e:
        print(f"    → A04-2 접근 제어 검사 실패: {e}")

    # A04-3: 권한 우회 검사
    try:
        print(f"    A04-3: 권한 우회 취약점 검사...")
        a04_permission = a04_checker.permission_bypass_run(config)
        results_json = merge_results(results_json, a04_permission, "A04", "A04-03")

        if gui_callback:
            gui_callback(results_json)

        print(f"    → A04-3 권한 우회 검사 완료")
    except Exception as e:
        print(f"    → A04-3 권한 우회 검사 실패: {e}")
    
    # 7. A05 - 보안 설정 오류 검사
    print(f"\n A05 - 보안 설정 오류 검사...")
    a05_checker = SecurityMisconfiguration()

    # A05-1: 취약한 헤더 검사
    try:
        print(f"    A05-1: 취약한 HTTP 헤더 검사...")
        a05_header = a05_checker.check_vulnerable_run(obj_list)
        results_json = merge_results(results_json, a05_header, "A05", "A05-01")

        if gui_callback:
            gui_callback(results_json)

        print(f"    → A05-1 HTTP 헤더 검사 완료")
    except Exception as e:
        print(f"    → A05-1 HTTP 헤더 검사 실패: {e}")

    # A05-2: 포트 스캔
    try:
        print("    A05-2: 포트 보안 스캔...")
        a05_port = a05_checker.port_security_run(config)
        results_json = merge_results(results_json, a05_port, "A05", "A05-02")

        if gui_callback:
            gui_callback(results_json)

        print(f"    → A05-2 포트 보안 스캔 완료")
    except Exception as e:
        print(f"    → A05-2 포트 보안 스캔 실패: {e}")

    # A05-3: 기본 계정 침투 테스트
    try:
        print(f"    A05-3: 기본 계정 침투 테스트...")
        a05_brute = a05_checker.default_account_run(config)
        results_json = merge_results(results_json, a05_brute, "A05", "A05-03")

        if gui_callback:
            gui_callback(results_json)

        print(f"    → A05-3 기본 계정 침투 테스트 완료")
    except Exception as e:
        print(f"    → A05-3 기본 계정 침투 테스트 실패: {e}")
    
    # 8. A06 - 취약하고 지원되지 않는 구성 요소 검사
    print(f"\n A06 - 취약하고 지원되지 않는 구성 요소 검사...")
    try:
        a06_checker = VulnerableComponents()
        # sample_data = sample_path()
        # dependency_files = sample_data

        # A06-1: 취약한 라이브러리 검사
        print(f"    A06-1: 취약한 라이브러리 검사...")
        a06_vuln = a06_checker.vulnerability_library_run(dependency_files)
        results_json = merge_results(results_json, a06_vuln, "A06", "A06-01")
    except Exception as e:
        print(f"    → A06 취약하고 지원되지 않는 구성 요소 검사 실패: {e}")
        
    # 8. A07 - 세션 관리 취약점 검사
    print(f"\n A07 - 세션 관리 취약점 검사...")
    try:
        a07_checker = IDAuthFail()
        # A07-1: 세션 고정 검사
        print(f"    A07-1: 세션 고정 취약점 검사...")
        a07_session = a07_checker.session_management_run(config)
        results_json = merge_results(results_json, a07_session, "A07", "A07-01")
    except Exception as e:
        print(f"    → A07 세션 관리 취약점 검사 실패: {e}")

    # 8. 최종 요약 정보 계산
    calculate_final_summary(results_json, web_url=web_url, project_path=project_path)
    
    print(json.dumps(results_json, indent=2, ensure_ascii=False))
    
    # 9. 통합된 최종 결과 출력
    print(f"\n{'='*60}")
    print(f"통합 보안 검사 결과")
    print(f"{'='*60}")
    print(f"총 테스트: {results_json['summary']['total_tests']}개")
    print(f"총 취약점: {results_json['summary']['total_vulnerabilities']}개")
    print(f"위험도 분포: {results_json['summary']['risk_distribution']}")
    print(f"{'='*60}")
    
    # 최종 결과를 파일로 저장 (타임스탬프 포함)
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_dir = os.path.join(PROJECT_ROOT, "results")

    # 타임스탬프가 포함된 파일명
    timestamped_results_path = os.path.join(results_dir, f"result_{timestamp}.json")

    # 최신 결과를 가리키는 파일 (호환성 유지)
    final_results_path = os.path.join(results_dir, "final_results.json")

    try:
        # 디렉토리가 없으면 생성
        os.makedirs(results_dir, exist_ok=True)

        # 타임스탬프 파일 저장 (이력 관리용)
        with open(timestamped_results_path, "w", encoding="utf-8") as f:
            json.dump(results_json, f, indent=2, ensure_ascii=False)
        print(f"\n검사 결과가 {timestamped_results_path}에 저장되었습니다.")

    except Exception as e:
        print(f"결과 파일 저장 중 오류 발생: {e}")
    
    return results_json


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="통합 보안 취약점 검사 도구")
    parser.add_argument(
        "--project-path",
        type=str,
        help="검사할 프로젝트 폴더 경로 (지정하지 않으면 GUI 선택 경로 또는 기본 경로 사용)"
    )
    args = parser.parse_args()

    # CLI에서 경로를 지정한 경우 먼저 스캔 수행
    if args.project_path:
        print(f"📁 CLI 인자 경로 사용: {args.project_path}")
        collect_and_save_project_files(project_path=args.project_path)

    main_security_test()

