import streamlit as st
import json
import os
import base64
from openai import OpenAI
# Import fungsi LLM yang sudah diserahkan Tim 2
from llm_service import generate_ootd_recommendation 
# Import Pillow jika ingin memproses gambar lokal
# from PIL import Image 

# --- KONFIGURASI DAN INIITALISASI ---

# Inisialisasi OpenAI Client (Bisa diaktifkan jika Tim 1/2 sudah menggunakan API key)
# client = OpenAI()

# Nama file database sederhana (JSON)
WARDROBE_FILE = "wardrobe_data.json"

# Inisialisasi session state
if 'selected_items' not in st.session_state:
    st.session_state.selected_items = []
if 'wardrobe_data' not in st.session_state:
    st.session_state.wardrobe_data = []

# --- FUNGSI DATA & AI ---

# FUNGSI DUMMY: Load Wardrobe (Database)
def load_wardrobe():
    """Memuat data lemari dari file JSON. Menggunakan dummy jika file tidak ada."""
    if os.path.exists(WARDROBE_FILE):
        try:
            with open(WARDROBE_FILE, "r") as f:
                data = json.load(f)
                if isinstance(data, list):
                    st.session_state.wardrobe_data = data
                    return data
                else:
                    return []
        except json.JSONDecodeError:
            return []
    
    # DUMMY DATA UNTUK DEMO AWAL: (Tolong hapus ini dan tambahkan item Anda sendiri!)
    return [
        {"id": "CLO001", "file_path": "https://via.placeholder.com/100x100?text=Kemeja+Putih", "jenis": "Atasan", "warna": "Putih", "gaya": "Kemeja"},
        {"id": "CLO002", "file_path": "https://via.placeholder.com/100x100?text=Celana+Hitam", "jenis": "Bawahan", "warna": "Hitam", "gaya": "Celana Slim Fit"},
        {"id": "CLO003", "file_path": "https://via.placeholder.com/100x100?text=Rok+Merah", "jenis": "Bawahan", "warna": "Merah", "gaya": "Rok Plisket"},
        {"id": "CLO004", "file_path": "https://via.placeholder.com/100x100?text=Sepatu", "jenis": "Sepatu", "warna": "Coklat", "gaya": "Loafers"},
    ]


# FUNGSI DUMMY: AI Vision Classifier (Tim 1 harus mengganti ini!)
def classify_item(image_path):
    """Fungsi dummy klasifikasi AI."""
    # DUMMY: Mengembalikan hasil yang diprediksi
    item_attributes = {
        "jenis": "Atasan",
        "warna": "Hijau Olive",
        "gaya": "T-Shirt Oversize",
    }
    return item_attributes

# FUNGSI DUMMY: LLM Recommender LAMA SUDAH DIHAPUS.
# Sekarang menggunakan generate_ootd_recommendation dari llm_service.py

# FUNGSI UNTUK MENYIMPAN ITEM (Tim 1 harus menyempurnakan!)
def save_item_to_wardrobe(item_data):
    """Menyimpan item baru ke session state dan file JSON."""
    wardrobe = st.session_state.wardrobe_data
    
    # Jika menggunakan data sungguhan, pastikan file_path disimpan dengan benar
    new_id = f"CLO{len(wardrobe) + 1:03d}"
    item_data["id"] = new_id
    
    wardrobe.append(item_data)
    
    # Simpan ke file JSON (untuk persistensi)
    # Catatan: Jika Tim 1 menggunakan format dictionary di JSON, ini perlu disesuaikan.
    with open(WARDROBE_FILE, "w") as f:
        json.dump(wardrobe, f, indent=4)
    
    # Muat ulang data (penting agar UI ter-update)
    st.session_state.wardrobe_data = load_wardrobe()
    return True


# --- FUNGSI HANDLER UNTUK INTERAKSI UI ---
def handle_selection(item_id):
    """Menambah/menghapus item dari daftar pilihan OOTD."""
    if item_id in st.session_state.selected_items:
        st.session_state.selected_items.remove(item_id)
    else:
        st.session_state.selected_items.append(item_id)

