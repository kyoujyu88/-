import pypdfium2 as pdfium
import tkinter as tk
from tkinter import ttk, messagebox

# formulas.py から計算メニューと裏方さんを読み込みます
from formulas import AVAILABLE_FORMULAS, extract_number

class InteractiveCalculator:
    def __init__(self, parent, extracted_texts):
        self.window = tk.Toplevel(parent)
        self.window.title("🧮 計算と結果チェック画面")
        self.window.geometry("500x600")
        
        self.texts = extracted_texts
        self.options = [f"枠{i+1}: {text}" for i, text in enumerate(self.texts)]
        self.formula_names = list(AVAILABLE_FORMULAS.keys())

        # 画面上部のタイトル
        tk.Label(self.window, text="計算と結果チェック画面", font=("", 14, "bold")).pack(pady=10)

        # 入力フォーム用のフレーム（設計図のように左と右で揃えます）
        form_frame = tk.Frame(self.window)
        form_frame.pack(pady=10, padx=20, fill="x")

        # 【1行目】 対象1
        tk.Label(form_frame, text="対象1").grid(row=0, column=0, sticky="e", pady=8, padx=10)
        self.combo_a = ttk.Combobox(form_frame, values=self.options, width=40, state="readonly")
        self.combo_a.grid(row=0, column=1, sticky="w", pady=8)

        # 【2行目】 対象2
        tk.Label(form_frame, text="対象2").grid(row=1, column=0, sticky="e", pady=8, padx=10)
        self.combo_b = ttk.Combobox(form_frame, values=self.options, width=40, state="readonly")
        self.combo_b.grid(row=1, column=1, sticky="w", pady=8)

        # 【3行目】 計算式
        tk.Label(form_frame, text="計算式").grid(row=2, column=0, sticky="e", pady=8, padx=10)
        self.combo_formula = ttk.Combobox(form_frame, values=self.formula_names, width=40, state="readonly")
        self.combo_formula.grid(row=2, column=1, sticky="w", pady=8)

        # 【4行目】 結果（最初は空っぽにしておきます）
        tk.Label(form_frame, text="結果").grid(row=3, column=0, sticky="e", pady=8, padx=10)
        self.lbl_calc_result = tk.Label(form_frame, text="---", font=("", 12, "bold"), fg="blue")
        self.lbl_calc_result.grid(row=3, column=1, sticky="w", pady=8)

        # ここで少し線を引いて区切ります
        ttk.Separator(form_frame, orient="horizontal").grid(row=4, column=0, columnspan=2, sticky="ew", pady=15)

        # 【5行目】 チェック対象
        tk.Label(form_frame, text="チェック対象").grid(row=5, column=0, sticky="e", pady=8, padx=10)
        self.combo_compare = ttk.Combobox(form_frame, values=["（比較しない）"] + self.options, width=40, state="readonly")
        self.combo_compare.current(0)
        self.combo_compare.grid(row=5, column=1, sticky="w", pady=8)

        # 【6行目】 チェック結果
        tk.Label(form_frame, text="チェック結果").grid(row=6, column=0, sticky="e", pady=8, padx=10)
        self.lbl_check_result = tk.Label(form_frame, text="---", font=("", 12, "bold"))
        self.lbl_check_result.grid(row=6, column=1, sticky="w", pady=8)

        # 実行ボタン
        btn_frame = tk.Frame(self.window)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="計算とチェックを実行", command=self.run_calculation, bg="lightgreen", width=20, font=("", 10, "bold")).pack()

        # --- 手書きの図の下の部分（読み取ったデータ一覧） ---
        list_frame = tk.LabelFrame(self.window, text="【参考】 読み取ったデータの一覧")
        list_frame.pack(fill="both", expand=True, padx=20, pady=(10, 20))
        
        list_text = tk.Text(list_frame, height=6, state="normal", bg="#f8f9fa", font=("", 10))
        list_text.pack(fill="both", expand=True, padx=10, pady=10)
        for i, text in enumerate(self.texts):
            list_text.insert("end", f"枠{i+1} : {text}\n")
        list_text.config(state="disabled")

    def run_calculation(self):
        """実行ボタンが押された時の処理です"""
        idx_a = self.combo_a.current()
        idx_b = self.combo_b.current()
        idx_f = self.combo_formula.current()
        idx_c = self.combo_compare.current()

        # 表示をリセットします
        self.lbl_calc_result.config(text="---", fg="black")
        self.lbl_check_result.config(text="---", fg="black")

        if idx_a == -1 or idx_b == -1 or idx_f == -1:
            messagebox.showwarning("確認", "対象1、対象2、計算式をすべて選んでくださいね。")
            return

        text_a = self.texts[idx_a]
        text_b = self.texts[idx_b]
        formula_name = self.formula_names[idx_f]
        
        try:
            # formulas.py に計算をお願いします
            calc_func = AVAILABLE_FORMULAS[formula_name]
            calculated_value, _ = calc_func(text_a, text_b)
            
            # 【4行目】結果のラベルに数値を書き込みます
            self.lbl_calc_result.config(text=str(calculated_value), fg="blue")

            # 【6行目】チェック対象と答え合わせをします
            if idx_c > 0: 
                compare_text = self.texts[idx_c - 1]
                compare_val = extract_number(compare_text)
                
                if calculated_value == compare_val:
                    self.lbl_check_result.config(text="💮 一致しました！", fg="green")
                else:
                    self.lbl_check_result.config(text=f"💦 不一致 (対象の枠の値: {compare_val})", fg="red")
            else:
                self.lbl_check_result.config(text="（比較なし）", fg="gray")

        except Exception as e:
            self.lbl_calc_result.config(text="エラー", fg="red")
            self.lbl_check_result.config(text="---")
            messagebox.showerror("エラー", f"計算に失敗しました…\n{e}")

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
