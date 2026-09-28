class Vehicle:
    def __init__(self, id: str, width: int, length: int, orientation: str, shippingFee: int, weight: int, eta: int):
        self.id = id
        self.width = width
        self.length = length
        self.orientation = orientation
        self.shippingFee = shippingFee
        self.weight = weight
        self.eta = eta

class Ship:
    def __init__(self, width: int, length: int, maxCapacity: int):
        self.width = width
        self.length = length
        self.maxCapacity = maxCapacity

class Dimension:
    def __init__(self, width: int, length: int):
        self.width = width
        self.length = length

def shipping_fee(vehicles: list[Vehicle]) -> int:
    return sum(vehicle.shippingFee for vehicle in vehicles)


def not_overlapping():
    #if vehicle1 and vehicle2 are overlapping, return False
    pass

def exceed_ship_limit():
    #if the total weight of all vehicles exceed the ship's border/area, return True
    pass

def exceed_capacity_limit(vehicles: list[Vehicle], ship: Ship) -> bool:
    total_weight = sum(v.weight for v in vehicles)
    if total_weight > ship.maxCapacity:
        return True
    return False