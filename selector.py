import pypdfium2 as pdfium
import cv2
import numpy as np
import os
import tkinter as tk

class PDFSelector:
    def __init__(self):
        self.drawing = False
        self.ix, self.iy = -1, -1
        self.rois = []
        self.display_img = None
        self.clean_img = None
        
        self.pdf_h = None
        self.textpage = None
        self.scale = 1.5
        
        self.info_window = None
        self.lbl_preview = None
        # ★ 脱出するためのフラグです
        self.is_running = True

    def on_close_window(self):
        """プレビュー画面の「×」が押された時に呼ばれる関数です"""
        self.is_running = False

    def redraw_image(self):
        """現在の枠をすべて描き直す裏方さんです"""
        self.display_img = self.clean_img.copy()
        for i, roi in enumerate(self.rois):
            rx, ry, w, h = roi
            cv2.rectangle(self.display_img, (rx, ry), (rx+w, ry+h), (255, 0, 0), 2)
            cv2.putText(self.display_img, str(i+1), (rx, ry - 5), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
        cv2.imshow("PDF Selector", self.display_img)

    def mouse_callback(self, event, x, y, flags, param):
        """マウスの動きを見張る関数です"""
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            self.ix, self.iy = x, y
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drawing:
                temp_img = self.display_img.copy()
                cv2.rectangle(temp_img, (self.ix, self.iy), (x, y), (0, 255, 0), 2)
                cv2.imshow("PDF Selector", temp_img)
        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False
            w = abs(x - self.ix)
            h = abs(y - self.iy)
            rx = min(self.ix, x)
            ry = min(self.iy, y)
            if w > 5 and h > 5:
                self.rois.append((rx, ry, w, h))
                self.redraw_image()

                pdf_left = rx / self.scale
                pdf_right = (rx + w) / self.scale
                pdf_top = self.pdf_h - (ry / self.scale)
                pdf_bottom = self.pdf_h - ((ry + h) / self.scale)
                
                if self.textpage:
                    text = self.textpage.get_text_bounded(left=pdf_left, bottom=pdf_bottom, right=pdf_right, top=pdf_top)
                    clean_text = text.strip()
                    
                    if self.lbl_preview and self.lbl_preview.winfo_exists():
                        if clean_text:
                            self.lbl_preview.config(text=f"枠{len(self.rois)} :  {clean_text}", fg="blue")
                        else:
                            self.lbl_preview.config(text=f"枠{len(self.rois)} :  (文字が見つかりません…)", fg="red")

    def select(self, pdf_path, existing_rois=None):
        self.is_running = True # 実行フラグをリセットします
        
        if existing_rois:
            self.rois = existing_rois.copy()
        else:
            self.rois = []
            
        if not os.path.exists(pdf_path):
            return []

        pdf = pdfium.PdfDocument(pdf_path)
        page = pdf[0]
        self.pdf_h = page.get_size()[1]
        self.textpage = page.get_textpage()
        
        bitmap = page.render(scale=self.scale, rev_byteorder=False)
        pil_image = bitmap.to_pil()
        self.clean_img = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        
        # --- 使い方画面の作成 ---
        self.info_window = tk.Toplevel()
        self.info_window.title("使い方 ＆ プレビュー")
        self.info_window.geometry("380x200")
        self.info_window.attributes("-topmost", True)
        
        # ★ ここで「×」ボタンが押された時の処理を登録します！
        self.info_window.protocol("WM_DELETE_WINDOW", self.on_close_window)
        
        tk.Label(self.info_window, text="【 使い方 】", font=("MS UI Gothic", 12, "bold")).pack(pady=(10, 5))
        instructions = "1. マウスでドラッグして枠を囲む\n2. 「c」キーで一つ前の枠を消す\n3. 「Enter」キーで決定して完了する"
        tk.Label(self.info_window, text=instructions, justify="left", font=("MS UI Gothic", 10)).pack()
        
        tk.Label(self.info_window, text="【 読み取りプレビュー 】", font=("MS UI Gothic", 12, "bold"), fg="blue").pack(pady=(15, 5))
        self.lbl_preview = tk.Label(self.info_window, text="(枠を囲むとここに結果がすぐ出ます)", font=("MS UI Gothic", 14, "bold"))
        self.lbl_preview.pack()

        cv2.namedWindow("PDF Selector")
        cv2.setMouseCallback("PDF Selector", self.mouse_callback)
        self.redraw_image()
        
        while self.is_running:
            key = cv2.waitKey(10) & 0xFF
            
            # Enterキー
            if key == 13: 
                break
                
            # cキー（取り消し）
            elif key == ord('c'):
                if self.rois:
                    self.rois.pop()
                    self.redraw_image()
                    if self.lbl_preview and self.lbl_preview.winfo_exists():
                        self.lbl_preview.config(text="一つ前の枠を取り消しました！", fg="gray")
            
            # ★ OpenCVの画面が「×」で閉じられたかチェックします
            if cv2.getWindowProperty("PDF Selector", cv2.WND_PROP_VISIBLE) < 1:
                break
            
            try:
                self.info_window.update()
            except tk.TclError:
                # プレビュー画面が破壊された場合はループを抜けます
                break
                
        # 全ての画面を後片付けします
        cv2.destroyAllWindows()
        try:
            if self.info_window.winfo_exists():
                self.info_window.destroy()
        except:
            pass
            
        return self.rois
