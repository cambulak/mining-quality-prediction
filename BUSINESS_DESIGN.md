Kurumsal Sistem Tasarımı ve İş Kurgusu (Business Case)
Rol: Kıdemli Veri Bilimci, Dijital Dönüşüm Departmanı Şirket: Global Madencilik A.Ş. (Temsili) Proje: Flotasyon Tesisi Akıllı Kalite Kontrol Sistemi (Smart Quality Control)

1. Mevcut Durum ve Sorun (AS-IS Analysis)
Maden zenginleştirme tesisimizde, ürün kalitesini belirleyen en kritik parametre % Silika (Safsızlık) oranıdır. Mevcut süreçte:

Operatörler numune alır ve laboratuvara gönderir.

XRF analiz sonuçları 2 ila 4 saat sonra gelir.

Sorun: Bu 4 saatlik "kör noktada", tesis operatörleri tecrübelerine dayanarak manuel ayar yaparlar. Ancak hammadde yapısı (tenör) ani değiştiğinde, geç müdahale edilir.

Sonuç: Yüksek silika içeren (kalitesiz) ürün üretimi, müşteri cezaları (penalty) ve gereksiz reaktif (kimyasal) tüketimi.

2. Önerilen Çözüm (TO-BE Scenario)
Geliştirdiğimiz "AI Tabanlı Sanal Sensör (Soft Sensor)" projesi ile laboratuvar analizini beklemeden, sahadaki IoT sensörlerinden (basınç, debi, yoğunluk vb.) alınan verilerle kalite anlık olarak (Real-Time) tahmin edilecektir.

Bu sistem, laboratuvarı ortadan kaldırmaz; laboratuvar sonuçlarını doğrulama ve kalibrasyon (Ground Truth) noktası olarak kullanır.

3. Sistem Mimarisi ve Veri Akışı
Gerçek bir üretim ortamında bu model şu mimari ile çalışacak şekilde tasarlanmıştır:

Veri Kaynağı (Edge): Tesisteki SCADA/PLC sistemleri, sensör verilerini saniyede bir okur.

Veri İletimi: Veriler Kafka veya MQTT protokolü ile güvenli bir şekilde veri gölüne (Data Lake) akar.

Model Motoru (Inference Engine):

Sunucuda çalışan XGBoost Modelimiz, gelen canlı veriyi işler (pipeline.py).

5 dakikalık periyotlarla Silica % tahminini üretir.

Arayüz (Frontend): Kontrol odasındaki operatörlerin önünde açık olan Streamlit Dashboard, anlık kaliteyi gösterir.

Aksiyon (Decision Support):

Eğer tahmin edilen Silika > %3.5 ise (Kritik Eşik), sistem kırmızı alarm verir.

Sistem, "Demir Konsantrasyonunu artır" veya "Hava akışını kıs" gibi öneriler sunar (Prescriptive Analytics).

Geri Besleme (Feedback Loop):

4 saat sonra gerçek laboratuvar sonucu sisteme girilir.

Model, kendi tahmini ile gerçek sonuç arasındaki farkı (Bias) hesaplar ve sonraki tahminleri buna göre otomatik kalibre eder (App içindeki Lab Entegrasyonu özelliği).

4. Beklenen İş Değeri (ROI & KPIs)
Bu projenin hayata geçmesiyle hedeflenen kazanımlar:

Reaktif Karar Verme -> Proaktif Yönetim: Hatalı üretime 4 saat sonra değil, anında müdahale edilmesi.

%5 Enerji Tasarrufu: Gereksiz öğütme ve pompalamanın önüne geçilerek enerji maliyetlerinin düşürülmesi.

%10 Reaktif Tasarrufu: Kimyasalların (Nişasta, Amin) sadece gerektiği kadar kullanılması.

Standartizasyon: Vardiyalar arası operatör performans farklarının minimize edilmesi.

5. Risk Yönetimi
Risk: Sensör arızası durumunda modelin yanlış tahmin üretmesi.

Önlem: Sistemdeki sensör verileri belirli bir aralığın dışına çıkarsa (Outlier), model otomatik olarak "Güvenli Mod"a geçer ve operatörü uyarır.