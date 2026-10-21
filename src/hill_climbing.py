import copy, os, random, sys, time, matplotlib.patches as patches, matplotlib.pyplot as plt

# Pastikan path modul src tersedia
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import utils
from utils import (
    Dimension,
    Ship,
    Vehicle,
    exceed_capacity_limit,
    exceed_ship_limit,
    not_overlapping,
    objective_function,
)

# Re-ekspor seluruh varian dan helper dari paket hill_climbing_variants
from hill_climbing_variants import (
    RandomRestartResult,
    SearchResult,
    bikin_kendaraan_awal,
    bikin_state_acak,
    get_all_neighbors,
    get_random_neighbor,
    random_restart_hill_climbing,
    sideways_move_hill_climbing,
    steepest_ascent_hill_climbing,
    stochastic_hill_climbing,
)

# Folder output visualisasi
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "output", "hill_climbing")


# Alias fungsi lama untuk backward compatibility
def hill_climbing(awal, ship, max_eval=3000, max_stuck=300, num_candidates=4, verbose=False):
    t0 = time.perf_counter()
    res = stochastic_hill_climbing(
        awal, ship, max_iterations=max_eval, num_candidates=num_candidates, verbose=verbose
    )
    lama = time.perf_counter() - t0
    return {
        "initial_state": copy.deepcopy(awal),
        "final_state": res[0],
        "skor_awal": res[3][0],
        "final_score": res[1],
        "score_history": res[3],
        "total_evaluations": res[2],
        "execution_time": lama,
    }


def print_output(state, ship):
    """Mencetak daftar kendaraan yang dimuat ke kapal dan total skor ke konsol."""
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


def plot_deck(vehicles, ship, judul, ax):
    """Menggambar denah 2D geladak kapal dan tata letak mobil yang dimuat."""
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


def generate_bin_packing_movement_plot(kapal=None, vehicles=None):
    """Menghasilkan ilustrasi 4-panel transisi pergerakan (Initial -> Move -> Swap -> Rotate)."""
    if kapal is None:
        kapal = Ship(10, 10, 50)
    if vehicles is None:
        vehicles = bikin_kendaraan_awal()

    fig, axes = plt.subplots(1, 4, figsize=(18, 4.5))

    # 1. State Awal
    st0 = copy.deepcopy(vehicles)
    st0[0].x, st0[0].y, st0[0].is_loaded = 1, 1, True
    if len(st0) > 1:
        st0[1].x, st0[1].y, st0[1].is_loaded = 6, 2, True
    plot_deck(st0, kapal, "1. State Awal\n(Initial State)", axes[0])

    # 2. Movement (Move)
    st_move = copy.deepcopy(st0)
    st_move[0].x, st_move[0].y = 4, 1
    plot_deck(st_move, kapal, "2. Pergerakan Koordinat\n(Move: V1 geser ke X=4)", axes[1])

    # 3. Swap (Tukar Posisi)
    st_swap = copy.deepcopy(st_move)
    if len(st_swap) >= 2:
        st_swap[0].x, st_swap[1].x = st_swap[1].x, st_swap[0].x
        st_swap[0].y, st_swap[1].y = st_swap[1].y, st_swap[0].y
    plot_deck(st_swap, kapal, "3. Pertukaran Posisi\n(Swap: V1 <-> V2)", axes[2])

    # 4. Rotation (Rotate)
    st_rotate = copy.deepcopy(st_swap)
    target = st_rotate[0]
    target.orientation = "Vertical" if target.orientation == "Horizontal" else "Horizontal"
    target.dimension.width, target.dimension.length = target.dimension.length, target.dimension.width
    plot_deck(st_rotate, kapal, "4. Rotasi Dimensi\n(Rotate: Orientasi berubah)", axes[3])

    fig.suptitle("Ilustrasi Mekanisme Movement Transisi State (Bin Packing)", fontsize=13, fontweight="bold")
    simpan_gambar(fig, "bin_packing_movement.png")
    plt.close(fig)


