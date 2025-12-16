#!/bin/bash

instances=(kroAB100 kroAB200)
solvers=(nsbrkga)
seeds=(305089489 511812191 608055156)
versions=(best median)

num_processes=1

time_limit=15
max_num_solutions=500
max_num_snapshots=30
max_ref_solutions=800

path=$(dirname $(realpath $0))

mkdir -p ${path}/statistics
# mkdir -p ${path}/solutions
mkdir -p ${path}/pareto
mkdir -p ${path}/best_solutions_snapshots
mkdir -p ${path}/num_non_dominated_snapshots
mkdir -p ${path}/num_fronts_snapshots
mkdir -p ${path}/populations_snapshots
mkdir -p ${path}/num_elites_snapshots
mkdir -p ${path}/hypervolume
mkdir -p ${path}/hypervolume_snapshots
mkdir -p ${path}/igd_plus
mkdir -p ${path}/igd_plus_snapshots
mkdir -p ${path}/multiplicative_epsilon
mkdir -p ${path}/multiplicative_epsilon_snapshots
mkdir -p ${path}/metrics
mkdir -p ${path}/metrics_snapshots

# ==============================================================================
# 1. EXECUÇÃO DOS SOLVERS
# ==============================================================================
commands=()
for ((i=0;i<num_processes;i++)); do commands[$i]="("; done
i=0

for instance in ${instances[@]}
do
    for solver in ${solvers[@]}
    do
        for seed in ${seeds[@]}
        do
            command="${path}/bin/exec/${solver}_solver_exec "
            command+="--instance ${path}/instances/${instance}.txt "
            command+="--seed ${seed} "
            command+="--time-limit ${time_limit} "
            command+="--max-num-solutions ${max_num_solutions} "
            command+="--max-num-snapshots ${max_num_snapshots} "
            command+="--statistics ${path}/statistics/${instance}_${solver}_${seed}.txt "
            command+="--pareto ${path}/pareto/${instance}_${solver}_${seed}.txt "
            command+="--best-solutions-snapshots ${path}/best_solutions_snapshots/${instance}_${solver}_${seed}_ "
            command+="--num-non-dominated-snapshots ${path}/num_non_dominated_snapshots/${instance}_${solver}_${seed}.txt "
            command+="--num-fronts-snapshots ${path}/num_fronts_snapshots/${instance}_${solver}_${seed}.txt "
            command+="--populations-snapshots ${path}/populations_snapshots/${instance}_${solver}_${seed}_ "
            
            if [ $solver = "nspso" ]; then command+="--memory "; fi
            if [ $solver = "moead" ]; then command+="--preserve-diversity "; fi
            if [ $solver = "mhaco" ]; then command+="--memory "; fi
            if [ $solver = "nsbrkga" ]; then
                command+="--num-elites-snapshots ${path}/num_elites_snapshots/${instance}_${solver}_${seed}.txt "
            fi
            
            if [ $i -lt $num_processes ]; then commands[$i]+="$command"; else commands[$((i%num_processes))]+=" && $command"; fi
            i=$((i+1))
        done
    done
done

for ((i=0;i<num_processes;i++)); do commands[$i]+=") &> ${path}/log_${i}.txt"; done
final_command=""
for ((i=0;i<num_processes;i++)); do command=${commands[$i]}; final_command+="$command & "; done
eval $final_command
wait

# ==============================================================================
# 2. CÁLCULO DA FRONTEIRA DE REFERÊNCIA
# ==============================================================================
commands=()
for ((i=0;i<num_processes;i++)); do commands[$i]="("; done
i=0

for instance in ${instances[@]}
do
    command="${path}/bin/exec/reference_pareto_front_calculator_exec "
    command+="--instance ${path}/instances/${instance}.txt "
    command+="--max-num-solutions ${max_ref_solutions} "
    j=0;
    for solver in ${solvers[@]}
    do
        for seed in ${seeds[@]}
        do
            command+="--pareto-${j} ${path}/pareto/${instance}_${solver}_${seed}.txt "
            command+="--best-solutions-snapshots-${j} ${path}/best_solutions_snapshots/${instance}_${solver}_${seed}_ "
            command+="--reference-pareto ${path}/pareto/${instance}.txt "
            j=$((j+1))
        done
    done
    if [ $i -lt $num_processes ]; then commands[$i]+="$command"; else commands[$((i%num_processes))]+=" && $command"; fi
    i=$((i+1))
done

for ((i=0;i<num_processes;i++)); do commands[$i]+=") &>> ${path}/log_${i}.txt"; done
final_command=""
for ((i=0;i<num_processes;i++)); do command=${commands[$i]}; final_command+="$command & "; done
eval $final_command
wait

# ==============================================================================
# 3. CÁLCULO DO HIPERVOLUME 
# ==============================================================================
commands=()
for ((i=0;i<num_processes;i++)); do commands[$i]="("; done
i=0

