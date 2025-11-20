import joblib
import pandas as pd
import os
import sys

# Config dosyasını import edebilmek için yolu ekle
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import config


class ModelService:
    def __init__(self):
        self.model = self._load_model()

    def _load_model(self):
        """Modeli diskten yükler."""
        if os.path.exists(config.MODEL_PATH):
            print(f"Model yüklendi: {config.MODEL_PATH}")
            return joblib.load(config.MODEL_PATH)
        else:
            raise FileNotFoundError(f"Model dosyası bulunamadı: {config.MODEL_PATH}")

    def predict(self, input_data):
        """
        Sözlük (dict) formatında veri alır, modele uygun DataFrame'e çevirir ve tahmin döner.
        """
        if not self.model:
            return None

        # Modelin beklediği sütun isimlerini al
        expected_columns = self.model.get_booster().feature_names

        # Boş DataFrame oluştur
        input_df = pd.DataFrame(columns=expected_columns)
        input_df.loc[0] = 0  # Başlangıç değeri

        # Gelen veriyi eşleştir
        for key, value in input_data.items():
            for col in expected_columns:
                # Örn: 'Iron_Feed' verisini 'Iron_Feed_Rolling_Mean' sütununa da yazar
                if key in col:
                    input_df.at[0, col] = value

        # Tahmin yap
        prediction = self.model.predict(input_df)[0]
        return float(prediction)