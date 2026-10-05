import utils

def main():
    vehicles, ship = utils.load_json("src/vehicles.json")
    state = utils.init_state(vehicles, ship)

    print("INITIAL STATE")
    print("SHIP")
    utils.display(state, ship)
    print("MAP")
    utils.display_map(state, ship)

    print("\nSWAP")
    utils.swap(state)
    utils.display(state, ship)
    print("MAP")
    utils.display_map(state, ship)

main()