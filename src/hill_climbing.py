import copy
import os
import random
import sys
import time

import matplotlib.patches as patches
import matplotlib.pyplot as plt

# atur path biar bisa import modul main dari root atau src/
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from main import Ship, Vehicle, move, objective_function, rotate, swap
except ImportError:
    from src.main import Ship, Vehicle, move, objective_function, rotate, swap

# folder buat nyimpen hasil gambar
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "output", "hill_climbing")


# class hasil pencarian agar kompatibel dengan unpacking 4 tuple (best_v, best_s, iters, hist)
class SearchResult(tuple):
    def __new__(cls, best_vehicles, best_score, total_iterations, history_score, status="Local Optima", sideways_moves=0):
        return super().__new__(cls, (best_vehicles, best_score, total_iterations, history_score))

    def __init__(self, best_vehicles, best_score, total_iterations, history_score, status="Local Optima", sideways_moves=0):
        self.best_vehicles = best_vehicles
        self.best_score = best_score
        self.total_iterations = total_iterations
        self.history_score = history_score
        self.status = status
        self.sideways_moves = sideways_moves


# class hasil random restart agar kompatibel dengan unpacking 4 tuple (best_v, best_s, total_r, iters_per_r)
class RandomRestartResult(tuple):
    def __new__(cls, best_vehicles, best_score, total_restarts, iterations_per_restart, history_score=None, initial_score=None, status="Max Restart Reached", initial_state=None):
        return super().__new__(cls, (best_vehicles, best_score, total_restarts, iterations_per_restart))

    def __init__(self, best_vehicles, best_score, total_restarts, iterations_per_restart, history_score=None, initial_score=None, status="Max Restart Reached", initial_state=None):
        self.best_vehicles = best_vehicles
        self.best_score = best_score
        self.total_restarts = total_restarts
        self.iterations_per_restart = iterations_per_restart
        self.history_score = history_score if history_score is not None else [best_score]
        self.initial_score = initial_score
        self.status = status
        self.initial_state = initial_state


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


# bangkitkan seluruh tetangga (move, swap, rotate, toggle_load) untuk steepest ascent
def get_all_neighbors(vehicles, ship):
    neighbors = []

    # 1. move: coba pindahkan mobil ke semua koordinat yang muat di dek
    for i, v in enumerate(vehicles):
        if not v.is_loaded:
            continue
        max_x = max(0, ship.dimension.width - v.dimension.width)
        max_y = max(0, ship.dimension.length - v.dimension.length)
        for nx in range(max_x + 1):
            for ny in range(max_y + 1):
                if nx != v.x or ny != v.y:
                    n = copy.deepcopy(vehicles)
                    n[i].x = nx
                    n[i].y = ny
                    neighbors.append(n)

    # 2. swap: tukar koordinat antar pasangan mobil yang ada di dek
    loaded_idx = [idx for idx, v in enumerate(vehicles) if v.is_loaded]
    for i in range(len(loaded_idx)):
        for j in range(i + 1, len(loaded_idx)):
            idx_a = loaded_idx[i]
            idx_b = loaded_idx[j]
            n = copy.deepcopy(vehicles)
            n[idx_a].x, n[idx_b].x = n[idx_b].x, n[idx_a].x
            n[idx_a].y, n[idx_b].y = n[idx_b].y, n[idx_a].y
            neighbors.append(n)

    # 3. rotate: putar orientasi mobil yang dimuat
    for i, v in enumerate(vehicles):
        if not v.is_loaded:
            continue
        n = copy.deepcopy(vehicles)
        veh = n[i]
        if veh.orientation == "Horizontal":
            veh.orientation = "Vertical"
        else:
            veh.orientation = "Horizontal"
        veh.dimension.width, veh.dimension.length = veh.dimension.length, veh.dimension.width
        # sesuaikan posisi bila keluar batas
        veh.x = min(veh.x, max(0, ship.dimension.width - veh.dimension.width))
        veh.y = min(veh.y, max(0, ship.dimension.length - veh.dimension.length))
        neighbors.append(n)

    # 4. toggle: muat atau turunkan mobil
    for i, v in enumerate(vehicles):
        if not v.is_loaded:
            max_x = max(0, ship.dimension.width - v.dimension.width)
            max_y = max(0, ship.dimension.length - v.dimension.length)
            for nx in range(max_x + 1):
                for ny in range(max_y + 1):
                    n = copy.deepcopy(vehicles)
                    n[i].is_loaded = True
                    n[i].x = nx
                    n[i].y = ny
                    neighbors.append(n)
        else:
            n = copy.deepcopy(vehicles)
            n[i].is_loaded = False
            neighbors.append(n)

    return neighbors


