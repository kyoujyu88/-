import pypdfium2 as pdfium
import tkinter as tk
from tkinter import ttk, messagebox

# ★ 新しく作った計算式のファイルから、メニュー表と裏方さんを呼んできます！
from formulas import AVAILABLE_FORMULAS, extract_number

class InteractiveCalculator:
    def __init__(self, parent, extracted_texts):
        self.window = tk.Toplevel(parent)
        self.window.title("🧮 計算と答え合わせチェック")
        self.window.geometry("450x500")
        
        self.texts = extracted_texts
        self.options = [f"枠{i+1}: {text}" for i, text in enumerate(self.texts)]
        
        # ★ 計算式のリスト（コンボボックスの中身）を formulas.py から自動でもらってきます！
        self.formula_names = list(AVAILABLE_FORMULAS.keys())

        tk.Label(self.window, text="📝 自由に組み合わせてチェックできます", font=("", 12, "bold")).pack(pady=15)

        tk.Label(self.window, text="【 対象 1 】").pack()
        self.combo_a = ttk.Combobox(self.window, values=self.options, width=40, state="readonly")
        self.combo_a.pack(pady=5)

        tk.Label(self.window, text="【 計算式 】").pack()
        self.combo_formula = ttk.Combobox(self.window, values=self.formula_names, width=40, state="readonly")
        self.combo_formula.pack(pady=5)

        tk.Label(self.window, text="【 対象 2 】").pack()
        self.combo_b = ttk.Combobox(self.window, values=self.options, width=40, state="readonly")
        self.combo_b.pack(pady=5)

        tk.Label(self.window, text="【 答え合わせする枠 (比較対象) 】", fg="blue").pack(pady=(15, 0))
        self.combo_compare = ttk.Combobox(self.window, values=["比較しない（計算結果だけ見る）"] + self.options, width=40, state="readonly")
        self.combo_compare.current(0)
        self.combo_compare.pack(pady=5)

        tk.Button(self.window, text="✨ 計算してチェックする ✨", command=self.run_calculation, width=25, height=2, bg="lightgreen").pack(pady=20)

        self.lbl_result = tk.Label(self.window, text="", font=("", 11), fg="black", justify="left")
        self.lbl_result.pack(pady=5)

    def run_calculation(self):
        idx_a = self.combo_a.current()
        idx_b = self.combo_b.current()
        idx_f = self.combo_formula.current()
        idx_c = self.combo_compare.current()

        if idx_a == -1 or idx_b == -1 or idx_f == -1:
            messagebox.showwarning("確認", "対象1、計算式、対象2 をすべて選んでくださいね。")
            return

        text_a = self.texts[idx_a]
        text_b = self.texts[idx_b]
        formula_name = self.formula_names[idx_f]
        
        try:
            # ★ formulas.py の中から、選ばれた計算式の関数を呼び出してお任せします！
            calc_func = AVAILABLE_FORMULAS[formula_name]
            calculated_value, result_msg = calc_func(text_a, text_b)

            # --- 答え合わせ（比較）のチェックです ---
            if idx_c > 0: 
                compare_text = self.texts[idx_c - 1]
                compare_val = extract_number(compare_text)
                
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
            self.lbl_result.config(text=f"あわわ…っ（計算エラー）\n{e}", fg="red")

def open_calculator(pdf_path, rois, parent_root):
    try:
        pdf = pdfium.PdfDocument(pdf_path)
        page = pdf[0]
        pdf_w, pdf_h = page.get_size()
        textpage = page.get_textpage()
        
        scale = 1.5 
        extracted_texts = []
        
        for roi in rois:
            x, y, w, h = roi
            pdf_left = x / scale
            pdf_right = (x + w) / scale
            pdf_top = pdf_h - (y / scale)
            pdf_bottom = pdf_h - ((y + h) / scale)
            
            text = textpage.get_text_bounded(left=pdf_left, bottom=pdf_bottom, right=pdf_right, top=pdf_top)
            extracted_texts.append(text.strip())
        
        InteractiveCalculator(parent_root, extracted_texts)
        return True, "計算画面を開きました！"
        
    except Exception as e:
        return False, f"読み取り中にエラーが起きました…\n{e}"