# --- TAMPILAN UTAMA STREAMLIT ---

st.set_page_config(page_title="Smart Wardrobe Organizer", layout="wide")

# =========================================================================
# === START: STYLING GLOBAL (CSS) ===
# =========================================================================
st.markdown(
    f"""
    <style>
    
    /* 1. IMPORT FONT POPPINS (konten) dan PACIFICO (judul) */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&family=Pacifico&display=swap');

    /* 2. TERAPKAN FONT POPPINS SECARA GLOBAL (untuk semua teks konten) */
    html, body, [class*="st-"] {{
        font-family: 'Poppins', sans-serif;
    }}
    
    /* 3. TARGET H1 KHUSUS MENGGUNAKAN PACIFICO */
    h1 {{
        font-family: 'Pacifico', cursive; 
        color: #880e4f; /* Maroon/Deep Pink */
        font-weight: 400; 
        padding-bottom: 10px;
        margin-top: -10px;
        font-size: 3em; 
    }}
    
    /* 4. Style Latar Belakang & Header Bagian (H2) */
    body {{
        background-color: #fce4ec; /* Pink Sangat Muda */
    }}
    
    h2 {{
        color: #4a148c; /* Ungu Gelap */
        font-size: 1.8em;
        margin-top: 30px;
        border-left: 5px solid #ff80ab; /* Aksen Pink Cerah */
        padding-left: 10px;
    }}
    
    /* 5. Style Tombol Utama (Generate OOTD) */
    .stButton>button {{
        background: linear-gradient(45deg, #ff80ab, #e040fb); /* Gradien Pink-Ungu */
        color: white;
        border-radius: 20px; 
        border: none;
        padding: 10px 20px;
        font-weight: 600; 
        transition: 0.3s;
        box-shadow: 0 4px 10px rgba(224, 64, 251, 0.4);
    }}
    
    /* 6. Style Border Kontainer */
    .stContainer {{
        border-radius: 15px;
        box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
        padding: 20px;
        margin-bottom: 20px;
        background-color: white;
        border: 1px solid #f8bbd0;
    }}
    
    /* 7. Style untuk Kotak Info/Warning (Penting untuk Output AI) */
    .stAlert {{
        border-radius: 10px;
        padding: 15px;
        background-color: #f3e5f5 !important;
        border: 1px solid #ce93d8 !important;
        color: #4a148c !important;
    }}

    </style>
    """,
    unsafe_allow_html=True
)
# =========================================================================
# === END: STYLING GLOBAL (CSS) ===
# =========================================================================

# Load data di awal
wardrobe_data = load_wardrobe()

# --- SISIPAN LOGO DAN HEADER KUSTOM ---

# Simulasikan Logo Header
st.markdown("""
    <div style="text-align: center; padding: 10px; background: linear-gradient(90deg, #f48fb1, #ce93d8); border-radius: 15px 15px 0 0;">
        <span style="font-size: 3em;">
            ✨👗
        </span>
        <p style="color: white; font-style: italic; margin: 0; font-weight: 300;">Your AI Fashion Companion</p>
    </div>
    """, unsafe_allow_html=True)

# Judul Utama (Menggunakan font Pacifico dari CSS)
st.title("👗 OOTD Generator AI")
st.markdown("""*Transformasikan lemari Anda menjadi katalog digital yang cerdas.*""")
st.markdown("---")

