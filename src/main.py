import utils, json, main_simulated_annealing, simulated_annealing
#import hill_climbing, genetic_algorithm
#import main_hill_climbing, main_genetic_algorithm

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
            pass
        elif pilihan == "2":
            pass
        elif pilihan == "3":
            pass
        elif pilihan == "4":
            pass
        elif pilihan == "5":
            main_simulated_annealing.main_simulated_annealing()
        elif pilihan == "6":
            pass
        else:
            print("Pilihan tidak valid.")


if __name__ == "__main__":
    main()