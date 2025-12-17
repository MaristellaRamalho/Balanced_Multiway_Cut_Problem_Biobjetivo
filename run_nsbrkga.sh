#!/bin/bash

instances=(N640_M8N_K80_3)
solvers=(nsbrkga)
seeds=(1089661 1602347 1644410)
versions=(best median)

num_processes=1

time_limit=16
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
            command+="--instance ${path}/instances/${instance}.gr "
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

