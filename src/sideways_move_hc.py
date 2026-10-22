import copy, random
from utils import objective_function
from hill_climbing import SearchResult, get_random_neighbor

def sideways_move_hill_climbing(initial_vehicles, ship, max_iterations=3000, max_sideways_move=100, num_candidates=10, tampil=False):
    current_vehicles = copy.deepcopy(initial_vehicles)
    current_score = objective_function(current_vehicles, ship)
    history_score = [current_score]
    total_iterations, sideways_count, total_sideways = 0, 0, 0
    status = "Local Optima"

    if tampil: print(f"[0] State Awal. Skor: {current_score}")
    while total_iterations < max_iterations:
        total_iterations += 1
        candidates = [get_random_neighbor(current_vehicles, ship) for _ in range(num_candidates)]
        # skor yang sama juga boleh (sideways)
        eligible = [(c, s) for c in candidates if (s := objective_function(c, ship)) >= current_score]
        if not eligible: break
        top = max(s for _, s in eligible)
        selected, selected_score = random.choice([e for e in eligible if e[1] == top])
        if selected_score > current_score:
            sideways_count = 0
            if tampil: print(f"[{total_iterations}] Naik Skor. Skor Baru: {selected_score}")
        else:
            sideways_count += 1
            total_sideways += 1
            if sideways_count >= max_sideways_move:
                status = "Max Sideways Reached"
                break
            if tampil: print(f"[{total_iterations}] Pindah Samping (Sideways). Skor: {selected_score}")
        current_vehicles, current_score = copy.deepcopy(selected), selected_score
        history_score.append(current_score)

    if total_iterations >= max_iterations and status == "Local Optima":
        status = "Max Iteration Reached"
    return SearchResult(current_vehicles, current_score, total_iterations, history_score, status=status, sideways_moves=total_sideways)