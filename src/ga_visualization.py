import os 

import matplotlib.pyplot as plt 
from matplotlib.patches import Rectangle

import utils 

#memberi id kendaraan satu warna tetap, supaya warna sama di initial & final 
def build_color_map(vehicles): 
    colors={}
    palette = list(plt.get_cmap("tab20").colors) + list(plt.get_cmap("tab20b").colors) #40 warna
    for i, vehicle in enumerate(vehicles): 
        index_warna = i % len(palette)
        colors[vehicle.id] = palette[index_warna]

    return colors 

#gambar satu kendaraan sebagai persegi panjang berlabel ID (dan fee kalau cukupp besar)
def draw_vehicles(ax,v,x,y,color,outside=False): 
    w, l = v.dimension.width, v.dimension.length 

    #kendaraan di luar dibuat pucat + diarsir supaya beda dengan yang diangkut 
    ax.add_patch(Rectangle((x,y),w,l,facecolor=color, edgecolor="black",
    alpha=0.5 if outside else 0.95, hatch="//" if outside else None))

    #tambahkan tarif kalau kotaknya cukup besar 
    label = str(v.id)
    if w >= 2 and l >= 2: 
        label += f"\n{v.shippingFee}"

    #putar tulisan kalau kotaknya sempit dan memanjang 
    rotation = 0 
    if w ==1 and l >= 2: 
        rotation=90 
    ax.text(
        x+w/2, y+l/2, label,
        ha="center", va="center", 
        fontsize=8, rotation=rotation, fontweight="bold", 
    )

#susun kendaraan di luar kapal baris demi baris (kiri ke kanan), kalau satu beris penuh, lanjut ke baris dibawahnya
def layout_outside(outside_vehicles, row_width): 
    positions = {}
    x,y,row_height = 0,0,0 
    for v in outside_vehicles: 
        w,l = v.dimension.width, v.dimension.length 
        if x + w > row_width: 
            x=0
            y+=row_height+1 
            row_height=0
        positions[v.id]=(x,y)
        x+=w+1 
        row_height=max(row_height,l)

    return positions, y+row_height


def draw_state(ax,vehicles,ship,colors,title): 
    W,L = ship.dimension.width, ship.dimension.length
    inside = [v for v in vehicles if v.is_loaded]
    outside = [v for v in vehicles if not v.is_loaded]

    #gambar geladak kapal 
    kapal = Rectangle((0,0),W,L,facecolor="#eef3f8",edgecolor="black",linewidth=2.5,)
    ax.add_patch(kapal)
    #garis vertikal pada geladak 
    for x in range(1,W): 
        ax.plot([x,x],[0,L],color="#c5ced8",linewidth=0.6,)
    #garis horizontal pada geladak 
    for y in range(1,L): 
        ax.plot([0,W],[y,y],color="#c5ced8",linewidth=0.6,)

    ax.text(W/2,-0.7,"GELADAK KAPAL",ha="center",fontsize=9,fontweight="bold",)

    #kendaraan di kapal memakai koordinat asli 
    for v in inside: 
        draw_vehicles(ax,v,v.x,v.y,colors[v.id])

    #area luar dimulai 2 satuan di sebelah kanan kapal 
    outside_x = W + 2 
    row_width = W 

    #pastiin kendaraan terlebar muat dalam baris 
    for v in outside: 
        if v.dimension.width > row_width : 
            row_width = v.dimension.width

    positions, outside_height = layout_outside(outside, row_width)

    ax.text(
        outside_x + row_width / 2, -0.7,
        f"DI LUAR KAPAL - SKEMATIS ({len(outside)})", 
        ha = "center", fontsize=9, fontweight="bold", color="dimgray",)

    #gambar kendaraan luar memakai posisi dari layout outside 
    for v in outside: 
        x,y=positions[v.id]
        draw_vehicles(ax,v,outside_x+x,y,colors[v.id],outside=True,)

    #tinggi gambar ikuti area yang lebih panjang
    image_height = L 

    if outside_height>image_height: 
        image_height = outside_height

    #beri ruang di sekeliling gambar 
    ax.set_xlim(-1.5,outside_x + row_width + 1.5)

    #batas y dibalik supaya koordinat y bertambah ke bawah 
    ax.set_ylim(image_height + 1.5, -2.5)

    #ukuran satu satuan pada sumbu x dan y dibuat sama 
    ax.set_aspect("equal")

    #angka koordinat ditampilkan setiap 2 satuan 
    ax.set_xticks(range(0, W+1, 2))
    ax.set_yticks(range(0,L+1,2))
    ax.tick_params(labelsize=7)

    #hitung berat kendaraan yang dimuat
    total_weight = sum(v.weight for v in inside)
    status = (not utils.exceed_ship_limit(vehicles,ship) and utils.not_overlapping(vehicles,ship) and not utils.exceed_capacity_limit(vehicles,ship))
    if status: 
        status = "Valid"
    else: 
        status="Tidak valid"
    objective = utils.objective_function(vehicles,ship)
    ax.set_title(
        f"{title}\n"
        f"Objective = {objective} |" f"Berat {total_weight}/{ship.maxCapacity}\n" f"Terangkut{len(inside)}/{len(vehicles)} | {status}", fontsize=10,)

#objective maks dan rata rata populasi 
def plot_convergence(ax,info,title): 
    ax.plot(info["max_history"], color="#1f77b4",linewidth=2,label="Maksimum populasi")
    ax.plot(info["mean_history"], color="#ff7f0e",linewidth=1.6,linestyle="--",label="Rata-rata populasi")
    ax.set_xlabel("Iterasi")
    ax.set_ylabel("Objective(total shipping fee)")
    ax.set_title(title,fontsize=10)
    ax.grid(alpha=0.3)
    ax.legend(loc="lower right",fontsize=8)

# menggabungkan grafik beberapa run dalam satu gambar, yang garis tebal = maks, yang garis putus-putus = rata-rata
def plot_runs_convergence(ax,results,title): 
    palette = plt.get_cmap("tab10").colors

    for i, result in enumerate(results): 
        color=palette[i%len(palette)]
        info=result["info"]
        run=result["run"]

        #grafik objective maks
        ax.plot(info["max_history"], color=color, linewidth=2, label=f"Run {run} maks")

        #grafik objective rata-rata
        ax.plot(info["mean_history"],color=color,linewidth=1.2,linestyle="--",label=f"Run {run} rata-rata")

    ax.set_xlabel("Generasi (0 = populasi awal)")
    ax.set_ylabel("Objective")
    ax.set_title(title,fontsize=10)

    ax.grid(alpha=0.3)
    ax.legend(loc="lower right",fontsize=7,ncol=2)

def save_figure(fig,path): 
    os.makedirs(os.path.dirname(path),exist_ok=True)
    fig.savefig(path,dpi=150,bbox_inches="tight")
    plt.close(fig)

#simpan satu state sbg PNG 
def save_state_figure(vehicles,ship,colors,title,path):
    W,L = ship.dimension.width, ship.dimension.length
    fig,ax=plt.subplots(figsize=(max(7,0.37*(2*W+5)), max(5,0.36*L+2.2)))
    draw_state(ax,vehicles,ship,colors,title)
    save_figure(fig,path)

#simpan grafik objective terhadap iterasi satu run sbg png 
def save_convergence_figure(info,title,path): 
    fig,ax=plt.subplots(figsize=(8,4.2))
    plot_convergence(ax,info,title)
    save_figure(fig,path)