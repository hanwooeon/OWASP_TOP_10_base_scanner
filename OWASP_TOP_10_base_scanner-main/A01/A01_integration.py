# A01_integration.py
# A01 Broken Access Control 통합 검사 클래스

import json
import sys
import os

from A01.A01_CSRF import CSRFScanner
from add_in.crawl2 import start_crawl2

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USER_INFO_PATH = os.path.join(PROJECT_ROOT, "etc", "user_info.json")

def user_info():
    with open(USER_INFO_PATH, "r") as f:
        return json.load(f)

class BrokenAccessControl:
    """A01 Broken Access Control 통합 검사 클래스"""

    def __init__(self):
        pass

    def csrf_run(self, obj_list, config):
        """A01-01: CSRF 보호 검사"""
        scanner = CSRFScanner()
        web_url = config.get("web_url", "")
        return scanner.run(web_url, obj_list)

    def run_all(self, obj_list, config):
        """모든 A01 검사 실행"""
        results = {
            "A01-01": self.csrf_run(obj_list, config)
        }
        return results


if __name__ == "__main__":
    
    config = user_info()

    web_url = config["web_url"]
    obj_list = start_crawl2(web_url, "", "")

    checker = BrokenAccessControl()
    results = checker.run_all(obj_list, config)

    print("\n=== A01 Broken Access Control 검사 결과 ===")
    for test_id, details in results.items():
        print(f"\n{test_id}: {len(details)}개 발견")
        print(json.dumps(details, indent=2, ensure_ascii=False))
