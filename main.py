# main.py
import sys
from PyQt5.QtWidgets import QApplication
from widget.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 다크 모드 스타일을 앱 전체에 적용
    app.setStyleSheet("""
    QWidget { 
        background-color: #1e1e1e; 
        color: #e0e0e0; 
        selection-background-color: #555; /* 선택 영역 색상 */
    }
    QLineEdit, QListWidget, QPlainTextEdit {
        background-color: #2b2b2b; 
        border: 1px solid #444; 
        border-radius: 6px; 
        padding: 4px;
    }
    QPushButton { 
        background-color: #3a3a3a; 
        border: 1px solid #555; 
        border-radius: 6px; 
        padding: 5px; 
    }
    QPushButton:hover { background-color: #505050; }
    QCheckBox { margin: 2px; }
    QCheckBox::indicator { 
        width: 16px; height: 16px; 
        background-color: #3a3a3a; 
        border: 1px solid #777; 
    }
    QCheckBox::indicator:checked { background-color: #888; }
    /* 'i' 체크박스만 작게 만들기 */
    QCheckBox[objectName="case_i_cb"] { font-size: 9pt; }
    QCheckBox[objectName="case_i_cb"]::indicator { width: 12px; height: 12px; }
    QScrollBar:vertical { background: #1e1e1e; width: 12px; }
    QScrollBar::handle:vertical { background: #e0e0e0; }
    QSplitter::handle { background-color: #444; }
    QSplitter::handle:horizontal { width: 2px; }
    """)
    
    viewer = MainWindow()
    viewer.show()
    sys.exit(app.exec_())