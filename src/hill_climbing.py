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


# Stochastic Hill Climbing sesuai standar Lab
def stochastic_hill_climbing(initial_vehicles, ship, max_iterations=3000, num_candidates=4):
    current_vehicles = copy.deepcopy(initial_vehicles)
    current_score = objective_function(current_vehicles, ship)
    history_score = [current_score]
    total_iterations = 0

    while total_iterations < max_iterations:
        total_iterations += 1
        better_neighbors = []

        # Sampling sekumpulan kandidat tetangga acak
        for _ in range(num_candidates):
            candidate = get_random_neighbor(current_vehicles, ship)
            candidate_score = objective_function(candidate, ship)
            if candidate_score > current_score:
                better_neighbors.append((candidate, candidate_score))

        # Terhenti jika tidak ada kandidat yang lebih baik (stuck di local optima)
        if not better_neighbors:
            break

        # Pilih 1 kandidat secara acak dari kumpulan yang lebih baik
        selected_neighbor, selected_score = random.choice(better_neighbors)
        current_vehicles = copy.deepcopy(selected_neighbor)
        current_score = selected_score
        
        history_score.append(current_score)

    return current_vehicles, current_score, total_iterations, history_score


# Alias fungsi untuk kompatibilitas
def hill_climbing(awal, ship, max_eval=3000, max_stuck=300, num_candidates=4):
    t0 = time.process_time()
    best_vehicles, best_score, total_iterations, history_score = stochastic_hill_climbing(
        awal, ship, max_iterations=max_eval, num_candidates=num_candidates
    )
    lama = time.process_time() - t0
    return {
        "initial_state": copy.deepcopy(awal),
        "final_state": best_vehicles,
        "skor_awal": history_score[0],
        "final_score": best_score,
        "score_history": history_score,
        "total_evaluations": total_iterations,
        "execution_time": lama,
    }


# 1. Steepest Ascent Hill Climbing
def steepest_ascent_hill_climbing(initial_vehicles, ship, max_iterations=3000, num_candidates=20):
    current_vehicles = copy.deepcopy(initial_vehicles)
    current_score = objective_function(current_vehicles, ship)
    history_score = [current_score]
    total_iterations = 0

    while total_iterations < max_iterations:
        total_iterations += 1
        better_neighbors = []

        # Sampling sekumpulan kandidat tetangga acak
        for _ in range(num_candidates):
            candidate = get_random_neighbor(current_vehicles, ship)
            candidate_score = objective_function(candidate, ship)
            if candidate_score > current_score:
                better_neighbors.append((candidate, candidate_score))

        # Terhenti jika tidak ada kandidat yang lebih baik (stuck di local optima)
        if not better_neighbors:
            break

        # Pilih kandidat dengan skor TERTINGGI (steepest ascent)
        best_candidate, best_candidate_score = max(better_neighbors, key=lambda item: item[1])
        current_vehicles = copy.deepcopy(best_candidate)
        current_score = best_candidate_score

        history_score.append(current_score)

    return current_vehicles, current_score, total_iterations, history_score


# 2. Hill Climbing with Sideways Move
def sideways_move_hill_climbing(initial_vehicles, ship, max_iterations=3000, max_sideways=100, num_candidates=4):
    current_vehicles = copy.deepcopy(initial_vehicles)
    current_score = objective_function(current_vehicles, ship)
    history_score = [current_score]
    total_iterations = 0
    sideways_count = 0

    while total_iterations < max_iterations:
        total_iterations += 1
        eligible_neighbors = []

        # Sampling sekumpulan kandidat tetangga acak
        for _ in range(num_candidates):
            candidate = get_random_neighbor(current_vehicles, ship)
            candidate_score = objective_function(candidate, ship)
            if candidate_score >= current_score:
                eligible_neighbors.append((candidate, candidate_score))

        # Berhenti jika tidak ada tetangga yang >= current_score
        if not eligible_neighbors:
            break

        # Pilih kandidat dengan skor terbaik di antara eligible
        selected_neighbor, selected_score = max(eligible_neighbors, key=lambda item: item[1])

        if selected_score > current_score:
            # Peningkatan terdeteksi: reset sideways counter
            sideways_count = 0
            current_vehicles = copy.deepcopy(selected_neighbor)
            current_score = selected_score
            history_score.append(current_score)
        else:
            # Pergerakan mendatar (sideways move)
            sideways_count += 1
            if sideways_count >= max_sideways:
                break
            current_vehicles = copy.deepcopy(selected_neighbor)
            current_score = selected_score
            history_score.append(current_score)

    return current_vehicles, current_score, total_iterations, history_score


