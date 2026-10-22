import copy, csv, os, sys, time
import matplotlib.pyplot as plt

_src_dir = os.path.dirname(os.path.abspath(__file__))
if _src_dir not in sys.path: sys.path.insert(0, _src_dir)

import utils
from utils import objective_function
from hill_climbing_variants import (
    bikin_kendaraan_awal, bikin_state_acak,
    random_restart_hill_climbing, sideways_move_hill_climbing,
    steepest_ascent_hill_climbing, stochastic_hill_climbing,
)

BASE_DIR = os.path.dirname(_src_dir)
OUTPUT_DIR = os.path.join(BASE_DIR, "output", "hill_climbing")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def render_deck_ascii(vehicles, ship):
    # Bikin visualisasi teks simpel buat posisi kapal di grid
    grid = [["." for _ in range(ship.dimension.width)] for _ in range(ship.dimension.length)]
    for v in vehicles:
        if v.is_loaded:
            for x in range(v.x, v.x + v.dimension.width):
                for y in range(v.y, v.y + v.dimension.length):
                    if 0 <= x < ship.dimension.width and 0 <= y < ship.dimension.length:
                        grid[y][x] = v.id[0]
    return "\n".join("".join(row) for row in grid)

def simpan_gambar(fig, filename):
    # Simpan plot matplotlib ke folder output biar gampang dicek
    path = os.path.join(OUTPUT_DIR, filename)
    fig.savefig(path, bbox_inches="tight", dpi=150)
    print(f"Mantap, gambar aman di: {path}")


