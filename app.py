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
Ayrıca laboratuvar sonuçları ile **anlık kalibrasyon (bias correction)** yapabilir.
""")


# Modeli Yükleme
@st.cache_resource
def load_model():
    # Model yolunu kontrol et
    model_path = 'models/final_xgboost_model.pkl'
    if not os.path.exists(model_path):
        model_path = '../models/final_xgboost_model.pkl'

    try:
        model = joblib.load(model_path)
        return model
    except FileNotFoundError:
        st.error("Model dosyası bulunamadı! Lütfen önce 'src/pipeline.py' dosyasını çalıştırın.")
        return None


model = load_model()

# --- YAN MENÜ (GİRİŞLER) ---
st.sidebar.header("⚙️ Sensör Değerleri")
st.sidebar.info("Anlık sensör değerlerini aşağıdan değiştirebilirsiniz.")


def user_input_features():
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

# --- LAB ENTEGRASYONU (YENİ EKLENDİ) ---
st.sidebar.markdown("---")
st.sidebar.header("🧪 Lab Kalibrasyonu")
use_lab = st.sidebar.checkbox("Lab Verisiyle Düzelt (Bias Correction)")

bias = 0.0
if use_lab:
    st.sidebar.warning("Son gelen laboratuvar sonucunu girerek modeli kalibre edebilirsiniz.")
    last_lab_val = st.sidebar.number_input("Son Lab Sonucu (% Silika)", 0.0, 10.0, 2.5, step=0.1)
    last_model_val = st.sidebar.number_input("O Anki Model Tahmini (% Silika)", 0.0, 10.0, 2.3, step=0.1)

    # Bias (Sapma) Hesabı
    bias = last_lab_val - last_model_val
    st.sidebar.info(f"Uygulanan Düzeltme (Bias): {bias:+.2f}")

# --- İMZA ---
st.sidebar.markdown("---")
st.sidebar.caption(
    "Bu verimlilik aracı **Sedat Akdağ (Maden Yüksek Mühendisi)** tarafından "
    "**MultiGroup Zero2End Machine Learning Bootcamp** kapsamında hazırlanmıştır."
)

# --- TAHMİN BUTONU VE GÖRSELLEŞTİRME ---
if st.button('🔍 Kaliteyi Tahmin Et'):
    if model:
        # Model Feature Names
        expected_columns = model.get_booster().feature_names
        input_df = pd.DataFrame(columns=expected_columns)
        input_df.loc[0] = 0

        for key, value in input_data.items():
            for col in expected_columns:
                if key in col:
                    input_df.at[0, col] = value

        # Ham Tahmin
        raw_prediction = model.predict(input_df)[0]

        # Düzeltilmiş (Final) Tahmin
        final_prediction = raw_prediction + bias

        # Sonuçları Göster
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Tahmini Silika Oranı")
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=final_prediction,
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
                        'value': final_prediction}}))
            st.plotly_chart(fig)

        with col2:
            st.subheader("Sistem Durumu")

            # Kalite Mesajı
            if final_prediction < 2.0:
                st.success("✅ MÜKEMMEL KALİTE! \nÜretim hattı optimum seviyede.")
            elif final_prediction < 3.5:
                st.warning("⚠️ ORTA KALİTE. \nParametreler sınırlarda geziyor.")
            else:
                st.error("❌ KÖTÜ KALİTE! \nAcil müdahale gerekli.")

            st.markdown("---")
            st.write(f"🤖 **Yapay Zeka Ham Tahmini:** %{raw_prediction:.2f}")

            if use_lab:
                st.write(f"🧪 **Lab Düzeltmesi (Bias):** {bias:+.2f}")
                st.write(f"🎯 **Final (Kalibre) Sonuç:** %{final_prediction:.2f}")
            else:
                st.info("Lab kalibrasyonu kapalı.")