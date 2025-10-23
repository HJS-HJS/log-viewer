# search_widget.py
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QCheckBox, QLabel
from PyQt5.QtGui import QTextDocument
from PyQt5.QtCore import pyqtSignal

class SearchWidget(QWidget):
    # 시그널: (검색어, 검색플래그)
    search_triggered = pyqtSignal(str, object) 
    search_cleared = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search...")
        
        self.search_case_cb = QCheckBox("Case (i)")
        self.search_case_cb.setToolTip("Case Insensitive Search")
        
        self.search_count_label = QLabel("0/0")
        self.search_count_label.setFixedWidth(60)
        
        layout.addWidget(self.search_box)
        layout.addWidget(self.search_case_cb)
        layout.addWidget(self.search_count_label)
        
        self.search_box.returnPressed.connect(self.on_search)
        self.search_box.textChanged.connect(self.on_text_changed)
        self.search_case_cb.stateChanged.connect(self.on_search)

    def on_search(self):
        term = self.search_box.text().strip()
        if term:
            find_flags = QTextDocument.FindFlags()
            if not self.search_case_cb.isChecked():
                find_flags |= QTextDocument.FindCaseSensitively
            
            self.search_triggered.emit(term, find_flags)
        else:
            self.search_cleared.emit()
            
    def on_text_changed(self, text):
        if not text.strip():
            self.search_count_label.setText("0/0")
            self.search_cleared.emit()

    def set_search_count(self, index, total):
        """검색 결과 라벨을 업데이트하는 슬롯"""
        self.search_count_label.setText(f"{index}/{total}")