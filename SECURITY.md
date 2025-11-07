🛡️ Kebijakan Keamanan Proyek (Security Policy)
Proyek ini adalah prototipe hackathon, sehingga fokus keamanan utama kami adalah perlindungan kredensial selama pengembangan.
Praktik lain diakui penting, namun prioritas tertinggi kami adalah mencegah kebocoran rahasia (secrets).

🔑 Peringatan Kunci API (API Keys)
JANGAN PERNAH commit atau push file yang berisi Kunci API (misalnya, GOOGLE_API_KEY).
Mendorong kredensial ke repositori publik dapat menyebabkan kebocoran instan oleh bot otomatis, yang berisiko menghabiskan dana atau mengunci akun Anda.
Semua Kunci API HARUS disimpan secara lokal di Environment Variables (misal: setx atau export) sesuai panduan setup. 

🚫 Pelaporan Kerentanan (Vulnerability Reporting)
Karena ini adalah proyek lomba hackathon yang berjalan singkat dan bukan produk rilis, kami tidak memiliki program pelaporan kerentanan (bug bounty) formal.
