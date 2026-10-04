import copy
import os
import random
import sys
import time

import matplotlib.patches as patches
import matplotlib.pyplot as plt

# Memastikan modul dapat diimpor baik saat dijalankan dari root maupun dari dalam src/
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from main import Ship, Vehicle, move, objective_function, rotate, swap
except ImportError:
    from src.main import Ship, Vehicle, move, objective_function, rotate, swap

# Tentukan direktori output relatif terhadap root repository
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "output", "hill_climbing")


# Bikin 1 tetangga acak dari state sekarang
def get_random_neighbor(vehicles, ship):
    neighbor = copy.deepcopy(vehicles)
    move_type = random.choice(["move", "swap", "rotate", "toggle_load"])
    
    # Move 1: geser posisi kendaraan
    if move_type == "move":
        move(neighbor, ship)
        return neighbor
        
    # Move 2: tukar posisi 2 kendaraan
    if move_type == "swap":
        swap(neighbor)
        return neighbor
        
    # Move 3: putar arah (horizontal <-> vertikal)
    if move_type == "rotate":
        rotate(neighbor, ship)
        return neighbor
        
    # Move 4: naik/turun dari kapal
    if move_type == "toggle_load":
        v = random.choice(neighbor)
        v.is_loaded = not v.is_loaded
        if v.is_loaded:
            max_x = ship.dimension.width - v.dimension.width
            max_y = ship.dimension.length - v.dimension.length
            if max_x < 0 or max_y < 0:
                v.is_loaded = False
            else:
                v.x = random.randint(0, max_x)
                v.y = random.randint(0, max_y)
        return neighbor
        
    return neighbor


# Simple / Stochastic Hill Climbing
def hill_climbing(awal, ship, max_eval=3000, max_stuck=300):
    print(f"Maksimum evaluasi tetangga: {max_eval}")
    t0 = time.process_time()
    
    # Simpan state awal
    state_sekarang = copy.deepcopy(awal)
    skor = objective_function(state_sekarang, ship)
    print(f"Skor Awal Objective: {skor}")
    history = [skor]
    stuck = 0
    iterasi = 0
    print(f"[{iterasi}] State Awal. Skor: {skor}")
    
    while iterasi < max_eval and stuck < max_stuck:
        iterasi += 1
        tetangga = get_random_neighbor(state_sekarang, ship)
        skor_tetangga = objective_function(tetangga, ship)
        history.append(skor_tetangga)
        
        # Kalau dapat yang lebih bagus, pindah
        if skor_tetangga > skor:
            state_sekarang = tetangga
            skor = skor_tetangga
            stuck = 0
            print(f"[{iterasi}] Pindah. Skor Baru: {skor}")
        else:
            stuck += 1
            
    lama = time.process_time() - t0
    skor_awal = history[0]
    return {
        "initial_state": copy.deepcopy(awal),
        "final_state": state_sekarang,
        "skor_awal": skor_awal,
        "final_score": skor,
        "score_history": history,
        "total_evaluations": iterasi,
        "execution_time": lama,
    }


def print_output(state, ship):
    yang_naik = [v for v in state if v.is_loaded]
    total_skor = objective_function(state, ship)
    total_berat = sum(v.weight for v in yang_naik)
    print(f"Total Mobil Dimuat: {len(yang_naik)}")
    print(f"Kapasitas Berat: {total_berat} / {ship.maxCapacity} (Max Capacity)")
    print(f"Total Shipping Fee: {total_skor}")
    print("Daftar Kendaraan di Kapal:")
    for i, v in enumerate(yang_naik, 1):
        print(f"   {i}. Mobil {v.id} (Fee: {v.shippingFee}, Berat: {v.weight})")
        print(f"      - Posisi: X={v.x}, Y={v.y}, Ukuran: {v.dimension.width}x{v.dimension.length}")
    belum = [v.id for v in state if not v.is_loaded]
    if belum:
        print(f"Belum dimuat: {', '.join(belum)}")


# Gambar geladak kapal
def plot_deck(vehicles, ship, judul, ax):
    ax.set_xlim(0, ship.dimension.width)
    ax.set_ylim(0, ship.dimension.length)
    ax.set_aspect("equal")
    ax.set_title(judul)
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_xticks(range(ship.dimension.width + 1))
    ax.set_yticks(range(ship.dimension.length + 1))
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.add_patch(
        patches.Rectangle(
            (0, 0),
            ship.dimension.width,
            ship.dimension.length,
            fill=False,
            linewidth=2,
            edgecolor="black",
        )
    )
    warna = plt.cm.tab10.colors
    for i, v in enumerate(vehicles):
        if not v.is_loaded:
            continue
        c = warna[i % len(warna)]
        ax.add_patch(
            patches.Rectangle(
                (v.x, v.y),
                v.dimension.width,
                v.dimension.length,
                linewidth=1.2,
                edgecolor="black",
                facecolor=c,
                alpha=0.75,
            )
        )
        ax.text(
            v.x + v.dimension.width / 2,
            v.y + v.dimension.length / 2,
            f"{v.id}\n{v.shippingFee}",
            ha="center",
            va="center",
            fontsize=8,
            fontweight="bold",
        )
    # Yang belum naik ditaruh di sudut agar kelihatan
    belum = [v.id for v in vehicles if not v.is_loaded]
    if belum:
        ax.text(
            0.02,
            0.98,
            "Belum dimuat: " + ", ".join(belum),
            transform=ax.transAxes,
            va="top",
            fontsize=8,
        )


