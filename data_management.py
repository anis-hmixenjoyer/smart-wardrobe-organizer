import json
import os # Penting: Diperlukan untuk cek file

# Nama file database sederhana kita
WARDROBE_FILE = "wardrobe_data.json"
# Folder tempat gambar disimpan (harus sama dengan di app.py)
IMAGE_DIR = "wardrobe_images"

def load_wardrobe():
    """Memuat data lemari dari file JSON."""
    if not os.path.exists(WARDROBE_FILE):
        return [] 
    try:
        with open(WARDROBE_FILE, "r") as f:
            # Tambahkan pengecekan jika file kosong
            content = f.read()
            if not content:
                return []
            return json.loads(content)
    except json.JSONDecodeError:
        return []

def save_wardrobe_to_file(wardrobe_data):
    """Fungsi internal untuk menyimpan data ke file."""
    with open(WARDROBE_FILE, "w") as f:
        json.dump(wardrobe_data, f, indent=4)

def save_item_to_wardrobe(item_data):
    """Menyimpan item BARU ke file JSON."""
    wardrobe = load_wardrobe()
    wardrobe.append(item_data)
    save_wardrobe_to_file(wardrobe)
    print(f"Item {item_data.get('id', '??')} berhasil disimpan!")

# --- FUNGSI BARU UNTUK DELETE ---
def delete_item_from_wardrobe(item_id):
    """Menghapus item dari database DAN file gambarnya."""
    
    wardrobe = load_wardrobe()
    
    # 1. Cari item yang akan dihapus
    item_to_delete = None
    for item in wardrobe:
        if item.get('id') == item_id:
            item_to_delete = item
            break
            
    if not item_to_delete:
        print(f"Error: Item dengan ID {item_id} tidak ditemukan.")
        return # Keluar jika item tidak ada

    # 2. Hapus file gambar terkait
    image_path = item_to_delete.get('image_path')
    if image_path and os.path.exists(image_path):
        try:
            os.remove(image_path)
            print(f"Berhasil menghapus file gambar: {image_path}")
        except Exception as e:
            print(f"Gagal menghapus file gambar {image_path}: {e}")
    elif image_path:
        print(f"Warning: Path gambar {image_path} dicatat tapi file tidak ditemukan.")
        
    # 3. Buat daftar baru tanpa item yang dihapus
    new_wardrobe = [item for item in wardrobe if item.get('id') != item_id]
    
    # 4. Simpan daftar baru ke file
    save_wardrobe_to_file(new_wardrobe)
    print(f"Berhasil menghapus item {item_id} dari database.")