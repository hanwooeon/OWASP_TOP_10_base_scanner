import aiohttp
import asyncio
import logging
from urllib.parse import urljoin
import json



logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

def parse_scan_results(vulnerabilities):
    details = []

    if not vulnerabilities:
        return details

    for vuln in vulnerabilities:
        details.append({
                "file": vuln['path'],
                "line": vuln['line'],
                "pattern": vuln['pattern']
            }
        )

    return details

async def RequestHandler(session, url, method, headers, body):
    try:
        async with session.request(method, url, headers=headers, data=body) as response:
            # response 데이터를 미리 읽어서 객체로 반환
            response_data = {
                'status': response.status,
                'headers': dict(response.headers),
                'text': await response.text()
            }
            return response_data
    except Exception as e:
        logging.error(f"요청 오류: {e}")
        return None

async def RateLimiter(response_data):
    if response_data is None:
        return False

    status = response_data['status']
    headers = response_data['headers']
    text = response_data['text']

    if status == 429:
        logging.warning("429 Too Many Requests 상태 감지")

        retry_after = headers.get('Retry-After')
        rate_limit = headers.get('X-RateLimit-Limit')
        rate_remaining = headers.get('X-RateLimit-Remaining')
        rate_reset = headers.get('X-RateLimit-Reset')

        if retry_after:
            logging.info(f"{retry_after}초 후 재시도 권장")
        if rate_limit:
            logging.info(f"요청 가능 횟수: {rate_limit}")
        if rate_remaining:
            logging.info(f"남은 요청 가능 횟수: {rate_remaining}")
        if rate_reset:
            logging.info(f"요청 가능 횟수 초기화 시간: {rate_reset}")

    if "too many requests" in text.lower():
        logging.warning("응답 본문에 'too many requests' 문자열 포함됨")
        return True

    return status == 429

async def test_rate_limit_on_endpoint(session, target_url, method, headers, inputs, max_requests=3):
    """특정 엔드포인트에 대해 Rate Limit 테스트"""
    rate_limited = False
    successful_requests = 0
    
    for i in range(max_requests):
        try:
            res = await RequestHandler(session, target_url, method, headers, inputs)
            if res:
                # Rate Limit 확인
                if await RateLimiter(res):
                    logging.info(f"Rate Limit 탐지됨 (요청 {i+1}회 후): {target_url}")
                    rate_limited = True
                    break
                successful_requests += 1
            await asyncio.sleep(0.01)  # 간격 단축
        except Exception as e:
            logging.error(f"요청 실패: {e}")
            break
    
    if not rate_limited and successful_requests >= max_requests:
        logging.warning(f"Rate Limit 없음: {target_url} ({max_requests}회 연속 요청 성공)")
    
    return rate_limited

