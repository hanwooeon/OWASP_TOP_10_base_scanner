"""
UI 컴포넌트 모듈
재사용 가능한 UI 요소들을 정의
"""
import tkinter as tk
from tkinter import ttk

# CustomTkinter 안전 import
try:
    import customtkinter as ctk
    CTK_AVAILABLE = True
except ImportError:
    CTK_AVAILABLE = False

class UIComponents:
    """재사용 가능한 UI 컴포넌트 클래스"""
    
    def __init__(self):
        self.colors = {
            "primary": "#3498db",
            "secondary": "#2c3e50", 
            "success": "#27ae60",
            "warning": "#f39c12",
            "danger": "#e74c3c",
            "light": "#ecf0f1",
            "dark": "#34495e",
            "white": "#ffffff",
            "background": "#f8f9fa"
        }
        
    def create_modern_button(self, parent, text, command, style="primary", **kwargs):
        """현대적 스타일 버튼 생성"""
        if CTK_AVAILABLE:
            try:
                color = self.colors.get(style, self.colors["primary"])
                return ctk.CTkButton(
                    parent,
                    text=text,
                    command=command,
                    corner_radius=8,
                    height=40,
                    font=("Arial", 12, "bold"),
                    fg_color=color,
                    hover_color=self._darken_color(color),
                    **kwargs
                )
            except Exception:
                pass
                
        # Tkinter 폴백
        color = self.colors.get(style, self.colors["primary"])
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=color,
            fg="white",
            font=("Arial", 11, "bold"),
            relief="flat",
            padx=20,
            pady=10,
            cursor="hand2",
            activebackground=self._darken_color(color),
            **kwargs
        )
        
    def create_nav_button(self, parent, text, command):
        """네비게이션 버튼 생성"""
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=self.colors["light"],
            fg=self.colors["secondary"],
            font=("Arial", 10, "bold"),
            relief="flat",
            padx=15,
            pady=8,
            cursor="hand2",
            activebackground=self.colors["primary"],
            activeforeground="white"
        )
        
    def create_card_frame(self, parent, title=None, **kwargs):
        """카드 스타일 프레임 생성"""
        # 외부 프레임 (그림자 효과)
        shadow_frame = tk.Frame(parent, bg="#d0d0d0")
        
        # 메인 카드 프레임
        card_frame = tk.Frame(
            shadow_frame,
            bg=self.colors["white"],
            relief="flat",
            bd=0,
            **kwargs
        )
        card_frame.pack(fill="both", expand=True, padx=2, pady=2)
        
        if title:
            title_frame = tk.Frame(card_frame, bg=self.colors["light"], height=40)
            title_frame.pack(fill="x")
            title_frame.pack_propagate(False)
            
            title_label = tk.Label(
                title_frame,
                text=title,
                font=("Arial", 12, "bold"),
                bg=self.colors["light"],
                fg=self.colors["secondary"]
            )
            title_label.pack(pady=10)
            
        return shadow_frame, card_frame
        
            
    def create_status_indicator(self, parent, status="idle"):
        """상태 표시기 생성"""
        colors = {
            "idle": self.colors["light"],
            "running": self.colors["warning"], 
            "success": self.colors["success"],
            "error": self.colors["danger"]
        }
        
        indicator = tk.Frame(
            parent,
            bg=colors.get(status, colors["idle"]),
            width=12,
            height=12
        )
        indicator.pack_propagate(False)
        
        return indicator
        
    def create_log_display(self, parent):
        """로그 표시 영역 생성"""
        # 로그 프레임
        log_frame = tk.Frame(parent, bg=self.colors["white"])
        
        # 스크롤바가 있는 텍스트 위젯
        scrollbar = ttk.Scrollbar(log_frame)
        scrollbar.pack(side="right", fill="y")
        
        log_text = tk.Text(
            log_frame,
            bg="#1e1e1e",
            fg="#ffffff",
            font=("Consolas", 10),
            wrap="word",
            yscrollcommand=scrollbar.set,
            state="disabled"
        )
        log_text.pack(side="left", fill="both", expand=True)
        
        scrollbar.config(command=log_text.yview)
        
        return log_frame, log_text
        
    def add_log_message(self, log_text, message, level="info"):
        """로그 메시지 추가"""
        log_text.config(state="normal")
        
        # 타임스탬프
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        # 레벨별 색상
        colors = {
            "info": "#ffffff",
            "warning": "#f39c12", 
            "error": "#e74c3c",
            "success": "#27ae60"
        }
        
        # 메시지 추가
        log_text.insert("end", f"[{timestamp}] ", "timestamp")
        log_text.insert("end", f"{message}\n", level)
        
        # 태그 설정
        log_text.tag_config("timestamp", foreground="#888888")
        log_text.tag_config(level, foreground=colors.get(level, "#ffffff"))
        
        # 자동 스크롤
        log_text.see("end")
        log_text.config(state="disabled")
        
    def _darken_color(self, color_hex, factor=0.8):
        """색상을 어둡게 만드는 함수"""
        if color_hex.startswith('#'):
            color_hex = color_hex[1:]
            
        try:
            r = int(color_hex[0:2], 16)
            g = int(color_hex[2:4], 16) 
            b = int(color_hex[4:6], 16)
            
            r = int(r * factor)
            g = int(g * factor)
            b = int(b * factor)
            
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            return color_hex