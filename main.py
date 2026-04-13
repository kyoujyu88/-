import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import os

# ★ 作った部品たちを読み込みます
from selector import PDFSelector
from calculator import open_calculator
from config_manager import ConfigManager  # ← 新しい裏方さんです！

class DangoDocumentScanner:
    def __init__(self, root):
        self.root = root
        self.root.title("書類読み取りシステム")
        self.root.geometry("450x500")
        
        self.pdf_path = ""
        self.rois = []
        
        # ★ 設定の管理は、新しく作った裏方さんにお任せします！
        self.config_manager = ConfigManager()
        
        title_label = tk.Label(root, text="📄 書類自動解析システム", font=("MS UI Gothic", 16, "bold"))
        title_label.pack(pady=20)
        
        # --- 基本操作エリア ---
        frame_basic = tk.LabelFrame(root, text="1. 基本操作", padx=10, pady=10)
        frame_basic.pack(pady=10, fill="x", padx=20)

        self.btn_select = tk.Button(frame_basic, text="PDFファイルを選ぶ", command=self.select_pdf, width=30)
        self.btn_select.pack(pady=5)
        
        self.lbl_path = tk.Label(frame_basic, text="ファイル未選択", fg="gray")
        self.lbl_path.pack()

        self.btn_roi = tk.Button(frame_basic, text="読み取り範囲を設定（マウス）", command=self.set_rois, width=30, state=tk.DISABLED)
        self.btn_roi.pack(pady=5)

        # --- 保存・読込エリア ---
        frame_config = tk.LabelFrame(root, text="2. 設定の保存・読込", padx=10, pady=10)
        frame_config.pack(pady=10, fill="x", padx=20)

        self.btn_save = tk.Button(frame_config, text="今の範囲に名前をつけて保存", command=self.save_ranges, width=30, state=tk.DISABLED)
        self.btn_save.pack(pady=5)

        self.btn_load = tk.Button(frame_config, text="保存済みの設定を読み込む", command=self.load_ranges, width=30)
        self.btn_load.pack(pady=5)

        # --- 実行エリア ---
        tk.Button(root, text="✨ 読み取って計算する！ ✨", command=self.calculate_data, 
                  width=35, height=2, bg="lightcyan", font=("", 10, "bold")).pack(pady=20)

    def select_pdf(self):
        filepath = filedialog.askopenfilename(title="PDF選択", filetypes=[("PDF", "*.pdf")])
        if filepath:
            self.pdf_path = filepath
            self.lbl_path.config(text=f"選択中: {os.path.basename(filepath)}", fg="blue")
            self.btn_roi.config(state=tk.NORMAL)

    def set_rois(self):
        self.root.withdraw() 
        try:
            selector = PDFSelector()
            self.rois = selector.select(self.pdf_path, self.rois)
            if self.rois:
                self.btn_save.config(state=tk.NORMAL)
                messagebox.showinfo("完了", f"{len(self.rois)}箇所の範囲を保持しました。")
        except Exception as e:
            messagebox.showerror("エラー", f"失敗しました…: {e}")
        self.root.deiconify() 

    def save_ranges(self):
        """今の範囲に名前をつけて保存します"""
        name = simpledialog.askstring("設定の保存", "この範囲設定に名前をつけてください\n(例: 請求書フォーマットA)")
        if not name: return

        # ★ 保存の処理は config_manager にお願いするだけです！
        self.config_manager.save(name, self.rois)
        messagebox.showinfo("成功", f"「{name}」として保存しました！")

    def load_ranges(self):
        """保存された名前の一覧から選んで読み込みます"""
        # ★ ファイルを読み込む処理も config_manager にお願いします！
        data = self.config_manager.load_all()
        
        if not data:
            messagebox.showwarning("お知らせ", "保存された設定がまだありません…")
            return

        load_win = tk.Toplevel(self.root)
        load_win.title("設定の読み込み")
        load_win.geometry("300x250")
        
        tk.Label(load_win, text="読み込む設定を選んでください", pady=10).pack()
        
        listbox = tk.Listbox(load_win)
        listbox.pack(fill="both", expand=True, padx=20)
        for name in data.keys():
            listbox.insert("end", name)

        def on_select():
            selected = listbox.curselection()
            if selected:
                name = listbox.get(selected[0])
                self.rois = data[name]
                messagebox.showinfo("読み込み完了", f"「{name}」の設定（{len(self.rois)}箇所）を読み込みました！")
                self.btn_save.config(state=tk.NORMAL)
                load_win.destroy()

        tk.Button(load_win, text="読み込む", command=on_select, pady=5).pack(pady=10)

    def calculate_data(self):
        if not self.pdf_path:
            messagebox.showwarning("確認", "まずはPDFファイルを選んでくださいね。")
            return
        if not self.rois:
            messagebox.showwarning("確認", "読み取り範囲が設定されていません…\nマウスで指定するか、保存した設定を読み込んでください。")
            return
            
        success, result_text = open_calculator(self.pdf_path, self.rois, self.root)
        if not success:
            messagebox.showerror("エラー", result_text)

if __name__ == "__main__":
    root = tk.Tk()
    app = DangoDocumentScanner(root)
    root.mainloop()
