import utils, simulated_annealing, matplotlib.pyplot as plt, copy

#display sebelumnya disini, tapi sementara ga dipake dulu biar ga kebanyakan output

def plot(y, ylabel, run, start=0):
    plt.figure(figsize=(10, 5))
    plt.plot(range(start, start + len(y)), y)
    plt.xlabel("Banyak Iterasi")
    plt.ylabel(ylabel)
    plt.title(f"{ylabel} terhadap Banyak Iterasi (Run {run})")
    plt.grid(True)


def main_simulated_annealing():
    vehicles, ship = utils.load_json("src/vehicles.json")
    state = utils.init_state(vehicles, ship) #ini bisa di initialize disini atau di main yang real main.py, tapi sementara disini dulu buat testing

    summary = []

    for run in range(0, 3): #run 3x
        for i in range(100):

            state = utils.init_state(vehicles, ship)
            if utils.objective_function(state, ship) > 0:
                break

        initial_score = utils.objective_function(state, ship)
        best_state, best_score, objective_function_value, stuck_count, duration, acceptance_probabilities = simulated_annealing.simulated_annealing(
            copy.deepcopy(state), ship, max_iter=1000, init_temp=30, cooling_rate=0.99, stuck_threshold=10)

        summary.append((run, initial_score, best_score, stuck_count, duration))

        # Plot objective function terhadap iterasi
        plot(objective_function_value, "Objective Function", run)
        plot(acceptance_probabilities, "e^(deltaE / T)", run, start=1)

    print("\nHASIL 3X RUN")
    print(f"{'Run':<5}{'Initial':<10}{'Final':<10}{'Stuck':<8}{'Durasi (s)':<12}")
    for run, init_s, final_s, stuck, dur in summary:
        print(f"{run:<5}{init_s:<10}{final_s:<10}{stuck:<8}{dur:<12.4f}")

    plt.show() #ini jadi keluar semua barengan, nanti revisi lagi mau gimana

if __name__ == "__main__":
    main_simulated_annealing()