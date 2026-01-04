# A06_VulnerableComponents.py
# A06 취약하고 지원되지 않는 구성 요소 통합 검사 클래스

import json
import sys
import os

from A06.A06_vulnerabilityLibrary import vulnerabilityLibrary


# 프로젝트 루트 경로 설정
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# SAMPLE_PATH = os.path.join(PROJECT_ROOT, "etc", "A06_sample.json")
sys.path.append(PROJECT_ROOT)

# def sample_path():
#    with open(SAMPLE_PATH, "r") as f:
#        return json.load(f)


class VulnerableComponents:
    """A06 취약하고 지원되지 않는 구성 요소 통합 검사 클래스"""

    def __init__(self):
        pass

    def vulnerability_library_run(self, dependencyfiles):
        """A06-01: 취약한 라이브러리 검사"""
        vuln_lib = vulnerabilityLibrary()
        return vuln_lib.run(dependencyfiles)

    def run_all(self, dependencyfiles):
        """모든 A06 검사 실행"""
        results = {
            "A06-01": self.vulnerability_library_run(dependencyfiles),
        }
        return results


if __name__ == "__main__":
    

    # 프로젝트 루트 기준 절대 경로 설정
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_PATH = os.path.join(PROJECT_ROOT, "add_in", "manage_data.json")
    with open(DATA_PATH, "r") as f:
        data = json.load(f)
    # sample_data = sample_path()
    # dependencyfiles = data.get(sample_data, [])

    checker = VulnerableComponents()
    dependencyfiles = data.get("dependency_files", [])
    results = checker.vulnerability_library_run(dependencyfiles)
    # results = checker.run_all(sample_data)

    with open("./Library_vulnerabilities.json3", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

