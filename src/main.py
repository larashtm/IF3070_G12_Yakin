import utils

def main():
    vehicles, ship = utils.load_json("src/vehicles.json")
    state = utils.init_state(vehicles, ship) #ini bisa di initialize disini atau di masing masing algoritma, sementara disini dulu buat testing

    print("INITIAL STATE")
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

main()