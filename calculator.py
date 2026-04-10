import pypdfium2 as pdfium
import re

def extract_and_calculate(pdf_path, rois):
    """PDFのパスと座標を受け取って、計算結果を返す関数です"""
    try:
        pdf = pdfium.PdfDocument(pdf_path)
        page = pdf[0]
        pdf_w, pdf_h = page.get_size()
        textpage = page.get_textpage()
        
        scale = 1.5 
        total_sum = 0
        results_text = "--- 📝 読み取りと計算の結果です ---\n\n"
        
        for i, roi in enumerate(rois):
            x, y, w, h = roi
            
            # 座標をPDF用に変換します
            pdf_left = x / scale
            pdf_right = (x + w) / scale
            pdf_top = pdf_h - (y / scale)
            pdf_bottom = pdf_h - ((y + h) / scale)
            
            text = textpage.get_text_bounded(left=pdf_left, bottom=pdf_bottom, right=pdf_right, top=pdf_top)
            clean_text = text.strip()
            results_text += f"枠 {i+1} : {clean_text}\n"
            
            # 数字を探して足し算します
            numbers = re.findall(r'\d+', clean_text.replace(',', ''))
            if numbers:
                num_val = int("".join(numbers))
                total_sum += num_val
                results_text += f"  👉 数字を発見: {num_val}\n"
            else:
                results_text += "  👉 （数字はありませんでした…）\n"
        
        results_text += f"\n========================\n"
        results_text += f"✨ 合計金額: {total_sum} ✨\n"
        results_text += f"========================"
        
        return results_text, True # 成功したよ！という合図（True）と一緒に返します
        
    except Exception as e:
        return f"読み取り中にエラーが起きました…\n{e}", False
