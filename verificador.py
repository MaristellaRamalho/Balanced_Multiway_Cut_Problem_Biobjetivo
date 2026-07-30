'''
  Verifica os resultados obtidos -> Lê arquivo da instância, fronteira de Pareto e Statistics correspondentes -> confere os valores reportados para as funções objetivo, validade da solução e informações da instância. 
'''

import os
from os.path import isfile, join
import math
import numpy as np
import glob

ROOT_DIR = "."
INSTANCES_DIR = os.path.join(ROOT_DIR, "instances")
PARETO_DIR = os.path.join(ROOT_DIR, "pareto")
STATS_DIR = os.path.join(ROOT_DIR, "statistics")

EXTENSION_INSTANCE = ".gr"
EXTENSION_PARETO = ".txt"
EXTENSION_STATS = ".txt"

time_limit = 2048

DEBUG = 0

def ler_instancia(path):
    """
    Lê o arquivo .gr da pasta instances.
    """

    if not os.path.exists(path):
        return None
    
    with open(path, 'r', encoding='utf-8') as f:
        lines = [l.strip() for l in f.readlines() if l.strip()]
    
    grafo = {}
    terminais = []
    n = 0
    m = 0
    k = 0

    start_idx = 1 # Pula DIMACS2

    for i in range(start_idx, len(lines)):
        parts = lines[i].split()
        
        if parts[0] == 'p':
            n = int(parts[2])
            m = int(parts[3])
            
        elif parts[0] == 'e':
            u = int(parts[1])
            v = int(parts[2])
            cost = float(parts[3])
            
            if u not in grafo: grafo[u] = []
            if v not in grafo: grafo[v] = []
            grafo[u].append((v, cost))
            grafo[v].append((u, cost))
            
        else:
            k = int(parts[0])
            terminais = [int(t) for t in parts[1:]]

    return grafo, terminais, n, m, k

# Lê o arquivo de métricas gerais da instância (mostra número de nós, terminais e arestas ) e parâmetros do NSBRKGA
#Transforma as linhas do arquivo em um dicionário chave-valor
def ler_statistics(path):
    stats = {}
    if not os.path.exists(path):
        return stats

    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            if ":" in line:
                key, val = line.split(":", 1)
                stats[key.strip()] = val.strip()
    return stats


# Lê a fronteira de Pareto correspondete à instância (dada a seed corrente)
# O arquivo contem as soluções encontradas (valores das funções objetivo) nas linhas iniciais. Nas linhas seguintes tem blocos com as componentes formadas em cada solução, iniciando cada um com "Componentes da Solução"

def ler_pareto(path):
    if not os.path.exists(path):
        print(f"[ERRO] Arquivo pareto não encontrado: {path}")
        return [], []

    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    #Separa os blocos com as componentes formadas em cada solução da fronteira
    blocks = content.split("Componentes da solução:")
    
    #Linhas inicias guardam as soluções encontradas
    header_lines = blocks[0].strip().split('\n')
    expected_costs = []
    for line in header_lines:
        line = line.strip()
        if not line: continue
        try:
            parts = line.split()
            c1 = float(parts[0])
            c2 = float(parts[1])
            expected_costs.append((c1, c2))
        except ValueError:
            continue 
    
    msg_erro = []
    for ec1 in expected_costs:
        for ec2 in expected_costs:
            if ec1[0] == ec2[0] and ec1[1] == ec2[1]:
                continue
            if ec1[0] < ec2[0] and ec1[1] <= ec2[1] or ec1[0] <= ec2[0] and ec1[1] < ec2[1]:
                msg_erro.append(f"{ec2} é dominado por {ec1}\n")


    solutions_components = []

    for block in blocks[1:]:
        comp_dict = {}
        lines = block.strip().split('\n')
        for line in lines:
            line = line.strip()
            if "=" in line:
                comp_str, nodes_str = line.split("=")
                comp_id = int(comp_str.strip())
                
                nodes_clean = nodes_str.replace("{", "").replace("}", "").strip()
                if nodes_clean:
                    nodes = [int(x) for x in nodes_clean.split()]
                else:
                    nodes = [] 
                
                comp_dict[comp_id] = nodes
        
        if comp_dict:
            solutions_components.append(comp_dict)

    return expected_costs, solutions_components, msg_erro

