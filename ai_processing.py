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

def clean_json_response(response_text):
    """
    Helper function to clean and extract JSON from Gemini's response.
    Handles markdown code blocks like ```json ... ``` or ``` ... ```.
    (Fungsi ini disamakan dengan styling_logic.py agar konsisten)
    """
    response_text = response_text.strip()
    if response_text.startswith("```json") and response_text.endswith("```"):
        return response_text[7:-3].strip()  # Remove ```json and ```
    elif response_text.startswith("```") and response_text.endswith("```"):
        return response_text[3:-3].strip()  # Remove ``` and ```
    else:
        return response_text  # Assume it's already clean JSON

def remove_background(image_path):
    """
    Menghapus background dari gambar dan mengembalikan
    sebagai object PIL.Image.
    """
    print(f"Mulai menghapus background dari: {image_path}")
    try:
        # Buka gambar original
        with open(image_path, "rb") as f:
            input_bytes = f.read()
        
        # 2. Gunakan rembg untuk menghapus background
        # Ini mengembalikan bytes dari gambar PNG (dengan transparansi)
        output_bytes = remove(input_bytes)
        
        # 3. Konversi bytes PNG kembali ke object PIL Image
        # Ini penting agar app.py bisa menyimpannya
        processed_image = Image.open(io.BytesIO(output_bytes))
        print("Background berhasil dihapus.")
        return processed_image
    
    except Exception as e:
        print(f"Error saat menghapus background: {e}")
        # Jika gagal, kembalikan saja gambar originalnya
        return Image.open(image_path)

def classify_item(image_path):
    """Mengirim gambar ke Google Gemini Vision API untuk klasifikasi."""
    try:
        # Muat gambar menggunakan PIL
        img = Image.open(image_path)

        # Inisialisasi model Vision (Gunakan model terbaru)
        model = genai.GenerativeModel('gemini-2.5-flash')

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
        
        # Ekstraksi dan pembersihan JSON menggunakan helper function
        ai_output = clean_json_response(response.text)
        
        # Konversi string JSON ke dictionary Python
        parsed_json = json.loads(ai_output)
        
        # Ekstraksi dan pembersihan JSON
        # ai_output = response.text.strip()
        
        # Membersihkan jika ada ```json ... ```
        # if ai_output.startswith("```json"):
        #     ai_output = ai_output[7:-3].strip()
            
        # return json.loads(ai_output)
    
        # Validasi dasar (bisa ditambahkan sesuai kebutuhan)
        required_keys = {"jenis", "warna", "gaya"}
        if not required_keys.issubset(parsed_json.keys()):
            raise ValueError("Respons AI Vision tidak memiliki format JSON yang diharapkan.")

        return parsed_json

    except json.JSONDecodeError as e:
        print(f"Error parsing JSON dari AI Vision: {e}")
        ai_output = response.text # Ambil text mentah sebelum dibersihkan
        print(f"Raw output dari AI Vision: {ai_output}")
        return None # Kembalikan None jika gagal
    except Exception as e:
        print(f"Error saat klasifikasi AI Vision (Gemini): {e}")
        return None