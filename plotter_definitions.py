instances = ["N160_M2N_K10_1", "N160_M2N_K10_2", "N160_M2N_K10_3",
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
    "N640_M8N_K80_1", "N640_M8N_K80_2", "N640_M8N_K80_3"]

solvers =  ["nsbrkgaColoracaoMax", "nsbrkgaColoracaoQuad", "nsbrkgaKruskalMax", "nsbrkgaKruskalQuad", "cplex"]

#Separando solvers com seed -> nsbrkga e solvers sem seed -> método exato
solvers_with_seed = [s for s in solvers if s != "cplex"]
solvers_without_seed = ["cplex"]

solver_labels = {"nsbrkgaColoracaoMax": "NS-BRKGA_Coloracao_Max",
                 "nsbrkgaColoracaoQuad": "NS-BRKGA_Coloracao_Quad",
                 "nsbrkgaKruskalMax": "NS-BRKGA_Kruskal_Max",
                 "nsbrkgaKruskalQuad": "NS-BRKGA_Kruskal_Quad",
                 "cplex": "CPLEX"}

seeds = [1089661, 1602347, 1644410]

versions = ["best", "median"]

colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]
colors2 = ["#103c5a", "#804007", "#165016", "#6b1414", "#4a345f"]

ms = [2]
instances_per_m = {2 : ["N160_M2N_K10_1", "N160_M2N_K10_2", "N160_M2N_K10_3",
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
    "N640_M8N_K80_1", "N640_M8N_K80_2", "N640_M8N_K80_3"]}

m_per_instance = {instance: 2 for instance in instances} #todas as instancias tem 2 objetivos

sizes = [160, 320, 640]

instances_per_size = {
    160: [inst for inst in instances if inst.startswith("N160_")],
    320: [inst for inst in instances if inst.startswith("N320_")],
    640: [inst for inst in instances if inst.startswith("N640_")]
}

size_per_instance = {
    inst: int(inst.split("_")[0][1:])
    for inst in instances
}

num_snapshots = 30