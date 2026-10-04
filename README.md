## ✦ Overview

> **YAKIN Vessel Cargo Optimizer** adalah sistem optimasi muatan kapal berbasis CLI yang dirancang untuk menyelesaikan permasalahan alokasi dan penataan kendaraan pada deck kapal (*2D Packing & Vessel Loading Problem*). Proyek ini dibangun sebagai bagian dari **Tugas Besar 1 IF3070 Dasar Inteligensi Artifisial (2026/2027)** oleh **Kelompok Yakin** untuk memaksimalkan *value* muatan kapal menggunakan algoritma *Local Search* dan *Genetic Algorithm*.

**Alur dan fungsionalitas utama mencakup:**

- **Vessel Space Optimization:** Mengatur posisi $(x, y)$, orientasi/rotasi, serta *swapping* kendaraan di dalam *deck* kapal.
- **Strict Maritime Constraints:** Menjamin kargo tidak saling berbenturan (*no overlapping*), berada di dalam batas fisik *deck*, dan tidak melebihi kapasitas beban maksimum kapal.
- **Visual Convergence & Fleet Analytics:** Menyediakan grafik konvergensi skor terhadap iterasi serta visualisasi tata letak muatan *deck* secara real-time.

---

## ✦ Project Structure

Struktur direktori utama dalam pengembangan repositori **IF3070_G12_Yakin**:

```text
IF3070_G12_Yakin/
├── 📁 src/                    → Source code utama algoritma (.py)
│   ├── hill_climbing.py       → Engine Hill Climbing & seluruh variannya
│   ├── simulated_annealing.py → Engine Simulated Annealing & cooling schedule
│   └── genetic_algorithm.py   → Engine GA, kromosom, & operator genetika
├── 📁 output/                 → Output grafik konvergensi & visualisasi deck (.png)
├── 📄 requirements.txt        → Dependencies library (matplotlib, numpy, dll.)
└── 📄 README.md               → Dokumentasi utama proyek
```

---

## ✦ Getting Started

### Prasyarat

Sebelum menjalankan aplikasi, pastikan perangkat telah terinstal:

* **Python** (versi 3.10 atau lebih baru)
* **Pip** package manager

### Build & Installation

1. Clone repository ini:

```bash
git clone https://github.com/larashtm/IF3070_G12_Yakin.git
cd IF3070_G12_Yakin
```

2. Install seluruh dependency yang dibutuhkan:

```bash
pip install -r requirements.txt
```

### Running the App

Jalankan skrip modul kapal/algoritma yang ingin diuji melalui terminal:

```bash
# Simulasi Penataan Kapal dengan Hill Climbing
python src/hill_climbing.py

# Simulasi Penataan Kapal dengan Simulated Annealing
python src/simulated_annealing.py

# Simulasi Penataan Kapal dengan Genetic Algorithm
python src/genetic_algorithm.py
```

---

## ✦ Contributors

Berikut adalah daftar kontributor **Kelompok Yakin** beserta pembagian tugasnya:

| No | Nama | NIM | Kontribusi |
| --- | --- | --- | --- |
| 1 |  **Fathimah Nurhumaida Ramadhani** | 18223052 | **Simulated Annealing Lead** | 
| 2 | **Laras Hati Mahendra** | 18223118 | **Hill Climbing (4 Tipe) & laporan** |
| 3 | **Tyara Penelope Lumban Gaol** | 18224122 | **Genetic Algorithm Lead** |