def run_experiment(show_plot=False, json_path=None):
    # Gaspol eksperimen 4 varian HC, masing-masing 3 run biar datanya valid.
    if json_path is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        candidates = [os.path.join(base_dir, "vehicles.json"), os.path.join(base_dir, "..", "vehicles.json"), "vehicles.json", "src/vehicles.json"]
        for p in candidates:
            if os.path.exists(p): json_path = os.path.abspath(p); break
        if json_path is None: json_path = os.path.join(base_dir, "vehicles.json")

    kendaraan_template = bikin_kendaraan_awal(json_path)
    _, kapal = utils.load_json(json_path)

    print("\n--- Mulai Benchmark 4 Varian Hill Climbing (3 Run Santai) ---")

    daftar_hasil = []
    data_algoritma = {
        "Steepest Ascent": [], "Stochastic": [],
        "Sideways Move": [], "Random Restart": [],
    }, 

    for i in range(1, 4):
        run_label = f"Run {i}"
        init_st = bikin_state_acak(kendaraan_template, kapal)
        init_of = objective_function(init_st, kapal)

        # 1. Steepest Ascent
        t0 = time.perf_counter()
        res = steepest_ascent_hill_climbing(copy.deepcopy(init_st), kapal, max_iterations=3000, verbose=False)
        item1 = {
            "algoritma": "Steepest Ascent", "run": run_label,
            "initial_state": copy.deepcopy(init_st), "initial_of": init_of,
            "final_of": res.best_score, "iterasi_info": f"{res.total_iterations} iterasi",
            "durasi": time.perf_counter() - t0, "status": res.status,
            "final_state": res.best_vehicles, "history": res.history_score,
        }
        daftar_hasil.append(item1); data_algoritma["Steepest Ascent"].append(item1)

        # 2. Stochastic
        t0 = time.perf_counter()
        res = stochastic_hill_climbing(copy.deepcopy(init_st), kapal, max_iterations=3000, num_candidates=10, verbose=False)
        item2 = {
            "algoritma": "Stochastic", "run": run_label,
            "initial_state": copy.deepcopy(init_st), "initial_of": init_of,
            "final_of": res.best_score, "iterasi_info": f"{res.total_iterations} iterasi",
            "durasi": time.perf_counter() - t0, "status": res.status,
            "final_state": res.best_vehicles, "history": res.history_score,
        }
        daftar_hasil.append(item2); data_algoritma["Stochastic"].append(item2)
        
        # 3. Sideways Move
        t0 = time.perf_counter()
        res = sideways_move_hill_climbing(copy.deepcopy(init_st), kapal, max_iterations=3000, max_sideways_move=100, num_candidates=10, verbose=False)
        item3 = {
            "algoritma": "Sideways Move", "run": run_label,
            "initial_state": copy.deepcopy(init_st), "initial_of": init_of,
            "final_of": res.best_score, "iterasi_info": f"{res.total_iterations} iterasi ({res.sideways_moves} sideways)",
            "durasi": time.perf_counter() - t0, "status": res.status,
            "final_state": res.best_vehicles, "history": res.history_score,
        }
        daftar_hasil.append(item3); data_algoritma["Sideways Move"].append(item3)

        # 4. Random Restart
        t0 = time.perf_counter()
        res = random_restart_hill_climbing(kapal, max_restart=10, max_iterations_per_restart=1000, initial_vehicles=copy.deepcopy(init_st), num_candidates=10, verbose=False)
        item4 = {
            "algoritma": "Random Restart", "run": run_label,
            "initial_state": res.initial_state if hasattr(res, "initial_state") and res.initial_state is not None else copy.deepcopy(init_st),
            "initial_of": res.initial_score if hasattr(res, "initial_score") and res.initial_score is not None else init_of,
            "final_of": res.best_score, "iterasi_info": f"{sum(res.iterations_per_restart)} iterasi ({res.total_restarts} restarts)",
            "durasi": time.perf_counter() - t0, "status": res.status,
            "final_state": res.best_vehicles, "history": res.history_score,
        }
        daftar_hasil.append(item4); data_algoritma["Random Restart"].append(item4)

    prefix_map = {
        "Steepest Ascent": "steepest_ascent", "Stochastic": "stochastic",
        "Sideways Move": "sideways_move", "Random Restart": "random_restart",
    }
    run_colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]

    for algo_key, prefix in prefix_map.items():
        runs = data_algoritma[algo_key]
        for idx, item in enumerate(runs, 1):
            # Dump state awal/akhir ke text file
            txt_path = os.path.join(OUTPUT_DIR, f"{prefix}_run{idx}_states.txt")
            init_str = render_deck_ascii(item["initial_state"], kapal)
            final_str = render_deck_ascii(item["final_state"], kapal)
            with open(txt_path, "w", encoding="utf-8") as f_txt:
                f_txt.write(f"State awal ({algo_key}, run={idx}) (OF = {item['initial_of']})\n{init_str}\n\n")
                f_txt.write(f"State akhir ({algo_key}, run={idx}) (OF = {item['final_of']})\n{final_str}\n")

            # Plot individual konvergensi
            fig_run, ax = plt.subplots(figsize=(8, 4.5))
            ax.plot(range(len(item["history"])), item["history"], color=run_colors[idx-1], marker="o", markersize=4, linewidth=2, label=f"Final OF: {item['final_of']}")
            ax.set_title(f"Konvergensi: {algo_key} - {item['run']}", fontsize=11, fontweight="bold")
            ax.set_xlabel("Iterasi", fontsize=9); ax.set_ylabel("Objective Function", fontsize=9)
            ax.grid(True, linestyle="--", alpha=0.5); ax.legend(fontsize=9, loc="lower right")
            simpan_gambar(fig_run, f"{prefix}_run{idx}.png")
            plt.close(fig_run)

        # Simpan CSV per varian
        csv_path = os.path.join(OUTPUT_DIR, f"tabel_{prefix}.csv")
        with open(csv_path, "w", newline="", encoding="utf-8") as f_csv:
            writer = csv.writer(f_csv)
            writer.writerow(["algoritma", "percobaan", "initial_of", "final_of", "durasi_detik", "jumlah_iterasi", "status"])
            for r_item in runs:
                writer.writerow([algo_key, r_item["run"], r_item["initial_of"], r_item["final_of"], f"{r_item['durasi']:.4f}", r_item["iterasi_info"], r_item["status"]])

    # Plot Grid 2x2 Gabungan
    fig_conv, axes = plt.subplots(2, 2, figsize=(13, 9))
    coords = [(0, 0), (0, 1), (1, 0), (1, 1)]
    markers = ["o", "s", "^"]
    for idx, algo_name in enumerate(prefix_map.keys()):
        r, c = coords[idx]; ax = axes[r, c]
        for run_idx, item in enumerate(data_algoritma[algo_name]):
            ax.plot(range(len(item["history"])), item["history"], label=f"{item['run']} (Final: {item['final_of']})", color=run_colors[run_idx], marker=markers[run_idx], markersize=4, linewidth=1.8, alpha=0.85)
        ax.set_title(f"Konvergensi: {algo_name}", fontsize=11, fontweight="bold")
        ax.set_xlabel("Jumlah Iterasi", fontsize=9); ax.set_ylabel("Objective Function", fontsize=9)
        ax.grid(True, linestyle="--", alpha=0.5); ax.legend(fontsize=9, loc="lower right")
    simpan_gambar(fig_conv, "objective_vs_iterasi.png")
    if not show_plot:
        plt.close(fig_conv)

    summary_csv = os.path.join(OUTPUT_DIR, "summary_hill_climbing.csv")
    with open(summary_csv, "w", newline="", encoding="utf-8") as f_sum:
        writer = csv.writer(f_sum)
        writer.writerow(["algoritma", "percobaan", "initial_of", "final_of", "durasi_detik", "jumlah_iterasi", "status"])
        for item in daftar_hasil:
            writer.writerow([item["algoritma"], item["run"], item["initial_of"], item["final_of"], f"{item['durasi']:.4f}", item["iterasi_info"], item["status"]])

    print("\n[Selesai] Semua file eksperimen Hill Climbing berhasil dieksekusi!\n")
    return daftar_hasil, data_algoritma


if __name__ == "__main__":
    run_experiment(show_plot=False)