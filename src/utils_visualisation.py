from matplotlib.patches import Rectangle
import utils, matplotlib.pyplot as plt 

#satu warna tetap per id kendaraan, supaya sama di state awal & akhir
def build_color_map(vehicles): 
    palette = list(plt.get_cmap("tab20").colors) + list(plt.get_cmap("tab20b").colors)
    return {v.id: palette[i % len(palette)] for i, v in enumerate(vehicles)}

#gambar satu kendaraan, label nama saja (yang di luar kapal pucat + diarsir)
def draw_vehicles(ax,v,x,y,color,outside=False): 
    w, l = v.dimension.width, v.dimension.length 
    ax.add_patch(Rectangle((x,y),w,l,facecolor=color,edgecolor="black",
        alpha=0.5 if outside else 0.95, hatch="//" if outside else None))
    ax.text(x+w/2, y+l/2, str(v.id), ha="center", va="center", fontsize=8,
        fontweight="bold", rotation=90 if w == 1 and l >= 2 else 0)

#susun kendaraan di luar kapal per baris, kalau penuh turun ke baris berikutnya
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

    #kapal + garis kotak
    ax.add_patch(Rectangle((0,0),W,L,facecolor="#eef3f8",edgecolor="black",linewidth=2.5))
    for x in range(1,W): 
        ax.plot([x,x],[0,L],color="#c5ced8",linewidth=0.6)
    for y in range(1,L): 
        ax.plot([0,W],[y,y],color="#c5ced8",linewidth=0.6)
    ax.text(W/2,-0.7,"KAPAL",ha="center",fontsize=9,fontweight="bold")

    for v in inside: 
        draw_vehicles(ax,v,v.x,v.y,colors[v.id])

    #area luar di sebelah kanan kapal, lebar baris minimal selebar kendaraan terlebar
    outside_x = W + 2 
    row_width = max([W] + [v.dimension.width for v in outside])
    positions, outside_height = layout_outside(outside, row_width)

    ax.text(outside_x + row_width/2, -0.7, f"DI LUAR KAPAL ({len(outside)})",
        ha="center", fontsize=9, fontweight="bold", color="dimgray")
    for v in outside: 
        x,y=positions[v.id]
        draw_vehicles(ax,v,outside_x+x,y,colors[v.id],outside=True)

    #batas gambar (y dibalik supaya y bertambah ke bawah), skala x dan y sama
    ax.set_xlim(-1.5,outside_x + row_width + 1.5)
    ax.set_ylim(max(L,outside_height) + 1.5, -2.5)
    ax.set_aspect("equal")
    ax.set_xticks(range(0, W+1, 2))
    ax.set_yticks(range(0,L+1,2))
    ax.tick_params(labelsize=7)

    total_weight = sum(v.weight for v in inside)
    objective = utils.objective_function(vehicles,ship)
    ax.set_title(
        f"{title}\n"
        f"Objective = {objective} | Berat {total_weight}/{ship.maxCapacity}\n"
        f"Terangkut {len(inside)}/{len(vehicles)}", fontsize=10)