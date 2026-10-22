import copy
import random
from utils import objective_function
from .common import SearchResult, get_random_neighbor


def stochastic_hill_climbing(
    initial_vehicles, ship, max_iterations=3000, num_candidates=10, verbose=False
):
    #Varian Stochastic: sampling acak dari kandidat tetangga dan memilih salah satu tetangga yang lebih baik secara acak
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
        # Sampling kandidat tetangga acak
        for _ in range(num_candidates):
            candidate = get_random_neighbor(current_vehicles, ship)
            candidate_score = objective_function(candidate, ship)
            if candidate_score > current_score:
                better_neighbors.append((candidate, candidate_score))
        # Berhenti saat tidak ada tetangga yang lebih baik (local optima)
        if not better_neighbors:
            status = "Local Optima"
            break
        # Pilih 1 tetangga secara acak dari kumpulan tetangga yang lebih baik
        selected_neighbor, selected_score = random.choice(better_neighbors)
        current_vehicles, current_score = copy.deepcopy(selected_neighbor), selected_score
        history_score.append(current_score)
        if verbose:
            print(f"[{total_iterations}] Pindah. Skor Baru: {current_score}")
    if total_iterations >= max_iterations and status != "Local Optima":
        status = "Max Iteration Reached"
    return SearchResult(current_vehicles, current_score, total_iterations, history_score, status=status)