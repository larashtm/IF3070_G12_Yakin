import copy, os, random, utils
from utils import Vehicle, exceed_capacity_limit, exceed_ship_limit, move, not_overlapping, rotate, swap

#hasilnya tuple biar bisa di-unpack, tapi atributnya tetap bisa diakses pakai nama
class SearchResult(tuple):
    def __new__(cls, best_vehicles, best_score, total_iterations, history_score, status="Local Optima", sideways_moves=0):
        self = super().__new__(cls, (best_vehicles, best_score, total_iterations, history_score))
        self.best_vehicles, self.best_score = best_vehicles, best_score
        self.total_iterations, self.history_score = total_iterations, history_score
        self.status, self.sideways_moves = status, sideways_moves
        return self

class RandomRestartResult(tuple):
    def __new__(cls, best_vehicles, best_score, total_restarts, iterations_per_restart, history_score=None, initial_score=None, status="Max Restart Reached", initial_state=None):
        self = super().__new__(cls, (best_vehicles, best_score, total_restarts, iterations_per_restart))
        self.best_vehicles, self.best_score = best_vehicles, best_score
        self.total_restarts, self.iterations_per_restart = total_restarts, iterations_per_restart
        self.history_score = history_score if history_score is not None else [best_score]
        self.initial_score, self.status, self.initial_state = initial_score, status, initial_state
        return self

def get_random_neighbor(vehicles, ship):
    neighbor = copy.deepcopy(vehicles)
    m_type = random.choice(["move", "swap", "rotate", "toggle_load"])
    if m_type == "move": move(neighbor, ship)
    elif m_type == "swap": swap(neighbor, ship)
    elif m_type == "rotate": rotate(neighbor, ship)
    else:
        v = random.choice(neighbor)
        v.is_loaded = not v.is_loaded
        if v.is_loaded:
            mx, my = ship.dimension.width - v.dimension.width, ship.dimension.length - v.dimension.length
            if mx < 0 or my < 0: v.is_loaded = False
            else: v.x, v.y = random.randint(0, mx), random.randint(0, my)
    return neighbor

def _clone_state(vehicles, indices):
    res = list(vehicles)
    for idx in indices:
        res[idx] = copy.copy(vehicles[idx])
        res[idx].dimension = copy.copy(vehicles[idx].dimension)
    return res

def get_all_neighbors(vehicles, ship):
    neighbors = []
    w, l = ship.dimension.width, ship.dimension.length
    #move
    for i, v in enumerate(vehicles):
        if not v.is_loaded: continue
        mx, my = max(0, w - v.dimension.width), max(0, l - v.dimension.length)
        for nx in range(mx + 1):
            for ny in range(my + 1):
                if nx != v.x or ny != v.y:
                    n = _clone_state(vehicles, [i])
                    n[i].x, n[i].y = nx, ny
                    neighbors.append(n)
    #swap
    loaded = [i for i, v in enumerate(vehicles) if v.is_loaded]
    for a in range(len(loaded)):
        for b in range(a + 1, len(loaded)):
            ia, ib = loaded[a], loaded[b]
            n = _clone_state(vehicles, [ia, ib])
            n[ia].x, n[ib].x = n[ib].x, n[ia].x
            n[ia].y, n[ib].y = n[ib].y, n[ia].y
            neighbors.append(n)
    #rotate
    for i, v in enumerate(vehicles):
        if not v.is_loaded: continue
        n = _clone_state(vehicles, [i])
        veh = n[i]
        veh.orientation = "Vertical" if veh.orientation == "Horizontal" else "Horizontal"
        veh.dimension.width, veh.dimension.length = veh.dimension.length, veh.dimension.width
        veh.x = min(veh.x, max(0, w - veh.dimension.width))
        veh.y = min(veh.y, max(0, l - veh.dimension.length))
        neighbors.append(n)
    #load
    for i, v in enumerate(vehicles):
        if v.is_loaded:
            n = _clone_state(vehicles, [i])
            n[i].is_loaded = False
            neighbors.append(n)
            continue
        mx, my = max(0, w - v.dimension.width), max(0, l - v.dimension.length)
        for nx in range(mx + 1):
            for ny in range(my + 1):
                n = _clone_state(vehicles, [i])
                n[i].is_loaded, n[i].x, n[i].y = True, nx, ny
                neighbors.append(n)
    return neighbors

def bikin_state_acak(template, ship):
    state = copy.deepcopy(template)
    w, l = ship.dimension.width, ship.dimension.length
    for v in state:
        v.orientation = random.choice(["Horizontal", "Vertical"])
        if (v.orientation == "Vertical") == (v.dimension.width > v.dimension.length):
            v.dimension.width, v.dimension.length = v.dimension.length, v.dimension.width
        v.is_loaded = random.choice([True, False])
        mx, my = max(0, w - v.dimension.width), max(0, l - v.dimension.length)
        if v.is_loaded:
            placed = False
            for _ in range(200):
                v.x, v.y = random.randint(0, mx), random.randint(0, my)
                if not_overlapping(state, ship) and not exceed_ship_limit([v], ship) and not exceed_capacity_limit(state, ship):
                    placed = True
                    break
            if not placed: v.is_loaded = False
        else:
            v.x, v.y = random.randint(0, mx), random.randint(0, my)
    return state

def bikin_kendaraan_awal(json_path=None):
    json_path = json_path or os.path.join(os.path.dirname(os.path.abspath(__file__)), "vehicles.json")
    try:
        v_list, _ = utils.load_json(json_path)
        if v_list: return v_list
    except Exception: pass

    #eksperimen sementara, dummy kalau file json nyasar atau gak ketemu
    return [
        Vehicle("V1", 2, 4, "Horizontal", 150, 200, 1),
        Vehicle("V2", 2, 4, "Horizontal", 200, 300, 2),
    ]