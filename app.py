import streamlit as st
from PIL import Image
from rembg import remove
import os
import shutil  # Kita perlu ini untuk menyalin file


# Impor fungsi dari file rekan satu tim kamu
# Pastikan semua file (.py) ada di folder yang sama
try:
    from ai_processing import classify_item, remove_background
    from data_management import load_wardrobe, save_item_to_wardrobe
    # (Ganti nama 'logika_styling' jika berbeda)
    from logika_styling import get_ootd_feedback
except ImportError:
    st.error("Gagal memuat file .py (ai_processing, data_management, logika_styling). Pastikan semua file ada di folder yang sama.")
    st.stop()




# --- Konfigurasi Halaman ---
st.set_page_config(page_title="Smart Wardrobe", page_icon="👗", layout="wide")


# --- Inisialisasi Direktori ---
# Folder untuk upload sementara
TEMP_DIR = "temp_uploads"
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)


# Folder untuk menyimpan gambar lemari secara permanen
PERMANENT_DIR = "wardrobe_images"
if not os.path.exists(PERMANENT_DIR):
    os.makedirs(PERMANENT_DIR)


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


def get_new_item_id(wardrobe_list):
    """Membuat ID unik baru berdasarkan jumlah item saat ini."""
    # Ini akan membuat ID seperti CLO001, CLO002, dst.
    return f"CLO{len(wardrobe_list) + 1:03d}"


def make_image_permanent(temp_path, new_id):
    """Menyalin gambar dari temp ke folder permanen."""
    try:
        # Dapatkan ekstensi file (misal: .jpg, .png)
        file_extension = os.path.splitext(temp_path)[1]
        permanent_path = os.path.join(PERMANENT_DIR, f"{new_id}{file_extension}")
       
        # Salin file
        shutil.copyfile(temp_path, permanent_path)
       
        # Hapus file sementara
        os.remove(temp_path)
        return permanent_path
    except Exception as e:
        st.error(f"Gagal memindahkan file ke lemari: {e}")
        return None


# --- Tampilan Utama Aplikasi ---
st.title("Smart Wardrobe 👗")
st.caption("Asisten Fashion Pribadimu. Tidak ada lagi 'bingung mau pakai baju apa'.")


# --- Gunakan TABS untuk memisahkan fungsionalitas ---
tab1, tab2, tab3 = st.tabs([
    "👕 1. Tambah Baju ke Lemari",
    "🧐 2. Lihat Lemari Digital",
    "✨ 3. Mix & Match OOTD"
])


# =======================================================================
# --- TAB 1: Katalogisasi / Tambah Baju ---
# =======================================================================
with tab1:
    st.header("Upload Pakaianmu")
    st.write("Foto satu item pakaianmu (atasan, bawahan, dll.) untuk disimpan di lemari digital.")
   
    uploaded_image = st.file_uploader("Pilih gambar pakaian...", type=["jpg", "jpeg", "png"], key="uploader")
   
    col1, col2 = st.columns(2)
   
    with col1:
        if uploaded_image:
            st.image(uploaded_image, caption="Gambar yang di-upload", use_container_width=True)
           
            # Tombol untuk memproses gambar
            if st.button("Analisa Pakaian Ini", key="analyze_btn", use_container_width=True):
                with st.spinner("AI sedang menganalisa gambarmu..."):
                    # 1. Simpan file sementara
                    temp_path = save_uploaded_file(uploaded_image)
                   
                    if temp_path:
                        # 2. Panggil AI Vision (dari ai_processing.py)
                        classification_result = classify_item(temp_path)
                       
                        if classification_result:
                            st.success("Analisa Selesai!")
                            # Simpan hasil di session state untuk disimpan nanti
                            st.session_state.current_item = classification_result
                            st.session_state.temp_image_path = temp_path
                            # Refresh halaman untuk menampilkan hasil di kolom 2
                            st.rerun()
                        else:
                            st.error("Gagal menganalisa gambar. Coba lagi.")
   
    with col2:
        # Tombol Simpan (muncul setelah analisa berhasil)
        if 'current_item' in st.session_state:
            st.subheader("Hasil Analisa AI")
            st.json(st.session_state.current_item)
            st.info("Jika hasil analisa sudah benar, simpan ke lemari.")


            if st.button("Simpan ke Lemari Digital", key="save_btn", type="primary", use_container_width=True):
                
                item_data = st.session_state.current_item
                temp_path = st.session_state.temp_image_path
                
                with st.spinner("Menghapus background dan menyimpan..."):
                    # 1. Dapatkan ID baru
                    current_wardrobe = load_wardrobe()
                    new_id = get_new_item_id(current_wardrobe)
                    
                    # 2. PANGGIL FUNGSI BARU (dari ai_processing.py)
                    # Ini mengembalikan object PIL.Image yang sudah bersih
                    processed_pil_image = remove_background(temp_path)
                    
                    # 3. Tentukan path permanen
                    # WAJIB .png agar transparansi tersimpan
                    permanent_path = os.path.join(PERMANENT_DIR, f"{new_id}.png")
                    
                    try:
                        # 4. Simpan gambar yang sudah diproses ke path permanen
                        processed_pil_image.save(permanent_path, "PNG")
                        
                        # Hapus file sementara (yang original)
                        os.remove(temp_path)
                        
                        # 5. Tambahkan ID dan Path Gambar (.png) ke data
                        item_data['id'] = new_id
                        item_data['image_path'] = permanent_path # Path ke file .png
                        
                        # 6. Panggil Data Management
                        save_item_to_wardrobe(item_data)
                        
                        st.success(f"Item {new_id} berhasil disimpan (tanpa background)!")
                        st.balloons()
                        
                        # Hapus dari state setelah disimpan
                        del st.session_state.current_item
                        del st.session_state.temp_image_path
                        st.rerun() # Refresh untuk membersihkan
                        
                    except Exception as e:
                        st.error(f"Gagal menyimpan gambar yang diproses: {e}")


