"""
검사 실행 컨트롤러
보안 검사 실행 및 결과 처리를 담당
"""
import threading
import sys
import os


class ScanController:
    """보안 검사 실행 관리 클래스"""

    def __init__(self, callback=None):
        """
        Args:
            callback: 검사 완료 시 호출될 콜백 함수 (결과 데이터를 인자로 받음)
        """
        self.callback = callback
        self.is_scanning = False
        self.scan_thread = None

    def start_scan(self, url, gui_callback=None):
        """
        보안 검사 시작

        Args:
            url: 검사 대상 URL
            gui_callback: GUI 업데이트용 콜백 함수

        Returns:
            bool: 검사 시작 성공 여부
        """
        if self.is_scanning:
            print("⚠️ 이미 검사가 진행 중입니다.")
            return False

        self.is_scanning = True

        # 별도 스레드에서 검사 실행
        self.scan_thread = threading.Thread(
            target=self._run_scan_thread,
            args=(url, gui_callback)
        )
        self.scan_thread.daemon = True
        self.scan_thread.start()

        return True

    def _run_scan_thread(self, url, gui_callback):
        """별도 스레드에서 검사 실행"""
        try:
            print(f"🚀 검사 시작: {url}")

            # main_test.py가 있는 경로로 이동
            original_path = os.getcwd()
            project_path = self._get_project_path()
            os.chdir(project_path)

            # main_test.py import 및 실행
            result = self._execute_main_test(project_path, gui_callback)

            # 원래 경로로 복원
            os.chdir(original_path)

            print("✅ 검사 완료")

            # 콜백 호출
            if self.callback and result:
                self.callback(result)

        except Exception as e:
            print(f"❌ 검사 실행 오류: {e}")
            import traceback
            traceback.print_exc()

        finally:
            self.is_scanning = False

    def _get_project_path(self):
        """프로젝트 루트 경로 반환"""
        current_file = os.path.abspath(__file__)
        gui_dir = os.path.dirname(current_file)
        project_path = os.path.dirname(gui_dir)
        return project_path

    def _execute_main_test(self, project_path, gui_callback):
        """main_test.py 실행"""
        import importlib

        # 기존 모듈 캐시 제거 (재실행을 위해)
        if 'main_test' in sys.modules:
            importlib.reload(sys.modules['main_test'])
            from main_test import main_security_test
        else:
            # main_test.py 직접 import
            sys.path.insert(0, project_path)
            from main_test import main_security_test

        # main_test 실행
        result = main_security_test(gui_callback=gui_callback)
        return result

    def is_running(self):
        """검사 실행 중인지 확인"""
        return self.is_scanning

    def stop_scan(self):
        """검사 중지 (향후 구현 예정)"""
        # TODO: 검사 중지 기능 구현
        pass
