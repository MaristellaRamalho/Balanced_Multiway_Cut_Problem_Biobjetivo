import os
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
import statistics as stats
from plotter_definitions import *
import matplotlib.ticker as ticker

dirname = os.path.dirname(__file__)
STATS_DIR = os.path.join(dirname, "statistics")


def parse_stats_file(filepath):
    data = {}

    if not os.path.exists(filepath):
        return None
    try:
        with open(filepath, "r") as f:
            for line in f:
                if ":" in line:
                    key, val = line.split(":", 1)
                    data[key.strip()] = val.strip()

        return {
            "vertices": int(data.get("Number of vertices", 0)),
            "edges": int(data.get("Number of edges", 0)),
            "iterations": int(data.get("Number of iterations", 1)),
            "time": float(data.get("Solving time", 0.0))
        }

    except Exception:
        return None


# Separação dos solvers
# Desconsidera método exato -> olha só versões nsbrkga
coloring_solvers = [s for s in solvers_with_seed if "Kruskal" not in s]
kruskal_solvers = [s for s in solvers_with_seed if "Kruskal" in s]
#print(coloring_solvers)
#print(kruskal_solvers)

# Processamento solvers de coloração
time_per_vertices = {}

for solver in coloring_solvers:
    time_per_vertices[solver] = {}
    for size in sizes:
        time_per_vertices[solver][size] = []

for size in sizes:
    for instance in instances_per_size[size]:
        for solver in coloring_solvers:
            for seed in seeds:

                filename = os.path.join(
                    STATS_DIR,
                    instance + "_" + solver + "_" + str(seed) + ".txt"
                )
                #print(f"Arquivo: {filename}")
                stats_file = parse_stats_file(filename)

                if stats_file and stats_file["iterations"] > 0:
                    ratio = stats_file["time"] / stats_file["iterations"] 
                    v = stats_file["vertices"]
                    time_per_vertices[solver][v].append(ratio)
                #print(f"num_it : {stats_file["iterations"] } | time : {stats_file["time"] } | v : {stats_file["vertices"]} | ratio : {ratio}")

# Processamento solvers de kruskal
time_per_edges = {}

for solver in kruskal_solvers:
    time_per_edges[solver] = {}

for instance in instances:
    for solver in kruskal_solvers:
        for seed in seeds:

            filename = os.path.join(
                STATS_DIR,
                instance + "_" + solver + "_" + str(seed) + ".txt"
            )

            #print(f"arquivo : {filename}")
            stats_file = parse_stats_file(filename)

            if stats_file and stats_file["iterations"] > 0:
                ratio = stats_file["time"] / stats_file["iterations"]
                e = stats_file["edges"]

                if e not in time_per_edges[solver]:
                    time_per_edges[solver][e] = []

                time_per_edges[solver][e].append(ratio)
                #print(f"num_it : {stats_file["iterations"] } | time : {stats_file["time"] } | v : {stats_file["vertices"]} | ratio : {ratio}")


#cálculo dos limites do eixo y
all_y_values = []

for solver in coloring_solvers:
    x_values = sorted(time_per_vertices[solver].keys())
    y = [stats.mean(time_per_vertices[solver][x]) for x in x_values]
    all_y_values.extend(y)
    #print(f"solver : {solver} | vetor_y : {y} | media_160: {stats.mean(time_per_vertices[solver][160])} | media_320: {stats.mean(time_per_vertices[solver][320])} | media_640: {stats.mean(time_per_vertices[solver][640])}")

for solver in kruskal_solvers:
    x_values = sorted(time_per_edges[solver].keys())
    #print(f"chaves_edges: {x_values}")
    y = [stats.mean(time_per_edges[solver][e]) for e in x_values]
    #print(f"solver : {solver} | edges : {e} | vetor_y : {y} ")
    all_y_values.extend(y)

y_min = min(all_y_values)
y_max = max(all_y_values)

#Plotando os dois graficos no mesmo qudro -> mesma escala eixo y
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

#Configurando marcadores
#markers = ['s', 'o']

# ---- COLORAÇÃO ----

ax1.set_xlabel("Número de Vértices", fontsize="large")
ax1.set_ylabel("Média (Tempo de execução / Número de iterações)", fontsize="large")
ax1.tick_params(axis="both", which="both", labelsize="large")
ax1.grid(alpha=0.5, color='gray', linestyle='dashed', linewidth=0.5)

for solver in coloring_solvers:
    i = solvers.index(solver)
    x_values = sorted(time_per_vertices[solver].keys())
    y = [stats.mean(time_per_vertices[solver][x]) for x in x_values]
    #marker_idx = i % len(markers)
    #line_idx = i % len(linestyles)

    ax1.plot(
        x_values,
        y,
        label=solver_labels[solver],
        #marker=markers[marker_idx],
        #linestyle=linestyles[line_idx],
        markersize=4,
        linewidth=1.5,
        color=colors[i],
        alpha=0.8
    )

ax1.set_xscale("log")
ax1.set_yscale("linear")

# nos ticks aparece apenas 160 320 e 640
ax1.xaxis.set_major_locator(ticker.FixedLocator(sizes))
ax1.xaxis.set_major_formatter(FormatStrFormatter('%d'))
ax1.xaxis.set_minor_locator(ticker.NullLocator())

ax1.set_ylim(y_min, y_max)

ax1.xaxis.set_major_formatter(FormatStrFormatter('%d'))
ax1.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))

ax1.legend(fontsize="large", loc="upper right")


# ---- KRUSKAL ----

ax2.set_xlabel("Número de Arestas", fontsize="large")
ax2.set_ylabel("Média (Tempo de execução / Número de iterações)", fontsize="large")
ax2.tick_params(axis="both", which="both", labelsize="large")
ax2.grid(alpha=0.4, color='gray', linestyle='dashed', linewidth=0.5)

for solver in kruskal_solvers:
    i = solvers.index(solver)
    x_values = sorted(time_per_edges[solver].keys())
    y_values = [stats.mean(time_per_edges[solver][e]) for e in x_values]
    #marker_idx = i % len(markers)
    #line_idx = i % len(linestyles)

    ax2.plot(
        x_values,
        y_values,
        label=solver_labels[solver],
        #marker=markers[marker_idx],
        #linestyle=linestyles[line_idx],
        markersize=4,
        linewidth=1.5,
        color=colors[i],
        alpha=0.8
    )

ax2.set_xscale("log")
ax2.set_yscale("linear")

all_edges = sorted({e for solver in kruskal_solvers for e in time_per_edges[solver].keys()})
ax2.set_xlim(min(all_edges), max(all_edges))

ax2.xaxis.set_major_locator(
    ticker.LogLocator(base=10.0, subs=(1.0, 2.0, 5.0))
)

ax2.xaxis.set_major_formatter(FormatStrFormatter('%d'))
ax2.set_ylim(y_min, y_max)
ax2.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))

ax2.legend(fontsize="large", loc="upper left")


plt.tight_layout()

plt.savefig(
    bbox_inches='tight',
    fname=os.path.join(dirname, "statistics/time_mean_combined.png"),
    format="png"
)

plt.savefig(
    bbox_inches='tight',
    fname=os.path.join(dirname, "statistics/time_mean_combined.pdf"),
    format="pdf"
)

plt.close()