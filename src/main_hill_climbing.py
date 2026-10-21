import copy
import os
import sys
import time

# Pastikan direktori saat ini masuk ke sys.path untuk impor lokal
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

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
    return os.path.join(base_dir, "vehicles.json")


def run_hc_variant(variant_name):
    """Menjalankan satu varian Hill Climbing sebanyak 3 kali percobaan independen."""
    json_path = get_json_path()
    kendaraan_template = hill_climbing.bikin_kendaraan_awal(json_path)
    _, kapal = utils.load_json(json_path)

    label_map = {
        "steepest": "Steepest Ascent Hill Climbing",
        "stochastic": "Stochastic Hill Climbing",
        "sideways": "Sideways Move Hill Climbing",
        "random_restart": "Random Restart Hill Climbing",
    }

    title = label_map.get(variant_name, variant_name)
    print(f"\n{'=' * 60}")
    print(f"  {title} — 3 Run")
    print(f"{'=' * 60}")

    summary = []

    for run_idx in range(1, 4):
        init_st = hill_climbing.bikin_state_acak(kendaraan_template, kapal)
        init_of = utils.objective_function(init_st, kapal)

        t0 = time.perf_counter()
        if variant_name == "steepest":
            res = hill_climbing.steepest_ascent_hill_climbing(
                copy.deepcopy(init_st), kapal, max_iterations=3000, verbose=False
            )
        elif variant_name == "stochastic":
            res = hill_climbing.stochastic_hill_climbing(
                copy.deepcopy(init_st), kapal, max_iterations=3000, num_candidates=10, verbose=False
            )
        elif variant_name == "sideways":
            res = hill_climbing.sideways_move_hill_climbing(
                copy.deepcopy(init_st),
                kapal,
                max_iterations=3000,
                max_sideways_move=100,
                num_candidates=10,
                verbose=False,
            )
        elif variant_name == "random_restart":
            res = hill_climbing.random_restart_hill_climbing(
                kapal,
                max_restart=10,
                max_iterations_per_restart=1000,
                initial_vehicles=copy.deepcopy(init_st),
                num_candidates=10,
                verbose=False,
            )
        else:
            raise ValueError(f"Varian '{variant_name}' tidak dikenal.")

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
    """Entry point umum untuk modul Hill Climbing."""
    if variant is not None:
        run_hc_variant(variant)
    else:
        # Jalankan seluruh varian secara berurutan jika dipanggil tanpa argumen
        main_steepest_ascent()
        main_stochastic()
        main_sideways_move()
        main_random_restart()


if __name__ == "__main__":
    main_hill_climbing()
