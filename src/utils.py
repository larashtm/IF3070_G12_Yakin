import random, copy, json

#class & objects
class Vehicle:
    def __init__(self, id: str, width: int, length: int, orientation: str, shippingFee: int, weight: int, eta: int):
        self.id = id
        self.dimension = Dimension(width,length)
        self.orientation = orientation
        self.shippingFee = shippingFee
        self.weight = weight
        self.eta = eta
        self.is_loaded = False #awalnya ga di kapal semua

        self.x = 0 
        self.y = 0


class Ship:
    def __init__(self, width: int, length: int, maxCapacity: int):
        self.dimension = Dimension(width,length)
        self.maxCapacity = maxCapacity


class Dimension:
    def __init__(self, width: int, length: int):
        self.width = width
        self.length = length


#json & initialize states
def load_json(path: str):
    with open(path) as file:
        data = json.load(file)
    s = data["ship"]
    ship = Ship(s["width"], s["length"], s["maxCapacity"])
    vehicles = []
    for v in data["vehicles"]:
        vehicles.append(Vehicle(v["id"], v["width"], v["length"], v["orientation"], v["shippingFee"], v["weight"], v["eta"]))
    
    return vehicles, ship


def init_state(vehicles: list[Vehicle], ship: Ship) -> list[Vehicle]:
    state = copy.deepcopy(vehicles)
    for v in state:
        v.is_loaded = random.random() < 0.5 #dirandomin dulu

        if not v.is_loaded:
            v.x = random.randint(-ship.dimension.width, ship.dimension.width)
            v.y = random.randint(-ship.dimension.length, ship.dimension.length)
            continue

        while True:
            v.x = random.randint(0, ship.dimension.width - v.dimension.width)
            v.y = random.randint(0, ship.dimension.length - v.dimension.length)
            if not_overlapping(state, ship):
                break #ulang lagi, ga boleh vehicles tumpuk nanti menyalahi constraints

    return state


#objective functions
def shipping_fee(vehicles: list[Vehicle]) -> int:
    return sum(vehicle.shippingFee for vehicle in vehicles if vehicle.is_loaded)


def not_overlapping(vehicles: list[Vehicle], ship: Ship) -> bool:
    #kumpulin semua vehicle di kapalnya 
    vehicle_in_ship = []
    for vehicle in vehicles: 
        if vehicle.is_loaded: 
            vehicle_in_ship.append(vehicle)

    #bandingin setiap vehicle satu dengan lain 
    jumlah_vehicle = len(vehicle_in_ship)
    for i in range(jumlah_vehicle): 
        vehicle_a = vehicle_in_ship[i]

        for j in range (i+1,jumlah_vehicle): 
            vehicle_b = vehicle_in_ship[j]
            #ngitung batas fisik 
            a_right = vehicle_a.x + vehicle_a.dimension.width
            a_below = vehicle_a.y + vehicle_a.dimension.length 

            b_right = vehicle_b.x + vehicle_b.dimension.width 
            b_below = vehicle_b.y + vehicle_b.dimension.length 

            #cek apakah posisinya aman di sumbu mendatar (X) atau menurun (Y)
            aman_x = (a_right <= vehicle_b.x) or (vehicle_a.x >= b_right)
            aman_y = (a_below <= vehicle_b.y) or (vehicle_a.y >= b_below)

            if not (aman_x and aman_y): 
                return False 
               
    return True


def exceed_ship_limit(vehicles: list[Vehicle], ship:Ship) -> bool:
    for vehicle in vehicles: 
        if not vehicle.is_loaded: 
            continue #ngelewat vehicle yang gak di kapal 

        left = vehicle.x 
        above = vehicle.y 
        right = vehicle.x + vehicle.dimension.width 
        below = vehicle.y + vehicle.dimension.length

        if left < 0 or above < 0 or right > ship.dimension.width or below > ship.dimension.length: 
            return True 

    return False #artinya aman, semua di dalam garis 
    

def exceed_capacity_limit(vehicles: list[Vehicle], ship: Ship) -> bool:
    total_weight = sum(v.weight for v in vehicles if v.is_loaded)
    if total_weight > ship.maxCapacity:
        return True
    else:
        return False


def objective_function(vehicles: list[Vehicle], ship: Ship) -> int: 
    if exceed_capacity_limit(vehicles,ship) == True: 
        return 0 
    if exceed_ship_limit(vehicles,ship) == True: 
        return 0 
    if not_overlapping(vehicles,ship)==False: 
        return 0
    total_uang = shipping_fee(vehicles)
    return total_uang


def swap(vehicles: list[Vehicle]):
    vehicle_a, vehicle_b = random.sample(vehicles, 2)
    vehicle_a.x, vehicle_b.x = vehicle_b.x, vehicle_a.x
    vehicle_a.y, vehicle_b.y = vehicle_b.y, vehicle_a.y


def move(vehicles: list[Vehicle], ship: Ship):
    vehicle = random.choice(vehicles)
    vehicle.x = random.randint(0, ship.dimension.width - vehicle.dimension.width)
    vehicle.y = random.randint(0, ship.dimension.length - vehicle.dimension.length)


def rotate(vehicles: list[Vehicle]):
    vehicle = random.choice(vehicles)

    if vehicle.orientation == "Horizontal":
        vehicle.orientation = "Vertical"
    else:
        vehicle.orientation = "Horizontal"

    vehicle.dimension.width, vehicle.dimension.length = vehicle.dimension.length, vehicle.dimension.width


#display ship
def display(vehicles: list[Vehicle], ship: Ship):
    map = [["." for i in range(ship.dimension.width)] for i in range(ship.dimension.length)]
    
    if exceed_ship_limit(vehicles, ship):
        return

    for v in vehicles:
        if v.is_loaded:
            for x in range(v.x, v.x + v.dimension.width):
                for y in range(v.y, v.y + v.dimension.length):
                    if 0 <= x < ship.dimension.width and 0 <= y < ship.dimension.length:
                        map[y][x] = v.id[0]  #sementara ini masih pake id, tapi kalo id string nama owen gitu tar jadi owenowen etc??

    for row in map:
        print("".join(row))


#display map dan ship, regardless of vehicles keitung is_loaded enggak (tetep ditampilin)
def display_map(vehicles: list[Vehicle], ship: Ship):
    min_x = -ship.dimension.width
    max_x = ship.dimension.width * 2
    min_y = -ship.dimension.length
    max_y = ship.dimension.length * 2

    map = [["." for _ in range(min_x, max_x + 1)] for _ in range(min_y, max_y + 1)]

    for x in range(ship.dimension.width):
        for y in range(ship.dimension.length):
            map[y - min_y][x - min_x] = "x" #biar beda aja sih, ini bebas sebenernya mau apa

    for v in vehicles:
        for x in range(v.x, v.x + v.dimension.width):
            for y in range(v.y, v.y + v.dimension.length):
                map[y - min_y][x - min_x] = v.id[0]

    for row in map:
        print("".join(row))