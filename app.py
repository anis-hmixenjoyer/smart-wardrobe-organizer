import streamlit as st
from PIL import Image
from rembg import remove
import os
import shutil  # Kita perlu ini untuk menyalin file
import base64  # Diperlukan untuk memuat CSS


# Impor fungsi dari file rekan satu tim kamu
# Pastikan semua file (.py) ada di folder yang sama
try:
    from ai_processing import classify_item, remove_background
    # IMPORT FUNGSI BARU (delete_item_from_wardrobe) DARI data_management
    from data_management import load_wardrobe, save_item_to_wardrobe, delete_item_from_wardrobe
    # (Ganti nama 'logika_styling' jika berbeda)
    from logika_styling import get_ootd_feedback, get_weather_data
except ImportError:
    st.error("Failed to load module files (ai_processing, data_management, logika_styling). Make sure all files are in the same folder.")
    st.stop()




# --- Konfigurasi Halaman ---
st.set_page_config(page_title="Smart Wardrobe", page_icon="👗", layout="wide")




# --- FUNGSI DESAIN BARU: Memuat CSS Kustom ---
def load_css(file_name):
    """Fungsi untuk memuat file CSS kustom dari lokal."""
    try:
        with open(file_name, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"CSS file '{file_name}' not found. Make sure it's in the same folder.")


