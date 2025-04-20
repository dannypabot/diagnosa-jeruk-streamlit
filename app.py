import streamlit as st
import pandas as pd
import json
from datetime import datetime
from database import init_db, get_gejala, get_data_penyakit, simpan_diagnosa

# Set page config for better appearance
st.set_page_config(
    page_title="Diagnosa Penyakit Jeruk",
    page_icon="🍊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme styling
st.markdown("""
    <style>
        :root {
            --primary-color: #4CAF50;
            --background-color: #121212;
            --secondary-background: #1E1E1E;
            --text-color: #FFFFFF;
            --card-background: #2D2D2D;
            --border-color: #444444;
        }
        
        body {
            background-color: var(--background-color);
            color: var(--text-color);
        }
        
        .main {
            background-color: var(--background-color);
        }
        
        .stButton>button {
            background-color: var(--primary-color);
            color: white;
            border-radius: 5px;
            padding: 0.5rem 1rem;
            border: none;
        }
        
        .stButton>button:hover {
            background-color: #45a049;
        }
        
        .stCheckbox>label {
            font-size: 1rem;
            padding: 0.5rem;
            color: var(--text-color);
        }
        
        .stMarkdown h1 {
            color: var(--primary-color);
        }
        
        .stMarkdown h2 {
            color: #81C784;
        }
        
        .stMarkdown h3 {
            color: #A5D6A7;
        }
        
        .result-card {
            border-radius: 10px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            background-color: var(--card-background);
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            border-left: 4px solid var(--primary-color);
        }
        
        .symptom-card {
            border-left: 4px solid var(--primary-color);
            padding: 0.5rem 1rem;
            margin: 0.5rem 0;
            background-color: var(--secondary-background);
            border-radius: 5px;
        }
        
        .stExpander {
            background-color: var(--secondary-background);
            border: 1px solid var(--border-color);
            border-radius: 8px;
        }
        
        .stExpander label {
            color: var(--text-color) !important;
        }
        
        .stAlert {
            background-color: var(--card-background);
        }
        
        .stDataFrame {
            background-color: var(--secondary-background);
        }
        
        .stTabs [data-baseweb="tab-list"] {
            background-color: var(--secondary-background);
        }
        
        .stTabs [data-baseweb="tab"] {
            color: var(--text-color);
        }
        
        .stTabs [aria-selected="true"] {
            background-color: var(--card-background);
        }
        
        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background-color: var(--secondary-background) !important;
        }
        
        /* Change all text to white */
        p, div, span, h1, h2, h3, h4, h5, h6 {
            color: var(--text-color) !important;
        }
        
        /* Change checkbox color */
        .stCheckbox [data-baseweb="checkbox"] {
            border-color: var(--primary-color) !important;
        }
        
        .stCheckbox [data-baseweb="checkbox"]:checked {
            background-color: var(--primary-color) !important;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize database
init_db()

# Fungsi diagnosa
def hitung_probabilitas(gejala_terpilih, data_penyakit):
    hasil = {}
    total_penyakit = len(data_penyakit)

    for kode_penyakit, penyakit in data_penyakit.items():
        P_H = 1 / total_penyakit
        likelihood = 1.0
        evidence = 1.0

        for gejala in gejala_terpilih:
            likelihood *= penyakit["gejala"].get(gejala, 0.01)
            total = sum(p["gejala"].get(gejala, 0.01) for p in data_penyakit.values())
            evidence *= total / total_penyakit

        P_H_E = (likelihood * P_H) / evidence
        hasil[kode_penyakit] = {"nama": penyakit["nama"], "probabilitas": P_H_E}

    total_prob = sum(item["probabilitas"] for item in hasil.values())
    for kode in hasil:
        hasil[kode]["probabilitas"] = (hasil[kode]["probabilitas"] / total_prob) * 100

    return hasil

# STREAMLIT UI
st.title("🍊 Sistem Pakar Diagnosa Penyakit Jeruk")
st.markdown("""
    <div style="background-color:#2D2D2D; padding:1rem; border-radius:10px; margin-bottom:2rem; border-left:4px solid #4CAF50;">
        <h3 style="color:#81C784;">Berbasis Teorema Bayes</h3>
        <p>Pilih gejala yang teramati pada tanaman jeruk untuk mendapatkan diagnosis penyakit yang mungkin terjadi.</p>
    </div>
""", unsafe_allow_html=True)

data_gejala = get_gejala()
data_penyakit = get_data_penyakit()
gejala_terpilih = []

# Symptoms selection in expandable sections
with st.expander("🔍 Pilih Gejala yang Teramati", expanded=True):
    st.write("Silakan centang gejala yang sesuai:")
    
    cols = st.columns(2)
    col_idx = 0
    
    for kode, deskripsi in data_gejala.items():
        with cols[col_idx]:
            if st.checkbox(f"**{kode}**: {deskripsi}", key=kode):
                gejala_terpilih.append(kode)
        col_idx = (col_idx + 1) % 2

# Diagnosis button centered
col1, col2, col3 = st.columns([1,2,1])
with col2:
    if st.button("🚀 Lakukan Diagnosa", use_container_width=True):
        if not gejala_terpilih:
            st.warning("⚠️ Silakan pilih minimal satu gejala.")
        else:
            with st.spinner('🔍 Menganalisis gejala...'):
                hasil = hitung_probabilitas(gejala_terpilih, data_penyakit)
                simpan_diagnosa(gejala_terpilih, hasil)
                
                hasil_terurut = sorted(hasil.items(), key=lambda x: x[1]["probabilitas"], reverse=True)
                
                st.success("Diagnosis selesai! Berikut hasilnya:")
                st.markdown("---")
                
                # Display top 3 results in cards
                for i, (kode, data) in enumerate(hasil_terurut[:3]):
                    with st.container():
                        st.markdown(f"""
                            <div class="result-card">
                                <h3>🏆 #{i+1}: {data['nama']} ({kode})</h3>
                                <div style="background:linear-gradient(to right, #4CAF50 {data['probabilitas']}%, #444444 {data['probabilitas']}%); 
                                    height:30px; border-radius:5px; margin:1rem 0; position:relative;">
                                    <span style="position:absolute; left:10px; top:5px; color:white; font-weight:bold;">
                                        Probabilitas: {data['probabilitas']:.2f}%
                                    </span>
                                </div>
                                <h4>Gejala terkait:</h4>
                        """, unsafe_allow_html=True)
                        
                        for gejala_kode, nilai in data_penyakit[kode]["gejala"].items():
                            status = "✅ Teramati" if gejala_kode in gejala_terpilih else "❌ Tidak Teramati"
                            st.markdown(f"""
                                <div class="symptom-card">
                                    <p><b>{data_gejala[gejala_kode]}</b><br>
                                    {status} | Nilai probabilitas: {nilai}</p>
                                </div>
                            """, unsafe_allow_html=True)
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                        st.write("")

                # Visualization section
                st.markdown("---")
                st.subheader("📊 Visualisasi Probabilitas Penyakit")
                
                df = pd.DataFrame({
                    "Penyakit": [item[1]["nama"] for item in hasil_terurut],
                    "Probabilitas (%)": [item[1]["probabilitas"] for item in hasil_terurut]
                })
                
                tab1, tab2 = st.tabs(["📈 Grafik Batang", "📋 Tabel Data"])
                
                with tab1:
                    st.bar_chart(df.set_index("Penyakit"), height=400, use_container_width=True)
                
                with tab2:
                    st.dataframe(df.style.highlight_max(axis=0, color='#2E7D32'), use_container_width=True)

# Sidebar with additional information
with st.sidebar:
    st.markdown("""
        <div style="text-align:center; margin-bottom:2rem;">
            <h2 style="color:#81C784;">🍊 Diagnosa Jeruk</h2>
            <p>Sistem pakar untuk mendiagnosis penyakit pada tanaman jeruk menggunakan metode Bayes</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### ℹ️ Tentang Sistem")
    st.markdown("""
        Sistem ini membantu mengidentifikasi penyakit pada tanaman jeruk berdasarkan gejala yang diamati.
        Pilih gejala yang terlihat pada tanaman, lalu klik tombol "Lakukan Diagnosa" untuk mendapatkan hasil.
    """)
    
    st.markdown("### 📌 Petunjuk Penggunaan")
    st.markdown("""
        1. Centang gejala yang teramati
        2. Klik tombol "Lakukan Diagnosa"
        3. Sistem akan menampilkan hasil diagnosis
        4. Lihat probabilitas masing-masing penyakit
    """)
    
    st.markdown("---")
    st.markdown("""
        <div style="text-align:center; color:#BDBDBD;">
            <p>Dikembangkan oleh Danny Putra Ardianto & M. Nabil Pratama</p>
        </div>
    """, unsafe_allow_html=True)