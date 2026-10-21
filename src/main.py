import utils
import simulated_annealing
import main_simulated_annealing
import hill_climbing
import genetic_algorithm


# ---------------------------------------------------------------------------
# Adapter per-varian Hill Climbing
# Memanggil masing-masing fungsi HC secara individual (3 run per varian)
# menggunakan data dari vehicles.json via hill_climbing.bikin_kendaraan_awal()
# ---------------------------------------------------------------------------

def _run_hc_variant(variant_name):
    """Adapter minimal: jalankan 1 varian HC (3 run) dan tampilkan hasilnya."""
    import copy, time, os
    from utils import load_json, objective_function

    # Muat data kendaraan dan kapal
    json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vehicles.json")
    kendaraan_template = hill_climbing.bikin_kendaraan_awal(json_path)
    _, kapal = load_json(json_path)

    variant_map = {
        "steepest":  hill_climbing.steepest_ascent_hill_climbing,
        "stochastic": hill_climbing.stochastic_hill_climbing,
        "sideways":  hill_climbing.sideways_move_hill_climbing,
        "random_restart": None,  # ditangani khusus di bawah
    }

    label_map = {
        "steepest":       "Steepest Ascent Hill Climbing",
        "stochastic":     "Stochastic Hill Climbing",
        "sideways":       "Sideways Move Hill Climbing",
        "random_restart": "Random Restart Hill Climbing",
    }

    print(f"\n{'='*60}")
    print(f"  {label_map[variant_name]} — 3 Run")
    print(f"{'='*60}")

    for run_idx in range(1, 4):
        init_st = hill_climbing.bikin_state_acak(kendaraan_template, kapal)
        init_of = objective_function(init_st, kapal)

        t0 = time.perf_counter()
        if variant_name == "steepest":
            res = hill_climbing.steepest_ascent_hill_climbing(
                copy.deepcopy(init_st), kapal, max_iterations=3000, verbose=False)
        elif variant_name == "stochastic":
            res = hill_climbing.stochastic_hill_climbing(
                copy.deepcopy(init_st), kapal, max_iterations=3000, num_candidates=10, verbose=False)
        elif variant_name == "sideways":
            res = hill_climbing.sideways_move_hill_climbing(
                copy.deepcopy(init_st), kapal, max_iterations=3000,
                max_sideways_move=100, num_candidates=10, verbose=False)
        else:  # random_restart
            res = hill_climbing.random_restart_hill_climbing(
                kapal, max_restart=10, max_iterations_per_restart=1000,
                initial_vehicles=copy.deepcopy(init_st), num_candidates=10, verbose=False)
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

    print()


def main():
    while True:
        print("\nPilih algoritma yang ingin dijalankan:\n")
        print("1. Steepest Ascent Hill Climbing")
        print("2. Stochastic Hill Climbing")
        print("3. Sideways Move Hill Climbing")
        print("4. Random Restart Hill Climbing")
        print("5. Simulated Annealing")
        print("6. Genetic Algorithm")
        print("0. Keluar")
        pilihan = input("Masukkan pilihan (0-6): ").strip()

        if pilihan == "0":
            break
        elif pilihan == "1":
            _run_hc_variant("steepest")
        elif pilihan == "2":
            _run_hc_variant("stochastic")
        elif pilihan == "3":
            _run_hc_variant("sideways")
        elif pilihan == "4":
            _run_hc_variant("random_restart")
        elif pilihan == "5":
            main_simulated_annealing.main_simulated_annealing()
        elif pilihan == "6":
            genetic_algorithm.genetic_algorithm()
        else:
            print("Pilihan tidak valid.")


if __name__ == "__main__":
    main()
