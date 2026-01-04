from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from urllib.parse import urlparse, urljoin, unquote, parse_qs, urlencode
import json
import time

INPUT_FILE = "/home/ruqos/Desktop/project/etc/crawl_input_type.json"

def read_file():
    with open(f"{INPUT_FILE}", "r") as file:
        return json.load(file)

class FrontCode():
    seen_forms_global = set()  # 클래스 단위로 전역 중복 방지

    def __init__(self, path, header, types):
        self.header = header
        self.path = path
        self.login_form = list()
        self.formData = list() # form > action, form > method, input > name, input > valuse, input > type
        self.types= types
    
    def __dict__(self):
        return {
            "path": self.path,
            "header": dict(self.header),  # ← dict로 변환
            "login_form": self.login_form,
            "formData": self.formData,
            "types": self.types            
        }
    
    def get(self, key, default=None):
        return getattr(self, key, default)

    def is_input_field(self, input_tag):
        non_input_types = self.types['non_input_types'] 
        input_types = self.types['input_types']
        
        input_type = input_tag.get('type', 'text').lower()
        if input_type in non_input_types:
            return False
        if input_type not in input_types:
            input_type = 'text'

        if input_tag.has_attr('disabled') or input_tag.has_attr('readonly'):
            return False

        value = input_tag.get('value', '').strip()
        name = input_tag.get('name', '').strip()
        input_id = input_tag.get('id', '').strip()
        likely_placeholder_value = {name, input_id}

        value_condition = value == '' or value in likely_placeholder_value
        has_placeholder = input_tag.has_attr('placeholder')
        autocomplete_off = input_tag.get('autocomplete', '').lower() == 'off'

        return value_condition or has_placeholder or autocomplete_off

    def getFormData(self, html, url=""):
        soup = BeautifulSoup(html, "html.parser")
        forms = soup.find_all("form")

        for form in forms:
            form_action = form.get("action", "")
            form_method = form.get("method", "get").lower()
            inputs = form.find_all("input")
            textarea = form.find_all("textarea")
            input_data = {}

            if form_action == "" or form_action == "#":
                form_action = self.path

            if urlparse(form_action).netloc == '':
                form_action = urljoin(url, form_action)

            # 리다이렉션 루프가 있는 form action 필터링
            if 'login?back=' in form_action and form_action.count('login') > 1:
                print(f"[🚫] 리다이렉션 루프 폼 제외: {form_action[:100]}...")
                continue

            passTF = False
            
            for inp in inputs:
                name = inp.get("name")
                value = inp.get("value", "payload")
                type = inp.get("type", "text")
                
                if type == "password":
                    passTF = True
                    
                if name:
                    input_data[name] = "payload" if self.is_input_field(inp) else value
                    
            for inp in textarea:
                name = inp.get("name")
                value = inp.get("value", "payload")
                type = inp.get("type", "text")
                
                if type == "password":
                    passTF = True
                    
                if name:
                    input_data[name] = "payload" if self.is_input_field(inp) else value
                
            if not input_data:
                continue

            form_key = (
                form_action.strip(),
                form_method,
                tuple(sorted(input_data.items()))
            )

            if form_key in FrontCode.seen_forms_global:
                continue
            FrontCode.seen_forms_global.add(form_key)

            form_info = {
                "action": form_action,
                "method": form_method,
                "inputs": input_data,
                "headers": dict(self.header)  # ← dict로 변환
            }
            
            if passTF:
                self.login_form.append(form_info)
            
            self.formData.append(form_info)


visited = set()
page_contents = {}  # URL별 HTML 콘텐츠 저장

def normalize_url(url):
    """URL을 정규화하여 중복 방지 (back, redirect 파라미터 제거)"""
    parsed = urlparse(url)

    # back 파라미터가 있으면 제거 (리다이렉션 루프 방지)
    if parsed.query:
        params = parse_qs(parsed.query)
        # back, redirect 등 리다이렉션 관련 파라미터 제거
        params.pop('back', None)
        params.pop('redirect', None)
        new_query = urlencode(params, doseq=True)
        normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        if new_query:
            normalized += f"?{new_query}"
        return normalized

    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

