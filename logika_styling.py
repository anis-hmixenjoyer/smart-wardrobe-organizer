import os
import google.generativeai as genai
import json
import requests
from dotenv import load_dotenv

# ---------------------------------------------
# PENTING: Panggil load_dotenv() di awal skrip
# ---------------------------------------------
load_dotenv()

# Ambil kunci dari Environment Variable
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY")

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

def get_weather_data(city_name):
    """Mengambil suhu dan kondisi cuaca dari OpenWeatherMap."""
    # global OPENWEATHER_API_KEY # Gunakan kunci yang sudah dimuat di atas

    if not OPENWEATHER_API_KEY:
        print("OPENWEATHER_API_KEY tidak ditemukan. Menggunakan cuaca default.")
        return "Unknown, default to pleasant weather (25°C, Cerah)"
        
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': city_name,
        'appid': OPENWEATHER_API_KEY,
        'units': 'metric', # Celsius
        'lang': 'id'       # Bahasa Indonesia
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status() # Cek error HTTP (misal: 404 kota tidak ditemukan)
        data = response.json()
        
        temperature = data['main']['temp']
        description = data['weather'][0]['description'].capitalize()
        
        # Format string cuaca untuk AI
        weather_string = f"Suhu: {temperature}°C, Kondisi: {description}."
        
        # Tambahkan kondisi jika suhu ekstrem (memberi konteks yang lebih kuat pada AI)
        if temperature > 30:
            weather_string += " Cuaca sangat panas dan terik."
        elif temperature < 15:
            weather_string += " Cuaca dingin. Perlu pakaian berlapis."
            
        return weather_string
        
    except requests.exceptions.RequestException as e:
        print(f"Error saat mengambil data cuaca dari kota '{city_name}': {e}")
        return "Unknown, default to pleasant weather (25°C, Cerah)"

def get_ootd_feedback(item_list, current_weather):
    """
    Mengirim daftar item (sebagai dict/json) ke Google Gemini
    untuk mendapatkan feedback fashion.
    """
    
    # Ubah daftar item menjadi string JSON agar mudah dibaca AI
    items_json_string = json.dumps(item_list, indent=2)
    
    # Inisialisasi model
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # Ini adalah "Prompt Engineering"
    # prompt = (
    #     "Anda adalah 'OOTD Oracle', seorang fashion stylist AI yang ramah dan suportif.\n"
    #     "Tugas Anda adalah menilai kecocokan kombinasi pakaian berikut yang diberikan dalam format JSON:\n"
    #     f"{items_json_string}\n\n"
    #     "Berdasarkan input tersebut, berikan penilaian untuk acara 'Santai' (Casual).\n"
    #     "Berikan respons HANYA dalam format JSON yang valid berikut ini, tanpa teks tambahan di luar JSON:\n"
    #     "{\n"
    #     "  \"rating\": (angka 1-10),\n"
    #     "  \"feedback\": \"(Komentar singkat, misal: 'Kombinasi ini Cocok!' atau 'Hmm, kurang pas.')\",\n"
    #     "  \"saran\": \"(Satu kalimat saran perbaikan atau aksesoris, misal: 'Coba ganti atasan dengan warna netral seperti putih.' atau 'Tambahkan sneakers putih untuk look casual!')\"\n"
    #     "}\n"
    # )
    prompt = (
            "Anda adalah 'OOTD Oracle', seorang fashion stylist AI yang ramah dan suportif.\n"
            "Tugas Anda adalah menilai kecocokan kombinasi pakaian berikut yang diberikan dalam format JSON:\n"
            f"{items_json_string}\n\n"
            
            # === PERUBAHAN DI SINI ===
            f"Kondisi cuaca saat ini adalah: {current_weather}\n"
            "Harap PERTIMBANGKAN cuaca ini dalam penilaian Anda (misal, jangan sarankan jaket tebal saat cuaca panas).\n"
            # === AKHIR PERUBAHAN ===

            "Berdasarkan input tersebut DAN KONDISI CUACA, berikan penilaian untuk acara 'Santai' (Casual).\n"
            "Berikan respons HANYA dalam format JSON yang valid berikut ini, tanpa teks tambahan di luar JSON:\n"
            "{\n"
            "  \"rating\": (angka 1-10),\n"
            "  \"feedback\": \"(Komentar singkat, misal: 'Kombinasi ini Cocok!' atau 'Hmm, kurang pas.')\",\n"
            "  \"saran\": \"(Satu kalimat saran perbaikan ATAU pujian terkait cuaca, misal: 'Pilihan linen-mu pas untuk cuaca panas!' atau 'Mungkin terlalu gerah untuk cuaca ini.')\"\n"
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
        ai_output = response.text # Ambil text mentah sebelum dibersihkan
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
# Catatan: Fungsi get_weather_data() dan get_ootd_feedback() harus sudah didefinisikan
# di atas blok ini, seperti yang telah kita bahas sebelumnya.
if __name__ == "__main__":
    print("--- Memulai Tes Logika Styling dengan Cuaca ---")
    
    # 1. Definisikan Kota yang akan diuji
    # Ganti dengan kota lain, misalnya "Jakarta", "Surabaya", atau "London" untuk cuaca yang kontras
    TEST_CITY = "Depok" 

    # 2. Ambil data cuaca dari API
    # Panggilan ke fungsi get_weather_data (Membutuhkan OPENWEATHER_API_KEY)
    current_weather = get_weather_data(TEST_CITY)
    print(f"Cuaca di {TEST_CITY}: {current_weather}")
    
    # 3. Buat item palsu untuk diuji
    # Pakaian yang dipilih (Contoh: Outfit yang lebih cocok untuk cuaca panas)
    selected_outfit_items = [
        {'jenis': 'Atasan', 'warna': 'Putih', 'gaya': 'Kemeja Linen Tipis'}, 
        {'jenis': 'Bawahan', 'warna': 'Biru Muda', 'gaya': 'Celana Chino Pendek'} 
    ]
    
    # Mencetak item yang sedang diuji
    print("\nItem yang Diuji:")
    for item in selected_outfit_items:
        print(f" - {item['gaya']} ({item['warna']})")

    # 4. Panggil fungsi AI dengan menyertakan item DAN data cuaca
    # Panggilan ke fungsi get_ootd_feedback (Membutuhkan GOOGLE_API_KEY)
    hasil_feedback = get_ootd_feedback(selected_outfit_items, current_weather)
    
    # 5. Tampilkan hasil feedback
    if hasil_feedback and hasil_feedback.get('rating', 0) > 0:
        print("\n[OK] Hasil Feedback AI (Dicetak ke Terminal):")
        print(json.dumps(hasil_feedback, indent=2))
        
        # Contoh cara mengakses feedback spesifik
        print(f"\nRating: {hasil_feedback.get('rating')}/10")
        print(f"Komentar: {hasil_feedback.get('feedback')}")
        print(f"Saran: {hasil_feedback.get('saran')}")
    else:
        print("\n[GAGAL] Gagal mendapatkan feedback.")
        print("Detail:", json.dumps(hasil_feedback, indent=2))
        
    print("\n--- Tes Selesai ---")