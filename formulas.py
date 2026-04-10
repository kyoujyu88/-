import re
from datetime import datetime

def extract_number(text):
    """文字から数字だけを抜き出す共通の裏方さんです"""
    nums = re.findall(r'\d+', text.replace(',', ''))
    if nums:
        return int("".join(nums))
    return None

# ==========================================
#   ここから個別の計算ルールを作ります
# ==========================================

def calc_addition(text_a, text_b):
    val_a = extract_number(text_a)
    val_b = extract_number(text_b)
    if val_a is not None and val_b is not None:
        return val_a + val_b, f"計算結果: {val_a} ＋ {val_b} ＝ {val_a + val_b}\n"
    raise ValueError("数字が見つかりませんでした…")

def calc_subtraction(text_a, text_b):
    val_a = extract_number(text_a)
    val_b = extract_number(text_b)
    if val_a is not None and val_b is not None:
        return val_a - val_b, f"計算結果: {val_a} － {val_b} ＝ {val_a - val_b}\n"
    raise ValueError("数字が見つかりませんでした…")

def calc_date_diff(text_a, text_b):
    nums_a = re.findall(r'\d+', text_a)
    nums_b = re.findall(r'\d+', text_b)
    if len(nums_a) >= 3 and len(nums_b) >= 3:
        date_a = datetime(int(nums_a[0]), int(nums_a[1]), int(nums_a[2]))
        date_b = datetime(int(nums_b[0]), int(nums_b[1]), int(nums_b[2]))
        diff = abs((date_a - date_b).days)
        return diff, f"計算結果: {text_a} と {text_b} の差は {diff} 日\n"
    raise ValueError("正しい日付が見つかりませんでした…")

# ==========================================
#   画面のコンボボックスに渡す「メニュー表」です！
# ==========================================
AVAILABLE_FORMULAS = {
    "足し算 (対象1 ＋ 対象2)": calc_addition,
    "引き算 (対象1 － 対象2)": calc_subtraction,
    "日数の差 (対象1 ～ 対象2)": calc_date_diff
}
