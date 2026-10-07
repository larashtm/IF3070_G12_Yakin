import utils
import genetic_algorithm 

def main(): 
    vehicles,ship = utils.load_json("src/vehicles.json")
    
    best_state, best_score, info = genetic_algorithm.genetic_algorithm(
        vehicles, ship, population_size = 30, max_iter = 100, mutation_rate = 0.15, seed = 42,
    )

    # GA punya banyak state awal. Untuk ditampilkan, ambil yang terbaik dari populasi awal. 
    
    initial_best = max(info["initial_population"], key=lambda state: utils.objective_function(state, ship), ) 

    print("\nBest Initial State")
    utils.display(initial_best, ship)
    print("Initial score: ", utils.objective_function(initial_best, ship))