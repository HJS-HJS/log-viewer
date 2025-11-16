# log_view.py
import re
from PyQt5.QtWidgets import QPlainTextEdit
from PyQt5.QtGui import (
    QColor, QTextCharFormat, QFont, QSyntaxHighlighter,
    QTextDocument, QTextCursor
)
from PyQt5.QtCore import Qt, QRegExp

# --- Highlighter 클래스 (변경 없음) ---
class Highlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlight_rules = []

    def set_rules(self, rules_list):
        """
        rules_list: [{"term": str, "color": QColor, "is_case_i": bool}, ...]
        """
        self.highlight_rules = []
        for rule in rules_list:
            term = rule["term"]
            color = rule["color"]
            is_case_i = rule["is_case_i"]
            
            fmt = QTextCharFormat()
            fmt.setBackground(color)
            
            flags = re.IGNORECASE if is_case_i else 0
            
            try:
                # 일반 텍스트 검색 (이스케이프 처리)
                pattern = re.compile(re.escape(term), flags)
                self.highlight_rules.append((pattern, fmt))
            except re.error as e:
                print(f"Error compiling: {term} -> {e}")
        
        self.rehighlight()

    def highlightBlock(self, text):
        # 줄 번호 서식 (회색)
        line_num_format = QTextCharFormat()
        line_num_format.setForeground(QColor("#888888"))
        # " 123456 | " (10자)
        self.setFormat(0, 10, line_num_format)

        # 하이라이트 규칙 적용
        for pattern, fmt in self.highlight_rules:
            for match in pattern.finditer(text):
                start, end = match.span(0)
                # 줄 번호 영역(0~10)은 덮어쓰지 않음
                if start >= 10:
                    self.setFormat(start, end - start, fmt)


# --- LogView 클래스 ---
class LogView(QPlainTextEdit):
    """로그 텍스트를 표시하고 검색/하이라이트를 담당하는 뷰"""
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self.setFont(QFont("Courier New", 10))
        
        self.highlighter = Highlighter(self.document())
        
        self.search_results = []
        self.search_index = -1
        self.last_search_term = ""

        # --- [핵심 수정] 원본 줄 번호(key)와 뷰 줄 번호(value) 매핑 ---
        self.original_to_displayed_map = {} 
        # --- [여기까지] ---


    # --- [핵심 수정] set_log_data 메서드 ---
    def set_log_data(self, filtered_data):
        """(인덱스, 라인) 리스트를 받아 줄 번호와 함께 텍스트를 설정합니다."""
        
        # [수정] 매핑 초기화
        self.original_to_displayed_map.clear()
        
        # 1. 텍스트 조립 및 매핑 생성
        display_lines = []
        # 'displayed_index'는 0부터 시작하는 필터링된 뷰의 줄 번호
        for displayed_index, (original_index, line) in enumerate(filtered_data):
            
            # [수정] 원본 인덱스(0-based) -> 표시된 인덱스(0-based)
            self.original_to_displayed_map[original_index] = displayed_index
            
            line_text = line.rstrip("\n")
            line_num = f"{original_index+1:>6}" # 원본 인덱스+1
            display_lines.append(f" {line_num} | {line_text}")
        
        # 2. 텍스트 설정
        self.setPlainText("\n".join(display_lines))
        
        # 3. 하이라이트 및 검색 상태 초기화
        self.clear_manual_formats()
        self.highlighter.rehighlight() # 하이라이트 재적용
        self.search_results.clear()
        self.search_index = -1
    # --- [여기까지 수정] ---

    def update_highlight_rules(self, rules_list):
        """Highlighter에 새 규칙을 적용합니다."""
        self.highlighter.set_rules(rules_list)

    # ... (find_next 메서드는 변경 없음) ...
    def find_next(self, term, find_flags):
        if term != self.last_search_term or not self.search_results:
            self.last_search_term = term
            self.search_results.clear()
            self.search_index = -1
            
            cursor = self.document().find(term, 0, find_flags)
            while not cursor.isNull():
                self.search_results.append(cursor)
                cursor = self.document().find(term, cursor, find_flags)
        
        if not self.search_results:
            return 0, 0
            
        self.search_index = (self.search_index + 1) % len(self.search_results)
        
        self.clear_manual_formats() 
        self.highlighter.rehighlight() 
        
        current_cursor = self.search_results[self.search_index]
        fmt = QTextCharFormat()
        fmt.setBackground(QColor("#00ff00"))
        fmt.setForeground(QColor("#000000"))
        current_cursor.mergeCharFormat(fmt)
        self.setTextCursor(current_cursor)
        
        return self.search_index + 1, len(self.search_results)

    # --- [핵심 수정] go_to_line 메서드 (근사치 이동 기능 포함) ---
    def go_to_line(self, original_line_num): # 1-based
        """원본 줄 번호를 받아 해당 줄로 이동합니다. 없으면 근사치로 이동합니다."""
        target_original_index = original_line_num - 1 # 0-based
        
        if not self.original_to_displayed_map:
            return False # 뷰가 비어있음

        # 1. 정확한 줄 번호가 뷰에 있는지 확인
        displayed_line_index = self.original_to_displayed_map.get(target_original_index)
        
        if displayed_line_index is None:
            # 2. (근사치 찾기) 뷰에 없음. 타겟보다 *작은* 라인 중 가장 큰(가까운) 라인을 찾음
            # (딕셔너리 키는 원본 인덱스이므로 정렬되어 있음)
            closest_original_index = -1
            for index in self.original_to_displayed_map.keys():
                if index < target_original_index:
                    closest_original_index = index
                else:
                    # 타겟보다 큰 인덱스를 만났으므로, 바로 이전 인덱스가 근사치임
                    break
            
            if closest_original_index != -1:
                # 850번 줄을 찾음
                displayed_line_index = self.original_to_displayed_map[closest_original_index]
            else:
                # 3. (근사치 찾기) 타겟보다 *작은* 라인이 없음 (예: 100번 입력, 뷰는 200번부터 시작)
                # 그냥 뷰의 *첫 번째* 라인으로 이동
                try:
                    first_visible_original_index = next(iter(self.original_to_displayed_map))
                    displayed_line_index = self.original_to_displayed_map[first_visible_original_index]
                except StopIteration:
                    return False # 맵이 완전히 비어있음
            
        # 4. 해당 뷰의 줄 번호로 커서 이동
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.Start)
        cursor.movePosition(QTextCursor.NextBlock, QTextCursor.MoveAnchor, displayed_line_index)
        
        self.setTextCursor(cursor)
        self.centerCursor() # 커서 위치를 뷰의 중앙으로
        
        self.setFocus() # 뷰 활성화
        
        return True
    # --- [여기까지 수정] ---

    def clear_manual_formats(self):
        """수동으로 적용된 서식(초록색 검색)을 지웁니다."""
        null_fmt = QTextCharFormat()
        cursor = self.textCursor()
        cursor.select(QTextCursor.Document)
        cursor.setCharFormat(null_fmt)

    def clear_search_highlights(self):
        """검색 하이라이트를 지우고 영구 하이라이트를 복원합니다."""
        self.clear_manual_formats()
        self.highlighter.rehighlight()
        self.search_results.clear()
        self.search_index = -1
        self.last_search_term = ""
