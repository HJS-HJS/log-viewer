from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPlainTextEdit, QLabel

class MemoWidget(QWidget):
    
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        add_widget = QWidget()
        add_layout = QHBoxLayout(add_widget)
        add_layout.addWidget(QLabel("Memo"))

        self.memo_box = QPlainTextEdit() 
        self.memo_box.setPlaceholderText("Memo...")

        layout.addWidget(add_widget)
        layout.addWidget(self.memo_box)

    def get_text(self):
        return self.memo_box.toPlainText()
        
    def set_text(self, text):
        self.memo_box.setPlainText(text)