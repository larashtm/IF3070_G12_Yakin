import copy, random
from utils import objective_function
from hill_climbing import SearchResult, get_all_neighbors, get_random_neighbor

def steepest_ascent_hill_climbing(initial_vehicles, ship, max_iterations=3000, num_candidates=None, tampil=False):
    # Varian Steepest Ascent: Evaluasi tetangga dan pindah ke skor tertinggi
    current_vehicles = copy.deepcopy(initial_vehicles)
    current_score = objective_function(current_vehicles, ship)
    history_score = [current_score]
    total_iterations = 0
    status = "Local Optima"

    if tampil: print(f"[0] State Awal. Skor: {current_score}")
    while total_iterations < max_iterations:
        total_iterations += 1
        if num_candidates is None or num_candidates == "all":
            candidates = get_all_neighbors(current_vehicles, ship)
        else:
            candidates = [get_random_neighbor(current_vehicles, ship) for _ in range(num_candidates)]
        better = [(c, s) for c in candidates if (s := objective_function(c, ship)) > current_score]
        if not better: break
        top = max(s for _, s in better)
        current_vehicles = copy.deepcopy(random.choice([c for c, s in better if s == top]))
        current_score = top
        history_score.append(current_score)
        if tampil: print(f"[{total_iterations}] Pindah. Skor Baru: {current_score}")
    if total_iterations >= max_iterations and status == "Local Optima":
        status = "Max Iteration Reached"
    return SearchResult(current_vehicles, current_score, total_iterations, history_score, status=status)