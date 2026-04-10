import pypdfium2 as pdfium
import re
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

class InteractiveCalculator:
    def __init__(self, parent, extracted_texts):
        # メイン画面の上に、計算専用の新しいウィンドウを開きます
        self.window = tk.Toplevel(parent)
        self.window.title("🧮 計算と答え合わせチェック")
        self.window.geometry("450x500")
        
        self.texts = extracted_texts
        
        # コンボボックスに表示する選択肢を作ります（例：「枠1: 50,000」）
        self.options = [f"枠{i+1}: {text}" for i, text in enumerate(self.texts)]
        
        # 別の機能で作ったと想定した「計算式」のリストです
        self.formulas = ["足し算 (対象1 ＋ 対象2)", "引き算 (対象1 － 対象2)", "日数の差 (対象1 ～ 対象2)"]

        # --- 画面の部品を作って並べていきます ---
        tk.Label(self.window, text="📝 自由に組み合わせてチェックできます", font=("", 12, "bold")).pack(pady=15)

        # 対象1
        tk.Label(self.window, text="【 対象 1 】").pack()
        self.combo_a = ttk.Combobox(self.window, values=self.options, width=40, state="readonly")
        self.combo_a.pack(pady=5)

        # 計算式
        tk.Label(self.window, text="【 計算式 】").pack()
        self.combo_formula = ttk.Combobox(self.window, values=self.formulas, width=40, state="readonly")
        self.combo_formula.pack(pady=5)

        # 対象2
        tk.Label(self.window, text="【 対象 2 】").pack()
        self.combo_b = ttk.Combobox(self.window, values=self.options, width=40, state="readonly")
        self.combo_b.pack(pady=5)

        # 比較対象（答え合わせ用）
        tk.Label(self.window, text="【 答え合わせする枠 (比較対象) 】", fg="blue").pack(pady=(15, 0))
        self.combo_compare = ttk.Combobox(self.window, values=["比較しない（計算結果だけ見る）"] + self.options, width=40, state="readonly")
        self.combo_compare.current(0) # 最初は「比較しない」を選んでおきます
        self.combo_compare.pack(pady=5)

        # 実行ボタン
        tk.Button(self.window, text="✨ 計算してチェックする ✨", command=self.run_calculation, width=25, height=2, bg="lightgreen").pack(pady=20)

        # 結果表示エリア
        self.lbl_result = tk.Label(self.window, text="", font=("", 11), fg="black", justify="left")
        self.lbl_result.pack(pady=5)

    def extract_number(self, text):
        """文字から数字だけを抜き出す裏方さんです"""
        nums = re.findall(r'\d+', text.replace(',', ''))
        if nums:
            return int("".join(nums))
        return None

    def run_calculation(self):
        """実行ボタンが押された時の処理です"""
        idx_a = self.combo_a.current()
        idx_b = self.combo_b.current()
        idx_f = self.combo_formula.current()
        idx_c = self.combo_compare.current()

        if idx_a == -1 or idx_b == -1 or idx_f == -1:
            messagebox.showwarning("確認", "対象1、計算式、対象2 をすべて選んでくださいね。")
            return

        text_a = self.texts[idx_a]
        text_b = self.texts[idx_b]
        formula_name = self.formulas[idx_f]
        
        calculated_value = None
        result_msg = ""

        try:
            # --- 選ばれた計算式ごとに処理を分けます ---
            if formula_name == "足し算 (対象1 ＋ 対象2)":
                val_a = self.extract_number(text_a)
                val_b = self.extract_number(text_b)
                if val_a is not None and val_b is not None:
                    calculated_value = val_a + val_b
                    result_msg = f"計算結果: {val_a} ＋ {val_b} ＝ {calculated_value}\n"
                else:
                    raise ValueError("数字が見つかりませんでした…")

            elif formula_name == "引き算 (対象1 － 対象2)":
                val_a = self.extract_number(text_a)
                val_b = self.extract_number(text_b)
                if val_a is not None and val_b is not None:
                    calculated_value = val_a - val_b
                    result_msg = f"計算結果: {val_a} － {val_b} ＝ {calculated_value}\n"
                else:
                    raise ValueError("数字が見つかりませんでした…")

            elif formula_name == "日数の差 (対象1 ～ 対象2)":
                nums_a = re.findall(r'\d+', text_a)
                nums_b = re.findall(r'\d+', text_b)
                if len(nums_a) >= 3 and len(nums_b) >= 3:
                    date_a = datetime(int(nums_a[0]), int(nums_a[1]), int(nums_a[2]))
                    date_b = datetime(int(nums_b[0]), int(nums_b[1]), int(nums_b[2]))
                    calculated_value = abs((date_a - date_b).days)
                    result_msg = f"計算結果: {text_a} と {text_b} の差は {calculated_value} 日\n"
                else:
                     raise ValueError("正しい日付が見つかりませんでした…")

            # --- ここから、問題ないか（答え合わせ）のチェックです ---
            if idx_c > 0: # 「比較しない」以外が選ばれている時
                compare_text = self.texts[idx_c - 1]
                compare_val = self.extract_number(compare_text)
                
                result_msg += "-" * 30 + "\n"
                result_msg += f"比較する枠の値: {compare_val}\n"
                
                if calculated_value == compare_val:
                    result_msg += "💮 【結果】 ピッタリ一致しました！ 問題ありません！"
                    self.lbl_result.config(fg="green")
                else:
                    result_msg += "💦 【結果】 ズレています…！ 確認が必要です。"
                    self.lbl_result.config(fg="red")
            else:
                self.lbl_result.config(fg="black")

            self.lbl_result.config(text=result_msg)

        except Exception as e:
            self.lbl_result.config(text=f"えれぇ…っ（計算エラー）\n{e}", fg="red")


def open_calculator(pdf_path, rois, parent_root):
    """メイン画面から呼ばれる、PDFを読み取ってウィンドウを開く関数です"""
    try:
        pdf = pdfium.PdfDocument(pdf_path)
        page = pdf[0]
        pdf_w, pdf_h = page.get_size()
        textpage = page.get_textpage()
        
        scale = 1.5 
        extracted_texts = []
        
        # まずは裏側で、枠の文字を全部読み取っておきます
        for roi in rois:
            x, y, w, h = roi
            pdf_left = x / scale
            pdf_right = (x + w) / scale
            pdf_top = pdf_h - (y / scale)
            pdf_bottom = pdf_h - ((y + h) / scale)
            
            text = textpage.get_text_bounded(left=pdf_left, bottom=pdf_bottom, right=pdf_right, top=pdf_top)
            extracted_texts.append(text.strip())
        
        # 読み取った文字を渡して、計算専用ウィンドウを立ち上げます！
        InteractiveCalculator(parent_root, extracted_texts)
        return True, "計算画面を開きました！"
        
    except Exception as e:
        return False, f"読み取り中にエラーが起きました…\n{e}"
