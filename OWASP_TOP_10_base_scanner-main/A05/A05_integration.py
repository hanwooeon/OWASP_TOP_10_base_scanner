# A05_SecurityMisconfiguration.py
# A05 보안 설정 오류 통합 검사 클래스

import json
import sys
import os

# 프로젝트 루트 경로 설정
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

from A05.A05_check_vulnerable import check_vulnerable_headers
from A05.A05_Port_Security import start_port_security_scan
from A05.A05_default import start_brute_force_scan


class SecurityMisconfiguration:
    """A05 보안 설정 오류 통합 검사 클래스"""

    def __init__(self):
        pass

    def check_vulnerable_run(self, obj_list):
        """A05-01: 취약한 HTTP 헤더 검사"""
        return check_vulnerable_headers(obj_list)

    def port_security_run(self, config):
        """A05-02: 포트 보안 검사"""
        return start_port_security_scan(config)

    def default_account_run(self, config):
        """A05-03: 기본 계정 침투 테스트"""
        return start_brute_force_scan(config)

    def run_all(self, obj_list, config):
        """모든 A05 검사 실행"""
        results = {
            "A05-01": self.check_vulnerable_run(obj_list),
            "A05-02": self.port_security_run(config),
            "A05-03": self.default_account_run(config)
        }
        return results


if __name__ == "__main__":
    from add_in.crawl2 import start_crawl2
    import os

    # 프로젝트 루트 기준 절대 경로 설정
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    USER_INFO_PATH = os.path.join(PROJECT_ROOT, "etc", "user_info.json")

    with open(USER_INFO_PATH, "r") as f:
        config = json.load(f)

    web_url = config["web_url"]
    obj_list = start_crawl2(web_url, "", "")

    checker = SecurityMisconfiguration()
    results = checker.run_all(obj_list, config)

    print("\n=== A05 보안 설정 오류 검사 결과 ===")
    for test_id, details in results.items():
        print(f"\n{test_id}: {len(details)}개 발견")
        print(json.dumps(details, indent=2, ensure_ascii=False))