def simpan_gambar(gambar, nama):
    """Menyimpan gambar visualisasi ke folder output/hill_climbing/."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    lokasi = os.path.join(OUTPUT_DIR, nama)
    gambar.tight_layout()
    gambar.savefig(lokasi, dpi=150)
    print(f"Gambar disimpan: {lokasi}")
    return lokasi


def run_experiment(show_plot=True, json_path=None):
    """Menjalankan eksperimen lengkap 4 varian Hill Climbing dengan 3 kali percobaan (Run 1, 2, 3) dan membuat 21 visualisasi."""
    if json_path is None:
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vehicles.json")

    kapal = None
    if os.path.exists(json_path):
        try:
            kendaraan_template, kapal = utils.load_json(json_path)
        except Exception:
            pass

    if kapal is None:
        kapal = Ship(10, 10, 50)
        kendaraan_template = bikin_kendaraan_awal()

    percobaan_list = ["Run 1", "Run 2", "Run 3"]
    initial_states_per_run = {}
    for run_label in percobaan_list:
        initial_states_per_run[run_label] = bikin_state_acak(kendaraan_template, kapal)

    # Simpan denah state awal ketiga run
    fig_awal, axes_awal = plt.subplots(1, 3, figsize=(14, 5))
    for idx, run_label in enumerate(percobaan_list):
        st = initial_states_per_run[run_label]
        sc = objective_function(st, kapal)
        plot_deck(st, kapal, f"Initial State - {run_label}\nObjective = {sc}", axes_awal[idx])
    simpan_gambar(fig_awal, "initial_state.png")
    if not show_plot:
        plt.close(fig_awal)

    # Ilustrasi movement bin packing
    generate_bin_packing_movement_plot(kapal, kendaraan_template)

    daftar_hasil = []
    data_algoritma = {
        "Steepest Ascent": [],
        "Stochastic": [],
        "Sideways Move": [],
        "Random Restart": [],
    }

    print("\n--- Menjalankan Eksperimen 4 Varian Hill Climbing (3 Run Tiap Varian) ---")

    # 1. Steepest Ascent Hill Climbing
    for run_label in percobaan_list:
        init_st = copy.deepcopy(initial_states_per_run[run_label])
        t0 = time.perf_counter()
        res = steepest_ascent_hill_climbing(init_st, kapal, max_iterations=3000, num_candidates=None, verbose=False)
        durasi = time.perf_counter() - t0

        item = {
            "algoritma": "Steepest Ascent",
            "run": run_label,
            "initial_state": copy.deepcopy(init_st),
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

    # 2. Stochastic Hill Climbing
    for run_label in percobaan_list:
        init_st = copy.deepcopy(initial_states_per_run[run_label])
        t0 = time.perf_counter()
        res = stochastic_hill_climbing(init_st, kapal, max_iterations=3000, num_candidates=10, verbose=False)
        durasi = time.perf_counter() - t0

        item = {
            "algoritma": "Stochastic",
            "run": run_label,
            "initial_state": copy.deepcopy(init_st),
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

    # 3. Sideways Move Hill Climbing
    for run_label in percobaan_list:
        init_st = copy.deepcopy(initial_states_per_run[run_label])
        t0 = time.perf_counter()
        res = sideways_move_hill_climbing(init_st, kapal, max_iterations=3000, max_sideways_move=100, num_candidates=10, verbose=False)
        durasi = time.perf_counter() - t0

        item = {
            "algoritma": "Sideways Move",
            "run": run_label,
            "initial_state": copy.deepcopy(init_st),
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

    # 4. Random Restart Hill Climbing
    for run_label in percobaan_list:
        init_st = copy.deepcopy(initial_states_per_run[run_label])
        t0 = time.perf_counter()
        res = random_restart_hill_climbing(kapal, max_restart=10, max_iterations_per_restart=1000, initial_vehicles=init_st, num_candidates=10, verbose=False)
        durasi = time.perf_counter() - t0

        item = {
            "algoritma": "Random Restart",
            "run": run_label,
            "initial_state": res.initial_state if hasattr(res, "initial_state") and res.initial_state is not None else copy.deepcopy(init_st),
            "initial_of": res.initial_score if res.initial_score is not None else objective_function(init_st, kapal),
            "final_of": res[1],
            "iterasi_info": f"{sum(res[3])} iterasi ({res[2]} restarts)",
            "durasi": durasi,
            "status": res.status,
            "final_state": res[0],
            "history": res.history_score,
        }
        daftar_hasil.append(item)
        data_algoritma["Random Restart"].append(item)

    # Visualisasi per varian
    for algo_key, prefix in [
        ("Steepest Ascent", "steepest_ascent"),
        ("Stochastic", "stochastic"),
        ("Sideways Move", "sideways_move"),
        ("Random Restart", "random_restart"),
    ]:
        runs = data_algoritma[algo_key]

        # Plot individual per percobaan
        for idx, item in enumerate(runs, 1):
            fig_run, (ax_init, ax_final, ax_conv) = plt.subplots(1, 3, figsize=(16, 5))
            plot_deck(item["initial_state"], kapal, f"State Awal ({item['run']})\nInitial OF: {item['initial_of']}", ax_init)
            plot_deck(item["final_state"], kapal, f"State Akhir ({item['run']})\nFinal OF: {item['final_of']} | {item['status']}", ax_final)

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

        # Tabel ringkasan khusus per algoritma
        fig_algo_tab, ax_algo_tab = plt.subplots(figsize=(12, 3.2))
        ax_algo_tab.axis("off")
        ax_algo_tab.set_title(f"Tabel Percobaan {algo_key}", fontsize=12, fontweight="bold", pad=10)

        algo_tab_rows = [
            [r_item["run"], str(r_item["initial_of"]), str(r_item["final_of"]), f"{r_item['durasi']:.4f} s", r_item["iterasi_info"], r_item["status"]]
            for r_item in runs
        ]
        algo_headers = ["Percobaan Ke-", "Initial OF", "Final OF", "Durasi (detik)", "Jumlah Iterasi / Info", "Status Berhenti"]
        tab_inst = ax_algo_tab.table(cellText=algo_tab_rows, colLabels=algo_headers, loc="center", cellLoc="center")
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

    # Visualisasi gabungan 1: Grid Final State (4x3)
    fig_final, axes_final = plt.subplots(4, 3, figsize=(14, 16))
    algo_names = ["Steepest Ascent", "Stochastic", "Sideways Move", "Random Restart"]
    for row_idx, algo_name in enumerate(algo_names):
        for col_idx, item in enumerate(data_algoritma[algo_name]):
            plot_deck(item["final_state"], kapal, f"{item['algoritma']} ({item['run']})\nFinal OF: {item['final_of']}", axes_final[row_idx, col_idx])
    simpan_gambar(fig_final, "final_state.png")
    if not show_plot:
        plt.close(fig_final)

    # Visualisasi gabungan 2: Grafik Konvergensi (2x2)
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

    # Visualisasi gabungan 3: Tabel Rekapitulasi Bab 3
    fig_tab, ax_tab = plt.subplots(figsize=(14, 6.5))
    ax_tab.axis("off")
    ax_tab.set_title("Hasil Eksperimen 4 Varian Hill Climbing (3 Kali Percobaan)", fontsize=13, fontweight="bold", pad=12)

    col_headers = ["Algoritma", "Percobaan", "Initial OF", "Final OF", "Durasi (detik)", "Jumlah Iterasi / Info", "Status Berhenti"]
    tabel_data = [
        [item["algoritma"], item["run"], str(item["initial_of"]), str(item["final_of"]), f"{item['durasi']:.4f} s", item["iterasi_info"], item["status"]]
        for item in daftar_hasil
    ]
    tabel = ax_tab.table(cellText=tabel_data, colLabels=col_headers, loc="center", cellLoc="center")
    tabel.auto_set_font_size(False)
    tabel.set_fontsize(8.5)
    tabel.scale(1.1, 1.5)

    for col_idx in range(len(col_headers)):
        cell = tabel[0, col_idx]
        cell.set_facecolor("#1B365D")
        cell.set_text_props(weight="bold", color="white")

    for row_idx in range(1, len(tabel_data) + 1):
        bg = "#F5F8FA" if row_idx % 2 == 0 else "#FFFFFF"
        for col_idx in range(len(col_headers)):
            tabel[row_idx, col_idx].set_facecolor(bg)

    simpan_gambar(fig_tab, "hasil_eksperimen.png")
    if not show_plot:
        plt.close(fig_tab)

    return daftar_hasil, data_algoritma


def verify_all_hill_climbing():
    """Fungsi verifikasi otomatis integritas 4 varian Hill Climbing."""
    print("Mulai pengujian 4 varian Hill Climbing...")

    # Muat konfigurasi aktual dari vehicles.json jika ada
    json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vehicles.json")
    if os.path.exists(json_path):
        try:
            kendaraan, kapal = utils.load_json(json_path)
        except Exception:
            kapal = Ship(10, 10, 50)
            kendaraan = bikin_kendaraan_awal()
    else:
        kapal = Ship(10, 10, 50)
        kendaraan = bikin_kendaraan_awal()

    # 1. Steepest Ascent
    random.seed(42)
    sa_v, sa_s, sa_iter, sa_hist = steepest_ascent_hill_climbing(kendaraan, kapal, max_iterations=100, num_candidates=20, verbose=False)
    assert isinstance(sa_iter, int) and sa_iter >= 1, "Steepest Ascent harus mencatat total iterasi >= 1"
    assert all(sa_hist[i] <= sa_hist[i + 1] for i in range(len(sa_hist) - 1)), "History Steepest Ascent harus monoton naik"
    print(f"- Steepest Ascent: PASSED (Iterasi: {sa_iter}, Skor: {sa_s})")

    # 2. Stochastic
    random.seed(42)
    st_v, st_s, st_iter, st_hist = stochastic_hill_climbing(kendaraan, kapal, max_iterations=100, num_candidates=4, verbose=False)
    assert isinstance(st_iter, int) and st_iter >= 1, "Stochastic HC harus mencatat total iterasi >= 1"
    assert all(st_hist[i] <= st_hist[i + 1] for i in range(len(st_hist) - 1)), "History Stochastic HC harus monoton naik"
    print(f"- Stochastic: PASSED (Iterasi: {st_iter}, Skor: {st_s})")

    # 3. Sideways Move
    random.seed(8)
    sm_v, sm_s, sm_iter, sm_hist = sideways_move_hill_climbing(kendaraan, kapal, max_iterations=100, max_sideways_move=5, num_candidates=4, verbose=False)
    assert isinstance(sm_iter, int) and sm_iter >= 1, "Sideways Move harus mencatat total iterasi >= 1"
    print(f"- Sideways Move: PASSED (Iterasi: {sm_iter}, Max Sideways: 5, Skor: {sm_s})")

    # 4. Random Restart
    random.seed(42)
    rr_v, rr_s, rr_restarts, rr_iters = random_restart_hill_climbing(kapal, max_restart=3, max_iterations_per_restart=20, initial_vehicles=kendaraan, num_candidates=4, verbose=False)
    assert isinstance(rr_restarts, int) and rr_restarts >= 1, "Random Restart harus mencatat total restart >= 1"
    assert len(rr_iters) == rr_restarts, "Jumlah record iterasi harus sesuai jumlah restart"
    print(f"- Random Restart: PASSED (Restarts: {rr_restarts}, Skor: {rr_s})")

    # Validasi kepatuhan constraint (overlap, batas kapal, batas kapasitas)
    for v_set, name in [(sa_v, "Steepest Ascent"), (st_v, "Stochastic"), (sm_v, "Sideways Move"), (rr_v, "Random Restart")]:
        assert not_overlapping(v_set, kapal), f"Constraint overlap gagal pada {name}"
        assert not exceed_capacity_limit(v_set, kapal), f"Constraint kapasitas kapal ({kapal.maxCapacity}) terlampaui pada {name}"
        assert not exceed_ship_limit(v_set, kapal), f"Constraint batas dek kapal terlampaui pada {name}"

    # Validasi kasus batas kapasitas ketat (tight capacity boundary)
    tight_kapal = Ship(10, 10, 20)
    tight_res = stochastic_hill_climbing(kendaraan, tight_kapal, max_iterations=50, num_candidates=4, verbose=False)
    total_w = sum(v.weight for v in tight_res.best_vehicles if v.is_loaded)
    assert total_w <= tight_kapal.maxCapacity, f"Total berat ({total_w}) melebihi batas kapasitas ketat ({tight_kapal.maxCapacity})"
    print(f"- Validasi Constraint & Batas Kapasitas ({kapal.maxCapacity} & {tight_kapal.maxCapacity}): PASSED")

    # 5. Verifikasi ketersediaan output visualisasi
    required_files = [
        "initial_state.png",
        "final_state.png",
        "objective_vs_iterasi.png",
        "hasil_eksperimen.png",
        "bin_packing_movement.png",
    ]
    for rf in required_files:
        path = os.path.join(OUTPUT_DIR, rf)
        assert os.path.exists(path), f"File visualisasi wajib tidak ditemukan: {rf}"
    print("- Output visualisasi: OK")

    print("\nSemua verifikasi berhasil.")