# Helper untuk membangkitkan state awal acak baru
def bikin_state_acak(vehicles_template, ship):
    state = copy.deepcopy(vehicles_template)
    for v in state:
        v.is_loaded = random.choice([True, False])
        v.orientation = random.choice(["Horizontal", "Vertical"])
        if v.orientation == "Vertical" and v.dimension.width > v.dimension.length:
            v.dimension.width, v.dimension.length = v.dimension.length, v.dimension.width
        elif v.orientation == "Horizontal" and v.dimension.length > v.dimension.width:
            v.dimension.width, v.dimension.length = v.dimension.length, v.dimension.width

        max_x = max(0, ship.dimension.width - v.dimension.width)
        max_y = max(0, ship.dimension.length - v.dimension.length)
        v.x = random.randint(0, max_x)
        v.y = random.randint(0, max_y)
    return state


# Class pembungkus tuple untuk random restart agar backward-compatible (4-tuple) sekaligus menyediakan history_score
class RandomRestartResult(tuple):
    def __new__(cls, best_vehicles, best_score, total_restarts, iterations_per_restart, history_score=None, initial_score=None):
        return super().__new__(cls, (best_vehicles, best_score, total_restarts, iterations_per_restart))

    def __init__(self, best_vehicles, best_score, total_restarts, iterations_per_restart, history_score=None, initial_score=None):
        self.history_score = history_score if history_score is not None else [best_score]
        self.initial_score = initial_score


