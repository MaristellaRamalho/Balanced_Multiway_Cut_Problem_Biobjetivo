instances = ["N160_M4N_K20_1", "N160_M8N_K40_1", "N320_M8N_K40_1" ,"N320_M8N_K80_1", "N640_M8N_K40_1", "N640_M8N_K80_1"]
solvers = ["nsbrkga"]
solver_labels = {"nsga2": "NSGA-II",
                 "nspso": "NSPSO",
                 "moead": "MOEA/D-DE",
                 "mhaco": "MHACO",
                 "ihs": "IHS",
                 "nsbrkga": "NS-BRKGA"}
seeds = [1089661,1602347,1644410]
versions = ["best", "median"]
colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf", "#8c7e6e", "#738191"]
colors2 = ["#103c5a", "#804007", "#165016", "#6b1414", "#4a345f", "#462b26", "#723c61", "#404040", "#5e5f11", "#0c5f68", "#463f37", "#3a4149"]
ms = [2]
instances_per_m = {2 : ["N160_M4N_K20_1", "N160_M8N_K40_1", "N320_M8N_K40_1" ,"N320_M8N_K80_1", "N640_M8N_K40_1", "N640_M8N_K80_1"]}
m_per_instance = {"N160_M4N_K20_1"   : 2, "N160_M8N_K40_1"   : 2, "N320_M8N_K40_1"   : 2, "N320_M8N_K80_1"   : 2,"N640_M8N_K40_1"   : 2,"N640_M8N_K80_1"   : 2}
sizes = [160, 320, 640]
instances_per_size = {160  : ["N160_M4N_K20_1", "N160_M8N_K40_1"],
                      320  : ["N320_M8N_K40_1" ,"N320_M8N_K80_1"],
                      640 :   ["N640_M8N_K40_1", "N640_M8N_K80_1"]
                    }
size_per_instance = {"N160_M4N_K20_1"   : 160, "N160_M8N_K40_1"   : 160, "N320_M8N_K40_1"   : 320, "N320_M8N_K80_1"   : 320,"N640_M8N_K40_1"   : 640,"N640_M8N_K80_1"   : 640}
num_snapshots = 30