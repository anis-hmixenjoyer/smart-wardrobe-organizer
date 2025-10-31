import os
import google.generativeai as genai
from PIL import Image
import json

# Inisialisasi Klien Google
# Ini akan otomatis mengambil kunci GOOGLE_API_KEY
# yang Anda set di FASE 0 (Langkah 8)
try:
    genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
except Exception as e:
    print(f"Error Konfigurasi Google API: {e}. Pastikan GOOGLE_API_KEY sudah di set.")

def classify_item(image_path):
    """Mengirim gambar ke Google Gemini Vision API untuk klasifikasi."""
    try:
        # Muat gambar menggunakan PIL
        img = Image.open(image_path)

        # Inisialisasi model Vision
        model = genai.GenerativeModel('gemini-pro-vision')

        # Prompt yang cerdas untuk meminta output terstruktur
        prompt = (
            "Klasifikasikan item pakaian dalam gambar ini. "
            "Berikan respons HANYA dalam format JSON berikut: "
            "{'jenis': '...', 'warna': '...', 'gaya': '...'}."
            "Jenis harus salah satu dari: Atasan, Bawahan, Luaran, Gaun, Sepatu, Aksesori. "
            "Gaya harus mencakup model atau bahan (misal: 'Kemeja Polos', 'Jeans Slim Fit')."
        )

        # Kirim prompt dan gambar ke model
        response = model.generate_content([prompt, img])
        
        # Ekstraksi dan pembersihan JSON
        ai_output = response.text.strip()
        
        # Membersihkan jika ada ```json ... ```
        if ai_output.startswith("```json"):
            ai_output = ai_output[7:-3].strip()
            
        return json.loads(ai_output)

    except Exception as e:
        print(f"Error saat klasifikasi AI Vision (Gemini): {e}")
        return None