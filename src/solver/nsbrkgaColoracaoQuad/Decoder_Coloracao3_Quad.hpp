#pragma once

#include "solution/solution.hpp"
#include "chromosome.hpp"
#include "instance/instance.hpp"
#include <vector>

namespace bmcp {

class Decoder_Coloracao3_Quad {
    public:

     /// Auxiliary edge structure
    typedef struct {unsigned src; unsigned dst; unsigned cost; unsigned edge_index; } edge;

    const Instance & instance;

    /// Position of the beginning of the adjacency list of each node in vector
    std::vector<unsigned> init_adjacency_list;

     /// Position of each edge in the edge vector (mapping 2*m -> m)
    std::vector<unsigned> position_edge_vector;


    Decoder_Coloracao3_Quad(const Instance & instance);

    // Retorna custos para o NSBRKGA
    std::vector<double> decode(NSBRKGA::Chromosome & chromosome, bool rewrite);

    //Retorna OBJETO SOLUTION (que o Solver utiliza para armazenar soluções)
    Solution decode_to_solution(const std::vector<double>& chromosome);

    /// Search edges in cut

    double bfs_visited_nodes(std::vector<int>& color_node, std::vector<bool>& visited_node, std::vector<unsigned>& components_size);

    double bfs_recolor_nodes(std::vector<int>& color_node, std::vector<bool>& visited_node, NSBRKGA::Chromosome& chromosome,  std::vector<unsigned>& components_size);

    unsigned get_edge_index(unsigned u, unsigned v);

};

} // namespace bmcp
