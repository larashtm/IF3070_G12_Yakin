import os, matplotlib.pyplot as plt 

#objective maks dan rata rata populasi
def plot_convergence(ax,info,title):
    ax.plot(info["max_history"], color="#1f77b4",linewidth=2,label="Maksimum populasi")
    ax.plot(info["mean_history"], color="#ff7f0e",linewidth=1.6,linestyle="--",label="Rata-rata populasi")
    ax.set_xlabel("Iterasi")
    ax.set_ylabel("Objective(total shipping fee)")
    ax.set_title(title,fontsize=10)
    ax.grid(alpha=0.3)
    ax.legend(loc="lower right",fontsize=8)
    
#menggabungkan grafik beberapa run dalam satu gambar, yang garis tebal = maks, yang garis putus-putus = rata-rata
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

#simpan grafik objective terhadap iterasi satu run sbg png 
def save_convergence_figure(info,title,path): 
    fig,ax=plt.subplots(figsize=(8,4.2))
    plot_convergence(ax,info,title)
    save_figure(fig,path)