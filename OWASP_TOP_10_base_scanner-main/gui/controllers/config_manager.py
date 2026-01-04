"""
설정 관리 모듈
user_info.json 파일의 읽기/쓰기를 담당
"""
import json
import os


class ConfigManager:
    """설정 파일 관리 클래스"""

    def __init__(self, config_path=None):
        """
        Args:
            config_path: 설정 파일 경로 (기본값: etc/user_info.json)
        """
        if config_path is None:
            # 프로젝트 루트 기준 경로 설정
            current_file = os.path.abspath(__file__)  # /home/.../gui/controllers/config_manager.py
            controllers_dir = os.path.dirname(current_file)  # /home/.../gui/controllers
            gui_dir = os.path.dirname(controllers_dir)  # /home/.../gui
            project_root = os.path.dirname(gui_dir)  # /home/.../project
            self.config_path = os.path.join(project_root, "etc", "user_info.json")
        else:
            self.config_path = config_path

    def load_config(self):
        """
        설정 파일 로드

        Returns:
            dict: 설정 데이터 (실패 시 빈 딕셔너리)
        """
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            return config
        except FileNotFoundError:
            print(f"⚠️ 설정 파일을 찾을 수 없습니다: {self.config_path}")
            return {}
        except json.JSONDecodeError as e:
            print(f"❌ 설정 파일 파싱 오류: {e}")
            return {}
        except Exception as e:
            print(f"❌ 설정 파일 로드 실패: {e}")
            return {}

    def save_config(self, config):
        """
        설정 파일 저장

        Args:
            config: 저장할 설정 데이터

        Returns:
            bool: 저장 성공 여부
        """
        try:
            # 디렉토리가 없으면 생성
            config_dir = os.path.dirname(self.config_path)
            os.makedirs(config_dir, exist_ok=True)

            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ 설정 파일 저장 실패: {e}")
            return False

    def get_config(self):
        """
        전체 설정 가져오기

        Returns:
            dict: 전체 설정 데이터
        """
        return self.load_config()

    def get_web_url(self):
        """
        web_url 가져오기

        Returns:
            str: web_url 값 (없으면 기본값)
        """
        config = self.load_config()
        return config.get("web_url")

    def set_web_url(self, url):
        """
        web_url 설정

        Args:
            url: 설정할 URL

        Returns:
            bool: 저장 성공 여부
        """
        config = self.load_config()
        config["web_url"] = url
        success = self.save_config(config)

        if success:
            print(f"✅ URL 업데이트: {url}")
        else:
            print(f"❌ URL 업데이트 실패: {url}")

        return success

    def get_value(self, key, default=None):
        """
        특정 키의 값 가져오기

        Args:
            key: 설정 키
            default: 기본값

        Returns:
            설정 값 (없으면 기본값)
        """
        config = self.load_config()
        return config.get(key, default)

    def set_value(self, key, value):
        """
        특정 키의 값 설정

        Args:
            key: 설정 키
            value: 설정 값

        Returns:
            bool: 저장 성공 여부
        """
        config = self.load_config()
        config[key] = value
        return self.save_config(config)
