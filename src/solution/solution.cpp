#include "solution/solution.hpp"
#include <algorithm>
#include <numeric>
#include <limits>

namespace bmcp {
bool Solution::dominates(const std::vector<double> & costA,
                         const std::vector<double> & costB) {
    if(costA.size() != costB.size()) {
        return false;
    }

    bool at_least_as_good = true, better = false;

    for(std::size_t i = 0; i < costA.size() && at_least_as_good; i++) {
        if(costA[i] > costB[i] + std::numeric_limits<double>::epsilon()) {
            at_least_as_good =  false;
        } else if(costA[i] < costB[i] - std::numeric_limits<double>::epsilon()) {
            better = true;
        }
    }

    return at_least_as_good && better;
}

void Solution::init() {
    
    this->cost.resize(this->instance.num_objectives, 0.0);
    this->cost.assign(this->instance.num_objectives, 0.0);
}

Solution::Solution(const Instance & instance):
    instance(instance),
    componentes_solucao(instance.num_terminals,std::vector<unsigned>(0)),
    cost(instance.num_objectives, 0.0){}

Solution::Solution(const Instance & instance, 
             const std::vector<std::vector<unsigned>>  &componentes_solucao, 
             const std::vector<double> & cost)
    : instance(instance), componentes_solucao(componentes_solucao), cost(cost){}


bool Solution::dominates(const Solution & solution) const {
    return Solution::dominates(this->cost, solution.cost);
}

std::istream & operator >>(std::istream & is, Solution & solution) {
    return is;
}

std::ostream & operator <<(std::ostream & os, const Solution & solution) {
  
    return os;
}

}
