import copy, random
from utils import objective_function
from hill_climbing import SearchResult, get_random_neighbor

def stochastic_hill_climbing(initial_vehicles, ship, max_iterations=3000, num_candidates=10, tampil=False):
    #Varian Stochastic: sampling acak dari kandidat tetangga dan memilih salah satu tetangga yang lebih baik secara acak
    current_vehicles = copy.deepcopy(initial_vehicles)
    current_score = objective_function(current_vehicles, ship)
    history_score = [current_score]
    total_iterations = 0
    status = "Local Optima"
    if tampil: print(f"[0] State Awal. Skor: {current_score}")
    while total_iterations < max_iterations:
        total_iterations += 1
        # Sampling kandidat tetangga acak
        candidates = [get_random_neighbor(current_vehicles, ship) for _ in range(num_candidates)]
        better = [(c, s) for c in candidates if (s := objective_function(c, ship)) > current_score]
        # Berhenti saat tidak ada tetangga yang lebih baik (local optima)
        if not better: break
        # Pilih 1 tetangga secara acak dari kumpulan tetangga yang lebih baik
        selected, current_score = random.choice(better)
        current_vehicles = copy.deepcopy(selected)
        history_score.append(current_score)
        if tampil: print(f"[{total_iterations}] Pindah. Skor Baru: {current_score}")
    if total_iterations >= max_iterations and status == "Local Optima":
        status = "Max Iteration Reached"
    return SearchResult(current_vehicles, current_score, total_iterations, history_score, status=status)