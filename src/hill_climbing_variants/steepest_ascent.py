import copy, random
from utils import objective_function
from .common import SearchResult, get_all_neighbors, get_random_neighbor

def steepest_ascent_hill_climbing(initial_vehicles, ship, max_iterations=3000, num_candidates=None, verbose=False):
    # Varian Steepest Ascent: Evaluasi tetangga dan pindah ke skor tertinggi
    current_vehicles = copy.deepcopy(initial_vehicles)
    current_score = objective_function(current_vehicles, ship)
    history_score = [current_score]
    total_iterations = 0
    status = "Local Optima"

    if verbose:
        print(f"[0] State Awal. Skor: {current_score}")
    while total_iterations < max_iterations:
        total_iterations += 1
        better_neighbors = []
        if num_candidates is None or num_candidates == "all":
            for candidate in get_all_neighbors(current_vehicles, ship):
                score = objective_function(candidate, ship)
                if score > current_score:
                    better_neighbors.append((candidate, score))
        else:
            for _ in range(num_candidates):
                candidate = get_random_neighbor(current_vehicles, ship)
                score = objective_function(candidate, ship)
                if score > current_score:
                    better_neighbors.append((candidate, score))
        if not better_neighbors:
            status = "Local Optima"
            break
        max_score = max(item[1] for item in better_neighbors)
        best_candidates = [item for item in better_neighbors if item[1] == max_score]
        best_candidate, best_candidate_score = random.choice(best_candidates)
        current_vehicles, current_score = copy.deepcopy(best_candidate), best_candidate_score
        history_score.append(current_score)
        if verbose:
            print(f"[{total_iterations}] Pindah. Skor Baru: {current_score}")
    if total_iterations >= max_iterations and status != "Local Optima":
        status = "Max Iteration Reached"
    return SearchResult(current_vehicles, current_score, total_iterations, history_score, status=status)