import requests
import socket
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from OpenSSL import SSL
import json

# RANK = "A02"



class ProtocolHandler:

    def check_https_security(self, url):
        results = []
        # # check = False
        parsed = urlparse(url)
        hostname = parsed.hostname
        port = parsed.port or 443

        print(f"\n 점검 대상: {url}\n")

        # ✅ 1. HTTPS 사용 확인
        if parsed.scheme != 'https':
            msg = f" HTTPS not used"
            return  [msg]
        print(" HTTPS 사용 확인")

        # ✅ 2. HSTS 및 쿠키 보안 확인
        try:
            resp = requests.get(url, timeout=5)
            headers = resp.headers

            # HSTS 확인
            if 'strict-transport-security' in headers:
                print("  HSTS 헤더가 설정되어 있습니다.")
            else:
                msg = f" HSTS header is missing."
                print("  HSTS 헤더가 없습니다.")
                results.append(msg)
                # # check = True
                

            # 쿠키 보안 설정 확인
            set_cookie_headers = resp.headers.get('Set-Cookie', '')
            if 'Secure' in set_cookie_headers and 'HttpOnly' in set_cookie_headers:
                print("🍪  쿠키에 Secure 및 HttpOnly 설정됨")
            else:
                msg = f" Secure or HttpOnly attribute is missing in cookies"
                print("🍪  쿠키에 Secure 또는 HttpOnly 설정이 누락됨")
                results.append(msg)
                # # check = True
                

            # Mixed Content 검사
            soup = BeautifulSoup(resp.text, 'html.parser')
            tags = soup.find_all(['img', 'script', 'iframe', 'link'])
            http_links = [tag.get('src') or tag.get('href') for tag in tags if tag.get('src', '').startswith('http://') or tag.get('href', '').startswith('http://')]
            if http_links:
                msg = f" Mixed Content detected ({len(http_links)} HTTP resources)"
                
                print(f"🌐  Mixed Content 감지됨 (HTTP 리소스 {len(http_links)}개):")
                for link in http_links:
                    print(f"    - {link}")
                    
                results.append(msg)
                # check = True
            else:
                print("🌐  모든 리소스가 HTTPS로 로드됨")
        except Exception as e:
            print(f"url 요청 실패: {e}")
            return

        # ✅ 3. TLS 구성 및 인증 확인
        try:
            context = SSL.Context(SSL.TLS_CLIENT_METHOD)
            conn = SSL.Connection(context, socket.socket(socket.AF_INET, socket.SOCK_STREAM))
            conn.set_tlsext_host_name(hostname.encode())
            conn.connect((hostname, port))
            conn.set_connect_state()
            conn.do_handshake()

            cipher = conn.get_cipher_name() # 사용 중인 암호화 스위트(예: AES-GCM 등)를 가져옵니다.
            tls_version = conn.get_protocol_version_name() #용 중인 TLS 프로토콜 버전(예: TLSv1.2, TLSv1.3 등)을 가져옵니다.
            cert = conn.get_peer_certificate() #서버가 제공한 인증서를 가져옵니다.
            cert_subject = cert.get_subject().CN #인증서의 CN(Common Name, 도메인명)을 가져옵니다.
            cert_issuer = cert.get_issuer().CN #인증서의 발급자를 가져옵니다.
            valid_from = cert.get_notBefore().decode() #인증서의 유효 시작일을 가져옵니다.
            valid_to = cert.get_notAfter().decode() #인증서의 유효 종료일을 가져옵니다.

            print(f" TLS 버전: {tls_version}")
            print(f" 사용 중인 암호화 스위트: {cipher}")
            print(f" 인증서 CN: {cert_subject}, 발급자: {cert_issuer}")
            print(f" 유효 기간: {valid_from[:8]} ~ {valid_to[:8]}")

            # AEAD 인증 암호화 판단
            if 'GCM' in cipher or 'CHACHA20' in cipher:
                print("url  인증된 암호화(AEAD) 방식 사용 중 (예: AES-GCM)")
            else:
                msg = f" Cipher suite may not be authenticated encryption (e.g., AES-CBC)"
                print("url  인증된 암호화 방식이 아닐 수 있음")
                results.append(msg)
                # check = True
                
                

            # Forward Secrecy 판단
            if 'ECDHE' in cipher or 'DHE' in cipher:
                print("🔁  Forward Secrecy(FS) 지원")
            else:
                msg = f" Forward Secrecy (FS) not supported"
                print("🔁  Forward Secrecy 미지원")
                results.append(msg)
                # check = True
                
                

            conn.close()
            
        except Exception as e:
            conn.close()
            msg = f"url TLS connection failed: {e}"
            print(f"url TLS 연결 실패: {e}")
            results.append(msg)
            # check = True
            

        return results
        
    def parse_scan_results(self, results):

        if not results:
            return []

        return [{
            "description": results
        }]

    def run(self, url):
        results = self.check_https_security(url)
        
        return self.parse_scan_results(results)

if __name__ == "__main__":
    url = "https://github.com"
    # url = "http://127.0.0.1/index.php"
    obj = ProtocolHandler()
    
    with open("https_check_results.json", "w") as f:
        json.dump(obj.run(url), f, ensure_ascii=False, indent=2)