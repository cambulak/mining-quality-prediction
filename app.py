import streamlit as st
import pandas as pd
import joblib
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import os
import sqlite3
from datetime import datetime

# --- AYARLAR ---
st.set_page_config(page_title="Madencilik Kalite Tahmini", page_icon="⛏️", layout="wide")


# --- VERİTABANI İŞLEMLERİ (MONITORING) ---
def init_db():
    """Loglama için SQLite veritabani oluşturur."""
    conn = sqlite3.connect('monitoring.db')
    c = conn.cursor()
    # Tabloyu oluştur (Eğer yoksa)
    c.execute('''CREATE TABLE IF NOT EXISTS predictions
                 (
                     timestamp
                     TEXT,
                     iron_feed
                     REAL,
                     silica_feed
                     REAL,
                     starch_flow
                     REAL,
                     amina_flow
                     REAL,
                     ore_pulp_flow
                     REAL,
                     ore_pulp_ph
                     REAL,
                     ore_pulp_density
                     REAL,
                     iron_concentrate
                     REAL,
                     prediction
                     REAL,
                     bias
                     REAL,
                     final_result
                     REAL
                 )''')
    conn.commit()
    conn.close()


def log_prediction(input_data, raw_pred, bias, final_pred):
    """Yapılan tahmini veritabanına kaydeder."""
    conn = sqlite3.connect('monitoring.db')
    c = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    c.execute("INSERT INTO predictions VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
              (timestamp, input_data['Iron_Feed'], input_data['Silica_Feed'],
               input_data['Starch_Flow'], input_data['Amina_Flow'], input_data['Ore_Pulp_Flow'],
               input_data['Ore_Pulp_pH'], input_data['Ore_Pulp_Density'], input_data['Iron_Concentrate'],
               raw_prediction, bias, final_pred))
    conn.commit()
    conn.close()


def get_logs():
    """Geçmiş tahminleri getirir."""
    conn = sqlite3.connect('monitoring.db')
    df = pd.read_sql("SELECT * FROM predictions", conn)
    conn.close()
    return df


# Uygulama başlarken veritabanını hazırla
init_db()


# --- MODEL YÜKLEME ---
@st.cache_resource
def load_model():
    model_path = 'models/final_xgboost_model.pkl'
    if not os.path.exists(model_path):
        model_path = '../models/final_xgboost_model.pkl'
    try:
        return joblib.load(model_path)
    except:
        return None


model = load_model()

# --- BAŞLIK ---
st.title("⛏️ Maden Flotasyon Tesisi - AI Sistemi")

# --- SEKME YAPISI (Prediction vs Monitoring) ---
tab1, tab2 = st.tabs(["🔍 Tahmin Ekranı", "📊 Monitoring (İzleme)"])

