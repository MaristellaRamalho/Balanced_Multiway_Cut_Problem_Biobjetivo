'''
  Verifica os resultados obtidos 
'''

import os
from os.path import isfile, join
import math
import numpy as np
import glob

ROOT_DIR = "/mnt/c/Users/maris/OneDrive/Documentos/bmcp_biobjetivo"
INSTANCES_DIR = os.path.join(ROOT_DIR, "instances")
PARETO_DIR = os.path.join(ROOT_DIR, "pareto")
STATS_DIR = os.path.join(ROOT_DIR, "statistics")

EXTENSION_INSTANCE = ".gr"
EXTENSION_PARETO = ".txt"
EXTENSION_STATS = ".txt"

DEBUG = 0

def ler_instancia(path):
    """
    Lê o arquivo .gr da pasta instances.
    """
    # A verificação de existência agora é feita antes de chamar esta função,
    # mas mantemos aqui por segurança.
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


def ler_pareto(path):
    if not os.path.exists(path):
        print(f"[ERRO] Arquivo pareto não encontrado: {path}")
        return [], []

    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    blocks = content.split("Componentes da solução:")
    
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

    solutions_components = []

    for block in blocks[1:]:
        comp_dict = {}
        lines = block.strip().split('\n')
        for line in lines:
            line = line.strip()
            if "=" in line:
                cid_str, nodes_str = line.split("=")
                cid = int(cid_str.strip())
                
                nodes_clean = nodes_str.replace("{", "").replace("}", "").strip()
                if nodes_clean:
                    nodes = [int(x) for x in nodes_clean.split()]
                else:
                    nodes = [] 
                
                comp_dict[cid] = nodes
        
        if comp_dict:
            solutions_components.append(comp_dict)

    return expected_costs, solutions_components

def verificar_solucao(grafo, terminais, n, k, componentes):
    msg_erro = []
    
    # Verificar Terminais
    for i in range(k):
        term_esperado = terminais[i]
        if i not in componentes:
            msg_erro.append(f"Componente {i} inexistente")
            continue
        
        if term_esperado not in componentes[i]:
            msg_erro.append(f"Componente {i} não contém terminal {term_esperado}")
        
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

    # Recalcular Custos
    node_colors = [-1] * n
    for cid, nodes in componentes.items():
        for node in nodes:
            if node < n:
                node_colors[node] = cid
            else:
                msg_erro.append(f"Nó {node} fora dos limites 0-{n-1}")
                return False, -1, -1, msg_erro

    cut_cost = 0.0
    for u in range(n):
        if u not in grafo: continue
        color_u = node_colors[u]
        for v, w in grafo[u]:
            if u < v: 
                color_v = node_colors[v]
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
        
        # --- FILTRO DE ARQUIVOS DE REFERÊNCIA ---
        # Se o arquivo não tiver "_" ou parecer ser um arquivo de referência, pula
        # Ajuste esta condição conforme o padrão dos seus arquivos de referência
        # Exemplo: se o arquivo termina exatamente com _1.txt mas não tem o nome do algoritmo
        parts_filname = filename.split("_")
        
        if len(parts_filname) == 4:
             print(f"[INFO] Ignorando arquivo da fronteira de  referência: {filename}")
             continue
        
        if parts_filname[-1] == "best.txt" or parts_filname[-1] == "median.txt":
            print(f"[INFO] Ignorando arquivo de best ou median {filename}")
            continue
        
        has_error = False 
        total_files += 1

        
        # --- EXTRAÇÃO DO NOME DA INSTÂNCIA ---
        try:
            base_filename = os.path.splitext(filename)[0] 
            
            if "_nsbrkga" in base_filename:
                instance_name_raw = base_filename.split("_nsbrkga")[0]
            else:
                # Lógica conservadora para arquivos sem tag do algoritmo
                parts = base_filename.split("_")
                if len(parts) > 1 and parts[-1].isdigit():
                    instance_name_raw = "_".join(parts[:-1])
                else:
                    instance_name_raw = base_filename
            
        except Exception as e:
            print(f"[SKIP] Erro ao processar nome: {filename}. {e}")
            arquivos_com_erro.append(os.path.abspath(p_file))
            continue

        # --- BUSCA INTELIGENTE POR SUFIXOS (_1, _2, _3) ---
        found_instance_path = None
        
        # Lista de tentativas: nome exato, depois com _1, _2, _3
        suffixes_to_try = ["", "_1", "_2", "_3"]
        
        for suf in suffixes_to_try:
            nome_teste = f"{instance_name_raw}{suf}{EXTENSION_INSTANCE}"
            caminho_teste = os.path.join(INSTANCES_DIR, nome_teste)
            
            if os.path.exists(caminho_teste):
                found_instance_path = caminho_teste
                break # Encontrou! Para o loop.
        
        if not found_instance_path:
            # Se saiu do loop sem encontrar nada
            print(f"   [ERRO CRÍTICO] Instância não encontrada (tentado sufixos _1 a _3): {instance_name_raw}*.gr")
            # Armazena CAMINHO COMPLETO no erro
            arquivos_com_erro.append(os.path.abspath(p_file))
            continue
            
        stats_path = os.path.join(STATS_DIR, filename) 

        if DEBUG > 0:
            print(f"\n>> Processando: {filename}")
            print(f"   Instância detectada: {os.path.basename(found_instance_path)}")

        # 1. Carregar Dados da Instância Encontrada
        inst_data = ler_instancia(found_instance_path)
        
        if not inst_data: 
            # Caso raro onde exists retorna true mas leitura falha
            print(f"   [ERRO LEITURA] Falha ao ler instância: {found_instance_path}")
            arquivos_com_erro.append(os.path.abspath(p_file))
            continue
            
        grafo, terminais, n, m, k = inst_data
        stats_data = ler_statistics(stats_path)
        
        # 2. Validar Estatísticas
        if stats_data:
            stats_n = int(stats_data.get("Number of vertices", -1))
            stats_k = int(stats_data.get("Number of terminals", -1))
            solucoes_obtidas_stats += int(stats_data['Solutions obtained'])
            
            if stats_n != -1 and (stats_n != n or stats_k != k):
                print(f"   [ALERTA] Divergência Stats vs Instância. N({stats_n}vs{n}), K({stats_k}vs{k})")
                has_error = True

        # 3. Validar Soluções
        exp_costs, solutions = ler_pareto(p_file)
        
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
        print(f"Foram encontrados erros em {len(arquivos_com_erro)} arquivos (Caminhos Completos):")
        for arq in arquivos_com_erro:
            print(f" -> {arq}")
    else:
        print("Nenhum erro encontrado! Todos os arquivos estão consistentes.")
    print("="*50)

if __name__ == "__main__":
    main()