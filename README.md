# ⛏️ Mining Quality Prediction: End-to-End ML Project

Bu proje, gerçek bir maden zenginleştirme (flotasyon) tesisinden alınan sensör verilerini kullanarak, üretim kalitesini belirleyen **% Silika (Safsızlık)** oranını tahmin eden uçtan uca bir makine öğrenmesi çözümüdür.

![Project Status](https://img.shields.io/badge/Status-Completed-success)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Library](https://img.shields.io/badge/Library-XGBoost%20%7C%20Streamlit%20%7C%20SHAP-orange)

## 🎯 Problem Tanımı ve Çözüm
**Problem:** Flotasyon tesislerinde ürün kalitesi (Silika oranı) geleneksel laboratuvar analizleriyle belirlenir. Ancak bu analizler **1-2 saat** sürer. Bu gecikme, prosesin geç optimize edilmesine, enerji israfına ve hatalı üretime neden olur.

**Çözüm:** Geliştirdiğimiz Makine Öğrenmesi (XGBoost) modeli, tesisin sensör verilerini (Hava akışı, Pülp yoğunluğu, Demir beslemesi vb.) anlık olarak analiz eder ve kaliteyi **saniyeler içinde** tahmin eder. Bu sayede operatörler anlık müdahale edebilir.

## 📸 Proje Önizlemesi
![Uygulama Arayüzü](reports/app_screenshot.png)

## 📊 Veri Seti
* **Kaynak:** [Kaggle - Mining Process Flotation Plant Database](https://www.kaggle.com/datasets/edumagalhaes/quality-prediction-in-a-mining-process)
* **Boyut:** 737,453 satır, 24 sütun (Mart 2017 - Eylül 2017 arası).
* **Yapı:** Zaman serisi (Time-Series) niteliğinde sensör verileri.
* **Hedef Değişken:** `% Silica Concentrate` (Minimize edilmesi gereken safsızlık).

> **⚠️ Önemli Not:** Veri seti boyutu (175MB) GitHub sınırlarını aştığı için repoya eklenmemiştir. Projeyi çalıştırmak için veriyi yukarıdaki linkten indirip `data/` klasörüne `MiningProcess_Flotation_Plant_Database.csv` adıyla kaydetmelisiniz.

## 🛠️ Pipeline ve Metodoloji

Proje 6 ana aşamadan oluşmaktadır:

1. **EDA (Keşifçi Veri Analizi):** Veri dağılımı ve korelasyonlar incelendi. Demir konsantrasyonu ile Silika arasındaki negatif ilişki tespit edildi.
2. **Preprocessing:** Tarih formatı `datetime`'a çevrildi, virgül ondalık ayracı düzeltildi.
3. **Feature Engineering:**
   * **Rolling Window (Hareketli Ortalama):** Sensörlerdeki anlık gürültüyü (noise) azaltmak için son 5 periyodun ortalaması alındı.
   * **Lag Features:** Tesis içindeki akış gecikmesini (girişten çıkışa geçen süre) modellemek için `Lag1` özellikleri türetildi.
4. **Modelleme:** `RandomForest` ile baseline oluşturuldu, ardından `XGBoost` seçildi.
5. **Optimizasyon:** `Optuna` kütüphanesi ile hiperparametre optimizasyonu (Learning rate, max depth vb.) yapıldı.
6. **Deployment:** Model `Streamlit` ile canlı bir web arayüzüne dönüştürüldü.

## 📈 Model Performansı ve Değerlendirme

| Model | Validasyon Yöntemi | R2 Score | RMSE | Açıklama |
|-------|--------------------|----------|------|----------|
| **Baseline (Random Forest)** | Shuffle Split (Rastgele) | 0.88 | 0.38 | **Data Leakage Var.** Rastgele bölme yapıldığı için model geleceği gördü. |
| **Final Model (XGBoost)** | **Time Series Split** | **0.70** | **0.64** | **Gerçekçi Senaryo.** Gelecek verisi gösterilmeden, sadece geçmişe bakarak tahmin yapıldı. |

**Neden Time Series Split Seçildi?**
Endüstriyel veriler zamana bağlıdır. Rastgele karıştırarak (Shuffle) test yapmak, modelin 12:00 verisini öğrenip 11:59'u tahmin etmesine (kolaycılığa) yol açar. Projede gerçek hayat simülasyonu için veriyi zamana göre keserek (Ocak-Ağustos: Train, Eylül: Test) validasyon yapılmıştır.

## 🧠 Modelin Karar Mekanizması (SHAP Analizi)
Modelin "Kara Kutu" olmasını engellemek için SHAP analizi yapılmıştır.
* **Bulgu:** Kaliteyi etkileyen en kritik faktör **Demir Konsantresi (Iron Concentrate)** seviyesidir.
* **İş Aksiyonu:** Simülasyonlar göstermiştir ki; Demir konsantrasyonu düştüğünde, safsızlık (Silika) artmaktadır. Operatörler arayüz üzerinden bu değeri takip ederek kaliteyi kontrol altında tutabilir.

## 🚀 Kurulum ve Çalıştırma (Local)

**1. Repoyu Klonlayın:**
```bash
git clone [https://github.com/KULLANICI_ADINIZ/mining-quality-prediction.git](https://github.com/KULLANICI_ADINIZ/mining-quality-prediction.git)
cd mining-quality-prediction
2. Sanal Ortam Kurun ve Kütüphaneleri Yükleyin:

Bash

pip install -r requirements.txt
3. Pipeline'ı Çalıştırın (Model Eğitimi): (Veri setini data/ klasörüne koyduğunuzdan emin olun)

Bash

python src/pipeline.py
Bu işlem veriyi işler, modeli eğitir ve models/final_xgboost_model.pkl dosyasını oluşturur.

4. Arayüzü Başlatın:

Bash

streamlit run app.py

📂 Repo Yapısı

mining-quality-prediction/
├── data/               # Ham veri dosyası (Git-ignore edilmiştir)
├── notebooks/          # Jupyter Notebooks
│   ├── 1_eda.ipynb
│   ├── 2_baseline.ipynb
│   ├── 3_feature_engineering.ipynb
│   ├── 4_model_optimization.ipynb
│   └── 5_evaluation.ipynb
├── src/                # Kaynak kodlar
│   └── pipeline.py     # Final eğitim scripti
├── models/             # Eğitilmiş model dosyaları (.pkl)
├── app.py              # Streamlit web arayüzü kodu
├── requirements.txt    # Proje bağımlılıkları
└── README.md           # Proje dokümantasyonu

🛠️ Kullanılan Teknolojiler
Python 3.x

Veri İşleme: Pandas, NumPy

Makine Öğrenmesi: Scikit-learn, XGBoost

Optimizasyon: Optuna

Açıklanabilirlik (XAI): SHAP

Görselleştirme: Matplotlib, Seaborn, Plotly

Deployment: Streamlit

📞 İletişim
Geliştirici: Sedat AKDAG

LinkedIn: [https://linkedin/in/msedatakdag]

Email: [akdags@outlook.com.tr]