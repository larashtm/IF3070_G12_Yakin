import os
import sys
import json
import utils
import hill_climbing
import simulated_annealing
import genetic_algorithm

# Re-ekspor objek & helper agar tetap backward-compatible bila diimpor dari main
Vehicle = utils.Vehicle
Ship = utils.Ship
Dimension = utils.Dimension
shipping_fee = utils.shipping_fee
not_overlapping = utils.not_overlapping
exceed_ship_limit = utils.exceed_ship_limit
exceed_capacity_limit = utils.exceed_capacity_limit
objective_function = utils.objective_function
# Re-ekspor fungsi dengan wrapper toleran terhadap argumen ship opsional
def swap(vehicles, ship=None):
    if ship is not None:
        return utils.swap(vehicles, ship)
    # Jika dipanggil tanpa ship (format awal hill climbing), lakukan swap koordinat
    loaded = [v for v in vehicles if v.is_loaded]
    target_list = loaded if len(loaded) >= 2 else vehicles
    if len(target_list) >= 2:
        import random
        va, vb = random.sample(target_list, 2)
        va.x, vb.x = vb.x, va.x
        va.y, vb.y = vb.y, va.y


def move(vehicles, ship):
    return utils.move(vehicles, ship)


def rotate(vehicles, ship=None):
    if ship is not None:
        return utils.rotate(vehicles, ship)
    import random
    v = random.choice(vehicles)
    if v.orientation == "Horizontal":
        v.orientation = "Vertical"
    else:
        v.orientation = "Horizontal"
    v.dimension.width, v.dimension.length = v.dimension.length, v.dimension.width
display = utils.display
display_map = utils.display_map
load_json = utils.load_json
init_state = utils.init_state


def main():
    json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vehicles.json")
    if not os.path.exists(json_path):
        json_path = "src/vehicles.json"
    vehicles, ship = utils.load_json(json_path)
    state = utils.init_state(vehicles, ship)

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

    # Tester simulated annealing
    print("\nSIMULATED ANNEALING")
    best_sa_state, best_sa_score = simulated_annealing.simulated_annealing(
        state, ship, max_iter=100, init_temp=100, cooling_rate=0.99
    )
    print("\nBEST STATE (SA)")
    utils.display(best_sa_state, ship)
    print("BEST SCORE (SA):", best_sa_score)
    print("MAP (SA)")
    utils.display_map(best_sa_state, ship)

    # Tester Hill Climbing (4 Varian)
    print("\nHILL CLIMBING EXPERIMENT & VERIFICATION")
    hill_climbing.verify_all_hill_climbing()


if __name__ == "__main__":
    main()
