import csv
import matplotlib.pyplot as plt
import os
import seaborn as sns
from plotter_definitions import *

"""
    Para os solvers com mais de uma execução (que possuem seeds): para cada combinação de instance_solver temos um arquivo pareto/instance_solver_best.txt que guarda a melhor fronteira encontrada (com base no HVR, ou seja, gurada a fronteira que obteve o melhor HVR) e um arquivo pareto/instance_solver_median.txt, que guarda a fronteira que obteve o HVR mediano.
    Para o método exato (sem seed) que possui uma única fronteira para cada instância, não temos arquivos best e median.

"""

#Gráficos gerados vão para a pasta /pareto
dirname = os.path.dirname(__file__)

#Para cada instância, varre as fronteiras best e median (de maior HV e HV mediano, respectivamente) encontradas por cada solver -> armazena min_ys[0] = menor_corte_encontrado_global | min_ys[1] = menor balanceamento_encontrado_global , max_ys[0] = maior_corte_encontrado_global e max_ys[1] = maior_balanceamento_encontrado_global
#Para o método exato, best e median se referem à unica fronteira encontrada
for m in ms:
    for instance in instances_per_m[m]:
        for version in versions:
            min_ys = []
            max_ys = []
            for i in range(m):
                min_ys.append(-1)
                max_ys.append(-1)
            for solver in solvers:
                #Se solver tem seeds -> mais de uma execução para a mesma instância -> possui arquivos pareto_best e pareto_median
                if(solver not in solvers_without_seed):
                    filename = os.path.join(dirname, "pareto/" + instance + "_" + solver + "_" + version + ".txt")
                else: #método exato só tem uma execução por instância
                    filename = os.path.join(dirname, "pareto/" + instance + "_" + solver + ".txt")
                    
                if os.path.exists(filename):
                    with open(filename) as csv_file:
                        data = csv.reader(csv_file, delimiter=" ")
                        for row in data:
                            row = [col for col in row if col.strip()] #remove colunas vazias
                            if row:
                                try:
                                    float(row[0])
                                    #Tenta converter a primeira col p float, se falhar é uma linha que guarda informações das componentes
                                    for i in range(m):
                                        if min_ys[i] == -1 or min_ys[i] > float(row[i]):
                                            min_ys[i] = float(row[i])
                                        if max_ys[i] == -1 or max_ys[i] < float(row[i]):
                                            max_ys[i] = float(row[i])
                                except ValueError:
                                    break #Encontrou linhas de texto, terminou de processar soluções da fronteira
                        csv_file.close()

                    #print(filename)
                    #print(f"min_ys[0] = {min_ys[0]} | min_ys[1] = {min_ys[1]}")
                    #print(f"max_ys[0] = {max_ys[0]} | max_ys[1] = {max_ys[1]}")
                                
            for i in range(m):
                delta_y = max_ys[i] - min_ys[i]
                min_ys[i] = min_ys[i] - round(0.025 * delta_y)
                max_ys[i] = max_ys[i] + round(0.025 * delta_y)
            fig, axs = plt.subplots(nrows = m, ncols = m, figsize = (5.0 * m, 5.0 * m), squeeze = False, num = 1, clear = True)
            fig.set_size_inches(5.0 * m, 5.0 * m)
            fig.suptitle(instance, fontsize = "xx-large")
            for i in range(len(solvers)):
                if(solvers[i] not in solvers_without_seed):
                    filename = os.path.join(dirname, "pareto/" + instance + "_" + solvers[i] + "_" + version + ".txt")
                else: #método exato só tem uma execução por instância
                    filename = os.path.join(dirname, "pareto/" + instance + "_" + solvers[i] + ".txt")
                if os.path.exists(filename):
                    ys = [] # Valores das funções objetivo
                    for j in range(m):
                        ys.append([])
                    #print(f"solver : {solvers[i]} | filename {filename}")
                    with open(filename) as csv_file:
                        data = csv.reader(csv_file, delimiter = " ")
                        for row in data:
                            row = [col for col in row if col.strip()] #remove colunas vazias
                            if row:
                                try:
                                    float(row[0])
                                    for j in range(m):
                                        ys[j].append(float(row[j]))
                                except ValueError:
                                    break
                        #print(ys)
                        csv_file.close()

                    for j in range(m):
                        axs[j][j].set_xlim(left = min_ys[j], right = max_ys[j])
                        axs[j][j].set_xlabel(xlabel = "$f_{" + str(j + 1) + "}$", fontsize = "x-large")
                        axs[j][j].set_yticks([])
                        axs[j][j].set_ylabel(ylabel = "Densidade", fontsize = "x-large")
                        sns.kdeplot(data = ys[j], ax = axs[j][j], color = colors[i], label = solver_labels[solvers[i]], marker = (i + 3, 2, 0), alpha = 0.80)
                        axs[j][j].legend(loc = "best")
                        for l in range(m):
                            if j != l:
                                axs[j][l].set_xlim(left = min_ys[l], right = max_ys[l])
                                axs[j][l].set_ylim(bottom = min_ys[j], top = max_ys[j])
                                axs[j][l].set_xlabel(xlabel = "$f_{" + str(l + 1) + "}$", fontsize = "x-large")
                                axs[j][l].set_ylabel(ylabel = "$f_{" + str(j + 1) + "}$", fontsize = "x-large")
                                axs[j][l].scatter(x = ys[l], y = ys[j], color = colors[i], label = solver_labels[solvers[i]], marker = (i + 3, 2, 0), alpha = 0.80)
                                axs[j][l].legend(loc = "best", fontsize = "small" )
                    del ys
            plt.subplots_adjust(wspace = 0.16 + 0.07 * m, hspace = 0.16 + 0.07 * m)
            filename = os.path.join(dirname, "pareto/" + instance + "_" + version + ".png")
            plt.savefig(filename, format = "png")