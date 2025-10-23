# core_logic.py
import json
import os
import re

class SettingsManager:
    """설정을 JSON 파일로 저장하고 불러오는 클래스"""
    def __init__(self, filepath):
        self.filepath = filepath

    def load(self):
        """설정 파일에서 데이터를 불러옵니다."""
        if not os.path.exists(self.filepath):
            return {}
        try:
            with open(self.filepath, "r") as f:
                data = json.load(f)
            return data
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}

    def save(self, data):
        """데이터를 설정 파일에 저장합니다."""
        try:
            with open(self.filepath, "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

class LogDataManager:
    """로그 파일의 원본 데이터를 관리하고 필터링하는 클래스"""
    def __init__(self):
        self.lines = []

    def load_file(self, path):
        """파일을 읽어 원본 라인을 저장합니다."""
        try:
            with open(path, "r", encoding="utf-8", errors='ignore') as f:
                self.lines = f.readlines()
            return True
        except Exception as e:
            print(f"Error loading log file: {e}")
            self.lines = []
            return False

    def get_filtered_lines(self, active_filters):
        """필터 규칙에 따라 원본 라인을 필터링하여 반환합니다."""
        if not active_filters:
            # 필터가 없으면 전체 라인을 (인덱스, 텍스트)로 반환
            return list(enumerate(self.lines))

        filtered_data = []
        for idx, line in enumerate(self.lines):
            line_text = line.rstrip("\n")
            
            # OR 조건: 필터 중 하나라도 맞으면 통과
            passed = False
            for f_data in active_filters:
                term = f_data["term"]
                is_case_i = f_data["is_case_i"]
                
                if is_case_i:
                    if term.lower() in line_text.lower():
                        passed = True
                        break
                else:
                    if term in line_text:
                        passed = True
                        break
            
            if passed:
                filtered_data.append((idx, line))
        
        return filtered_data