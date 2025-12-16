#include "solver/nsbrkga/decoder.hpp"
#include <cmath>
#include <algorithm>
#include <limits>

namespace bmcp {

Decoder::Decoder(const Instance & instance) : instance(instance) {}

// Método decode exigido pelo solver
std::vector<double> Decoder::decode(NSBRKGA::Chromosome & chromosome, bool rewrite) {
    // 1. Gera a solução baseada no cromossomo
    Solution sol = decode_to_solution(chromosome);

    // 2. Lógica de Rewrite (Opcional/Futura)
    // No decoder simples, o mapeamento é determinístico e direto,
    // então não há "melhoria" para escrever de volta no cromossomo.
    // if (rewrite) { ... }

    // 3. Retorna os custos para o processo de ordenação do NSBRKGA
    return sol.cost;
}

// Lógica interna de decodificação
Solution Decoder::decode_to_solution(const std::vector<double>& chromosome) const {
    unsigned N = instance.num_nodes;
    unsigned K = instance.num_terminals;

    std::vector<int> partitions(N);
    std::vector<unsigned> partition_sizes(K, 0);

    // --- Passo 1: Definir Partições ---
    for (unsigned u = 0; u < N; ++u) {
        int assigned_partition = -1;
        bool is_terminal = false;

        // Verifica se é terminal (Restrição Fixa)
        for (unsigned k = 0; k < K; ++k) {
            // Nota: instance.terminals já deve estar em 0-based
            if (instance.terminals[k] == u) {
                assigned_partition = k;
                is_terminal = true;
                break;
            }
        }

        // Se não for terminal, o gene define a partição
        if (!is_terminal) {
            double allele = chromosome[u];
            // Proteção para o caso raro de allele == 1.0
            if (allele >= 1.0) allele = 0.999999;
            
            // Mapeia [0, 1) -> [0, K-1]
            assigned_partition = (int)(allele * K);
        }

        partitions[u] = assigned_partition;
        
        // Contabiliza tamanho da partição para o Objetivo 2
        if (assigned_partition >= 0 && assigned_partition < (int)K) {
            partition_sizes[assigned_partition]++;
        }
    }

    // --- Passo 2: Calcular Custo do Corte (Obj 1) ---
    double cut_cost = 0.0;

    for (unsigned u = 0; u < N; ++u) {
        int part_u = partitions[u];

        for (const auto& edge : instance.G[u]) {
            unsigned v = edge.dst;
            
            // Verifica aresta apenas uma vez (u < v) para grafos não direcionados
            if (u < v) {
                int part_v = partitions[v];
                // Se aresta cruza partições diferentes, soma o custo
                if (part_u != part_v) {
                    cut_cost += edge.cost;
                }
            }
        }
    }

    // --- Passo 3: Calcular Tamanho da Maior Componente (Obj 2) ---
    unsigned max_size = 0;
    for (unsigned s : partition_sizes) {
        if (s > max_size) max_size = s;
    }

    // Cria o vetor de custos: {Corte, MaiorComponente}
    std::vector<double> costs = { cut_cost, (double)max_size };

    // Retorna a solução construída
    return Solution(instance, partitions, costs);
}

} // namespace bmcp