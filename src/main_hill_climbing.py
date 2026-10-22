import copy, csv, os, sys, time
import matplotlib.pyplot as plt

_src_dir = os.path.dirname(os.path.abspath(__file__))
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

import utils
from hill_climbing_variants import (
    bikin_kendaraan_awal, bikin_state_acak, random_restart_hill_climbing,
    sideways_move_hill_climbing, steepest_ascent_hill_climbing, stochastic_hill_climbing
)

BASE_DIR = os.path.dirname(_src_dir)
OUTPUT_DIR = os.path.join(BASE_DIR, "output", "hill_climbing")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def render_ascii(vehicles, ship):
    # hasilin representasi teks grid ASCII untuk kapal
    grid = [["." for _ in range(ship.dimension.width)] for _ in range(ship.dimension.length)]
    for v in vehicles:
        if v.is_loaded:
            for x in range(v.x, v.x + v.dimension.width):
                for y in range(v.y, v.y + v.dimension.length):
                    if 0 <= x < ship.dimension.width and 0 <= y < ship.dimension.length:
                        grid[y][x] = v.id[0]
    return "\n".join("".join(r) for r in grid)


def get_json():
    # cari fail vehicles.json secara automatik
    for p in [os.path.join(os.path.dirname(__file__), "vehicles.json"), "vehicles.json", "src/vehicles.json"]:
        if os.path.exists(p):
            return os.path.abspath(p)
    return "vehicles.json"


def run_hc_variant(v_name):
    # jalanin varian Hill Climbing 3 kali percubaan
    json_path = get_json()
    template, kapal = bikin_kendaraan_awal(json_path), utils.load_json(json_path)[1]
    
    configs = {
        "steepest": ("Steepest Ascent", "steepest_ascent", lambda st: steepest_ascent_hill_climbing(copy.deepcopy(st), kapal, max_iterations=3000, verbose=False)),
        "stochastic": ("Stochastic", "stochastic", lambda st: stochastic_hill_climbing(copy.deepcopy(st), kapal, max_iterations=3000, num_candidates=10, verbose=False)),
        "sideways": ("Sideways Move", "sideways_move", lambda st: sideways_move_hill_climbing(copy.deepcopy(st), kapal, max_iterations=3000, max_sideways_move=100, num_candidates=10, verbose=False)),
        "random_restart": ("Random Restart", "random_restart", lambda st: random_restart_hill_climbing(kapal, max_restart=10, max_iterations_per_restart=1000, initial_vehicles=copy.deepcopy(st), num_candidates=10, verbose=False))
    }
    
    title, prefix, algo = configs[v_name]
    print(f"\n{'='*65}\n  {title.upper()} — 3 RUN\n{'='*65}")
    summary, histories = [], []

    for run in range(1, 4):
        init_st = bikin_state_acak(template, kapal)
        init_of = utils.objective_function(init_st, kapal)
        
        print(f"\nRUN {run}\nState awal (OF = {init_of}):")
        utils.display(init_st, kapal)
        utils.display_image(init_st, kapal)

        t0 = time.perf_counter()
        res = algo(init_st)
        durasi = time.perf_counter() - t0

        iters = sum(res.iterations_per_restart) if v_name == "random_restart" else res.total_iterations
        extra = f"({res.total_restarts} restarts)" if v_name == "random_restart" else (f"({res.sideways_moves} sideways)" if v_name == "sideways" else "")
        iter_info = f"{iters} {extra}".strip()

        print(f"\nState terbaik (OF = {res.best_score}):")
        utils.display(res.best_vehicles, kapal)
        utils.display_image(res.best_vehicles, kapal)
        print(f"Durasi: {durasi:.4f}s | Iterasi: {iter_info} | Status: {res.status}")

        with open(os.path.join(OUTPUT_DIR, f"{prefix}_run{run}_states.txt"), "w", encoding="utf-8") as f:
            f.write(f"State awal ({title}, run={run}) (OF = {init_of})\n{render_ascii(init_st, kapal)}\n\n")
            f.write(f"State akhir ({title}, run={run}) (OF = {res.best_score})\n{render_ascii(res.best_vehicles, kapal)}\n")

        histories.append((run, res.history_score))
        plt.figure(figsize=(7, 4))
        plt.plot(res.history_score, marker="o", markersize=3, color="#1f77b4")
        plt.title(f"{title} - Run {run}", fontsize=11, fontweight="bold")
        plt.xlabel("Iterasi")
        plt.ylabel("Objective Function")
        plt.grid(True, linestyle="--", alpha=0.5)
        plt.savefig(os.path.join(OUTPUT_DIR, f"{prefix}_run{run}.png"), bbox_inches="tight", dpi=150)
        plt.close()

        summary.append((run, init_of, res.best_score, iter_info, durasi, res.status))

    # hasilnya disimpan ke fail CSV varian 
    for mode, filename in [("w", f"tabel_{prefix}.csv"), ("a", "summary_hill_climbing.csv")]:
        if mode == "w" or not os.path.exists(os.path.join(OUTPUT_DIR, filename)):
            with open(os.path.join(OUTPUT_DIR, filename), mode, newline="", encoding="utf-8") as f:
                csv.writer(f).writerow(["algoritma", "percobaan", "initial_of", "final_of", "durasi_detik", "jumlah_iterasi", "status"])
        with open(os.path.join(OUTPUT_DIR, filename), "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            for r in summary:
                w.writerow([title, r[0], r[1], r[2], f"{r[4]:.4f}", r[3], r[5]])

    plt.figure(figsize=(8, 4.5))
    for r, h in histories:
        plt.plot(h, label=f"Run {r}", linewidth=1.8, marker="o", markersize=3)
    plt.title(f"Konvergensi 3 Run - {title}", fontsize=11, fontweight="bold")
    plt.xlabel("Iterasi")
    plt.ylabel("Objective Function")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.savefig(os.path.join(OUTPUT_DIR, f"{prefix}_convergence.png"), bbox_inches="tight", dpi=150)
    plt.close()

    print(f"Selesai! Output disimpan di {OUTPUT_DIR}\n")

def main_steepest_ascent(): run_hc_variant("steepest")
def main_stochastic(): run_hc_variant("stochastic")
def main_sideways_move(): run_hc_variant("sideways")
def main_random_restart(): run_hc_variant("random_restart")

def main_hill_climbing(variant=None):
    if variant:
        run_hc_variant(variant)
    else:
        for fn in [main_steepest_ascent, main_stochastic, main_sideways_move, main_random_restart]:
            fn()


if __name__ == "__main__":
    main_hill_climbing()