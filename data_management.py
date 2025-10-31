import json
import os # Penting: Diperlukan untuk cek file

# Nama file database sederhana kita
WARDROBE_FILE = "wardrobe_data.json"

def load_wardrobe():
    """Memuat data lemari dari file JSON."""
    if not os.path.exists(WARDROBE_FILE):
        return [] # Jika file tidak ada, kembalikan list kosong
    try:
        with open(WARDROBE_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return [] # Kembalikan list kosong jika file JSON korup/kosong

def save_item_to_wardrobe(item_data):
    """Menyimpan item baru ke file JSON."""
    wardrobe = load_wardrobe()
    
    # Tambahkan ID unik ke data item (penting!)
    item_data["id"] = f"CLO{len(wardrobe) + 1:03d}"
    
    wardrobe.append(item_data)
    
    with open(WARDROBE_FILE, "w") as f:
        # Tulis data baru ke file
        json.dump(wardrobe, f, indent=4)
    
    print(f"Item {item_data['id']} berhasil disimpan!")