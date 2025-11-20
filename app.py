import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import sqlite3
from datetime import datetime
from src.inference import ModelService
from src import config  # Veritabanı yolu için

# --- AYARLAR ---
st.set_page_config(page_title="Madencilik Kalite Tahmini", page_icon="⛏️", layout="wide")


# --- SERVİSİ BAŞLAT ---
@st.cache_resource
def get_service():
    try:
        return ModelService()
    except Exception as e:
        st.error(f"Hata: {e}")
        return None


service = get_service()


# --- VERİTABANI İŞLEMLERİ ---
def init_db():
    conn = sqlite3.connect(config.DB_PATH)
    c = conn.cursor()
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


def log_prediction(data, raw, bias, final):
    conn = sqlite3.connect(config.DB_PATH)
    c = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO predictions VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
              (timestamp, float(data['Iron_Feed']), float(data['Silica_Feed']),
               float(data['Starch_Flow']), float(data['Amina_Flow']), float(data['Ore_Pulp_Flow']),
               float(data['Ore_Pulp_pH']), float(data['Ore_Pulp_Density']), float(data['Iron_Concentrate']),
               float(raw), float(bias), float(final)))
    conn.commit()
    conn.close()


init_db()

# --- ARAYÜZ ---
st.title("⛏️ Maden Flotasyon Tesisi - AI Sistemi")

tab1, tab2 = st.tabs(["🔍 Tahmin", "📊 Monitoring"])

with tab1:
    st.sidebar.header("⚙️ Sensörler")

    iron_feed = st.sidebar.slider('Demir Besleme', 40.0, 65.0, 55.0)
    silica_feed = st.sidebar.slider('Silika Besleme', 5.0, 35.0, 15.0)
    starch_flow = st.sidebar.slider('Nişasta Akışı', 0.0, 6000.0, 3000.0)
    amina_flow = st.sidebar.slider('Amina Akışı', 200.0, 600.0, 450.0)
    ore_pulp_flow = st.sidebar.slider('Cevher Pülp Akışı', 350.0, 450.0, 400.0)
    ore_pulp_ph = st.sidebar.slider('Cevher Pülp pH', 8.5, 11.0, 9.8)
    ore_pulp_density = st.sidebar.slider('Cevher Pülp Yoğunluğu', 1.5, 1.9, 1.7)
    st.sidebar.markdown("**🔥 Kritik Sensör**")
    iron_conc = st.sidebar.slider('Demir Konsantresi', 40.0, 70.0, 65.0)

    input_data = {
        'Iron_Feed': iron_feed, 'Silica_Feed': silica_feed,
        'Starch_Flow': starch_flow, 'Amina_Flow': amina_flow,
        'Ore_Pulp_Flow': ore_pulp_flow, 'Ore_Pulp_pH': ore_pulp_ph,
        'Ore_Pulp_Density': ore_pulp_density, 'Iron_Concentrate': iron_conc
    }

    # Lab Entegrasyonu
    st.sidebar.markdown("---")
    st.sidebar.header("🧪 Lab Kalibrasyonu")
    use_lab = st.sidebar.checkbox("Lab Verisiyle Düzelt")
    bias = 0.0
    if use_lab:
        last_lab = st.sidebar.number_input("Son Lab Sonucu", 0.0, 10.0, 2.5)
        last_model = st.sidebar.number_input("O Anki Model Tahmini", 0.0, 10.0, 2.3)
        bias = last_lab - last_model
        st.sidebar.info(f"Bias: {bias:+.2f}")

    st.sidebar.caption("Sedat Akdağ - Maden Yüksek Mühendisi")

    if st.button('🔍 Tahmin Et'):
        if service:
            raw_pred = service.predict(input_data)
            final_pred = raw_pred + bias

            log_prediction(input_data, raw_pred, bias, final_pred)
            st.toast("Kayıt Başarılı!", icon="💾")

            col1, col2 = st.columns(2)
            with col1:
                fig = go.Figure(go.Indicator(
                    mode="gauge+number+delta", value=final_pred,
                    title={'text': "% Silica"},
                    delta={'reference': 2.5, 'increasing': {'color': "red"}, 'decreasing': {'color': "green"}},
                    gauge={'axis': {'range': [0, 6]}, 'bar': {'color': "darkblue"},
                           'steps': [{'range': [0, 2.0], 'color': "lightgreen"},
                                     {'range': [2.0, 3.5], 'color': "yellow"},
                                     {'range': [3.5, 6.0], 'color': "red"}]}))
                st.plotly_chart(fig)
            with col2:
                if final_pred < 2.0:
                    st.success("✅ MÜKEMMEL")
                elif final_pred < 3.5:
                    st.warning("⚠️ ORTA")
                else:
                    st.error("❌ KÖTÜ")
                st.write(f"**Model:** %{raw_pred:.2f}")
                if use_lab: st.write(f"**Bias:** {bias:+.2f}")

with tab2:
    st.header("📊 İzleme Paneli")
    conn = sqlite3.connect(config.DB_PATH)
    try:
        df_logs = pd.read_sql("SELECT * FROM predictions", conn)
        if not df_logs.empty:
            st.dataframe(df_logs.sort_values('timestamp', ascending=False).head(5), use_container_width=True)
            fig = px.line(df_logs, x='timestamp', y='final_result', title="Kalite Trendi")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Veri yok.")
    except:
        st.info("Veritabanı henüz oluşmadı.")
    conn.close()