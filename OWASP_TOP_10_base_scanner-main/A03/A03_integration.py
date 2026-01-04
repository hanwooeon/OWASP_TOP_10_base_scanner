# A03_integration.py
# A03 Injection 통합 검사 클래스

import json
import sys
import os

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


from A03.A03_Injection import InjectionPatterns


class Injection:
    """A03 Injection 통합 검사 클래스"""

    def __init__(self):
        self.checker = InjectionPatterns()

    def xss_run(self, source_files):
        """A03-01: XSS 취약점 검사"""
        return self.checker.xss_run(source_files)

    def sqli_run(self, source_files):
        """A03-02: SQL Injection 검사"""
        return self.checker.sqli_run(source_files)

    def command_injection_run(self, source_files):
        """A03-03: Command Injection 검사"""
        return self.checker.command_injection_run(source_files)

    def run_all(self, source_files):
        """모든 A03 검사 실행"""
        results = {
            "A03-01": self.xss_run(source_files),
            "A03-02": self.sqli_run(source_files),
            "A03-03": self.command_injection_run(source_files)
        }
        return results

if __name__ == "__main__":
    # source_files 준비
    data = load_data()
    source_files = data.get("source_files", [])

    checker = Injection()
    results = checker.run_all(source_files)

    print("\n=== A03 Injection 검사 결과 ===")
    for test_id, details in results.items():
        print(f"\n{test_id}: {len(details)}개 발견")
        print(json.dumps(details, indent=2, ensure_ascii=False))
