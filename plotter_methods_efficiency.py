import os
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict
import plotter_definitions as pd

# Configurações de caminho
STATS_DIR = "statistics"

def parse_stats_file(filepath):
    """Extrai os dados necessários de um arquivo de estatísticas."""
    data = {}
    try:
        with open(filepath, 'r') as f:
            for line in f:
                if ":" in line:
                    key, val = line.split(":", 1)
                    data[key.strip()] = val.strip()
        
        return {
            "vertices": int(data.get("Number of vertices", 0)),
            "edges": int(data.get("Number of edges", 0)),
            "iterations": int(data.get("Number of iterations", 1)), # Evitar divisão por zero
            "time": float(data.get("Solving time", 0))
        }
    except FileNotFoundError:
        return None

def generate_plots():
    # Estrutura: results[solver][instance] = list of (time/iterations)
    # E guardamos metadados da instância (edges/vertices)
    results = defaultdict(lambda: defaultdict(list))
    instance_metadata = {}

    # 1. Coleta de dados
    for solver in pd.solvers:
        for inst in pd.instances:
            for seed in pd.seeds:
                filename = f"{inst}_{solver}_{seed}.txt"
                filepath = os.path.join(STATS_DIR, filename)
                
                stats = parse_stats_file(filepath)
                if stats:
                    ratio = stats["time"] / stats["iterations"]
                    results[solver][inst].append(ratio)
                    
                    # Salva metadados apenas uma vez por instância
                    if inst not in instance_metadata:
                        instance_metadata[inst] = {
                            "edges": stats["edges"],
                            "vertices": stats["vertices"]
                        }

    # 2. Preparação para o Plot
    fig, (ax_kruskal, ax_color) = plt.subplots(1, 2, figsize=(16, 6))

    for i, solver in enumerate(pd.solvers):
        is_kruskal = "Kruskal" in solver
        ax = ax_kruskal if is_kruskal else ax_color
        
        x_values = []
        y_values = []

        # Calcula a média das seeds para cada instância
        for inst in pd.instances:
            if inst in results[solver] and results[solver][inst]:
                avg_ratio = np.mean(results[solver][inst])
                y_values.append(avg_ratio)
                
                if is_kruskal:
                    x_values.append(instance_metadata[inst]["edges"])
                else:
                    x_values.append(instance_metadata[inst]["vertices"])

        # Ordenar os dados pelo eixo X para que a linha do gráfico não fique "vai e vem"
        if x_values:
            sorted_idx = np.argsort(x_values)
            x_sorted = np.array(x_values)[sorted_idx]
            y_sorted = np.array(y_values)[sorted_idx]

            ax.plot(x_sorted, y_sorted, marker='o', label=pd.solver_labels[solver], color=pd.colors[i])

    # 3. Formatação do Gráfico Kruskal (Eixo X: Arestas)
    ax_kruskal.set_title("Métodos Baseados em Kruskal")
    ax_kruskal.set_xlabel("Número de Arestas (Edges)")
    ax_kruskal.set_ylabel("Média (Solving Time / Iterations)")
    ax_kruskal.grid(True, linestyle='--', alpha=0.7)
    ax_kruskal.legend()

    # 4. Formatação do Gráfico Coloração (Eixo X: Vértices)
    ax_color.set_title("Métodos Baseados em Coloração")
    ax_color.set_xlabel("Número de Vértices (Vertices)")
    ax_color.set_ylabel("Média (Solving Time / Iterations)")
    ax_color.grid(True, linestyle='--', alpha=0.7)
    ax_color.legend()

    plt.tight_layout()
    plt.savefig("analysis_results.png")
    plt.show()

if __name__ == "__main__":
    generate_plots()