# Panggil fungsi CSS di sini
load_css("style.css")




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
        img_path = os.path.join(TEMP_DIR, uploaded_file.name)
        with open(img_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return img_path
    except Exception as e:
        st.error(f"Error saving file: {e}")
        return None




def get_new_item_id(wardrobe_list):
    """Membuat ID unik baru berdasarkan jumlah item saat ini."""
    return f"CLO{len(wardrobe_list) + 1:03d}"


# --- Tampilan Utama Aplikasi ---
st.title("Smart Wardrobe 👗")
st.caption("Your Personal Fashion Assistant. No more 'I have nothing to wear' moments.")


# --- Gunakan TABS untuk memisahkan fungsionalitas ---
tab1, tab2, tab3 = st.tabs([
    "👕 1. Add Item to Closet",
    "🧐 2. View Digital Closet",
    "✨ 3. Mix & Match OOTD"
])




# =======================================================================
# --- TAB 1: Katalogisasi / Tambah Baju ---
# =======================================================================
with tab1:
    st.header("Upload Your Clothing")
    st.write("Upload a photo of a single clothing item (top, bottom, etc.) to save it to your digital closet.")
   
    uploaded_image = st.file_uploader("Choose a clothing image...", type=["jpg", "jpeg", "png"], key="uploader")
   
    col1, col2 = st.columns(2)
   
    with col1:
        if uploaded_image:
            st.image(uploaded_image, caption="Uploaded Image", use_container_width=True)
           
            if st.button("Analyze This Item", key="analyze_btn", use_container_width=True):
                with st.spinner("AI is analyzing your image..."):
                    temp_path = save_uploaded_file(uploaded_image)
                   
                    if temp_path:
                        classification_result = classify_item(temp_path)
                       
                        if classification_result:
                            st.success("Analysis Complete!")
                            st.session_state.current_item = classification_result
                            st.session_state.temp_image_path = temp_path
                            st.rerun()
                        else:
                            st.error("Failed to analyze image. Please try again.")
   
    with col2:
        if 'current_item' in st.session_state:
            st.subheader("AI Analysis Result")
            st.json(st.session_state.current_item)
            st.info("If the analysis is correct, save it to your closet.")


            if st.button("Save to Digital Closet", key="save_btn", type="primary", use_container_width=True):
               
                item_data = st.session_state.current_item
                temp_path = st.session_state.temp_image_path
               
                with st.spinner("Removing background and saving..."):
                    current_wardrobe = load_wardrobe()
                    new_id = get_new_item_id(current_wardrobe)
                    processed_pil_image = remove_background(temp_path)
                    permanent_path = os.path.join(PERMANENT_DIR, f"{new_id}.png")
                   
                    try:
                        processed_pil_image.save(permanent_path, "PNG")
                        os.remove(temp_path)
                        item_data['id'] = new_id
                        item_data['image_path'] = permanent_path
                        save_item_to_wardrobe(item_data)
                        st.success(f"Item {new_id} saved successfully (without background)!")
                        st.balloons()
                       
                        del st.session_state.current_item
                        del st.session_state.temp_image_path
                        st.rerun()
                       
                    except Exception as e:
                        st.error(f"Failed to save processed image: {e}")




# =======================================================================
# --- TAB 2: Lihat Lemari Digital (Update Desain + Delete) ---
# =======================================================================
with tab2:
    st.header("Your Digital Closet")
    st.write("View, search, and delete all the items you have saved.")


    wardrobe = load_wardrobe()


    if not wardrobe:
        st.warning("Your digital closet is empty. Please add items in Tab 1 first.")
    else:
        # --- Opsi Filter ---
        st.subheader("Filter Closet")
        all_jenis = sorted(list(set(item['jenis'] for item in wardrobe)))
        all_warna = sorted(list(set(item['warna'] for item in wardrobe)))


        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            filter_jenis = st.multiselect("Filter by Type:", all_jenis)
        with col_f2:
            filter_warna = st.multiselect("Filter by Color:", all_warna)
        with col_f3:
            filter_gaya = st.text_input("Search by Style (e.g., 'Shirt', 'Jeans'):")


        # --- Logika Filter ---
        filtered_wardrobe = wardrobe
        if filter_jenis:
            filtered_wardrobe = [item for item in filtered_wardrobe if item['jenis'] in filter_jenis]
        if filter_warna:
            filtered_wardrobe = [item for item in filtered_wardrobe if item['warna'] in filter_warna]
        if filter_gaya:
            filtered_wardrobe = [item for item in filtered_wardrobe if filter_gaya.lower() in item['gaya'].lower()]


        st.divider()
        st.write(f"Showing **{len(filtered_wardrobe)}** of **{len(wardrobe)}** total items.")


        # --- Tampilan Grid Visual (DENGAN CSS CARD) ---
        num_cols = 5
        cols = st.columns(num_cols)
       
        for i, item in enumerate(filtered_wardrobe):
            with cols[i % num_cols]:
                # PERBAIKAN: Bungkus setiap kartu dengan st.container()
                # CSS akan secara otomatis menargetkan container ini
                with st.container():
                    img_path = item.get('image_path', '')
                   
                    if os.path.exists(img_path):
                        st.image(img_path, use_container_width=True)
                    else:
                        st.image("https://placehold.co/200x200/eee/aaa?text=No+Image", use_container_width=True)
                   
                    # Tampilkan detail
                    st.markdown(f"<h6>{item['gaya']}</h6>", unsafe_allow_html=True)
                    st.markdown(f"**Type:** {item['jenis']}")
                    st.markdown(f"**Color:** {item['warna']}")
                    st.caption(f"ID: {item['id']}")
                   
                    # FITUR BARU: Tombol Hapus
                    st.markdown("---") # Pemisah kecil
                    if st.button("Delete", key=f"delete_{item['id']}", use_container_width=True):
                        try:
                            # Panggil fungsi delete dari data_management.py
                            delete_item_from_wardrobe(item['id'])
                            st.toast(f"Item {item['id']} has been deleted.")
                            st.rerun() # Refresh halaman untuk update galeri
                        except Exception as e:
                            st.error(f"Failed to delete item: {e}")




# =======================================================================
# --- TAB 3: Mix & Match (OOTD Generator) (Update Desain) ---
# =======================================================================
with tab3:
    st.header("Check OOTD Compatibility")
    st.write("Select 2 or 3 items from your digital closet to be rated by the AI Stylist.")


    wardrobe = load_wardrobe()
   
    if not wardrobe:
        st.warning("Your digital closet is empty. Please add items in Tab 1 first.")
    else:
        st.subheader("**Select Items:**")


        # --- Tampilan Grid Visual dengan Checkbox (DENGAN CSS CARD) ---
        num_cols = 5
        cols = st.columns(num_cols)
       
        selected_items_data = []
       
        for i, item in enumerate(wardrobe):
            with cols[i % num_cols]:
                # PERBAIKAN: Bungkus setiap kartu dengan st.container()
                with st.container():
                    img_path = item.get('image_path', '')
                   
                    if os.path.exists(img_path):
                        st.image(img_path, use_container_width=True)
                    else:
                        st.image("https://placehold.co/200x200/eee/aaa?text=No+Image", use_container_width=True)
                   
                    item_label = f"({item['id']}) {item['gaya']}"
                   
                    if st.checkbox(item_label, key=f"select_{item['id']}"):
                        selected_items_data.append(item)


        st.divider()


        # --- Logika Cek OOTD ---
        st.subheader("Send to AI Stylist")
       
        city = st.text_input("Enter your city (e.g., Jakarta, New York):", "Jakarta")
       
        is_ready_to_check = (len(selected_items_data) >= 2)
       
        if st.button("Get Feedback, Oracle!", disabled=(not is_ready_to_check), type="primary", use_container_width=True):
           
            if not city:
                st.error("Please enter a city name to check the weather!")
            elif len(selected_items_data) > 3:
                st.error("Please select a maximum of 3 items.")
            else:
                with st.spinner(f"Checking weather in {city} and mixing matches..."):
                   
                    current_weather_info = get_weather_data(city)
                    feedback_result = get_ootd_feedback(selected_items_data, current_weather_info)
                   
                    if feedback_result:
                        st.subheader("The OOTD Oracle says:")
                        rating_val = feedback_result.get('rating', 0)
                        st.metric(label="Compatibility Rating", value=f"{rating_val}/10")
                        st.caption(f"Rating based on weather: {current_weather_info}")
                        st.info(f"**Feedback:** {feedback_result.get('feedback', 'N/A')}")
                        st.success(f"**Suggestion:** {feedback_result.get('saran', 'N/A')}")
                    else:
                        st.error("Failed to get feedback from the AI Stylist.")
        elif not is_ready_to_check:
            st.caption("Select at least 2 items to get a rating.")
