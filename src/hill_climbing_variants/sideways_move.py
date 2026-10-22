import copy, random
from utils import objective_function
from .common import SearchResult, get_random_neighbor

def sideways_move_hill_climbing(initial_vehicles, ship, max_iterations=3000, max_sideways_move=100, num_candidates=10, verbose=False):
    current_vehicles = copy.deepcopy(initial_vehicles)
    current_score = objective_function(current_vehicles, ship)
    history_score = [current_score]
    total_iterations, sideways_count, total_sideways_executed = 0, 0, 0
    status = "Local Optima"

    if verbose: print(f"[0] State Awal. Skor: {current_score}")

    while total_iterations < max_iterations:
        total_iterations += 1
        eligible_neighbors = []
        for _ in range(num_candidates):
            candidate = get_random_neighbor(current_vehicles, ship)
            candidate_score = objective_function(candidate, ship)
            if candidate_score >= current_score:
                eligible_neighbors.append((candidate, candidate_score))
        if not eligible_neighbors:
            status = "Local Optima"
            break
        max_score = max(item[1] for item in eligible_neighbors)
        best_candidates = [item for item in eligible_neighbors if item[1] == max_score]
        selected_neighbor, selected_score = random.choice(best_candidates)
        if selected_score > current_score:
            sideways_count = 0
            current_vehicles = copy.deepcopy(selected_neighbor)
            current_score = selected_score
            if verbose: print(f"[{total_iterations}] Naik Skor. Skor Baru: {current_score}")
        else:
            sideways_count += 1
            total_sideways_executed += 1
            
            if sideways_count >= max_sideways_move:
                status = "Max Sideways Reached"
                break
            
            current_vehicles = copy.deepcopy(selected_neighbor)
            current_score = selected_score
            if verbose: print(f"[{total_iterations}] Pindah Samping (Sideways). Skor: {current_score}")
        
        history_score.append(current_score)
    
    if total_iterations >= max_iterations and status == "Local Optima":
        status = "Max Iteration Reached"
        
    return SearchResult(current_vehicles, current_score, total_iterations, history_score, status=status, sideways_moves=total_sideways_executed)