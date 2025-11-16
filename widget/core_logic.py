import json
import os
import re
import gzip
import zipfile
import tarfile
from io import TextIOWrapper

class SettingsManager:
    """설정을 JSON 파일로 저장하고 불러오는 클래스"""
    def __init__(self, base_path):
        self.filepath = os.path.join(base_path, ".log_viewer_config.json")

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

    # def load_file(self, path):
    #     """파일을 읽어 원본 라인을 저장합니다."""
    #     try:
    #         with open(path, "r", encoding="utf-8", errors='ignore') as f:
    #             self.lines = f.readlines()
    #         return True
    #     except Exception as e:
    #         print(f"Error loading log file: {e}")
    #         self.lines = []
    #         return False

    def load_file(self, path):
        """
        파일을 읽어 원본 라인을 저장합니다.
        .gz, .zip 확장자를 감지하여 압축을 해제합니다.
        """
        try:
            # 파일 확장자 확인
            _, ext = os.path.splitext(path)

            if ext == '.gz':
                with gzip.open(path, 'rt', encoding='utf-8', errors='ignore') as f:
                    self.lines = f.readlines()
            
            elif ext == '.zip':
                with zipfile.ZipFile(path, 'r') as zf:
                    file_list = zf.namelist()
                    if not file_list:
                        self.lines = ["Error: ZIP file is empty.\n"]
                        return True
                    
                    first_file_name = file_list[0]
                    
                    with TextIOWrapper(zf.open(first_file_name, 'r'), 
                                      encoding='utf-8', errors='ignore') as f:
                        self.lines = f.readlines()
                        
                    self.lines.insert(0, f"[Info: Loaded '{first_file_name}' from {os.path.basename(path)}]\n")
            
            elif ext == '.tar':
                with tarfile.open(path, 'r:*') as tf:
                    members = tf.getmembers()
                    
                    file_members = [m for m in members if m.isfile()]
                    
                    if not file_members:
                        self.lines = ["Error: TAR file contains no files.\n"]
                        return True
                        
                    first_file_member = file_members[0]
                    first_file_name = first_file_member.name
                    
                    file_obj = tf.extractfile(first_file_member)
                    if file_obj is None:
                         raise Exception(f"Failed to extract file {first_file_name} from tar.")

                    with TextIOWrapper(file_obj, 
                                      encoding='utf-8', errors='ignore') as f:
                        self.lines = f.readlines()
                        
                    self.lines.insert(0, f"[Info: Loaded '{first_file_name}' from {os.path.basename(path)}]\n")

            else:
                with open(path, "r", encoding="utf-8", errors='ignore') as f:
                    self.lines = f.readlines()
                    
            return True
        
        except Exception as e:
            # 오류 발생 시, 오류 메시지를 뷰어에 표시
            print(f"Error loading log file: {e}")
            self.lines = [
                f"Error: Failed to read file.\n",
                f"File: {path}\n",
                f"Details: {e}\n"
            ]
            # 오류 메시지를 뷰어에 보여줘야 하므로 True 반환
            return True

    def get_filtered_lines(self, or_filters, and_filters):
        """필터 규칙에 따라 원본 라인을 필터링하여 반환합니다."""
        if not or_filters and not and_filters:
            # 필터가 없으면 전체 라인을 (인덱스, 텍스트)로 반환
            return list(enumerate(self.lines))

        filtered_data = []
        for idx, line in enumerate(self.lines):
            line_text = line.rstrip("\n")
            
            # AND 조건: 필터 모두 맞아야 통과
            and_passed = True
            for f_data in and_filters:
                term = f_data["term"]
                is_case_i = f_data["is_case_i"]
                
                if is_case_i:
                    if not term.lower() in line_text.lower():
                        and_passed = False
                        break
                else:
                    if not term in line_text:
                        and_passed = False
                        break
            
            if not and_passed: continue

            or_passed = False
            # OR 조건: 필터 중 하나라도 맞으면 통과
            for f_data in or_filters:
                term = f_data["term"]
                is_case_i = f_data["is_case_i"]
                
                if is_case_i:
                    if term.lower() in line_text.lower():
                        or_passed = True
                        break
                else:
                    if term in line_text:
                        or_passed = True
                        break
            
            if or_passed:
                filtered_data.append((idx, line))
        
        return filtered_data
