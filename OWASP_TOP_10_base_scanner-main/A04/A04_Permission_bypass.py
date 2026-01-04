import requests
from urllib.parse import urljoin
from typing import List, Dict, Optional, Tuple
import logging
import os
import argparse
import concurrent.futures
import json
from datetime import datetime
from tqdm import tqdm
import urllib3

# SSL 인증서 검증 경고 및 Connection Pool 경고 비활성화
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)
PATH_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
File_path = os.path.join(PATH_ROOT, "etc", "A04_Permission_bypass.json")

def read_file():
    with open(File_path, "r") as f:
        data = json.load(f)
    return data

class PermissionBypassScanner:

    def __init__(self, target_url: str, session: Optional[requests.Session] = None, verify_ssl: bool = False, timeout: int = 10, max_workers: int = 10):
        self.logger = logging.getLogger(__name__)

        self.target_url = target_url.rstrip('/')
        self.session = session or requests.Session()

        # Connection Pool 크기 증가
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=100,
            pool_maxsize=100,
            max_retries=3
        )
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

        self.verify_ssl = verify_ssl
        self.timeout = timeout
        self.max_workers = max_workers
        self.test_cookies = read_file().get("test_cookies", {})
        self.id_patterns = read_file().get("id_patterns", [])
        self.user_keywords = read_file().get("user_keywords", [])
        self.default_urls = read_file().get("default_urls", [])
        self.admin_urls = read_file().get("admin_urls", [])

        # 결과 저장용(조재호가 추가함)
        self.details = []

    #조재호 수정버전
    def parse_scan_results(self, results):
        print(f"test parse_scan_results: {len(results)}개 결과 처리 중...")

        from urllib.parse import urlparse

        details = []
        seen_vulnerabilities = set()  # (base_url, check_type) 조합으로 중복 체크

        for result in results:
            url = result.get('url', '')
            check_type = result.get('check_type', 'unknown')
            description = result.get('description', '')

            # URL을 base path로 정규화 (쿼리 문자열 제거)
            if url:
                parsed = urlparse(url)
                base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            else:
                base_url = ''

            # (base_url, check_type) 조합으로 중복 체크
            vuln_key = (base_url, check_type)

            # 중복이 아닌 경우만 추가
            if vuln_key not in seen_vulnerabilities:
                seen_vulnerabilities.add(vuln_key)
                details.append({
                    "path": base_url,
                    "description": description,
                    "method": "GET",
                    "timestamp": datetime.now().isoformat()
                })

        print(f"중복 제거 완료: {len(results)}개 → {len(details)}개 고유 취약점")
        return details
    
    def is_error_page(self, response) -> bool:
        """에러 페이지인지 감지"""
        content = response.text.lower()

        # 에러 페이지 감지 키워드
        error_keywords = [
            '404', 'not found', 'page not found', '페이지를 찾을 수 없습니다',
            '403', 'forbidden', 'access denied', '접근이 거부',
            '400', 'bad request', '잘못된 요청',
            '500', 'internal server error', '서버 오류',
            'error', 'exception', 'oops'
        ]

        # 응답이 너무 작으면 에러 페이지일 가능성
        if len(content) < 100:
            return True

        # 에러 키워드가 많이 포함되어 있으면 에러 페이지
        error_count = sum(1 for keyword in error_keywords if keyword in content)
        if error_count >= 2:
            return True

        return False

    def check_direct_url_access(self, protected_urls_with_lines: List[Tuple[str, int]], source_file: str, batch_size: int = 1000) -> List[Dict]:
        """
        URL에 대한 직접 접근을 시도하여 취약점을 검사합니다. 대량의 URL을 batch_size 단위로 나누어 처리합니다.
        인증 없이 보호된 리소스에 접근 가능한지 검사합니다.
        """
        results = []
        total_urls = len(protected_urls_with_lines)
        num_batches = (total_urls + batch_size - 1) // batch_size  # 올림 나눗셈

        for batch_num in range(num_batches):
            start_idx = batch_num * batch_size
            end_idx = min((batch_num + 1) * batch_size, total_urls)
            current_batch = protected_urls_with_lines[start_idx:end_idx]

            print(f"직접 URL 접근 검사 진행 중: 배치 {batch_num + 1}/{num_batches} ({start_idx+1}-{end_idx}/{total_urls} URLs)")

            # 병렬 처리를 위한 함수
            def check_url(url_info):
                url, line_number = url_info
                full_url = urljoin(self.target_url, url)
                try:
                    # 리다이렉트 허용 (로그인 페이지로 리다이렉트 되는지 확인)
                    response = self.session.get(full_url, allow_redirects=True, verify=self.verify_ssl, timeout=self.timeout)

                    # 200 응답이고, 에러 페이지가 아닌 경우만 취약점으로 판단
                    if response.status_code == 200:
                        # 에러 페이지 체크
                        if self.is_error_page(response):
                            return None

                        # 로그인 페이지로 리다이렉트되었는지 체크
                        if 'login' in response.url.lower() or 'signin' in response.url.lower():
                            return None  # 로그인 필요 = 정상

                        # 홈페이지로 리다이렉트되었는지 체크 (오탐 방지)
                        # 요청한 URL과 최종 URL을 비교
                        from urllib.parse import urlparse, parse_qs
                        requested_path = urlparse(full_url).path.rstrip('/')
                        final_path = urlparse(response.url).path.rstrip('/')

                        # 리다이렉트되어 다른 페이지로 이동했는지 확인
                        if requested_path and final_path != requested_path:
                            # 홈페이지('/', '/index.php', '/en/', '/ko/' 등)로 리다이렉트된 경우
                            if final_path in ['', '/', '/index.php', '/en', '/ko']:
                                return None  # 홈페이지로 리다이렉트 = 접근 불가 = 정상
                            # 또는 쿼리 파라미터에 'url=' 같은 리다이렉트 파라미터가 있는 경우
                            query_params = parse_qs(urlparse(response.url).query)
                            if 'url' in query_params or 'redirect' in query_params:
                                return None  # 리다이렉트 = 정상

                        # 보호된 리소스에 접근 가능 - 취약!
                        return {
                            'url': full_url,
                            'source_url': url,
                            'status': '취약',
                            'description': '인증 없이 보호된 리소스에 직접 접근이 가능함',
                            'line_number': line_number,
                            'source_file': source_file,
                            'check_type': 'direct_access'
                        }
                except Exception as e:
                    self.logger.error(f"{full_url}에 대한 직접 접근 검사 중 오류 발생: {str(e)}")
                return None
            
            # 병렬 처리 실행
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = [executor.submit(check_url, url_info) for url_info in current_batch]
                
                # tqdm을 사용하여 진행 상황 표시
                for future in tqdm(concurrent.futures.as_completed(futures), total=len(current_batch), desc="URL 검사 중"):
                    result = future.result()
                    if result:
                        results.append(result)  
        return results         
    
    def check_session_manipulation(self) -> List[Dict]:
        """
        세션 조작을 통한 취약점을 검사합니다.
        """
        results = []
        try:
            original_cookies = self.session.cookies.copy()
            
            # 일반적인 권한 관련 쿠키 값 테스트
            test_cookies = self.test_cookies
            
            for cookie_name, cookie_value in test_cookies.items():
                # 기존 쿠키 백업
                old_value = self.session.cookies.get(cookie_name)
                
                # 테스트 쿠키 설정
                self.session.cookies.set(cookie_name, cookie_value)
                
                # 응답 확인
                try:
                    response = self.session.get(self.target_url, verify=self.verify_ssl, timeout=self.timeout)
                    
                    # 관리자 키워드 확인
                    admin_keywords = ['admin', 'administrator', 'dashboard', '관리자', '대시보드', '제어판', 'settings']
                    content = response.text.lower()
                    
                    if response.status_code == 200 and any(keyword in content for keyword in admin_keywords):
                        results.append({
                            'url': self.target_url,
                            'status': '취약',
                            'description': f'세션 쿠키 조작이 가능함 ({cookie_name}={cookie_value})',
                            'check_type': 'session_manipulation'
                        })
                except Exception as e:
                    self.logger.error(f"세션 조작 검사 중 오류 발생: {str(e)}")
                
                # 쿠키 원래 값으로 복원
                if old_value:
                    self.session.cookies.set(cookie_name, old_value)
                else:
                    self.session.cookies.pop(cookie_name, None)
            
            # 원래 쿠키로 복원
            self.session.cookies = original_cookies
                
        except Exception as e:
            self.logger.error(f"세션 조작 검사 중 오류 발생: {str(e)}")
        
        return results

    def check_privilege_escalation(self, admin_urls_with_lines: List[Tuple[str, int]], source_file: str, batch_size: int = 1000) -> List[Dict]:
        """
        권한 상승 취약점을 검사합니다. 대량의 URL을 batch_size 단위로 나누어 처리합니다.
        일반 사용자가 관리자 페이지/기능에 접근 가능한지 검사합니다.
        """
        results = []
        total_urls = len(admin_urls_with_lines)
        num_batches = (total_urls + batch_size - 1) // batch_size  # 올림 나눗셈

        for batch_num in range(num_batches):
            start_idx = batch_num * batch_size
            end_idx = min((batch_num + 1) * batch_size, total_urls)
            current_batch = admin_urls_with_lines[start_idx:end_idx]

            print(f"권한 상승 검사 진행 중: 배치 {batch_num + 1}/{num_batches} ({start_idx+1}-{end_idx}/{total_urls} URLs)")

            # 병렬 처리를 위한 함수
            def check_url(url_info):
                url, line_number = url_info
                full_url = urljoin(self.target_url, url)
                try:
                    response = self.session.get(full_url, allow_redirects=True, verify=self.verify_ssl, timeout=self.timeout)

                    if response.status_code == 200:
                        # 에러 페이지 체크
                        if self.is_error_page(response):
                            return None

                        # 로그인 페이지로 리다이렉트되었는지 체크
                        if 'login' in response.url.lower() or 'signin' in response.url.lower():
                            return None  # 로그인 필요 = 정상

                        # 홈페이지로 리다이렉트되었는지 체크 (오탐 방지)
                        from urllib.parse import urlparse, parse_qs
                        requested_path = urlparse(full_url).path.rstrip('/')
                        final_path = urlparse(response.url).path.rstrip('/')

                        if requested_path and final_path != requested_path:
                            if final_path in ['', '/', '/index.php', '/en', '/ko']:
                                return None  # 홈페이지로 리다이렉트 = 정상
                            query_params = parse_qs(urlparse(response.url).query)
                            if 'url' in query_params or 'redirect' in query_params:
                                return None  # 리다이렉트 = 정상

                        # 관리자 페이지 특성 확인 (더 엄격한 검사)
                        admin_keywords = ['admin panel', 'administrator', 'dashboard', '관리자 패널', '대시보드', '제어판']
                        content = response.text.lower()

                        # 관리 기능 키워드 (더 구체적)
                        admin_functions = ['user management', 'system settings', 'delete user', 'edit user',
                                          '사용자 관리', '시스템 설정', '사용자 삭제', '권한 설정']

                        # 관리자 페이지 특성이 있는지 확인
                        has_admin_panel = any(keyword in content for keyword in admin_keywords)
                        has_admin_function = any(func in content for func in admin_functions)

                        if has_admin_panel or has_admin_function:
                            return {
                                'url': full_url,
                                'source_url': url,
                                'status': '취약',
                                'description': '인증 없이 관리자 페이지/기능에 접근 가능함 (권한 상승)',
                                'line_number': line_number,
                                'source_file': source_file,
                                'check_type': 'privilege_escalation'
                            }
                except Exception as e:
                    self.logger.error(f"{full_url}에 대한 권한 상승 검사 중 오류 발생: {str(e)}")
                return None
            
            # 병렬 처리 실행
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = [executor.submit(check_url, url_info) for url_info in current_batch]
                
                # tqdm을 사용하여 진행 상황 표시
                for future in tqdm(concurrent.futures.as_completed(futures), total=len(current_batch), desc="URL 검사 중"):
                    result = future.result()
                    if result:
                        results.append(result) 
                        
            return results
    
    #조재호 수정버전(user_endpoints 매개변수 추가) get_url_lists 함수에서 endpoint.txt 읽어서 전달하는데 기존 코드에는 리턴을 안함
    def check_user_id_manipulation(self,user_endpoints, user_id_range: range = range(1, 11)) -> List[Dict]:
        """
        사용자 ID 조작으로 타 사용자 정보에 접근 가능한지 검사합니다.
        """
        results = []
        
        # 원래 없어도 되는 부분*(조재호)
        # 엔드포인트 목록 파일 경로 수정 - 절대 경로 사용
        # endpoint_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "etc", "A10_endpoint.txt")
        
        try:
            # 원래 없어도 되는 부분*(조재호)
            # 파일에서 엔드포인트 목록 읽기
            # with open(endpoint_file, 'r') as f:
            #     user_endpoints = [line.strip() for line in f if line.strip()]
            
            self.logger.info(f"{len(user_endpoints)}개의 사용자 엔드포인트 템플릿을 로드했습니다.")
            
            # 사용자 ID 패턴 목록 - {}는 포맷팅용 플레이스홀더
            id_patterns = self.id_patterns
            # 테스트할 모든 URL 생성
            all_urls = []
            for endpoint in user_endpoints:
                endpoint = endpoint.strip('/')  # 앞뒤 슬래시 제거
                
                for pattern in id_patterns:
                    # 패턴이 {} 하나만 있는 경우는 경로 자체를 대체
                    if pattern == '{}':
                        formatted_endpoints = [f"/{endpoint}/{user_id}" for user_id in user_id_range]
                    else:
                        # 쿼리스트링 패턴의 경우
                        connector = '&' if '?' in endpoint else '?'
                        formatted_endpoints = [f"/{endpoint}{connector}{pattern.lstrip('?')}".format(user_id) 
                                            for user_id in user_id_range]
                    
                    for url in formatted_endpoints:
                        all_urls.append((url, endpoint, pattern))
            
            # 병렬 처리를 위한 함수
            def check_url(url_info):
                url, original_endpoint, pattern = url_info
                full_url = urljoin(self.target_url, url)

                try:
                    response = self.session.get(full_url, allow_redirects=True, verify=self.verify_ssl, timeout=self.timeout)

                    if response.status_code == 200:
                        # 에러 페이지 체크
                        if self.is_error_page(response):
                            return None

                        # 로그인 페이지로 리다이렉트되었는지 체크
                        if 'login' in response.url.lower() or 'signin' in response.url.lower():
                            return None

                        # 사용자 정보 관련 키워드 (더 구체적)
                        user_keywords = self.user_keywords
                        content = response.text.lower()

                        # 사용자 정보가 실제로 포함되어 있는지 확인
                        if any(keyword in content for keyword in user_keywords):
                            # 추가 검증: 실제 사용자 데이터가 있는지 확인
                            # (이메일, 전화번호, 주소 등의 패턴)
                            has_user_data = any([
                                '@' in content and '.' in content,  # 이메일 패턴
                                'phone' in content or '전화' in content,
                                'address' in content or '주소' in content,
                                'email' in content or '이메일' in content
                            ])

                            if has_user_data:
                                return {
                                    'url': full_url,
                                    'status': '취약',
                                    'description': f'사용자 ID 조작으로 타 사용자 개인정보 접근 가능 (IDOR)',
                                    'check_type': 'user_id_manipulation',
                                    'original_endpoint': original_endpoint,
                                    'tested_pattern': pattern
                                }
                except Exception as e:
                    self.logger.error(f"{full_url}에 대한 사용자 ID 조작 검사 중 오류 발생: {str(e)}")

                return None
                
            # URL을 배치로 나누어 병렬 처리
            batch_size = 1000
            total_urls = len(all_urls)
            num_batches = (total_urls + batch_size - 1) // batch_size
            
            for batch_num in range(num_batches):
                start_idx = batch_num * batch_size
                end_idx = min((batch_num + 1) * batch_size, total_urls)
                current_batch = all_urls[start_idx:end_idx]
                
                print(f"사용자 ID 조작 검사 진행 중: 배치 {batch_num + 1}/{num_batches} ({start_idx+1}-{end_idx}/{total_urls} URLs)")
                
                with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                    futures = [executor.submit(check_url, url_info) for url_info in current_batch]
                    
                    for future in tqdm(concurrent.futures.as_completed(futures), total=len(current_batch), desc="URL 검사 중"):
                        result = future.result()
                        if result:
                            results.append(result)
                            self.logger.info(f"사용자 ID 조작 검사 성공: {result['url']}")
                            
        except Exception as e:
            self.logger.error(f"사용자 ID 조작 검사 중 오류 발생: {str(e)}")
        
        return results


    #조재호 수정버전
    def get_url_lists(self, file_name: str) -> List[str]:
        urls_with_line_numbers = []
        count = 0

        try:
            with open(f"../etc/{file_name}", 'r') as f:
                for line_number, line in enumerate(f, 1):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        urls_with_line_numbers.append((line, line_number))
                        count += 1
                        # if max_urls and count >= max_urls:
                        #     break
            # with open(, "r") as f:
            #     return f.read().splitlines()
        except FileNotFoundError:
            self.logger.error(f"파일을 찾을 수 없습니다: {file_name}")
            return []

        return urls_with_line_numbers
    
    #조재호 수정버전
    def run(self):
        results = []
        # details = []

        #기존코드에 endpoint_file 리턴이 없어서 주석
        protected_urls = self.get_url_lists("A04_common.txt")
        admin_urls = self.get_url_lists("A04_general.txt")
        endpoint_urls = self.get_url_lists("A04_endpoint.txt")

        # 1. 직접 접근
        print(f"- 직접 URL 접근 검사 시작")
        results.extend(self.check_direct_url_access(protected_urls_with_lines=protected_urls, source_file="common.txt"))
        
        # 2. 세션 조작
        print(f"- 세션 조작 검사 시작")
        results.extend(self.check_session_manipulation())

        # 3. 권한 상승
        print(f"- 권한 상승 검사 시작")
        results.extend(self.check_privilege_escalation(admin_urls_with_lines=admin_urls, source_file="general.txt"))

        # 4. 사용자 ID 조작
        print(f"- 사용자 ID 조작 검사 시작")
        results.extend(self.check_user_id_manipulation(user_endpoints=endpoint_urls))


        details = self.parse_scan_results(results)

        print(f"Permission_bypass22 검사 완료: {len(results)}개 취약점 발견")


        return details
    


        

