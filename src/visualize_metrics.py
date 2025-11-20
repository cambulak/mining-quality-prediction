import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import os

# Rapor klasörünü kontrol et
output_folder = '../reports'
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Metrik Verileri (Senin sonuçların)
data = {
    'Model': ['Baseline (Random Forest)', 'Final (XGBoost)', 'Baseline (Random Forest)', 'Final (XGBoost)'],
    'Metrik': ['R2 Score (Başarı)', 'R2 Score (Başarı)', 'RMSE (Hata)', 'RMSE (Hata)'],
    'Değer': [0.88, 0.70, 0.38, 0.64],
    'Durum': ['Data Leakage (Yanıltıcı)', 'Gerçekçi (Time Series Split)', 'Data Leakage (Yanıltıcı)', 'Gerçekçi (Time Series Split)']
}

df = pd.DataFrame(data)

# Grafik Ayarları
plt.figure(figsize=(10, 6))
sns.set_theme(style="whitegrid")

# Çizim (Barplot)
# Palette: Gri (Baseline) ve Kırmızı (Final Model) kullanarak odağı final modele çekiyoruz
ax = sns.barplot(x='Metrik', y='Değer', hue='Model', data=df, palette=['#bdc3c7', '#e74c3c'])

# Barların üzerine değerleri yazalım
for container in ax.containers:
    ax.bar_label(container, fmt='%.2f', padding=3, fontsize=12, fontweight='bold')

# Başlık ve Etiketler
plt.title('Model Performans Karşılaştırması\n(Baseline vs Final)', fontsize=16, fontweight='bold', pad=20)
plt.ylabel('Skor', fontsize=12)
plt.xlabel('')
plt.ylim(0, 1.0) # Y eksenini sabitleyelim
plt.legend(title='Model Versiyonu', loc='upper right')

# Altına not düşelim
plt.figtext(0.5, 0.01, "Not: Baseline model 'Shuffle Split' kullandığı için skoru yapay olarak yüksektir.\nFinal model 'Time Series Split' ile gerçek hayat senaryosunda test edilmiştir.",
            ha="center", fontsize=10, style='italic', color='gray')

# Kaydetme
save_path = os.path.join(output_folder, 'performance_comparison.png')
plt.tight_layout()
plt.savefig(save_path, dpi=300)

print(f"Grafik başarıyla oluşturuldu: {save_path} ✅")