# Simpan plot ke folder output
def simpan_gambar(gambar, nama):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    lokasi = os.path.join(OUTPUT_DIR, nama)
    gambar.tight_layout()
    gambar.savefig(lokasi, dpi=150)
    print(f"Gambar disimpan: {lokasi}")
    return lokasi


def bikin_kendaraan_awal():
    v1 = Vehicle("V1", 2, 4, "Horizontal", 150, 200, 1)
    v1.x, v1.y, v1.is_loaded = 0, 0, True
    v2 = Vehicle("V2", 2, 4, "Horizontal", 200, 300, 2)
    v2.x, v2.y, v2.is_loaded = 3, 0, True
    v3 = Vehicle("V3", 3, 3, "Vertical", 80, 100, 3)
    return [v1, v2, v3]


def run_experiment(show_plot=True):
    # Inisialisasi kapal & kendaraan awal
    kapal = Ship(10, 10, 1000)
    kendaraan_awal = bikin_kendaraan_awal()
    skor_awal = objective_function(kendaraan_awal, kapal)
    
    fig_awal, ax_awal = plt.subplots(figsize=(6, 6))
    plot_deck(kendaraan_awal, kapal, f"Initial State (objective = {skor_awal})", ax_awal)
    simpan_gambar(fig_awal, "initial_state.png")
    
    hasil = []
    for run, seed in enumerate([1, 2, 3], start=1):
        random.seed(seed)
        print(f"\n--- EKSPERIMEN RUN {run} ---")
        res = hill_climbing(copy.deepcopy(kendaraan_awal), kapal, 3000, 300)
        res["run_id"] = run
        hasil.append(res)
        print(f"\nHasil Akhir Run {run}:")
        print(f"Objective awal : {res['skor_awal']}")
        print(f"Objective akhir: {res['final_score']}")
        print(f"Jumlah iterasi : {res['total_evaluations']}")
        print(f"Durasi         : {res['execution_time']:.4f} detik")
        print_output(res["final_state"], kapal)

    # Gambar 3 final state sekaligus
    fig_akhir, axes_akhir = plt.subplots(1, 3, figsize=(15, 5))
    for res, ax in zip(hasil, axes_akhir):
        plot_deck(
            res["final_state"],
            kapal,
            f"Final State Run {res['run_id']}\nobjective = {res['final_score']}",
            ax,
        )
    simpan_gambar(fig_akhir, "final_state.png")

    # Plot skor vs iterasi
    fig_plot, ax_plot = plt.subplots(figsize=(9, 5))
    for res in hasil:
        ax_plot.plot(
            range(len(res["score_history"])),
            res["score_history"],
            marker="o",
            markersize=3,
            linewidth=1.5,
            label=f"Run {res['run_id']}",
        )
    ax_plot.set_title("Objective Function vs Jumlah Iterasi")
    ax_plot.set_xlabel("Iterasi")
    ax_plot.set_ylabel("Objective Function")
    ax_plot.grid(True, linestyle="--", alpha=0.4)
    ax_plot.legend()
    simpan_gambar(fig_plot, "objective_vs_iterasi.png")

    # Tabel hasil eksperimen 
    fig_tab, ax_tab = plt.subplots(figsize=(10, 2.8))
    ax_tab.axis("off")
    ax_tab.set_title("Hasil Eksperimen Stochastic Hill Climbing")
    isi_tabel = []
    for res in hasil:
        isi_tabel.append([
            f"Run {res['run_id']}",
            str(res["skor_awal"]),
            str(res["final_score"]),
            str(res["total_evaluations"]),
            f"{res['execution_time']:.4f} s",
        ])
    tabel = ax_tab.table(
        cellText=isi_tabel,
        colLabels=["Run", "OF Awal", "OF Akhir", "Iterasi", "Durasi"],
        loc="center",
    )
    tabel.scale(1.2, 1.6)
    simpan_gambar(fig_tab, "hasil_eksperimen.png")

    print("\n===== RINGKASAN EKSPERIMEN =====")
    for res in hasil:
        print(
            f"Run {res['run_id']}: OF {res['skor_awal']} -> {res['final_score']}, "
            f"iterasi={res['total_evaluations']}, durasi={res['execution_time']:.4f}s"
        )

    if show_plot:
        try:
            plt.show()
        except Exception:
            pass


if __name__ == "__main__":
    show = "--no-show" not in sys.argv
    run_experiment(show_plot=show)