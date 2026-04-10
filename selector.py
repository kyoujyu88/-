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
                cv2.rectangle(self.display_img, (rx, ry), (rx+w, ry+h), (255, 0, 0), 2)
                cv2.putText(self.display_img, str(len(self.rois)), (rx, ry - 5), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
                cv2.imshow("PDF Selector", self.display_img)

    def select(self, pdf_path):
        """画面を開いて、選ばれた座標（枠）を返す関数です"""
        self.rois = []
        if not os.path.exists(pdf_path):
            return []

        pdf = pdfium.PdfDocument(pdf_path)
        page = pdf[0]
        scale = 1.5
        bitmap = page.render(scale=scale, rev_byteorder=False)
        pil_image = bitmap.to_pil()
        
        self.clean_img = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        self.display_img = self.clean_img.copy()
        
        cv2.namedWindow("PDF Selector")
        cv2.setMouseCallback("PDF Selector", self.mouse_callback)
        cv2.imshow("PDF Selector", self.display_img)
        
        print("マウスで枠を囲んでくださいね。終わったら「Enter」、やり直しは「c」です。")
        
        while True:
            key = cv2.waitKey(1) & 0xFF
            if key == 13: # Enterキー
                break
            elif key == ord('c'):
                self.rois = []
                self.display_img = self.clean_img.copy()
                cv2.imshow("PDF Selector", self.display_img)
                
        cv2.destroyAllWindows()
        return self.rois
