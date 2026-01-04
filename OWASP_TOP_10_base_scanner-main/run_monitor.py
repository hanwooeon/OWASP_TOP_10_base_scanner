#!/usr/bin/env python3
"""
보안 취약점 검사 도구 GUI 실행 스크립트
"""
import sys
import os
import tkinter as tk
from tkinter import messagebox

# 현재 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'gui'))

# 세그멘테이션 오류 방지를 위한 환경 설정
os.environ['TK_SILENCE_DEPRECATION'] = '1'

def check_configuration():
    """설정 파일 확인"""
    config_path = os.path.join(current_dir, "etc", "user_info.json")
    if not os.path.exists(config_path):
        print("⚠️ 설정 파일이 없습니다. 기본 설정으로 시작합니다.")
        # 기본 설정 파일 생성은 config_manager가 자동으로 처리
    return True

def main():
    """메인 함수"""
    try:
        print("=" * 60)
        print("🛡️  보안 취약점 검사 도구 GUI v2.0")
        print("📂 실행 위치:", current_dir)
        print("=" * 60)

        # 설정 파일 확인
        check_configuration()

        # GUI 모듈 import
        print("📦 GUI 모듈 로드 중...")
        from gui.main_window import MainWindow

        # Tkinter 루트 윈도우 생성
        print("🪟 윈도우 생성 중...")
        root = tk.Tk()
        root.title("🛡️ 보안 취약점 검사 도구 v2.0")
        root.geometry("900x700")
        root.minsize(800, 600)

        # 윈도우 중앙 배치
        root.update_idletasks()
        width = root.winfo_width()
        height = root.winfo_height()
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry(f'{width}x{height}+{x}+{y}')

        # 윈도우 닫기 이벤트 처리
        def on_closing():
            if messagebox.askokcancel("종료", "프로그램을 종료하시겠습니까?"):
                print("👋 프로그램을 종료합니다.")
                root.destroy()

        root.protocol("WM_DELETE_WINDOW", on_closing)

        # MainWindow 초기화
        print("🔧 GUI 초기화 중...")
        app = MainWindow(root)

        # 메인 UI 설정
        print("🎨 UI 구성 중...")
        app.setup_main_ui()

        print("✅ GUI 초기화 완료")
        print("=" * 60)
        print("🚀 GUI를 시작합니다...")

        # 메인 루프 실행
        root.mainloop()

    except ImportError as e:
        print(f"❌ 모듈 import 실패: {e}")
        print("\n💡 해결 방법:")
        print("1. 프로젝트 루트 디렉토리에서 실행하고 있는지 확인")
        print("2. gui 폴더가 존재하는지 확인")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    except Exception as e:
        print(f"❌ GUI 실행 실패: {e}")
        import traceback
        traceback.print_exc()

        # 에러 메시지 박스 표시
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(
                "GUI 실행 오류",
                f"GUI를 시작할 수 없습니다.\n\n오류: {e}\n\n콘솔을 확인하세요."
            )
        except:
            pass

        sys.exit(1)

if __name__ == "__main__":
    main()