import copy
from .common import RandomRestartResult, bikin_kendaraan_awal, bikin_state_acak
from .stochastic import stochastic_hill_climbing


def random_restart_hill_climbing(
    ship,
    max_restart=10,
    max_restarts=None,
    max_iterations_per_restart=1000,
    initial_vehicles=None,
    num_candidates=10,
    verbose=False,
):
    limit_restarts = max_restarts if max_restarts is not None else max_restart
    if isinstance(ship, list) and hasattr(limit_restarts, "maxCapacity"):
        initial_vehicles, ship, limit_restarts = ship, limit_restarts, max_iterations_per_restart
    has_custom_initial = initial_vehicles is not None
    if initial_vehicles is None:
        initial_vehicles = bikin_kendaraan_awal()
    global_best_vehicles = None
    global_best_score = -1
    iterations_per_restart = []
    cumulative_history = []
    initial_score = None
    first_initial_state = None
    for restart_idx in range(1, limit_restarts + 1):
        if restart_idx == 1 and has_custom_initial:
            start_state = copy.deepcopy(initial_vehicles)
        else:
            start_state = bikin_state_acak(initial_vehicles, ship)
        if first_initial_state is None:
            first_initial_state = copy.deepcopy(start_state)
        best_v, best_s, iters, hist = stochastic_hill_climbing(
            start_state, ship,
            max_iterations=max_iterations_per_restart,
            num_candidates=num_candidates,
            verbose=False,
        )
        if initial_score is None and hist:
            initial_score = hist[0]
        iterations_per_restart.append(iters)
        if best_s > global_best_score or global_best_vehicles is None:
            global_best_vehicles = copy.deepcopy(best_v)
            global_best_score = best_s
        for s in hist:
            if s > global_best_score or global_best_score == -1:
                global_best_score = s
            cumulative_history.append(global_best_score)
        if verbose:
            print(f"[{restart_idx}] Restart. Skor Baru: {global_best_score}")
    return RandomRestartResult(
        global_best_vehicles,
        global_best_score,
        len(iterations_per_restart),
        iterations_per_restart,
        cumulative_history,
        initial_score,
        status="Max Restart Reached",
        initial_state=first_initial_state,
    )