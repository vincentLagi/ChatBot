from langchain.tools import tool

@tool("get_correction_casemaking_knowledge_base")
def get_correction_casemaking_knowledge_base():
    """Returns the knowledge base for correction and case making procedures."""
    return {
        "case_making": {
            "langkah": [
                "1. Lihat jadwal case making pada website messier (perhatikan deadline)",
                "2. Hubungi SubCo untuk briefing cara case making",
                "3. Konsultasi ide soal dengan SubCo sebelum membuat soal",
                "4. Minta template soal dari SubCo lalu buat soal sesuai format",
                "5. Kumpulkan case ke SubCo (bisa melalui Line atau metode lain)",
                "6. Submit queue di 'My Queue' academic.slc.net atau apps-nya",
                "7. Ulangi step 5-6 sampai disetujui SubCo",
                "8. Submit ke messier via menu 'Job' > 'Case Making'",
                "9. Beritahu SubCo setelah submit untuk pengecekan akhir",
                "10. Selesai jika disetujui SubCo di messier"
            ],
            "tips": [
                "Lihat referensi soal di academic.slc.net atau apps-nya",
                "Hubungi SubCo jika bingung atau ada hal yang ambigu",
                "Buat reminder agar tidak lupa jadwal (misal sticky note)"
            ],
            "deadline": "Deadline case making setiap mata kuliah berbeda-beda. Lihat di messier pada menu 'Job' > 'Case Making'.",
            "subco": "Lihat SubCo di website academic.slc.net atau apps-nya melalui menu 'My Queue'."
        },
        "koreksian": {
            "langkah": [
                "1. Lihat jadwal koreksian di messier (perhatikan deadline)",
                "2. Hubungi SubCo untuk briefing dan minta template",
                "3. Download jawaban mahasiswa di messier > 'Marking' > 'Answer to be Graded'",
                "4. Mulai koreksi, tanya SubCo jika ada pertanyaan",
                "5. Kumpulkan ke SubCo (via Line atau lainnya)",
                "6. Submit queue di 'My Queue' academic.slc.net atau apps-nya",
                "7. Ulangi step 5-6 sampai disetujui SubCo",
                "8. Masukkan skor ke messier via template excel di 'Register Student Score'",
                "9. Beritahu SubCo untuk pengecekan terakhir",
                "10. Selesai jika disetujui SubCo di messier"
            ],
            "tips": [
                "Beri komentar detail dan jelas di template koreksi",
                "Tanya SubCo jika template ambigu",
                "Buat reminder agar tidak lupa jadwal"
            ],
            "deadline": "Deadline koreksian berbeda tiap mata kuliah. Cek di messier menu 'Marking'.",
            "subco": "Lihat SubCo di website academic.slc.net atau apps-nya melalui menu 'My Queue'."
        }
    }
