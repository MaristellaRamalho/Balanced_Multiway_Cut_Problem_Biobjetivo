import pandas as pd
import os

# VARIÁVEIS DE CONFIGURAÇÃO 
BASE_DIR = 'TESTES_NSBRKGA_MAX_E_QUAD_2048s'
PATH_PARETO = os.path.join(BASE_DIR, 'pareto')
PATH_STATISTICS = os.path.join(BASE_DIR, 'statistics')

tempo = "2048s"
NOME_SAIDA = f'Resultados_NSBRKGA_{tempo}.xlsx'

instancias_base = [
    "N160_M2N_K10_1", "N160_M2N_K10_2", "N160_M2N_K10_3",
    "N160_M2N_K20_1", "N160_M2N_K20_2", "N160_M2N_K20_3",
    "N160_M2N_K40_1", "N160_M2N_K40_2", "N160_M2N_K40_3",
    "N160_M4N_K10_1", "N160_M4N_K10_2", "N160_M4N_K10_3",
    "N160_M4N_K20_1", "N160_M4N_K20_2", "N160_M4N_K20_3",
    "N160_M4N_K40_1", "N160_M4N_K40_2", "N160_M4N_K40_3",
    "N160_M8N_K10_1", "N160_M8N_K10_2", "N160_M8N_K10_3",
    "N160_M8N_K20_1", "N160_M8N_K20_2", "N160_M8N_K20_3",
    "N160_M8N_K40_1", "N160_M8N_K40_2", "N160_M8N_K40_3",
    "N320_M2N_K20_1", "N320_M2N_K20_2", "N320_M2N_K20_3",
    "N320_M2N_K40_1", "N320_M2N_K40_2", "N320_M2N_K40_3",
    "N320_M2N_K80_1", "N320_M2N_K80_2", "N320_M2N_K80_3",
    "N320_M4N_K20_1", "N320_M4N_K20_2", "N320_M4N_K20_3",
    "N320_M4N_K40_1", "N320_M4N_K40_2", "N320_M4N_K40_3",
    "N320_M4N_K80_1", "N320_M4N_K80_2", "N320_M4N_K80_3",
    "N320_M8N_K20_1", "N320_M8N_K20_2", "N320_M8N_K20_3",
    "N320_M8N_K40_1", "N320_M8N_K40_2", "N320_M8N_K40_3",
    "N320_M8N_K80_1", "N320_M8N_K80_2", "N320_M8N_K80_3",
    "N640_M2N_K160_1", "N640_M2N_K160_2", "N640_M2N_K160_3",
    "N640_M2N_K40_1", "N640_M2N_K40_2", "N640_M2N_K40_3",
    "N640_M2N_K80_1", "N640_M2N_K80_2", "N640_M2N_K80_3",
    "N640_M4N_K160_1", "N640_M4N_K160_2", "N640_M4N_K160_3",
    "N640_M4N_K40_1", "N640_M4N_K40_2", "N640_M4N_K40_3",
    "N640_M4N_K80_1", "N640_M4N_K80_2", "N640_M4N_K80_3",
    "N640_M8N_K160_1", "N640_M8N_K160_2", "N640_M8N_K160_3",
    "N640_M8N_K40_1", "N640_M8N_K40_2", "N640_M8N_K40_3",
    "N640_M8N_K80_1", "N640_M8N_K80_2", "N640_M8N_K80_3"
]

metodos = ["nsbrkgaMax", "nsbrkgaQuad"]
seeds = ["1089661", "1602347", "1644410"]

def format_brazilian(val):
    if val is None or val == "": return ""
    try:
        return f"{float(val):.4f}".replace('.', ',')
    except:
        return val

def processar():
    writer = pd.ExcelWriter(NOME_SAIDA, engine='openpyxl')
    
    for metodo in metodos:
        rows = []
        nome_aba = f"{metodo}_{tempo}"
        print(f"Processando: {nome_aba}...")
        
        for inst in instancias_base:
            for seed in seeds:
                file_name = f"{inst}_{metodo}_{seed}.txt"
                
                # Pareto 
                path_p = os.path.join(PATH_PARETO, file_name)
                cost_min, bal_rel, cost_rel, bal_min, total_sols = None, None, None, None, 0
                
                if os.path.exists(path_p):
                    solutions = []
                    with open(path_p, 'r') as f:
                        for line in f:
                            if "Componentes" in line: break
                            parts = line.split()
                            if len(parts) >= 2:
                                try:
                                    solutions.append((float(parts[0]), float(parts[1])))
                                except ValueError: continue
                    if solutions:
                        total_sols = len(solutions)
                        s_c_min = min(solutions, key=lambda x: x[0])
                        cost_min, bal_rel = s_c_min[0], s_c_min[1]
                        s_b_min = min(solutions, key=lambda x: x[1])
                        cost_rel, bal_min = s_b_min[0], s_b_min[1]
                
                # Statistics 
                path_s = os.path.join(PATH_STATISTICS, file_name)
                last_gen, n_iters, solving_time, seed_val = "", "", "", ""
                nodes, edges, terminals = "", "", ""
                
                if os.path.exists(path_s):
                    with open(path_s, 'r') as f:
                        for line in f:
                            if "Number of vertices" in line: nodes = line.split()[-1]
                            elif "Number of edges" in line: edges = line.split()[-1]
                            elif "Number of terminals" in line: terminals = line.split()[-1]
                            elif "Last update generation" in line: last_gen = line.split()[-1]
                            elif "Number of iterations" in line: n_iters = line.split()[-1]
                            elif "Solving time" in line: solving_time = format_brazilian(line.split()[-1])
                            elif "Seed" in line: seed_val = line.split()[-1]

                rows.append({
                    "metodo": metodo,
                    "instancia": inst,
                    "Nodes": nodes,
                    "Edges": edges,
                    "Terminals": terminals,
                    "Cost (min)": cost_min, 
                    "Bal": format_brazilian(bal_rel),
                    "Cost": cost_rel, 
                    "Bal (min)": format_brazilian(bal_min),
                    "Last update generation": last_gen,
                    "Number of iterations": n_iters,
                    "Solving time": solving_time,
                    "Total de Soluções Obtidas": total_sols,
                    "Seed": seed_val
                })
        
        pd.DataFrame(rows).to_excel(writer, sheet_name=nome_aba, index=False)
    
    writer.close()
    print(f"\nRelatório gerado com sucesso: {NOME_SAIDA}")

if __name__ == "__main__":
    processar()