def verificar_solucao(grafo, terminais, n, k, componentes):
    msg_erro = []

    set_terminais = set(terminais)

    for comp_id, nodes in componentes.items():
        #Verifica se tem mais de um terminal na componente
        qtd_terminais_componente = 0
        for node in nodes:
            if node in set_terminais:
                qtd_terminais_componente += 1
        
        if qtd_terminais_componente > 1:
            msg_erro.append(f"Componente {comp_id} inválida: possui {qtd_terminais_componente} terminais (permitido: 1)")
        
        if qtd_terminais_componente == 0:
            msg_erro.append(f"Componente {comp_id} inválida: não possui nenhum terminal")
        
        #Verifica se a componente possui o terminal esperado (terminais atribuídos às componentes na ordem da lista na instância)
        term_esperado = terminais[comp_id]
        if term_esperado not in nodes:
            msg_erro.append(f"Componente {comp_id} incorreta: deveria conter o terminal {term_esperado}")
        
    # Verificar partição
    todos_nos = []
    for nodes in componentes.values():
        todos_nos.extend(nodes)
    
    if len(todos_nos) != n:
        msg_erro.append(f"Número de nós na solução ({len(todos_nos)}) difere de N ({n})")
    
    if len(todos_nos) != len(set(todos_nos)):
        msg_erro.append("Existem nós duplicados em componentes diferentes")
    
    if msg_erro:
        return False, -1, -1, msg_erro


    #Cada nó é marcado com o id de sua componente
    node_colors = [-1] * n
    for comp_id, nodes in componentes.items():
        for node in nodes:
            if node < n:
                node_colors[node] = comp_id
            else:
                msg_erro.append(f"Nó {node} fora dos limites 0-{n-1}")
                return False, -1, -1, msg_erro

   
    # Recalcular Custos
    cut_cost = 0.0
    for u in range(n):
        if u not in grafo: continue
        color_u = node_colors[u]
        for v, w in grafo[u]:
            if u < v: #Não soma o custo duas vezes -> Guarda o cutso de (1,5) e não de (5,1)
                color_v = node_colors[v] #cor do vizinho
                if color_u != color_v:
                    cut_cost += w

    sizes = [len(componentes[c]) for c in sorted(componentes.keys())]
    if not sizes: sizes = [0]
    
    maxV = max(sizes)
    balanceamentoPerfeito = math.ceil(n / k)
    fator_maxV_balPerfeito = maxV / balanceamentoPerfeito

    return True, cut_cost, fator_maxV_balPerfeito, ["OK"]

