# main_window.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, 
    QLineEdit, QPushButton, QFileDialog, QMessageBox, QCheckBox
)
from PyQt5.QtCore import QFileInfo, Qt

from .core_logic import LogDataManager, SettingsManager
from .log_view import LogView
from .side_panel import SidePanel

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Log Viewer")
        self.resize(1200, 700)

        # 1. 로직 및 설정 관리자 생성
        self.log_data = LogDataManager()
        self.settings = SettingsManager("log_viewer_config.json")

        # 2. UI 위젯 생성
        self.log_view = LogView()
        self.side_panel = SidePanel()
        
        self.file_path_box = QLineEdit()
        self.file_path_box.setPlaceholderText("Enter file path...")
        self.file_path_box.setFixedHeight(30)
        
        self.file_btn = QPushButton("📁")
        self.file_btn.setFixedWidth(30)
        self.file_btn.setFixedHeight(30)

        # 3. UI 레이아웃 조립
        top_layout = QHBoxLayout()
        top_layout.addWidget(self.file_path_box)
        top_layout.addWidget(self.file_btn)
        
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.log_view)
        splitter.addWidget(self.side_panel)
        splitter.setStretchFactor(0, 3) # 로그 창이 더 넓게
        splitter.setStretchFactor(1, 1)

        main_layout = QVBoxLayout(self)
        main_layout.addLayout(top_layout)
        main_layout.addWidget(splitter)

        # 4. 시그널/슬롯 연결 (핵심)
        self.file_btn.clicked.connect(self.on_open_file_dialog)
        self.file_path_box.returnPressed.connect(self.on_load_from_path)
        
        # 사이드 패널의 시그널을 메인 윈도우의 슬롯에 연결
        self.side_panel.filters_updated.connect(self.on_filters_changed)
        self.side_panel.highlights_updated.connect(self.on_highlights_changed)
        self.side_panel.export_requested.connect(self.on_export_log)
        self.side_panel.search_triggered.connect(self.on_search)
        self.side_panel.search_cleared.connect(self.log_view.clear_search_highlights)

        # 5. 설정 불러오기
        self.load_settings()

    # --- 슬롯 메서드 ---
    
    def on_open_file_dialog(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Log File", "", "All Files (*.*);;Text Files (*.txt)")
        if path:
            self.file_path_box.setText(path)
            self.load_file(path)

    def on_load_from_path(self):
        path = self.file_path_box.text().strip()
        if path:
            self.load_file(path)
            
    def load_file(self, path):
        """파일을 로드하고 뷰를 갱신합니다."""
        file_info = QFileInfo(path)
        if not (file_info.exists() and file_info.isFile()):
            QMessageBox.warning(self, "Error", "File does not exist.")
            return
            
        if self.log_data.load_file(path):
            # 파일 로드 성공 시, 현재 필터/하이라이트 기준으로
            # 뷰를 다시 그림
            self.on_filters_changed()
            self.on_highlights_changed()
        else:
            QMessageBox.warning(self, "Error", f"Failed to load log file:\n{path}")

    def on_filters_changed(self):
        """필터가 변경되면, 로직을 호출하고 뷰를 갱신합니다."""
        active_filters = self.side_panel.filter_manager.get_all_data()
        filtered_data = self.log_data.get_filtered_lines(active_filters)
        self.log_view.set_log_data(filtered_data)
        # 필터 변경 시 하이라이트도 다시 적용해야 함
        self.on_highlights_changed()

    def on_highlights_changed(self):
        """하이라이트가 변경되면, 뷰의 하이라이터를 갱신합니다."""
        active_highlights = self.side_panel.hl_manager.get_all_data()
        self.log_view.update_highlight_rules(active_highlights)

    def on_search(self, term, find_flags):
        """검색 신호를 받아 뷰에서 검색을 실행하고, 결과를 패널에 알립니다."""
        index, total = self.log_view.find_next(term, find_flags)
        self.side_panel.search_widget.set_search_count(index, total)

    def on_export_log(self):
        """내보내기 신호를 받아 파일 저장 대화상자를 엽니다."""
        
        # 1. 파일 경로 먼저 묻기
        path, _ = QFileDialog.getSaveFileName(self, 
            "Export Visible Log", "", "Text Files (*.txt);;All Files (*.*)")
        
        if not path:
            return # 사용자가 취소함
            
        # 2. 줄 번호 포함 여부 묻기 (옵션 팝업)
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Export Options")
        msg_box.setText("Will you export include line number?")
        
        # '예' (줄 번호 포함), '아니오' (텍스트만), '취소' 버튼
        include_btn = msg_box.addButton("Yes (Include Line Number)", QMessageBox.YesRole)
        exclude_btn = msg_box.addButton("No (Only Text)", QMessageBox.NoRole)
        cancel_btn = msg_box.addButton("Cancle", QMessageBox.RejectRole)
        
        msg_box.setDefaultButton(include_btn)
        msg_box.exec_()
        
        clicked_button = msg_box.clickedButton()
        
        # 3. 사용자 선택에 따라 동작
        try:
            if clicked_button == cancel_btn:
                return # 내보내기 취소
                
            elif clicked_button == include_btn:
                # 옵션 1: 줄 번호 포함 (현재 보이는 그대로 저장)
                text_to_save = self.log_view.toPlainText()
                
            elif clicked_button == exclude_btn:
                # 옵션 2: 줄 번호 제외 (텍스트만)
                # " 1234 | " (9자) 형식을 제거
                original_text = self.log_view.toPlainText()
                lines = original_text.split('\n')
                # 각 줄의 9번째 문자부터 끝까지 (줄 번호 포맷: " 1234 | ")
                stripped_lines = [line[9:] for line in lines]
                text_to_save = "\n".join(stripped_lines)

            # 4. 파일 쓰기
            with open(path, "w", encoding="utf-8") as f:
                f.write(text_to_save)
                
        except Exception as e:
            QMessageBox.warning(self, "Export Error", f"Failed to export log:\n{e}")

    # --- 설정 저장/불러오기 ---
    
    def load_settings(self):
        config = self.settings.load()
        if config:
            self.side_panel.load_settings(config)

    def closeEvent(self, event):
        """창을 닫을 때 현재 설정을 저장합니다."""
        # 각 매니저에서 '모든' 아이템의 데이터를 수집
        filters = []
        for i in range(self.side_panel.filter_manager.list_widget.count()):
            item = self.side_panel.filter_manager.list_widget.item(i)
            widget = self.side_panel.filter_manager.list_widget.itemWidget(item)
            data = item.data(Qt.UserRole)
            case_cb = widget.findChild(QCheckBox, "case_i_cb")
            data["is_case_i"] = case_cb.isChecked() if case_cb else False
            filters.append(data)
            
        highlights = []
        for i in range(self.side_panel.hl_manager.list_widget.count()):
            item = self.side_panel.hl_manager.list_widget.item(i)
            widget = self.side_panel.hl_manager.list_widget.itemWidget(item)
            data = item.data(Qt.UserRole)
            case_cb = widget.findChild(QCheckBox, "case_i_cb")
            data["is_case_i"] = case_cb.isChecked() if case_cb else False
            data["color"] = self.side_panel.hl_manager.highlight_colors.get(data["term"], QColor("#ffff00")).name()
            highlights.append(data)

        config_to_save = {
            "filters": filters,
            "highlights": highlights
        }
        self.settings.save(config_to_save)
        event.accept()