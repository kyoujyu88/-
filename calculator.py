import pypdfium2 as pdfium
import re
from datetime import datetime

def extract_and_calculate(pdf_path, rois):
    """PDFのパスと座標を受け取って、計算結果を返す関数です"""
    try:
        pdf = pdfium.PdfDocument(pdf_path)
        page = pdf[0]
        pdf_w, pdf_h = page.get_size()
        textpage = page.get_textpage()
        
        scale = 1.5 
        extracted_texts = [] # 順番に読んだ文字を保存する「リスト」です
        results_text = "--- 📝 読み取り結果 ---\n\n"
        
        for i, roi in enumerate(rois):
            x, y, w, h = roi
            
            # 座標をPDF用に変換します
            pdf_left = x / scale
            pdf_right = (x + w) / scale
            pdf_top = pdf_h - (y / scale)
            pdf_bottom = pdf_h - ((y + h) / scale)
            
            text = textpage.get_text_bounded(left=pdf_left, bottom=pdf_bottom, right=pdf_right, top=pdf_top)
            clean_text = text.strip()
            
            # 後で計算できるように、リストに順番に保存しておきます
            extracted_texts.append(clean_text)
            results_text += f"枠 {i+1} : {clean_text}\n"
            
        
        results_text += f"\n--- 🧮 計算結果 ---\n\n"
        
        # ==========================================
        # ★ ここに篤志さん専用の計算ルールを書きます！ ★
        # ==========================================
        
        # 枠がちゃんと2つ以上選ばれているか確認します
        if len(extracted_texts) >= 2:
            # プログラムは0番目から数えるので、[0]が枠1、[1]が枠2です
            text1 = extracted_texts[0] 
            text2 = extracted_texts[1] 
            
            # 「2026年4月1日」や「2026/04/01」のような文字から、数字だけを抜き出します
            nums1 = re.findall(r'\d+', text1)
            nums2 = re.findall(r'\d+', text2)
            
            # 年、月、日の3つの数字がちゃんと見つかったか確認します
            if len(nums1) >= 3 and len(nums2) >= 3:
                try:
                    # 数字を「日付のデータ」に変換します
                    date1 = datetime(int(nums1[0]), int(nums1[1]), int(nums1[2]))
                    date2 = datetime(int(nums2[0]), int(nums2[1]), int(nums2[2]))
                    
                    # 引き算をして、日数を計算します！
                    diff = date1 - date2
                    days = abs(diff.days) # どっちが先でもプラスの日数になるように abs を使います
                    
                    results_text += f"📅 枠1と枠2の日数の差は 【 {days}日 】 です！\n"
                    
                except Exception as e:
                     results_text += f"💦 日付の計算ができませんでした…（ありえない日付だったかもしれません）\n"
            else:
                results_text += "💦 枠1と枠2から、正しい年月日が見つけられませんでした…\n"
        else:
            results_text += "💡 日付の引き算をするには、枠を2つ以上選んでくださいね。\n"

        return results_text, True
        
    except Exception as e:
        return f"読み取り中にエラーが起きました…\n{e}", False