def main():
    print("=== INICIANDO VERIFICAÇÃO BMCP ===")
    print(f"Raiz: {ROOT_DIR}")
    
    pareto_files = glob.glob(os.path.join(PARETO_DIR, f"*{EXTENSION_PARETO}"))
    
    total_files = 0
    total_solutions = 0
    total_correct = 0
    solucoes_obtidas_stats = 0
    
    arquivos_com_erro = []

    for p_file in pareto_files:
        filename = os.path.basename(p_file) 
        
        # --- FILTRO DE ARQUIVOS DE FRONTEIRA DE PARETO DE REFERÊNCIA   E ARQUIVOS DE FRONTEIRA BEST E MEDIAN---
        parts_filname = filename.split("_")
        
        if len(parts_filname) == 4:
             if DEBUG > 0:
                print(f"[INFO] Ignorando arquivo da fronteira de Pareto de  referência: {filename}")
             continue
        
        if parts_filname[-1] == "best.txt" or parts_filname[-1] == "median.txt" or parts_filname[-1] == "cplex.txt":
            if DEBUG > 0 :
                print(f"[INFO] Ignorando arquivo de best ou median ou do cplex {filename}")
            continue
        
        has_error = False 
        total_files += 1

        
        # --- EXTRAÇÃO DO NOME DA INSTÂNCIA ---
        try:
            base_filename = os.path.splitext(filename)[0] 
            
            if "_nsbrkga" in base_filename:
                instance_name_raw = base_filename.split("_nsbrkga")[0]
            else:
                parts = base_filename.split("_")
                if len(parts) > 1 and parts[-1].isdigit():
                    instance_name_raw = "_".join(parts[:-1])
                else:
                    instance_name_raw = base_filename
            
        except Exception as e:
            print(f"[SKIP] Erro ao processar nome: {filename}. {e}")
            arquivos_com_erro.append(os.path.abspath(p_file))
            continue

        found_instance_path = None
        
        suffixes_to_try = ["", "_1", "_2", "_3"]
        
        for suf in suffixes_to_try:
            nome_teste = f"{instance_name_raw}{suf}{EXTENSION_INSTANCE}"
            caminho_teste = os.path.join(INSTANCES_DIR, nome_teste)
            
            if os.path.exists(caminho_teste):
                found_instance_path = caminho_teste
                break # Encontrou para o loop.
        
        if not found_instance_path:
            print(f"   [ERRO CRÍTICO] Instância não encontrada (tentado sufixos _1 a _3): {instance_name_raw}*.gr")
            # Armazena CAMINHO COMPLETO no erro
            arquivos_com_erro.append(os.path.abspath(p_file))
            continue
            
        stats_path = os.path.join(STATS_DIR, filename) 

        if DEBUG > 0:
            print(f"\n>> Processando: {filename}")
            print(f"   Instância detectada: {os.path.basename(found_instance_path)}")

        # Carrega Dados da Instância Encontrada
        inst_data = ler_instancia(found_instance_path)
        
        if not inst_data: 
            print(f"   [ERRO LEITURA] Falha ao ler instância: {found_instance_path}")
            arquivos_com_erro.append(os.path.abspath(p_file))
            continue
            
        grafo, terminais, n, m, k = inst_data
        stats_data = ler_statistics(stats_path)
        
        # Validar dados do arquivo de statistics
        if stats_data:
            stats_n = int(stats_data.get("Number of vertices", -1))
            stats_k = int(stats_data.get("Number of terminals", -1))
            stats_solving_time = float(stats_data.get("Solving time",-1))
            solucoes_obtidas_stats += int(stats_data['Solutions obtained'])
            
            if stats_n != -1 and (stats_n != n or stats_k != k):
                print(f"   [ALERTA] Divergência Stats vs Instância. N({stats_n}vs{n}), K({stats_k}vs{k})")
                has_error = True

            if stats_solving_time > (time_limit + 0.5):
                print(f"arquivo {filename} superou o tempo limite de execução : solving time = {stats_solving_time} | time limit : {time_limit}")
                has_error = True

        # Valida Soluções
        exp_costs, solutions, msg = ler_pareto(p_file)
        if len(msg) > 0:
            has_error = True
            print(f"   [FALHA] Falha de dominância. {msg} ({filename})")
        
        if len(exp_costs) != len(solutions):
            print(f"   [ERRO] Cabeçalho ({len(exp_costs)}) vs Componentes ({len(solutions)})")
            has_error = True
            limit = min(len(exp_costs), len(solutions))
        else:
            limit = len(solutions)

        if limit == 0:
             print("   [AVISO] Nenhuma solução encontrada no arquivo.")
        
        for i in range(limit):
            total_solutions += 1
            rep_c1, rep_c2 = exp_costs[i]
            comps = solutions[i]
            
            valid, calc_c1, calc_c2, msgs = verificar_solucao(grafo, terminais, n, k, comps)
            
            if not valid:
                print(f"   [FALHA] Solução {i}: Inválida estruturalmente. {msgs}")
                has_error = True
                continue

            match_c1 = math.isclose(rep_c1, calc_c1, abs_tol=1e-2)
            match_c2 = math.isclose(rep_c2, calc_c2, abs_tol=1e-3)
            
            if match_c1 and match_c2:
                total_correct += 1
                if DEBUG > 1: print(f"   [OK] Solução {i} validada.")
            else:
                print(f"   [ERRO DADOS] Solução {i} Divergência:")
                print(f"          Reportado : Cut={rep_c1}, Bal={rep_c2}")
                print(f"          Calculado : Cut={calc_c1}, Bal={calc_c2}")
                has_error = True

    
        if solucoes_obtidas_stats != total_solutions:
                print(f"   [ALERTA] Divergência Stats vs Verificador. Soluções obtidas verificador({total_solutions})vs soluções obtidas stats({solucoes_obtidas_stats})")

        if has_error:
            # Armazena CAMINHO COMPLETO
            arquivos_com_erro.append(os.path.abspath(p_file))

            
    
    # =========================================================
    # RELATÓRIO FINAL
    # =========================================================
    print("\n" + "="*50)
    print("RESUMO FINAL DA VERIFICAÇÃO")
    print("="*50)
    print(f"Arquivos Processados: {total_files}")
    print(f"Soluções Verificadas: {total_solutions}")
    print(f"Soluções Corretas   : {total_correct}")
    
    if total_solutions > 0:
        acc = (total_correct/total_solutions)*100
        print(f"Acurácia Geral      : {acc:.2f}%")
    
    print("-" * 50)
    if len(arquivos_com_erro) > 0:
        print(f"Foram encontrados erros em {len(arquivos_com_erro)} arquivos:")
        for arq in arquivos_com_erro:
            print(f" -> {arq}")
    else:
        print("Nenhum erro encontrado! Todos os arquivos estão consistentes.")
    print("="*50)

if __name__ == "__main__":
    main()