import copy
import os
import random
import sys
import time

import matplotlib.patches as patches
import matplotlib.pyplot as plt

# atur path biar bisa import main dari root atau src/
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from main import Ship, Vehicle, move, objective_function, rotate, swap
except ImportError:
    from src.main import Ship, Vehicle, move, objective_function, rotate, swap

# folder buat nyimpen hasil gambar
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "output", "hill_climbing")


# bikin 1 tetangga acak dari state sekarang
def get_random_neighbor(vehicles, ship):
    neighbor = copy.deepcopy(vehicles)
    move_type = random.choice(["move", "swap", "rotate", "toggle_load"])

    # aksi 1: geser posisi koordinat
    if move_type == "move":
        move(neighbor, ship)
        return neighbor

    # aksi 2: tuker posisi 2 mobil
    if move_type == "swap":
        swap(neighbor)
        return neighbor

    # aksi 3: putar arah mobil (horizontal <-> vertikal)
    if move_type == "rotate":
        rotate(neighbor, ship)
        return neighbor

    # aksi 4: naik/turunin mobil dari kapal
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


# stochastic hill climbing: pilih acak dari tetangga yang lebih bagus
def stochastic_hill_climbing(initial_vehicles, ship, max_iterations=3000, num_candidates=4, verbose=False):
    # inisialisasi state awal
    current_vehicles = copy.deepcopy(initial_vehicles)
    current_score = objective_function(current_vehicles, ship)
    history_score = [current_score]
    total_iterations = 0

    if verbose:
        print(f"[0] State Awal. Skor: {current_score}")

    while total_iterations < max_iterations:
        total_iterations += 1
        better_neighbors = []

        # sampling kandidat tetangga acak
        for _ in range(num_candidates):
            candidate = get_random_neighbor(current_vehicles, ship)
            candidate_score = objective_function(candidate, ship)
            if candidate_score > current_score:
                better_neighbors.append((candidate, candidate_score))

        # berhenti kalau gak ada tetangga yang lebih baik (stuck di local optima)
        if not better_neighbors:
            break

        # pilih 1 acak dari tetangga yang lebih baik
        selected_neighbor, selected_score = random.choice(better_neighbors)
        current_vehicles = copy.deepcopy(selected_neighbor)
        current_score = selected_score

        # simpan history skor
        history_score.append(current_score)
        if verbose:
            print(f"[{total_iterations}] Pindah. Skor Baru: {current_score}")

    return current_vehicles, current_score, total_iterations, history_score


