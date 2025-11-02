import os
import google.generativeai as genai
import json

# Inisialisasi Klien Google
# Ini akan otomatis mengambil kunci GOOGLE_API_KEY
try:
    genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
except Exception as e:
    print(f"Error Konfigurasi Google API: {e}. Pastikan GOOGLE_API_KEY sudah di set.")

def clean_json_response(response_text):
    """
    Helper function to clean and extract JSON from Gemini's response.
    Handles markdown code blocks like ```json ... ``` or ``` ... ```.
    """
    response_text = response_text.strip()
    if response_text.startswith("```json") and response_text.endswith("```"):
        return response_text[7:-3].strip()  # Remove ```json and ```
    elif response_text.startswith("```") and response_text.endswith("```"):
        return response_text[3:-3].strip()  # Remove ``` and ```
    else:
        return response_text  # Assume it's already clean JSON

def get_ootd_feedback(item_list):
    """
    Mengirim daftar item (sebagai dict/json) ke Google Gemini
    untuk mendapatkan feedback fashion.
    """
    
    # Ubah daftar item menjadi string JSON agar mudah dibaca AI
    items_json_string = json.dumps(item_list, indent=2)
    
    # Inisialisasi model (gunakan model yang tersedia dan stabil)
    model = genai.GenerativeModel('gemini-2.5-flash')  # Corrected model name
    
    # Ini adalah "Prompt Engineering"
    # Kita memberi instruksi AI secara spesifik
    prompt = (
        "Anda adalah 'OOTD Oracle', seorang fashion stylist AI yang ramah dan suportif.\n"
        "Tugas Anda adalah menilai kecocokan kombinasi pakaian berikut yang diberikan dalam format JSON:\n"
        f"{items_json_string}\n\n"
        "Berdasarkan input tersebut, berikan penilaian untuk acara 'Santai' (Casual).\n"
        "Berikan respons HANYA dalam format JSON yang valid berikut ini, tanpa teks tambahan di luar JSON:\n"
        "{\n"
        "  \"rating\": (angka 1-10),\n"
        "  \"feedback\": \"(Komentar singkat, misal: 'Kombinasi ini Cocok!' atau 'Hmm, kurang pas.')\",\n"
        "  \"saran\": \"(Satu kalimat saran perbaikan atau aksesoris, misal: 'Coba ganti atasan dengan warna netral seperti putih.' atau 'Tambahkan sneakers putih untuk look casual!')\"\n"
        "}\n"
    )
    
    try:
        # Kirim prompt (teks saja) ke model
        response = model.generate_content(prompt)
        
        # Ekstraksi dan pembersihan JSON menggunakan helper function
        ai_output = clean_json_response(response.text)
        
        # Konversi string JSON ke dictionary Python
        parsed_json = json.loads(ai_output)
        
        # Validasi bahwa JSON memiliki kunci yang diperlukan
        required_keys = {"rating", "feedback", "saran"}
        if not required_keys.issubset(parsed_json.keys()):
            raise ValueError("Respons AI tidak memiliki format JSON yang diharapkan.")
        
        return parsed_json

    except json.JSONDecodeError as e:
        print(f"Error parsing JSON dari AI: {e}")
        print(f"Raw output dari AI: {ai_output}")
        return {
            "rating": 0,
            "feedback": "Error: Respons AI bukan JSON yang valid.",
            "saran": f"Detail error: {str(e)}"
        }
    except Exception as e:
        print(f"Error saat mendapatkan feedback OOTD (Gemini): {e}")
        # ai_output mungkin tidak terdefinisi jika error terjadi sebelum ekstraksi
        ai_output = getattr(response, 'text', 'Tidak ada respons') if 'response' in locals() else 'Tidak ada respons'
        print(f"Raw output dari AI: {ai_output}")
        return {
            "rating": 0,
            "feedback": "Error: Terjadi masalah saat menghubungi AI.",
            "saran": str(e)
        }

# --- BLOK UNTUK TES MANDIRI ---
# Kamu bisa menjalankan file ini langsung untuk tes
# 'python styling_logic.py'
if __name__ == "__main__":
    print("--- Memulai Tes Logika Styling ---")
    
    # Buat 2 item palsu untuk tes
    tes_atasan = {'jenis': 'Atasan', 'warna': 'Biru Langit', 'gaya': 'Kemeja Katun'}
    tes_bawahan = {'jenis': 'Bawahan', 'warna': 'Hitam', 'gaya': 'Jeans Slim Fit'}
    
    print(f"Menguji: {tes_atasan['gaya']} + {tes_bawahan['gaya']}")
    
    # Panggil fungsi utamamu
    hasil_feedback = get_ootd_feedback([tes_atasan, tes_bawahan])
    
    if hasil_feedback and hasil_feedback.get('rating', 0) > 0:
        print("\n[OK] Hasil Feedback AI:")
        print(json.dumps(hasil_feedback, indent=2))
    else:
        print("\n[GAGAL] Gagal mendapatkan feedback.")
        print("Detail:", json.dumps(hasil_feedback, indent=2))
        
    print("\n--- Tes Selesai ---")