def read_file_with_lines(file_path, max_urls=None):
    """
    파일에서 URL을 읽어오고 각 URL의 줄 번호도 함께 반환합니다.
    max_urls가 지정되면 최대 해당 개수까지만 읽습니다.
    """
    if not os.path.exists(file_path):
        print(f"경고: 파일이 존재하지 않습니다 - {file_path}")
        return None
    
    try:
        urls_with_line_numbers = []
        count = 0
        
        with open(file_path, 'r') as f:
            for line_number, line in enumerate(f, 1):
                line = line.strip()
                if line and not line.startswith('#'):
                    urls_with_line_numbers.append((line, line_number))
                    count += 1
                    if max_urls and count >= max_urls:
                        break
        
        print(f"{file_path}에서 {len(urls_with_line_numbers)}개를 읽어왔습니다.")
        return urls_with_line_numbers
    except Exception as e:
        print(f"파일 읽기 오류 ({file_path}): {str(e)}")
        return None

# def get_url_lists(common_path=None, general_path=None, max_urls=None):
#     """URL 리스트를 파일에서 읽어옵니다."""
#     # 현재 스크립트의 디렉토리 경로 가져오기
#     script_dir = os.path.dirname(os.path.abspath(__file__))
#     project_dir = "/home/ruqos/Desktop/project" # Desktop/project 디렉토리
#     
#     
#     
#     # common.txt 경로 설정 (protected_urls용)
#     if common_path:
#         protected_path = common_path
#     else:
#         protected_path = os.path.join(project_dir, 'etc', 'common.txt')
#     
#     # general.txt 경로 설정 (admin_urls용)
#     if general_path:
#         admin_path = general_path
#     else:
#         admin_path = os.path.join(project_dir, 'etc', 'general.txt')
# 
#     # endpoint.txt 경로 설정 (user_id_manipulation용)
#     endpoint_path = os.path.join(project_dir, 'etc', 'A10_endpoint.txt')
#     if endpoint_path:
#         endpoint_path = endpoint_path
#     
#     print(f"protected_urls 파일 경로: {protected_path}")
#     print(f"admin_urls 파일 경로: {admin_path}")
#     
#     # 파일에서 URL 읽기
#     protected_urls = read_file_with_lines(protected_path, max_urls)
#     admin_urls = read_file_with_lines(admin_path, max_urls)
#     
#     # 파일 읽기 실패 시 기본값 사용
#     if not protected_urls:
#         print(f"common.txt 파일을 읽을 수 없어 기본 URL 목록을 사용합니다.")
#         default_urls = read_file()["default_urls"]
#         protected_urls = [(url, 0) for url in default_urls]
#         protected_path = "기본 protected_urls 목록"
#     
#     if not admin_urls:
#         print(f"general.txt 파일을 읽을 수 없어 기본 URL 목록을 사용합니다.")
#         default_urls = read_file()["default_urls"]
#         admin_urls = [(url, 0) for url in default_urls]
#         admin_path = "기본 admin_urls 목록"
#     
#     return protected_urls, admin_urls, protected_path, admin_path, endpoint_path