def load_sensitive_endpoints():
    """민감한 엔드포인트 목록을 파일에서 로드"""
    endpoints = []
    try:
        with open("etc/A04_rate_limit_endpoint.txt", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    endpoints.append(line)
    except FileNotFoundError:
        logging.warning("A04_rate_limit_endpoint.txt 파일을 찾을 수 없습니다. 기본 패턴을 사용합니다.")
        # 기본 패턴
        endpoints = ['/login', '/signin', '/auth', '/register', '/payment', '/admin']
    return endpoints

def is_sensitive_endpoint(url, form_action):
    """민감한 엔드포인트인지 확인"""
    sensitive_endpoints = load_sensitive_endpoints()
    
    full_url = url.lower()
    if form_action:
        full_url += form_action.lower()
    
    # 정확한 매칭 또는 부분 매칭 확인
    for endpoint in sensitive_endpoints:
        if endpoint.lower() in full_url:
            return True
    
    return False

async def start_rate_limit(obj_list, config):
    """details만 반환하는 Rate Limit 테스트 함수"""
    from datetime import datetime
    
    endpoints_tested = 0

    # 하나의 세션을 공유해서 사용
    async with aiohttp.ClientSession() as session:
        # 민감한 엔드포인트만 필터링해서 테스트
        tasks = []
        for obj in obj_list:
            for form in obj.formData:
                target_url = urljoin(config["web_url"], form['action']) if form.get('action') else obj.path
                
                # 민감한 엔드포인트인지 확인
                if is_sensitive_endpoint(obj.path, form.get('action')):
                    endpoints_tested += 1
                    logging.info(f"민감 엔드포인트 발견: {target_url}")
                    
                    method = form.get('method', 'POST').upper()
                    inputs = form['inputs']
                    headers = form['headers']
                    
                    # 병렬 실행을 위한 태스크 생성
                    task = test_rate_limit_on_endpoint(session, target_url, method, headers, inputs)
                    tasks.append(task)
                else:
                    logging.debug(f"일반 엔드포인트 스킵: {target_url}")
        
        # 모든 태스크를 병렬로 실행 (최대 5개씩)
        logging.info(f"총 {len(tasks)}개 민감 엔드포인트 테스트 시작...")
        
        semaphore = asyncio.Semaphore(5)  # 동시 요청 수 제한
        
        async def limited_test(task):
            async with semaphore:
                return await task
        
        results_list = await asyncio.gather(*[limited_test(task) for task in tasks], return_exceptions=True)
    
    # 결과 처리 및 상세 정보 수집
    details = []
    tested_endpoints = []
    
    # 테스트된 엔드포인트 정보 수집
    task_index = 0
    for obj in obj_list:
        for form in obj.formData:
            target_url = urljoin(config["web_url"], form['action']) if form.get('action') else obj.path
            if is_sensitive_endpoint(obj.path, form.get('action')):
                method = form.get('method', 'POST').upper()
                tested_endpoints.append({
                    'url': target_url,
                    'method': method,
                    'index': task_index
                })
                task_index += 1
    
    # 취약점 탐지 결과만 수집 (Rate Limiting이 없는 경우만)
    # 중복 제거를 위한 set (쿼리 문자열 제외한 base path + method 조합)
    seen_vulnerabilities = set()

    for i, rate_limited in enumerate(results_list):
        if isinstance(rate_limited, Exception):
            logging.error(f"테스트 실패: {rate_limited}")
            continue

        if i < len(tested_endpoints):
            endpoint = tested_endpoints[i]
            if not rate_limited:
                # URL에서 쿼리 문자열 제거 (path만 추출)
                from urllib.parse import urlparse
                parsed = urlparse(endpoint['url'])
                base_path = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

                # (base_path, method) 조합으로 중복 체크
                vuln_key = (base_path, endpoint['method'])

                if vuln_key not in seen_vulnerabilities:
                    seen_vulnerabilities.add(vuln_key)
                    details.append({
                        "url": base_path,  # 쿼리 문자열 제외한 clean URL
                        "method": endpoint['method'],
                        "issue": "Rate Limiting 미적용 - 연속 요청 성공",
                        "timestamp": datetime.now().isoformat()
                    })

    logging.info(f"Rate Limit 검사 완료: {len(details)}개 고유 취약점 발견 (중복 제거됨)")
    return details

def run(obj_list, config):
    return asyncio.run(start_rate_limit(obj_list, config))

# def main(obj_list, config):
#     """main_test.py에서 호출되는 함수 - JSON 결과 반환"""
#     return asyncio.run(start_rate_limit(obj_list, config))
    

if __name__ == "__main__":
    from add_in.crawl2 import start_crawl2

    USER_INFO_PATH = "etc/user_info.json"

    with open(USER_INFO_PATH, "r") as f:
        config = json.load(f)
        
    obj_list = start_crawl2(config["web_url"],"","")

    details = run(obj_list, config)

    print(json.dumps(details, indent=2, ensure_ascii=False))

    with open("Rate_Limit_result.json", "w", encoding="utf-8") as f:
        json.dump(details, f, indent=2, ensure_ascii=False)