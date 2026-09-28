class Vehicle:
    def __init__(self, id: str, width: int, length: int, orientation: str, shippingFee: int, weight: int, eta: int):
        self.id = id
        self.dimension = Dimension(width,length)
        self.orientation = orientation
        self.shippingFee = shippingFee
        self.weight = weight
        self.eta = eta
        self.is_loaded = False 

        self.x = 0 
        self.y = 0

    def rotate(self):
        #Ubah orientation dan tukar ukuran dimensi 
        if self.orientation == 'Horizontal': 
            self.orientation = 'Vertical'
        else:
            self.orientation = 'Horizontal'

        self.dimension.width, self.dimension.length = self.dimension.length, self.dimension.width; 


class Ship:
    def __init__(self, width: int, length: int, maxCapacity: int):
        self.dimension = Dimension(width,length)
        self.maxCapacity = maxCapacity

class Dimension:
    def __init__(self, width: int, length: int):
        self.width = width
        self.length = length

def shipping_fee(vehicles: list[Vehicle]) -> int:
    return sum(vehicle.shippingFee for vehicle in vehicles)

def not_overlapping(vehicles: list[Vehicle], ship: Ship) -> bool:
    #kumpulin semua mobil di kapalnya 
    mobil_di_kapal = []
    for mobil in vehicles: 
        if mobil.is_loaded: 
            mobil_di_kapal.append(mobil)

    #bandingin setiap mobil satu dengan lain 
    jumlah_mobil = len(mobil_di_kapal)
    for i in range(jumlah_mobil): 
        mobil_a = mobil_di_kapal[i]

        for j in range (i+1,jumlah_mobil): 
            mobil_b = mobil_di_kapal[j]
            #ngitung batas fisik 
            a_kanan = mobil_a.x + mobil_a.dimension.width
            a_bawah = mobil_a.y + mobil_a.dimension.length 

            b_kanan = mobil_b.x + mobil_b.dimension.width 
            b_bawah = mobil_b.y + mobil_b.dimension.length 

            #cek apakah posisinya aman di sumbu mendatar (X) atau menurun (Y)
            aman_di_sumbu_x = (a_kanan <= mobil_b.x) or (mobil_a.x >= b_kanan)
            aman_di_sumbu_y = (a_bawah <= mobil_b.y) or (mobil_a.y >= b_bawah)

            if not (aman_di_sumbu_x or aman_di_sumbu_y): 
                return False 

    return True



def exceed_ship_limit(vehicles: list[Vehicles], ship:Ship) -> bool:
    for mobil in vehicles: 
        if not mobil.is_loaded: 
            continue #ngelewat mobil yang gak di kapal 

        kiri = mobil.x 
        atas = mobil.y 
        kanan = mobil.x + mobil.dimension.width 
        bawah = mobil.y + mobil.dimension.length

        if kiri < 0 or atas < 0 or kanan > ship.dimension.width or bawah > ship.dimension.length: 
            return True 

    return False #Artinya aman, semua di dalam garis 
    

def exceed_capacity_limit(vehicles: list[Vehicle], ship: Ship) -> bool:
    total_weight = sum(v.weight for v in vehicles)
    if total_weight > ship.maxCapacity:
        return True
    return False

def swapping_neighbor(): 
    pass

def moving_neighbor(): 
    pass

def rotating_neighbor(): 
    pass
