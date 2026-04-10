import pypdfium2 as pdfium
import tkinter as tk
from tkinter import ttk, messagebox

# formulas.py から計算メニューと裏方さんを読み込みます
from formulas import AVAILABLE_FORMULAS, extract_number

class InteractiveCalculator:
    def __init__(self, parent, extracted_texts):
        self.window = tk.Toplevel(parent)
        self.window.title("🧮 一括計算と結果チェック画面")
        
        # 表がしっかり入るように、画面の「横幅」を広くします！
        self.window.geometry("950x400")
        
        self.texts = extracted_texts
        self.options = [f"枠{i+1}: {text}" for i, text in enumerate(self.texts)]
        self.formula_names = list(AVAILABLE_FORMULAS.keys())

        tk.Label(self.window, text="複数の計算を一度に設定して、一括でチェックできます！", font=("MS UI Gothic", 14, "bold")).pack(pady=15)

        # 表のようなレイアウトを作るためのフレームです
        table_frame = tk.Frame(self.window)
        table_frame.pack(pady=5, padx=10, fill="x")

        # --- 表の見出しを作ります ---
        headers = ["対象1", "計算式", "対象2", "計算結果", "チェック対象", "チェック結果"]
        for col, text in enumerate(headers):
            tk.Label(table_frame, text=text, font=("MS UI Gothic", 10, "bold")).grid(row=0, column=col, padx=5, pady=5)

        # 複数行の部品（コンボボックスなど）を覚えておくためのリストです
        self.row_widgets = []
        
        # ひとまず5行分の入力欄を作りますね！（数字を変えれば何行でも増やせます）
        NUM_ROWS = 5 

        for i in range(NUM_ROWS):
            # 1. 対象1
            combo_a = ttk.Combobox(table_frame, values=["（なし）"] + self.options, width=15, state="readonly")
            combo_a.current(0) # 最初は「（なし）」にしておきます
            combo_a.grid(row=i+1, column=0, padx=5, pady=5)

            # 2. 計算式
            combo_f = ttk.Combobox(table_frame, values=["（なし）"] + self.formula_names, width=22, state="readonly")
            combo_f.current(0)
            combo_f.grid(row=i+1, column=1, padx=5, pady=5)

            # 3. 対象2
            combo_b = ttk.Combobox(table_frame, values=["（なし）"] + self.options, width=15, state="readonly")
            combo_b.current(0)
            combo_b.grid(row=i+1, column=2, padx=5, pady=5)

            # 4. 計算結果
            lbl_calc = tk.Label(table_frame, text="---", width=12, fg="blue", font=("MS UI Gothic", 11, "bold"))
            lbl_calc.grid(row=i+1, column=3, padx=5, pady=5)

            # 5. チェック対象
            combo_c = ttk.Combobox(table_frame, values=["（比較しない）"] + self.options, width=15, state="readonly")
            combo_c.current(0)
            combo_c.grid(row=i+1, column=4, padx=5, pady=5)

            # 6. チェック結果
            lbl_chk = tk.Label(table_frame, text="---", width=20, font=("MS UI Gothic", 11, "bold"))
            lbl_chk.grid(row=i+1, column=5, padx=5, pady=5)

            # 1行分の部品をセットにして、リストに保存しておきます
            self.row_widgets.append({
                'a': combo_a, 'f': combo_f, 'b': combo_b,
                'calc_res': lbl_calc, 'comp': combo_c, 'chk_res': lbl_chk
            })

        # 一括実行ボタン
        tk.Button(self.window, text="✨ 一括で計算とチェックを実行 ✨", command=self.run_calculation, bg="lightgreen", width=35, font=("MS UI Gothic", 11, "bold")).pack(pady=20)

    def run_calculation(self):
        """実行ボタンが押された時、全行を一気に処理します！"""
        for row in self.row_widgets:
            idx_a = row['a'].current()
            idx_f = row['f'].current()
            idx_b = row['b'].current()
            idx_c = row['comp'].current()

            # まず、前の結果の表示をリセットします
            row['calc_res'].config(text="---", fg="black")
            row['chk_res'].config(text="---", fg="black")

            # 「（なし）」が選ばれている行は、計算せずに飛ばします
            if idx_a == 0 or idx_b == 0 or idx_f == 0:
                continue

            # リストの0番目に「（なし）」を追加したので、実際のテキストを取り出す時は -1 します
            text_a = self.texts[idx_a - 1]
            text_b = self.texts[idx_b - 1]
            formula_name = self.formula_names[idx_f - 1]
            
            try:
                # formulas.py に計算をお任せします
                calc_func = AVAILABLE_FORMULAS[formula_name]
                calculated_value, _ = calc_func(text_a, text_b)
                
                # 計算結果を表示します
                row['calc_res'].config(text=str(calculated_value), fg="blue")

                # 答え合わせ（比較）をします
                if idx_c > 0: 
                    compare_text = self.texts[idx_c - 1]
                    compare_val = extract_number(compare_text)
                    
                    if calculated_value == compare_val:
                        row['chk_res'].config(text="✅ 一致！", fg="green")
                    else:
                        row['chk_res'].config(text=f"❌ ズレ ({compare_val})", fg="red")
                else:
                    row['chk_res'].config(text="❓ (比較なし)", fg="gray")

            except Exception:
                row['calc_res'].config(text="エラー", fg="red")
                row['chk_res'].config(text="---")

def open_calculator(pdf_path, rois, parent_root):
    """メイン画面から呼ばれる、PDFを読み取ってウィンドウを開く関数です"""
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
