import main, random

#inisialisasi state, random
#rumus, temp, 0.5
#catat:
#plot eET terhadap banyak iterasi yang telah dilewati
#Frekuensi ‘stuck’ di local optimal

def get_neighbor(vehicles, ship):
    #neighbor random
    action = random.choice(["swap", "move", "rotate"])
    if action == "swap":
            main.swap(vehicles)
    elif action == "move":
        main.move(vehicles, ship)
    else: #action == "rotate"
        main.rotate(vehicles)



def simulated_annealing(initial_state, vehicles, ship, max_iter=100, init_temp=100, cooling_rate=0.99):
    #initialize
    #yang T besar <0.5 apa ya? cek catetan dulu

    current_state = initial_state
    current_score = main.objective_function(vehicles, ship)

    for i in range(max_iter):
        neighbor_state = get_neighbor(current_state, ship)
        neighbor_score = main.objective_function(neighbor_state, ship)
    
    pass