# side_panel.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt, pyqtSignal

# 분리된 위젯들 임포트
from .side_penel_widget.search_widget import SearchWidget
from .side_penel_widget.go_to_line_widget import GoToLineWidget
from .side_penel_widget.item_managers import FilterManager, HighlightManager

class SidePanel(QWidget):
    # MainWindow로 보낼 시그널들
    filters_updated = pyqtSignal(list)
    highlights_updated = pyqtSignal(list)
    export_requested = pyqtSignal()
    search_triggered = pyqtSignal(str, object)
    search_cleared = pyqtSignal()
    go_to_line_requested = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        # 1. 위젯 생성
        self.search_widget = SearchWidget()
        # self.go_to_line_widget = GoToLineWidget()
        self.filter_manager = FilterManager()
        self.hl_manager = HighlightManager()
        
        self.info_label = QLabel(
            "Made by: js1008.han@samsung.com\n"
            "Update Date: 2025-10-23\n"
            "Version: 1.0.1"
        )
        self.info_label.setStyleSheet("""
            QLabel {
                font-size: 9pt;
                color: #888;
                padding-top: 10px;
                padding-left: 5px;
            }
        """)
        self.info_label.setAlignment(Qt.AlignLeft)
        
        self.export_btn = QPushButton("Export Visible Log")
        
        # 2. 레이아웃에 조립
        layout.addWidget(self.search_widget)
        # layout.addWidget(self.go_to_line_widget)
        layout.addWidget(self.filter_manager)
        layout.addWidget(self.hl_manager)
        layout.addStretch() 
        layout.addWidget(self.info_label)
        layout.addWidget(self.export_btn)
        
        # 3. 내부 시그널을 외부 시그널로 연결
        self.filter_manager.items_changed.connect(self.filters_updated)
        self.hl_manager.items_changed.connect(self.highlights_updated)
        self.export_btn.clicked.connect(self.export_requested)
        self.search_widget.search_triggered.connect(self.search_triggered)
        self.search_widget.search_cleared.connect(self.search_cleared)
        # self.go_to_line_widget.go_to_line_requested.connect(self.go_to_line_requested)
        
    def load_settings(self, config):
        """설정을 각 매니저에 전달합니다."""
        filters = config.get("filters", [])
        highlights = config.get("highlights", [])
        
        for f_data in filters:
            term = f_data.get("term")
            is_case_i = f_data.get("is_case_i", False)
            if term:
                self.filter_manager.add_filter_item(term, checked=True, is_case_i=is_case_i)
        
        for h_data in highlights:
            term = h_data.get("term")
            color = h_data.get("color", "#ffff00")
            is_case_i = h_data.get("is_case_i", False)
            if term:
                self.hl_manager.add_highlight_item(term, color, checked=True, is_case_i=is_case_i)