# =======================================================================
# --- TAB 2: Lihat Lemari Digital (BARU) ---
# =======================================================================
with tab2:
    st.header("Isi Lemari Digitalmu")
    st.write("Lihat dan cari semua koleksi pakaian yang sudah kamu simpan.")


    wardrobe = load_wardrobe()


    if not wardrobe:
        st.warning("Lemari digitalmu masih kosong. Silakan 'Tambah Baju' di Tab 1 dulu.")
    else:
        # --- Opsi Filter ---
        st.subheader("Filter Lemari")
        all_jenis = sorted(list(set(item['jenis'] for item in wardrobe)))
        all_warna = sorted(list(set(item['warna'] for item in wardrobe)))


        col_f1, col_f2 = st.columns(2)
        with col_f1:
            filter_jenis = st.multiselect("Filter berdasarkan Jenis:", all_jenis)
        with col_f2:
            filter_warna = st.multiselect("Filter berdasarkan Warna:", all_warna)
       
        filter_gaya = st.text_input("Cari berdasarkan Gaya (misal: 'Kemeja', 'Jeans'):")


        # --- Logika Filter ---
        filtered_wardrobe = wardrobe
        if filter_jenis:
            filtered_wardrobe = [item for item in filtered_wardrobe if item['jenis'] in filter_jenis]
        if filter_warna:
            filtered_wardrobe = [item for item in filtered_wardrobe if item['warna'] in filter_warna]
        if filter_gaya:
            filtered_wardrobe = [item for item in filtered_wardrobe if filter_gaya.lower() in item['gaya'].lower()]


        st.divider()
        st.write(f"Menampilkan **{len(filtered_wardrobe)}** dari **{len(wardrobe)}** total item.")


        # --- Tampilan Grid Visual ---
        num_cols = 5
        cols = st.columns(num_cols)
       
        for i, item in enumerate(filtered_wardrobe):
            with cols[i % num_cols]:
                img_path = item.get('image_path', '')
               
                # Tampilkan gambar jika ada, jika tidak, tampilkan placeholder
                if os.path.exists(img_path):
                    st.image(img_path, use_container_width=True, caption=f"ID: {item['id']}")
                else:
                    st.image("https://placehold.co/200x200/eee/aaa?text=No+Image", use_container_width=True)
               
                # Tampilkan detail
                st.markdown(f"**{item['gaya']}**")
                st.markdown(f"**Jenis:** {item['jenis']}")
                st.markdown(f"**Warna:** {item['warna']}")
                st.markdown("---") # Pemisah antar item


# =======================================================================
# --- TAB 3: Mix & Match (OOTD Generator) ---
# =======================================================================
with tab3:
    st.header("Cek Kecocokan OOTD")
    st.write("Pilih 2 atau 3 item dari lemari digitalmu untuk dinilai oleh AI Stylist.")


    wardrobe = load_wardrobe()
   
    if not wardrobe:
        st.warning("Lemari digitalmu masih kosong. Silakan 'Tambah Baju' di Tab 1 dulu.")
    else:
        selected_items = []
        st.subheader("**Pilih Pakaian:**")


        # --- Tampilan Grid Visual dengan Checkbox ---
        num_cols = 5
        cols = st.columns(num_cols)
       
        for i, item in enumerate(wardrobe):
            with cols[i % num_cols]:
                img_path = item.get('image_path', '')
               
                if os.path.exists(img_path):
                    st.image(img_path, use_container_width=True)
                else:
                    st.image("https://placehold.co/200x200/eee/aaa?text=No+Image", use_container_width=True)
               
                # Buat label yang deskriptif untuk checkbox
                item_label = f"({item['id']}) {item['gaya']}"
                if st.checkbox(item_label, key=f"select_{item['id']}"):
                    selected_items.append(item)
       
        st.divider()


        # --- Logika Cek OOTD ---
        st.subheader("Kirim ke AI Stylist")
        is_ready_to_check = (len(selected_items) >= 2)
       
        if st.button("Kasih Feedback, Oracle!", disabled=(not is_ready_to_check), type="primary", use_container_width=True):
            if len(selected_items) > 3:
                st.error("Pilih maksimal 3 item saja ya.")
            else:
                with st.spinner("AI Stylist sedang memadupadankan..."):
                    # 4. Panggil AI Styling (dari logika_styling.py)
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