import copy, csv, os, sys, time
import matplotlib.pyplot as plt

_src_dir = os.path.dirname(os.path.abspath(__file__))
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

import utils
import hill_climbing


def get_json_path():
    """Mencari lokasi vehicles.json secara andal dari berbagai working directory."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(base_dir, "vehicles.json"),
        os.path.join(base_dir, "..", "vehicles.json"),
        "vehicles.json",
        "src/vehicles.json",
    ]
    for p in candidates:
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
        final_of = res[1]
        total_iter = res[2]
        status = res.status if hasattr(res, "status") else "-"

        print(f"\n  Run {run_idx}")
        print(f"    Initial OF : {init_of}")
        print(f"    Final OF   : {final_of}")
        print(f"    Durasi     : {durasi:.4f} detik")
        print(f"    Iterasi    : {total_iter}")
        print(f"    Status     : {status}")

        summary.append((run_idx, init_of, final_of, total_iter, durasi, status))

    print(f"\n{'-' * 60}")
    print(f"  RINGKASAN HASIL 3X RUN ({title})")
    print(f"{'-' * 60}")
    print(f"  {'Run':<6}{'Initial':<10}{'Final':<10}{'Iterasi':<12}{'Durasi (s)':<14}{'Status':<20}")
    for run_i, init_s, fin_s, iters, dur, stat in summary:
        print(f"  {run_i:<6}{init_s:<10}{fin_s:<10}{str(iters):<12}{dur:<14.4f}{stat:<20}")
    print()


# Fungsi publik per varian untuk dipanggil oleh main.py
def main_steepest_ascent():
    """Entry point untuk Steepest Ascent Hill Climbing."""
    run_hc_variant("steepest")


def main_stochastic():
    """Entry point untuk Stochastic Hill Climbing."""
    run_hc_variant("stochastic")


def main_sideways_move():
    """Entry point untuk Sideways Move Hill Climbing."""
    run_hc_variant("sideways")


def main_random_restart():
    """Entry point untuk Random Restart Hill Climbing."""
    run_hc_variant("random_restart")


def main_hill_climbing(variant=None):
    if variant:
        run_hc_variant(variant)
    else:
        for fn in [main_steepest_ascent, main_stochastic, main_sideways_move, main_random_restart]:
            fn()


if __name__ == "__main__":
    main_hill_climbing()