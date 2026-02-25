import os
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict
import plotter_definitions as pd

# Configurações de diretório
STATS_DIR = "statistics"

def parse_stats_file(filepath):
    """Lê o arquivo e retorna um dicionário com os valores numéricos."""
    data = {}
    if not os.path.exists(filepath):
        return None
    try:
        with open(filepath, 'r') as f:
            for line in f:
                if ":" in line:
                    key, val = line.split(":", 1)
                    data[key.strip()] = val.strip()
        
        return {
            "vertices": int(data.get("Number of vertices", 0)),
            "edges": int(data.get("Number of edges", 0)),
            "iterations": int(data.get("Number of iterations", 1)),
            "time": float(data.get("Solving time", 0))
        }
    except Exception as e:
        print(f"Erro ao ler {filepath}: {e}")
        return None

def generate_individual_plots():
    # Estrutura para armazenar os dados calculados
    # data_points[solver] = { instance: { 'x': val, 'ratios': [val1, val2, val3] } }
    data_points = defaultdict(lambda: defaultdict(lambda: {'x': 0, 'ratios': []}))

    # Processamento
    for solver in pd.solvers:
        is_kruskal = "Kruskal" in solver
        
        for inst in pd.instances:
            for seed in pd.seeds:
                filename = f"{inst}_{solver}_{seed}.txt"
                filepath = os.path.join(STATS_DIR, filename)
                
                stats = parse_stats_file(filepath)
                if stats:
                    # Define o valor do eixo X conforme o tipo de solver
                    x_val = stats["edges"] if is_kruskal else stats["vertices"]
                    ratio = stats["time"] / stats["iterations"]
                    
                    data_points[solver][inst]['x'] = x_val
                    data_points[solver][inst]['ratios'].append(ratio)

    # Geração de um gráfico para cada solver
    for i, solver in enumerate(pd.solvers):
        plt.figure(figsize=(10, 6))
        
        x_final = []
        y_final = []
        
        # Calcula a média das seeds para cada instância do solver atual 
        for inst, info in data_points[solver].items():
            if info['ratios']:
                x_final.append(info['x'])
                y_final.append(np.mean(info['ratios']))
        
        # Ordenação para garantir que a linha do gráfico siga o eixo X crescentemente
        if x_final:
            sorted_idx = np.argsort(x_final)
            x_plot = np.array(x_final)[sorted_idx]
            y_plot = np.array(y_final)[sorted_idx]
            
            # Plotagem
            label_name = pd.solver_labels[solver]
            plt.plot(x_plot, y_plot, marker='o', linestyle='-', color=pd.colors[i], label=label_name)
            
            # Configurações 
            is_kruskal = "Kruskal" in solver
            xlabel = "Número de Arestas" if is_kruskal else "Número de Vértices"
            
            plt.title(f"Eficiência: {label_name}")
            plt.xlabel(xlabel)
            plt.ylabel("Média (Solving Time / Iterations)")
            plt.grid(True, which="both", ls="--", alpha=0.5)
            plt.legend()
            
            # Salva cada gráfico com o nome do solver
            filename_png = f"eficiência_{solver}.png"
            plt.savefig(filename_png)
            plt.close() # Fecha a figura atual para não sobrepor na próxima iteração

if __name__ == "__main__":
    generate_individual_plots()