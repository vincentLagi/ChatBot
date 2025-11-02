from crewai import Task

from unified_system.config.settings import get_additional_information, get_answering_style, get_fallback

general_information =  get_additional_information()
def create_rules_answer_task(agent, user_query: str, context: list = None) -> Task:
    """
    Membuat tugas untuk Agen Jawaban Aturan UAP.
    """
    fallback_message = get_fallback(user_query)
    description = f"""Berdasarkan hasil pencarian dari Agen Rules & Procedure UAP Query Processing Specialist, berikan jawaban yang natural dan percakapan tentang Aturan & Prosedur UAP:
    
    TM = Assignment

    KUERI AWAL PENGGUNA: "{user_query}"

    ========================= DATASET =========================
    {general_information}
    
    [Informasi Penting tentang Ujian]
    - Mahasiswa tidak diperkenankan mengikuti UAP apabila masih terdapat kendala eligibility seperti attendance, document, atau finance. (Hanya untuk UAP, bukan Assignment)
    - Mahasiswa wajib menunjukkan Binusian Flazzcard sebelum memasuki ruangan. (Hanya untuk UAP, bukan Assignment)
    - Mahasiswa wajib duduk sesuai seat yang ditampilkan melalui proyektor oleh pengawas dari Messier.
    - Mahasiswa tidak dapat request menggunakan backup. 
    - Jika setelah (UAP / Assignment) jawaban mahasiswa NF, langsung masukkan dari backup (pastikan last modified masih valid).
    - Mahasiswa yang terlambat lebih dari 30 menit sejak (UAP / Assignment) dimulai tidak diperkenankan masuk ruangan atau mengerjakan (UAP / Assignment).
    - Sebelum mahasiswa diperbolehkan keluar, pastikan jawaban sudah terkumpul, di-finalize, dan backup dimasukkan ke FTP.
    - Pengawas wajib menarik seluruh jawaban melalui NetFileManager v2 & penyimpanan pribadi (fs-user, flashdisk, cloud, dll). Kedua pengawas harus menyimpan backup jawaban mahasiswa.
    
    [Transaksi UAP di Messier]
    - Pada Active Job Messier, tiap pertemuan UAP memiliki dua transaksi: 
    - Teaching: untuk finalize pertemuan.
    - Exam Proctor: untuk keperluan pengawasan dan tampilan layar proyektor.

    [Satu Sesi Sebelum (UAP / Assignment)]
    - Siapkan dan jelaskan slide prosedur (UAP / Assignment) ke mahasiswa.
    - Informasikan bahwa pertemuan berikutnya adalah (UAP / Assignment). Sampaikan bobot nilai, ukuran file maksimum, software yang digunakan, durasi ujian, dan waktu pengerjaan.
    - Informasikan material criteria (UAP / Assignment) dan tanggal penting seperti pengumuman nilai nol, jadwal susulan, dll.
    - Jelaskan prosedur penggunaan aplikasi (lab.slc.net, Galaxion, algo.binus, dll).

    [Persiapan Pelaksanaan (UAP / Assignment)]
    - Minta mahasiswa menunggu di luar saat persiapan ruangan.
    - Gunakan Ruman untuk:
        1. Clear All Drive & FTP.
        2. Cek kembali Drive D seluruh komputer.
        3. Buka aplikasi lab.slc.net / algo.binus / dbprk.slc.net.
        4. Lock USB.
    - Tampilkan seating di proyektor: Messier > Job > Exam Proctor Schedule > Attendance and Exam Official (untuk UAP)
    - Tampilkan seating di proyektor: Messier > Job > Assignemnt Proctor (untuk Assignemnt)
    Report.
    - Tulis waktu pengerjaan di papan.
    - Ingatkan mahasiswa ke toilet sebelum ujian jika diperlukan.
    - Ingatkan prosedur absensi: classroom check-in dan login lab.slc.net sebagai backup.
    - Semua barang mahasiswa WAJIB disimpan di tempat penyimpanan (loker/podium).

    [Sebelum Mahasiswa Masuk Ruangan UAP] (hanya untuk UAP)
    1. Cek Binusian Flazzcard:
    - Jika tidak membawa: 
        - Belum mendekati 30 menit selama ujian berlangsung → lapor LSC → surat perjanjian → boleh ikut ujian.
        - Sudah mendekati 30 menit selama ujiab berlangsung → tetap ikut ujian namun diskors 25 menit setelah ujian, lalu lapor LSC.
    2. Cek Exam Pass Eligibility:
    - Financial: Pending pembayaran → bayar ke VA BCA (BinusMobile > Finance).
    - Document: Pending dokumen → submit di https://binus.ac.id/daftaronline.
    - Attendance: Tidak memenuhi kehadiran minimum → cek di Binusmaya > Academic Services > Attendance Information.

    [Saat (UAP / Assignment) Dimulai]
    - Mahasiswa tidak boleh keluar ruangan mulai menit ke-20 sampai finalize selesai.
    - Jika keluar sebelum menit ke-50, jawaban dinolkan walaupun sudah finalize.

    [Selama (UAP / Assignment)]
    - Tampilkan soal (UAP / Assignment) di layar share screen.
    - Mahasiswa download soal dari akun lab.slc.net masing-masing.
    - FTP hanya digunakan jika ada kendala.
    - Mahasiswa simpan jawaban di Drive D:\, rutin save, dan beri nama file dengan NIM.
    - Ingatkan sisa waktu dan bahwa finalize bersifat permanen.

    [Teguran]
    - Teguran diberikan jika mahasiswa melakukan tindakan mencurigakan:
    - Teguran 1: -10 poin.
    - Teguran 2: -20 poin.
    - Teguran 3: -100 poin.
    - Teguran disampaikan di kelas dan didengar semua mahasiswa.
    - Bukti sontekan dikumpulkan, jangan katakan mahasiswa pasti DO. Sampaikan bahwa akan diproses akademik.

    [Kecurangan]
    - Offense “Cheat (-100)” diberikan di Messier > Exam Proctor atau Assignment Proctor > kolom Offense.
    - Sampaikan ke seluruh kelas.
    - Simpan bukti dan laporkan ke OPMan, lalu buat Official Cheating Report.

    [Perpanjangan Waktu]
    - Diberikan hanya untuk kendala internal (bukan kesalahan mahasiswa).
    - Jika lebih dari 10 menit, koordinasi dengan OPMan.

    [Pengumpulan Jawaban]
    - Ingatkan mahasiswa untuk kumpulkan sebelum waktu habis.
    - Upload jawaban dalam zip file dengan nama sesuai NIM.
    - Mahasiswa harus download kembali untuk memastikan benar sebelum finalize.
    - Upload ke FTP sebagai backup.
    - Setelah ujian, pengawas ambil jawaban dari FTP dan simpan ke NetFileManager & media pribadi.

    [Hal Penting]
    - Jika status NF tapi mahasiswa hadir → upload manual jika backup valid.
    - Jika tidak valid → tetap simpan dan beri catatan.
    - Upload manual WAJIB dilakukan di hari yang sama.
    - Saat verifikasi pertemuan di Messier, konfirmasi upload manual dan pilih kategori serta keterangan yang sesuai. Setelah semua upload selesai, lakukan juga verifikasi manual upload di Miscellaneous > My Manual Upload Verification.

    [Setelah UAP]
    - Gunakan Ruman untuk:
    - Hapus Drive D
    - Clear FTP
    - Clear All Drive

    [Informasi tentang Assignment]
    - Tidak perlu cek Flazzcard.
    - Tidak perlu cek Exam Eligibility.
    - Tidak perlu tampilkan seating di proyektor.
    - Transaksi Messier: "Assignment Proctor" bukan "Exam Proctor.
    - Proses pengerjaan dan pengumpulan tetap sesuai prosedur seperti backup dan finalize.

    ========================= END DATASET =========================
    
    Jika yang ditanyakan adalah tentang Assignment, maka ganti UAP menjadi Assignment di atas.

    TUGAS ANDA:
    1. 📊 Analisa Hasil: Pahami hasil pencarian dari Agen Pemrosesan Kuery
    2. 📋 Ekstrak Info Kunci: Ambil informasi penting dari aturan yang ditemukan
    3. 💬 Jawaban Natural: Jawab pertanyaan pengguna secara natural seperti bot asisten
    4. 🎯 Fokus pada Data: Berikan jawaban berdasarkan konten aktual dari database
    5. 🤔 Reasoning: Pahami konteks pertanyaan dan relevansi data untuk menjawab secara tepat
    
    GAYA JAWABAN:
    {get_answering_style()}
    
    CONTOH JAWABAN YANG BAIK:
    
    Pengguna: "apa yang harus dilakukan jika mahasiswa menyontek?"
    Jawaban Baik: "Berdasarkan aturan UAP, jika ada mahasiswa yang menyontek, pengawas harus mengambil bukti contekan dan mencatat keterangannya di layanan akademik untuk UAS atau messier untuk UAP Lab. Mahasiswa tersebut boleh meninggalkan ruang ujian, dan pengumuman harus disampaikan di depan seluruh peserta ujian."
    
    Pengguna: "keterlambatan berapa menit?"  
    Jawaban Baik: "Maksimal keterlambatan adalah 30 menit. Jika mahasiswa terlambat, pengawas akan menunjukkan jam di sistem internal SLC sebagai bukti. Kalau terlambat lebih dari 30 menit, mahasiswa tidak boleh ikut ujian."
    
    HINDARI:
    ❌ Gunakan format "Jawaban Singkat:", "Penjelasan Detail:", dll
    ❌ Buat struktur formal dengan bullet points yang kaku  
    ❌ Tambahkan informasi yang tidak ada di hasil pencarian
    ❌ Jawab dengan jawaban generik tanpa rujukan data aktual
    ❌ Gunakan template yang sama untuk semua jawaban
    
    HARUS:
    ✅ Jawab natural berdasarkan data dari hasil pencarian
    ✅ Sebutkan detail spesifik dari aturan yang ditemukan
    ✅ Gunakan bahasa percakapan Indonesia
    ✅ Berikan informasi praktis yang dapat ditindaklanjuti

    Berdasarkan jawaban Anda secara ketat pada hasil pencarian yang disediakan. Jangan membuat informasi.
    
    Jika pertanyaan user ambigu atau tidak jelas, awali jawaban dengan fallback berikut:
    {fallback_message}, kemudian jelaskan lagi error sesuai dengan context.
    """
    
    expected_output = f"""Jawaban natural dan percakapan dalam bahasa Indonesia yang:

    1. BERDASARKAN data aktual dari hasil pencarian
    2. MENGGUNAKAN informasi spesifik dari aturan yang ditemukan
    3. GAYA percakapan natural, bukan format formal
    4. REASONING konteks pertanyaan untuk memberikan jawaban yang relevan
    5. INFORMASI praktis yang bermanfaat untuk pengguna
    
    Format: Percakapan natural dalam bahasa Indonesia, informatif tapi santai, dengan menambahkan reasoning untuk memastikan relevansi dan akurasi dalam menjawab pertanyaan."""
    return Task(
        description=description,
        expected_output=expected_output,
        agent=agent,
        context= (context or []) 
    )

def create_rules_workflow_tasks(answer_agent, user_query: str, context: list = None):
    
    
    answer_task = create_rules_answer_task(answer_agent, user_query, context)
    
    return answer_task