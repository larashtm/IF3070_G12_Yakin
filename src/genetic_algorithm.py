import copy 
import random 
import time 
import utils 

# satu state isinya seluruh kendaraan
# setiap kendaraan simpan x, y, arah, dan loaded


def genetic_algorithm(vehicles, ship, population_size = 30, max_iter = 100, mutation_rate = 0.15, seed = None):
    #pengecekan input sebelum GA jalan 
    if type(population_size) != int: 
        raise ValueError("Jumlah population harus bilangan bulat.")
    if population_size < 2: 
        raise ValueError("Jumlah populasi minimal 2.")
    if type(max_iter) != int: 
        raise ValueError("Jumlah iterasi harus bilangan bulat.")
    if max_iter < 0: 
        raise ValueError("Jumlah iterasi tidak boleh negatif.")
    if mutation_rate < 0 or mutation_rate > 1: 
        raise ValueError("Peluang mutasi harus antara 0 dan 1.")
    for vehicle in vehicles: 
        if vehicle.shippingFee < 0: 
            raise ValueError("Tarif pengiriman tidak boleh negatif.")
    used_ids = []
    for vehicle in vehicles: 
        if vehicle.id in used_ids: 
            raise ValueError("ID kendaraan tidak boleh sama.")
        used_ids.append(vehicle.id)
    if seed is not None: 
        random.seed(seed)

    #after that, kita membuat populasi awal, menghitung skor, lalu simpan susunan terbaik 
    start_time = time.perf_counter()
    population = []
    for i in range (population_size): 
        state = create_individual


def create_individual(vehicles,ship): 
    state = copy.deepcopy(vehicles) 

    for vehicle in state: 
        if random.random() < 0.5: 
            vehicle.dimension.width, vehicle.dimension.length = (vehicle.dimension.length, vehicle.dimension.width,)
            if vehicle.orientation == "Horizontal": 
                vehicle.orientation = "Vertical"
            else:
                vehicle.orientation = "Horizontal"

        max_x = ship.dimension.width-vehicle.dimension.width
        max_y = ship.dimension.lenfth-vehicle.dimension.length

        vehicle.is_loaded = False

        #acak apakah kendaraan akan dimuat
        if random.random() < 0.5: 
            if max_x >= 0 and max_y >= 0: 
                vehicle.is_loaded = True
                vehicle.x = random.randint(0,max_x) #pilih koordinat acak 
                vehicle.y = random.randint(0,max_y)

        repair_state(state,ship) #fix benturan and kapasitas
        return state 
    
def repair_state(state, ship): 
    candidates = []
    for vehicle in state: 
        if vehicle.is_loaded: 
            candidates.append(vehicle)
    #kosongin kapal sementara 
    for vehicle in state: 
        vehicle.is_loaded = False
    random.shuffle(candidates)
    total_weight = 0 

    for vehicle in candidates: 
        max_x = ship.dimension.width-vehicle.dimension.width
        max_y = ship.dimension.lenfth-vehicle.dimension.length

        #lewati kendaraan yang ukuran tidak muat
        if max_x < 0 or max_y < 0: 
            continue
        #lewati kendaraan jika kapasitas akan overloaded 
        if total_weight + vehicle.weight > ship.maxCapacity: 
            continue


def select_parents(): 
    pass 

def crossover(parent_a, parent_b): 
    pass
def mutate (state,ship,mutation_rate): 
    pass