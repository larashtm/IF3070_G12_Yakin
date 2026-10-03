import main, random, copy

#inisialisasi state, random
#rumus, temp, 0.5
#catat:
#plot eET terhadap banyak iterasi yang telah dilewati
#Frekuensi ‘stuck’ di local optimal

def get_neighbor(vehicles, ship):
    #neighbor random
    neighbor = copy.deepcopy(vehicles)
    action = random.choice(["swap", "move", "rotate"])
    if action == "swap":
        main.swap(get_neighbor)
    elif action == "move":
        main.move(neighbor, ship)
    else: #action == "rotate"
        main.rotate(neighbor)
    return neighbor


def simulated_annealing(initial_state, ship, max_iter=100, init_temp=100, cooling_rate=0.99):
    #initialize
    #yang T besar <0.5 apa ya? cek catetan dulu
    current_state = copy.deepcopy(initial_state)
    current_score = main.objective_function(current_state, ship)
    best_state = copy.deepcopy(current_state)
    best_score = current_score
    temperature = init_temp

    for i in range(max_iter):
        neighbor_state = get_neighbor(current_state, ship)
        neighbor_score = main.objective_function(neighbor_state, ship)

        #rumus euler delta T/t
        delta = neighbor_score - current_score

        if delta > 0:
            current_state = neighbor_state
            current_score = neighbor_score
        else: #bikin yang probabilitas. cek catetan!!
            pass
    
    pass