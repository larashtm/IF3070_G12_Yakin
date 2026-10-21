# Tugas Besar 1
# IF3070 Dasar Inteligensi Artifisial 2026/2027

## Penjelasan Tugas

**Vessel Loading Problem** merupakan masalah terkait penempatan kendaraan (*vehicles*) pada kapal (*ship*). Pada permasalahan ini, setiap kendaraan memiliki atribut-atribut yaitu ID, ukuran, orientasi, berat, biaya pengiriman, dan waktu kedatangan. Kendaraan dapat ditempatkan di dalam kapal dengan posisi tertentu atau tidak dimuat apabila *out of bounds*.

Pendekatan yang digunakan adalah pencarian solusi menggunakan tiga algoritma, yaitu *Hill Climbing*, *Simulated Annealing*, dan *Genetic Algorithm*. Ketiga algoritma menggunakan beberapa mekanisme yang sama, seperti berpindah posisi (*move*), bertukar posisi dengan kendaraan lain (*swap*), dan mengubah orientasi (*rotate*). Setiap state kemudian diperiksa berdasarkan batas *ship*, kapasitas maksimum *ship*, serta kondisi kendaraan agar tidak saling *overlapping*.


### Objective Function
Beberapa constraint yang diperhatikan dalam pencarian solusi adalah:
- Permasalahan ini bertujuan untuk memaksimalkan ShippingFee pada kapal.
- Kendaraan tidak boleh saling bertumpuk (no overlapping)
- Tidak boleh ada satu sel grid geladak yang ditempati oleh lebih dari satu kendaraan.
- Kendaraan harus berada di dalam batas geladak.
- Seluruh sel grid yang ditempati suatu kendaraan harus berada di dalam dimensi geladak kapal.
- Truk tidak boleh mengangkut melebihi kapasitasnya.

### Neighbor State
State *neighbor* dapat didapatkan melalui:
- **Move**: memindahkan kendaraan ke posisi $(x,y)$ yang berbeda.
- **Swap**: menukar posisi dua kendaraan.
- **Rotate**: mengubah orientasi kendaraan sehingga dimensi *width* dan *length* dapat berubah.

## Cara Menjalankan Kode Secara Lokal
1. Lakukan clone repository
   ```bash
   git clone https://github.com/larashtm/IF3070_G12_Yakin
3. Buka folder hasil clone
   ```bash
   cd IFIF3070_G12_Yakin
5. Buka folder dan src folder
   ```bash
   cd src
7. Ubah dictionary dari *vehicles* yang akan di-*load* ke *ship* dengan mengubah file vehicles.json
8. Jalankan program main dari kode python di file main
   ```bash
   main.py


## Authors
| No | Nama | NIM | Kontribusi |
| --- | --- | --- | --- |
| 1 |  **Fathimah Nurhumaida Ramadhani** | 18223052 | **Simulated Annealing Lead** | 
| 2 | **Laras Hati Mahendra** | 18223118 | **Hill Climbing (4 Tipe) & laporan** |
| 3 | **Tyara Penelope Lumban Gaol** | 18224122 | **Genetic Algorithm Lead** |
