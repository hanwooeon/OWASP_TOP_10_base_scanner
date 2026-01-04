"""
파일 추가 컨트롤러
파일 및 데이터 추가 관리 로직 처리
"""
import os
import json
from tkinter import filedialog, messagebox


class AddController:
    """파일/데이터 추가 관리 컨트롤러 클래스"""

    def __init__(self):
        self.selected_files = []

    def select_files(self):
        """파일 선택 다이얼로그"""
        files = filedialog.askopenfilenames(
            title="파일 선택",
            filetypes=[
                ("모든 설정 파일", "*.json;*.txt;*.cfg;*.conf"),
                ("JSON 파일", "*.json"),
                ("텍스트 파일", "*.txt"),
                ("설정 파일", "*.cfg;*.conf"),
                ("모든 파일", "*.*")
            ]
        )

        for file_path in files:
            if file_path not in self.selected_files:
                self.selected_files.append(file_path)

        return self.selected_files

    def select_folder(self):
        """폴더 선택 - 프로젝트 폴더 경로 저장"""
        folder_path = filedialog.askdirectory(title="프로젝트 폴더 선택")

        if not folder_path:
            return None

        try:
            # 확인 메시지
            confirm = messagebox.askyesno(
                f"폴더: {folder_path}\n"
            )

            if not confirm:
                return None

            print(f"\n  [AddController] 폴더 경로 저장: {folder_path}")

            # user_info.json의 Web_Dir 값 변경
            project_root = self._get_project_root()
            user_info_path = os.path.join(project_root, "etc", "user_info.json")

            # 절대 경로로 변환
            abs_folder_path = os.path.abspath(folder_path)

            # user_info.json 읽기
            with open(user_info_path, "r", encoding="utf-8") as f:
                user_info = json.load(f)

            # Web_Dir 값 업데이트
            user_info["Web_Dir"] = abs_folder_path

            # user_info.json 저장
            with open(user_info_path, "w", encoding="utf-8") as f:
                json.dump(user_info, f, indent=2, ensure_ascii=False)

            messagebox.showinfo(
                "폴더 추가 완료",
                f"✅ 폴더가 검사 대상으로 설정되었습니다!\n\n"
                f"경로: {abs_folder_path}\n\n"
                f"user_info.json의 Web_Dir이 업데이트되었습니다.\n"
                f"검사를 실행하면 이 폴더의 파일들이 분석됩니다."
            )

            print(f"  [AddController] user_info.json Web_Dir 업데이트 완료: {abs_folder_path}")
            return {"project_path": abs_folder_path}

        except Exception as e:
            print(f"  [AddController] ❌ 폴더 경로 저장 오류: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("오류", f"폴더 경로 저장 중 오류가 발생했습니다:\n{e}")
            return None

    def clear_files(self):
        """파일 목록 초기화"""
        try:
            if self.selected_files:
                if messagebox.askyesno("확인", "선택된 모든 파일을 제거하시겠습니까?"):
                    self.selected_files.clear()
                    print(f"  [AddController] 파일 목록 초기화 완료")
                    return True
                return False
            else:
                messagebox.showinfo("알림", "선택된 파일이 없습니다.")
                return False
        except Exception as e:
            print(f"  [AddController] ❌ 파일 목록 초기화 실패: {e}")
            messagebox.showerror("오류", f"파일 목록 초기화 중 오류가 발생했습니다:\n{e}")
            return False

    def remove_file_by_index(self, index):
        """인덱스로 파일 제거"""
        try:
            if 0 <= index < len(self.selected_files):
                removed_file = self.selected_files.pop(index)
                # 성공 메시지 (간단히)
                file_name = os.path.basename(removed_file)
                print(f"✅ 파일 제거됨: {file_name}")
                return True
        except Exception as e:
            print(f"❌ 파일 제거 실패: {e}")
            return False

    def apply_files(self):
        """선택된 파일들 적용 - data.json에 추가하여 검사 대상으로 등록"""
        if not self.selected_files:
            messagebox.showwarning("경고", "적용할 파일이 선택되지 않았습니다.")
            return None

        try:
            print(f"\n  [AddController] 파일 적용 시작: {len(self.selected_files)}개 파일")

            # add_in/data.json 경로
            project_root = self._get_project_root()
            data_json_path = os.path.join(project_root, "add_in", "data.json")

            # 기존 data.json 로드
            try:
                with open(data_json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                print(f"  [AddController] 기존 data.json 로드 완료")
            except FileNotFoundError:
                # data.json이 없으면 새로 생성
                data = {
                    "project_id": "",
                    "source_files": [],
                    "dependency_files": []
                }
                print(f"  [AddController] data.json 파일이 없어서 새로 생성")
            except Exception as e:
                messagebox.showerror("오류", f"data.json 로드 실패:\n{e}")
                return None

            # 현재 등록된 파일 경로 목록 (중복 방지)
            existing_paths = {item.get("path") for item in data.get("source_files", [])}

            # 언어 확장자 매핑 (data_management.py와 동일)
            LANG_EXT = {
                ".c": "C", ".h": "C/C++ Header", ".cpp": "C++", ".hpp": "C++ Header",
                ".cs": "C#", ".java": "Java", ".kt": "Kotlin", ".go": "Go", ".rs": "Rust",
                ".js": "JavaScript", ".jsx": "JavaScript + JSX", ".ts": "TypeScript",
                ".tsx": "TypeScript + JSX", ".php": "PHP", ".py": "Python", ".rb": "Ruby",
                ".html": "HTML", ".css": "CSS", ".vue": "Vue.js", ".json": "JSON"
            }

            applied_count = 0
            skipped_count = 0
            failed_files = []

            for file_path in self.selected_files:
                try:
                    # 절대 경로로 변환
                    abs_path = os.path.abspath(file_path)

                    # 이미 등록된 파일인지 확인
                    if abs_path in existing_paths:
                        skipped_count += 1
                        print(f"  [AddController] ⊙ 이미 등록됨: {os.path.basename(abs_path)}")
                        continue

                    # 파일 확장자 확인
                    _, ext = os.path.splitext(abs_path)
                    language = LANG_EXT.get(ext.lower(), "Unknown")

                    # 파일 내용 읽기
                    with open(abs_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()

                    # data.json에 추가
                    data["source_files"].append({
                        "path": abs_path,
                        "language": language,
                        "content": content
                    })

                    applied_count += 1
                    print(f"  [AddController] ✓ 추가됨: {os.path.basename(abs_path)} ({language})")

                except Exception as e:
                    failed_files.append(f"{os.path.basename(file_path)}: {e}")
                    print(f"  [AddController] ✗ 실패: {os.path.basename(file_path)} - {e}")

            # 수정된 data.json 저장
            if applied_count > 0:
                try:
                    with open(data_json_path, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    print(f"  [AddController] data.json 저장 완료")
                except Exception as e:
                    messagebox.showerror("저장 오류", f"data.json 저장 실패:\n{e}")
                    return None

            # 결과 메시지
            message_parts = []
            if applied_count > 0:
                message_parts.append(f"✅ 추가된 파일: {applied_count}개")
            if skipped_count > 0:
                message_parts.append(f"⊙ 이미 등록된 파일: {skipped_count}개")
            if failed_files:
                message_parts.append(f"\n❌ 실패한 파일:\n" + "\n".join(failed_files))

            result = {
                "applied_count": applied_count,
                "skipped_count": skipped_count,
                "failed_files": failed_files,
                "total_files": len(data.get("source_files", []))
            }

            if applied_count > 0 or skipped_count > 0:
                message_parts.append(f"\n📊 전체 등록 파일: {result['total_files']}개")
                messagebox.showinfo("적용 완료", "\n".join(message_parts))
            else:
                messagebox.showerror("적용 실패", "파일 적용에 실패했습니다:\n" + "\n".join(failed_files))

            print(f"  [AddController] 파일 적용 완료: {applied_count}개 추가, {skipped_count}개 스킵")
            return result

        except Exception as e:
            print(f"  [AddController] ❌ 파일 적용 중 오류: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("오류", f"파일 적용 중 오류가 발생했습니다:\n{e}")
            return None

    def create_backup(self):
        """현재 설정의 백업 생성"""
        try:
            import datetime

            backup_dir = filedialog.askdirectory(title="백업 저장 위치 선택")
            if not backup_dir:
                return None

            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"security_tool_backup_{timestamp}.json"
            backup_path = os.path.join(backup_dir, backup_filename)

            # 백업 데이터 생성
            backup_data = {
                "timestamp": datetime.datetime.now().isoformat(),
                "selected_files": self.selected_files,
                "file_count": len(self.selected_files)
            }

            # 백업 파일 저장
            with open(backup_path, "w", encoding="utf-8") as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=4)

            messagebox.showinfo("백업 완료", f"백업이 생성되었습니다:\n{backup_path}")
            return backup_path

        except Exception as e:
            messagebox.showerror("백업 실패", f"백업 생성 중 오류가 발생했습니다:\n{e}")
            return None

    def get_file_info(self, file_path):
        """파일 정보 가져오기"""
        try:
            stat = os.stat(file_path)
            import datetime
            modified_time = datetime.datetime.fromtimestamp(stat.st_mtime)

            return {
                "path": file_path,
                "name": os.path.basename(file_path),
                "size": stat.st_size,
                "size_formatted": self.format_file_size(stat.st_size),
                "modified": modified_time.strftime('%Y-%m-%d %H:%M:%S'),
                "readonly": not os.access(file_path, os.W_OK)
            }
        except Exception as e:
            print(f"  [AddController] ❌ 파일 정보 가져오기 실패: {e}")
            return None

    def format_file_size(self, size_bytes):
        """파일 크기 포맷팅"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"

    def get_file_icon(self, filename):
        """파일 확장자에 따른 아이콘 반환"""
        ext = os.path.splitext(filename)[1].lower()

        icon_map = {
            '.json': '📄',
            '.txt': '📝',
            '.cfg': '⚙️',
            '.conf': '⚙️',
            '.py': '🐍',
            '.js': '📜',
            '.html': '🌐',
            '.css': '🎨',
            '.xml': '📋',
            '.csv': '📊',
            '.log': '📋'
        }

        return icon_map.get(ext, '📄')

    def _get_project_root(self):
        """프로젝트 루트 경로 반환"""
        current_file = os.path.abspath(__file__)
        controllers_dir = os.path.dirname(current_file)
        gui_dir = os.path.dirname(controllers_dir)
        project_root = os.path.dirname(gui_dir)
        return project_root