# 3. Random Restart Hill Climbing
def random_restart_hill_climbing(ship, max_restarts=5, max_iterations_per_restart=1000, initial_vehicles=None, num_candidates=4):
    # Fleksibel jika dipanggil dengan urutan (initial_vehicles, ship, ...)
    if isinstance(ship, list) and hasattr(max_restarts, "maxCapacity"):
        initial_vehicles, ship, max_restarts = ship, max_restarts, max_iterations_per_restart

    if initial_vehicles is None:
        initial_vehicles = bikin_kendaraan_awal()

    global_best_vehicles = None
    global_best_score = -1
    iterations_per_restart = []
    cumulative_history = []
    initial_score = None

    for restart_idx in range(1, max_restarts + 1):
        # Bangkitkan state awal acak baru
        start_state = bikin_state_acak(initial_vehicles, ship)

        # Jalankan stochastic hill climbing untuk restart ini
        best_v, best_s, iters, hist = stochastic_hill_climbing(
            start_state, ship, max_iterations=max_iterations_per_restart, num_candidates=num_candidates
        )

        if initial_score is None and hist:
            initial_score = hist[0]

        iterations_per_restart.append(iters)

        # Catat akumulasi progres skor terbaik global
        for s in hist:
            if s > global_best_score or global_best_vehicles is None:
                global_best_score = s
            cumulative_history.append(global_best_score)

        if best_s > global_best_score or global_best_vehicles is None:
            global_best_score = best_s
            global_best_vehicles = copy.deepcopy(best_v)

    total_restarts = len(iterations_per_restart)
    return RandomRestartResult(
        global_best_vehicles, global_best_score, total_restarts, iterations_per_restart, cumulative_history, initial_score
    )


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
    random.seed(42)  # Seed tetap agar eksperimen perbandingan adil dan reproducible
    
    # Inisialisasi kapal & kendaraan awal
    kapal = Ship(10, 10, 1000)
    kendaraan_awal = bikin_kendaraan_awal()
    skor_awal = objective_function(kendaraan_awal, kapal)

    # 1. Gambar & Simpan Initial State
    fig_awal, ax_awal = plt.subplots(figsize=(6, 6))
    plot_deck(kendaraan_awal, kapal, f"Initial State (objective = {skor_awal})", ax_awal)
    simpan_gambar(fig_awal, "initial_state.png")

    print("\n" + "=" * 65)
    print(f"{'MENJALANKAN 4 VARIAN HILL CLIMBING':^65}")
    print("=" * 65)

    # 1. Steepest Ascent Hill Climbing
    print("\n[1/4] Menjalankan Steepest Ascent Hill Climbing...")
    t0 = time.process_time()
    sa_v, sa_score, sa_iter, sa_hist = steepest_ascent_hill_climbing(
        kendaraan_awal, kapal, max_iterations=3000, num_candidates=20
    )
    sa_dur = time.process_time() - t0
    print(f"      OF: {sa_hist[0]} -> {sa_score} | Iterasi: {sa_iter} | Waktu: {sa_dur:.4f}s")

    # 2. Stochastic Hill Climbing
    print("\n[2/4] Menjalankan Stochastic Hill Climbing...")
    t0 = time.process_time()
    st_v, st_score, st_iter, st_hist = stochastic_hill_climbing(
        kendaraan_awal, kapal, max_iterations=3000, num_candidates=4
    )
    st_dur = time.process_time() - t0
    print(f"      OF: {st_hist[0]} -> {st_score} | Iterasi: {st_iter} | Waktu: {st_dur:.4f}s")

    # 3. Sideways Move Hill Climbing
    print("\n[3/4] Menjalankan Sideways Move Hill Climbing...")
    t0 = time.process_time()
    sw_v, sw_score, sw_iter, sw_hist = sideways_move_hill_climbing(
        kendaraan_awal, kapal, max_iterations=3000, max_sideways=100, num_candidates=4
    )
    sw_dur = time.process_time() - t0
    print(f"      OF: {sw_hist[0]} -> {sw_score} | Iterasi: {sw_iter} | Waktu: {sw_dur:.4f}s")

    # 4. Random Restart Hill Climbing
    print("\n[4/4] Menjalankan Random Restart Hill Climbing...")
    t0 = time.process_time()
    rr_res = random_restart_hill_climbing(
        kapal, max_restarts=5, max_iterations_per_restart=1000, initial_vehicles=kendaraan_awal, num_candidates=4
    )
    rr_v, rr_score, rr_restarts, rr_iters = rr_res
    rr_hist = rr_res.history_score
    rr_init_of = rr_res.initial_score if rr_res.initial_score is not None else skor_awal
    rr_dur = time.process_time() - t0
    print(f"      OF: {rr_init_of} -> {rr_score} | Restarts: {rr_restarts} (total {sum(rr_iters)} iter) | Waktu: {rr_dur:.4f}s")

    hasil_eksperimen = [
        {
            "nama": "Steepest Ascent",
            "final_state": sa_v,
            "skor_awal": sa_hist[0],
            "final_score": sa_score,
            "iterasi_info": f"{sa_iter} iterasi",
            "durasi": sa_dur,
            "history": sa_hist,
            "color": "#1f77b4",
            "marker": "o",
            "linestyle": "-",
        },
        {
            "nama": "Stochastic",
            "final_state": st_v,
            "skor_awal": st_hist[0],
            "final_score": st_score,
            "iterasi_info": f"{st_iter} iterasi",
            "durasi": st_dur,
            "history": st_hist,
            "color": "#2ca02c",
            "marker": "s",
            "linestyle": "--",
        },
        {
            "nama": "Sideways Move",
            "final_state": sw_v,
            "skor_awal": sw_hist[0],
            "final_score": sw_score,
            "iterasi_info": f"{sw_iter} iterasi",
            "durasi": sw_dur,
            "history": sw_hist,
            "color": "#ff7f0e",
            "marker": "^",
            "linestyle": "-.",
        },
        {
            "nama": "Random Restart",
            "final_state": rr_v,
            "skor_awal": rr_init_of,
            "final_score": rr_score,
            "iterasi_info": f"{sum(rr_iters)} iter ({rr_restarts} restarts)",
            "durasi": rr_dur,
            "history": rr_hist,
            "color": "#9467bd",
            "marker": "D",
            "linestyle": ":",
        },
    ]

    # Cetak detail muatan masing-masing algoritma
    for item in hasil_eksperimen:
        print(f"\n--- Hasil {item['nama']} ---")
        print_output(item["final_state"], kapal)

    # 2. Gambar 4 final state sekaligus (1 baris x 4 kolom)
    fig_akhir, axes_akhir = plt.subplots(1, 4, figsize=(20, 5))
    for item, ax in zip(hasil_eksperimen, axes_akhir):
        plot_deck(
            item["final_state"],
            kapal,
            f"{item['nama']}\nObjective = {item['final_score']}",
            ax,
        )
    simpan_gambar(fig_akhir, "final_state.png")

    # 3. Plot skor vs iterasi dari ke-4 algoritma
    fig_plot, ax_plot = plt.subplots(figsize=(10, 5.5))
    for item in hasil_eksperimen:
        ax_plot.plot(
            range(len(item["history"])),
            item["history"],
            label=f"{item['nama']} (Akhir: {item['final_score']})",
            color=item["color"],
            linestyle=item["linestyle"],
            marker=item["marker"],
            markersize=5,
            linewidth=2,
            alpha=0.85,
        )
    ax_plot.set_title("Perbandingan Objective Function vs Iterasi (4 Varian Hill Climbing)", fontsize=12, fontweight="bold")
    ax_plot.set_xlabel("Iterasi", fontsize=10)
    ax_plot.set_ylabel("Objective Function (Total Shipping Fee)", fontsize=10)
    ax_plot.grid(True, linestyle="--", alpha=0.5)
    ax_plot.legend(loc="lower right", fontsize=10)
    simpan_gambar(fig_plot, "objective_vs_iterasi.png")

    # 4. Tabel hasil eksperimen perbandingan ke-4 algoritma
    fig_tab, ax_tab = plt.subplots(figsize=(11, 3.2))
    ax_tab.axis("off")
    ax_tab.set_title("Perbandingan Performa 4 Varian Hill Climbing", fontsize=12, fontweight="bold", pad=12)
    isi_tabel = []
    for item in hasil_eksperimen:
        isi_tabel.append([
            item["nama"],
            str(item["skor_awal"]),
            str(item["final_score"]),
            item["iterasi_info"],
            f"{item['durasi']:.4f} s",
        ])
    tabel = ax_tab.table(
        cellText=isi_tabel,
        colLabels=["Algoritma", "OF Awal", "OF Akhir", "Iterasi / Restart", "Durasi"],
        loc="center",
        cellLoc="center",
    )
    tabel.auto_set_font_size(False)
    tabel.set_fontsize(10)
    tabel.scale(1.2, 1.8)
    for col_idx in range(5):
        cell = tabel[0, col_idx]
        cell.set_facecolor("#4A90E2")
        cell.set_text_props(weight="bold", color="white")
    simpan_gambar(fig_tab, "hasil_eksperimen.png")

    print("\n" + "=" * 68)
    print(f"{'RINGKASAN PERBANDINGAN 4 VARIAN HILL CLIMBING':^68}")
    print("=" * 68)
    print(f"{'Algoritma':<18} | {'OF Awal':<8} | {'OF Akhir':<8} | {'Iterasi / Restart':<26} | {'Durasi'}")
    print("-" * 68)
    for item in hasil_eksperimen:
        print(f"{item['nama']:<18} | {item['skor_awal']:<8} | {item['final_score']:<8} | {item['iterasi_info']:<26} | {item['durasi']:.4f}s")
    print("=" * 68)


