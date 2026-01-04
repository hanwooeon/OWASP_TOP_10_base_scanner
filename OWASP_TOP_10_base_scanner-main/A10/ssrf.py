from ProtocolHandler import ProtocolHandler
import json
import requests
from requests.adapters import HTTPAdapter, Retry
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, Optional


HEADERS = "../etc/headers.txt"
PROTOCOLS = "../etc/protocols.txt"


@dataclass
class ScanResult:
    url: str
    attack_type: str
    payload: str
    response_code: int
    response_size: int
    timestamp: datetime
    headers: Dict[str, str]
    is_vulnerable: bool
    verification_method: str = ""
    notes: str = ""

class SSRF(object):
    
    PREVIEW_LIBS = {
        # JavaScript / Node.js
        "JavaScript": [
            "open-graph-scraper",
            "metascraper",
            "unfurl.js",
            "Iframely",
            "Readability",
            "Puppeteer/Playwright",
        ],

        # React
        "React": [
            "react-tiny-link",
            "react-link-preview",
        ],

        # Python
        "Python": [
            "trafilatura",
            "extruct",
            "linkpreview",
            "metadata_parser",
            "newspaper3k",
            "goose3",
        ],

        # Ruby / Rails
        "Ruby": [
            "Onebox",
            "LinkThumbnailer",
            "MetaInspector",
        ],

        # PHP / Laravel
        "PHP": [
            "oscarotero/Embed",
            "php-OpenGraph",
            "essence",
            "WP oEmbed",
        ],

        # Java / Kotlin
        "Java": [
            "Jsoup",
            "OpenGraph-java",
            "Apache Tika",
            "Boilerpipe",
        ],
        
        "Kotlin": [
            "Jsoup",
            "OpenGraph-java",
            "Apache Tika",
            "Boilerpipe",
        ],

        # C# / .NET
        "C#": [
            "HtmlAgilityPack",
            "OpenGraphNet",
            "SmartReader",
        ],

        # Go
        "Go": [
            "otiai10/opengraph",
            "go-readability",
            "colly",
            "mvdan/xurls",
        ],

        # Rust
        "Rust": [
            "reqwest",
            "scraper",
            "opengraph-rs",
            "readability-rs",
        ],

        # Swift / iOS
        "Swift": [
            "LinkPresentation",
            "SwiftSoup",
            "OpenGraphSwift",
        ],

        # Elixir
        "Elixir": [
            "Floki",
            "opengraphx",
            "oembed",
        ]
    }
    
    def __init__(self, url):
        self.vulnerabilities = []
        
        self.url = url

        self.session = self._create_session()
        
        self.protocol_handler = ProtocolHandler()
        self.headers = self.load_list_from_file(HEADERS)
        self.protocols = self.load_list_from_file(PROTOCOLS)
    
    def run(self):
        print("ssrf Start")
        self.protocolAttack()

    def load_list_from_file(self, filepath):
        try:
            with open(filepath, 'r') as file:
                return [line.strip() for line in file if line.strip()]
        except Exception as e:
            # logging.error(f"Error loading list from {filepath}: {str(e)}")
            return []
    
    def _create_session(self):
        """Create and configure requests session"""
        session = requests.Session()
        retry_strategy = Retry(
            total=3,  # 3번 재시도
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504]
        )
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=10,
            pool_maxsize=10
        )
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session
    
    def make_request(self, url, method='GET', headers=None, timeout=None):
        """Enhanced request method with rate limiting and error handling"""
        try:
            self.throttler.pre_request()
            
            default_headers = {
                'User-Agent': self.config.scanner['user_agent'],
                'Accept': '*/*'
            }
            
            if headers:
                default_headers.update(headers)

            if self.cookies:
                if isinstance(self.cookies, str):
                    default_headers['Cookie'] = self.cookies
                elif isinstance(self.cookies, dict):
                    default_headers['Cookie'] = '; '.join([f'{k}={v}' for k, v in self.cookies.items()])

            response = self.session.request(
                method=method,
                url=url,
                headers=default_headers,
                timeout=timeout or self.config.scanner['timeout'],
                verify=self.config.scanner['verify_ssl'],
                allow_redirects=self.config.scanner['follow_redirects']
            )

            # Check for Set-Cookie header in response
            if self.config.scanner['capture_cookies'] and 'Set-Cookie' in response.headers and not self.cookies:
                self.cookies = response.headers['Set-Cookie']
                if self.config.scanner['debug']:
                    self.logger.info(f"Captured cookies from response: {self.cookies}")

            self.throttler.post_request(success=True)
            return response
            
        except Exception as e:
            self.throttler.post_request(success=False)
            if self.config.scanner['debug']:
                self.logger.error(f"Request failed for {url}: {str(e)}")
            return None


        
    def perform_attack(self, url: str, attack_type: str, payload: str, headers: Dict[str, str]) -> Optional[ScanResult]:
        """Perform an attack and record the result"""
        try:
            original_response = self.make_request(url)
            if not original_response:
                return None

            response = self.make_request(url, headers=headers)
            if not response:
                return None

            is_vulnerable, differences = self.analyze_response(original_response, response)
            
            result = ScanResult(
                url=url,
                attack_type=attack_type,
                payload=payload,
                response_code=response.status_code,
                response_size=len(response.content),
                timestamp=datetime.now(),
                headers=headers,
                is_vulnerable=is_vulnerable,
                notes=str(differences) if differences else ""
            )

            if is_vulnerable:
                result.verification_method = self.verify_vulnerability(url, payload, response)
                self.reporter.add_result(result)

            return result

        except Exception as e:
            # self.logger.error(f"Error performing {attack_type} attack on {url}: {str(e)}")
            return None
    
    def log_vulnerability(self, result: ScanResult):

        print(f"\nPotential SSRF vulnerability found!")
        print(f"URL: {result.url}")
        print(f"Attack Type: {result.attack_type}")
        print(f"Payload: {result.payload}")
        print(f"Response Code: {result.response_code}")
        print(f"Verification Method: {result.verification_method}")
        print("-" * 50)

    def protocolAttack(self):
        """Enhanced protocol attack with protocol-specific handlers"""
        tempResponses = {}
        # total_tests = len(self.headers) * len(self.protocols) * min(len(self.local_ips), 5)
        # completed_tests = 0
        
        for header in self.headers:
            for protocol in self.protocols:
                ip = "127.0.0.1"
                # for ip in self.local_ips[:5]:  # Limit IPs for performance
                # completed_tests += 1
                # self.update_progress('Protocol', completed_tests, total_tests)
                
                # Get protocol-specific payloads
                if protocol == 'gopher':
                    payloads = self.protocol_handler.handle_gopher(ip)
                elif protocol == 'dict':
                    payloads = self.protocol_handler.handle_dict(ip)
                elif protocol == 'file':
                    payloads = self.protocol_handler.handle_file(ip)
                else:
                    payloads = self.protocol_handler.generate_protocol_variations(protocol, ip)
                
                for payload in payloads:
                    badHeader = {header: payload}
                    result = self.perform_attack(self.url, 'Protocol', payload, badHeader)
                    
                    if result and result.is_vulnerable:
                        self.log_vulnerability(result)

    

# lang -> lib 사용하면 -> ssrf 취약점 가능성 -> 필터링 검사
def main():
    
    # with open("../add_in/data.json", "r", encoding="utf-8") as f:
    #     data = json.load(f)
        
        # print(data)
    # source_files = data["source_files"]
        # data = json.loads(data)
    # print("ssrf")
    obj = SSRF("127.0.0.1")
    obj.run()
if __name__ == "__main__":
    
    main()