with tab1:
    # --- YAN MENÜ (INPUTS) ---
    st.sidebar.header("⚙️ Sensör Değerleri")


    def user_input_features():
        Iron_Feed = st.sidebar.slider('Demir Besleme', 40.0, 65.0, 55.0)
        Silica_Feed = st.sidebar.slider('Silika Besleme', 5.0, 35.0, 15.0)
        Starch_Flow = st.sidebar.slider('Nişasta Akışı', 0.0, 6000.0, 3000.0)
        Amina_Flow = st.sidebar.slider('Amina Akışı', 200.0, 600.0, 450.0)
        Ore_Pulp_Flow = st.sidebar.slider('Cevher Pülp Akışı', 350.0, 450.0, 400.0)
        Ore_Pulp_pH = st.sidebar.slider('Cevher Pülp pH', 8.5, 11.0, 9.8)
        Ore_Pulp_Density = st.sidebar.slider('Cevher Pülp Yoğunluğu', 1.5, 1.9, 1.7)
        st.sidebar.markdown("**🔥 Kritik Sensör**")
        Iron_Concentrate = st.sidebar.slider('Demir Konsantresi', 40.0, 70.0, 65.0)

        return {
            'Iron_Feed': Iron_Feed, 'Silica_Feed': Silica_Feed,
            'Starch_Flow': Starch_Flow, 'Amina_Flow': Amina_Flow,
            'Ore_Pulp_Flow': Ore_Pulp_Flow, 'Ore_Pulp_pH': Ore_Pulp_pH,
            'Ore_Pulp_Density': Ore_Pulp_Density, 'Iron_Concentrate': Iron_Concentrate
        }


    input_data = user_input_features()

    # --- LAB KALİBRASYONU ---
    st.sidebar.markdown("---")
    st.sidebar.header("🧪 Lab Kalibrasyonu")
    use_lab = st.sidebar.checkbox("Lab Verisiyle Düzelt")
    bias = 0.0
    if use_lab:
        last_lab = st.sidebar.number_input("Son Lab Sonucu", 0.0, 10.0, 2.5)
        last_model = st.sidebar.number_input("O Anki Model Tahmini", 0.0, 10.0, 2.3)
        bias = last_lab - last_model
        st.sidebar.info(f"Bias: {bias:+.2f}")

    st.sidebar.caption("Hazırlayan: Sedat Akdağ (Maden Yüksek Mühendisi)")

    # --- TAHMİN BUTONU ---
    if st.button('🔍 Kaliteyi Tahmin Et ve Kaydet'):
        if model:
            # Veriyi hazırla
            expected_cols = model.get_booster().feature_names
            input_df = pd.DataFrame(columns=expected_cols)
            input_df.loc[0] = 0
            for key, val in input_data.items():
                for col in expected_cols:
                    if key in col: input_df.at[0, col] = val

            # Tahmin
            raw_prediction = model.predict(input_df)[0]
            final_prediction = raw_prediction + bias

            # --- LOGLAMA İŞLEMİ ---
            log_prediction(input_data, raw_prediction, bias, final_prediction)
            st.toast("Veri başarıyla loglandı!", icon="💾")  # Kullanıcıya bildirim

            # Görselleştirme
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Tahmini Silika")
                fig = go.Figure(go.Indicator(
                    mode="gauge+number+delta", value=final_prediction,
                    title={'text': "% Silica"},
                    delta={'reference': 2.5, 'increasing': {'color': "red"}, 'decreasing': {'color': "green"}},
                    gauge={'axis': {'range': [0, 6]}, 'bar': {'color': "darkblue"},
                           'steps': [{'range': [0, 2.0], 'color': "lightgreen"},
                                     {'range': [2.0, 3.5], 'color': "yellow"},
                                     {'range': [3.5, 6.0], 'color': "red"}]}))
                st.plotly_chart(fig)

            with col2:
                st.subheader("Durum Analizi")
                if final_prediction < 2.0:
                    st.success("✅ MÜKEMMEL KALİTE")
                elif final_prediction < 3.5:
                    st.warning("⚠️ ORTA KALİTE")
                else:
                    st.error("❌ KÖTÜ KALİTE")
                st.write(f"**Ham Tahmin:** %{raw_prediction:.2f}")
                if use_lab: st.write(f"**Lab Düzeltmesi:** {bias:+.2f}")

with tab2:
    st.header("📊 Gerçek Zamanlı İzleme Paneli (Monitoring)")
    st.markdown("Modelin canlı ortamdaki performans geçmişi ve tahmin dağılımları.")

    # Logları Çek
    df_logs = get_logs()

    if not df_logs.empty:
        # Tabloyu Göster
        st.dataframe(df_logs.sort_values('timestamp', ascending=False).head(10), use_container_width=True)

        # Grafik 1: Zaman İçindeki Tahminler
        st.subheader("📈 Tahmin Trendi (Zaman Serisi)")
        fig_trend = px.line(df_logs, x='timestamp', y='final_result', markers=True,
                            title="Tahmini Silika Oranı Değişimi")
        fig_trend.add_hline(y=2.5, line_dash="dash", line_color="green", annotation_text="Hedef Kalite")
        st.plotly_chart(fig_trend, use_container_width=True)

        # Grafik 2: Dağılım
        col_mon1, col_mon2 = st.columns(2)
        with col_mon1:
            st.subheader("Demir Konsantresi vs Silika")
            fig_scatter = px.scatter(df_logs, x='iron_concentrate', y='final_result', color='final_result',
                                     color_continuous_scale='RdYlGn_r', title="Kritik Sensör İlişkisi")
            st.plotly_chart(fig_scatter)

        with col_mon2:
            st.subheader("İstatistikler")
            st.metric("Toplam Tahmin Sayısı", len(df_logs))
            st.metric("Ortalama Silika", f"%{df_logs['final_result'].mean():.2f}")
            st.metric("En Kötü Tahmin", f"%{df_logs['final_result'].max():.2f}")

        # İndirme Butonu
        csv = df_logs.to_csv(index=False).encode('utf-8')
        st.download_button("Logları İndir (CSV)", csv, "monitoring_logs.csv", "text/csv")

    else:
        st.info("Henüz kayıtlı bir tahmin yok. 'Tahmin Ekranı'na gidip butona basın.")