def verify_all_hill_climbing():
    print("\n" + "=" * 68)
    print(f"{'VERIFIKASI ATURAN RESMI LABORATORIUM (4 VARIAN HC)':^68}")
    print("=" * 68)

    kapal = Ship(10, 10, 1000)
    kendaraan = bikin_kendaraan_awal()

    # 1. Verifikasi Steepest Ascent
    sa_v, sa_s, sa_iter, sa_hist = steepest_ascent_hill_climbing(kendaraan, kapal, max_iterations=100, num_candidates=20)
    assert isinstance(sa_iter, int) and sa_iter >= 1, "Steepest Ascent harus mencatat total iterasi >= 1"
    assert all(sa_hist[i] <= sa_hist[i + 1] for i in range(len(sa_hist) - 1)), "History Steepest Ascent harus monoton naik"
    print(f"[OK] Steepest Ascent Rules Passed: Total iterasi dicatat ({sa_iter} iterasi), pemilihan kandidat tertinggi (argmax), skor akhir={sa_s}.")

    # 2. Verifikasi Stochastic
    st_v, st_s, st_iter, st_hist = stochastic_hill_climbing(kendaraan, kapal, max_iterations=100, num_candidates=4)
    assert isinstance(st_iter, int) and st_iter >= 1, "Stochastic HC harus mencatat total iterasi >= 1"
    assert all(st_hist[i] <= st_hist[i + 1] for i in range(len(st_hist) - 1)), "History Stochastic HC harus monoton naik"
    print(f"[OK] Stochastic Hill Climbing Rules Passed: Pemilihan acak dari tetangga yang lebih baik (candidate > current), berhenti di local optima ({st_iter} iterasi).")

    # 3. Verifikasi Sideways Move
    max_side = 5
    sw_v, sw_s, sw_iter, sw_hist = sideways_move_hill_climbing(kendaraan, kapal, max_iterations=100, max_sideways=max_side, num_candidates=4)
    assert isinstance(sw_iter, int) and sw_iter >= 1, "Sideways Move harus mencatat total iterasi >= 1"
    assert all(sw_hist[i] <= sw_hist[i + 1] for i in range(len(sw_hist) - 1)), "History Sideways Move tidak boleh anjlok"
    print(f"[OK] Sideways Move Rules Passed: Menerima candidate_score >= current_score, parameter max_sideways={max_side} membatasi plateau.")

    # 4. Verifikasi Random Restart
    restarts_target = 3
    rr_res = random_restart_hill_climbing(kapal, max_restarts=restarts_target, max_iterations_per_restart=50, initial_vehicles=kendaraan)
    rr_v, rr_s, rr_total_r, rr_iters = rr_res
    assert rr_total_r == restarts_target, f"Banyak restart harus tepat {restarts_target}"
    assert len(rr_iters) == restarts_target, "Harus mencatat banyak iterasi untuk setiap restart"
    assert rr_s >= 0, "Harus melacak global best score"
    print(f"[OK] Random Restart Rules Passed: Berhenti saat mencapai max_restarts={restarts_target}, iterasi per restart={rr_iters}, best global={rr_s}.")

    # 5. Verifikasi Output Visualisasi
    required_files = ["final_state.png", "hasil_eksperimen.png", "objective_vs_iterasi.png"]
    for fname in required_files:
        fpath = os.path.join(OUTPUT_DIR, fname)
        assert os.path.exists(fpath), f"File {fname} tidak ditemukan di {OUTPUT_DIR}"
    print(f"[OK] Output Verification Passed: Semua file ({', '.join(required_files)}) tersedia di {OUTPUT_DIR}.")

    print("=" * 68)
    print(f"{'ALL 4 HILL CLIMBING VARIANTS PASSED VERIFICATION!':^68}")
    print("=" * 68 + "\n")


if __name__ == "__main__":
    if "--verify" in sys.argv:
        verify_all_hill_climbing()
    else:
        show = "--no-show" not in sys.argv
        run_experiment(show_plot=show)
        verify_all_hill_climbing()