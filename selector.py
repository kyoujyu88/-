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
        
        # 新しく追加するプレビュー画面のためのメモ帳です
        self.info_window = None
        self.lbl_preview = None

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

                # --- 読み取ってリアルタイムで表示します！ ---
                pdf_left = rx / self.scale
                pdf_right = (rx + w) / self.scale
                pdf_top = self.pdf_h - (ry / self.scale)
                pdf_bottom = self.pdf_h - ((ry + h) / self.scale)
                
                if self.textpage:
                    text = self.textpage.get_text_bounded(left=pdf_left, bottom=pdf_bottom, right=pdf_right, top=pdf_top)
                    clean_text = text.strip()
                    
                    # 邪魔なOKボタンの代わりに、プレビュー画面の文字をパッと書き換えます！
                    if self.lbl_preview:
                        if clean_text:
                            self.lbl_preview.config(text=f"枠{len(self.rois)} :  {clean_text}", fg="blue")
                        else:
                            self.lbl_preview.config(text=f"枠{len(self.rois)} :  (文字が見つかりません…)", fg="red")

    def select(self, pdf_path, existing_rois=None):
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
        
        # ==========================================
        # ★ 新機能：使い方＆プレビュー専用の画面を開きます！
        # ==========================================
        self.info_window = tk.Toplevel()
        self.info_window.title("使い方 ＆ プレビュー")
        self.info_window.geometry("380x200")
        # OpenCVの裏に隠れないように、常に一番手前に表示させる魔法です
        self.info_window.attributes("-topmost", True)
        
        # 使い方の表示
        tk.Label(self.info_window, text="【 使い方 】", font=("MS UI Gothic", 12, "bold")).pack(pady=(10, 5))
        instructions = "1. マウスでドラッグして枠を囲む\n2. 「c」キーで一つ前の枠を消す\n3. 「Enter」キーで決定して完了する"
        tk.Label(self.info_window, text=instructions, justify="left", font=("MS UI Gothic", 10)).pack()
        
        # プレビューの表示
        tk.Label(self.info_window, text="【 読み取りプレビュー 】", font=("MS UI Gothic", 12, "bold"), fg="blue").pack(pady=(15, 5))
        self.lbl_preview = tk.Label(self.info_window, text="(枠を囲むとここに結果がすぐ出ます)", font=("MS UI Gothic", 14, "bold"))
        self.lbl_preview.pack()

        # ==========================================

        cv2.namedWindow("PDF Selector")
        cv2.setMouseCallback("PDF Selector", self.mouse_callback)
        self.redraw_image()
        
        while True:
            # 待ち時間を10ミリ秒にしてキーボードを見張ります
            key = cv2.waitKey(10) & 0xFF
            if key == 13: # Enterキー
                break
            elif key == ord('c'):
                if self.rois:
                    self.rois.pop()
                    self.redraw_image()
                    # cキーで消した時も、画面にメッセージを出します
                    if self.lbl_preview:
                        self.lbl_preview.config(text="一つ前の枠を取り消しました！", fg="gray")
            
            # ★ OpenCVの画面を開きながら、プレビュー画面も同時に動かし続けます
            try:
                self.info_window.update()
            except tk.TclError:
                # ユーザーがプレビュー画面の「×」ボタンを押してしまった時は無視します
                pass
                
        cv2.destroyAllWindows()
        
        # 枠選びが終わったら、プレビュー画面も一緒に閉じます
        try:
            self.info_window.destroy()
        except:
            pass
            
        return self.rois
