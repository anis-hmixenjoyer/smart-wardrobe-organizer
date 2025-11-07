import streamlit as st
from PIL import Image
import os
import shutil
import uuid

# Impor fungsi dari file rekan satu tim kamu
try:
    from ai_processing import classify_item
    from data_management import load_wardrobe, save_item_to_wardrobe
    from logika_styling import get_ootd_feedback
except ImportError:
    st.error("Gagal memuat file .py (ai_processing, data_management, logika_styling). Pastikan semua file ada di folder yang sama.")
    st.stop()


# --- Konfigurasi Halaman & Tema Minimalis ---
# Layout 'wide' sangat cocok untuk tampilan modern berbasis card
st.set_page_config(
    page_title="Chic Minimalist Wardrobe",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CSS Injeksi untuk Tema Modern dan Card ---
ACCENT_COLOR = "#FF5C8D"  # Vibrant Pink/Coral
CSS_MODERN = f"""
<style>
/* 1. Global Reset & Font (Clean Sans-Serif) */
.stApp {{
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    color: #333333; /* Darker text */
    background-color: #FAFAFA; /* Very Light Grey Background */
}}

/* 2. Judul Utama */
.main-title {{
    font-size: 2.5em;
    color: {ACCENT_COLOR}; 
    text-align: center;
    font-weight: 700;
    letter-spacing: 1px;
}}

/* 3. Tombol Utama (Accent Color) */
.stButton>button {{
    background-color: {ACCENT_COLOR}; 
    color: white;
    border: none;
    border-radius: 6px;
    font-weight: bold;
    padding: 10px 20px;
    transition: background-color 0.2s;
}}
.stButton>button:hover {{
    background-color: #FF8BA6; /* Lighter on hover */
    color: white;
}}

/* 4. Tampilan Card Item (Paling Penting untuk meniru GitHub ref) */
.item-card-container {{
    border: 1px solid #EEEEEE; /* Very light border */
    border-radius: 8px;
    padding: 0; /* Padding di dalam card */
    margin-bottom: 20px;
    background-color: white; /* White Card Background */
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05); /* Soft shadow */
    overflow: hidden;
}}

.item-card-details {{
    padding: 10px 15px;
}}

/* 5. Streamlit Alerts/Info Boxes */
div[data-testid="stAlert"] {{
    border-left: 6px solid {ACCENT_COLOR} !important;
    border-radius: 4px;
}}

/* Hapus Garis Bawah Header */
.stApp h1, .stApp h2, .stApp h3 {{
    border-bottom: none !important;
    color: #333333;
}}
</style>
"""
st.markdown(CSS_MODERN, unsafe_allow_html=True)


# --- Inisialisasi Direktori ---
TEMP_DIR = "temp_uploads"
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

PERMANENT_DIR = "wardrobe_images"
if not os.path.exists(PERMANENT_DIR):
    os.makedirs(PERMANENT_DIR)

# --- Fungsi Bantuan ---
def save_uploaded_file(uploaded_file):
    """Menyimpan file yang di-upload ke lokasi sementara."""
    try:
        file_extension = os.path.splitext(uploaded_file.name)[1]
        unique_name = str(uuid.uuid4()) + file_extension
        img_path = os.path.join(TEMP_DIR, unique_name)
        with open(img_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return img_path
    except Exception as e:
        st.error(f"❌ Error menyimpan file: {e}")
        return None

def get_new_item_id(wardrobe_list):
    """Membuat ID unik baru."""
    return f"CLO{len(wardrobe_list) + 1:03d}"

def make_image_permanent(temp_path, new_id):
    """Menyalin gambar dari temp ke folder permanen."""
    try:
        file_extension = os.path.splitext(temp_path)[1]
        permanent_filename = f"{new_id}{file_extension}"
        permanent_path = os.path.join(PERMANENT_DIR, permanent_filename)
        
        shutil.copyfile(temp_path, permanent_path)
        os.remove(temp_path)
        return permanent_path, permanent_filename
    except Exception as e:
        st.error(f"❌ Gagal memindahkan file ke lemari: {e}")
        return None, None

# --- Tampilan Utama Aplikasi ---
st.markdown("<h1 class='main-title'>SMART WARDROBE AI 👚</h1>", unsafe_allow_html=True)
st.caption("✨ Asisten Styling Pribadimu.")
st.markdown("---")


# --- Gunakan TABS untuk memisahkan fungsionalitas ---
tab1, tab2, tab3 = st.tabs([
    "📸 ADD ITEM",
    "🗂️ KOLEKSI DIGITAL",
    "💖 MIX & MATCH"
])

# =======================================================================
# --- TAB 1: Katalogisasi / Tambah Baju (Modern Card Layout) ---
# =======================================================================
with tab1:
    st.header("Upload Item Baru")
    st.markdown("Tambahkan pakaianmu satu per satu. AI akan menganalisis detailnya.")
    
    col_upload, col_analysis = st.columns([1, 1.5])
    
    with col_upload:
        st.markdown("#### 1. Upload Foto")
        uploaded_image = st.file_uploader("Pilih gambar pakaian...", type=["jpg", "jpeg", "png"], key="uploader_tab1")
        if uploaded_image:
            st.image(uploaded_image, caption="Item untuk Analisis", use_column_width=True)
        
            if st.button("🔎 ANALISA DENGAN AI", key="analyze_btn_tab1", use_container_width=True, type="primary"):
                with st.spinner("AI sedang menganalisis..."):
                    temp_path = save_uploaded_file(uploaded_image)
                    if temp_path:
                        classification_result = classify_item(temp_path)
                        if classification_result:
                            st.session_state.current_item = classification_result
                            st.session_state.temp_image_path = temp_path
                            st.rerun()
                        else:
                            st.error("❌ Gagal menganalisis gambar.")

    with col_analysis:
        st.markdown("#### 2. Hasil Analisis & Simpan")
        if 'current_item' in st.session_state:
            item_data = st.session_state.current_item
            
            # Tampilan Hasil di Card
            st.markdown("<div class='item-card-container'>", unsafe_allow_html=True)
            st.markdown("<div class='item-card-details'>", unsafe_allow_html=True)
            
            st.subheader("Detail Item")
            st.markdown(f"**Jenis:** **{item_data.get('jenis', 'N/A')}**")
            st.markdown(f"**Warna Utama:** {item_data.get('warna', 'N/A')}")
            st.markdown(f"**Gaya/Motif:** {item_data.get('gaya', 'N/A')}")
            
            # Opsi edit manual
            with st.expander("🛠️ Koreksi Detail (Opsional)"):
                item_data['jenis'] = st.text_input("Jenis Item:", value=item_data.get('jenis', ''), key="edit_jenis")
                item_data['warna'] = st.text_input("Warna Dominan:", value=item_data.get('warna', ''), key="edit_warna")
                item_data['gaya'] = st.text_input("Gaya/Motif:", value=item_data.get('gaya', ''), key="edit_gaya")
            
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
            st.success("Analisis Selesai! Klik Simpan di bawah.")

            if st.button("💾 SIMPAN KE LEMARI PERMANEN", key="save_btn_tab1", type="primary", use_container_width=True):
                # --- LOGIKA SIMPAN ---
                temp_path_to_save = st.session_state.temp_image_path
                current_wardrobe = load_wardrobe()
                new_id = get_new_item_id(current_wardrobe)
                
                permanent_image_path, permanent_filename = make_image_permanent(temp_path_to_save, new_id)
                
                if permanent_image_path:
                    item_data['id'] = new_id
                    item_data['image_path'] = permanent_image_path
                    item_data['filename'] = permanent_filename
                    
                    save_item_to_wardrobe(item_data)
                    st.success(f"Item {new_id} berhasil disimpan! 🥳")
                    st.balloons()
                    
                    del st.session_state.current_item
                    del st.session_state.temp_image_path
                    st.rerun()
                else:
                    st.error("Gagal menyimpan gambar. Proses dibatalkan.")
        else:
            st.info("Upload gambar di sebelah kiri dan klik 'Analisa' untuk melihat detail item di sini.")

# =======================================================================
# --- TAB 2: Lihat Lemari Digital (Visual Grid Card) ---
# =======================================================================
with tab2:
    st.header("Koleksi Pakaian Digital")
    st.markdown("Tampilan Galeri seluruh koleksi Anda. Gunakan filter untuk mencari.")

    wardrobe = load_wardrobe()

    if not wardrobe:
        st.warning("Lemari digitalmu masih kosong. Silakan tambahkan item di tab sebelumnya.")
    else:
        # --- Opsi Filter dengan tata letak horizontal ---
        st.subheader("Filter Koleksi")
        all_jenis = sorted(list(set(item.get('jenis', 'N/A') for item in wardrobe)))
        all_warna = sorted(list(set(item.get('warna', 'N/A') for item in wardrobe)))
        
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            filter_jenis = st.multiselect("Jenis Item:", all_jenis)
        with col_f2:
            filter_warna = st.multiselect("Warna Utama:", all_warna)
        with col_f3:
             filter_gaya = st.text_input("Cari Gaya/Motif:")

        # --- Logika Filter ---
        filtered_wardrobe = wardrobe
        if filter_jenis:
            filtered_wardrobe = [item for item in filtered_wardrobe if item.get('jenis') in filter_jenis]
        if filter_warna:
            filtered_wardrobe = [item for item in filtered_wardrobe if item.get('warna') in filter_warna]
        if filter_gaya:
            filtered_wardrobe = [item for item in filtered_wardrobe if filter_gaya.lower() in item.get('gaya', '').lower()]

        st.markdown(f"**Total Item Ditemukan:** **{len(filtered_wardrobe)}** dari **{len(wardrobe)}**")
        st.markdown("---")

        # --- Tampilan Grid Visual (Card) ---
        num_cols = 5 # 5 kolom per baris untuk tampilan lebar
        cols = st.columns(num_cols)
        
        for i, item in enumerate(filtered_wardrobe):
            with cols[i % num_cols]:
                # Menggunakan CSS Class untuk tampilan card
                st.markdown("<div class='item-card-container'>", unsafe_allow_html=True)
                
                img_path = item.get('image_path', '')
                
                # Tampilkan gambar di bagian atas card
                if os.path.exists(img_path):
                    st.image(img_path, use_column_width=True)
                else:
                    st.image("https://placehold.co/200x200/FFFFFF/CCCCCC?text=No+Image", use_column_width=True)

                # Tampilkan detail di bagian bawah card
                st.markdown("<div class='item-card-details'>", unsafe_allow_html=True)
                st.markdown(f"**{item.get('gaya', 'N/A')}**")
                st.markdown(f"<small>Jenis: {item.get('jenis', 'N/A')} | Warna: {item.get('warna', 'N/A')}</small>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True) 

# =======================================================================
# --- TAB 3: Mix & Match (OOTD Generator) (Visualisasi Pilihan) ---
# =======================================================================
with tab3:
    st.header("AI Stylist: Mix & Match")
    st.markdown("Pilih 2 hingga 3 item dari koleksimu untuk dinilai kecocokannya.")

    wardrobe = load_wardrobe()
    
    if not wardrobe:
        st.warning("Lemari digitalmu masih kosong. Silakan 'ADD ITEM' dulu.")
    else:
        selected_items = []
        st.subheader("Pilih Item")

        # Tampilan Grid Visual dengan Checkbox
        num_cols = 5
        cols = st.columns(num_cols)
        
        for i, item in enumerate(wardrobe):
            with cols[i % num_cols]:
                # Menggunakan Container untuk styling card
                st.markdown("<div class='item-card-container'>", unsafe_allow_html=True)
                
                img_path = item.get('image_path', '')
                
                if os.path.exists(img_path):
                    st.image(img_path, use_column_width=True)
                else:
                    st.image("https://placehold.co/200x200/FFFFFF/CCCCCC?text=No+Image", use_column_width=True)
                
                st.markdown("<div class='item-card-details'>", unsafe_allow_html=True)
                item_label = f"**{item.get('gaya', 'N/A')}** ({item.get('jenis', 'N/A')})"
                
                # Gunakan checkbox kecil di dalam card
                if st.checkbox(item_label, key=f"select_tab3_{item['id']}"):
                    selected_items.append(item)
                
                st.caption(f"Warna: {item.get('warna', 'N/A')}")
                st.markdown("</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("---")

        # --- Logika Cek OOTD ---
        st.subheader("Dapatkan Penilaian Styling")
        items_count = len(selected_items)
        is_ready_to_check = (items_count >= 2 and items_count <= 3)
        
        if items_count == 0:
            st.caption("Pilih minimal 2 item.")
        elif items_count > 3:
            st.error("❌ Pilih maksimal 3 item saja!")

        if st.button("✨ ANALISA OOTD SEKARANG", disabled=(not is_ready_to_check), type="primary", use_container_width=True):
            st.markdown("---")
            
            with st.spinner("AI Stylist sedang menganalisis kecocokan OOTD..."):
                feedback_result = get_ootd_feedback(selected_items)
                
                if feedback_result:
                    st.markdown(f"<h3 style='color:{ACCENT_COLOR};'>💖 Hasil Penilaian Stylist 💖</h3>", unsafe_allow_html=True)
                    
                    rating_val = feedback_result.get('rating', 0)
                    
                    # Tampilan Rating
                    col_rate, col_dummy = st.columns([1, 4])
                    with col_rate:
                        st.metric(label="Rating Kecocokan", value=f"{rating_val}/10")
                    
                    # Tampilan Feedback dan Saran dalam box yang bersih
                    st.markdown("#### Detail Feedback:")
                    
                    col_feedback, col_saran = st.columns(2)
                    
                    with col_feedback:
                        st.markdown("**💬 Komentar AI:**")
                        st.info(f"{feedback_result.get('feedback', 'N/A')}")
                    
                    with col_saran:
                        st.markdown("**💡 Saran Perbaikan:**")
                        st.success(f"{feedback_result.get('saran', 'N/A')}")
                else:
                    st.error("❌ Gagal mendapatkan feedback dari AI Stylist. (Periksa fungsi `get_ootd_feedback`).")