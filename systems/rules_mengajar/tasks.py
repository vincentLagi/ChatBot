from crewai import Task
from unified_system.config.settings import get_additional_information, get_fallback, get_answering_style

general_information =  get_additional_information()

def create_practicum_answer_task(agent, search_results_context: list, user_query: str, context: list = None) -> Task:
    """Create task for Practicum Answer Agent"""
    fallback_message = get_fallback(user_query)
    description = f"""Berdasarkan search results dari Query Processing Agent, berikan jawaban yang natural dan conversational tentang Rules & Procedures Practicum:
    
    ORIGINAL USER QUERY: "{user_query}"
    
    TUGAS ANDA:
    1. 📊 Analyze Results: Pahami hasil pencarian dari Query Processing Agent
    2. 📋 Extract Key Info: Ambil informasi penting dari rule yang ditemukan
    3. 💬 Natural Response: Jawab pertanyaan user secara natural seperti assistant bot
    4. 🎯 Focus on Data: Berikan jawaban berdasarkan content actual dari database
    
    You are provided with the full rules and guidelines for assistant during practicum.

        ========================= DATASET =========================
        {general_information}

        [Batas Keterlambatan Mahasiswa]
        Mahasiswa memiliki batas telat kehadiran 30 menit sejak praktikum dimulai.
        Apabila mahasiswa baru tiba melebihi menit ke-30 dan belum melakukan classroom attendance, maka kehadiran mahasiswa tidak akan didatakan. 
        Mahasiswa tetap diperkenankan masuk kelas, namun tidak perlu ditandakan "late", langsung uncheck saja.

        [Akses Zoom untuk Asisten]
        Asisten dapat mengakses link Zoom dengan cara scan QR code di PC tutor. 
        Hal ini bersifat wajib untuk perkuliahan yang berjalan onsite.
        Asisten tetap wajib join Zoom Meeting dan mengikuti prosedur record pengajaran.
        Link Zoom Meeting bisa diakses melalui scan QR code di PC tutor, Binusmaya, atau Messier.

        [Persiapan Sebelum Praktikum dimulai]
        Hanya untuk sesi pertama praktikum:
        1. Siapkan dan lengkapi informasi pada Slide Introduction to Students untuk setiap mata kuliah yang diajarkan.
        2. Siapkan grup LINE / WhatsApp berisikan semua mahasiswa dan asisten lainnya untuk setiap mata kuliah yang diajarkan.
        3. Siapkan link dan QR code invitation group untuk dibagikan ke mahasiswa.
        4. Jelaskan Slide Introduction to Students ke mahasiswa.

        [Pakaian Wajib untuk Asisten]
        - Kemeja dimasukkan.
        - Dasi (untuk pria) dan Name Tag wajib.
        - Wajib melapor apabila:
          - Terlambat datang
          - Tidak memakai pakaian yang sesuai
          - Name tag rusak / tidak membawa name tag
          - Lupa login Messier
          - Tidak bisa menyalakan kamera

        [Ketentuan Pakaian Asisten per Hari]
        Senin, Selasa, Kamis:
        - Wajib berpakaian formal dan seragam.
        - Kemeja putih atau batik resmi BINUS.
        - Celana panjang hitam.

        Rabu:
        - Boleh memakai kemeja atau batik berwarna bebas.
        - Bawahan (celana/rok) berwarna bebas.
        - Dilarang memakai kaos polo atau kaos berkerah.
        - Jeans dilarang.

        Jumat & Sabtu:
        - Boleh memakai kemeja atau batik berwarna bebas.
        - Celana/rok berwarna bebas.
        - Kaos polo diperbolehkan.
        - Jeans diperbolehkan jika tidak ada sesi praktikum.

        [Keterlambatan Asisten]
        - Maksimal keterlambatan adalah 10 menit sebelum praktikum dimulai.
        - Jika terlambat < 30 menit → status Late, pengganti dibatalkan.
        - Jika terlambat ≥ 30 menit atau tanpa kabar → status Alpha, pengganti tetap menggantikan, dan yang digantikan tidak bisa menggantikan kembali. Hal ini mempengaruhi KPI.

        [Prosedur Asistensi Praktikum]

        1. Kehadiran Asisten:
        - Asisten WAJIB relogin Messier dari PC lokal ruangan untuk pendataan kehadiran.
        - Join Zoom Meeting melalui scan QR di PC tutor.

        2. Kesiapan Ruangan:
        - Nyalakan lampu dan PC.
        - Cek perangkat: Proyektor, Mic/Saramonic, Speaker.
        - Ruman: Clear Drive D, Clear FTP, buka software, slc.net, dan poster (termasuk poster NAR).

        3. Pelaksanaan Asistensi:
        - Ajarkan materi sesuai durasi.
        - Jika ada waktu sisa, berikan materi tambahan atau latihan, jangan AFK.
        - Asisten tidak boleh memberi izin ke mahasiswa (kecuali izin ke toilet).
        - Dilarang:
          - Mengerjakan TPA, RIG, tugas kuliah, atau hal tidak relevan.
          - Chatting, bermain game, browsing tidak relevan.
          - Membagikan kode/jawaban praktikum (boleh tutorial berupa video/gambar via forum).
          - Membagikan template proyek/quiz take-home tanpa konsultasi SubCo.
          - Mengajarkan jawaban proyek.
          - Menggunakan soal quiz/UAP untuk mengajar.

        - Semua materi di CO harus diajarkan.
        - Materi penting untuk UAP wajib dijelaskan secara detail.
        - Jika CO sedikit, jelaskan lebih dalam.
        - Materi boleh dibagi antar asisten jika waktu tidak cukup.
        - Pastikan semua materi selesai sebelum quiz/UAP.

        4. Verifikasi Asistensi:
        - Attendance Log & Session Log terbuka 30 menit sebelum dan sesudah praktikum.
        - Centang CO di Messier dan isi NIM & password Binusmaya mahasiswa untuk verifikasi.

        5. Penyelesaian Asistensi:
        - Cek kerapian ruang & PC:
          - Clear semua drive.
          - Cek Drive kosong.
          - Logout semua aplikasi.
          - Rapikan kursi.
          - Pastikan tidak ada barang tertinggal.
          - Matikan lampu.
          - Kunci ruangan dan kembalikan ke R.724 (KMG) / A1408 (ALS).
        - Jika ada barang tertinggal, bawa ke R.724 (KMG) / A1408 (ALS) dan catat ruang, tanggal, dan waktu.

        [Kelas Tambahan]
        Pengajar atau asisten dapat memberikan kelas tambahan di luar jadwal praktikum. Bila dilakukan, pengajar akan mendapatkan reward berupa poin tambahan untuk involvement, dengan ketentuan:

        - Minimal 30% dari total mahasiswa hadir. Jika kehadiran kurang dari 30%, maka tidak akan mendapatkan poin involvement.
        - Mahasiswa akan mengisi daftar hadir (absen) saat kelas tambahan berlangsung melalui Binusmaya Practicum.

        Langkah-langkah untuk membuat kelas tambahan:
        - Ajukan peminjaman ruangan di: https://labfacility.apps.binus.ac.id/ (pastikan status sudah accepted).
        - Request Zoom meeting ke Qman via email.
        - Setelah peminjaman disetujui, buat kelas tambahan di Binusmaya Practicum → Menu: Extra Class > Create Extra Class.

        Cara mahasiswa melakukan absensi:
        - Saat kelas berlangsung, tekan tombol *Start Absent* di Binusmaya Practicum agar absensi tercatat.
        - Batas waktu mencatat absensi adalah 120 menit setelah *Start Absent* ditekan.

        ========================= END DATASET =========================

        Based on the user query, your job is to identify the relevant section(s) from the above rules.
        You should:
        - Identify the search method or matching technique used.
        - Report how many sections matched the query.
        - Display the most relevant sections or rules based on the query.
        - Add any related metadata or summary if needed.

        
    GAYA MENJAWAB:
    {get_answering_style()}
    
    HINDARI:
    ❌ Format formal atau template kaku
    ❌ Informasi yang tidak ada di search results
    ❌ Bahasa korporat atau terlalu formal
    ❌ Struktur "Konsekuensi", "Catatan Penting", dll
    
    CONTOH RESPONSE STYLE:
    - "Kalau mau ngambil kunci ruangan, kamu harus ke 724 Support Administration Staff dulu..."
    - "Sebelum mengajar, ada beberapa hal yang perlu dipersiapkan..."
    - "Untuk setup Ruman, langkah-langkahnya adalah..."
    - "Kalau telat mengajar, ada batas waktunya yaitu..."
    
    CONTEXT DARI SEARCH RESULTS:
    {search_results_context}
    
    Jawab dengan gaya natural dan helpful, seperti sedang membantu teman yang bertanya tentang prosedur praktikum.
    
    Jika pertanyaan user ambigu atau tidak jelas, awali jawaban dengan fallback berikut:
    {fallback_message}, kemudian jelaskan lagi error sesuai dengan context."""
    
    expected_output = """Jawaban natural dalam Bahasa Indonesia yang:

    1. **Langsung menjawab** pertanyaan user berdasarkan search results
    2. **Conversational tone** - seperti berbicara dengan teman/kolega
    3. **Praktis dan actionable** - fokus pada langkah-langkah yang bisa dilakukan
    4. **Berdasarkan data actual** - semua informasi dari database search results
    5. **Explain the why** - berikan context mengapa prosedur tersebut penting
    
    Response harus natural, helpful, dan mudah dipahami tanpa format formal."""
    
    return Task(
        description=description,
        expected_output=expected_output,
        agent=agent,
        context=context
    ) 