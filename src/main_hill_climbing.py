import copy, csv, os, time, matplotlib.pyplot as plt, utils, utils_visualisation
from hill_climbing import bikin_kendaraan_awal, bikin_state_acak
from random_restart_hc import random_restart_hill_climbing
from sideways_move_hc import sideways_move_hill_climbing
from steepest_ascent_hc import steepest_ascent_hill_climbing
from stochastic_hc import stochastic_hill_climbing

src = os.path.dirname(os.path.abspath(__file__))
output = os.path.join(os.path.dirname(src), "output", "hill_climbing") #output/ sejajar dengan src/


def new_final_folder(base):
    os.makedirs(base, exist_ok=True)
    nums = [int(n[5:]) for n in os.listdir(base) if n.startswith("final") and n[5:].isdigit()]
    folder = os.path.join(base, f"final{max(nums, default=0) + 1}")
    os.makedirs(folder)
    return folder


def get_json_path():
    for p in [os.path.join(src, "vehicles.json"), os.path.join(src, "..", "vehicles.json"), "vehicles.json"]:
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


def run_hc_variant(v_name, out=None):
    out = out or new_final_folder(output) #folder final[x] baru tiap run
    json_path = get_json_path()
    vehicles, ship = utils.load_json(json_path)
    template = bikin_kendaraan_awal(json_path)
    colors = utils_visualisation.build_color_map(vehicles)

    algos = {
        "steepest": ("Steepest Ascent", lambda st: steepest_ascent_hill_climbing(copy.deepcopy(st), ship, max_iterations=3000, tampil=False)),
        "stochastic": ("Stochastic", lambda st: stochastic_hill_climbing(copy.deepcopy(st), ship, max_iterations=3000, num_candidates=10, tampil=False)),
        "sideways": ("Sideways Move", lambda st: sideways_move_hill_climbing(copy.deepcopy(st), ship, max_iterations=3000, max_sideways_move=100, num_candidates=10, tampil=False)),
        "random_restart": ("Random Restart", lambda st: random_restart_hill_climbing(ship, max_restart=10, max_iterations_per_restart=1000, initial_vehicles=copy.deepcopy(st), num_candidates=10, tampil=False)),
    }
    title, algo = algos[v_name]

    def gambar(st, run, nama, label):
        fig, ax = plt.subplots(figsize=(12, 6))
        utils_visualisation.draw_state(ax, st, ship, colors, f"Run {run} - {label}")
        fig.savefig(os.path.join(out, f"{v_name}_run{run}_{nama}.png"), dpi=150, bbox_inches="tight")
        plt.close(fig)

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
        plt.gcf().savefig(os.path.join(out, f"{v_name}_run{run}_plot_objFunc.png"), dpi=150, bbox_inches="tight")
        plt.close()

    print(f"\nHASIL 3X RUN ({title})")
    print(f"{'Run':<5}{'Initial':<10}{'Final':<10}{'Iterasi':<10}{'Durasi (s)':<12}{'Status':<20}")
    for run, init_s, final_s, iters, dur, stat in summary:
        print(f"{run:<5}{init_s:<10}{final_s:<10}{iters:<10}{dur:<12.4f}{stat:<20}")

    #summaryHC, kalau varian lain jalan di folder yang sama barisnya nambah
    path = os.path.join(out, "summaryHC.csv")
    baru = not os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if baru:
            w.writerow(["algoritma", "percobaan", "initial_of", "final_of", "durasi_detik", "jumlah_iterasi", "status"])
        for run, init_s, final_s, iters, dur, stat in summary:
            w.writerow([title, run, init_s, final_s, f"{dur:.4f}", iters, stat])

    #plt.show()

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
        out = new_final_folder(output) #keempat varian satu folder
        for v in ["steepest", "stochastic", "sideways", "random_restart"]:
            run_hc_variant(v, out)


if __name__ == "__main__":
    main_hill_climbing()