import os
import base64 # Penting: Diperlukan untuk encoding gambar
from openai import OpenAI
from PIL import Image
import json

# Inisialisasi Klien OpenAI
# Ini akan otomatis mengambil kunci dari Environment Variable
# yang Anda set di FASE 0 (Langkah 8)
client = OpenAI()

def classify_item(image_path):
    """Mengirim gambar ke OpenAI Vision API untuk klasifikasi."""
    try:
        # Konversi gambar lokal ke base64 (syarat untuk API)
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode("utf-8")

        # Prompt yang cerdas untuk meminta output terstruktur
        prompt = (
            "Klasifikasikan item pakaian dalam gambar ini. "
            "Berikan respons HANYA dalam format JSON berikut: "
            "{'jenis': '...', 'warna': '...', 'gaya': '...'}."
            "Jenis harus salah satu dari: Atasan, Bawahan, Luaran, Gaun, Sepatu, Aksesori. "
            "Gaya harus mencakup model atau bahan (misal: 'Kemeja Polos', 'Jeans Slim Fit')."
        )

        response = client.chat.completions.create(
            model="gpt-4-vision-preview", # Model yang kuat untuk visi
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
                    ],
                }
            ],
            max_tokens=300,
        )
        
        # Ekstraksi dan pembersihan JSON
        ai_output = response.choices[0].message.content.strip()
        
        # Membersihkan jika ada ```json ... ```
        if ai_output.startswith("```json"):
            ai_output = ai_output[7:-3].strip()
            
        return json.loads(ai_output)

    except Exception as e:
        print(f"Error saat klasifikasi AI Vision: {e}")
        return None