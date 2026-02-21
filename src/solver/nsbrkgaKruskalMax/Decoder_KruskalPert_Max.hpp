#pragma once

#include "solution/solution.hpp"
#include "chromosome.hpp"
#include "instance/instance.hpp"
#include <vector>

namespace bmcp {

class Decoder_KruskalPert_Max {
    public:

    // BMCP instance
    const Instance & instance;

    /// Auxiliary edge structure
    typedef struct {unsigned src; unsigned dst; unsigned cost;} edge;


    /// Auxiliary structure to store the edges of Graph
    std::vector<edge> list_edges;


    Decoder_KruskalPert_Max(const  Instance & instance);

    // Retorna custos para o NSBRKGA -> usado no processo evolutivo
    std::vector<double> decode(NSBRKGA::Chromosome & chromosome, bool rewrite);

    //Retorna OBJETO SOLUTION (usado no fim do processo evolutivo)
    Solution decode_to_solution(const std::vector<double>& chromosome);

    /// Custom union-find data structure functions
    void union_elements(
        std::vector<unsigned>& component, 
        std::vector<int>& terminal, 
        std::vector<unsigned>& rank, 
        std::vector<unsigned> &components_size,
        unsigned u, unsigned v
    );

    unsigned find_element(
        std::vector<unsigned>& component, 
        unsigned v
    );

      /// Quick Sort functions

    void quick_sort(
        std::vector<double>& chromosome, 
        std::vector<edge> &edges, 
        int start, int end
    );

    int separa(
        std::vector<double>& chromosome, 
        std::vector<edge> &edges, 
        int start, int end
    );

    void troca_d(std::vector<double> &v, int a, int b);
    void troca_e(std::vector<edge> &edges, int a, int b); 

};

} // namespace bmcp