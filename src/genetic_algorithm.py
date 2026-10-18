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
        state = create_individual(vehicles, ship)
        population.append(state)

        initial_population - copy.deepcopy(population)

        #hitung skor tiap individu
        scores = []

        for state in population: 
            score = utils.objective_function(state,ship)
            score.append(score)

        #cari indeks individy dengan skor tinggi 
        best_index = scores.index(max(scores))

        #simpan individu terbaik beserta stoknya 
        best_state = copy.deepcopy(population[best_index])
        best_score = scores[best_index]

        #simpan statistik populasi awal untuk grafik 
        max_history = [max(scores)]
        mean_history = [sum(scores) / len(scores)]




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
        max_y = ship.dimension.length-vehicle.dimension.length

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


        #aktifin sementara agar ikut diperiksa oleh utils
        vehicle.is_loaded = True 
        position_is_valid = (not utils.exceed_ship_limit(state,ship) and utils.not_overlapping(state,ship))

        #jika tidak valid, cari posisi lain
        if not position_is_valid: 
            positions=[]

            for x in range (max_x + 1): 
                for y in range (max_y+1): 
                    positions.append((x,y))

            random.shuffle(positions)

            for x, y in positions: 
                vehicle.x = x 
                vehicle.y = y 

                position_is_valid = (
                    not utils.exceed_ship_limit(state,ship)
                    and utils.not_overlapping(state,ship)
                )

                if position_is_valid: 
                    break

        if position_is_valid: 
            total_weight+=vehicle.weight
        else: 
            vehicle.is_loaded = False

    return state


def select_parents(population, scores): #memilih dua individu yang akan menghasilkan anak melalui crossover
    parents=[]

    #lakukan dua turnamen untuk pilih dua parent 
    for i in range (2): 
        #ambil maks 3 individual secara acak 
        tournament_size = min(3,len(population))

        candidate_indices = random.sample(range(len(population)),tournament_size)

        pemenang_index = candidate_indices[0] #sementara
        for index in candidate_indices: 
            if scores[index] > scores[pemenang_index]: 
                pemenang_index = index 

        parents.append(population[pemenang_index])

    return parents[0], parents[1]

def crossover(parent_a, parent_b): #buat satu anak dari dua parent
    child = []
    for i in range(len(parent_a)): 
        #peluang 50 persen mengambil gene dari masing-masing parent 
        if random.random() < 0.5: 
            vehicle = copy.deepcopy(parent_a[i])
        else: 
            vehicle = copy.deepcopy(parent_b[i])
        
        child.append(vehicle)
    return child




    
def mutate (state,ship,mutation_rate): 
    pass