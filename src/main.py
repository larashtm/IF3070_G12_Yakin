class Vehicle:
    def __init__(self, id, width, length, orientation, shippingFee, weight, eta):
        self.id = id
        self.width = width
        self.length = length
        self.orientation = orientation
        self.shippingfee = shippingFee
        self.weight = weight
        self.eta = eta

class Ship:
    def __init__(self, width, length, maxCapacity):
        self.width = width
        self.length = length
        self.maxCapacity = maxCapacity

class Dimension:
    def __init__(self, width, length):
        self.width = width
        self.length = length

def calculate_shipping_fee():
    pass

def not_overlapping():
    pass

def exceed_ship_limit():
    pass

def exceed_capacity_limit():
    pass