# A04_integration.py
# A04 Insecure Design 통합 검사 클래스

import json
import sys
import os

# 프로젝트 루트 경로 설정
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

from A04.A04_Rate_Limit import run as rate_limit_run
from A04.A04_Insufficien_access_control import start_check_access_control
from A04.A04_Permission_bypass import start_permission_bypass


class InsecureDesign:
    """A04 Insecure Design 통합 검사 클래스"""

    def __init__(self):
        pass

    def rate_limit_run(self, obj_list, config):
        """A04-01: Rate Limiting 검사"""
        return rate_limit_run(obj_list, config)

    def access_control_run(self, web_directory):
        """A04-02: 접근 제어 취약점 검사"""
        return start_check_access_control(web_directory)

    def permission_bypass_run(self, config):
        """A04-03: 권한 우회 취약점 검사"""
        return start_permission_bypass(config)

    def run_all(self, obj_list, config):
        """모든 A04 검사 실행"""
        web_directory = config.get("web_directory", "")

        results = {
            "A04-01": self.rate_limit_run(obj_list, config),
            "A04-02": self.access_control_run(web_directory),
            "A04-03": self.permission_bypass_run(config)
        }
        return results


if __name__ == "__main__":
    from add_in.crawl2 import start_crawl2

    USER_INFO_PATH = "etc/user_info.json"

    with open(USER_INFO_PATH, "r") as f:
        config = json.load(f)

    web_url = config["web_url"]
    obj_list = start_crawl2(web_url, "", "")

    checker = InsecureDesign()
    results = checker.run_all(obj_list, config)

    print("\n=== A04 Insecure Design 검사 결과 ===")
    for test_id, details in results.items():
        print(f"\n{test_id}: {len(details) if details else 0}개 발견")
        if details:
            print(json.dumps(details, indent=2, ensure_ascii=False))