def crawl2(page, url, base_domain, depth=3, start_url=""):

    # URL 정규화
    normalized_url = normalize_url(url)
    clean_url = unquote(normalized_url)

    if depth > 3 or clean_url in visited or len(visited) > 100:
        return

    # 로그인 페이지는 한 번만 크롤링
    if 'login' in clean_url.lower() or 'auth' in clean_url.lower() or 'connexion' in clean_url.lower():
        if any('login' in v.lower() or 'auth' in v.lower() or 'connexion' in v.lower() for v in visited):
            print(f"[🚫] 로그인 페이지 중복 차단: {url}")
            return

    visited.add(clean_url)
    print(f"[✔] 크롤링: {url} (깊이: {depth})")

    try:
        # 해시(#) URL 처리 - SPA 라우팅
        if '#' in url:
            # 해시가 있는 경우, JavaScript로 직접 navigate
            page.evaluate(f"window.location.hash = '{url.split('#')[1]}'")
            page.wait_for_timeout(500)  # 500ms로 단축
            response = None
        else:
            # Playwright로 페이지 로드 (networkidle 대신 domcontentloaded 사용 - 훨씬 빠름)
            response = page.goto(url, timeout=5000, wait_until='domcontentloaded')

            if not response:
                print(f"[!] 응답 없음: {url}")
                return

            # 현재 URL 확인 (리다이렉트 체크)
            current_url = page.url

            # 리다이렉션이 발생했는지 확인
            if current_url != url:
                # 로그인 페이지로 리다이렉션되었는지 확인
                if 'login' in current_url.lower() or 'auth' in current_url.lower() or 'connexion' in current_url.lower():
                    print(f"[🚫] 로그인 필요 페이지로 리다이렉션: {url} → {current_url}")
                    return

                # 이미 방문한 페이지로 리다이렉션된 경우
                normalized_current = normalize_url(current_url)
                if unquote(normalized_current) in visited:
                    print(f"[🚫] 이미 방문한 페이지로 리다이렉션: {url} → {current_url}")
                    return

            # HTTP 에러 상태 확인
            if response.status >= 400:
                print(f"[!] HTTP 에러: {url} (상태: {response.status})")
                return

            # JavaScript 렌더링 대기 (최소화)
            page.wait_for_timeout(300)  # 300ms로 단축 (1500ms → 300ms)

        # 현재 URL 재확인 (JavaScript 실행 후)
        current_url = page.url
        current_domain = urlparse(current_url).netloc

        # localhost와 127.0.0.1을 같은 것으로 처리
        def normalize_domain(domain):
            # 포트 포함하여 정규화
            if domain.startswith('localhost'):
                return domain.replace('localhost', '127.0.0.1')
            return domain

        normalized_current = normalize_domain(current_domain)
        normalized_base = normalize_domain(base_domain)

        # 다른 도메인으로 리다이렉트된 경우 중단
        if normalized_current != normalized_base:
            print(f"[🚫] 외부 도메인으로 리다이렉트: {current_url}")
            return

        # 렌더링된 HTML 가져오기
        html_content = page.content()
        page_contents[clean_url] = html_content

        soup = BeautifulSoup(html_content, 'html.parser')

        for link in soup.find_all('a'):
            href = link.get('href')
            if not href:
                continue

            # 외부 링크 필터링 (localhost와 127.0.0.1을 같은 것으로 처리)
            if href.startswith('http'):
                href_domain = urlparse(href).netloc
                normalized_href_domain = normalize_domain(href_domain)
                if normalized_href_domain != normalized_base:
                    continue

            # 해시(#) 링크 처리 - SPA 라우팅
            if href.startswith('#/'):
                # 시작 URL에 해시 경로 추가
                full_url = start_url.split('#')[0] + href
            else:
                full_url = urljoin(url, href)

            parsed_url = urlparse(full_url)

            # 같은 도메인만 크롤링 (localhost와 127.0.0.1 정규화)
            if parsed_url.netloc != '':
                normalized_link_domain = normalize_domain(parsed_url.netloc)
                if normalized_link_domain != normalized_base:
                    continue

            clean_full_url = unquote(full_url)

            skip_patterns = ['.css', '.js', '.jpg', '.jpeg', '.png', '.gif', '.pdf',
                            '/images/', '/css/', '/js/', '/modules/', '/pdf/', '/redirect']
            if any(pattern in full_url.lower() for pattern in skip_patterns):
                continue

            if (clean_full_url not in visited and
                not ('/login?back=' in full_url and full_url.count('login') > 1)):
                crawl2(page, full_url, base_domain, depth + 1, start_url)

    except Exception as e:
        print(f"[에러] {url}: {e}")


