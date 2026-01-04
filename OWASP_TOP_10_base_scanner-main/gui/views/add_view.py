"""
Add View 모듈
파일 및 데이터 추가 관리 화면
"""
import tkinter as tk
from tkinter import messagebox
import os

try:
    from ..components import UIComponents
    from ..controllers.add_controller import AddController
except ImportError:
    from components import UIComponents
    from controllers.add_controller import AddController


class AddView:
    """파일/데이터 추가 뷰 클래스"""

    def __init__(self, main_window):
        self.main_window = main_window
        try:
            self.ui_components = UIComponents()
        except Exception as e:
            print(f"⚠️ AddView: UIComponents 초기화 실패: {e}")
            self.ui_components = None

        # Controller 초기화
        self.controller = AddController()

        # UI 위젯들을 저장할 변수 초기화
        self.file_listbox = None
        self.file_widgets = []
        self.file_canvas = None
        self.file_scroll_frame = None

    def setup_view(self, parent_frame):
        """Add 뷰 설정"""
        try:
            print("  [AddView] 뷰 초기화 시작...")

            # 메인 컨테이너
            main_container = tk.Frame(parent_frame, bg="#ffffff")
            main_container.pack(fill="both", expand=True, padx=20, pady=20)
            print("  [AddView] 메인 컨테이너 생성 완료")

            # 제목
            try:
                title_label = tk.Label(
                    main_container,
                    text="➕ 파일 추가",
                    font=("Arial", 18, "bold"),
                    bg="#ffffff",
                    fg="#2c3e50"
                )
                title_label.pack(pady=(20, 30))
                print("  [AddView] 제목 생성 완료")
            except Exception as e:
                print(f"  [AddView] ⚠️ 제목 생성 실패: {e}")

            # 파일 추가 섹션
            try:
                self.setup_simple_file_section(main_container)
                print("  [AddView] 파일 섹션 생성 완료")
            except Exception as e:
                print(f"  [AddView] ⚠️ 파일 섹션 생성 실패: {e}")
                import traceback
                traceback.print_exc()

            # 파일 목록 섹션
            try:
                self.setup_simple_file_list(main_container)
                print("  [AddView] 파일 목록 생성 완료")
            except Exception as e:
                print(f"  [AddView] ⚠️ 파일 목록 생성 실패: {e}")
                import traceback
                traceback.print_exc()

            # 액션 섹션
            try:
                self.setup_simple_actions(main_container)
                print("  [AddView] 액션 섹션 생성 완료")
            except Exception as e:
                print(f"  [AddView] ⚠️ 액션 섹션 생성 실패: {e}")
                import traceback
                traceback.print_exc()

            print("  [AddView] 뷰 초기화 완료")

        except Exception as e:
            print(f"  [AddView] ❌ 뷰 초기화 실패: {e}")
            import traceback
            traceback.print_exc()
            # 최소한의 화면 표시
            try:
                self.setup_minimal_add_view(parent_frame)
            except:
                print(f"  [AddView] ❌ 최소 화면도 생성 실패")

    def setup_simple_file_section(self, parent):
        """간단한 파일 선택 섹션"""
        try:
            # 파일 선택 프레임
            file_frame = tk.Frame(parent, bg="white", relief="solid", bd=1)
            file_frame.pack(fill="x", pady=(0, 20))

            # 제목
            tk.Label(file_frame, text="📁 파일 선택",
                    font=("Arial", 14, "bold"), bg="white").pack(pady=(15, 10))

            # 설명
            tk.Label(file_frame,
                    text="검사에 사용할 설정 파일이나 데이터 파일을 추가하세요.",
                    font=("Arial", 10), bg="white", fg="#666666").pack(pady=(0, 15))

            # 버튼 프레임
            button_frame = tk.Frame(file_frame, bg="white")
            button_frame.pack(pady=(0, 15))

            # 파일 선택 버튼
            tk.Button(button_frame, text="📄 파일 선택",
                     command=self.on_select_files,
                     bg="#3498db", fg="white",
                     font=("Arial", 11, "bold"),
                     relief="flat", padx=15, pady=8).pack(side="left", padx=5)

            # 폴더 선택 버튼
            tk.Button(button_frame, text="📁 폴더 선택",
                     command=self.on_select_folder,
                     bg="#2c3e50", fg="white",
                     font=("Arial", 11, "bold"),
                     relief="flat", padx=15, pady=8).pack(side="left", padx=5)

            # 초기화 버튼
            tk.Button(button_frame, text="🗑️ 초기화",
                     command=self.on_clear_files,
                     bg="#f39c12", fg="white",
                     font=("Arial", 11, "bold"),
                     relief="flat", padx=15, pady=8).pack(side="left", padx=5)

        except Exception as e:
            print(f"❌ 간단한 파일 섹션 생성 실패: {e}")

    def setup_simple_file_list(self, parent):
        """간단한 파일 목록 섹션"""
        try:
            # 파일 목록 프레임
            list_frame = tk.Frame(parent, bg="white", relief="solid", bd=1)
            list_frame.pack(fill="both", expand=True, pady=(0, 20))

            # 제목
            tk.Label(list_frame, text="📋 선택된 파일 목록",
                    font=("Arial", 14, "bold"), bg="white").pack(pady=(15, 10))

            # 리스트박스 컨테이너
            listbox_container = tk.Frame(list_frame, bg="white")
            listbox_container.pack(fill="both", expand=True, padx=15, pady=(0, 15))

            # 스크롤바
            scrollbar = tk.Scrollbar(listbox_container)
            scrollbar.pack(side="right", fill="y")

            # 리스트박스
            self.file_listbox = tk.Listbox(
                listbox_container,
                yscrollcommand=scrollbar.set,
                font=("Arial", 10),
                bg="#f8f9fa",
                fg="#2c3e50",
                selectbackground="#3498db",
                selectforeground="white",
                relief="solid",
                bd=1
            )
            self.file_listbox.pack(side="left", fill="both", expand=True)

            scrollbar.config(command=self.file_listbox.yview)

            # 더블클릭으로 파일 제거
            self.file_listbox.bind("<Double-Button-1>", self.on_remove_selected_file)

            # 컨텍스트 메뉴 설정
            self.setup_context_menu()

        except Exception as e:
            print(f"❌ 간단한 파일 목록 생성 실패: {e}")

    def setup_context_menu(self):
        """컨텍스트 메뉴 설정"""
        self.context_menu = tk.Menu(self.file_listbox, tearoff=0)
        self.context_menu.add_command(label="파일 제거", command=self.on_remove_selected_file)
        self.context_menu.add_command(label="파일 정보", command=self.on_show_file_info)

        def show_context_menu(event):
            try:
                # 클릭한 위치의 아이템 선택
                index = self.file_listbox.nearest(event.y)
                self.file_listbox.selection_clear(0, tk.END)
                self.file_listbox.selection_set(index)

                if self.file_listbox.get(index):  # 아이템이 있으면
                    self.context_menu.post(event.x_root, event.y_root)
            except:
                pass

        self.file_listbox.bind("<Button-3>", show_context_menu)  # 우클릭

    def setup_simple_actions(self, parent):
        """간단한 액션 버튼 섹션"""
        try:
            # 액션 프레임
            action_frame = tk.Frame(parent, bg="white", relief="solid", bd=1)
            action_frame.pack(fill="x")

            # 제목
            tk.Label(action_frame, text="⚡ 작업",
                    font=("Arial", 14, "bold"), bg="white").pack(pady=(15, 10))

            # 버튼 프레임
            button_frame = tk.Frame(action_frame, bg="white")
            button_frame.pack(pady=(0, 15))

            # 파일 적용 버튼
            tk.Button(button_frame, text="✅ 파일 적용",
                     command=self.on_apply_files,
                     bg="#27ae60", fg="white",
                     font=("Arial", 11, "bold"),
                     relief="flat", padx=15, pady=8).pack(side="left", padx=5)

            # 백업 생성 버튼
            tk.Button(button_frame, text="💾 백업 생성",
                     command=self.on_create_backup,
                     bg="#3498db", fg="white",
                     font=("Arial", 11, "bold"),
                     relief="flat", padx=15, pady=8).pack(side="left", padx=5)

            # 메인으로 돌아가기 버튼
            tk.Button(button_frame, text="🔙 메인으로",
                     command=lambda: self.main_window.switch_view("dast"),
                     bg="#2c3e50", fg="white",
                     font=("Arial", 11, "bold"),
                     relief="flat", padx=15, pady=8).pack(side="right", padx=5)

        except Exception as e:
            print(f"❌ 간단한 액션 섹션 생성 실패: {e}")

    def setup_minimal_add_view(self, parent):
        """최소한의 Add 화면"""
        try:
            label = tk.Label(
                parent,
                text="➕ 파일 추가 화면\n\n화면을 로드하는 중 문제가 발생했습니다.\n기본 모드로 실행 중입니다.",
                font=("Arial", 14),
                bg="#ffffff",
                fg="#2c3e50",
                justify="center"
            )
            label.pack(expand=True)

        except Exception as e:
            print(f"❌ 최소 Add 화면 생성 실패: {e}")

    # ==================== 이벤트 핸들러 ====================

    def on_select_files(self):
        """파일 선택 이벤트 핸들러"""
        self.controller.select_files()
        self.update_file_list()

    def on_select_folder(self):
        """폴더 선택 이벤트 핸들러"""
        self.controller.select_folder()
        # 폴더 선택은 controller에서 직접 data.json을 업데이트하므로
        # 별도의 UI 업데이트는 필요 없음

    def on_clear_files(self):
        """파일 목록 초기화 이벤트 핸들러"""
        if self.controller.clear_files():
            self.update_file_list()

    def on_remove_selected_file(self, event=None):
        """선택된 파일 제거 이벤트 핸들러 (더블클릭)"""
        try:
            if hasattr(self, 'file_listbox') and self.file_listbox is not None:
                try:
                    selection = self.file_listbox.curselection()
                    if selection:
                        index = selection[0]
                        if 0 <= index < len(self.controller.selected_files):
                            file_name = os.path.basename(self.controller.selected_files[index])
                            if self.controller.remove_file_by_index(index):
                                self.update_file_list()
                                messagebox.showinfo("완료", f"파일이 제거되었습니다:\n{file_name}")
                    else:
                        messagebox.showinfo("알림", "제거할 파일을 선택하세요.")
                except tk.TclError as tcl_e:
                    print(f"  [AddView] ⚠️ Listbox 접근 오류: {tcl_e}")
            else:
                print(f"  [AddView] ⚠️ file_listbox가 생성되지 않음")
        except Exception as e:
            print(f"  [AddView] ❌ 파일 제거 실패: {e}")
            import traceback
            traceback.print_exc()

    def on_show_file_info(self):
        """파일 정보 표시 이벤트 핸들러"""
        try:
            if hasattr(self, 'file_listbox') and self.file_listbox is not None:
                try:
                    selection = self.file_listbox.curselection()
                    if selection:
                        index = selection[0]
                        if 0 <= index < len(self.controller.selected_files):
                            file_path = self.controller.selected_files[index]
                            file_info = self.controller.get_file_info(file_path)

                            if file_info:
                                info = f"""파일 정보:

경로: {file_info['path']}
크기: {file_info['size_formatted']}
수정일: {file_info['modified']}
읽기 전용: {'예' if file_info['readonly'] else '아니오'}"""

                                messagebox.showinfo("파일 정보", info)
                            else:
                                messagebox.showerror("오류", "파일 정보를 가져올 수 없습니다.")
                    else:
                        messagebox.showinfo("알림", "파일을 선택하세요.")
                except tk.TclError as tcl_e:
                    print(f"  [AddView] ⚠️ Listbox 접근 오류: {tcl_e}")
            else:
                print(f"  [AddView] ⚠️ file_listbox가 생성되지 않음")
        except Exception as e:
            print(f"  [AddView] ❌ 파일 정보 표시 실패: {e}")
            import traceback
            traceback.print_exc()

    def on_apply_files(self):
        """파일 적용 이벤트 핸들러"""
        self.controller.apply_files()

    def on_create_backup(self):
        """백업 생성 이벤트 핸들러"""
        self.controller.create_backup()

    # ==================== UI 업데이트 ====================

    def update_file_list(self):
        """파일 목록 업데이트"""
        try:
            # file_listbox가 존재하고 None이 아닌지 확인
            if hasattr(self, 'file_listbox') and self.file_listbox is not None:
                try:
                    self.file_listbox.delete(0, tk.END)

                    for file_path in self.controller.selected_files:
                        # 파일명과 크기 정보 표시
                        try:
                            file_name = os.path.basename(file_path)
                            file_size = os.path.getsize(file_path)
                            size_str = self.controller.format_file_size(file_size)
                            display_text = f"{file_name} ({size_str})"
                            self.file_listbox.insert(tk.END, display_text)
                        except Exception as inner_e:
                            # 파일 정보를 가져올 수 없으면 파일명만 표시
                            try:
                                self.file_listbox.insert(tk.END, os.path.basename(file_path))
                            except:
                                pass
                except tk.TclError as tcl_e:
                    print(f"  [AddView] ⚠️ Listbox가 이미 파괴됨: {tcl_e}")
            else:
                print(f"  [AddView] ⚠️ file_listbox가 아직 생성되지 않음")

        except Exception as e:
            print(f"  [AddView] ❌ 파일 목록 업데이트 실패: {e}")
            import traceback
            traceback.print_exc()