# alias fungsi biar tetap jalan kalau dipanggil dengan nama lama
def hill_climbing(awal, ship, max_eval=3000, max_stuck=300, num_candidates=4, verbose=False):
    t0 = time.process_time()
    best_vehicles, best_score, total_iterations, history_score = stochastic_hill_climbing(
        awal, ship, max_iterations=max_eval, num_candidates=num_candidates, verbose=verbose
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


# 1. steepest ascent: pilih kandidat dengan skor tertinggi (paling curam)
def steepest_ascent_hill_climbing(initial_vehicles, ship, max_iterations=3000, num_candidates=20, verbose=False):
    # inisialisasi state awal
    current_vehicles = copy.deepcopy(initial_vehicles)
    current_score = objective_function(current_vehicles, ship)
    history_score = [current_score]
    total_iterations = 0

    if verbose:
        print(f"[0] State Awal. Skor: {current_score}")

    while total_iterations < max_iterations:
        total_iterations += 1
        better_neighbors = []

        # sampling kandidat tetangga acak
        for _ in range(num_candidates):
            candidate = get_random_neighbor(current_vehicles, ship)
            candidate_score = objective_function(candidate, ship)
            if candidate_score > current_score:
                better_neighbors.append((candidate, candidate_score))

        # berhenti kalau gak nemu tetangga yang lebih baik
        if not better_neighbors:
            break

        # cari tetangga terbaik (skor tertinggi)
        best_candidate, best_candidate_score = max(better_neighbors, key=lambda item: item[1])
        current_vehicles = copy.deepcopy(best_candidate)
        current_score = best_candidate_score

        # simpan history skor
        history_score.append(current_score)
        if verbose:
            print(f"[{total_iterations}] Pindah. Skor Baru: {current_score}")

    return current_vehicles, current_score, total_iterations, history_score


# 2. sideways move: boleh geser mendatar kalau skornya sama
def sideways_move_hill_climbing(initial_vehicles, ship, max_iterations=3000, max_sideways=100, num_candidates=4, verbose=False):
    # inisialisasi state awal
    current_vehicles = copy.deepcopy(initial_vehicles)
    current_score = objective_function(current_vehicles, ship)
    history_score = [current_score]
    total_iterations = 0
    sideways_count = 0

    if verbose:
        print(f"[0] State Awal. Skor: {current_score}")

    while total_iterations < max_iterations:
        total_iterations += 1
        eligible_neighbors = []

        # sampling kandidat tetangga acak
        for _ in range(num_candidates):
            candidate = get_random_neighbor(current_vehicles, ship)
            candidate_score = objective_function(candidate, ship)
            if candidate_score >= current_score:
                eligible_neighbors.append((candidate, candidate_score))

        # berhenti kalau gak ada tetangga >= skor sekarang
        if not eligible_neighbors:
            break

        # pilih tetangga dengan skor terbaik di antara yang eligible
        selected_neighbor, selected_score = max(eligible_neighbors, key=lambda item: item[1])

        if selected_score > current_score:
            # skor naik: reset hitungan sideways
            sideways_count = 0
            current_vehicles = copy.deepcopy(selected_neighbor)
            current_score = selected_score
            history_score.append(current_score)
            if verbose:
                print(f"[{total_iterations}] Pindah. Skor Baru: {current_score}")
        else:
            # skor sama: tambah hitungan sideways
            sideways_count += 1
            # cek batas max_sideways biar gak muter-muter terus di plateau
            if sideways_count >= max_sideways:
                break
            current_vehicles = copy.deepcopy(selected_neighbor)
            current_score = selected_score
            history_score.append(current_score)
            if verbose:
                print(f"[{total_iterations}] Pindah Samping. Skor Baru: {current_score}")

    return current_vehicles, current_score, total_iterations, history_score


# helper buat bikin state awal acak baru untuk random restart
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


# class pembungkus tuple untuk random restart agar backward-compatible (4 elemen)
class RandomRestartResult(tuple):
    def __new__(cls, best_vehicles, best_score, total_restarts, iterations_per_restart, history_score=None, initial_score=None):
        return super().__new__(cls, (best_vehicles, best_score, total_restarts, iterations_per_restart))

    def __init__(self, best_vehicles, best_score, total_restarts, iterations_per_restart, history_score=None, initial_score=None):
        self.history_score = history_score if history_score is not None else [best_score]
        self.initial_score = initial_score


# 3. random restart: ulang pencarian beberapa kali dari state awal acak
def random_restart_hill_climbing(ship, max_restarts=5, max_iterations_per_restart=1000, initial_vehicles=None, num_candidates=4, verbose=False):
    # fleksibel kalau urutan argumennya kebalik (initial_vehicles, ship)
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
        # bangkitkan state awal acak baru di tiap restart
        start_state = bikin_state_acak(initial_vehicles, ship)

        # jalankan stochastic hill climbing untuk restart kali ini
        best_v, best_s, iters, hist = stochastic_hill_climbing(
            start_state, ship, max_iterations=max_iterations_per_restart, num_candidates=num_candidates, verbose=False
        )

        if initial_score is None and hist:
            initial_score = hist[0]

        iterations_per_restart.append(iters)

        # catat akumulasi progres skor terbaik global
        for s in hist:
            if s > global_best_score or global_best_vehicles is None:
                global_best_score = s
            cumulative_history.append(global_best_score)

        if best_s > global_best_score or global_best_vehicles is None:
            global_best_score = best_s
            global_best_vehicles = copy.deepcopy(best_v)

        if verbose:
            print(f"[{restart_idx}] Restart. Skor Baru: {global_best_score}")

    total_restarts = len(iterations_per_restart)
    return RandomRestartResult(
        global_best_vehicles, global_best_score, total_restarts, iterations_per_restart, cumulative_history, initial_score
    )


# cetak daftar mobil yang naik ke kapal
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


# fungsi buat gambar denah geladak kapal
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
    # yang belum naik ditaruh di pojok
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


# simpan plot ke file gambar
def simpan_gambar(gambar, nama):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    lokasi = os.path.join(OUTPUT_DIR, nama)
    gambar.tight_layout()
    gambar.savefig(lokasi, dpi=150)
    print(f"Gambar disimpan: {lokasi}")
    return lokasi


# bikin data kendaraan awal buat uji coba
def bikin_kendaraan_awal():
    v1 = Vehicle("V1", 2, 4, "Horizontal", 150, 200, 1)
    v1.x, v1.y, v1.is_loaded = 0, 0, True
    v2 = Vehicle("V2", 2, 4, "Horizontal", 200, 300, 2)
    v2.x, v2.y, v2.is_loaded = 3, 0, True
    v3 = Vehicle("V3", 3, 3, "Vertical", 80, 100, 3)
    return [v1, v2, v3]


# jalanin eksperimen lengkap 4 varian hill climbing
def run_experiment(show_plot=True):
    random.seed(42)  # seed tetap biar hasil perbandingannya adil

    kapal = Ship(10, 10, 1000)
    kendaraan_awal = bikin_kendaraan_awal()
    skor_awal = objective_function(kendaraan_awal, kapal)

    # 1. gambar state awal
    fig_awal, ax_awal = plt.subplots(figsize=(6, 6))
    plot_deck(kendaraan_awal, kapal, f"Initial State (objective = {skor_awal})", ax_awal)
    simpan_gambar(fig_awal, "initial_state.png")

    print("\n--- Menjalankan 4 Varian Hill Climbing ---")

    # 1. steepest ascent
    print("\n[1/4] Steepest Ascent Hill Climbing...")
    t0 = time.process_time()
    sa_v, sa_score, sa_iter, sa_hist = steepest_ascent_hill_climbing(
        kendaraan_awal, kapal, max_iterations=3000, num_candidates=20, verbose=True
    )
    sa_dur = time.process_time() - t0

    # 2. stochastic
    print("\n[2/4] Stochastic Hill Climbing...")
    t0 = time.process_time()
    st_v, st_score, st_iter, st_hist = stochastic_hill_climbing(
        kendaraan_awal, kapal, max_iterations=3000, num_candidates=4, verbose=True
    )
    st_dur = time.process_time() - t0

    # 3. sideways move
    print("\n[3/4] Sideways Move Hill Climbing...")
    t0 = time.process_time()
    sw_v, sw_score, sw_iter, sw_hist = sideways_move_hill_climbing(
        kendaraan_awal, kapal, max_iterations=3000, max_sideways=100, num_candidates=4, verbose=True
    )
    sw_dur = time.process_time() - t0

    # 4. random restart
    print("\n[4/4] Random Restart Hill Climbing...")
    t0 = time.process_time()
    rr_res = random_restart_hill_climbing(
        kapal, max_restarts=5, max_iterations_per_restart=1000, initial_vehicles=kendaraan_awal, num_candidates=4, verbose=True
    )
    rr_v, rr_score, rr_restarts, rr_iters = rr_res
    rr_hist = rr_res.history_score
    rr_init_of = rr_res.initial_score if rr_res.initial_score is not None else skor_awal
    rr_dur = time.process_time() - t0

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

    # cetak detail mobil tiap algoritma
    for item in hasil_eksperimen:
        print(f"\n--- Hasil {item['nama']} ---")
        print_output(item["final_state"], kapal)

    # 2. gambar 4 state akhir berdampingan
    fig_akhir, axes_akhir = plt.subplots(1, 4, figsize=(20, 5))
    for item, ax in zip(hasil_eksperimen, axes_akhir):
        plot_deck(
            item["final_state"],
            kapal,
            f"{item['nama']}\nObjective = {item['final_score']}",
            ax,
        )
    simpan_gambar(fig_akhir, "final_state.png")

    # 3. plot perbandingan skor vs iterasi
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
    ax_plot.set_title("Perbandingan Objective Function vs Iterasi (4 Varian Hill Climbing)", fontsize=12)
    ax_plot.set_xlabel("Iterasi", fontsize=10)
    ax_plot.set_ylabel("Objective Function (Total Shipping Fee)", fontsize=10)
    ax_plot.grid(True, linestyle="--", alpha=0.5)
    ax_plot.legend(loc="lower right", fontsize=10)
    simpan_gambar(fig_plot, "objective_vs_iterasi.png")

    # 4. tabel perbandingan hasil eksperimen
    fig_tab, ax_tab = plt.subplots(figsize=(11, 3.2))
    ax_tab.axis("off")
    ax_tab.set_title("Perbandingan Performa 4 Varian Hill Climbing", fontsize=12, pad=12)
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

    # ringkasan tabel di terminal
    print("\n--- Ringkasan Hasil Eksperimen ---")
    print(f"{'Algoritma':<18} | {'OF Awal':<8} | {'OF Akhir':<8} | {'Iterasi / Restart':<26} | {'Durasi'}")
    print("-" * 68)
    for item in hasil_eksperimen:
        print(f"{item['nama']:<18} | {item['skor_awal']:<8} | {item['final_score']:<8} | {item['iterasi_info']:<26} | {item['durasi']:.4f}s")


# verifikasi 4 varian hill climbing sesuai spek tugas lab
def verify_all_hill_climbing():
    print("Mulai pengujian 4 varian Hill Climbing...")

    kapal = Ship(10, 10, 1000)
    kendaraan = bikin_kendaraan_awal()

    # 1. verifikasi steepest ascent
    random.seed(42)
    sa_v, sa_s, sa_iter, sa_hist = steepest_ascent_hill_climbing(kendaraan, kapal, max_iterations=100, num_candidates=20, verbose=False)
    assert isinstance(sa_iter, int) and sa_iter >= 1, "Steepest Ascent harus mencatat total iterasi >= 1"
    assert all(sa_hist[i] <= sa_hist[i + 1] for i in range(len(sa_hist) - 1)), "History Steepest Ascent harus monoton naik"
    print(f"- Steepest Ascent: PASSED (Iterasi: {sa_iter}, Skor: {sa_s})")

    # 2. verifikasi stochastic
    random.seed(42)
    st_v, st_s, st_iter, st_hist = stochastic_hill_climbing(kendaraan, kapal, max_iterations=100, num_candidates=4, verbose=False)
    assert isinstance(st_iter, int) and st_iter >= 1, "Stochastic HC harus mencatat total iterasi >= 1"
    assert all(st_hist[i] <= st_hist[i + 1] for i in range(len(st_hist) - 1)), "History Stochastic HC harus monoton naik"
    print(f"- Stochastic: PASSED (Iterasi: {st_iter}, Skor: {st_s})")

    # 3. verifikasi sideways move
    random.seed(8)
    max_side = 5
    sw_v, sw_s, sw_iter, sw_hist = sideways_move_hill_climbing(kendaraan, kapal, max_iterations=100, max_sideways=max_side, num_candidates=4, verbose=False)
    assert isinstance(sw_iter, int) and sw_iter >= 1, "Sideways Move harus mencatat total iterasi >= 1"
    assert all(sw_hist[i] <= sw_hist[i + 1] for i in range(len(sw_hist) - 1)), "History Sideways Move tidak boleh anjlok"
    print(f"- Sideways Move: PASSED (Iterasi: {sw_iter}, Max Sideways: {max_side}, Skor: {sw_s})")

    # 4. verifikasi random restart
    random.seed(0)
    restarts_target = 3
    rr_res = random_restart_hill_climbing(kapal, max_restarts=restarts_target, max_iterations_per_restart=50, initial_vehicles=kendaraan, verbose=False)
    rr_v, rr_s, rr_total_r, rr_iters = rr_res
    assert rr_total_r == restarts_target, f"Banyak restart harus tepat {restarts_target}"
    assert len(rr_iters) == restarts_target, "Harus mencatat banyak iterasi untuk setiap restart"
    assert rr_s >= 0, "Harus melacak global best score"
    print(f"- Random Restart: PASSED (Restarts: {restarts_target}, Skor: {rr_s})")

    # 5. verifikasi ketersediaan file output visualisasi
    required_files = ["final_state.png", "hasil_eksperimen.png", "objective_vs_iterasi.png"]
    for fname in required_files:
        fpath = os.path.join(OUTPUT_DIR, fname)
        assert os.path.exists(fpath), f"File {fname} tidak ditemukan di {OUTPUT_DIR}"
    print("- Output visualisasi: OK\n")

    print("Semua verifikasi berhasil.")


if __name__ == "__main__":
    if "--verify" in sys.argv:
        verify_all_hill_climbing()
    else:
        show = "--no-show" not in sys.argv
        run_experiment(show_plot=show)
        print()
        verify_all_hill_climbing()