def start_crawl2(url, login_path, login_data):
    print("[✔] Playwright 기반 크롤링 시작...")
    obj_list = list()

    # visited와 page_contents 초기화
    global visited, page_contents
    visited = set()
    page_contents = {}

    start_url = url
    base_domain = urlparse(start_url).netloc
    print(f"[✔] Base Domain: {base_domain}")

    with sync_playwright() as p:
        # Chromium 브라우저 실행 (헤드리스 모드)
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = context.new_page()

        # 불필요한 리소스 차단으로 속도 향상 (이미지, 폰트, 스타일시트 등)
        page.route("**/*", lambda route: route.abort() if route.request.resource_type in ["image", "font", "stylesheet", "media"] else route.continue_())

        # 로그인 처리 (login_data가 있는 경우)
        if login_path and login_data:
            login_url = urljoin(url, login_path)
            print(f"[✔] 로그인 시도: {login_url}")
            try:
                page.goto(login_url, timeout=5000, wait_until='domcontentloaded')
                page.wait_for_timeout(500)  # 1000ms → 500ms

                # 로그인 폼 자동 입력 (간단한 구현)
                for key, value in login_data.items():
                    try:
                        page.fill(f'input[name="{key}"]', value)
                    except:
                        pass

                # 로그인 버튼 클릭 시도
                try:
                    page.click('button[type="submit"]')
                    page.wait_for_timeout(1000)  # 2000ms → 1000ms
                except:
                    print("[!] 로그인 버튼을 찾을 수 없음")
            except Exception as e:
                print(f"[!] 로그인 실패: {e}")

        # 크롤링 시작
        crawl2(page, start_url, base_domain, 0, start_url)

        print(f"\n[✔] 크롤링 완료된 총 링크 수: {len(visited)}")

        types = read_file()

        # 저장된 HTML 콘텐츠로 폼 데이터 추출
        for path in visited:
            html_content = page_contents.get(path, "")
            if not html_content:
                continue

            # 헤더는 빈 딕셔너리로 설정 (Playwright에서는 response headers 접근이 다름)
            header = {}
            obj = FrontCode(path, header, types)
            obj.getFormData(html_content, start_url)

            if obj.formData != []:
                obj_list.append(obj)

        browser.close()

    return obj_list



if __name__ == "__main__":
    
    with open("../etc/user_info.json", "r", encoding="utf-8") as f:
        config = json.load(f)
    
    url = config["web_url"]

    obj_list = start_crawl2(url, "", "")

    li = []
    print(f"    → 크롤링 완료: {len(obj_list)}개 페이지 발견")
    for obj in obj_list:
        dic = obj.__dict__()
        li.append(dic)

    with open("./web_data.json", "w", encoding="utf-8") as f:
        json.dump(li, f, indent=4, ensure_ascii=False)

        # with open("./web_data.json", "w", encoding="utf-8") as f:
        #     json.dump(dic, f, indent=4, ensure_ascii=False)

    # with open("./web_data.json", "w", encoding="utf-8") as f:
    #     # json.dump(li, f, indent=4, ensure_ascii=False)
        
    # with open("./web_data.json", "w", encoding="utf-8") as f:
    #     f.write(a)

        # path = obj.path
        # for formdata in formlist:  #form 태그별 안에 있는 input 태그와 method 저장장
        #     method = formdata['method']
        #     action = formdata['action']
        #     inputs = formdata['inputs']

            # print(f"[*] URL: {path}\n, Method: {method}, Action: {action}, Inputs: {inputs}")