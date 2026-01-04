"""
검사 결과 뷰
저장된 검사 결과 목록 및 상세 정보 표시
"""
import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import webbrowser
from datetime import datetime

try:
    from ..controllers import ResultsController
    from ..utils.format_utils import (
        format_csrf_details,
        format_common_details,
        format_library_details,
        get_vulnerability_description
    )
except ImportError:
    from controllers import ResultsController
    from utils.format_utils import (
        format_csrf_details,
        format_common_details,
        format_library_details,
        get_vulnerability_description
    )

# report_generator는 별도로 import (gui 폴더에 있음)
try:
    from ..report_generator import generate_report_from_file
except ImportError:
    import sys
    gui_dir = os.path.join(os.path.dirname(__file__), '..')
    sys.path.insert(0, gui_dir)
    from report_generator import generate_report_from_file


class ResultsView:
    """검사 결과 뷰 클래스"""

    def __init__(self, main_window):
        self.main_window = main_window
        self.controller = ResultsController()

        # 현재 뷰 상태 ("list" 또는 "detail")
        self.current_mode = "list"
        self.current_result_data = None
        self.vulnerability_data = []
        self.current_filter = "All"  # 현재 선택된 필터

    def setup_view(self, parent):
        """뷰 설정"""
        self.parent = parent

        # 메인 컨테이너
        self.main_container = tk.Frame(parent, bg="white")
        self.main_container.pack(fill="both", expand=True)

        # 기본적으로 목록 뷰 표시
        self.show_list_view()

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
                fg="#3498db" if view == "results" else "#7f8c8d",
                font=("Arial", 12, "bold"),
                relief="flat",
                bd=0,
                cursor="hand2",
                activebackground="white",
                activeforeground="#2980b9"
            )
            btn.pack(side="left", padx=15, pady=10, expand=True, fill="both")

    def show_list_view(self):
        """결과 목록 뷰 표시"""
        try:
            self.current_mode = "list"

            # 대량의 취약점 데이터 정리 (메모리 해제)
            if hasattr(self, 'vulnerability_data'):
                self.vulnerability_data = []

            # 이벤트 바인딩 먼저 해제 (세그먼트 오류 방지)
            if hasattr(self, 'vuln_tree') and self.vuln_tree:
                try:
                    self.vuln_tree.unbind("<<TreeviewSelect>>")
                except:
                    pass

            if hasattr(self, 'results_tree') and self.results_tree:
                try:
                    self.results_tree.unbind("<Double-Button-1>")
                except:
                    pass

            if hasattr(self, 'filter_combo') and self.filter_combo:
                try:
                    self.filter_combo.unbind("<<ComboboxSelected>>")
                except:
                    pass

            # update_idletasks를 먼저 호출하여 보류 중인 이벤트 처리
            self.main_container.update_idletasks()

            # Treeview 항목 삭제 (이벤트 해제 후)
            if hasattr(self, 'vuln_tree') and self.vuln_tree:
                try:
                    for item in self.vuln_tree.get_children():
                        self.vuln_tree.delete(item)
                except:
                    pass

            if hasattr(self, 'results_tree') and self.results_tree:
                try:
                    for item in self.results_tree.get_children():
                        self.results_tree.delete(item)
                except:
                    pass

            # 한 번 더 이벤트 처리
            self.main_container.update_idletasks()

            # 기존 위젯 안전하게 제거
            children = list(self.main_container.winfo_children())
            for widget in children:
                try:
                    widget.pack_forget()
                except:
                    pass

            # 이벤트 처리 대기
            self.main_container.update()

            for widget in children:
                try:
                    widget.destroy()
                except:
                    pass

            # 참조 초기화
            self.vuln_tree = None
            self.detail_text = None
            self.results_tree = None
            self.filter_combo = None
            self.filter_var = None

            # 가비지 컬렉션 강제 실행
            import gc
            gc.collect()

        except Exception as e:
            print(f"❌ show_list_view 초기화 오류: {e}")
            import traceback
            traceback.print_exc()

        # 컨테이너
        list_container = tk.Frame(self.main_container, bg="white")
        list_container.pack(fill="both", expand=True, padx=20, pady=20)

        # 네비게이션 버튼 추가
        self.setup_navigation_buttons(list_container)

        # 제목
        header_frame = tk.Frame(list_container, bg="white")
        header_frame.pack(fill="x", pady=(0, 20))

        tk.Label(
            header_frame,
            text="검사 결과 목록",
            font=("Arial", 18, "bold"),
            bg="white",
            fg="#2c3e50"
        ).pack(side="left")

        # 새로고침 버튼
        refresh_btn = tk.Button(
            header_frame,
            text="🔄 새로고침",
            command=self.refresh_list,
            bg="#3498db",
            fg="white",
            font=("Arial", 10, "bold"),
            relief="flat",
            padx=15,
            pady=5
        )
        refresh_btn.pack(side="right")

        # 테이블 프레임
        table_frame = tk.Frame(list_container, bg="white")
        table_frame.pack(fill="both", expand=True)

        # Treeview 생성
        columns = ("timestamp", "target")
        self.results_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)

        # 컬럼 설정
        self.results_tree.heading("timestamp", text="검사 시간")
        self.results_tree.heading("target", text="검사 대상")

        # 컬럼 너비 설정
        self.results_tree.column("timestamp", width=200, minwidth=150)
        self.results_tree.column("target", width=400, minwidth=200)

        # 스크롤바
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=scrollbar.set)

        # 배치
        self.results_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 더블클릭 이벤트
        self.results_tree.bind("<Double-Button-1>", self.on_result_double_click)

        # 안내 라벨
        info_label = tk.Label(
            list_container,
            text="결과를 더블클릭하면 상세 정보를 볼 수 있습니다",
            font=("Arial", 10),
            bg="white",
            fg="#7f8c8d"
        )
        info_label.pack(pady=(10, 0))

        # 결과 로드
        self.load_results()

    def show_detail_view(self, result_data):
        """상세 결과 뷰 표시 (dast_view와 유사)"""
        try:
            self.current_mode = "detail"
            self.current_result_data = result_data

            # 기존 위젯 안전하게 제거 (메모리 누수 방지)
            # 이벤트 바인딩 해제 (중요: 세그먼트 오류 방지)
            if hasattr(self, 'vuln_tree') and self.vuln_tree:
                try:
                    self.vuln_tree.unbind("<<TreeviewSelect>>")
                    # Treeview 항목 먼저 삭제 (메모리 해제)
                    for item in self.vuln_tree.get_children():
                        self.vuln_tree.delete(item)
                except:
                    pass

            if hasattr(self, 'results_tree') and self.results_tree:
                try:
                    # 기존 results_tree 항목도 삭제
                    for item in self.results_tree.get_children():
                        self.results_tree.delete(item)
                except:
                    pass

            # 필터 콤보박스 정리
            if hasattr(self, 'filter_combo') and self.filter_combo:
                try:
                    self.filter_combo.unbind("<<ComboboxSelected>>")
                except:
                    pass

            # 먼저 모든 위젯의 참조를 리스트로 복사
            children = list(self.main_container.winfo_children())

            # pack_forget()을 먼저 모두 처리
            for widget in children:
                try:
                    widget.pack_forget()
                except:
                    pass

            # 이벤트 처리 - 여러 번 처리하여 확실하게 정리
            self.main_container.update_idletasks()
            self.main_container.update()

            # 그 다음 destroy() 처리
            for widget in children:
                try:
                    widget.destroy()
                except:
                    pass

            # 메모리 정리 - 여러 번 처리
            self.main_container.update_idletasks()
            self.main_container.update()

            # 참조 초기화 (메모리 누수 방지)
            if hasattr(self, 'vuln_tree'):
                self.vuln_tree = None
            if hasattr(self, 'detail_text'):
                self.detail_text = None
            if hasattr(self, 'results_tree'):
                self.results_tree = None
            if hasattr(self, 'filter_combo'):
                self.filter_combo = None
            if hasattr(self, 'filter_var'):
                self.filter_var = None

            # 가비지 컬렉션 강제 실행
            import gc
            gc.collect()

            # Tk 이벤트 루프가 정리를 완료할 시간을 주기 위해 after 사용
            self.main_container.after(100, lambda: self._build_detail_view(result_data))

        except Exception as e:
            print(f"❌ show_detail_view 초기화 오류: {e}")
            import traceback
            traceback.print_exc()
            return

    def _build_detail_view(self, result_data):
        """실제 상세 뷰 구축 (cleanup 이후에 호출)"""
        try:
            # 뷰 전환 중인지 확인 (세그폴트 방지)
            if not hasattr(self, 'main_container') or not self.main_container.winfo_exists():
                print("⚠️ 메인 컨테이너가 존재하지 않습니다.")
                return

            # 컨테이너
            detail_container = tk.Frame(self.main_container, bg="white")
            detail_container.pack(fill="both", expand=True, padx=20, pady=20)

            # 헤더
            header_frame = tk.Frame(detail_container, bg="white")
            header_frame.pack(fill="x", pady=(0, 20))

            # 뒤로가기 버튼
            back_btn = tk.Button(
                header_frame,
                text="← 목록으로",
                command=self.show_list_view,
                bg="#95a5a6",
                fg="white",
                font=("Arial", 10, "bold"),
                relief="flat",
                padx=15,
                pady=5
            )
            back_btn.pack(side="left")

            # 제목 (안전하게 생성)
            timestamp = result_data.get("summary", {}).get("scan_time", "")
            title_label = tk.Label(
                header_frame,
                text=f"검사 결과 - {timestamp}",
                font=("Arial", 16, "bold"),
                bg="white",
                fg="#2c3e50"
            )
            title_label.pack(side="left", padx=(20, 0))

            # 보고서 생성 버튼 (오른쪽 끝)
            report_btn = tk.Button(
                header_frame,
                text="📄 보고서 생성",
                command=self.generate_report,
                bg="#27ae60",
                fg="white",
                font=("Arial", 10, "bold"),
                relief="flat",
                padx=15,
                pady=5
            )
            report_btn.pack(side="right")

            # 메인 컨텐츠 프레임 (취약점 테이블 + 상세 정보)
            content_frame = tk.Frame(detail_container, bg="white")
            content_frame.pack(fill="both", expand=True)

            # Grid 시스템으로 480:360 비율 유지하며 자동 크기 조절
            content_frame.grid_columnconfigure(0, weight=480, minsize=480)  # 최소 480px, 480 비율
            content_frame.grid_columnconfigure(1, weight=360, minsize=360)  # 최소 360px, 360 비율
            content_frame.grid_rowconfigure(0, weight=1)

            # 왼쪽: 취약점 테이블 섹션
            left_frame = tk.Frame(content_frame, bg="white")
            left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
            self.setup_vulnerability_table(left_frame)

            # 오른쪽: 상세 정보 패널
            right_frame = tk.Frame(content_frame, bg="white")
            right_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 25))
            self.setup_detail_panel(right_frame)

            # 취약점 데이터 로드
            self.load_vulnerabilities()

        except Exception as e:
            print(f"❌ _build_detail_view 오류: {e}")
            import traceback
            traceback.print_exc()

    def setup_vulnerability_table(self, parent):
        """취약점 테이블 설정 (dast_view와 동일)"""
        table_frame = tk.Frame(parent, bg="white")
        table_frame.pack(fill="both", expand=True, padx=(0, 5))

        # 헤더 프레임 (필터 + 제목)
        header_frame = tk.Frame(table_frame, bg="white")
        header_frame.pack(fill="x", pady=(0, 10))

        # 필터 프레임 (왼쪽)
        filter_frame = tk.Frame(header_frame, bg="white")
        filter_frame.pack(side="left")

        # 필터 라벨
        tk.Label(
            filter_frame,
            text="필터:",
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
        tk.Label(
            header_frame,
            text="📋 발견된 취약점",
            font=("Arial", 14, "bold"),
            bg="white",
            fg="#333"
        ).pack(side="left", padx=(180, 0))

        # 스크롤바를 위한 컨테이너 프레임 생성 (grid 사용)
        tree_container = tk.Frame(table_frame, bg="white")
        tree_container.pack(fill="both", expand=True)

        # grid 설정
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)

        # Treeview 생성
        columns = ("test_id", "test_name", "risk_level", "location")
        self.vuln_tree = ttk.Treeview(tree_container, columns=columns, show="headings", height=20)

        # 컬럼 설정
        self.vuln_tree.heading("test_id", text="테스트 ID")
        self.vuln_tree.heading("test_name", text="취약점 명")
        self.vuln_tree.heading("risk_level", text="위험도")
        self.vuln_tree.heading("location", text="경로")

        # 컬럼 너비 설정 (취약점명 축소, 경로 확장)
        # stretch=False로 설정하여 가로 스크롤 활성화
        self.vuln_tree.column("test_id", width=90, minwidth=80, stretch=False)
        self.vuln_tree.column("test_name", width=180, minwidth=150, stretch=False)
        self.vuln_tree.column("risk_level", width=90, minwidth=80, stretch=False)
        self.vuln_tree.column("location", width=700, minwidth=600, stretch=False)

        # 세로 스크롤바
        v_scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.vuln_tree.yview)

        # 가로 스크롤바 추가
        h_scrollbar = ttk.Scrollbar(tree_container, orient="horizontal", command=self.vuln_tree.xview)

        # Treeview에 스크롤바 연결
        self.vuln_tree.configure(
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set
        )

        # 배치 (grid 레이아웃 사용)
        self.vuln_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")

        # 클릭 이벤트
        self.vuln_tree.bind("<<TreeviewSelect>>", self.on_vulnerability_select)

        # 위험도별 색상 태그
        self.vuln_tree.tag_configure("CRITICAL", foreground="#c0392b")
        self.vuln_tree.tag_configure("HIGH", foreground="#e74c3c")
        self.vuln_tree.tag_configure("MEDIUM", foreground="#f39c12")
        self.vuln_tree.tag_configure("LOW", foreground="#27ae60")
        self.vuln_tree.tag_configure("INFO", foreground="#3498db")

    def setup_detail_panel(self, parent):
        """상세 정보 패널 설정"""
        panel_frame = tk.Frame(parent, bg="#f8f9fa", relief="solid", bd=1)
        panel_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # 제목
        tk.Label(
            panel_frame,
            text="📄 상세 정보",
            font=("Arial", 12, "bold"),
            bg="#f8f9fa",
            fg="#2c3e50"
        ).pack(pady=(15, 10))

        # 스크롤 가능한 텍스트 영역
        text_frame = tk.Frame(panel_frame, bg="#f8f9fa")
        text_frame.pack(fill="both", expand=True, padx=5, pady=5)

        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side="right", fill="y", padx=(0, 5))

        self.detail_text = tk.Text(
            text_frame,
            wrap="word",
            font=("Arial", 10),
            bg="white",
            relief="flat",
            padx=10,
            pady=10,
            yscrollcommand=scrollbar.set
        )
        self.detail_text.pack(side="left", fill="both", expand=True, padx=(5, 0))
        scrollbar.config(command=self.detail_text.yview)

        # 기본 메시지
        self.update_detail_text("취약점을 선택하면 상세 정보가 표시됩니다.")

    def load_results(self):
        """결과 목록 로드"""
        # 기존 항목 제거
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)

        # 결과 로드
        results = self.controller.get_results_list()

        if not results:
            # 결과가 없을 때
            self.results_tree.insert("", "end", values=("결과가 없습니다", ""))
            return

        # 결과 삽입
        for result in results:
            self.results_tree.insert(
                "",
                "end",
                values=(result["timestamp"], result["target"]),
                tags=(result["file_path"],)  # file_path를 태그로 저장
            )

        print(f"✅ {len(results)}개 결과 표시 완료")

    def load_vulnerabilities(self):
        """취약점 목록 로드 (배치 처리로 메모리 오류 방지)"""
        try:
            # vuln_tree가 존재하는지 확인
            if not hasattr(self, 'vuln_tree') or not self.vuln_tree:
                print("⚠️ vuln_tree가 초기화되지 않았습니다.")
                return

            # 기존 항목 안전하게 제거
            try:
                items = self.vuln_tree.get_children()
                for item in items:
                    self.vuln_tree.delete(item)
                # 삭제 후 이벤트 처리
                self.vuln_tree.update_idletasks()
            except (tk.TclError, AttributeError) as e:
                print(f"⚠️ Treeview 항목 삭제 오류: {e}")
                return

            # 취약점 추출 - 안전하게 처리
            try:
                self.vulnerability_data = self.controller.get_vulnerability_list(self.current_result_data)
            except Exception as e:
                print(f"❌ 취약점 데이터 추출 오류: {e}")
                self.vuln_tree.insert("", "end", values=("데이터 로드 실패", str(e), "", ""))
                return

            # 데이터 유효성 검사
            if not self.vulnerability_data or not isinstance(self.vulnerability_data, list):
                self.vuln_tree.insert("", "end", values=("취약점이 발견되지 않았습니다", "", "", ""))
                return

            total_count = len(self.vulnerability_data)
            print(f"📊 총 {total_count}개 취약점 발견")

            # 메모리 보호: 최대 개수 제한 (더 보수적으로 설정)
            MAX_DISPLAY_ITEMS = 1000  # 2000 -> 1000으로 감소 (세그폴트 방지)
            if total_count > MAX_DISPLAY_ITEMS:
                print(f"⚠️ 경고: 취약점이 {total_count}개로 너무 많습니다.")
                print(f"⚠️ 메모리 보호를 위해 처음 {MAX_DISPLAY_ITEMS}개만 표시합니다.")
                print(f"⚠️ 전체 데이터는 HTML 보고서 생성으로 확인하세요.")
                self.vulnerability_data = self.vulnerability_data[:MAX_DISPLAY_ITEMS]

                # 사용자에게 경고 표시 (after_idle을 사용하여 비동기 처리)
                self.main_container.after_idle(lambda: messagebox.showwarning(
                    "데이터 크기 경고",
                    f"취약점이 {total_count}개로 매우 많습니다.\n\n"
                    f"메모리 보호를 위해 처음 {MAX_DISPLAY_ITEMS}개만 표시합니다.\n\n"
                    f"전체 데이터를 보려면 '보고서 생성' 버튼을 사용하세요."
                ))

            # 대량 데이터 처리: 배치로 나눠서 삽입 (세그멘테이션 오류 방지)
            BATCH_SIZE = 50  # 배치 크기 축소 (100 -> 50)

            # 필터 적용된 데이터 가져오기
            display_data = self.get_filtered_vulnerabilities()

            print(f"📊 필터 적용 후 {len(display_data)}개 취약점 표시 예정")

            # 컬럼 너비를 한 번만 계산 (성능 최적화)
            truncate_lengths = {
                "test_id": self._get_dynamic_truncate_length("test_id"),
                "test_name": self._get_dynamic_truncate_length("test_name"),
                "risk_level": self._get_dynamic_truncate_length("risk_level"),
                "location": self._get_dynamic_truncate_length("location")
            }

            # 배치 단위로 삽입
            for batch_start in range(0, len(display_data), BATCH_SIZE):
                # vuln_tree가 여전히 유효한지 확인 (뷰 전환 시 None이 될 수 있음)
                if not hasattr(self, 'vuln_tree') or not self.vuln_tree:
                    print("⚠️ 데이터 로드 중 뷰가 전환되었습니다.")
                    return

                batch_end = min(batch_start + BATCH_SIZE, len(display_data))
                batch = display_data[batch_start:batch_end]

                # 배치 처리 - 한 번에 하나씩 삽입 (메모리 안정성 향상)
                try:
                    for vuln in batch:
                        # 데이터 유효성 검사
                        if not isinstance(vuln, dict):
                            continue

                        risk_level = vuln.get("risk_level", "")
                        test_id = vuln.get("test_id", "")
                        test_name = vuln.get("test_name", "")
                        location = vuln.get("location", "")

                        # 미리 계산된 길이로 텍스트 절단 (성능 향상)
                        truncated_test_id = self._truncate_text(test_id, truncate_lengths["test_id"])
                        truncated_test_name = self._truncate_text(test_name, truncate_lengths["test_name"])
                        truncated_risk_level = self._truncate_text(risk_level, truncate_lengths["risk_level"])
                        truncated_location = self._truncate_text(location, truncate_lengths["location"])

                        self.vuln_tree.insert(
                            "", "end",
                            values=(truncated_test_id, truncated_test_name, truncated_risk_level, truncated_location),
                            tags=(risk_level,)
                        )
                except (tk.TclError, AttributeError) as e:
                    print(f"⚠️ Treeview 삽입 오류: {e}")
                    break

                # UI 업데이트는 더 큰 간격으로 (성능 향상)
                if batch_end % 100 == 0 or batch_end == len(display_data):
                    try:
                        self.vuln_tree.update_idletasks()
                        print(f"  ⏳ {batch_end}/{len(display_data)} 로딩 중...")
                    except (tk.TclError, AttributeError):
                        print("⚠️ UI 업데이트 중 오류 발생")
                        break

            print(f"✅ {len(display_data)}개 취약점 표시 완료")

        except Exception as e:
            print(f"❌ 취약점 로드 오류: {e}")
            import traceback
            traceback.print_exc()
            if hasattr(self, 'vuln_tree') and self.vuln_tree:
                try:
                    self.vuln_tree.insert("", "end", values=("취약점 로드 실패", str(e), "", ""))
                except:
                    pass

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
        for item in self.vuln_tree.get_children():
            self.vuln_tree.delete(item)

        if not self.vulnerability_data:
            self.vuln_tree.insert("", "end", values=("취약점이 발견되지 않았습니다", "", "", ""))
            return

        # 필터 적용된 데이터 가져오기
        display_data = self.get_filtered_vulnerabilities()

        if not display_data:
            self.vuln_tree.insert("", "end", values=("", "", "", ""))
            return

        print(f"📊 필터 적용 후 {len(display_data)}개 취약점 표시 예정")

        # 대량 데이터 처리: 배치로 나눠서 삽입
        BATCH_SIZE = 100

        # 컬럼 너비를 한 번만 계산 (성능 최적화)
        truncate_lengths = {
            "test_id": self._get_dynamic_truncate_length("test_id"),
            "test_name": self._get_dynamic_truncate_length("test_name"),
            "risk_level": self._get_dynamic_truncate_length("risk_level"),
            "location": self._get_dynamic_truncate_length("location")
        }

        # 배치 단위로 삽입
        for batch_start in range(0, len(display_data), BATCH_SIZE):
            batch_end = min(batch_start + BATCH_SIZE, len(display_data))
            batch = display_data[batch_start:batch_end]

            # 배치 처리
            for vuln in batch:
                risk_level = vuln.get("risk_level", "")
                test_id = vuln.get("test_id", "")
                test_name = vuln.get("test_name", "")
                location = vuln.get("location", "")

                # 미리 계산된 길이로 텍스트 절단 (성능 향상)
                truncated_test_id = self._truncate_text(test_id, truncate_lengths["test_id"])
                truncated_test_name = self._truncate_text(test_name, truncate_lengths["test_name"])
                truncated_risk_level = self._truncate_text(risk_level, truncate_lengths["risk_level"])
                truncated_location = self._truncate_text(location, truncate_lengths["location"])

                self.vuln_tree.insert(
                    "",
                    "end",
                    values=(
                        truncated_test_id,
                        truncated_test_name,
                        truncated_risk_level,
                        truncated_location
                    ),
                    tags=(risk_level,)
                )

            # UI 업데이트는 더 큰 간격으로 (성능 향상)
            if batch_end % 500 == 0 or batch_end == len(display_data):
                self.vuln_tree.update_idletasks()

        print(f"✅ {len(display_data)}개 취약점 표시 완료")

    def _truncate_text(self, text, max_length):
        """텍스트가 최대 길이를 초과하면 ...로 표시"""
        if not text:
            return text
        text_str = str(text)
        if len(text_str) <= max_length:
            return text_str
        return text_str[:max_length-3] + "..."

    def _get_dynamic_truncate_length(self, column_name):
        """컬럼 크기에 따른 동적 텍스트 길이 계산"""
        try:
            if not hasattr(self, 'vuln_tree'):
                # 기본값 반환
                defaults = {"test_id": 12, "test_name": 22, "risk_level": 10, "location": 60}
                return defaults.get(column_name, 20)
            
            # 현재 컬럼 너비 가져오기
            column_width = self.vuln_tree.column(column_name, "width")
            
            # 폰트 크기를 고려한 대략적인 문자 수 계산
            # Arial 10pt 기준으로 약 7-8픽셀당 1문자
            char_width = 8
            max_chars = max(5, (column_width - 20) // char_width)  # 최소 5문자, 패딩 20px 고려
            
            return int(max_chars)
        except:
            # 오류 시 기본값 반환
            defaults = {"test_id": 12, "test_name": 22, "risk_level": 10, "location": 60}
            return defaults.get(column_name, 20)

    def on_result_double_click(self, event):
        """결과 더블클릭 이벤트"""
        try:
            selection = self.results_tree.selection()
            if not selection:
                return

            item = selection[0]
            tags = self.results_tree.item(item, "tags")

            if not tags:
                return

            file_path = tags[0]

            # 결과 상세 로드
            result_data = self.controller.load_result_detail(file_path)

            if result_data:
                # after_idle을 사용하여 이벤트 처리 후 뷰 전환
                # lambda 클로저 문제 방지를 위해 default argument 사용
                self.main_container.after_idle(lambda data=result_data: self.show_detail_view(data))
            else:
                messagebox.showerror("오류", "결과 파일을 로드할 수 없습니다.")
        except Exception as e:
            print(f"❌ 더블클릭 이벤트 처리 오류: {e}")
            import traceback
            traceback.print_exc()


    def on_vulnerability_select(self, event):
        """취약점 선택 이벤트"""
        try:
            selection = self.vuln_tree.selection()
            if not selection:
                return

            item = selection[0]
            values = self.vuln_tree.item(item, 'values')

            if len(values) >= 4:
                test_id = values[0]
                test_name = values[1]
                risk_level = values[2]
                location = values[3]

                # 안전하게 선택된 행의 인덱스로 필터링된 데이터에서 접근
                try:
                    selection_index = self.vuln_tree.index(item)
                    filtered_data = self.get_filtered_vulnerabilities()

                    # 인덱스 범위 확인 (세그먼트 오류 방지)
                    if selection_index < 0 or selection_index >= len(filtered_data):
                        print(f"⚠️ 인덱스 범위 초과: {selection_index} (최대: {len(filtered_data)-1})")
                        self.update_detail_text("데이터를 불러올 수 없습니다. 목록을 새로고침해주세요.")
                        return

                    vuln_data = filtered_data[selection_index]

                    # vuln_data가 None이거나 유효하지 않은 경우 체크
                    if not vuln_data or not isinstance(vuln_data, dict):
                        print(f"⚠️ 유효하지 않은 데이터: {vuln_data}")
                        self.update_detail_text("데이터가 손상되었습니다.")
                        return

                    details = vuln_data.get('details', {})
                except (tk.TclError, IndexError, AttributeError) as e:
                    print(f"⚠️ 선택 처리 오류: {e}")
                    self.update_detail_text("선택한 항목을 불러올 수 없습니다.")
                    return

                # detail의 모든 필드를 동적으로 출력
                detail_info = ""

                # 1. 기본 정보 (테이블에서 가져온 값)
                detail_info += f"• 테스트 ID: {test_id}\n"
                detail_info += f"• 검사 유형: {test_name}\n"
                detail_info += f"• 위험도: {risk_level}\n"

                # 2. 한글 라벨 매핑
                FIELD_LABELS = {
                    'location': '위치',
                    'url': 'URL',
                    'path': '경로',
                    'description': '설명',
                    'issue': '이슈',
                    'method': '메서드',
                    'timestamp': '시간',
                    'line': '라인 번호',
                    'pattern': '탐지 패턴',
                    'status_code': '응답 코드',
                    'response_time': '응답 시간',
                    'csrf_token': 'CSRF 토큰',
                    'injection_type': 'Injection 유형',
                    'payload': '공격 페이로드',
                    'missing_headers': '누락된 헤더',
                    'cookie': '쿠키',
                    'session': '세션',
                    'user_agent': 'User Agent',
                    'port': '포트',
                    'service': '서비스',
                    'package': '패키지',
                    'version': '버전',
                    'ecosystem': '에코시스템',
                    'id': '취약점 ID',
                    'protections': '보호 메커니즘',
                    'samesite': 'SameSite Cookie',
                    'tokens_found': 'CSRF 토큰',
                    'forms': '폼',
                    'test_id': None,  # 건너뛰기
                    'test_name': None,  # 건너뛰기
                    'risk_level': None,  # 건너뛰기
                }

                # 우선 순서 필드 (공통적으로 먼저 출력할 필드들)
                PRIORITY_FIELDS = [
                    'location',
                    'url',
                    'path',
                    'description',
                    'issue',
                    'method',
                    'line',
                    'pattern',
                    'status_code',
                    'timestamp'
                ]

                # 3. details의 모든 키-값을 우선순위에 따라 출력 (빈 값 제외)
                if isinstance(details, dict):
                    # 3-1. 먼저 우선순위 필드 출력
                    for key in PRIORITY_FIELDS:
                        if key in details:
                            value = details[key]

                            # None이거나 빈 문자열, 빈 리스트는 건너뛰기
                            if value is None or value == '' or value == [] or value == {}:
                                continue

                            # 값 포맷팅 (함수 사용)
                            formatted_value = self._format_value(key, value)

                            # 한글 라벨 가져오기
                            label = FIELD_LABELS.get(key, key.replace('_', ' ').title())
                            detail_info += f"• {label}: {formatted_value}\n"

                    # 3-2. 나머지 필드 출력 (우선순위에 없는 필드들)
                    for key, value in details.items():
                        # 이미 출력한 우선순위 필드는 건너뛰기
                        if key in PRIORITY_FIELDS:
                            continue

                        # None이거나 빈 문자열, 빈 리스트는 건너뛰기
                        if value is None or value == '' or value == [] or value == {}:
                            continue

                        # 건너뛸 필드 (None으로 표시된 필드)
                        if key in FIELD_LABELS and FIELD_LABELS[key] is None:
                            continue

                        # 값 포맷팅 (함수 사용)
                        formatted_value = self._format_value(key, value)

                        # 한글 라벨 가져오기 (없으면 키를 읽기 쉽게 변환)
                        label = FIELD_LABELS.get(key, key.replace('_', ' ').title())
                        detail_info += f"• {label}: {formatted_value}\n"

                # 4. 취약점 설명
                detail_info += "\n" + self._get_vulnerability_description(test_name)

                self.update_detail_text(detail_info)

        except Exception as e:
            print(f"❌ 항목 선택 처리 실패: {e}")
            import traceback
            traceback.print_exc()

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

    def _get_vulnerability_description(self, test_name):
        """취약점 유형별 설명 반환"""
        if "CSRF" in test_name:
            return ("• 취약점 설명: 공격자가 사용자의 권한을 도용하여 악의적인 요청을 실행할 수 있는 취약점입니다.\n"
                   "• 권장 조치: CSRF 토큰 구현, SameSite 쿠키 속성 설정, Referer 검증\n")
        elif "Rate_Limit" in test_name:
            return ("• 취약점 설명: 요청 빈도 제한이 설정되지 않아 무차별 공격(브루트포스)이 가능한 취약점입니다.\n"
                   "• 권장 조치: 요청 빈도 제한 설정, IP별 접근 제한 구현, 계정 잠금 정책 적용\n")
        elif "Permission" in test_name or "Access" in test_name:
            return ("• 취약점 설명: 인증 및 권한 검증이 부족하여 보호된 리소스에 접근할 수 있는 취약점입니다.\n"
                   "• 권장 조치: 모든 보호 리소스에 인증 검증 추가, 권한별 접근 제어 강화\n")
        elif "XSS" in test_name:
            return ("• 취약점 설명: 웹 페이지에 악성 스크립트를 삽입하여 사용자의 브라우저에서 실행되는 취약점입니다.\n"
                   "• 권장 조치: 입력값 검증 및 이스케이프 처리, Content Security Policy 적용, HttpOnly 쿠키 설정\n")
        elif "SQL" in test_name:
            return ("• 취약점 설명: 데이터베이스 쿼리에 악성 SQL 코드를 삽입하여 데이터베이스를 조작할 수 있는 취약점입니다.\n"
                   "• 권장 조치: Prepared Statement 사용, 입력값 검증 강화, 데이터베이스 권한 최소화\n")
        elif "Command" in test_name or "Injection" in test_name:
            return ("• 취약점 설명: 시스템 명령어나 코드를 주입하여 서버를 조작할 수 있는 취약점입니다.\n"
                   "• 권장 조치: 입력값 검증 및 살균 처리, 안전한 API 사용, 최소 권한 원칙 적용\n")
        elif "vulnerable" in test_name.lower() or "header" in test_name.lower():
            return ("• 취약점 설명: 보안 헤더가 누락되거나 민감한 정보가 HTTP 헤더를 통해 노출되는 취약점입니다.\n"
                   "• 권장 조치: 보안 헤더 추가 (X-Frame-Options 등), 서버 정보 헤더 제거, HTTPS 강제 적용\n")
        elif "Library" in test_name or "Component" in test_name:
            return ("• 취약점 설명: 알려진 취약점이 있는 오래된 라이브러리를 사용하여 공격에 노출될 수 있는 취약점입니다.\n"
                   "• 권장 조치: 라이브러리 최신 버전으로 업데이트, 정기적인 의존성 점검, 취약점 스캐닝 자동화\n")
        else:
            return (f"• 취약점 설명: {test_name} 관련 보안 취약점이 발견되었습니다.\n"
                   "• 권장 조치: 상세한 보안 점검 수행, 보안 전문가 상담, 정기적인 취약점 점검\n")

    def update_detail_text(self, text):
        """상세 정보 텍스트 업데이트"""
        self.detail_text.config(state="normal")
        self.detail_text.delete("1.0", tk.END)
        self.detail_text.insert("1.0", text)
        self.detail_text.config(state="disabled")

    def refresh_list(self):
        """목록 새로고침"""
        self.load_results()
        messagebox.showinfo("새로고침", "결과 목록을 새로고침했습니다.")

    def generate_report(self):
        """보고서 생성"""
        if not self.current_result_data:
            messagebox.showerror("오류", "결과 데이터가 없습니다.")
            return

        try:
            # 프로젝트 루트 디렉토리 찾기
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(current_dir))

            # 임시 JSON 파일 경로 생성 (results 폴더에 임시 저장)
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            temp_json_file = os.path.join(project_root, "results", f"temp_report_data_{timestamp}.json")

            # results 디렉토리가 없으면 생성
            os.makedirs(os.path.dirname(temp_json_file), exist_ok=True)

            # 현재 결과 데이터를 JSON 파일로 저장
            with open(temp_json_file, 'w', encoding='utf-8') as f:
                json.dump(self.current_result_data, f, ensure_ascii=False, indent=2)

            print(f"✅ 임시 JSON 파일 생성: {temp_json_file}")

            # 보고서 출력 경로 (report 폴더)
            report_output_file = os.path.join(project_root, "report", f"security_report_{timestamp}.html")

            # report 디렉토리가 없으면 생성
            os.makedirs(os.path.dirname(report_output_file), exist_ok=True)

            # 보고서 생성
            report_path = generate_report_from_file(temp_json_file, report_output_file)

            # 임시 JSON 파일 삭제
            try:
                os.remove(temp_json_file)
                print(f"✅ 임시 JSON 파일 삭제: {temp_json_file}")
            except:
                pass

            # 성공 메시지
            messagebox.showinfo(
                "보고서 생성 완료",
                f"HTML 보고서가 생성되었습니다.\n\n파일 경로:\n{report_path}"
            )

        except Exception as e:
            print(f"❌ 보고서 생성 오류: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("오류", f"보고서 생성 중 오류가 발생했습니다:\n{str(e)}")
