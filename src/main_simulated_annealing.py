import utils, simulated_annealing, matplotlib.pyplot as plt


def main_simulated_annealing():
    vehicles, ship = utils.load_json("src/vehicles.json")
    state = utils.init_state(vehicles, ship) #ini bisa di initialize disini atau di masing masing algoritma, sementara disini dulu buat testing

    print("\nINITIAL STATE")
    print("SHIP")
    utils.display(state, ship)
    print("MAP")
    utils.display_map(state, ship)

    print("\nSWAP")
    utils.swap(state, ship)
    utils.display(state, ship)
    print("MAP")
    utils.display_map(state, ship)

    print("\nMOVE")
    utils.move(state, ship)
    utils.display(state, ship)
    print("MAP")
    utils.display_map(state, ship)

    #tester simulated annealing
    print("\nSIMULATED ANNEALING")
    best_state, best_score, objective_function_value, stuck_count, duration = simulated_annealing.simulated_annealing(state, ship, max_iter=100, init_temp=100, cooling_rate=0.99, stuck_threshold=10)
    print("\nBEST STATE")
    utils.display(best_state, ship)
    print("BEST SCORE")
    print(best_score)
    print("MAP")
    utils.display_map(best_state, ship)
    print("OBJECTIVES")
    print(objective_function_value)
    print("STUCK COUNT")
    print(stuck_count)  
    print("DURATION")
    print(duration)

    # Plot objective function terhadap iterasi
    plt.figure(figsize=(10, 5))
    plt.plot(range(len(objective_function_value)), objective_function_value)

    plt.xlabel("Banyak Iterasi")
    plt.ylabel("e^(deltaE / T)")
    plt.title("e^(deltaE / T) terhadap Banyak Iterasi")
    plt.grid(True)
    plt.show()

main_simulated_annealing()