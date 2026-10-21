import utils
import main_hill_climbing
import main_simulated_annealing
import simulated_annealing
import genetic_algorithm

# Alias backward compatibility jika ada modul lain yang mengimpor dari main
_run_hc_variant = main_hill_climbing.run_hc_variant


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
            main_hill_climbing.main_steepest_ascent()
        elif pilihan == "2":
            main_hill_climbing.main_stochastic()
        elif pilihan == "3":
            main_hill_climbing.main_sideways_move()
        elif pilihan == "4":
            main_hill_climbing.main_random_restart()
        elif pilihan == "5":
            main_simulated_annealing.main_simulated_annealing()
        elif pilihan == "6":
            genetic_algorithm.genetic_algorithm()
        else:
            print("Pilihan tidak valid.")


if __name__ == "__main__":
    main()
