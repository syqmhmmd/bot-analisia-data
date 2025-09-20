# 📊 Dashboard Anggaran Advanced

Dashboard interaktif berbasis **Streamlit** untuk analisis anggaran, realisasi, dan sisa dana.  
Dilengkapi dengan fitur chart interaktif, export Excel lengkap dengan chart, serta ringkasan otomatis.

## Harus install 

	pip install streamlit

	pip install six

	pip install pandas
	
	pip install plotly

	pip install openpyxl

	pip install xlsxwriter

  	pip install matplotlib

   	pip install reportlab

---

## 🚀 Fitur Utama
- Upload file **Excel (.xlsx)** dan analisis langsung.
- Pilih kolom **Anggaran, Realisasi, Kategori, dan Tanggal** secara fleksibel.
- **Filter tanggal** untuk membatasi analisis periode tertentu.
- Ringkasan otomatis:
  - Total Anggaran
  - Total Realisasi
  - Total Sisa
  - Persentase Serapan
  - Persentase Sisa
- Visualisasi:
  - **Pie Chart** distribusi sisa anggaran per kategori.
  - **Bar Chart** perbandingan realisasi dan sisa.
- Export ke Excel dengan:
  - Highlight Top 5 Realisasi & Sisa
  - Chart interaktif langsung tertanam (Pie & Bar)

## 📊 Tampilan dashboard

<img width="1908" height="895" alt="chart" src="https://github.com/user-attachments/assets/899b91f6-035d-40fd-a81a-529ed50e530a" /><img width="1911" height="905" alt="dashboard" src="https://github.com/user-attachments/assets/e54d1c7a-2458-4bd3-a998-c215813ace0e" />


---

## 📂 Struktur Proyek
📁 project/

┣ 📄 AnalisaData.py # Script utama

┣ 📄 README.md # Dokumentasi ini

┗ 📁 images/

┗ 📄 dashboard.png # Screenshot tampilan dashboard

## Cara Run python nya

Buka file nya terus klik kanan pilih " Buka di terminal ".

<img width="1471" height="751" alt="Cuplikan layar 2025-09-20 105830" src="https://github.com/user-attachments/assets/dd71853c-c9b9-4022-8cd6-6bb44e6fb647" />

 	python -m streamlit Nama script utama.py

Setelah itu bisa bikin file excel atau csvnya, bisa juga minta GPT buatin excel dummy

---

## Download disini

 	https://github.com/syqmhmmd/bot-analisia-data.git
  

