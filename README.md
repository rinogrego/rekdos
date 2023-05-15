# rekdos

Sistem Rekomendasi Dosen Pembimbing untuk Mahasiswa menggunakan metode Hungarian dan Kruskal.

Project Kelas Optimasi Jaringan.

## Cara Pakai (User)

1. Register
2. Pergi ke profile
3. Isi nilai-nilai kelas yang tersedia (untuk mahasiswa) ATAU isi kelas-kelas yang diajar (untuk dosen)
4. Kembali ke beranda (navigasi REKDOS), kemudian masuk ke salah satu available runs (jika ada) atau create run (untuk membuat run baru)
5. Pergi ke run yang dipilih/dibikin, kemudian bergabung dengan run
6. Jika semua mahasiswa/dosen sudah bergabung, maka pembuat run dapat melakukan run untuk mendapatkan hasil
7. Hasil akan ter-display dengan table mahasiswa beserta dosen pembimbing rekomendasi yang didapat berdasarkan masing-masing metode

## Penjelasan Implementasi Hungarian

Jika terdapat perbedaan jumlah dosen dan mahasiswa, maka dilakukan *batching*, dimana akan dipilih mahasiswa dengan nilai (jumlah_bobot_mahasiswa)/(jumlah_bobot_total) terbesar sebanyak sejumlah dosen yang ada, ketika jumlah mahasiswa > jumlah dosen. 

Logika yang sama juga diaplikasikan jika jumlah mahasiswa > jumlah dosen.
