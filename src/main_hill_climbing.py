import copy, os, sys, time, matplotlib.pyplot as plt

_src_dir = os.path.dirname(os.path.abspath(__file__))
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

import utils, utils_visualisation
from hill_climbing_variants import (
    bikin_kendaraan_awal, bikin_state_acak,
    random_restart_hill_climbing, sideways_move_hill_climbing,
    steepest_ascent_hill_climbing, stochastic_hill_climbing,
)

output = r"C:\Users\Zek\Python\IF3070_G12_Yakin\output\hill_climbing"


def get_json_path():
    base = os.path.dirname(os.path.abspath(__file__))
    for p in [os.path.join(base, "vehicles.json"), os.path.join(base, "..", "vehicles.json"), "vehicles.json", "src/vehicles.json"]:
        if os.path.exists(p):
            return os.path.abspath(p)
    return "vehicles.json"


def plot(y, ylabel, title, run, start=0):
    plt.figure(figsize=(10, 5))
    plt.plot(range(start, start + len(y)), y)
    plt.xlabel("Banyak Iterasi")
    plt.ylabel(ylabel)
    plt.title(f"{ylabel} terhadap Banyak Iterasi - {title} (Run {run})")
    plt.grid(True)


def run_hc_variant(v_name):
    json_path = get_json_path()
    vehicles, ship = utils.load_json(json_path)
    template = bikin_kendaraan_awal(json_path)
    colors = utils_visualisation.build_color_map(vehicles)
    os.makedirs(output, exist_ok=True)

    algos = {
        "steepest": ("Steepest Ascent", lambda st: steepest_ascent_hill_climbing(copy.deepcopy(st), ship, max_iterations=3000, verbose=False)),
        "stochastic": ("Stochastic", lambda st: stochastic_hill_climbing(copy.deepcopy(st), ship, max_iterations=3000, num_candidates=10, verbose=False)),
        "sideways": ("Sideways Move", lambda st: sideways_move_hill_climbing(copy.deepcopy(st), ship, max_iterations=3000, max_sideways_move=100, num_candidates=10, verbose=False)),
        "random_restart": ("Random Restart", lambda st: random_restart_hill_climbing(ship, max_restart=10, max_iterations_per_restart=1000, initial_vehicles=copy.deepcopy(st), num_candidates=10, verbose=False)),
    }
    title, algo = algos[v_name]

    def gambar(st, run, nama, label):
        fig, ax = plt.subplots(figsize=(12, 6))
        utils_visualisation.draw_state(ax, st, ship, colors, f"Run {run} - {label}")
        fig.savefig(os.path.join(output, f"{v_name}_run{run}_{nama}.png"), dpi=150, bbox_inches="tight")

    print(f"\n{title.upper()} - 3 RUN")
    summary = []

    for run in range(1, 4): #run 3x
        state = bikin_state_acak(template, ship)
        initial_score = utils.objective_function(state, ship)
        print(f"\nRUN {run}")
        print(f"State awal (objective function = {initial_score})")
        gambar(state, run, "state_awal", "State Awal")

        start_time = time.perf_counter()
        res = algo(state)
        duration = time.perf_counter() - start_time

        total_iter = sum(res.iterations_per_restart) if v_name == "random_restart" else res.total_iterations
        print(f"State akhir (objective function = {res.best_score})")
        gambar(res.best_vehicles, run, "state_akhir", "State Akhir")

        summary.append((run, initial_score, res.best_score, total_iter, duration, res.status))

        plot(res.history_score, "Objective Function", title, run)
        plt.gcf().savefig(os.path.join(output, f"{v_name}_run{run}_plot_objFunc.png"), dpi=150, bbox_inches="tight")

    print(f"\nHASIL 3X RUN ({title})")
    print(f"{'Run':<5}{'Initial':<10}{'Final':<10}{'Iterasi':<10}{'Durasi (s)':<12}{'Status':<20}")
    for run, init_s, final_s, iters, dur, stat in summary:
        print(f"{run:<5}{init_s:<10}{final_s:<10}{iters:<10}{dur:<12.4f}{stat:<20}")

    plt.show()


# Fungsi publik per varian untuk dipanggil oleh main.py
def main_steepest_ascent():
    run_hc_variant("steepest")


def main_stochastic():
    run_hc_variant("stochastic")


def main_sideways_move():
    run_hc_variant("sideways")


def main_random_restart():
    run_hc_variant("random_restart")


def main_hill_climbing(variant=None):
    if variant:
        run_hc_variant(variant)
    else:
        for fn in [main_steepest_ascent, main_stochastic, main_sideways_move, main_random_restart]:
            fn()


if __name__ == "__main__":
    main_hill_climbing()