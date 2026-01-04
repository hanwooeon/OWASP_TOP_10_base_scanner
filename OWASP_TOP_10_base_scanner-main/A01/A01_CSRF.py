# csrf_scanner_class.py
import requests
from bs4 import BeautifulSoup
import re
from http.cookies import SimpleCookie
import json, csv, os
from datetime import datetime

# --- 설정 (환경에 맞게 수정) ---

OUTPUT_DIR = "./csrf_reports"
TIMEOUT = 8

CSRF_NAME_CANDIDATES = [
    "csrf", "_csrf", "csrf_token", "_token", "authenticity_token",
    "__requestverificationtoken", "xsrf-token", "x-csrf-token",
    "x-xsrf-token", "csrfmiddlewaretoken", "anti_csrf", "__csrf"
]

JS_TOKEN_PATTERNS = [
    r"var\s+([a-zA-Z0-9_]*csrf[a-zA-Z0-9_]*)\s*=\s*['\"]([^'\"]+)['\"]",
    r"window\.[a-zA-Z0-9_]*csrf[a-zA-Z0-9_]*\s*=\s*['\"]([^'\"]+)['\"]",
    r"['\"]csrf['\"]\s*:\s*['\"]([^'\"]+)['\"]",
    r"['\"]xsrf['\"]\s*:\s*['\"]([^'\"]+)['\"]"
]