# 1. steepest ascent: evaluasi seluruh tetangga dan pilih skor tertinggi
def steepest_ascent_hill_climbing(initial_vehicles, ship, max_iterations=3000, num_candidates=None, verbose=False):
    # inisialisasi state awal
    current_vehicles = copy.deepcopy(initial_vehicles)
    current_score = objective_function(current_vehicles, ship)
    history_score = [current_score]
    total_iterations = 0
    status = "Local Optima"

    if verbose:
        print(f"[0] State Awal. Skor: {current_score}")

    while total_iterations < max_iterations:
        total_iterations += 1

        # jika num_candidates tidak diset, evaluasi seluruh tetangga
        if num_candidates is None or num_candidates == "all":
            all_n = get_all_neighbors(current_vehicles, ship)
            better_neighbors = []
            for candidate in all_n:
                candidate_score = objective_function(candidate, ship)
                if candidate_score > current_score:
                    better_neighbors.append((candidate, candidate_score))
        else:
            better_neighbors = []
            for _ in range(num_candidates):
                candidate = get_random_neighbor(current_vehicles, ship)
                candidate_score = objective_function(candidate, ship)
                if candidate_score > current_score:
                    better_neighbors.append((candidate, candidate_score))

        # berhenti saat tidak ada tetangga yang lebih baik (local optima)
        if not better_neighbors:
            status = "Local Optima"
            break

        # pilih tetangga dengan skor tertinggi (argmax)
        max_score = max(item[1] for item in better_neighbors)
        best_candidates = [item for item in better_neighbors if item[1] == max_score]
        best_candidate, best_candidate_score = random.choice(best_candidates)

        current_vehicles = copy.deepcopy(best_candidate)
        current_score = best_candidate_score

        # simpan history skor
        history_score.append(current_score)
        if verbose:
            print(f"[{total_iterations}] Pindah. Skor Baru: {current_score}")

    if total_iterations >= max_iterations and status != "Local Optima":
        status = "Max Iteration Reached"

    return SearchResult(current_vehicles, current_score, total_iterations, history_score, status=status)


# 2. stochastic hill climbing: pilih acak dari tetangga yang lebih baik
def stochastic_hill_climbing(initial_vehicles, ship, max_iterations=3000, num_candidates=10, verbose=False):
    # inisialisasi state awal
    current_vehicles = copy.deepcopy(initial_vehicles)
    current_score = objective_function(current_vehicles, ship)
    history_score = [current_score]
    total_iterations = 0
    status = "Local Optima"

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

        # berhenti saat tidak ada tetangga yang lebih baik (local optima)
        if not better_neighbors:
            status = "Local Optima"
            break

        # pilih 1 secara acak dari kumpulan tetangga yang lebih baik
        selected_neighbor, selected_score = random.choice(better_neighbors)
        current_vehicles = copy.deepcopy(selected_neighbor)
        current_score = selected_score

        # simpan history skor
        history_score.append(current_score)
        if verbose:
            print(f"[{total_iterations}] Pindah. Skor Baru: {current_score}")

    if total_iterations >= max_iterations and status != "Local Optima":
        status = "Max Iteration Reached"

    return SearchResult(current_vehicles, current_score, total_iterations, history_score, status=status)


