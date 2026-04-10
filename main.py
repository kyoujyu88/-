import pypdfium2 as pdfium
import cv2
import numpy as np
import os

def select_and_extract_text(pdf_path):
    if not os.path.exists(pdf_path):
        print("【エラー】PDFファイルが見つかりません…")
        return []

    # 1. PDFを開いて1ページ目を取得します
    pdf = pdfium.PdfDocument(pdf_path)
    page = pdf[0]
    
    # PDF本来のサイズ（ポイント数）を覚えておきます
    pdf_w, pdf_h = page.get_size()
    
    # 2. 画面に表示するために画像化します
    # ※画面からはみ出してしまう場合は、この 1.5 を 1.0 などに下げてくださいね
    scale = 1.5
    bitmap = page.render(scale=scale, rev_byteorder=False)
    pil_image = bitmap.to_pil()
    img_bgr = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    
    print("==================================================")
    print(" 🖱️ 画像が表示されたら、以下の手順で操作してください")
    print(" 1. 読み取りたい文字をマウスで四角くドラッグして囲みます")
    print(" 2. 囲んだら「スペースキー」を押して決定します（青い枠になります）")
    print(" 3. 複数の場所を選びたい場合は、1と2を繰り返します")
    print(" 4. 選び終わったら「Escキー」を押してください")
    print("==================================================")
    
    # 3. マウスで複数領域を選択するGUIを呼び出します
    rois = cv2.selectROIs("Select Areas (Space: Confirm, Esc: Finish)", img_bgr, showCrosshair=True, fromCenter=False)
    cv2.destroyAllWindows()
    
    # 文字データの層を取り出します
    textpage = page.get_textpage()
    results = []
    
    print("\n--- 📝 読み取り結果 ---")
    for i, roi in enumerate(rois):
        x, y, w, h = roi
        
        # 選択されなかった（空っぽの）場合は飛ばします
        if w == 0 or h == 0:
            continue
            
        # 4. 画像の座標を、PDF本来の座標に変換します（魔法の計算式です！）
        # 画像サイズに合わせて掛けた倍率（scale）で割って元に戻します
        pdf_left = x / scale
        pdf_right = (x + w) / scale
        
        # 上下のY座標は、画像(左上が0)とPDF(左下が0)で逆転しているので、引き算でひっくり返します
        img_top_in_pdf = y / scale
        img_bottom_in_pdf = (y + h) / scale
        
        pdf_top = pdf_h - img_top_in_pdf
        pdf_bottom = pdf_h - img_bottom_in_pdf
        
        # 5. 計算した座標を使って、文字を抽出します
        text = textpage.get_text_bounded(left=pdf_left, bottom=pdf_bottom, right=pdf_right, top=pdf_top)
        
        # 前後の余分な空白や改行を綺麗にお掃除します
        clean_text = text.strip()
        results.append(clean_text)
        
        print(f"枠 {i+1} : {clean_text}")
        
    return results

# ==========================================
#   ここから下が実行部分です
# ==========================================

if __name__ == "__main__":
    current_folder = os.path.dirname(os.path.abspath(__file__))
    
    # 実際のファイル名に合わせて書き換えてくださいね
    pdf_filename = "sample.pdf" 
    target_pdf = os.path.join(current_folder, pdf_filename)
    
    extracted_data = select_and_extract_text(target_pdf)
    
    if extracted_data:
        print("-----------------------")
        print("大成功です！すべての読み取りが完了しました！")
