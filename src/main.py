import utils, json, hill_climbing, simulated_annealing, genetic_algorithm


def main():
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
    best_state, best_score = simulated_annealing.simulated_annealing(state, ship, max_iter=100, init_temp=100, cooling_rate=0.99)
    print("\nBEST STATE")
    utils.display(best_state, ship)
    print("BEST SCORE")
    print(best_score)
    print("MAP")
    utils.display_map(best_state, ship)

main()