instances = ["kroAB100",   "kroAB200"]
solvers = ["nsbrkga"]
solver_labels = {"nsga2": "NSGA-II",
                 "nspso": "NSPSO",
                 "moead": "MOEA/D-DE",
                 "mhaco": "MHACO",
                 "ihs": "IHS",
                 "nsbrkga": "NS-BRKGA"}
seeds = [305089489, 511812191, 608055156]
versions = ["best", "median"]
colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf", "#8c7e6e", "#738191"]
colors2 = ["#103c5a", "#804007", "#165016", "#6b1414", "#4a345f", "#462b26", "#723c61", "#404040", "#5e5f11", "#0c5f68", "#463f37", "#3a4149"]
ms = [2]
instances_per_m = {2 : ["kroAB100",   "kroAB200"]}
m_per_instance = {"kroAB100"   : 2, "kroAB200"   : 2}
sizes = [100, 200]
instances_per_size = {100  : ["kroAB100"],
                      200  : ["kroAB200"],
                    }
size_per_instance = {"kroAB100"   : 100, "kroAB200"   : 200}
num_snapshots = 30