# -----------------------------------------------------------
# 1. BAGIAN KATALOGISASI OTOMATIS (Input)
# -----------------------------------------------------------
st.header("1️⃣ Katalogisasi Pakaian Baru (Organizer)")
# ... (Kode Bagian 1 tidak berubah)
with st.container(border=True):
    uploaded_file = st.file_uploader(
        "Upload Foto Item Pakaian (misal: Atasan, Rok, Sepatu)", 
        type=["jpg", "jpeg", "png"],
        help="Gambar akan dikirim ke AI Vision untuk klasifikasi otomatis."
    )

    if uploaded_file is not None:
        st.image(uploaded_file, caption="Pratinjau Item", width=200)
        
        if st.button("Proses dengan AI", type="primary"):
            
            # Simpan file sementara 
            temp_file_path = os.path.join("uploads", uploaded_file.name)
            os.makedirs("uploads", exist_ok=True)
            with open(temp_file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            with st.spinner("AI Vision sedang menganalisis item..."):
                item_attributes = classify_item(temp_file_path)

            if item_attributes:
                st.success("Klasifikasi AI Selesai!")
                st.json(item_attributes)
                
                # Simpan ke 'database'
                item_attributes["file_path"] = temp_file_path 
                save_item_to_wardrobe(item_attributes)
                
                st.info(f"Item {item_attributes['jenis']} berhasil ditambahkan ke lemari!")
                st.session_state.selected_items = [] 
                st.rerun()
            else:
                st.error("Gagal klasifikasi. Coba lagi.")


st.markdown("---")

# -----------------------------------------------------------
# 2. BAGIAN LEMARI DIGITAL & PEMILIHAN ITEM
# -----------------------------------------------------------
st.header("2️⃣ Lemari Pakaian Digital Anda")

if not wardrobe_data:
    st.info("Lemari Anda masih kosong. Silakan upload item pertama Anda di Bagian 1.")
else:
    st.markdown("#### Klik tombol **'Pilih/Batalkan'** di bawah item untuk memilihnya sebagai dasar OOTD:")
    
    # Tampilkan status pilihan
    st.subheader(f"Total {len(wardrobe_data)} Item | Dipilih: {len(st.session_state.selected_items)}")
    
    cols = st.columns(len(wardrobe_data) if len(wardrobe_data) < 7 else 7) # Maks 7 kolom
    
    for i, item in enumerate(wardrobe_data):
        item_id = item['id']
        is_selected = item_id in st.session_state.selected_items
        
        # Tentukan gaya border dan shadow berdasarkan status pilihan (Sudah diupdate dengan warna feminim)
        border_color = "#ff80ab" if is_selected else "#dee2e6" 
        shadow_style = "0 0 10px rgba(255, 128, 171, 0.7)" if is_selected else "0 2px 4px rgba(0, 0, 0, 0.05)"
        
        with cols[i % len(cols)]:
            # Tampilkan item dengan styling baru
            st.markdown(
                f"""
                <div style="
                    border: 2px solid {border_color}; 
                    border-radius: 8px; 
                    padding: 5px; 
                    text-align: center;
                    box-shadow: {shadow_style};
                    transition: all 0.2s ease-in-out;
                    height: 180px; 
                    background-color: #fff;
                ">
                    <img src="{item["file_path"]}" width="100px" height="100px" style="object-fit: cover; border-radius: 4px;">
                    <p style="font-size: 14px; margin: 5px 0 2px 0; font-weight: bold;">{item["jenis"]}</p>
                    <p style="font-size: 12px; margin: 0; color: #6c757d;">{item["warna"]}</p>
                </div>
                """, 
                unsafe_allow_html=True
            )
            
            # Tombol untuk memilih item
            select_button_label = "✅ BATALKAN" if is_selected else "Pilih Item"
            st.button(
                select_button_label, 
                key=f"select_{item_id}", 
                on_click=handle_selection, 
                args=(item_id,),
                use_container_width=True
            )
            
st.markdown("---")

# -----------------------------------------------------------
# -----------------------------------------------------------
# 3. BAGIAN OOTD GENERATOR (Output) - GANTI DENGAN KODE BARU INI
# -----------------------------------------------------------
st.header("3️⃣ OOTD Oracle: Rekomendasi Cerdas (The Smart)")

if st.session_state.selected_items:
    st.info(f"Item dasar yang akan digunakan ({len(st.session_state.selected_items)} item): {', '.join(st.session_state.selected_items)}")
    
    # 1. Input Kriteria
    criteria = st.text_input(
        "Masukkan Kriteria/Acara untuk Outfit Anda:", 
        "Casual untuk hangout sore di kafe",
        help="Input ini akan menjadi konteks untuk AI stylist."
    )
    
    # 2. Tombol Generate
    if st.button("✨ GENERATE OOTD DENGAN AI", type="primary"):
        if len(st.session_state.selected_items) < 2:
            st.error("Pilih minimal 2 item untuk membuat kombinasi OOTD yang baik.")
        else:
            # Ambil data item yang dipilih
            selected_items_data = [item for item in wardrobe_data if item['id'] in st.session_state.selected_items]
            
            # --- Persiapan Input untuk Fungsi LLM Tim 2 ---
            # 1. Buat list ID & deskripsi item yang dipilih
            selected_item_details = [f"{item['id']} ({item.get('jenis', 'N/A')})" for item in selected_items_data]
            
            # 2. Konversi data lemari menjadi Dictionary JSON String
            wardrobe_data_dict = {item['id']: item for item in wardrobe_data}
            wardrobe_data_json = json.dumps(wardrobe_data_dict)
            # -----------------------------------------------

            with st.spinner("AI Stylist sedang menciptakan outfit terbaik Anda..."):
                # Panggil fungsi LLM Recommender BARU dari llm_service.py
                recommendation_result = generate_ootd_recommendation(
                    selected_item_details=str(selected_item_details),
                    wardrobe_data_json=wardrobe_data_json,
                    ootd_criteria=criteria
                )

            # --- Ekstraksi Data dari Hasil Dictionary ---
            # Dapatkan data sesuai kontrak Tim 2 (score 0.0-1.0)
            score = int(recommendation_result['score'] * 10) # Dikonversi ke skala 0-10
            suggestion_ids = recommendation_result['suggestion_id']
            tip = recommendation_result['tip']
            
            st.subheader("🎉 Hasil Rekomendasi AI")
            
            # --- Visualisasi Skor dan Tip ---
            col_score, col_tip = st.columns([1, 2])
            
            with col_score:
                if score >= 8:
                    status_color = "#4CAF50"
                elif score >= 6:
                    status_color = "#FFC107"
                else:
                    status_color = "#F44336"
                
                st.markdown(f"""
                    <div style="text-align: center; padding: 15px; border: 2px solid {status_color}; border-radius: 8px; background-color: #fff;">
                        <p style="font-size: 1.2em; margin: 0; color: #880e4f;">Skor AI Stylist</p>
                        <p style="font-size: 3em; font-weight: bold; margin: 0; color: {status_color};">{score}/10</p>
                    </div>
                """, unsafe_allow_html=True)
            
            with col_tip:
                suggested_items_info = ", ".join([f"ID {sid}" for sid in suggestion_ids])
                if suggested_items_info:
                    st.info(f"Saran Item Tambahan: Item {suggested_items_info} disarankan.")
                else:
                     st.info(f"Tidak ada item tambahan yang disarankan.")
                st.markdown(f"**Tips Styling Cerdas:** {tip}")

            
            # --- Visualisasi Outfit ---
            st.subheader("Visualisasi Kombinasi Outfit")
            
            # Gabungkan item yang dipilih dan item yang disarankan
            items_to_visualize = selected_items_data.copy()
            
            # Cari data item yang disarankan
            for sid in suggestion_ids:
                suggested_item = next((item for item in wardrobe_data if item['id'] == sid), None)
                if suggested_item and sid not in st.session_state.selected_items:
                    items_to_visualize.append(suggested_item)

            cols_vis = st.columns(len(items_to_visualize) if items_to_visualize else 1)
            
            if items_to_visualize:
                for i, item in enumerate(items_to_visualize):
                    is_suggested = item['id'] not in st.session_state.selected_items
                    caption_text = f"SARAN: {item['jenis']}" if is_suggested else f"Pilihan Awal: {item['jenis']}"
                    
                    with cols_vis[i]:
                        st.image(item["file_path"], width=100)
                        st.caption(caption_text)
            else:
                 st.warning("Gagal menampilkan visualisasi item. Periksa data lemari.")


else:
    st.warning("Pilih item pakaian di Bagian 2 terlebih dahulu untuk mulai mendapatkan saran OOTD.")