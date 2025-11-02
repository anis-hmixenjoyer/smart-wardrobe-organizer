import streamlit as st
from PIL import Image
import os

# Impor fungsi dari file rekan satu tim kamu
# Pastikan semua file (.py) ada di folder yang sama
from ai_processing import classify_item
from data_management import load_wardrobe, save_item_to_wardrobe
from logika_styling import get_ootd_feedback # (Ini dari Tim 2)

# --- Konfigurasi Halaman ---
st.set_page_config(page_title="OOTD Oracle", page_icon="👗", layout="centered")

# --- Variabel Global ---
TEMP_DIR = "temp_uploads"
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

# --- Fungsi Bantuan ---
def save_uploaded_file(uploaded_file):
    """Menyimpan file yang di-upload ke lokasi sementara."""
    try:
        img_path = os.path.join(TEMP_DIR, uploaded_file.name)
        with open(img_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return img_path
    except Exception as e:
        st.error(f"Error menyimpan file: {e}")
        return None

# --- Tampilan Utama Aplikasi ---
st.title("OOTD Oracle 👗")
st.caption("Anti Bingung Pilih Baju!")

# --- Gunakan TABS untuk memisahkan fungsionalitas ---
tab1, tab2 = st.tabs(["1. Tambah Baju ke Lemari", "2. Mix & Match OOTD"])

# --- TAB 1: Katalogisasi / Tambah Baju ---
with tab1:
    st.header("Upload Pakaianmu")
    st.write("Foto satu item pakaianmu (atasan, bawahan, dll.) untuk disimpan di lemari digital.")
    
    uploaded_image = st.file_uploader("Pilih gambar pakaian...", type=["jpg", "jpeg", "png"])
    
    if uploaded_image:
        st.image(uploaded_image, caption="Gambar yang di-upload", width=300)
        
        # Tombol untuk memproses gambar
        if st.button("Analisa Pakaian Ini", key="analyze_btn"):
            with st.spinner("AI sedang menganalisa gambarmu..."):
                # 1. Simpan file sementara
                temp_path = save_uploaded_file(uploaded_image)
                
                if temp_path:
                    # 2. Panggil AI Vision (dari ai_processing.py)
                    classification_result = classify_item(temp_path)
                    
                    if classification_result:
                        st.success("Analisa Selesai!")
                        st.json(classification_result)
                        
                        # Simpan hasil di session state untuk disimpan nanti
                        st.session_state.current_item = classification_result
                    else:
                        st.error("Gagal menganalisa gambar. Coba lagi.")
    
    # Tombol Simpan (muncul setelah analisa berhasil)
    if 'current_item' in st.session_state:
        if st.button("Simpan ke Lemari Digital", key="save_btn"):
            # Panggil Data Management (dari data_management.py)
            save_item_to_wardrobe(st.session_state.current_item)
            st.success("Berhasil disimpan ke lemari!")
            st.balloons()
            # Hapus dari state setelah disimpan
            del st.session_state.current_item 

# --- TAB 2: Mix & Match (OOTD Generator) ---
with tab2:
    st.header("Cek Kecocokan OOTD")
    st.write("Pilih 2 atau 3 item dari lemari digitalmu untuk dinilai oleh AI Stylist.")

    # 1. Muat data lemari (dari data_management.py)
    wardrobe = load_wardrobe()
    
    if not wardrobe:
        st.warning("Lemari digitalmu masih kosong. Silakan 'Tambah Baju' di Tab 1 dulu.")
    else:
        selected_items = []
        st.write("**Pilih Pakaian:**")

        # 2. Tampilkan semua item sebagai checkbox
        for item in wardrobe:
            # Buat label yang deskriptif untuk checkbox
            item_label = f"({item['id']}) {item['gaya']} - {item['warna']}"
            if st.checkbox(item_label, key=item['id']):
                selected_items.append(item)
        
        st.divider()

        # 3. Tombol untuk memanggil AI Styling
        # Hanya aktif jika pengguna memilih 2 atau 3 item
        is_ready_to_check = (len(selected_items) >= 2)
        
        if st.button("Kasih Feedback, Oracle!", disabled=(not is_ready_to_check)):
            if len(selected_items) > 3:
                st.error("Pilih maksimal 3 item saja ya.")
            else:
                with st.spinner("AI Stylist sedang memadupadankan..."):
                    # 4. Panggil AI Styling (dari styling_logic.py)
                    feedback_result = get_ootd_feedback(selected_items)
                    
                    if feedback_result:
                        # 5. Tampilkan hasil dengan cantik
                        st.subheader("Kata OOTD Oracle:")
                        
                        rating_val = feedback_result.get('rating', 0)
                        st.metric(label="Rating Kecocokan", value=f"{rating_val}/10")
                        
                        st.info(f"**Feedback:** {feedback_result.get('feedback', 'N/A')}")
                        st.success(f"**Saran:** {feedback_result.get('saran', 'N/A')}")
                    else:
                        st.error("Gagal mendapatkan feedback dari AI Stylist.")
        elif not is_ready_to_check:
            st.caption("Pilih minimal 2 item untuk dinilai.")

# Untuk menjalankan aplikasi ini:
# 1. Buka terminal
# 2. Aktifkan venv: .\venv\Scripts\activate
# 3. Jalankan: streamlit run app.py
