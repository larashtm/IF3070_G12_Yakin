import copy
import os
import random
import sys

# Tambahkan src ke sys.path jika belum ada
_src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

import utils
from utils import (
    Dimension,
    Ship,
    Vehicle,
    exceed_capacity_limit,
    exceed_ship_limit,
    move,
    not_overlapping,
    objective_function,
    rotate,
    swap,
)


class SearchResult(tuple):
    """Hasil pencarian Hill Climbing yang kompatibel dengan unpacking 4 tuple (best_v, best_s, iters, hist)."""

    def __new__(
        cls,
        best_vehicles,
        best_score,
        total_iterations,
        history_score,
        status="Local Optima",
        sideways_moves=0,
    ):
        return super().__new__(
            cls, (best_vehicles, best_score, total_iterations, history_score)
        )

    def __init__(
        self,
        best_vehicles,
        best_score,
        total_iterations,
        history_score,
        status="Local Optima",
        sideways_moves=0,
    ):
        self.best_vehicles = best_vehicles
        self.best_score = best_score
        self.total_iterations = total_iterations
        self.history_score = history_score
        self.status = status
        self.sideways_moves = sideways_moves


class RandomRestartResult(tuple):
    """Hasil Random Restart HC yang kompatibel dengan unpacking 4 tuple (best_v, best_s, total_r, iters_per_r)."""

    def __new__(
        cls,
        best_vehicles,
        best_score,
        total_restarts,
        iterations_per_restart,
        history_score=None,
        initial_score=None,
        status="Max Restart Reached",
        initial_state=None,
    ):
        return super().__new__(
            cls, (best_vehicles, best_score, total_restarts, iterations_per_restart)
        )

    def __init__(
        self,
        best_vehicles,
        best_score,
        total_restarts,
        iterations_per_restart,
        history_score=None,
        initial_score=None,
        status="Max Restart Reached",
        initial_state=None,
    ):
        self.best_vehicles = best_vehicles
        self.best_score = best_score
        self.total_restarts = total_restarts
        self.iterations_per_restart = iterations_per_restart
        self.history_score = history_score if history_score is not None else [best_score]
        self.initial_score = initial_score
        self.status = status
        self.initial_state = initial_state


def get_random_neighbor(vehicles, ship):
    """Membangkitkan 1 tetangga acak dari state sekarang menggunakan operator move, swap, rotate, atau toggle_load."""
    neighbor = copy.deepcopy(vehicles)
    move_type = random.choice(["move", "swap", "rotate", "toggle_load"])

    if move_type == "move":
        move(neighbor, ship)
        return neighbor

    if move_type == "swap":
        try:
            swap(neighbor, ship)
        except TypeError:
            swap(neighbor)
        return neighbor

    if move_type == "rotate":
        rotate(neighbor, ship)
        return neighbor

    if move_type == "toggle_load":
        v = random.choice(neighbor)
        v.is_loaded = not v.is_loaded
        if v.is_loaded:
            max_x = ship.dimension.width - v.dimension.width
            max_y = ship.dimension.length - v.dimension.length
            if max_x < 0 or max_y < 0:
                v.is_loaded = False
            else:
                v.x = random.randint(0, max_x)
                v.y = random.randint(0, max_y)
        return neighbor

    return neighbor