# 3. hill climbing with sideways move: boleh geser mendatar jika skornya sama
def sideways_move_hill_climbing(initial_vehicles, ship, max_iterations=3000, max_sideways_move=100, max_sideways=None, num_candidates=10, verbose=False):
    limit_sideways = max_sideways if max_sideways is not None else max_sideways_move

    # inisialisasi state awal
    current_vehicles = copy.deepcopy(initial_vehicles)
    current_score = objective_function(current_vehicles, ship)
    history_score = [current_score]
    total_iterations = 0
    sideways_count = 0
    total_sideways_executed = 0
    status = "Local Optima"

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

        # berhenti kalau gak ada tetangga yang >= skor sekarang
        if not eligible_neighbors:
            status = "Local Optima"
            break

        # pilih tetangga dengan skor terbaik di antara yang eligible
        max_score = max(item[1] for item in eligible_neighbors)
        best_candidates = [item for item in eligible_neighbors if item[1] == max_score]
        selected_neighbor, selected_score = random.choice(best_candidates)

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
            total_sideways_executed += 1
            # cek batas max_sideways_move
            if sideways_count >= limit_sideways:
                status = "Max Sideways Reached"
                break
            current_vehicles = copy.deepcopy(selected_neighbor)
            current_score = selected_score
            history_score.append(current_score)
            if verbose:
                print(f"[{total_iterations}] Pindah Samping. Skor Baru: {current_score}")

    if total_iterations >= max_iterations and status not in ["Max Sideways Reached", "Local Optima"]:
        status = "Max Iteration Reached"

    return SearchResult(current_vehicles, current_score, total_iterations, history_score, status=status, sideways_moves=total_sideways_executed)


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


# 4. random restart hill climbing: ulang pencarian beberapa kali dari state acak baru
def random_restart_hill_climbing(ship, max_restart=10, max_restarts=None, max_iterations_per_restart=1000, initial_vehicles=None, num_candidates=10, verbose=False):
    limit_restarts = max_restarts if max_restarts is not None else max_restart

    if isinstance(ship, list) and hasattr(limit_restarts, "maxCapacity"):
        initial_vehicles, ship, limit_restarts = ship, limit_restarts, max_iterations_per_restart

    if initial_vehicles is None:
        initial_vehicles = bikin_kendaraan_awal()

    global_best_vehicles = None
    global_best_score = -1
    iterations_per_restart = []
    cumulative_history = []
    initial_score = None

    first_initial_state = None

    for restart_idx in range(1, limit_restarts + 1):
        # bangkitkan state awal acak baru di tiap restart
        start_state = bikin_state_acak(initial_vehicles, ship)
        if first_initial_state is None:
            first_initial_state = copy.deepcopy(start_state)

        # jalankan stochastic hill climbing untuk restart kali ini
        best_v, best_s, iters, hist = stochastic_hill_climbing(
            start_state, ship, max_iterations=max_iterations_per_restart, num_candidates=num_candidates, verbose=False
        )

        if initial_score is None and hist:
            initial_score = hist[0]

        iterations_per_restart.append(iters)

        # catat progres skor terbaik global secara kumulatif
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
    status = "Max Restart Reached"
    return RandomRestartResult(
        global_best_vehicles, global_best_score, total_restarts, iterations_per_restart, cumulative_history, initial_score, status=status, initial_state=first_initial_state
    )


