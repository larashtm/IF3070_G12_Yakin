class Vehicle:
    def __init__(self, id: str, width: int, length: int, orientation: str, shippingFee: int, weight: int, eta: int):
        self.id = id
        self.width = width
        self.length = length
        self.orientation = orientation
        self.shippingfee = shippingFee
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

def calculate_shipping_fee():
    pass

def not_overlapping():
    #if vehicle1 and vehicle2 are overlapping, return False
    pass

def exceed_ship_limit():
    #if the total weight of all vehicles exceed the ship's border/area, return True
    pass

def exceed_capacity_limit():
    #if the total weight of all vehicles exceed the ship's capacity, return True
    pass