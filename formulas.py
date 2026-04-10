import re
from datetime import datetime

def extract_number(text):
    """数字（37.11などの小数も対応！）を抜き出す裏方さんです"""
    # カンマを取り除いてから、数字の塊を探します（小数点があっても大丈夫です）
    match = re.search(r'\d+(?:\.\d+)?', text.replace(',', ''))
    if match:
        num_str = match.group()
        # 小数点があれば float（小数）、なければ int（整数）として扱います
        return float(num_str) if '.' in num_str else int(num_str)
    return None

def parse_japanese_date(text):
    """和暦（S, H, Rなど）や西暦を日付データに変換する裏方さんです"""
    # 例: S63.4.3 や R8.2.5 などの文字を探します
    match = re.search(r'(S|H|R|M|T|昭和|平成|令和|明治|大正)?\s*(\d+)[年\./]\s*(\d+)[月\./]\s*(\d+)[日]?', text)
    if not match:
        raise ValueError(f"日付が見つかりませんでした…: {text}")
        
    era, year_str, month_str, day_str = match.groups()
    year = int(year_str)
    month = int(month_str)
    day = int(day_str)
    
    # 和暦を西暦に変換します！
    if era in ['S', '昭和']:
        year += 1925
    elif era in ['H', '平成']:
        year += 1988
    elif era in ['R', '令和']:
        year += 2018
    elif era in ['T', '大正']:
        year += 1911
    elif era in ['M', '明治']:
        year += 1867
    elif year < 100:
        # 年号がない場合（例：63.4.3）の簡易対応です
        year += 1900 if year >= 60 else 2000

    return datetime(year, month, day)


# ==========================================
#   ここから個別の計算ルールを作ります
# ==========================================

def calc_addition(text_a, text_b):
    val_a = extract_number(text_a)
    val_b = extract_number(text_b)
    if val_a is not None and val_b is not None:
        return val_a + val_b, ""
    raise ValueError("数字が見つかりません…")

def calc_subtraction(text_a, text_b):
    val_a = extract_number(text_a)
    val_b = extract_number(text_b)
    if val_a is not None and val_b is not None:
        return val_a - val_b, ""
    raise ValueError("数字が見つかりません…")

def calc_date_diff(text_a, text_b):
    date_a = parse_japanese_date(text_a)
    date_b = parse_japanese_date(text_b)
    diff = abs((date_a - date_b).days)
    return diff, ""

def calc_service_years(text_a, text_b):
    """勤続年数を YY.MM 形式で計算します（開始月も終了月も含めます！）"""
    date_a = parse_japanese_date(text_a)
    date_b = parse_japanese_date(text_b)
    
    # 古い日付から順番になるようにします
    start = min(date_a, date_b)
    end = max(date_a, date_b)
        
    # 何ヶ月経ったかを計算します（開始月も終了月も1ヶ月として数える方式です）
    total_months = (end.year - start.year) * 12 + (end.month - start.month) + 1
    
    years = total_months // 12
    months = total_months % 12
    
    # 「37.11」のように、年と月を小数でくっつけます！
    result_val = years + (months / 100.0)
    
    # 誤差が出ないように、小数点第2位までに整えます
    result_val = round(result_val, 2)
    
    return result_val, ""

# ==========================================
#   画面のコンボボックスに渡す「メニュー表」です！
# ==========================================
AVAILABLE_FORMULAS = {
    "足し算 (対象1 ＋ 対象2)": calc_addition,
    "引き算 (対象1 － 対象2)": calc_subtraction,
    "日数の差 (対象1 ～ 対象2)": calc_date_diff,
    "勤続年数 (対象1 ～ 対象2)": calc_service_years  # ★これを追加しました！
}
