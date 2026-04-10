import pypdfium2 as pdfium
import cv2
import numpy as np
import os

class PDFSelector:
    def __init__(self):
        self.drawing = False
        self.ix, self.iy = -1, -1
        self.rois = []
        self.display_img = None
        self.clean_img = None

    def redraw_image(self):
        """現在の枠をすべて描き直す裏方さんです！"""
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
                # 新しい枠が追加されたので、画面を描き直します
                self.redraw_image()

    def select(self, pdf_path, existing_rois=None):
        """画面を開く関数です。前に選んだ枠があれば受け取ります！"""
        # ★ 前の枠があれば引き継ぎます
        if existing_rois:
            self.rois = existing_rois.copy()
        else:
            self.rois = []
            
        if not os.path.exists(pdf_path):
            return []

        pdf = pdfium.PdfDocument(pdf_path)
        page = pdf[0]
        scale = 1.5
        bitmap = page.render(scale=scale, rev_byteorder=False)
        pil_image = bitmap.to_pil()
        
        self.clean_img = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        
        cv2.namedWindow("PDF Selector")
        cv2.setMouseCallback("PDF Selector", self.mouse_callback)
        
        # ★ 最初から枠を描画しておきます！
        self.redraw_image()
        
        print("マウスで枠を囲んでくださいね。終わったら「Enter」です。")
        print("間違えた時は「c」を押すと、一つ前の枠を取り消せます！")
        
        while True:
            key = cv2.waitKey(1) & 0xFF
            if key == 13: # Enterキー
                break
            elif key == ord('c'):
                # ★ cを押したら、リストの一番最後を消して描き直します
                if self.rois:
                    self.rois.pop()
                    self.redraw_image()
                    print("一つ前の枠を取り消しました！")
                
        cv2.destroyAllWindows()
        return self.rois
