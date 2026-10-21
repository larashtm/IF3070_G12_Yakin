import csv
import statistics
import sys
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import io 
from contextlib import redirect_stdout

import utils
import ga_visualization as viz
from ga_genetic_algorithm import genetic_algorithm 
from pathlib import Path

#Time untuk menjalankan genetic algorithm 

#pengaturan eksperimen
OUTPUT_DIR="output/ga"
NUM_RUNS=3
MUTATION_RATE=0.15
PRINT_STATES=True 
SAVE_STATE_IMAGES =False

#eksperimen 1:populasi tetap, iterasi berubah 
POP_CONTROL=30
ITER_VARIATIONS=[50,100,200]

#eksperimen 2: iterasi tetap, populasi berubah 
ITER_CONTROL=100
POP_VARIATIONS=[10,30,60]

#nangkepin hasil displaymap supaya kesimpan ke file
def render_state(state,ship,title,score): 
    buffer=io.StringIO()
    with redirect_stdout(buffer): 
        utils.display_map(state,ship)

    return f"{title} (objective function-{score})\n{buffer.getvalue()}"

#jalanin satu konfigurasi sebanyak NUM_RUNS kali 
def run_config(vehicles,ship,colors,population_size,max_iter): 
    folder=f"{OUTPUT_DIR}/pop{population_size}_iter{max_iter}"
    os.makedirs(folder,exist_ok=True)

    results=[]

    for run in range(1,NUM_RUNS+1): 
        #seed berbeda tiap run, tetapi bisa ngulnag
        seed=run
        best_state,best_score,info=genetic_algorithm(vehicles,ship,population_size=population_size,max_iter=max_iter,mutation_rate=MUTATION_RATE,seed=seed)

        tag=f"populasi={population_size},iterasi={max_iter},run={run}"
        initial_text=render_state(info["initial_state"],ship,f"State awal({tag})",info["initial_score"])
        final_text=render_state(best_state,ship,f"State akhir({tag})",best_score)

        #simpenin state awal dan akhir dalam satu file teks 
        with open(
            f"{folder}/run{run}_states.txt","w",encoding="utf-8",) as file: file.write(initial_text+"\n"+final_text)

        #tampilin juga di terminal 
        if PRINT_STATES: 
            print(initial_text)
            print(final_text)
        #simpan png kalau diaktifin 
        if SAVE_STATE_IMAGES:
            viz.save_state_figure(info["initial_state"],ship,colors,f"State awal({tag})",f"{folder}/run{run}_initial.png")
            viz.save_state_figure(best_state,ship,colors,f"State akhir({tag})",f"{folder}/run{run}_final.png")
        #simpan grafik maksimum dan rata-rata populasi 
        viz.save_convergence_figure(
            info,f"Perkembangan objective({tag})",f"{folder}/run{run}_convergence.png"
        )

        results.append({
            "run":run,
            "seed":seed,
            "best_score":best_score,
            "info":info,
        })

        print(
            f"{tag}: "
            f"awal={info['initial_score']}, "
            f"akhir={best_score}, "
            f"durasi={info['duration']:.3f} detik"
        )

    #gabungin grafik semua run 
    fig,ax=plt.subplots(figsize=(9,5))

    viz.plot_runs_convergence(ax,results,f"{NUM_RUNS} run, populasi={population_size},iterasi={max_iter}")
    viz.save_figure(fig,f"{folder}/all_runs_convergence.png")
    return results 

def save_summary_csv(all_results,path): 
    columns=[
        "populasi",
        "iterasi",
        "run",
        "seed",
        "objective_awal",
        "objective_akhir", 
        "durasi_detik", 
    ]

    with open(path,"w",newline="",encoding="utf-8") as file: 
        writer = csv.DictWriter(file,fieldnames=columns)
        writer.writeheader()

        for config, results in all_results.items(): 
            population_size, max_iter = config 

            for result in results: 
                info = result["info"]
                writer.writerow({
                    "populasi":population_size,
                    "iterasi":max_iter,
                    "run":result["run"], 
                    "seed":result["seed"], 
                    "objective_awal":info["initial_score"], 
                    "objective_akhir":result["best_score"], 
                    "durasi_detik":info["duration"],
                })

#gambar pengaruh perubahan iterasi and populasi 
def plot_parameter_effect(experiment_groups,path): 
    fig,axes = plt.subplots(2,2,figsize=(11,8))
    for row,group in enumerate (experiment_groups): 
        ax_score,ax_time=axes[row]
        values=[]
        mean_scores=[]
        mean_times=[]

        for experiment in group["experiments"]: 
            value=experiment["value"]
            scores=[]
            durations=[]

            #kumpulin semuaaaa hasil run
            for result in experiment["results"]: 
                scores.append(result["best_score"])
                durations.append(result["info"]["duration"])

            values.append(value)
            mean_scores.append(statistics.mean(scores))
            mean_times.append(statistics.mean(durations))

            #semua run pada konfigurasi ini punya nilai x yang sama 
            xs = [value]*len(scores)
            ax_score.scatter(xs,scores,color="blue",alpha=0.5)
            ax_time.scatter(xs,durations,color="blue",alpha=0.5)

        #hubungin rata-rata tiap konfigurasinyaa
        ax_score.plot(values,mean_scores,
                      color="red",marker="o",label="Rata-rata run")
        ax_time.plot(values,mean_times,
                     color="red",marker="o",label="Rata-rata run")
        
        if group["parameter"]=="iterasi": 
            xlabel="jumlah iterasi"
            control=f"Populasi tetap={group['control']}"
        else:
            xlabel="Jumlah populasi"
            control=f"iterasi tetap={group['control']}"
       
        ax_score.set_title(f"{control}\nObjective akhir")
        ax_score.set_ylabel("Objective akhir")

        ax_time.set_title(f"{control}\nDurasi Pencarian")
        ax_time.set_ylabel("Durasi (detik)")

        #pengaturan sama untuk kedua grafikny
        for ax in axes[row]: 
            ax.set_xlabel(xlabel)
            ax.set_xticks(values)
            ax.grid(alpha=0.3)
            ax.legend(fontsize=8)

    fig.tight_layout()
    viz.save_figure(fig,path)


def main(): 
    data_path=Path(__file__).resolve().parent/"vehicles.json"
    vehicles,ship=utils.load_json(str(data_path))
    colors=viz.build_color_map(vehicles)
    os.makedirs(OUTPUT_DIR,exist_ok=True)

    plan=[
        ("Eksperimen 1","iterasi",ITER_VARIATIONS,POP_CONTROL),
        ("Eskperimen 2","populasi",POP_VARIATIONS,ITER_CONTROL),
    ]

    all_results={}
    experiment_groups=[]

    for name, parameter, values, controls in plan: 
        print(name)
        experiments=[]

        for value in sorted(values): 
            if parameter=="iterasi":
                population_size=controls
                max_iter=value
            else: 
                population_size=value
                max_iter=controls
            config=(population_size,max_iter)
            
            if config not in all_results:
                all_results[config]=run_config(
                    vehicles,ship,colors,
                    population_size,max_iter,
                )
            experiments.append({
                "value":value,
                "results":all_results[config],
            })
        experiment_groups.append({
            "name":name,
            "parameter":parameter,
            "control":controls,
            "experiments":experiments,


        })
    save_summary_csv(all_results,f"{OUTPUT_DIR}/summaryGA.csv")

    plot_parameter_effect(experiment_groups,f"{OUTPUT_DIR}/parameter_effect.png")

if __name__=="__main__": 
    main()
