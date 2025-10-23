# go_to_line_widget.py
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton
from PyQt5.QtGui import QIntValidator
from PyQt5.QtCore import pyqtSignal

class GoToLineWidget(QWidget):
    go_to_line_requested = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.line_num_box = QLineEdit()
        self.line_num_box.setPlaceholderText("Go to line...")
        self.line_num_box.setValidator(QIntValidator(1, 9999999)) 
        
        self.go_btn = QPushButton("Go")
        self.go_btn.setFixedWidth(40)
        
        layout.addWidget(self.line_num_box)
        layout.addWidget(self.go_btn)
        
        self.go_btn.clicked.connect(self.on_go_to_line)
        self.line_num_box.returnPressed.connect(self.on_go_to_line)
        
    def on_go_to_line(self):
        text = self.line_num_box.text()
        if text.isdigit():
            self.go_to_line_requested.emit(int(text))
            self.line_num_box.clear()