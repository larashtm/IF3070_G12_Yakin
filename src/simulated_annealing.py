import utils, random, copy, math, time

#inisialisasi state, random
#catat:
#plot eET terhadap banyak iterasi yang telah dilewati
#Frekuensi ‘stuck’ di local optimal

def get_neighbor(vehicles, ship):
    #neighbor random
    neighbor = copy.deepcopy(vehicles)
    action = random.choice(["swap", "move", "rotate"])
    if action == "swap":
        utils.swap(neighbor, ship)
    elif action == "move":
        utils.move(neighbor, ship)
    else: #action == "rotate"
        utils.rotate(neighbor, ship)
    return neighbor


def simulated_annealing(initial_state, ship, max_iter=1000, init_temp=30, cooling_rate=0.99, stuck_threshold=10, objective=utils.objective_function):  #awalnya kan pake 100, tapi ganti 1000 biar keliatan pola pendinginan
    #initialize
    start_time = time.perf_counter()
    #yang T besar <0.5 apa ya? cek catetan dulu
    current_state = copy.deepcopy(initial_state)
    current_score = objective(current_state, ship)
    best_state = copy.deepcopy(current_state)
    best_score = current_score
    temperature = init_temp

    objective_function_value = [current_score]
    acceptance_probabilities = []  #e^(deltaE/T) tiap iterasi, buat plotting
    stuck_count = 0
    no_improvement = 0

    #utils.display(current_state, ship) #buat crosscheck

    for i in range(max_iter):
        neighbor_state = get_neighbor(current_state, ship)
        neighbor_score = objective(neighbor_state, ship)

        #rumus euler delta T/t
        delta = neighbor_score - current_score
        #ini kalo neighbor lebih baik langsung acc
        if delta > 0:
            current_state = neighbor_state
            current_score = neighbor_score
            acceptance_probabilities.append(1.0)

        else: #bikin yang probabilitas. cek catetan!!
            probability = random.random()
            acceptance_prob = math.exp(delta / temperature)
            acceptance_probabilities.append(acceptance_prob)
            if probability < acceptance_prob:
                current_state = neighbor_state
                current_score = neighbor_score

        if current_score > best_score:
            best_state = copy.deepcopy(current_state)
            best_score = current_score

        objective_function_value.append(current_score)

        # kalo biasa best_score, tapi diganti jadi stuck dihitung dari current_score yang ga berubah selama threshold iterasi, dan ga dihitung berulang kalau skornya masih sama
        if current_score == objective_function_value[-2]:
            no_improvement += 1
        else:
            no_improvement = 0

        if no_improvement == stuck_threshold:
            stuck_count += 1

        temperature = temperature * cooling_rate
        #utils.display(current_state, ship) #buat cross check


    duration = time.perf_counter() - start_time

    return best_state, best_score, objective_function_value, stuck_count, duration, acceptance_probabilities