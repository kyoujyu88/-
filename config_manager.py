import json
import os

class ConfigManager:
    """設定ファイル（JSON）の保存や読み込みを専門に行うクラスです"""
    
    def __init__(self, filename="ranges_config.json"):
        self.filename = filename

    def load_all(self):
        """保存されているすべての設定を辞書形式で読み込みます"""
        if not os.path.exists(self.filename):
            return {}
            
        with open(self.filename, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        return data if data else {}

    def save(self, name, rois):
        """新しい設定を名前をつけて保存（上書き・追加）します"""
        data = self.load_all()
        data[name] = rois
        
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
