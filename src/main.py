import random

class Vehicle:
    def __init__(self, id: str, width: int, length: int, orientation: str, shippingFee: int, weight: int, eta: int):
        self.id = id
        self.dimension = Dimension(width, length)
        self.orientation = orientation
        self.shippingFee = shippingFee
        self.weight = weight
        self.eta = eta
        self.is_loaded = False 

        self.x = 0 
        self.y = 0


class Ship:
    def __init__(self, width: int, length: int, maxCapacity: int):
        self.dimension = Dimension(width, length)
        self.maxCapacity = maxCapacity


class Dimension:
    def __init__(self, width: int, length: int):
        self.width = width
        self.length = length


def shipping_fee(vehicles: list[Vehicle]) -> int:
    return sum(vehicle.shippingFee for vehicle in vehicles if vehicle.is_loaded)


def not_overlapping(vehicles: list[Vehicle], ship: Ship) -> bool:
    # kumpulin semua vehicle di kapalnya 
    vehicle_in_ship = []
    for vehicle in vehicles: 
        if vehicle.is_loaded: 
            vehicle_in_ship.append(vehicle)

    # bandingin setiap vehicle satu dengan lain 
    jumlah_vehicle = len(vehicle_in_ship)
    for i in range(jumlah_vehicle): 
        vehicle_a = vehicle_in_ship[i]

        for j in range(i + 1, jumlah_vehicle): 
            vehicle_b = vehicle_in_ship[j]
            # ngitung batas fisik 
            a_right = vehicle_a.x + vehicle_a.dimension.width
            a_below = vehicle_a.y + vehicle_a.dimension.length 

            b_right = vehicle_b.x + vehicle_b.dimension.width 
            b_below = vehicle_b.y + vehicle_b.dimension.length 

            # cek apakah posisinya aman di sumbu mendatar (X) atau menurun (Y)
            aman_x = (a_right <= vehicle_b.x) or (vehicle_a.x >= b_right)
            aman_y = (a_below <= vehicle_b.y) or (vehicle_a.y >= b_below)

            # jika tidak aman di X maupun di Y, berarti overlap
            if not (aman_x or aman_y): 
                return False 
                
    return True


def exceed_ship_limit(vehicles: list[Vehicle], ship: Ship) -> bool:
    for vehicle in vehicles: 
        if not vehicle.is_loaded: 
            continue # ngelewat vehicle yang gak di kapal 

        left = vehicle.x 
        above = vehicle.y 
        right = vehicle.x + vehicle.dimension.width 
        below = vehicle.y + vehicle.dimension.length

        if left < 0 or above < 0 or right > ship.dimension.width or below > ship.dimension.length: 
            return True 

    return False # artinya aman, semua di dalam garis 
    

def exceed_capacity_limit(vehicles: list[Vehicle], ship: Ship) -> bool:
    total_weight = sum(v.weight for v in vehicles if v.is_loaded)
    if total_weight > ship.maxCapacity:
        return True
    else:
        return False


def objective_function(vehicles: list[Vehicle], ship: Ship) -> int: 
    if exceed_capacity_limit(vehicles, ship): 
        return 0 
    if exceed_ship_limit(vehicles, ship): 
        return 0 
    if not not_overlapping(vehicles, ship): 
        return 0
    total_uang = shipping_fee(vehicles)
    return total_uang


def swap(vehicles: list[Vehicle]):
    loaded_vehicles = [v for v in vehicles if v.is_loaded]
    target_list = loaded_vehicles if len(loaded_vehicles) >= 2 else vehicles
    if len(target_list) >= 2:
        vehicle_a, vehicle_b = random.sample(target_list, 2)
        vehicle_a.x, vehicle_b.x = vehicle_b.x, vehicle_a.x
        vehicle_a.y, vehicle_b.y = vehicle_b.y, vehicle_a.y


def move(vehicles: list[Vehicle], ship: Ship):
    vehicle = random.choice(vehicles)
    max_x = max(0, ship.dimension.width - vehicle.dimension.width)
    max_y = max(0, ship.dimension.length - vehicle.dimension.length)
    vehicle.x = random.randint(0, max_x)
    vehicle.y = random.randint(0, max_y)


def rotate(vehicles: list[Vehicle], ship: Ship = None):
    vehicle = random.choice(vehicles)

    if vehicle.orientation == "Horizontal":
        vehicle.orientation = "Vertical"
    else:
        vehicle.orientation = "Horizontal"

    vehicle.dimension.width, vehicle.dimension.length = vehicle.dimension.length, vehicle.dimension.width

    if ship is not None and vehicle.is_loaded:
        if vehicle.x + vehicle.dimension.width > ship.dimension.width:
            vehicle.x = max(0, ship.dimension.width - vehicle.dimension.width)
        if vehicle.y + vehicle.dimension.length > ship.dimension.length:
            vehicle.y = max(0, ship.dimension.length - vehicle.dimension.length)


def display(vehicles: list[Vehicle], ship: Ship):
    grid = [["." for _ in range(ship.dimension.width)]
            for _ in range(ship.dimension.length)]

    for v in vehicles:
        if v.is_loaded:
            for x in range(v.x, v.x + v.dimension.width):
                for y in range(v.y, v.y + v.dimension.length):
                    if 0 <= x < ship.dimension.width and 0 <= y < ship.dimension.length:
                        grid[y][x] = v.id[0]

    for row in grid:
        print("".join(row))