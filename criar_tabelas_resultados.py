import pandas as pd
import os

#VARIÁVEIS DE CONFIGURAÇÃO
BASE_DIR = './'
PATH_PARETO = os.path.join(BASE_DIR, 'pareto')
PATH_STATISTICS = os.path.join(BASE_DIR, 'statistics')

tempo = "2048s"
NOME_SAIDA = f'Resultados_NSBRKGA_Coloracao_Kruskal{tempo}_SBPO.xlsx'


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


MAPEAMENTO_LEGENDA = {
    'nsbrkgaColoracaoMax': 'nsbrkgaColoracaoMax',
    'nsbrkgaColoracaoQuad': 'nsbrkgaColoracaoQuad',
    'nsbrkgaKruskalMax': 'nsbrkgaKruskalMax',
    'nsbrkgaKruskalQuad' : 'nsbrkgaKruskalQuad',
    'nsbrkgaColoracaoBase': 'nsbrkgaColoracaoBase'
}

metodos = ["nsbrkgaMax", "nsbrkgaQuad", "nsbrkgaKruskalMax", "nsbrkgaKruskalQuad","nsbrkgaColoracaoBase"]
seeds = ["1089661", "1602347", "1644410"]

def format_brazilian(val):
    """Aplica 4 casas decimais e troca ponto por vírgula para o Google Sheets."""
    if val is None or val == "": return ""
    try:
        return f"{float(val):.4f}".replace('.', ',')
    except:
        return val

def processar():
    writer = pd.ExcelWriter(NOME_SAIDA, engine='openpyxl')
    
    for metodo in metodos:
        rows = []
        # Nome das abas como metodo_tempo
        nome_aba = f"{MAPEAMENTO_LEGENDA[metodo]}_{tempo}"
        print(f"Processando: {nome_aba}...")
        
        for inst in instancias_base:
            for seed in seeds:
                file_name = f"{inst}_{metodo}_{seed}.txt"
                
               
                path_p = os.path.join(PATH_PARETO, file_name)
                cost_min, bal_rel, cost_rel, bal_min, total_sols = None, None, None, None, 0
                
                if os.path.exists(path_p):
                    solutions = []
                    with open(path_p, 'r') as f:
                        for line in f:
                            # Ignora linhas de componentes e separadores
                            if "Componentes" in line or "=" in line: break
                            parts = line.split()
                            if len(parts) >= 2:
                                try:
                                    solutions.append((float(parts[0]), float(parts[1])))
                                except ValueError: continue
                    
                    if solutions:
                        total_sols = len(solutions)
                        
                        
                        # Menor Custo e menor Bal correspondente
                        # Ordena por custo (asc) e depois por balanceamento (asc)
                        sol_by_cost = sorted(solutions, key=lambda x: (x[0], x[1]))
                        cost_min, bal_rel = sol_by_cost[0][0], sol_by_cost[0][1]
                        
                        # Menor Balanceamento e menor Custo correspondente
                        # Ordena por balanceamento (asc) e depois por custo (asc)
                        sol_by_bal = sorted(solutions, key=lambda x: (x[1], x[0]))
                        cost_rel, bal_min = sol_by_bal[0][0], sol_by_bal[0][1]
                
                # --- Leitura do arquivo Statistics ---
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

                # Montagem da linha conforme estrutura solicitada
                rows.append({
                    "metodo": MAPEAMENTO_LEGENDA[metodo],
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
        
        # Cria o DataFrame e salva na aba correspondente
        df = pd.DataFrame(rows)
        df.to_excel(writer, sheet_name=nome_aba, index=False)
    
    writer.close()
    print(f"\nSucesso! Relatório gerado: {NOME_SAIDA}")

if __name__ == "__main__":
    processar()