for instance in ${instances[@]}
do
    command="${path}/bin/exec/hypervolume_calculator_exec "
    command+="--instance ${path}/instances/${instance}.txt "
    command+="--reference-pareto ${path}/pareto/${instance}.txt "
    j=0;
    for solver in ${solvers[@]}
    do
        for seed in ${seeds[@]}
        do
            command+="--pareto-${j} ${path}/pareto/${instance}_${solver}_${seed}.txt "
            command+="--best-solutions-snapshots-${j} ${path}/best_solutions_snapshots/${instance}_${solver}_${seed}_ "
            command+="--hypervolume-${j} ${path}/hypervolume/${instance}_${solver}_${seed}.txt "
            command+="--hypervolume-snapshots-${j} ${path}/hypervolume_snapshots/${instance}_${solver}_${seed}.txt "
            j=$((j+1))
        done
    done
    if [ $i -lt $num_processes ]; then commands[$i]+="$command"; else commands[$((i%num_processes))]+=" && $command"; fi
    i=$((i+1))
done

for ((i=0;i<num_processes;i++)); do commands[$i]+=") &>> ${path}/log_${i}.txt"; done
final_command=""
for ((i=0;i<num_processes;i++)); do command=${commands[$i]}; final_command+="$command & "; done
eval $final_command
wait

# ==============================================================================
# 4. CÁLCULO DE IGD+ e EPSILON (REMOVIDOS/COMENTADOS)
# ==============================================================================

# ==============================================================================
# 5. AGREGAÇÃO DE RESULTADOS (Best/Median)
# ==============================================================================
commands=()
for ((i=0;i<num_processes;i++)); do commands[$i]="("; done
i=0

for instance in ${instances[@]}
do
    for solver in ${solvers[@]}
    do
        command="${path}/bin/exec/results_aggregator_exec "
        
        # --- APENAS Métricas Calculadas (Hypervolume) ---
        command+="--hypervolumes ${path}/hypervolume/${instance}_${solver}.txt "
        command+="--hypervolume-statistics ${path}/hypervolume/${instance}_${solver}_stats.txt "
        
       
        # --- Saídas Desejadas ---
        command+="--statistics-best ${path}/statistics/${instance}_${solver}_best.txt "
        command+="--statistics-median ${path}/statistics/${instance}_${solver}_median.txt "
        command+="--pareto-best ${path}/pareto/${instance}_${solver}_best.txt "
        command+="--pareto-median ${path}/pareto/${instance}_${solver}_median.txt "
        command+="--hypervolume-snapshots-best ${path}/hypervolume_snapshots/${instance}_${solver}_best.txt "
        command+="--hypervolume-snapshots-median ${path}/hypervolume_snapshots/${instance}_${solver}_median.txt "
        command+="--best-solutions-snapshots-best ${path}/best_solutions_snapshots/${instance}_${solver}_best_ "
        command+="--best-solutions-snapshots-median ${path}/best_solutions_snapshots/${instance}_${solver}_median_ "
        command+="--num-non-dominated-snapshots-best ${path}/num_non_dominated_snapshots/${instance}_${solver}_best.txt "
        command+="--num-non-dominated-snapshots-median ${path}/num_non_dominated_snapshots/${instance}_${solver}_median.txt "
        command+="--populations-snapshots-best ${path}/populations_snapshots/${instance}_${solver}_best_ "
        command+="--populations-snapshots-median ${path}/populations_snapshots/${instance}_${solver}_median_ "
        command+="--num-fronts-snapshots-best ${path}/num_fronts_snapshots/${instance}_${solver}_best.txt "
        command+="--num-fronts-snapshots-median ${path}/num_fronts_snapshots/${instance}_${solver}_median.txt "
        
        if [ $solver = "nsbrkga" ]
        then
            command+="--num-elites-snapshots-best ${path}/num_elites_snapshots/${instance}_${solver}_best.txt "
            command+="--num-elites-snapshots-median ${path}/num_elites_snapshots/${instance}_${solver}_median.txt "
        fi
        
        j=0;
        for seed in ${seeds[@]}
        do
            # --- Inputs de cada seed---
            command+="--statistics-${j} ${path}/statistics/${instance}_${solver}_${seed}.txt "
            command+="--pareto-${j} ${path}/pareto/${instance}_${solver}_${seed}.txt "
            command+="--hypervolume-${j} ${path}/hypervolume/${instance}_${solver}_${seed}.txt "
            command+="--hypervolume-snapshots-${j} ${path}/hypervolume_snapshots/${instance}_${solver}_${seed}.txt "
            
            command+="--best-solutions-snapshots-${j} ${path}/best_solutions_snapshots/${instance}_${solver}_${seed}_ "
            command+="--num-non-dominated-snapshots-${j} ${path}/num_non_dominated_snapshots/${instance}_${solver}_${seed}.txt "
            command+="--populations-snapshots-${j} ${path}/populations_snapshots/${instance}_${solver}_${seed}_ "
            command+="--num-fronts-snapshots-${j} ${path}/num_fronts_snapshots/${instance}_${solver}_${seed}.txt "
            
            if [ $solver = "nsbrkga" ]
            then
                command+="--num-elites-snapshots-${j} ${path}/num_elites_snapshots/${instance}_${solver}_${seed}.txt "
            fi
            j=$((j+1))
        done
        
        if [ $i -lt $num_processes ]; then commands[$i]+="$command"; else commands[$((i%num_processes))]+=" && $command"; fi
        i=$((i+1))
    done
done

for ((i=0;i<num_processes;i++)); do commands[$i]+=") &>> ${path}/log_${i}.txt"; done
final_command=""
for ((i=0;i<num_processes;i++)); do command=${commands[$i]}; final_command+="$command & "; done
eval $final_command

wait
#python3 ${path}/plotter_hypervolume.py &
python3 ${path}/plotter_pareto.py 

wait

