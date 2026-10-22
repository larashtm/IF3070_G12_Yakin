import utils, simulated_annealing, matplotlib.pyplot as plt, copy, utils_visualisation, os

output = r"C:\Users\Zek\Python\IF3070_G12_Yakin\output\simulated_annealing"

def plot(y, ylabel, run, start=0):
    plt.figure(figsize=(10, 5))
    plt.plot(range(start, start + len(y)), y)
    plt.xlabel("Banyak Iterasi")
    plt.ylabel(ylabel)
    plt.title(f"{ylabel} terhadap Banyak Iterasi (Run {run})")
    plt.grid(True)


def main_simulated_annealing():
    vehicles, ship = utils.load_json("vehicles.json")
    state = utils.init_state(vehicles, ship) #ini bisa di initialize disini atau di main yang real main.py, tapi sementara disini dulu buat testing

    choice = input("Objective Function (1 = Max Shipping Fee, 2 = Min ETA): ").strip()
    if choice == "2":
        objective = utils.objective_function_bonus

    else:
        objective = utils.objective_function

    os.makedirs(output, exist_ok=True)
    prefix = "eta" if choice == "2" else "shipping_fee"

    summary = []

    for run in range(1, 4): #run 3x
        for i in range(100):

            state = utils.init_state(vehicles, ship)
            if objective(state, ship) > 0:
                break

        initial_score = objective(state, ship)

        print(f"\nRUN {run}")
        print(f"State awal (objective function = {initial_score})")
        #utils.display(state, ship)
        fig, ax = plt.subplots(figsize=(12, 6))
        colors = utils_visualisation.build_color_map(vehicles)
        utils_visualisation.draw_state(ax, state, ship, colors, f"Run {run} - State Awal")
        fig.savefig(os.path.join(output, f"{prefix}_run{run}_state_awal.png"), dpi=150, bbox_inches="tight")

        best_state, best_score, objective_function_value, stuck_count, duration, acceptance_probabilities = simulated_annealing.simulated_annealing(
            copy.deepcopy(state), ship, max_iter=1000, init_temp=30, cooling_rate=0.99, stuck_threshold=10, objective=objective)

        print(f"State akhir (objective function = {best_score})")
        #utils.display(best_state, ship)
        fig, ax = plt.subplots(figsize=(12, 6))
        colors = utils_visualisation.build_color_map(vehicles)
        utils_visualisation.draw_state(ax, best_state, ship, colors, f"Run {run} - State Akhir")
        fig.savefig(os.path.join(output, f"{prefix}_run{run}_state_akhir.png"), dpi=150, bbox_inches="tight")

        summary.append((run, initial_score, best_score, stuck_count, duration))

        plot(objective_function_value, "Objective Function", run)
        plt.gcf().savefig(os.path.join(output, f"{prefix}_run{run}_plot_objFunc.png"), dpi=150, bbox_inches="tight")
        plot(acceptance_probabilities, "e^(deltaE / T)", run)
        plt.gcf().savefig(os.path.join(output, f"{prefix}_run{run}_plot_e.png"), dpi=150, bbox_inches="tight")

    print("\nHASIL 3X RUN")
    print(f"{'Run':<5}{'Initial':<10}{'Final':<10}{'Stuck':<8}{'Durasi (s)':<12}")
    for run, init_s, final_s, stuck, dur in summary:
        print(f"{run:<5}{init_s:<10}{final_s:<10}{stuck:<8}{dur:<12.4f}")

    plt.show() #ini jadi keluar semua barengan, nanti revisi lagi mau gimana

if __name__ == "__main__":
    main_simulated_annealing()