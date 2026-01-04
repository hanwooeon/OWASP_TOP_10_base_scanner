import socket
from urllib.parse import urlparse
import json
import os

# 프로젝트 루트 기준 절대 경로 설정
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ETC_PATH = os.path.join(PROJECT_ROOT, "etc", "A05_port_config.json")
USER_INFO_PATH = os.path.join(PROJECT_ROOT, "etc", "user_info.json")

def load_port_config():
    with open(ETC_PATH, "r") as f:
        return json.load(f)

def load_user_info():
    with open(USER_INFO_PATH, "r") as f:
        return json.load(f)

def scan_ports(host: str, start_port: int, end_port: int):
    # JSON에서 설정 로드
    config = load_port_config()
    PORT_SERVICE_MAP = {int(k): v for k, v in config["port_service_map"].items()}
    RISKY_PORTS = set(config["risky_ports"])
    
    open_ports = []

    # URL 보정
    if "://" not in host:
        host = "http://" + host

    try:
        parsed_url = urlparse(host)
        host = parsed_url.hostname
        ip = socket.gethostbyname(host)
    except Exception as e:
        print(f"유효하지 않은 호스트: {e}")
        return []

    print(f"[+] {host} ({ip}) 포트 스캔 시작: {start_port}~{end_port}")

    for port in range(start_port, end_port + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            timeout = config.get("scan_config", {}).get("timeout", 0.1)
            s.settimeout(timeout)
            result = s.connect_ex((ip, port))
            if result == 0:
                service_name = PORT_SERVICE_MAP.get(port)
                if not service_name:
                    try:
                        service_name = socket.getservbyport(port)
                    except:
                        service_name = "Unknown"

                risk_tag = "위험" if port in RISKY_PORTS else ""
                print(f"[OPEN] 포트 {port} 열림: {service_name}{risk_tag}")
                open_ports.append((port, service_name, port in RISKY_PORTS))
            else:
                pass

    return open_ports


def start_port_security_scan(config):
    """details만 반환하는 포트 스캔 함수"""
    from datetime import datetime
    
    host = config.get("host")
    if not host:
        raise ValueError("호스트 정보가 설정되지 않았습니다")
    open_ports = scan_ports(host, 1, 1024)
    
    # details 생성
    details = []
    for port, service, risky in open_ports:
        if risky:
            details.append({
                "url": f"{host}:{port}",
                "method": "PORT_SCAN",
                "issue": f"위험한 포트 열림: {port} ({service}) - 불필요한 기능 활성화",
                "timestamp": datetime.now().isoformat()
            })
    
    return details

def run(config):
    """main_test.py에서 호출되는 함수"""
    return start_port_security_scan(config)

if __name__ == "__main__":
    try:
        config = load_user_info()
        details = start_port_security_scan(config)
        
        print(json.dumps(details, indent=2, ensure_ascii=False))
        with open("A05/port_security.json", "w", encoding="utf-8") as f:
            json.dump(details, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"오류 발생: {e}")
