import os
import re


def clean_cell_value(value):
    if not isinstance(value, str):
        return value
    # 엑셀이 허용하지 않는 제어 문자 제거
    cleaned = re.sub(r"[\x00-\x1F\x7F]", "", value)
    return cleaned


def make_unique_filename(filepath):
    if not os.path.exists(filepath):
        return filepath

    base, ext = os.path.splitext(filepath)
    i = 1
    while True:
        new_filepath = f"{base}({i}){ext}"
        if not os.path.exists(new_filepath):
            return new_filepath
        i += 1