# alias fungsi biar tetap kompatibel
def hill_climbing(awal, ship, max_eval=3000, max_stuck=300, num_candidates=4, verbose=False):
    t0 = time.process_time()
    res = stochastic_hill_climbing(
        awal, ship, max_iterations=max_eval, num_candidates=num_candidates, verbose=verbose
    )
    lama = time.process_time() - t0
    return {
        "initial_state": copy.deepcopy(awal),
        "final_state": res[0],
        "skor_awal": res[3][0],
        "final_score": res[1],
        "score_history": res[3],
        "total_evaluations": res[2],
        "execution_time": lama,
    }


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
    ax.set_title(judul, fontsize=9, fontweight="bold")
    ax.set_xlabel("X", fontsize=8)
    ax.set_ylabel("Y", fontsize=8)
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
    belum = [v.id for v in vehicles if not v.is_loaded]
    if belum:
        ax.text(
            0.02,
            0.98,
            "Belum dimuat: " + ", ".join(belum),
            transform=ax.transAxes,
            va="top",
            fontsize=7,
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


# jalanin eksperimen lengkap 4 varian hill climbing dengan 3 kali percobaan (Run 1, Run 2, Run 3)
def run_experiment(show_plot=True):
    kapal = Ship(10, 10, 1000)
    kendaraan_awal = bikin_kendaraan_awal()
    skor_awal = objective_function(kendaraan_awal, kapal)

    # 1. simpan gambar denah geladak state awal
    fig_awal, ax_awal = plt.subplots(figsize=(6, 6))
    plot_deck(kendaraan_awal, kapal, f"Initial State (objective = {skor_awal})", ax_awal)
    simpan_gambar(fig_awal, "initial_state.png")

    # konfigurasi 3 kali percobaan untuk setiap algoritma
    percobaan_seeds = [("Run 1", 42), ("Run 2", 123), ("Run 3", 999)]

    # struktur data untuk merekam seluruh hasil eksperimen (12 baris)
    daftar_hasil = []

    # map data per algoritma untuk plotting
    data_algoritma = {
        "Steepest Ascent": [],
        "Stochastic": [],
        "Sideways Move": [],
        "Random Restart": [],
    }

    print("\n--- Menjalankan Eksperimen 4 Varian Hill Climbing (3 Run Tiap Varian) ---")

    # 1. Steepest Ascent Hill Climbing (Run 1, 2, 3)
    for run_label, seed_val in percobaan_seeds:
        random.seed(seed_val)
        t0 = time.process_time()
        res = steepest_ascent_hill_climbing(kendaraan_awal, kapal, max_iterations=3000, num_candidates=None, verbose=False)
        durasi = time.process_time() - t0

        item = {
            "algoritma": "Steepest Ascent",
            "run": run_label,
            "initial_state": copy.deepcopy(kendaraan_awal),
            "initial_of": res[3][0],
            "final_of": res[1],
            "iterasi_info": f"{res[2]} iterasi",
            "durasi": durasi,
            "status": res.status,
            "final_state": res[0],
            "history": res[3],
        }
        daftar_hasil.append(item)
        data_algoritma["Steepest Ascent"].append(item)

    # 2. Stochastic Hill Climbing (Run 1, 2, 3)
    for run_label, seed_val in percobaan_seeds:
        random.seed(seed_val)
        t0 = time.process_time()
        res = stochastic_hill_climbing(kendaraan_awal, kapal, max_iterations=3000, num_candidates=10, verbose=False)
        durasi = time.process_time() - t0

        item = {
            "algoritma": "Stochastic",
            "run": run_label,
            "initial_state": copy.deepcopy(kendaraan_awal),
            "initial_of": res[3][0],
            "final_of": res[1],
            "iterasi_info": f"{res[2]} iterasi",
            "durasi": durasi,
            "status": res.status,
            "final_state": res[0],
            "history": res[3],
        }
        daftar_hasil.append(item)
        data_algoritma["Stochastic"].append(item)

    # 3. Sideways Move Hill Climbing (Run 1, 2, 3)
    for run_label, seed_val in percobaan_seeds:
        random.seed(seed_val)
        t0 = time.process_time()
        res = sideways_move_hill_climbing(kendaraan_awal, kapal, max_iterations=3000, max_sideways_move=100, num_candidates=10, verbose=False)
        durasi = time.process_time() - t0

        item = {
            "algoritma": "Sideways Move",
            "run": run_label,
            "initial_state": copy.deepcopy(kendaraan_awal),
            "initial_of": res[3][0],
            "final_of": res[1],
            "iterasi_info": f"{res[2]} iterasi ({res.sideways_moves} sideways)",
            "durasi": durasi,
            "status": res.status,
            "final_state": res[0],
            "history": res[3],
        }
        daftar_hasil.append(item)
        data_algoritma["Sideways Move"].append(item)

    # 4. Random Restart Hill Climbing (Run 1, 2, 3)
    for run_label, seed_val in percobaan_seeds:
        random.seed(seed_val)
        t0 = time.process_time()
        res = random_restart_hill_climbing(kapal, max_restart=10, max_iterations_per_restart=1000, initial_vehicles=kendaraan_awal, num_candidates=10, verbose=False)
        durasi = time.process_time() - t0

        item = {
            "algoritma": "Random Restart",
            "run": run_label,
            "initial_state": res.initial_state if hasattr(res, "initial_state") and res.initial_state is not None else copy.deepcopy(kendaraan_awal),
            "initial_of": res.initial_score if res.initial_score is not None else skor_awal,
            "final_of": res[1],
            "iterasi_info": f"{sum(res[3])} iterasi ({res[2]} restarts)",
            "durasi": durasi,
            "status": res.status,
            "final_state": res[0],
            "history": res.history_score,
        }
        daftar_hasil.append(item)
        data_algoritma["Random Restart"].append(item)

    # VISUALISASI PER VARIAN ALGORITMA (DOKUMENTASI BAB 3)
    # Untuk setiap algoritma dan setiap percobaan (Run 1, 2, 3), buat gambar komprehensif 3-kolom:
    # [State Awal Geladak] | [State Akhir Geladak] | [Plot Objective Function vs Iterasi]
    # Serta simpan gambar tabel ringkasan khusus untuk algoritma tersebut.
    for algo_key, prefix in [
        ("Steepest Ascent", "steepest_ascent"),
        ("Stochastic", "stochastic"),
        ("Sideways Move", "sideways_move"),
        ("Random Restart", "random_restart"),
    ]:
        runs = data_algoritma[algo_key]

        # 1. Plot individual per percobaan (Run 1, Run 2, Run 3)
        for idx, item in enumerate(runs, 1):
            fig_run, (ax_init, ax_final, ax_conv) = plt.subplots(1, 3, figsize=(16, 5))

            # Kolom 1: State Awal
            plot_deck(
                item["initial_state"],
                kapal,
                f"State Awal ({item['run']})\nInitial OF: {item['initial_of']}",
                ax_init,
            )

            # Kolom 2: State Akhir
            plot_deck(
                item["final_state"],
                kapal,
                f"State Akhir ({item['run']})\nFinal OF: {item['final_of']} | {item['status']}",
                ax_final,
            )

            # Kolom 3: Plot Konvergensi Objective Function vs Iterasi
            hist = item["history"]
            ax_conv.plot(
                range(len(hist)),
                hist,
                color="#1f77b4" if idx == 1 else ("#ff7f0e" if idx == 2 else "#2ca02c"),
                marker="o",
                markersize=4,
                linewidth=2,
                label=f"OF ({item['iterasi_info']})",
            )
            ax_conv.set_title(f"Konvergensi OF vs Iterasi ({item['run']})", fontsize=10, fontweight="bold")
            ax_conv.set_xlabel("Iterasi", fontsize=9)
            ax_conv.set_ylabel("Nilai Objective Function", fontsize=9)
            ax_conv.grid(True, linestyle="--", alpha=0.5)
            ax_conv.legend(fontsize=9, loc="lower right")

            fig_run.suptitle(f"{algo_key} - Percobaan {idx} ({item['run']})", fontsize=13, fontweight="bold")
            simpan_gambar(fig_run, f"{prefix}_run{idx}.png")
            plt.close(fig_run)

        # 2. Tabel ringkasan khusus untuk algoritma ini (buat disisipkan di laporan sebelum bahasan percobaan)
        fig_algo_tab, ax_algo_tab = plt.subplots(figsize=(12, 3.2))
        ax_algo_tab.axis("off")
        ax_algo_tab.set_title(f"Tabel Percobaan {algo_key} (IF3070)", fontsize=12, fontweight="bold", pad=10)

        algo_tab_rows = []
        for r_item in runs:
            algo_tab_rows.append([
                r_item["run"],
                str(r_item["initial_of"]),
                str(r_item["final_of"]),
                r_item["iterasi_info"],
                f"{r_item['durasi']:.4f} s",
                r_item["status"],
            ])

        algo_headers = ["Percobaan Ke-", "Initial OF", "Final OF", "Jumlah Iterasi / Info", "Durasi (detik)", "Status Berhenti"]
        tab_inst = ax_algo_tab.table(
            cellText=algo_tab_rows,
            colLabels=algo_headers,
            loc="center",
            cellLoc="center",
        )
        tab_inst.auto_set_font_size(False)
        tab_inst.set_fontsize(9.5)
        tab_inst.scale(1.1, 1.8)

        for c_i in range(len(algo_headers)):
            cell = tab_inst[0, c_i]
            cell.set_facecolor("#2B547E")
            cell.set_text_props(weight="bold", color="white")

        for r_i in range(1, len(algo_tab_rows) + 1):
            bg = "#F5F8FA" if r_i % 2 == 0 else "#FFFFFF"
            for c_i in range(len(algo_headers)):
                tab_inst[r_i, c_i].set_facecolor(bg)

        simpan_gambar(fig_algo_tab, f"tabel_{prefix}.png")
        plt.close(fig_algo_tab)

    # VISUALISASI GABUNGAN 1: Grid Geladak (2D) Final State (4 algoritma x 3 run = 12 subplots)
    fig_final, axes_final = plt.subplots(4, 3, figsize=(14, 16))
    algo_names = ["Steepest Ascent", "Stochastic", "Sideways Move", "Random Restart"]
    for row_idx, algo_name in enumerate(algo_names):
        runs_data = data_algoritma[algo_name]
        for col_idx, item in enumerate(runs_data):
            ax = axes_final[row_idx, col_idx]
            plot_deck(
                item["final_state"],
                kapal,
                f"{item['algoritma']} ({item['run']})\nFinal OF: {item['final_of']}",
                ax,
            )
    simpan_gambar(fig_final, "final_state.png")
    if not show_plot:
        plt.close(fig_final)

    # VISUALISASI GABUNGAN 2: Grafik Konvergensi Objective Function vs Iterasi (2x2 subplots untuk ke-4 varian)
    fig_conv, axes_conv = plt.subplots(2, 2, figsize=(13, 9))
    plot_coords = [(0, 0), (0, 1), (1, 0), (1, 1)]
    run_colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]
    run_markers = ["o", "s", "^"]

    for idx, algo_name in enumerate(algo_names):
        r, c = plot_coords[idx]
        ax = axes_conv[r, c]
        for run_idx, item in enumerate(data_algoritma[algo_name]):
            ax.plot(
                range(len(item["history"])),
                item["history"],
                label=f"{item['run']} (Final: {item['final_of']})",
                color=run_colors[run_idx],
                marker=run_markers[run_idx],
                markersize=4,
                linewidth=1.8,
                alpha=0.85,
            )
        ax.set_title(f"Konvergensi: {algo_name}", fontsize=11, fontweight="bold")
        ax.set_xlabel("Jumlah Iterasi", fontsize=9)
        ax.set_ylabel("Objective Function", fontsize=9)
        ax.grid(True, linestyle="--", alpha=0.5)
        ax.legend(fontsize=9, loc="lower right")

    simpan_gambar(fig_conv, "objective_vs_iterasi.png")
    if not show_plot:
        plt.close(fig_conv)

    # VISUALISASI GABUNGAN 3: Tabel Hasil Eksperimen Lengkap sesuai format BAB 3 Dokumentasi
    fig_tab, ax_tab = plt.subplots(figsize=(14, 6.5))
    ax_tab.axis("off")
    ax_tab.set_title("Tabel Ringkasan Eksperimen 4 Varian Hill Climbing (IF3070)", fontsize=13, fontweight="bold", pad=14)

    tabel_data = []
    for item in daftar_hasil:
        tabel_data.append([
            item["algoritma"],
            item["run"],
            str(item["initial_of"]),
            str(item["final_of"]),
            item["iterasi_info"],
            f"{item['durasi']:.4f} s",
            item["status"],
        ])

    col_headers = ["Algoritma", "Percobaan Ke-", "Initial OF", "Final OF", "Total Iterasi / Restart", "Durasi (detik)", "Status Berhenti"]
    tabel = ax_tab.table(
        cellText=tabel_data,
        colLabels=col_headers,
        loc="center",
        cellLoc="center",
    )
    tabel.auto_set_font_size(False)
    tabel.set_fontsize(9.5)
    tabel.scale(1.15, 1.8)

    # styling header tabel
    for col_idx in range(len(col_headers)):
        cell = tabel[0, col_idx]
        cell.set_facecolor("#2B547E")
        cell.set_text_props(weight="bold", color="white")

    # styling baris bergantian
    for row_idx in range(1, len(tabel_data) + 1):
        bg = "#F5F8FA" if row_idx % 2 == 0 else "#FFFFFF"
        for col_idx in range(len(col_headers)):
            tabel[row_idx, col_idx].set_facecolor(bg)

    simpan_gambar(fig_tab, "hasil_eksperimen.png")
    if not show_plot:
        plt.close(fig_tab)

    # CETAK TABEL REKAPITULASI DOKUMENTASI BAB 3 DI TERMINAL PER ALGORITMA
    for algo_title in ["Steepest Ascent", "Stochastic", "Sideways Move", "Random Restart"]:
        print("\n" + "=" * 90)
        print(f"Informasi Eksperimen: {algo_title}")
        print("=" * 90)
        print(f"| {'Percobaan Ke-':<13} | {'Initial OF':<10} | {'Final OF':<8} | {'Jumlah Iterasi / Info':<28} | {'Durasi (detik)':<14} |")
        print(f"| {':---:':<13} | {':---:':<10} | {':---:':<8} | {':---':<28} | {':---':<14} |")
        for item in data_algoritma[algo_title]:
            dur_str = f"{item['durasi']:.4f} s"
            print(f"| {item['run']:^13} | {item['initial_of']:^10} | {item['final_of']:^8} | {item['iterasi_info']:<28} | {dur_str:<14} |")
        print("-" * 90)

    # CETAK TABEL REKAP KESELURUHAN
    print("\n" + "=" * 105)
    print(f"{'TABEL RINGKASAN SELURUH PERCOBAAN (DOKUMENTASI BAB 3)':^105}")
    print("=" * 105)
    print(f"| {'Algoritma':<17} | {'Percobaan Ke-':<13} | {'Initial OF':<10} | {'Final OF':<8} | {'Total Iterasi / Restart':<30} | {'Durasi (detik)':<14} | {'Status Berhenti':<20} |")
    print(f"| {':---':<17} | {':---:':<13} | {':---:':<10} | {':---:':<8} | {':---':<30} | {':---':<14} | {':---':<20} |")
    for item in daftar_hasil:
        dur_str = f"{item['durasi']:.4f} s"
        print(f"| {item['algoritma']:<17} | {item['run']:^13} | {item['initial_of']:^10} | {item['final_of']:^8} | {item['iterasi_info']:<30} | {dur_str:<14} | {item['status']:<20} |")
    print("=" * 105 + "\n")

    if show_plot:
        try:
            plt.show()
        except Exception:
            pass


# fungsi verifikasi otomatis sesuai spek pengujian
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

    # 5. verifikasi ketersediaan file output visualisasi utama
    required_files = [
        "final_state.png",
        "hasil_eksperimen.png",
        "objective_vs_iterasi.png",
        "steepest_ascent_run1.png",
        "stochastic_run1.png",
        "sideways_move_run1.png",
        "random_restart_run1.png",
    ]
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