class CSRFScanner:
    def __init__(self, base_url=None, timeout=TIMEOUT, session=None):
        self.base_url = base_url
        self.timeout = timeout
        self.session = session or requests.Session()
        # self.results = []

    def parse_scan_results(self, path, header_info, analysis, reason, severity):
        return {
                "path": f"{path}",
                "protections": header_info.get("protections", []),
                "samesite": header_info.get("samesite", False),
                "tokens_found": analysis.get("tokens", []),
                "forms": analysis["details"]["forms"],
                "meta": analysis["details"]["meta"],
                "js_tokens": analysis["details"]["js"],
                "severity": severity,
                "description": reason
            }

    # ---------- util ----------
    def _safe_get(self, url):
        """ 예외 처리된 GET 요청 """
        try:
            params = { }
            return self.session.get(url, timeout=self.timeout)
        except Exception as e:
            return None

    def _parse_set_cookie(self, header_value):
        """ Set-Cookie 헤더 파싱 """
        cookies = []
        if not header_value:
            return cookies
        if isinstance(header_value, list):
            lines = header_value
        else:
            lines = [header_value]
        for line in lines:
            try:
                sc = SimpleCookie()
                sc.load(line)
                for morsel in sc.values():
                    cookies.append({"name": morsel.key, "value": morsel.value, "raw": line})
            except Exception:
                cookies.append({"name": None, "value": None, "raw": line})
        return cookies

    # ---------- HTML analysis ----------
    def analyze_html_for_tokens(self, html_text):
        """ HTML 내에서 CSRF 토큰 후보 추출 """
        soup = BeautifulSoup(html_text or "", 'html.parser')
        details = {"forms": [], "meta": [], "js": []}
        found_tokens = []

        # form 분석
        forms = soup.find_all('form')
        for f in forms:
            method = (f.get('method') or 'GET').strip().upper()
            action = f.get('action') or ''
            tokens = []
            for inp in f.find_all('input'):
                name = (inp.get('name') or '').lower()
                id_ = (inp.get('id') or '').lower()
                classes = ' '.join(inp.get('class') or []).lower()
                value = inp.get('value', '')
                for cand in CSRF_NAME_CANDIDATES:
                    if cand in name or cand in id_ or cand in classes:
                        tokens.append({"field": name or id_ or classes, "value": value})
                        found_tokens.append(value)
                        break
            details["forms"].append({"method": method, "action": action, "tokens": tokens})

        # meta 태그
        metas = soup.find_all('meta')
        for m in metas:
            mname = (m.get('name') or '').lower()
            content = m.get('content') or ''
            if 'csrf' in mname or 'token' in mname:
                details["meta"].append({"name": mname, "content": content})
                if content:
                    found_tokens.append(content)

        # inline JS heuristic
        scripts = soup.find_all('script')
        for s in scripts:
            text = s.string or s.get_text() or ''
            if not text.strip():
                continue
            for pat in JS_TOKEN_PATTERNS:
                for m in re.finditer(pat, text, flags=re.IGNORECASE):
                    # 가장 마지막 group을 토큰 후보로 취함
                    token = m.group(len(m.groups()))
                    details["js"].append({"pattern": pat, "token_sample": token[:80]})
                    if token:
                        found_tokens.append(token)

        found_tokens = list(set([t for t in found_tokens if t]))
        return {"details": details, "tokens": found_tokens}

    # ---------- header 분석 ----------
    def analyze_headers(self, header_dict):
        """ 응답 헤더에서 CSRF 보호 관련 정보 추출 """

        h = {k.lower(): v for k, v in (header_dict or {}).items()}
        protections = []
        if h.get('x-csrf-token') or h.get('x-xsrf-token'):
            protections.append('X-CSRF-Token')
        if h.get('x-requested-with', '').lower() == 'xmlhttprequest':
            protections.append('X-Requested-With')
        set_cookie = h.get('set-cookie')
        cookies = self._parse_set_cookie(set_cookie)
        samesite = any('samesite=strict' in (c.get('raw','').lower()) or 'samesite=lax' in (c.get('raw','').lower()) for c in cookies)
        if samesite:
            protections.append('SameSite-Cookie')
        return {"protections": protections, "cookies": cookies, "samesite": samesite}

    # ---------- 분류 규칙 ----------
    def classify(self, path, header_info, token_info):
        """ 분류 규칙 (심각도, 사유) 반환"""
        post_forms = [f for f in token_info.get("details", {}).get("forms", []) if f["method"] == "POST"]
        has_token = bool(token_info.get("tokens"))
        has_header_protection = bool(header_info.get("protections"))
        samesite_present = header_info.get("samesite", False)

        if post_forms:
            forms_without_token = [f for f in post_forms if not f["tokens"]]
            if forms_without_token:
                return "High", f"{len(forms_without_token)} POST form(s) without CSRF token"
            else:
                if has_header_protection or samesite_present:
                    return "Low", "POST forms have token and header/cookie protections"
                else:
                    if any(token_info["details"]["js"]) and not token_info["details"]["forms"]:
                        return "Medium", "Token only found in JS (dynamic); server-side validation uncertain"
                    return "Medium", "POST forms have tokens but missing header/cookie protections"
        else:
            if has_token or has_header_protection or samesite_present:
                return "Info", "No POST forms; token/header present but not protecting forms directly"
            else:
                return "Info", "No POST forms and no CSRF indicators; further API tests recommended"

    # ---------- 대상 감사 (메인) ----------
    def audit_targets(self, base_url, obj_list):
        results = []
        # 메인 페이지 한 번 미리 조회 (공통 토큰 가능성)
        main_html = ""
        if base_url:
            resp = self._safe_get(base_url)
            if resp is not None:
                main_html = resp.text

        for obj in obj_list:
            if isinstance(obj, dict):
                path = obj.get('path', '')
                header = obj.get('header', {})
            else:
                path = obj.path
                header = obj.header 

            # full URL 구성
            if path.startswith('http://') or path.startswith('https://'):
                full_url = path
            else:
                full_url = (base_url.rstrip('/') + '/' + path.lstrip('/')) if base_url else path

            # HTML 분석
            resp = self._safe_get(full_url)
            html = resp.text if resp is not None else ""
            analysis = self.analyze_html_for_tokens(html or main_html)

            # header 분석
            header_info = self.analyze_headers(header)
            analysis["cookies"] = header_info.get("cookies", [])

            severity, reason = self.classify(path, header_info, analysis)

            findings = self.parse_scan_results(path, header_info, analysis, reason, severity)
            results.append(findings)
            print(f"[{severity}] {path} -> {reason} (tokens:{len(findings['tokens_found'])}, protections:{findings['protections']})")

        return results

    # ---------- 실행 (간단 래퍼) ----------
    def run(self, url, obj_list):
        base_url = url
       
        details = self.audit_targets(base_url, obj_list)
        
        return details

if __name__ == "__main__":
    scanner = CSRFScanner()

    CONFIG_PATH = "../etc/user_info.json"
    OBJ_LIST_PATH = "../add_in/web_data.json"

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            cfg = json.load(f)
    with open(OBJ_LIST_PATH, "r", encoding="utf-8") as f:
        obj_list = json.load(f)

    details = scanner.run(cfg.get('web_url'), obj_list)


    with open("./csrf_report.json", "w", newline='', encoding="utf-8") as f:
        json.dump(details, f, ensure_ascii=False, indent=2)
