#pragma once

#include "solution/solution.hpp"
#include "chromosome.hpp"
#include "instance/instance.hpp"
#include <vector>
#include <string>

namespace bmcp {

class Decoder_Coloracao_Base {
    public:

     /// Auxiliary edge structure
    typedef struct {unsigned src; unsigned dst; unsigned cost; unsigned edge_index; } edge;

    const Instance & instance;

    unsigned max_local_search_iterations;

    std::string local_search_type;

    /// Position of the beginning of the adjacency list of each node in vector
    std::vector<unsigned> init_adjacency_list;

     /// Position of each edge in the edge vector (mapping 2*m -> m)
    std::vector<unsigned> position_edge_vector;

    /// Auxiliary structure to store the edges of Graph
    std::vector<edge> list_edges;

    Decoder_Coloracao_Base(const Instance & instance, std::string local_search_type, unsigned max_local_search_iterations = 0);

    // Retorna custos para o NSBRKGA
    std::vector<double> decode(NSBRKGA::Chromosome & chromosome, bool rewrite);

    //Retorna OBJETO SOLUTION (que o Solver utiliza para armazenar soluções)
    Solution decode_to_solution(const std::vector<double>& chromosome);

    /// Search edges in cut

    unsigned get_edge_index(unsigned u, unsigned v);

};

} // namespace bmcp
