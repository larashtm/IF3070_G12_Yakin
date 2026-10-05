import utils, json
from hill_climbing import *
from simulated_annealing import *
from genetic_algorithm import *


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

main()