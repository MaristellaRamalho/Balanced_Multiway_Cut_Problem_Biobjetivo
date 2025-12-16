#pragma once

#include "solution/solution.hpp"
#include "chromosome.hpp"
#include "instance/instance.hpp"
#include <vector>

namespace bmcp {

class Decoder {
    public:
    const Instance & instance;

    Decoder(const Instance & instance);

    // Método principal chamado pelo NSBRKGA
    // Permite modificar o cromossomo se rewrite == true
    std::vector<double> decode(NSBRKGA::Chromosome & chromosome, bool rewrite);

    // Método auxiliar para criar o objeto Solution completo (const)
    Solution decode_to_solution(const std::vector<double>& chromosome) const;
};

} // namespace bmcp