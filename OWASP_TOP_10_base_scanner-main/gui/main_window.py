"""
메인 윈도우 관리 모듈
GUI의 기본 구조와 탭 관리를 담당
"""
import tkinter as tk
try:
    from .views import SettingsManager, DastView, AddView, ResultsView
except ImportError:
    from views import SettingsManager, DastView, AddView, ResultsView

class MainWindow:
    """메인 윈도우 클래스 - GUI의 기본 구조 관리"""
    
    def __init__(self, root):
        self.root = root
        self.setup_window()

        # 뷰 초기화
        self.settings_manager = SettingsManager(self)
        self.dast_view = DastView(self)
        self.add_view = AddView(self)
        self.results_view = ResultsView(self)

        print("✅ 모든 뷰 초기화 완료")

        # 현재 뷰 상태
        self.current_view = "main"
        
    def setup_window(self):
        """윈도우 기본 설정"""
        self.root.title("보안 취약점 검사 도구")
        self.root.geometry("950x700")
        self.root.configure(bg="#f0f0f0")
        
        # 윈도우 중앙 배치
        self.center_window()
        
        # 최소 크기 설정
        self.root.minsize(1200, 800)
        
    def center_window(self):
        """윈도우를 화면 중앙에 배치"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def setup_main_ui(self):
        """메인 UI 구성"""
        # 메인 컨테이너
        self.main_container = tk.Frame(self.root, bg="#f0f0f0")
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # 콘텐츠 영역
        self.setup_content_area()
            
    def setup_content_area(self):
        """콘텐츠 영역 설정"""
        self.content_frame = tk.Frame(self.main_container, bg="#ffffff", relief="solid", bd=1)
        self.content_frame.pack(fill="both", expand=True)

        # 기본적으로 DAST 뷰 표시
        self.switch_view("dast")
        
    def switch_view(self, view_name):
        """뷰 전환"""
        try:
            print(f"🔄 뷰 전환 시작: {view_name}")

            # 이전 뷰 정리
            for widget in self.content_frame.winfo_children():
                widget.destroy()

            # 새 뷰 로드
            self.current_view = view_name

            if view_name == "dast":
                self.dast_view.setup_view(self.content_frame)
            elif view_name == "results":
                self.results_view.setup_view(self.content_frame)
            elif view_name == "settings":
                self.settings_manager.setup_view(self.content_frame)
            else:
                self.setup_error_view("알 수 없는 뷰", f"'{view_name}' 뷰를 찾을 수 없습니다.")

            print(f"✅ 뷰 전환 완료: {view_name}")

        except Exception as e:
            print(f"❌ 뷰 전환 실패: {e}")
            import traceback
            traceback.print_exc()
            self.setup_error_view("뷰 전환 오류", str(e))
        
    def setup_error_view(self, error_type, error_message):
        """에러 뷰 설정"""
        try:
            error_frame = tk.Frame(self.content_frame, bg="white")
            error_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            # 에러 제목
            title_label = tk.Label(
                error_frame,
                text=f"{error_type} 오류",
                font=("Arial", 18, "bold"),
                fg="#e74c3c",
                bg="white"
            )
            title_label.pack(pady=(20, 10))

            # 에러 메시지
            message_label = tk.Label(
                error_frame,
                text=error_message,
                font=("Arial", 12),
                fg="#2c3e50",
                bg="white",
                wraplength=600,
                justify="center"
            )
            message_label.pack(pady=10)

            # 다시 시도 버튼
            retry_button = tk.Button(
                error_frame,
                text="검사 화면으로 돌아가기",
                command=lambda: self.switch_view("dast"),
                bg="#3498db",
                fg="white",
                font=("Arial", 11, "bold"),
                relief="flat",
                padx=20,
                pady=10,
                cursor="hand2"
            )
            retry_button.pack(pady=20)
            
        except Exception as e:
            print(f"❌ 에러 뷰 설정 실패: {e}")