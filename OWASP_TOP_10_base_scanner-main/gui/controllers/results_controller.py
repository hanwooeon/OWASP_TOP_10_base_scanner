"""
검사 결과 관리 컨트롤러
저장된 검사 결과 파일 로드 및 관리
"""
import json
import os
from datetime import datetime
from pathlib import Path


class ResultsController:
    """검사 결과 관리 클래스"""

    def __init__(self):
        """
        초기화
        results 폴더에서 결과 파일들을 관리
        """
        self.project_root = self._get_project_root()
        self.results_dir = os.path.join(self.project_root, "results")

        # results 디렉토리가 없으면 생성
        os.makedirs(self.results_dir, exist_ok=True)

    def _get_project_root(self):
        """프로젝트 루트 경로 반환"""
        current_file = os.path.abspath(__file__)
        controllers_dir = os.path.dirname(current_file)
        gui_dir = os.path.dirname(controllers_dir)
        project_root = os.path.dirname(gui_dir)
        return project_root

    def get_results_list(self):
        """
        모든 결과 파일 목록 가져오기 (최신순 정렬)

        Returns:
            list: 결과 파일 정보 리스트 [{"timestamp": ..., "target": ..., "file_path": ...}, ...]
        """
        results = []

        try:
            # results 폴더에서 모든 JSON 파일 찾기
            json_files = list(Path(self.results_dir).glob("*.json"))

            for file_path in json_files:
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)

                    # 타임스탬프와 검사 대상 추출
                    timestamp = data.get("summary", {}).get("scan_time", "")

                    # 검사 대상 결정 (URL 또는 폴더 경로)
                    target = data.get("summary", {}).get("target_url", "")
                    if not target:
                        target = data.get("summary", {}).get("target_folder", "알 수 없음")

                    results.append({
                        "timestamp": timestamp,
                        "target": target,
                        "file_path": str(file_path),
                        "total_vulnerabilities": data.get("summary", {}).get("total_vulnerabilities", 0)
                    })

                except Exception as e:
                    print(f"⚠️ 결과 파일 읽기 실패: {file_path} - {e}")
                    continue

            # 타임스탬프 기준 내림차순 정렬 (최신순)
            results.sort(key=lambda x: x["timestamp"], reverse=True)

            print(f"✅ 결과 파일 {len(results)}개 로드 완료")
            return results

        except Exception as e:
            print(f"❌ 결과 목록 로드 실패: {e}")
            return []

    def load_result_detail(self, file_path):
        """
        특정 결과 파일의 상세 내용 로드

        Args:
            file_path: 결과 파일 경로

        Returns:
            dict: 결과 데이터 (results.json 형식)
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            print(f"✅ 결과 상세 로드 완료: {file_path}")
            return data

        except FileNotFoundError:
            print(f"⚠️ 결과 파일을 찾을 수 없습니다: {file_path}")
            return None
        except json.JSONDecodeError as e:
            print(f"❌ JSON 파싱 오류: {e}")
            return None
        except Exception as e:
            print(f"❌ 결과 로드 실패: {e}")
            return None

    def get_vulnerability_list(self, result_data):
        """
        결과 데이터에서 취약점 목록 추출

        Args:
            result_data: load_result_detail()에서 반환된 데이터

        Returns:
            list: 취약점 리스트 [{"test_id": ..., "test_name": ..., "risk_level": ..., "location": ..., "details": ...}, ...]
        """
        vulnerabilities = []

        if not result_data:
            return vulnerabilities

        try:
            categories = result_data.get("categories", {})

            for category_id, category_data in categories.items():
                tests = category_data.get("tests", [])

                for test in tests:
                    # 취약점이 있는 테스트만 추가
                    if test.get("vulnerable_items", 0) > 0 or test.get("details"):
                        details_list = test.get("details", [])

                        # 각 상세 취약점별로 항목 생성
                        if details_list:
                            for detail in details_list:
                                vulnerabilities.append({
                                    "test_id": test.get("test_id", ""),
                                    "test_name": test.get("test_name", ""),
                                    "risk_level": test.get("risk_level", ""),
                                    "location": detail.get("location", ""),
                                    "details": detail  # 전체 상세 정보
                                })
                        else:
                            # details가 없으면 테스트 정보만 추가
                            vulnerabilities.append({
                                "test_id": test.get("test_id", ""),
                                "test_name": test.get("test_name", ""),
                                "risk_level": test.get("risk_level", ""),
                                "location": "N/A",
                                "details": {}
                            })

            print(f"✅ 취약점 {len(vulnerabilities)}개 추출 완료")
            return vulnerabilities

        except Exception as e:
            print(f"❌ 취약점 목록 추출 실패: {e}")
            return []

    def delete_result(self, file_path):
        """
        결과 파일 삭제

        Args:
            file_path: 삭제할 파일 경로

        Returns:
            bool: 삭제 성공 여부
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"✅ 결과 파일 삭제 완료: {file_path}")
                return True
            else:
                print(f"⚠️ 파일이 존재하지 않습니다: {file_path}")
                return False
        except Exception as e:
            print(f"❌ 파일 삭제 실패: {e}")
            return False

    def get_results_count(self):
        """
        저장된 결과 파일 개수 반환

        Returns:
            int: 결과 파일 개수
        """
        try:
            json_files = list(Path(self.results_dir).glob("*.json"))
            return len(json_files)
        except Exception as e:
            print(f"❌ 결과 개수 확인 실패: {e}")
            return 0
