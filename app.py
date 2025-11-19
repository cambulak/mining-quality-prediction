import streamlit as st
import pandas as pd
import joblib
import numpy as np
import plotly.graph_objects as go
import os

# Sayfa Ayarları
st.set_page_config(page_title="Madencilik Kalite Tahmini", page_icon="⛏️", layout="wide")

# Başlık ve Açıklama
st.title("⛏️ Maden Flotasyon Tesisi - Kalite Tahmin Sistemi")
st.markdown("""
Bu sistem, tesisteki sensör verilerini (Demir Besleme, Hava Akışı vb.) kullanarak 
ürün kalitesini belirleyen **% Silika (Safsızlık)** oranını yapay zeka ile tahmin eder.
""")


# Modeli Yükleme (Hata yönetimi eklenmiş hali)
@st.cache_resource
def load_model():
    # Model yolunu kontrol et
    model_path = 'models/final_xgboost_model.pkl'

    # Eğer direkt yolda yoksa bir üst klasöre bak (bazen çalışma dizini farklı olabilir)
    if not os.path.exists(model_path):
        model_path = '../models/final_xgboost_model.pkl'

    try:
        model = joblib.load(model_path)
        return model
    except FileNotFoundError:
        st.error("Model dosyası bulunamadı! Lütfen önce 'src/pipeline.py' dosyasını çalıştırın.")
        return None


model = load_model()

# Yan Menü (Sidebar) - Kullanıcı Girişleri
st.sidebar.header("⚙️ Sensör Değerleri")
st.sidebar.info("Anlık sensör değerlerini aşağıdan değiştirebilirsiniz.")


def user_input_features():
    # Varsayılan değerler veri setinin ortalamalarından alınmıştır
    Iron_Feed = st.sidebar.slider('Demir Besleme (Iron Feed)', 40.0, 65.0, 55.0)
    Silica_Feed = st.sidebar.slider('Silika Besleme (Silica Feed)', 5.0, 35.0, 15.0)
    Starch_Flow = st.sidebar.slider('Nişasta Akışı (Starch Flow)', 0.0, 6000.0, 3000.0)
    Amina_Flow = st.sidebar.slider('Amina Akışı (Amina Flow)', 200.0, 600.0, 450.0)
    Ore_Pulp_Flow = st.sidebar.slider('Cevher Pülp Akışı', 350.0, 450.0, 400.0)
    Ore_Pulp_pH = st.sidebar.slider('Cevher Pülp pH', 8.5, 11.0, 9.8)
    Ore_Pulp_Density = st.sidebar.slider('Cevher Pülp Yoğunluğu', 1.5, 1.9, 1.7)

    st.sidebar.markdown("---")
    st.sidebar.markdown("**🔥 En Kritik Sensör**")
    Iron_Concentrate = st.sidebar.slider('Demir Konsantresi', 40.0, 70.0, 65.0)

    data = {
        'Iron_Feed': Iron_Feed,
        'Silica_Feed': Silica_Feed,
        'Starch_Flow': Starch_Flow,
        'Amina_Flow': Amina_Flow,
        'Ore_Pulp_Flow': Ore_Pulp_Flow,
        'Ore_Pulp_pH': Ore_Pulp_pH,
        'Ore_Pulp_Density': Ore_Pulp_Density,
        'Iron_Concentrate': Iron_Concentrate
    }
    return data


input_data = user_input_features()

# Tahmin Butonu
if st.button('🔍 Kaliteyi Tahmin Et'):
    if model:
        # 1. Modelin beklediği tüm sütunları oluştur
        expected_columns = model.get_booster().feature_names

        # 2. Boş bir DataFrame oluştur ve varsayılan değerlerle doldur
        input_df = pd.DataFrame(columns=expected_columns)
        input_df.loc[0] = 0

        # 3. Kullanıcının girdiği verileri ilgili yerlere eşleştir
        for key, value in input_data.items():
            for col in expected_columns:
                if key in col:
                    input_df.at[0, col] = value

        # 4. Tahmin Yap
        prediction = model.predict(input_df)[0]

        # 5. Sonuçları Göster
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Tahmini Silika Oranı")
            # Gösterge (Gauge) Grafiği
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=prediction,
                title={'text': "% Silica (Safsızlık)"},
                delta={'reference': 2.5, 'increasing': {'color': "red"}, 'decreasing': {'color': "green"}},
                gauge={
                    'axis': {'range': [0, 6]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 2.0], 'color': "lightgreen"},
                        {'range': [2.0, 3.5], 'color': "yellow"},
                        {'range': [3.5, 6.0], 'color': "red"}
                    ],
                    'threshold': {
                        'line': {'color': "black", 'width': 4},
                        'thickness': 0.75,
                        'value': prediction}}))
            st.plotly_chart(fig)

        with col2:
            st.subheader("Kalite Durumu")
            if prediction < 2.0:
                st.success("✅ MÜKEMMEL KALİTE! \nSilika oranı çok düşük. Tesis verimli çalışıyor.")
            elif prediction < 3.5:
                st.warning("⚠️ ORTA KALİTE. \nDikkatli olunmalı, bazı ayarlar optimize edilebilir.")
            else:
                st.error("❌ KÖTÜ KALİTE! \nSilika çok yüksek. 'Iron Concentrate' değerini kontrol edin!")

            st.info(f"Modelin Tahmini: %{prediction:.2f}")