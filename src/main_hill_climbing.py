import copy
import os
import sys
import time

# Pastikan path modul src tersedia
_src_dir = os.path.dirname(os.path.abspath(__file__))
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

import utils
from hill_climbing_variants import (
    bikin_kendaraan_awal,
    bikin_state_acak,
    random_restart_hill_climbing,
    sideways_move_hill_climbing,
    steepest_ascent_hill_climbing,
    stochastic_hill_climbing,
)


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
    return os.path.join(base_dir, "vehicles.json")


def run_hc_variant(variant_name):
    """Menjalankan satu varian Hill Climbing sebanyak 3 kali percobaan independen dengan format output CLI konsisten."""
    json_path = get_json_path()
    kendaraan_template = bikin_kendaraan_awal(json_path)
    _, kapal = utils.load_json(json_path)

    label_map = {
        "steepest": "Steepest Ascent Hill Climbing",
        "stochastic": "Stochastic Hill Climbing",
        "sideways": "Sideways Move Hill Climbing",
        "random_restart": "Random Restart Hill Climbing",
    }

    title = label_map.get(variant_name, variant_name)
    print(f"\n{'=' * 65}")
    print(f"  {title.upper()} — 3 RUN")
    print(f"{'=' * 65}")

    summary = []

    for run_idx in range(1, 4):
        init_st = bikin_state_acak(kendaraan_template, kapal)
        init_of = utils.objective_function(init_st, kapal)

        print(f"\nRUN {run_idx}")
        print(f"State awal (objective function = {init_of}):")
        utils.display(init_st, kapal)

        t0 = time.perf_counter()
        if variant_name == "steepest":
            res = steepest_ascent_hill_climbing(
                copy.deepcopy(init_st), kapal, max_iterations=3000, verbose=False
            )
            best_state = res.best_vehicles
            best_of = res.best_score
            total_iters = res.total_iterations
            status = res.status
            extra_info = None

        elif variant_name == "stochastic":
            res = stochastic_hill_climbing(
                copy.deepcopy(init_st), kapal, max_iterations=3000, num_candidates=10, verbose=False
            )
            best_state = res.best_vehicles
            best_of = res.best_score
            total_iters = res.total_iterations
            status = res.status
            extra_info = None

        elif variant_name == "sideways":
            res = sideways_move_hill_climbing(
                copy.deepcopy(init_st),
                kapal,
                max_iterations=3000,
                max_sideways_move=100,
                num_candidates=10,
                verbose=False,
            )
            best_state = res.best_vehicles
            best_of = res.best_score
            total_iters = res.total_iterations
            status = res.status
            extra_info = f"Jumlah sideways move: {res.sideways_moves}"

        elif variant_name == "random_restart":
            res = random_restart_hill_climbing(
                kapal,
                max_restart=10,
                max_iterations_per_restart=1000,
                initial_vehicles=copy.deepcopy(init_st),
                num_candidates=10,
                verbose=False,
            )
            # Pastikan state terbaik adalah best state global sepanjang seluruh restart
            best_state = res.best_vehicles
            best_of = res.best_score
            total_iters = sum(res.iterations_per_restart)
            status = res.status
            extra_info = f"Jumlah restart: {res.total_restarts}"
            if hasattr(res, "initial_score") and res.initial_score is not None:
                init_of = res.initial_score
        else:
            raise ValueError(f"Varian '{variant_name}' tidak dikenal.")

        durasi = time.perf_counter() - t0

        print(f"\nState terbaik (objective function = {best_of}):")
        utils.display(best_state, kapal)

        print("\nRingkasan run:")
        print(f"- Objective function awal: {init_of}")
        print(f"- Objective function terbaik: {best_of}")
        print(f"- Jumlah iterasi: {total_iters}")
        if extra_info:
            print(f"- {extra_info}")
        print(f"- Status berhenti: {status}")
        print(f"- Durasi: {durasi:.4f} detik")

        iter_summary = f"{total_iters}"
        if variant_name == "sideways":
            iter_summary = f"{total_iters} ({res.sideways_moves} sideways)"
        elif variant_name == "random_restart":
            iter_summary = f"{total_iters} ({res.total_restarts} restarts)"

        summary.append((run_idx, init_of, best_of, iter_summary, durasi, status))

    print(f"\n{'-' * 70}")
    print(f"HASIL 3X RUN ({title})")
    print(f"{'-' * 70}")
    print(f"{'Run':<6}{'Initial':<10}{'Final':<10}{'Iterasi':<22}{'Durasi (s)':<14}{'Status':<20}")
    for run_i, init_s, fin_s, iters, dur, stat in summary:
        print(f"{run_i:<6}{init_s:<10}{fin_s:<10}{iters:<22}{dur:<14.4f}{stat:<20}")
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
    """Entry point umum untuk modul Hill Climbing."""
    if variant is not None:
        run_hc_variant(variant)
    else:
        main_steepest_ascent()
        main_stochastic()
        main_sideways_move()
        main_random_restart()


if __name__ == "__main__":
    main_hill_climbing()