def get_all_neighbors(vehicles, ship):
    """Membangkitkan seluruh tetangga (move, swap, rotate, toggle_load) untuk steepest ascent."""
    neighbors = []

    # 1. move: coba pindahkan mobil ke semua koordinat yang muat di dek
    for i, v in enumerate(vehicles):
        if not v.is_loaded:
            continue
        max_x = max(0, ship.dimension.width - v.dimension.width)
        max_y = max(0, ship.dimension.length - v.dimension.length)
        for nx in range(max_x + 1):
            for ny in range(max_y + 1):
                if nx != v.x or ny != v.y:
                    n = copy.deepcopy(vehicles)
                    n[i].x = nx
                    n[i].y = ny
                    neighbors.append(n)

    # 2. swap: tukar koordinat antar pasangan mobil yang ada di dek
    loaded_idx = [idx for idx, v in enumerate(vehicles) if v.is_loaded]
    for i in range(len(loaded_idx)):
        for j in range(i + 1, len(loaded_idx)):
            idx_a = loaded_idx[i]
            idx_b = loaded_idx[j]
            n = copy.deepcopy(vehicles)
            n[idx_a].x, n[idx_b].x = n[idx_b].x, n[idx_a].x
            n[idx_a].y, n[idx_b].y = n[idx_b].y, n[idx_a].y
            neighbors.append(n)

    # 3. rotate: putar orientasi mobil yang dimuat
    for i, v in enumerate(vehicles):
        if not v.is_loaded:
            continue
        n = copy.deepcopy(vehicles)
        veh = n[i]
        if veh.orientation == "Horizontal":
            veh.orientation = "Vertical"
        else:
            veh.orientation = "Horizontal"
        veh.dimension.width, veh.dimension.length = veh.dimension.length, veh.dimension.width
        # sesuaikan posisi bila keluar batas
        veh.x = min(veh.x, max(0, ship.dimension.width - veh.dimension.width))
        veh.y = min(veh.y, max(0, ship.dimension.length - veh.dimension.length))
        neighbors.append(n)

    # 4. toggle: muat atau turunkan mobil
    for i, v in enumerate(vehicles):
        if not v.is_loaded:
            max_x = max(0, ship.dimension.width - v.dimension.width)
            max_y = max(0, ship.dimension.length - v.dimension.length)
            for nx in range(max_x + 1):
                for ny in range(max_y + 1):
                    n = copy.deepcopy(vehicles)
                    n[i].is_loaded = True
                    n[i].x = nx
                    n[i].y = ny
                    neighbors.append(n)
        else:
            n = copy.deepcopy(vehicles)
            n[i].is_loaded = False
            neighbors.append(n)

    return neighbors


def bikin_state_acak(vehicles_template, ship):
    """Membangkitkan state awal yang acak bervariasi per run dengan orientasi dan posisi valid."""
    state = copy.deepcopy(vehicles_template)
    for v in state:
        v.orientation = random.choice(["Horizontal", "Vertical"])
        if v.orientation == "Vertical" and v.dimension.width > v.dimension.length:
            v.dimension.width, v.dimension.length = v.dimension.length, v.dimension.width
        elif v.orientation == "Horizontal" and v.dimension.length > v.dimension.width:
            v.dimension.width, v.dimension.length = v.dimension.length, v.dimension.width

        v.is_loaded = random.choice([True, False])
        max_x = max(0, ship.dimension.width - v.dimension.width)
        max_y = max(0, ship.dimension.length - v.dimension.length)

        if v.is_loaded:
            placed = False
            for _ in range(200):
                v.x = random.randint(0, max_x)
                v.y = random.randint(0, max_y)
                if not_overlapping(state, ship) and not exceed_ship_limit([v], ship) and not exceed_capacity_limit(state, ship):
                    placed = True
                    break
            if not placed:
                v.is_loaded = False
        else:
            v.x = random.randint(0, max_x)
            v.y = random.randint(0, max_y)
    return state


def bikin_kendaraan_awal(json_path=None):
    """Memuat template kendaraan dari file vehicles.json dengan fallback yang bersih."""
    if json_path is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        for p in [os.path.join(base_dir, "vehicles.json"), "vehicles.json", "src/vehicles.json"]:
            if os.path.exists(p):
                json_path = os.path.abspath(p)
                break

    if json_path and os.path.exists(json_path):
        try:
            veh_list, _ = utils.load_json(json_path)
            if veh_list:
                return veh_list
        except Exception:
            pass

    # Fallback jika file tidak ditemukan
    return [
        Vehicle("V1", 2, 4, "Horizontal", 150, 200, 1),
        Vehicle("V2", 2, 4, "Horizontal", 200, 300, 2),
        Vehicle("V3", 3, 3, "Vertical", 80, 100, 3),
    ]
