import pypdfium2 as pdfium
import cv2
import numpy as np
import os
import tkinter as tk
from tkinter import messagebox # ★ 結果を表示するためにメッセージボックスを使います！

class PDFSelector:
    def __init__(self):
        self.drawing = False
        self.ix, self.iy = -1, -1
        self.rois = []
        self.display_img = None
        self.clean_img = None
        
        # 裏方さんとして必要なデータを覚えておきます
        self.pdf_h = None
        self.textpage = None
        self.scale = 1.5

    def redraw_image(self):
        """現在の枠をすべて描き直す裏方さんです"""
        self.display_img = self.clean_img.copy()
        for i, roi in enumerate(self.rois):
            rx, ry, w, h = roi
            # 枠を描きます
            cv2.rectangle(self.display_img, (rx, ry), (rx+w, ry+h), (255, 0, 0), 2)
            # 番号を描きます
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
                # 画面を描き直して、新しい枠を表示します
                self.redraw_image()

                # ==========================================
                # ★ ここが新しい機能です！ ★
                # マウスを離した瞬間、その場所の文字を読み取って表示します
                # ==========================================
                
                # 画像の座標をPDF本来の座標に変換します
                pdf_left = rx / self.scale
                pdf_right = (rx + w) / self.scale
                # 上下をひっくり返す魔法の計算式です
                pdf_top = self.pdf_h - (ry / self.scale)
                pdf_bottom = self.pdf_h - ((ry + h) / self.scale)
                
                # 文字を抽出します…！
                if self.textpage:
                    text = self.textpage.get_text_bounded(left=pdf_left, bottom=pdf_bottom, right=pdf_right, top=pdf_top)
                    clean_text = text.strip()
                    
                    # 読み取った文字を、小さなメッセージボックスで画面の真ん中にポンッと表示します
                    if clean_text:
                        messagebox.showinfo("✨ 読み取りプレビュー", f"枠{len(self.rois)} の読み取り結果はこちらです！\n\n[{clean_text}]")
                    else:
                        messagebox.showwarning("✨ 読み取りプレビュー", f"枠{len(self.rois)} には、文字が見つかりませんでした…っ")

    def select(self, pdf_path, existing_rois=None):
        """画面を開く関数です"""
        # 前の枠があれば引き継ぎます
        if existing_rois:
            self.rois = existing_rois.copy()
        else:
            self.rois = []
            
        if not os.path.exists(pdf_path):
            return []

        # --- ここでPDFを開いて、裏方さん用のデータをセットします ---
        pdf = pdfium.PdfDocument(pdf_path)
        page = pdf[0]
        # PDF本来のサイズ（高さ）を覚えておきます
        self.pdf_h = page.get_size()[1]
        # 文字データの層を抜き出して、いつでも読めるように準備しておきます！
        self.textpage = page.get_textpage()
        
        # 画面に表示するために画像化します
        bitmap = page.render(scale=self.scale, rev_byteorder=False)
        pil_image = bitmap.to_pil()
        
        self.clean_img = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        
        cv2.namedWindow("PDF Selector")
        cv2.setMouseCallback("PDF Selector", self.mouse_callback)
        
        # 最初から枠を描画しておきます
        self.redraw_image()
        
        print("マウスで枠を囲んでくださいね。終わったら「Enter」です。")
        print("間違えた時は「c」を押すと、一つ前の枠を取り消せます！")
        
        while True:
            key = cv2.waitKey(1) & 0xFF
            if key == 13: # Enterキー
                break
            elif key == ord('c'):
                # cを押したら、リストの一番最後を消して描き直します
                if self.rois:
                    self.rois.pop()
                    self.redraw_image()
                    print("一つ前の枠を取り消しました！")
                
        cv2.destroyAllWindows()
        return self.rois
