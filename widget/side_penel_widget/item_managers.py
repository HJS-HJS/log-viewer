from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
    QListWidget, QListWidgetItem, QPushButton, QCheckBox, 
    QColorDialog, QLabel
)
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt, pyqtSignal

class BaseItemManager(QWidget):
    items_changed = pyqtSignal(list)
    
    def __init__(self, name='', add_placeholder=''):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.add_box = QLineEdit()
        self.add_box.setPlaceholderText(add_placeholder)
        
        self.add_btn = QPushButton(f"Add {self.__class__.__name__.replace('Manager', '')}")
        
        self.list_widget = QListWidget()

        add_widget = QWidget()
        add_layout = QHBoxLayout(add_widget)
        add_layout.addWidget(QLabel(name))
        add_layout.addWidget(self.add_box)
        add_layout.addWidget(self.add_btn)
        
        layout.addWidget(add_widget)
        layout.addWidget(self.list_widget)
        
        self.add_box.returnPressed.connect(self.on_add_pressed)
        self.add_btn.clicked.connect(self.on_add_pressed)

    def on_add_pressed(self):
        raise NotImplementedError

    def find_item(self, term):
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            data = item.data(Qt.UserRole)
            if data and data.get("term") == term:
                return item
        return None

    def get_all_data(self):
        data_list = []
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            widget = self.list_widget.itemWidget(item)
            cb = widget.findChild(QCheckBox)
            
            if cb and cb.isChecked():
                data = item.data(Qt.UserRole)
                if data:
                    case_cb = widget.findChild(QCheckBox, "case_i_cb")
                    data["is_case_i"] = case_cb.isChecked() if case_cb else False
                    data_list.append(data)
        return data_list

    def remove_item(self, list_item):
        self.list_widget.takeItem(self.list_widget.row(list_item))
        self.items_changed.emit(self.get_all_data())


# --- 필터 관리자 ---
class FilterManager(BaseItemManager):
    def __init__(self, filter_type='OR'):
        super().__init__(filter_type + " Filter", "Add filter keyword")

    def on_add_pressed(self):
        term = self.add_box.text().strip()
        if not term or self.find_item(term):
            return
        self.add_box.clear()
        self.add_filter_item(term, checked=True)
        self.items_changed.emit(self.get_all_data())

    def add_filter_item(self, term, checked=True, is_case_i=False):
        item_widget = QWidget()
        layout = QHBoxLayout(item_widget)
        layout.setContentsMargins(3, 0, 3, 0)
        
        checkbox = QCheckBox(term)
        checkbox.setChecked(checked)
        
        case_cb = QCheckBox("i")
        case_cb.setToolTip("Case Insensitive")
        case_cb.setObjectName("case_i_cb")
        case_cb.setFixedWidth(30)
        case_cb.setChecked(is_case_i)
        
        remove_btn = QPushButton("X")
        remove_btn.setFixedWidth(20)
        
        layout.addWidget(checkbox)
        layout.addStretch()
        layout.addWidget(case_cb)
        layout.addWidget(remove_btn)
        
        list_item = QListWidgetItem()
        data = {"term": term}
        list_item.setData(Qt.UserRole, data)
        
        self.list_widget.insertItem(0, list_item)
        self.list_widget.setItemWidget(list_item, item_widget)
        
        remove_btn.clicked.connect(lambda: self.remove_item(list_item))
        checkbox.stateChanged.connect(lambda: self.items_changed.emit(self.get_all_data()))
        case_cb.stateChanged.connect(lambda: self.items_changed.emit(self.get_all_data()))

# --- 하이라이트 관리자 ---
class HighlightManager(BaseItemManager):
    items_changed = pyqtSignal(list)
    
    def __init__(self):
        super().__init__("Highlighter", "Add highlight keyword")
        self.highlight_colors = {}

    def on_add_pressed(self):
        term = self.add_box.text().strip()
        if not term or self.find_item(term):
            return
        self.add_box.clear()
        self.add_highlight_item(term, "#ffff00", checked=True)
        self.items_changed.emit(self.get_all_data())

    def get_all_data(self):
        data_list = super().get_all_data()
        for data in data_list:
            data["color"] = self.highlight_colors.get(data["term"], QColor("#ffff00"))
        return data_list

    def add_highlight_item(self, term, color, checked=True, is_case_i=False):
        item_widget = QWidget()
        layout = QHBoxLayout(item_widget)
        layout.setContentsMargins(3, 0, 3, 0)
        
        checkbox = QCheckBox(term)
        checkbox.setChecked(checked)
        
        color_btn = QPushButton()
        color_btn.setFixedWidth(30)
        q_color = QColor(color)
        color_btn.setStyleSheet(f"background-color: {q_color.name()}; border-radius: 3px;")
        
        case_cb = QCheckBox("i")
        case_cb.setToolTip("Case Insensitive")
        case_cb.setObjectName("case_i_cb")
        case_cb.setFixedWidth(30)
        case_cb.setChecked(is_case_i)
        
        remove_btn = QPushButton("X")
        remove_btn.setFixedWidth(20)
        
        layout.addWidget(checkbox)
        layout.addStretch()
        layout.addWidget(color_btn)
        layout.addWidget(case_cb)
        layout.addWidget(remove_btn)
        
        list_item = QListWidgetItem()
        data = {"term": term}
        list_item.setData(Qt.UserRole, data)
        self.highlight_colors[term] = q_color
        
        self.list_widget.insertItem(0, list_item)
        self.list_widget.setItemWidget(list_item, item_widget)
        
        def change_color():
            new_color = QColorDialog.getColor(self.highlight_colors[term], self)
            if new_color.isValid():
                self.highlight_colors[term] = new_color
                color_btn.setStyleSheet(f"background-color: {new_color.name()}; border-radius: 3px;")
                self.items_changed.emit(self.get_all_data())

        color_btn.clicked.connect(change_color)
        remove_btn.clicked.connect(lambda: self.remove_item(list_item))
        checkbox.stateChanged.connect(lambda: self.items_changed.emit(self.get_all_data()))
        case_cb.stateChanged.connect(lambda: self.items_changed.emit(self.get_all_data()))

    def remove_item(self, list_item):
        data = list_item.data(Qt.UserRole)
        if data:
            term = data.get("term")
            if term and term in self.highlight_colors:
                del self.highlight_colors[term]
        super().remove_item(list_item)
