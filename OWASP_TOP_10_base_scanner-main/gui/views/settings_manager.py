"""
설정 관리 모듈
사용자 설정 및 구성 관리
"""
import tkinter as tk
from tkinter import messagebox
try:
    from ..utils import load_user_info, save_user_info
except ImportError:
    from utils import load_user_info, save_user_info

class SettingsManager:
    """설정 관리 클래스"""
    
    def __init__(self, main_window=None):
        self.main_window = main_window
        self.settings = {}
        self.load_settings()

    def load_settings(self):
        """설정 로드"""
        self.settings = load_user_info()
        
    def setup_view(self, parent_frame):
        """설정 뷰 설정"""
        try:
            print("🔧 설정 뷰 초기화 시작...")

            # 메인 컨테이너
            main_container = tk.Frame(parent_frame, bg="#ffffff")
            main_container.pack(fill="both", expand=True, padx=20, pady=20)

            # 네비게이션 버튼 추가
            self.setup_navigation_buttons(main_container)

            # 간단한 설정 화면 (스크롤 없이)
            try:
                # 제목
                title_label = tk.Label(
                    main_container,
                    font=("Arial", 18, "bold"),
                    bg="#ffffff",
                    fg="#2c3e50"
                )
                title_label.pack(pady=(10, 30))
                
                # 설정 섹션들 생성 (간단하게)
                self.setup_basic_settings_simple(main_container)
                self.setup_actions_simple(main_container)
                
                print("✅ 설정 뷰 초기화 완료")
                
            except Exception as section_error:
                print(f"❌ 설정 섹션 생성 실패: {section_error}")
                # 최소한의 설정 화면
                self.setup_minimal_settings(main_container)
                
        except Exception as e:
            print(f"❌ 설정 뷰 초기화 실패: {e}")
            raise e

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
                command=lambda v=view: self.main_window.switch_view(v) if self.main_window else None,
                bg="white",
                fg="#3498db" if view == "settings" else "#7f8c8d",
                font=("Arial", 12, "bold"),
                relief="flat",
                bd=0,
                cursor="hand2",
                activebackground="white",
                activeforeground="#2980b9"
            )
            btn.pack(side="left", padx=15, pady=10, expand=True, fill="both")

    def setup_basic_settings_simple(self, parent):
        """기존 monitor.py 방식의 설정"""
        try:
            # 입력 필드를 가운데 정렬하기 위한 컨테이너
            url_input_container = tk.Frame(parent, bg="white")
            url_input_container.place(relx=0.5, rely=0.55, anchor="center", relwidth=0.8, relheight=0.8)

            # 설정 입력 필드들을 위한 프레임
            settings_frame = tk.Frame(url_input_container, bg="white")
            settings_frame.pack(pady=(80, 15))
            
            # 웹 URL 입력
            web_url_frame = tk.Frame(settings_frame, bg="white")
            web_url_frame.pack(fill="x", pady=2)
            tk.Label(web_url_frame, text="Web URL:", font=("Arial", 10), bg="white", width=15, anchor="w").pack(side="left")
            self.url_entry = tk.Entry(web_url_frame, font=("Arial", 10), relief="solid", bd=1, width=35)
            self.url_entry.pack(side="left")
            
            # 호스트 입력
            host_frame = tk.Frame(settings_frame, bg="white")
            host_frame.pack(fill="x", pady=2)
            tk.Label(host_frame, text="Host:", font=("Arial", 10), bg="white", width=15, anchor="w").pack(side="left")
            self.host_entry = tk.Entry(host_frame, font=("Arial", 10), relief="solid", bd=1, width=35)
            self.host_entry.pack(side="left")
            
            # DB ID 입력
            db_id_frame = tk.Frame(settings_frame, bg="white")
            db_id_frame.pack(fill="x", pady=2)
            tk.Label(db_id_frame, text="DB ID:", font=("Arial", 10), bg="white", width=15, anchor="w").pack(side="left")
            self.db_id_entry = tk.Entry(db_id_frame, font=("Arial", 10), relief="solid", bd=1, width=35)
            self.db_id_entry.pack(side="left")
            
            # DB 비밀번호 입력
            db_pw_frame = tk.Frame(settings_frame, bg="white")
            db_pw_frame.pack(fill="x", pady=2)
            tk.Label(db_pw_frame, text="DB Password:", font=("Arial", 10), bg="white", width=15, anchor="w").pack(side="left")
            self.db_pw_entry = tk.Entry(db_pw_frame, font=("Arial", 10), relief="solid", bd=1, width=35, show="*")
            self.db_pw_entry.pack(side="left")
            
            # DB 포트 입력
            db_port_frame = tk.Frame(settings_frame, bg="white")
            db_port_frame.pack(fill="x", pady=2)
            tk.Label(db_port_frame, text="DB Port:", font=("Arial", 10), bg="white", width=15, anchor="w").pack(side="left")
            self.db_port_entry = tk.Entry(db_port_frame, font=("Arial", 10), relief="solid", bd=1, width=35)
            self.db_port_entry.pack(side="left")
            
            # DB 이름 입력
            db_name_frame = tk.Frame(settings_frame, bg="white")
            db_name_frame.pack(fill="x", pady=2)
            tk.Label(db_name_frame, text="DB Name:", font=("Arial", 10), bg="white", width=15, anchor="w").pack(side="left")
            self.db_name_entry = tk.Entry(db_name_frame, font=("Arial", 10), relief="solid", bd=1, width=35)
            self.db_name_entry.pack(side="left")
            
            # 로그인 URL 입력
            login_url_frame = tk.Frame(settings_frame, bg="white")
            login_url_frame.pack(fill="x", pady=2)
            tk.Label(login_url_frame, text="Login URL:", font=("Arial", 10), bg="white", width=15, anchor="w").pack(side="left")
            self.login_url_entry = tk.Entry(login_url_frame, font=("Arial", 10), relief="solid", bd=1, width=35)
            self.login_url_entry.pack(side="left")
            
            # 테스트 이메일 입력
            test_email_frame = tk.Frame(settings_frame, bg="white")
            test_email_frame.pack(fill="x", pady=2)
            tk.Label(test_email_frame, text="Test Email:", font=("Arial", 10), bg="white", width=15, anchor="w").pack(side="left")
            self.test_email_entry = tk.Entry(test_email_frame, font=("Arial", 10), relief="solid", bd=1, width=35)
            self.test_email_entry.pack(side="left")
            
            # 테스트 비밀번호 입력
            test_pw_frame = tk.Frame(settings_frame, bg="white")
            test_pw_frame.pack(fill="x", pady=2)
            tk.Label(test_pw_frame, text="Test Password:", font=("Arial", 10), bg="white", width=15, anchor="w").pack(side="left")
            self.test_pw_entry = tk.Entry(test_pw_frame, font=("Arial", 10), relief="solid", bd=1, width=35, show="*")
            self.test_pw_entry.pack(side="left")
            
            # user_info.json에서 모든 정보 자동 로드
            self.load_settings_to_fields()
            
            # 하단 확인 버튼을 settings_frame 아래에 추가
            bottom_button_frame = tk.Frame(url_input_container, bg="white")
            bottom_button_frame.pack(pady=(20, 0))
            
            confirm_button = tk.Button(
                bottom_button_frame, 
                text="확인", 
                command=self.save_settings_simple,
                bg="#4CAF50", 
                fg="white", 
                font=("Arial", 14),
                relief="solid", 
                bd=1, 
                width=8, 
                height=1
            )
            confirm_button.pack()
                
        except Exception as e:
            print(f"❌ 기본 설정 생성 실패: {e}")
            
    def setup_actions_simple(self, parent):
        """액션 버튼은 이미 setup_basic_settings_simple에서 처리됨"""
        # parent 파라미터는 인터페이스 일관성을 위해 필요
        pass
            
    def load_settings_to_fields(self):
        """user_info.json에서 설정을 로드해서 필드에 채움"""
        try:
            user_info = load_user_info()
            
            # 각 필드에 값 설정
            if hasattr(self, 'url_entry'):
                self.url_entry.insert(0, user_info.get("web_url", ""))
            if hasattr(self, 'host_entry'):
                self.host_entry.insert(0, user_info.get("host", ""))
            if hasattr(self, 'db_id_entry'):
                self.db_id_entry.insert(0, user_info.get("DB_ID", ""))
            if hasattr(self, 'db_pw_entry'):
                self.db_pw_entry.insert(0, user_info.get("DB_PW", ""))
            if hasattr(self, 'db_port_entry'):
                self.db_port_entry.insert(0, user_info.get("DB_PORT", ""))
            if hasattr(self, 'db_name_entry'):
                self.db_name_entry.insert(0, user_info.get("DB_NAME", ""))
            if hasattr(self, 'login_url_entry'):
                self.login_url_entry.insert(0, user_info.get("login_url", ""))
            if hasattr(self, 'test_email_entry'):
                self.test_email_entry.insert(0, user_info.get("test_email", ""))
            if hasattr(self, 'test_pw_entry'):
                self.test_pw_entry.insert(0, user_info.get("test_password", ""))
                
            print("✅ 설정 로드 완료")
            
        except FileNotFoundError:
            print("⚠️ user_info.json 파일을 찾을 수 없습니다.")
        except Exception as e:
            print(f"⚠️ 설정 로드 실패: {e}")
            
    def setup_minimal_settings(self, parent):
        """최소한의 설정 화면"""
        try:
            label = tk.Label(
                parent,
                text="⚙️ 설정 화면\n\n설정 기능을 로드하는 중 문제가 발생했습니다.\n기본 설정만 사용 가능합니다.",
                font=("Arial", 14),
                bg="#ffffff",
                fg="#2c3e50",
                justify="center"
            )
            label.pack(expand=True)
            
        except Exception as e:
            print(f"❌ 최소 설정 화면 생성 실패: {e}")
            
    def save_settings_simple(self):
        """monitor.py 방식의 설정 저장"""
        try:
            # 모든 필드에서 값을 수집
            updated_settings = {}
            
            if hasattr(self, 'url_entry'):
                updated_settings["web_url"] = self.url_entry.get().strip()
            if hasattr(self, 'host_entry'):
                updated_settings["host"] = self.host_entry.get().strip()
            if hasattr(self, 'db_id_entry'):
                updated_settings["DB_ID"] = self.db_id_entry.get().strip()
            if hasattr(self, 'db_pw_entry'):
                updated_settings["DB_PW"] = self.db_pw_entry.get().strip()
            if hasattr(self, 'db_port_entry'):
                updated_settings["DB_PORT"] = self.db_port_entry.get().strip()
            if hasattr(self, 'db_name_entry'):
                updated_settings["DB_NAME"] = self.db_name_entry.get().strip()
            if hasattr(self, 'login_url_entry'):
                updated_settings["login_url"] = self.login_url_entry.get().strip()
            if hasattr(self, 'test_email_entry'):
                updated_settings["test_email"] = self.test_email_entry.get().strip()
            if hasattr(self, 'test_pw_entry'):
                updated_settings["test_password"] = self.test_pw_entry.get().strip()
            
            # 기존 설정과 병합
            self.settings.update(updated_settings)
            
            # 저장
            if save_user_info(self.settings):
                messagebox.showinfo("성공", "설정이 저장되었습니다.")
                print("✅ 설정 저장 완료")
            else:
                messagebox.showerror("오류", "설정 저장에 실패했습니다.")
                
        except Exception as e:
            print(f"❌ 설정 저장 실패: {e}")
            messagebox.showerror("오류", f"설정 저장 중 오류: {e}")
            
    def reset_settings_simple(self):
        """간단한 설정 초기화"""
        try:
            if hasattr(self, 'url_entry'):
                self.url_entry.delete(0, tk.END)
                self.url_entry.insert(0, "http://example.com")
                
            messagebox.showinfo("완료", "설정이 초기화되었습니다.")
            
        except Exception as e:
            messagebox.showerror("오류", f"설정 초기화 중 오류: {e}")
        
    def setup_basic_settings(self, parent):
        """기본 설정 섹션"""
        shadow_frame, card_frame = self.ui_components.create_card_frame(
            parent, title="🌐 기본 설정"
        )
        shadow_frame.pack(fill="x", pady=(0, 20))
        
        content_frame = tk.Frame(card_frame, bg="#ffffff")
        content_frame.pack(fill="x", padx=20, pady=15)
        
        # 웹사이트 URL
        self.create_setting_row(
            content_frame,
            "웹사이트 URL:",
            "web_url",
            "검사할 대상 웹사이트의 URL을 입력하세요",
            "entry"
        )
        
        # 로그인 URL  
        self.create_setting_row(
            content_frame,
            "로그인 URL:",
            "login_url", 
            "로그인 페이지 URL (선택사항)",
            "entry"
        )
        
    def setup_scan_settings(self, parent):
        """검사 설정 섹션"""
        shadow_frame, card_frame = self.ui_components.create_card_frame(
            parent
        )
        shadow_frame.pack(fill="x", pady=(0, 20))
        
        content_frame = tk.Frame(card_frame, bg="#ffffff")
        content_frame.pack(fill="x", padx=20, pady=15)
        
        # 검사 타임아웃
        self.create_setting_row(
            content_frame,
            "요청 타임아웃 (초):",
            "timeout",
            "HTTP 요청 타임아웃 시간",
            "spinbox",
            {"from_": 1, "to": 60, "value": 10}
        )
        
        # 동시 요청 수
        self.create_setting_row(
            content_frame,
            "동시 요청 수:",
            "concurrent_requests",
            "동시에 실행할 최대 요청 수",
            "spinbox", 
            {"from_": 1, "to": 20, "value": 5}
        )
        
        # User-Agent
        self.create_setting_row(
            content_frame,
            "User-Agent:",
            "user_agent",
            "HTTP 요청 시 사용할 User-Agent",
            "entry",
            {"default": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        )
        
    def setup_advanced_settings(self, parent):
        """고급 설정 섹션"""
        shadow_frame, card_frame = self.ui_components.create_card_frame(
            parent, title="⚙️ 고급 설정"
        )
        shadow_frame.pack(fill="x", pady=(0, 20))
        
        content_frame = tk.Frame(card_frame, bg="#ffffff")
        content_frame.pack(fill="x", padx=20, pady=15)
        
        # SSL 검증 건너뛰기
        self.create_setting_row(
            content_frame,
            "SSL 검증 건너뛰기:",
            "skip_ssl_verify",
            "SSL 인증서 검증을 건너뜁니다 (비권장)",
            "checkbox"
        )
        
        # 상세 로그
        self.create_setting_row(
            content_frame,
            "상세 로그 출력:",
            "verbose_logging",
            "더 자세한 로그를 출력합니다",
            "checkbox"
        )
        
        # 결과 자동 저장
        self.create_setting_row(
            content_frame,
            "결과 자동 저장:",
            "auto_save_results",
            "검사 완료 후 자동으로 결과를 저장합니다",
            "checkbox",
            {"default": True}
        )
        
    def create_setting_row(self, parent, label_text, setting_key, description, widget_type, options=None):
        """설정 행 생성"""
        if options is None:
            options = {}
            
        # 행 프레임
        row_frame = tk.Frame(parent, bg="#ffffff")
        row_frame.pack(fill="x", pady=8)
        
        # 라벨 프레임
        label_frame = tk.Frame(row_frame, bg="#ffffff", width=150)
        label_frame.pack(side="left", fill="y")
        label_frame.pack_propagate(False)
        
        # 라벨
        label = tk.Label(
            label_frame,
            text=label_text,
            font=("Arial", 10, "bold"),
            bg="#ffffff",
            fg=self.ui_components.colors["secondary"],
            anchor="w"
        )
        label.pack(anchor="w")
        
        # 위젯 프레임
        widget_frame = tk.Frame(row_frame, bg="#ffffff")
        widget_frame.pack(side="left", fill="x", expand=True, padx=(10, 0))
        
        # 위젯 생성
        widget = None
        current_value = self.settings.get(setting_key, options.get("default", ""))
        
        if widget_type == "entry":
            widget = tk.Entry(
                widget_frame,
                font=("Arial", 10),
                relief="solid",
                bd=1
            )
            widget.pack(fill="x")
            if current_value:
                widget.insert(0, str(current_value))
                
        elif widget_type == "spinbox":
            widget = tk.Spinbox(
                widget_frame,
                font=("Arial", 10),
                relief="solid",
                bd=1,
                **{k: v for k, v in options.items() if k != "default"}
            )
            widget.pack(fill="x")
            if current_value:
                widget.delete(0, tk.END)
                widget.insert(0, str(current_value))
                
        elif widget_type == "checkbox":
            var = tk.BooleanVar(value=bool(current_value))
            widget = tk.Checkbutton(
                widget_frame,
                variable=var,
                bg="#ffffff",
                activebackground="#ffffff"
            )
            widget.pack(anchor="w")
            widget.var = var  # 변수 참조 유지
            
        # 설명 라벨
        if description:
            desc_label = tk.Label(
                widget_frame,
                text=description,
                font=("Arial", 8),
                bg="#ffffff",
                fg=self.ui_components.colors["dark"],
                anchor="w"
            )
            desc_label.pack(anchor="w", pady=(2, 0))
            
        # 위젯을 설정 딕셔너리에 저장
        if not hasattr(self, 'setting_widgets'):
            self.setting_widgets = {}
        self.setting_widgets[setting_key] = (widget, widget_type)
        
    def setup_actions(self, parent):
        """액션 버튼 섹션"""
        shadow_frame, card_frame = self.ui_components.create_card_frame(
            parent, title="💾 설정 관리"
        )
        shadow_frame.pack(fill="x", pady=(0, 20))
        
        content_frame = tk.Frame(card_frame, bg="#ffffff")
        content_frame.pack(fill="x", padx=20, pady=15)
        
        # 버튼 프레임
        button_frame = tk.Frame(content_frame, bg="#ffffff")
        button_frame.pack(fill="x")
        
        # 저장 버튼
        save_btn = self.ui_components.create_modern_button(
            button_frame,
            text="💾 설정 저장",
            command=self.save_settings,
            style="success"
        )
        save_btn.pack(side="left", padx=(0, 10))
        
        # 초기화 버튼
        reset_btn = self.ui_components.create_modern_button(
            button_frame,
            text="🔄 기본값으로 초기화",
            command=self.reset_settings,
            style="warning"
        )
        reset_btn.pack(side="left", padx=(0, 10))
        
        # 설정 내보내기 버튼
        export_btn = self.ui_components.create_modern_button(
            button_frame,
            text="📤 설정 내보내기",
            command=self.export_settings,
            style="primary"
        )
        export_btn.pack(side="left", padx=(0, 10))
        
        # 설정 가져오기 버튼
        import_btn = self.ui_components.create_modern_button(
            button_frame,
            text="📥 설정 가져오기", 
            command=self.import_settings,
            style="primary"
        )
        import_btn.pack(side="left")
        
    def save_settings(self):
        """설정 저장"""
        try:
            # 위젯에서 값 수집
            new_settings = {}
            
            for setting_key, (widget, widget_type) in self.setting_widgets.items():
                if widget_type == "entry":
                    new_settings[setting_key] = widget.get()
                elif widget_type == "spinbox":
                    new_settings[setting_key] = int(widget.get()) if widget.get().isdigit() else 0
                elif widget_type == "checkbox":
                    new_settings[setting_key] = widget.var.get()
                    
            # 기존 설정과 병합
            self.settings.update(new_settings)
            
            # 저장
            if save_user_info(self.settings):
                messagebox.showinfo("성공", "설정이 저장되었습니다.")
            else:
                messagebox.showerror("오류", "설정 저장에 실패했습니다.")
                
        except Exception as e:
            messagebox.showerror("오류", f"설정 저장 중 오류가 발생했습니다: {e}")
            
    def reset_settings(self):
        """설정 초기화"""
        if messagebox.askyesno("확인", "모든 설정을 기본값으로 초기화하시겠습니까?"):
            # 기본 설정
            default_settings = {
                "web_url": "",
                "login_url": "",
                "timeout": 10,
                "concurrent_requests": 5,
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "skip_ssl_verify": False,
                "verbose_logging": False,
                "auto_save_results": True
            }
            
            self.settings = default_settings
            
            # UI 업데이트
            self.update_widgets_from_settings()
            
            # 저장
            if save_user_info(self.settings):
                messagebox.showinfo("성공", "설정이 초기화되었습니다.")
                
    def update_widgets_from_settings(self):
        """설정값으로 위젯 업데이트"""
        for setting_key, (widget, widget_type) in self.setting_widgets.items():
            value = self.settings.get(setting_key, "")
            
            if widget_type == "entry":
                widget.delete(0, tk.END)
                widget.insert(0, str(value))
            elif widget_type == "spinbox":
                widget.delete(0, tk.END)
                widget.insert(0, str(value))
            elif widget_type == "checkbox":
                widget.var.set(bool(value))
                
    def export_settings(self):
        """설정 내보내기"""
        try:
            file_path = filedialog.asksaveasfilename(
                title="설정 파일 저장",
                defaultextension=".json",
                filetypes=[("JSON 파일", "*.json"), ("모든 파일", "*.*")]
            )
            
            if file_path:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(self.settings, f, ensure_ascii=False, indent=4)
                messagebox.showinfo("성공", f"설정이 {file_path}에 저장되었습니다.")
                
        except Exception as e:
            messagebox.showerror("오류", f"설정 내보내기 실패: {e}")
            
    def import_settings(self):
        """설정 가져오기"""
        try:
            file_path = filedialog.askopenfilename(
                title="설정 파일 선택",
                filetypes=[("JSON 파일", "*.json"), ("모든 파일", "*.*")]
            )
            
            if file_path:
                with open(file_path, "r", encoding="utf-8") as f:
                    imported_settings = json.load(f)
                    
                self.settings.update(imported_settings)
                self.update_widgets_from_settings()
                
                messagebox.showinfo("성공", "설정을 가져왔습니다.")
                
        except Exception as e:
            messagebox.showerror("오류", f"설정 가져오기 실패: {e}")