# def check_permission_bypass(target_url, timeout=3, max_workers=20, batch_size=1000):
#     """
#     main_test.py에서 직접 호출할 수 있는 권한 우회 검사 함수
#     (크롤링 없이 텍스트 파일 기반으로 검사)
#     results.json 파일을 읽어와서 A04-03 테스트 결과를 업데이트하고 반환
#     """
#     from datetime import datetime
#     
#     logging.basicConfig(level=logging.INFO)
#     logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)
# 
#     # etc/common.txt, general.txt 파일에서 URL 목록 읽기
#     protected_urls, admin_urls, protected_path, admin_path, endpoint_path = get_url_lists()
# 
#     scanner = PermissionBypassScanner(
#         target_url=target_url,
#         verify_ssl=False,
#         timeout=timeout,
#         max_workers=max_workers
#     )
# 
#     print(f"\n[!] '{target_url}' 대상으로 권한 우회 취약점 검사를 시작합니다...")
# 
#     # 각 테스트별 결과 수집
#     direct_results = []
#     session_results = []
#     privilege_results = []
#     user_id_results = []
# 
#     # 1. 직접 접근
#     print(f"- 직접 URL 접근 검사 시작")
#     direct_results = scanner.check_direct_url_access(protected_urls, protected_path, batch_size)
# 
#     # 2. 세션 조작
#     print(f"- 세션 조작 검사 시작")
#     session_results = scanner.check_session_manipulation()
# 
#     # 3. 권한 상승
#     print(f"- 권한 상승 검사 시작")
#     privilege_results = scanner.check_privilege_escalation(admin_urls, admin_path, batch_size)
# 
#     # 4. 사용자 ID 조작
#     print(f"- 사용자 ID 조작 검사 시작")
#     user_id_results = scanner.check_user_id_manipulation(endpoint_path)
# 
#     # results.json 파일을 읽어와서 업데이트
#     results_file_path = "../etc/results.json"
#     
#     try:
#         # 기존 results.json 파일 읽기
#         if os.path.exists(results_file_path):
#             with open(results_file_path, 'r', encoding='utf-8') as f:
#                 results = json.load(f)
#         else:
#             print(f"결과 파일을 찾을 수 없습니다: {results_file_path}")
#             return None
#         
#         # A04 카테고리의 Permission_bypass 테스트 결과 업데이트
#         for test in results["categories"]["A04"]["tests"]:
#             if test["test_id"] == "A04-03":  # Permission_bypass 테스트
#                 # 모든 결과를 details 형식으로 변환
#                 details = []
#                 
#                 # 각 테스트 결과를 details에 추가
#                 for result in direct_results:
#                     details.append({
#                         "url": result.get('url', ''),
#                         "method": "GET", 
#                         "issue": result.get('description', ''),
#                         "timestamp": datetime.now().isoformat()
#                     })
#                 
#                 for result in session_results:
#                     details.append({
#                         "url": target_url,
#                         "method": "GET",
#                         "issue": result.get('description', ''),
#                         "timestamp": datetime.now().isoformat()
#                     })
#                 
#                 for result in privilege_results:
#                     details.append({
#                         "url": result.get('url', ''),
#                         "method": "GET",
#                         "issue": result.get('description', ''),
#                         "timestamp": datetime.now().isoformat()
#                     })
#                 
#                 for result in user_id_results:
#                     details.append({
#                         "url": result.get('url', ''),
#                         "method": "GET", 
#                         "issue": result.get('description', ''),
#                         "timestamp": datetime.now().isoformat()
#                     })
#                 
#                 # 위험도 결정
#                 total_vulnerabilities = len(details)
#                 if total_vulnerabilities == 0:
#                     risk_level = ""
#                 elif total_vulnerabilities <= 2:
#                     risk_level = "MEDIUM"
#                 else:
#                     risk_level = "HIGH"
#                 
#                 # 테스트 결과 업데이트
#                 test["test_name"] = "Permission_bypass"
#                 test["risk_level"] = risk_level
#                 test["items_tested"] = total_vulnerabilities + len(protected_urls) + len(admin_urls)
#                 test["vulnerable_items"] = total_vulnerabilities
#                 test["details"] = details
#                 break
# 
#         with open("test_Permission1.json", 'w', encoding='utf-8') as f:
#             json.dump(results, f, indent=2, ensure_ascii=False)
# 
#         print(f"Permission_bypass111 검사 완료: {len(details)}개 취약점 발견")
# 
#         # 요약 정보 업데이트 (단일 테스트용)
#         results["summary"]["total_tests"] = 1
#         results["summary"]["total_vulnerabilities"] = len([test for test in results["categories"]["A04"]["tests"] if test["test_id"] == "A04-03"][0]["details"])
#         
#         # 위험도별 분포 업데이트
#         for key in results["summary"]["risk_distribution"]:
#             results["summary"]["risk_distribution"][key] = 0
#             
#         current_risk = [test for test in results["categories"]["A04"]["tests"] if test["test_id"] == "A04-03"][0]["risk_level"]
#         if current_risk:
#             results["summary"]["risk_distribution"][current_risk] = 1
#         
#         # 파일에 저장하지 않고 결과만 반환
#         print(f"Permission_bypass 검사 완료: {len([test for test in results['categories']['A04']['tests'] if test['test_id'] == 'A04-03'][0]['details'])}개 취약점 발견")
#         
#         # 전체 results 구조 반환 (파일은 수정하지 않음)
#         return results
#         
#     except Exception as e:
#         print(f"결과 처리 중 오류 발생: {e}")
#         return None

def start_permission_bypass(config):
    """main_test.py에서 호출되는 함수 - JSON 결과 반환"""
    obj = PermissionBypassScanner(config.get("web_url"))
    result = obj.run()
    # return check_permission_bypass(config.get("web_url"), timeout=3, max_workers=20, batch_size=1000)
    
    with open("Permission_bypass_result.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(result, indent=2, ensure_ascii=False))

    return result

if __name__ == "__main__":
    USER_INFO_PATH = "../etc/user_info.json"

    with open(USER_INFO_PATH, "r") as f:
        config = json.load(f)
    
    result = start_permission_bypass(config)

    # print(json.dumps(result, indent=2, ensure_ascii=False))
    