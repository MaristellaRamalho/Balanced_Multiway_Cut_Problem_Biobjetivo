#include "instance/instance.hpp"
#include "chromosome.hpp"


namespace bmcp{
    class switchSingleNodeColor{
        public:

        static void improve(const Instance & instance, std::vector<unsigned> & components_size, std::vector<std::vector<unsigned>> &componentes_solucao, std::vector<double>& chromosome, std::vector<double> &costs, unsigned max_local_search_iterations);

    };
}