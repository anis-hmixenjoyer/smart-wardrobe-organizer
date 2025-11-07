# Impor fungsi dari file yang Anda buat
from ai_processing import classify_item
from data_management import save_item_to_wardrobe, load_wardrobe

print("--- Memulai Tes ---")

# Ganti dengan nama file gambar Anda
gambar_tes = "Atasan.jpg" 

print(f"Mencoba mengklasifikasikan {gambar_tes}...")

# 1. Tes Fungsi AI Vision
hasil_klasifikasi = classify_item(gambar_tes)

if hasil_klasifikasi:
    print("\n[OK] Hasil Klasifikasi AI:")
    print(hasil_klasifikasi)

    # 2. Tes Fungsi Simpan Data
    print("\nMenyimpan ke database...")
    save_item_to_wardrobe(hasil_klasifikasi)

    # 3. Tes Fungsi Baca Data
    print("\nMembaca ulang dari database...")
    database_sekarang = load_wardrobe()
    print(f"\n[OK] Total item di database: {len(database_sekarang)}")
    print(database_sekarang)

else:
    print("\n[GAGAL] Klasifikasi AI tidak berhasil.")

print("\n--- Tes Selesai ---")