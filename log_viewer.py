import sys
import os
from PyQt5.QtWidgets import QApplication
from widget.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)

    if getattr(sys, 'frozen', False):
        # 1. PyInstaller로 빌드된 .exe 파일일 때
        # sys.executable은 .exe 파일의 경로입니다.
        base_path = os.path.dirname(sys.executable)
    else:
        # 2. .py 스크립트로 직접 실행할 때
        # __file__은 이 .py 파일의 경로입니다.
        base_path = os.path.dirname(os.path.abspath(__file__))

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
    QScrollBar:vertical { background: #1e1e1e; width: 12px;}
    QScrollBar::handle:vertical { background: #e0e0e0;  min-height: 100px; margin-top: -2px; margin-bottom: -2px; border-radius: 4px;}
    QSplitter::handle { background-color: #444; }
    QSplitter::handle:horizontal { width: 2px; }
    """)
    
    viewer = MainWindow(base_path)
    viewer.show()
    sys.exit(app.exec_())
