# A02_integration.py
# A02 Cryptographic Failures 통합 검사 클래스

import json
import sys
import os

from A02.A02_check_cryptographic import CheckCryptographic
from A02.A02_check_https import ProtocolHandler

# 프로젝트 루트 경로 설정
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANAGE_DATA = os.path.join(PROJECT_ROOT, "add_in", "manage_data.json")

def load_data():
    """manage_data.json에서 프로젝트 파일들 로드"""
    try:
        with open(MANAGE_DATA, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("⚠️ manage_data.json이 없습니다. main_test.py를 먼저 실행하세요.")
        return {"source_files": []}

class CryptographicFailures:
    """A02 Cryptographic Failures 통합 검사 클래스"""

    def __init__(self):
        pass

    def check_cryptographic_run(self, source_files):
        """A02-01: 취약한 암호화 알고리즘 검사"""
        checker = CheckCryptographic()
        return checker.run(source_files)

    def check_https_run(self, url):
        """A02-02: HTTPS 보안 검사"""
        checker = ProtocolHandler()
        return checker.run(url)

    def run_all(self, source_files, url):
        """모든 A02 검사 실행"""
        results = {
            "A02-01": self.check_cryptographic_run(source_files),
            "A02-02": self.check_https_run(url)
        }
        return results


if __name__ == "__main__":
    data = load_data()
    source_files = data.get("source_files", [])

    web_url = data.get("web_url", "")

    checker = CryptographicFailures()
    results = checker.run_all(source_files, web_url)

    print("\n=== A02 Cryptographic Failures 검사 결과 ===")
    for test_id, details in results.items():
        print(f"\n{test_id}: {len(details) if details else 0}개 발견")
        print(json.dumps(details, indent=2, ensure_ascii=False))
