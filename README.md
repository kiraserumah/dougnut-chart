# Doughnut Charts

Web app statis untuk mengedit nilai dan membuat doughnut chart dari Excel. Buka [index.html](index.html) langsung di browser untuk mencoba.

## Pakai

1. Pilih workbook `.xlsx` dengan sheet `AMEA`, `EUAM`, dan `AUNZ`. Bisa memakai workbook sumber (`Status`, `Value`) atau workbook hasil edit (`Status`, `Value`, `Adjusted Value`).
	Status yang digunakan: `Backlog`, `Open`, `Fix in Progress`, `Ready in UAT`, `Passed in UAT`, `Failed in UAT`, `For Client Review`, `Client Test`, dan `Closed`. Ejaan lama `Fix In Progress` serta `Close` tetap diterima.
2. Ubah kolom `Adjusted` pada tab region. Klik kotak warna di samping status untuk mengganti warna chart pada semua region; **Reset warna** mengembalikan palet awal. Chart langsung diperbarui. Unduh Excel untuk menyimpan nilai yang sudah diedit.
3. Unduh PNG region yang aktif, atau unduh semua PNG sekaligus sebagai ZIP berisi `AMEA.png`, `EUAM.png`, `AUNZ.png`, dan `ALL.png`.

PNG tiap region disiapkan untuk slide pada 300 DPI: 945 x 560 piksel, sekitar 8 x 4,74 cm. PNG `ALL.png` menggabungkan tiga region dalam ukuran sekitar 24 x 4,74 cm. Jika aplikasi slide tidak membaca metadata DPI, atur ukuran gambar secara manual sesuai angka tersebut.

Persentase `FIXED` dihitung dari `Adjusted Value` berstatus `Close` atau `Closed` dibagi total `Adjusted Value` region. Workbook diproses di browser, tanpa dikirim ke server aplikasi. Halaman membutuhkan internet untuk memuat SheetJS, Chart.js, JSZip, dan font dari CDN; untuk data sensitif, host salinan library tersebut sendiri sebelum dipakai secara produksi.

Warna pilihan tersimpan di browser (`localStorage`) pada perangkat tersebut, bukan di file Excel. Untuk memakai palet yang sama di perangkat lain, pilih kembali warnanya di sana.

## Deploy

Untuk membatasi akses hanya ke satu orang tanpa database aplikasi, deploy [index.html](index.html) ke **Cloudflare Pages** dan lindungi situs dengan **Cloudflare Access**. Jangan mengandalkan form password yang hanya berjalan di HTML/JavaScript: pengunjung bisa membaca dan melewatinya. Jangan deploy ke hosting publik tanpa proteksi Access.

1. Di Cloudflare Zero Trust, aktifkan identity provider **One-time PIN** (atau Google/Microsoft SSO dengan MFA). Buat kebijakan **Allow** hanya untuk alamat email istri; jangan pakai aturan seluruh domain email atau `Everyone`.
2. Di pengaturan project Pages, aktifkan access policy untuk preview. Atur kebijakan Access yang dibuat agar hanya email tersebut yang mendapat akses.
3. **Lindungi juga alamat produksi `nama-project.pages.dev`**: kebijakan preview saja tidak melindungi alamat ini. Ikuti [panduan Cloudflare untuk pages.dev](https://developers.cloudflare.com/pages/platform/known-issues/#enable-access-on-your-pagesdev-domain): ubah aplikasi Access yang memakai subdomain wildcard menjadi subdomain tanpa wildcard, lalu aktifkan lagi kebijakan preview. Pastikan ada dua aplikasi Access, masing-masing untuk produksi dan preview.
4. Bila memakai custom domain, buat aplikasi Access terpisah untuk hostname tersebut dengan kebijakan email yang sama. Pasang custom domain **sebelum** membuat kebijakan Access untuk domain itu.
5. Uji dalam jendela incognito pada alamat produksi, preview, dan custom domain (jika ada): semuanya harus meminta autentikasi; email lain harus ditolak. Jangan upload file Excel atau folder `charts/` ke hosting.

Login disediakan Cloudflare sebelum halaman HTML dikirim ke browser. Email penerima kode OTP harus dijaga keamanannya; gunakan MFA pada akun email. Akses lokal ke file HTML yang sudah disalin ke komputer orang lain tidak bisa dicabut dengan proteksi hosting. Cloudflare Access tidak menggantikan kebutuhan untuk memercayai script eksternal dari CDN; untuk data sensitif, host library sendiri.

Script Python dan GUI desktop lama tetap tersedia di [doughnut.py](doughnut.py) dan [doughnut_app.py](doughnut_app.py), tetapi tidak diperlukan untuk web app.