import tkinter as tk
from tkinter import ttk, messagebox

try:
    from ..controllers import ScanController, ConfigManager
except ImportError:
    from controllers import ScanController, ConfigManager


class DastView:
    def __init__(self, main_window):
        self.main_window = main_window
        self.vulnerability_data = []
        self.current_filter = "All"  # 현재 선택된 필터

        # 컨트롤러 및 설정 관리자 초기화
        try:
            self.scan_controller = ScanController()
        except Exception as e:
            print(f"⚠️ DastView: ScanController 초기화 실패: {e}")
            self.scan_controller = None

        try:
            self.config_manager = ConfigManager()
        except Exception as e:
            print(f"⚠️ DastView: ConfigManager 초기화 실패: {e}")
            self.config_manager = None

    def setup_view(self, parent):
        """뷰 설정 - main_window에서 호출"""
        self.setup_ui(parent)

    def setup_ui(self, parent):
        """핵심 UI만 설정"""
        try:
            print("  [DastView] UI 설정 시작")

            # parent 저장 (나중에 after 사용)
            self.parent = parent

            # 메인 프레임
            main_frame = tk.Frame(parent, bg="white")
            main_frame.pack(fill="both", expand=True, padx=20, pady=20)
            print("  [DastView] 메인 프레임 생성 완료")

            # 상단 네비게이션 버튼 추가
            try:
                self.setup_navigation_buttons(main_frame)
                print("  [DastView] 네비게이션 버튼 생성 완료")
            except Exception as e:
                print(f"  [DastView] ⚠️ 네비게이션 버튼 생성 실패: {e}")

            # URL 입력 섹션
            try:
                self.setup_url_section(main_frame)
                print("  [DastView] URL 섹션 생성 완료")
            except Exception as e:
                print(f"  [DastView] ⚠️ URL 섹션 생성 실패: {e}")

            # 메인 컨텐츠 프레임 (테이블 + 상세정보를 좌우로 배치)
            content_frame = tk.Frame(main_frame, bg="white")
            content_frame.pack(fill="both", expand=True)
            print("  [DastView] 컨텐츠 프레임 생성 완료")

            # Grid 시스템으로 500:350 비율 유지하며 자동 크기 조절
            content_frame.grid_columnconfigure(0, weight=520, minsize=520)  # 최소 500px, 500 비율
            content_frame.grid_columnconfigure(1, weight=330, minsize=330)  # 최소 350px, 350 비율
            content_frame.grid_rowconfigure(0, weight=1)

            # 왼쪽: 취약점 테이블 섹션
            left_frame = tk.Frame(content_frame, bg="white")
            left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
            try:
                self.setup_vulnerability_table(left_frame)
                print("  [DastView] 취약점 테이블 생성 완료")
            except Exception as e:
                print(f"  [DastView] ⚠️ 취약점 테이블 생성 실패: {e}")
                import traceback
                traceback.print_exc()

            # 오른쪽: 상세 정보 패널
            right_frame = tk.Frame(content_frame, bg="white")
            right_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 5))
            try:
                self.setup_detail_panel(right_frame)
                print("  [DastView] 상세 패널 생성 완료")
            except Exception as e:
                print(f"  [DastView] ⚠️ 상세 패널 생성 실패: {e}")

            print("  [DastView] UI 설정 완료")

        except Exception as e:
            print(f"  [DastView] ❌ UI 설정 실패: {e}")
            import traceback
            traceback.print_exc()
            raise

    def setup_navigation_buttons(self, parent):
        """상단 네비게이션 버튼 설정"""
        nav_frame = tk.Frame(parent, bg="white", height=50)
        nav_frame.pack(fill="x", pady=(0, 20))
        nav_frame.pack_propagate(False)

        # 버튼 데이터
        tabs = [
            ("검사", "dast"),
            ("결과", "results"),
            ("설정", "settings")
        ]

        # 각 버튼 생성
        for text, view in tabs:
            btn = tk.Button(
                nav_frame,
                text=text,
                command=lambda v=view: self.main_window.switch_view(v),
                bg="white",
                fg="#3498db" if view == "dast" else "#7f8c8d",
                font=("Arial", 12, "bold"),
                relief="flat",
                bd=0,
                cursor="hand2",
                activebackground="white",
                activeforeground="#2980b9"
            )
            btn.pack(side="left", padx=15, pady=10, expand=True, fill="both")

    def setup_url_section(self, parent):
        """검사 대상 선택 섹션 (URL 또는 폴더)"""
        from tkinter import filedialog

        main_section = tk.Frame(parent, bg="white")
        main_section.pack(fill="x", pady=(0, 20))

        # # 제목
        # tk.Label(main_section, text="검사 대상:", font=("Arial", 12, "bold"), bg="white").pack(anchor="w")

        # 라디오 버튼 변수
        self.scan_type = tk.StringVar(value="url")  # 기본값: URL

        # --- URL 옵션 ---
        url_frame = tk.Frame(main_section, bg="white")
        url_frame.pack(fill="x", pady=(10, 5))

        # URL 라디오 버튼
        url_radio = tk.Radiobutton(
            url_frame,
            text="URL",
            variable=self.scan_type,
            value="url",
            font=("Arial", 11),
            bg="white",
            command=self.on_scan_type_changed
        )
        url_radio.pack(side="left")

        # URL 입력 필드
        self.url_entry = tk.Entry(url_frame, font=("Arial", 11))
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(10, 0), ipady=6)

        # web_url 기본값 설정
        try:
            if self.config_manager:
                default_url = self.config_manager.get_web_url()
                if default_url:
                    self.url_entry.insert(0, default_url)
        except Exception as e:
            print(f"⚠️ 기본 URL 설정 실패: {e}")

        # --- 폴더 경로 옵션 ---
        folder_frame = tk.Frame(main_section, bg="white")
        folder_frame.pack(fill="x", pady=(5, 10))

        # 폴더 경로 라디오 버튼
        folder_radio = tk.Radiobutton(
            folder_frame,
            text="폴더 경로",
            variable=self.scan_type,
            value="folder",
            font=("Arial", 11),
            bg="white",
            command=self.on_scan_type_changed
        )
        folder_radio.pack(side="left")

        # 폴더 경로 입력 필드
        self.folder_entry = tk.Entry(folder_frame, font=("Arial", 11), state="disabled")
        self.folder_entry.pack(side="left", fill="x", expand=True, padx=(10, 5), ipady=6)

        # Web_Dir 기본값 설정
        try:
            if self.config_manager:
                default_folder = self.config_manager.get_config().get("Web_Dir", "")
                if default_folder:
                    self.folder_entry.insert(0, default_folder)
        except Exception as e:
            print(f"⚠️ 기본 폴더 설정 실패: {e}")

        # 찾아보기 버튼
        self.browse_button = tk.Button(
            folder_frame,
            text="찾아보기...",
            command=self.browse_folder,
            bg="#757575",
            fg="white",
            font=("Arial", 9, "bold"),
            relief="flat",
            padx=15,
            pady=6,
            state="disabled"
        )
        self.browse_button.pack(side="left")

        # --- 검사 시작 버튼 ---
        button_frame = tk.Frame(main_section, bg="white")
        button_frame.pack(fill="x", pady=(10, 0))

        self.start_button = tk.Button(
            button_frame,
            text="검사 시작",
            command=self.start_scan,
            bg="#2196f3",
            fg="white",
            font=("Arial", 11, "bold"),
            relief="flat",
            padx=30,
            pady=10
        )
        self.start_button.pack(anchor="center")

    def on_scan_type_changed(self):
        """라디오 버튼 선택 변경 시 호출"""
        if self.scan_type.get() == "url":
            # URL 모드: URL 입력 활성화, 폴더 입력 비활성화
            self.url_entry.config(state="normal")
            self.folder_entry.config(state="disabled")
            self.browse_button.config(state="disabled")
        else:
            # 폴더 모드: URL 입력 비활성화, 폴더 입력 활성화
            self.url_entry.config(state="disabled")
            self.folder_entry.config(state="normal")
            self.browse_button.config(state="normal")

    def browse_folder(self):
        """폴더 선택 다이얼로그"""
        from tkinter import filedialog
        import json
        import os

        folder_path = filedialog.askdirectory(title="검사할 프로젝트 폴더 선택")

        if folder_path:
            # 절대 경로로 변환
            abs_path = os.path.abspath(folder_path)

            # 입력 필드 업데이트
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, abs_path)

            # user_info.json의 Web_Dir 업데이트
            try:
                if self.config_manager:
                    config = self.config_manager.get_config()
                    config["Web_Dir"] = abs_path
                    self.config_manager.save_config(config)
                    print(f"✅ Web_Dir 업데이트: {abs_path}")
            except Exception as e:
                print(f"⚠️ Web_Dir 업데이트 실패: {e}")

    def setup_vulnerability_table(self, parent):
        """취약점 테이블 설정"""
        print("    [Table] 시작")
        table_frame = tk.Frame(parent, bg="white")
        table_frame.pack(fill="both", expand=True, padx=(0, 5), pady=(0, 20))
        print("    [Table] 프레임 완료")

        # 헤더 프레임 (필터 + 제목)
        header_frame = tk.Frame(table_frame, bg="white")
        header_frame.pack(fill="x", pady=(0, 10))

        # 필터 프레임 (왼쪽)
        filter_frame = tk.Frame(header_frame, bg="white")
        filter_frame.pack(side="left")

        # 필터 라벨
        tk.Label(
            filter_frame,
            text="결과:",
            font=("Arial", 10),
            bg="white",
            fg="#666"
        ).pack(side="left", padx=(0, 5))

        # 필터 콤보박스
        filter_options = ["All", "A01", "A02", "A03", "A04", "A05", "A06", "A07", "A08", "A09", "A10"]
        self.filter_var = tk.StringVar(value="All")
        self.filter_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.filter_var,
            values=filter_options,
            state="readonly",
            width=8,
            font=("Arial", 9)
        )
        self.filter_combo.pack(side="left", padx=(0, 15))
        self.filter_combo.bind("<<ComboboxSelected>>", self.on_filter_change)

        # 테이블 제목 (위험도 컬럼 위에 위치)
        print("    [Table] 라벨 생성 시작...")
        tk.Label(
            header_frame,
            text="발견된 취약점",
            font=("Arial", 14, "bold"),
            bg="white",
            fg="#333"
        ).pack(side="left", padx=(90, 0))
        print("    [Table] 라벨 완료")

        # Treeview 생성
        print("    [Table] Treeview 생성 시작...")
        columns = ("test_id", "test_name", "risk_level", "location")
        self.tree_view = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        print("    [Table] Treeview 생성 완료")

        # 컬럼 설정
        self.tree_view.heading("test_id", text="테스트 ID")
        self.tree_view.heading("test_name", text="취약점 명")
        self.tree_view.heading("risk_level", text="위험도")
        self.tree_view.heading("location", text="경로")

        # 컬럼 너비 설정 (동적 크기 조절 가능)
        self.tree_view.column("test_id", width=80, minwidth=60, stretch=True)
        self.tree_view.column("test_name", width=120, minwidth=100, stretch=True)
        self.tree_view.column("risk_level", width=70, minwidth=60, stretch=True)
        self.tree_view.column("location", width=200, minwidth=150, stretch=True)

        # 스크롤바
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree_view.yview)
        self.tree_view.configure(yscrollcommand=scrollbar.set)

        # 테이블과 스크롤바 배치
        self.tree_view.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 선택 이벤트 바인딩
        self.tree_view.bind("<<TreeviewSelect>>", self.on_item_select)

    def setup_detail_panel(self, parent):
        """오른쪽 상세 정보 패널"""
        detail_frame = tk.Frame(parent, bg="white", relief="solid", bd=1)
        detail_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # 제목
        title_frame = tk.Frame(detail_frame, bg="#f0f0f0")
        title_frame.pack(fill="x")

        tk.Label(title_frame, text="상세 정보",
                font=("Arial", 14, "bold"), bg="#f0f0f0", fg="#333").pack(pady=10)

        # 스크롤 가능한 텍스트 위젯
        text_frame = tk.Frame(detail_frame, bg="white")
        text_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # 스크롤바
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side="right", fill="y", padx=(0, 5))

        self.detail_text = tk.Text(
            text_frame,
            font=("Arial", 10),
            bg="#f8f9fa",
            relief="flat",
            wrap=tk.WORD,
            state="disabled",
            yscrollcommand=scrollbar.set
        )
        self.detail_text.pack(side="left", fill="both", expand=True, padx=(5, 0))
        scrollbar.config(command=self.detail_text.yview)

        # 기본 메시지
        self.update_detail_text("취약점을 선택하면 상세 정보가 표시됩니다.")

    def start_scan(self):
        """검사 시작 - ScanController 사용"""
        try:
            # 검사 타입에 따라 처리
            scan_type = self.scan_type.get()

            if scan_type == "url":
                # URL 모드
                url = self.url_entry.get().strip()

                if not url:
                    messagebox.showerror("오류", "검사할 URL을 입력해주세요.")
                    return

                if not url.startswith(("http://", "https://")):
                    url = "http://" + url
                    self.url_entry.delete(0, tk.END)
                    self.url_entry.insert(0, url)

                print(f"🚀 검사 시작 (URL): {url}")

                # ConfigManager로 URL 업데이트
                self.config_manager.set_web_url(url)

            else:
                # 폴더 경로 모드
                folder_path = self.folder_entry.get().strip()

                if not folder_path:
                    messagebox.showerror("오류", "검사할 폴더 경로를 선택해주세요.")
                    return

                import os
                if not os.path.exists(folder_path):
                    messagebox.showerror("오류", f"폴더를 찾을 수 없습니다:\n{folder_path}")
                    return

                print(f"🚀 검사 시작 (폴더): {folder_path}")

                # ConfigManager로 Web_Dir 업데이트 (이미 browse_folder에서 업데이트됨)
                # 검사 시작 시 한 번 더 확인
                config = self.config_manager.get_config()
                config["Web_Dir"] = folder_path
                self.config_manager.save_config(config)

                # URL은 기본값 사용 (user_info.json의 web_url)
                url = self.config_manager.get_web_url() or "http://localhost"

            # UI 상태 변경
            self.start_button.config(state="disabled", text="검사 중...")

            # 테이블 초기화
            for item in self.tree_view.get_children():
                self.tree_view.delete(item)
            self.vulnerability_data.clear()

            # GUI 콜백 함수 정의
            def gui_update_callback(results_json):
                # 메인 스레드에서 GUI 업데이트
                self.main_window.root.after(0, lambda: self.update_vulnerability_list(results_json))

            # ScanController로 검사 시작
            success = self.scan_controller.start_scan(url, gui_update_callback)

            if not success:
                messagebox.showwarning("경고", "이미 검사가 진행 중입니다.")
                self.start_button.config(state="normal", text="검사 시작")
                return

            # 검사 완료 후 UI 복원을 위한 콜백 등록
            def on_scan_complete():
                self.main_window.root.after(0, lambda: self.start_button.config(state="normal", text="검사 시작"))

            # 기존 콜백 래핑
            original_callback = self.scan_controller.callback
            def wrapped_callback(result):
                if original_callback:
                    original_callback(result)
                on_scan_complete()

            self.scan_controller.callback = wrapped_callback

        except Exception as e:
            print(f"❌ 검사 시작 실패: {e}")
            messagebox.showerror("오류", f"검사 시작 중 오류가 발생했습니다: {e}")
            self.start_button.config(state="normal", text="검사 시작")

    def update_vulnerability_list(self, scan_results):
        """검사 결과로 취약점 목록 업데이트"""
        try:
            # 테이블 초기화
            for item in self.tree_view.get_children():
                self.tree_view.delete(item)
            self.vulnerability_data.clear()

            if not scan_results or 'categories' not in scan_results:
                self.update_detail_text("취약점이 발견되지 않았습니다.")
                return

            vulnerability_count = 0

            for category_id, category_data in scan_results['categories'].items():
                for test in category_data.get('tests', []):
                    details = test.get('details', [])
                    if details:  # 취약점이 발견된 경우만
                        test_id = test.get('test_id', '')
                        test_name = test.get('test_name', '알 수 없음')
                        risk_level = test.get('risk_level', '미분류')

                        # details 배열의 각 개별 취약점마다 테이블 행 생성
                        for detail in details:
                            vulnerability_count += 1

                            # 테이블에 개별 취약점 추가 (텍스트 길이 제한)
                            location = detail.get('location', 'N/A')
                            
                            # 동적 텍스트 길이 제한 (컬럼 크기에 따라)
                            truncated_test_id = self._truncate_text(test_id, self._get_dynamic_truncate_length("test_id"))
                            truncated_test_name = self._truncate_text(test_name, self._get_dynamic_truncate_length("test_name"))
                            truncated_risk_level = self._truncate_text(risk_level, self._get_dynamic_truncate_length("risk_level"))
                            truncated_location = self._truncate_text(location, self._get_dynamic_truncate_length("location"))
                            
                            self.tree_view.insert("", "end", values=(
                                truncated_test_id, 
                                truncated_test_name, 
                                truncated_risk_level, 
                                truncated_location
                            ))

                            # 상세 데이터 저장 (개별 취약점 정보)
                            self.vulnerability_data.append({
                                'test_id': test_id,
                                'test_name': test_name,
                                'risk_level': risk_level,
                                'detail': detail  # 개별 취약점 하나만 저장
                            })

            if vulnerability_count == 0:
                self.update_detail_text("취약점이 발견되지 않았습니다.")
            else:
                self.update_detail_text(f"총 {vulnerability_count}개의 취약점이 발견되었습니다.\n취약점을 선택하면 상세 정보가 표시됩니다.")

        except Exception as e:
            print(f"❌ 취약점 목록 업데이트 실패: {e}")

    def get_filtered_vulnerabilities(self):
        """현재 필터에 따라 취약점 데이터 필터링"""
        if self.current_filter == "All":
            return self.vulnerability_data
        
        # A01-A10 필터 적용
        filtered_data = []
        for vuln in self.vulnerability_data:
            test_id = vuln.get("test_id", "")
            if test_id.startswith(self.current_filter):
                filtered_data.append(vuln)
        
        return filtered_data

    def on_filter_change(self, event=None):
        """필터 변경 이벤트"""
        self.current_filter = self.filter_var.get()
        print(f"🔍 필터 변경: {self.current_filter}")
        
        # 취약점 목록 다시 로드
        self.refresh_vulnerability_table()

    def refresh_vulnerability_table(self):
        """취약점 테이블만 새로고침"""
        # 기존 항목 제거
        for item in self.tree_view.get_children():
            self.tree_view.delete(item)

        if not self.vulnerability_data:
            return

        # 필터 적용된 데이터 가져오기
        display_data = self.get_filtered_vulnerabilities()

        if not display_data:
            return

        # 필터링된 데이터로 테이블 업데이트
        for vuln in display_data:
            test_id = vuln.get('test_id', '')
            test_name = vuln.get('test_name', '알 수 없음')
            risk_level = vuln.get('risk_level', '미분류')
            
            detail = vuln.get('detail', {})
            location = detail.get('location', 'N/A')
            
            # 동적 텍스트 길이 제한 (컬럼 크기에 따라)
            truncated_test_id = self._truncate_text(test_id, self._get_dynamic_truncate_length("test_id"))
            truncated_test_name = self._truncate_text(test_name, self._get_dynamic_truncate_length("test_name"))
            truncated_risk_level = self._truncate_text(risk_level, self._get_dynamic_truncate_length("risk_level"))
            truncated_location = self._truncate_text(location, self._get_dynamic_truncate_length("location"))
            
            self.tree_view.insert("", "end", values=(
                truncated_test_id, 
                truncated_test_name, 
                truncated_risk_level, 
                truncated_location
            ))

        # 상세 정보 업데이트
        filtered_count = len(display_data)
        if filtered_count == 0:
            self.update_detail_text("선택한 필터에 해당하는 취약점이 없습니다.")
        else:
            self.update_detail_text(f"필터 적용 결과: {filtered_count}개의 취약점이 발견되었습니다.\n취약점을 선택하면 상세 정보가 표시됩니다.")

    def _truncate_text(self, text, max_length):
        """텍스트가 최대 길이를 초과하면 ...로 표시"""
        if not text:
            return text
        text_str = str(text)
        if len(text_str) <= max_length:
            return text_str
        return text_str[:max_length-3] + "..."

    def _get_dynamic_truncate_length(self, column_name):
        """컬럼 크기에 따른 동적 truncate 길이 계산"""
        try:
            current_width = self.tree_view.column(column_name, "width")
            # 대략적인 문자당 픽셀 계산 (Arial 10pt 기준)
            char_width = 8
            available_chars = max(5, (current_width - 20) // char_width)  # 최소 5자
            return int(available_chars)
        except:
            # 기본값 반환
            defaults = {"test_id": 10, "test_name": 15, "risk_level": 8, "location": 25}
            return defaults.get(column_name, 15)

    def _format_value(self, key, value):
        """값 포맷팅 (timestamp, list, dict 처리)"""
        # timestamp 포맷팅
        if key == 'timestamp' and value and value != 'N/A':
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                return dt.strftime('%Y년 %m월 %d일 %H:%M:%S')
            except:
                return value

        # 리스트를 문자열로 변환
        elif isinstance(value, list):
            return ', '.join(str(v) for v in value) if value else '없음'

        # 딕셔너리를 문자열로 변환
        elif isinstance(value, dict):
            return str(value)

        # 그 외는 그대로
        return value

    def on_item_select(self, event):
        """테이블 항목 선택 시 상세 정보 업데이트"""
        try:
            selection = self.tree_view.selection()
            if not selection:
                return

            item = self.tree_view.item(selection[0])
            values = item['values']

            if len(values) >= 4:
                test_id = values[0]
                test_name = values[1]
                risk_level = values[2]
                location = values[3]

                # 선택된 행의 인덱스로 필터링된 데이터에서 접근
                selection_index = self.tree_view.index(selection[0])
                filtered_data = self.get_filtered_vulnerabilities()
                if selection_index < len(filtered_data):
                    vuln_data = filtered_data[selection_index]
                else:
                    vuln_data = None

                if vuln_data:
                    detail = vuln_data.get('detail', {})

                    # detail의 모든 필드를 동적으로 출력
                    detail_info = ""

                    # 1. 기본 정보 (테이블에서 가져온 값)
                    detail_info += f"• 테스트 ID: {test_id}\n"
                    detail_info += f"• 검사 유형: {test_name}\n"
                    detail_info += f"• 위험도: {risk_level}\n"

                    # 2. 한글 라벨 매핑
                    FIELD_LABELS = {
                        'location': '위치',
                        'description': '설명',
                        'method': '메서드',
                        'timestamp': '시간',
                        'csrf_token': 'CSRF 토큰',
                        'injection_type': 'Injection 유형',
                        'payload': '공격 페이로드',
                        'missing_headers': '누락된 헤더',
                        'line': '라인 번호',
                        'pattern': '탐지 패턴',
                        'status_code': '응답 코드',
                        'response_time': '응답 시간',
                        'cookie': '쿠키',
                        'session': '세션',
                        'user_agent': 'User Agent',
                        'port': '포트',
                        'service': '서비스',
                        'additional_info': None  # additional_info는 건너뛰기 위한 마커
                    }

                    # 3. detail의 모든 키-값을 items()로 출력
                    for key, value in detail.items():
                        # 값 포맷팅 (함수 사용)
                        formatted_value = self._format_value(key, value)

                        # 한글 라벨 가져오기 (없으면 키를 읽기 쉽게 변환)
                        label = FIELD_LABELS.get(key, key.replace('_', ' ').title())
                        detail_info += f"• {label}: {formatted_value}\n"

                    # 5. 취약점 설명
                    detail_info += "\n" + self._get_vulnerability_description(test_name)

                    self.update_detail_text(detail_info)

        except Exception as e:
            print(f"❌ 항목 선택 처리 실패: {e}")

    def _format_csrf_detail(self, detail):
        """A01 CSRF 상세 정보 포맷팅"""
        result = []

        # 보호 메커니즘
        protections = detail.get("protections", [])
        if protections:
            result.append(f"• 보호 메커니즘: {', '.join(protections)}")
        else:
            result.append("• 보호 메커니즘: 없음")

        # SameSite Cookie
        samesite = detail.get("samesite", False)
        result.append(f"• SameSite Cookie: {'설정됨' if samesite else '미설정'}")

        # CSRF 토큰
        tokens = detail.get("tokens_found", [])
        if tokens:
            result.append(f"• CSRF 토큰: {len(tokens)}개 발견")
        else:
            result.append("• CSRF 토큰: 발견되지 않음")

        # 폼 분석
        forms = detail.get("forms", [])
        if forms:
            post_forms = [f for f in forms if f.get("method") == "POST"]
            get_forms = [f for f in forms if f.get("method") == "GET"]

            result.append(f"• 전체 폼: {len(forms)}개")
            if post_forms:
                result.append(f"  - POST 폼: {len(post_forms)}개")
                forms_without_token = [f for f in post_forms if not f.get("tokens")]
                if forms_without_token:
                    result.append(f"  - ⚠ CSRF 토큰 없는 POST 폼: {len(forms_without_token)}개")
            if get_forms:
                result.append(f"  - GET 폼: {len(get_forms)}개")

        # 설명
        description = detail.get("description", "")
        if description:
            result.append(f"• 상세 설명: {description}")

        return "\n".join(result)

    def _format_injection_detail(self, detail):
        """A03 Injection 상세 정보 포맷팅"""
        result = []

        # 라인 번호
        line = detail.get("line", "")
        if line:
            result.append(f"• 라인 번호: {line}")

        # 패턴 (취약한 코드)
        pattern = detail.get("pattern", "")
        if pattern:
            result.append(f"• 탐지된 코드:\n  {pattern}")

        return "\n".join(result)

    def _get_vulnerability_description(self, test_name):
        """취약점 유형별 설명 반환"""
        if "CSRF" in test_name:
            return ("• 취약점 설명: 공격자가 사용자의 권한을 도용하여 악의적인 요청을 실행할 수 있는 취약점입니다.\n"
                   "• 권장 조치: CSRF 토큰 구현, SameSite 쿠키 속성 설정, Referer 검증\n")
        elif "Rate_Limit" in test_name:
            return ("• 취약점 설명: 요청 빈도 제한이 설정되지 않아 무차별 공격(브루트포스)이 가능한 취약점입니다.\n"
                   "• 권장 조치: 요청 빈도 제한 설정, IP별 접근 제한 구현, 계정 잠금 정책 적용\n")
        elif "XSS" in test_name:
            return ("• 취약점 설명: 웹 페이지에 악성 스크립트를 삽입하여 사용자의 브라우저에서 실행되는 취약점입니다.\n"
                   "• 권장 조치: 입력값 검증 및 이스케이프 처리, Content Security Policy 적용, HttpOnly 쿠키 설정\n")
        elif "SQL" in test_name:
            return ("• 취약점 설명: 데이터베이스 쿼리에 악성 SQL 코드를 삽입하여 데이터베이스를 조작할 수 있는 취약점입니다.\n"
                   "• 권장 조치: Prepared Statement 사용, 입력값 검증 강화, 데이터베이스 권한 최소화\n")
        elif "Command" in test_name or "Injection" in test_name:
            return ("• 취약점 설명: 시스템 명령어나 코드를 주입하여 서버를 조작할 수 있는 취약점입니다.\n"
                   "• 권장 조치: 입력값 검증 및 살균 처리, 안전한 API 사용, 최소 권한 원칙 적용\n")
        elif "Check_vulnerable" in test_name:
            return ("• 취약점 설명: 보안 헤더가 누락되거나 민감한 정보가 HTTP 헤더를 통해 노출되는 취약점입니다.\n"
                   "• 권장 조치: 보안 헤더 추가 (X-Frame-Options 등), 서버 정보 헤더 제거, HTTPS 강제 적용\n")
        else:
            return (f"• 취약점 설명: {test_name} 관련 보안 취약점이 발견되었습니다.\n"
                   "• 권장 조치: 상세한 보안 점검 수행, 보안 전문가 상담, 정기적인 취약점 점검\n")

    def update_detail_text(self, text):
        """상세 정보 텍스트 업데이트"""
        try:
            self.detail_text.config(state="normal")
            self.detail_text.delete("1.0", tk.END)
            self.detail_text.insert("1.0", text)
            self.detail_text.config(state="disabled")
        except Exception as e:
            print(f"❌ 상세 정보 업데이트 실패: {e}")
