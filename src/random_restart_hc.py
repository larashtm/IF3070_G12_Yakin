import copy
from hill_climbing import RandomRestartResult, bikin_kendaraan_awal, bikin_state_acak
from stochastic_hc import stochastic_hill_climbing

def random_restart_hill_climbing(ship, max_restart=10, max_iterations_per_restart=1000, initial_vehicles=None, num_candidates=10, tampil=False):
    # tiap restart pakai stochastic, restart pertama pakai initial_vehicles kalau dikasih
    custom_initial = initial_vehicles is not None
    if initial_vehicles is None:
        initial_vehicles = bikin_kendaraan_awal()
    best_vehicles, best_score = None, -1
    iterations_per_restart, history = [], []
    initial_score, first_state = None, None
    for i in range(1, max_restart + 1):
        start = copy.deepcopy(initial_vehicles) if i == 1 and custom_initial else bikin_state_acak(initial_vehicles, ship)
        if first_state is None: first_state = copy.deepcopy(start)
        best_v, best_s, iters, hist = stochastic_hill_climbing(start, ship, max_iterations=max_iterations_per_restart, num_candidates=num_candidates)
        if initial_score is None and hist: initial_score = hist[0]
        iterations_per_restart.append(iters)
        if best_s > best_score or best_vehicles is None:
            best_vehicles = copy.deepcopy(best_v)
        for s in hist: # history = skor terbaik sampai titik itu
            best_score = max(best_score, s)
            history.append(best_score)
        if tampil: print(f"[{i}] Restart. Skor Baru: {best_score}")
    return RandomRestartResult(best_vehicles, best_score, len(iterations_per_restart), iterations_per_restart, history, initial_score, status="Max Restart Reached", initial_state=first_state)