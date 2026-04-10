import tkinter as tk
from tkinter import filedialog, messagebox
import os

from selector import PDFSelector
from calculator import open_calculator

class DangoDocumentScanner:
    def __init__(self, root):
        self.root = root
        self.root.title("書類読み取りシステム")
        self.root.geometry("400x320")
        
        self.pdf_path = ""
        self.rois = []
        
        title_label = tk.Label(root, text="📄 自動計算システム", font=("", 16, "bold"))
        title_label.pack(pady=20)
        
        self.btn_select = tk.Button(root, text="1. PDFファイルを選ぶ", command=self.select_pdf, width=25, height=2)
        self.btn_select.pack(pady=5)
        
        self.lbl_path = tk.Label(root, text="ファイルが選ばれていません…", fg="gray")
        self.lbl_path.pack(pady=(0, 10))
        
        self.btn_roi = tk.Button(root, text="2. 読み取り範囲を設定する", command=self.set_rois, width=25, height=2, state=tk.DISABLED)
        self.btn_roi.pack(pady=5)
        
        self.btn_calc = tk.Button(root, text="3. 読み取って計算する！", command=self.calculate_data, width=25, height=2, state=tk.DISABLED)
        self.btn_calc.pack(pady=5)

    def select_pdf(self):
        filepath = filedialog.askopenfilename(
            title="PDFファイルを選んでくださいね",
            filetypes=[("PDFファイル", "*.pdf")]
        )
        if filepath:
            self.pdf_path = filepath
            filename = os.path.basename(filepath)
            self.lbl_path.config(text=f"選択中: {filename}", fg="blue")
            
            self.btn_roi.config(state=tk.NORMAL)
            self.rois = []
            self.btn_calc.config(state=tk.DISABLED)

    def set_rois(self):
        self.root.withdraw() 
        try:
            selector = PDFSelector()
            # ★ 引数に「今の自己の枠（self.rois）」を渡すように変更しました！
            selected_rois = selector.select(self.pdf_path, self.rois)
            
            self.rois = selected_rois
            
            # 枠が1つ以上あれば計算ボタンを押せるようにします
            if len(self.rois) > 0:
                messagebox.showinfo("成功です！", f"{len(self.rois)} 箇所の範囲を覚えました！")
                self.btn_calc.config(state=tk.NORMAL)
            else:
                messagebox.showwarning("お知らせ", "範囲が選ばれていません…")
                self.btn_calc.config(state=tk.DISABLED)
                
        except Exception as e:
            messagebox.showerror("えれぇ…っ（エラー）", f"画面が開けませんでした…\n{e}")
        self.root.deiconify() 

    def calculate_data(self):
        if not self.pdf_path or not self.rois:
            return
            
        success, result_text = open_calculator(self.pdf_path, self.rois, self.root)
        
        if not success:
            messagebox.showerror("えれぇ…っ（エラー）", result_text)

if __name__ == "__main__":
    root = tk.Tk()
    app = DangoDocumentScanner(root)
    root.mainloop()
