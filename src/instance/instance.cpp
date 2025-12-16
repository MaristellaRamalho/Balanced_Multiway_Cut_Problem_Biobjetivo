#include "instance/instance.hpp"
#include <algorithm>
#include <cmath>
#include <sstream>
#include <limits>
#include <iomanip>
#include <vector>

namespace bmcp
{

    void Instance::init()
    {
        this->num_objectives = 2; // (custo do corte, balanceamento)

        this->senses.resize(this->num_objectives, NSBRKGA::Sense::MINIMIZE);
        this->senses.assign(this->num_objectives, NSBRKGA::Sense::MINIMIZE);

        this->primal_bound.resize(this->num_objectives, 0.0);

        // ponto de refenecina objetivo 1: pior corte possivel -> soma dos custos de todas as arestas
        this->primal_bound[0] = (double)this->cumulative_edge_cost;

        // ponto de referencia objetivo 2: pior balanceamento -> próximo do número total de nós
        this->primal_bound[1] = (double)this->num_nodes;
    }

    Instance::Instance() : num_objectives(2),
                           num_nodes(0),
                           num_edges(0),
                           num_terminals(0),
                           cumulative_edge_cost(0) {}

    bool Instance::is_valid() const
    {
        if (this->num_nodes == 0)
            return false;
        if (this->terminals.size() != this->num_terminals)
            return false;
        if (this->cumulative_edge_cost == 0 && this->num_edges > 0)
            return false;
        return true;
    }

    std::istream &operator>>(std::istream &is, Instance &instance)
    {
        std::string line;
        std::string mark, discard;
        unsigned u, v, terminal;
        double cost;

        instance.cumulative_edge_cost = 0;
        instance.terminals.clear();

        // lógica para ler instancia do arquivo
        //  ignorar primeira linha (cabeçalho)

        if (!std::getline(is, line))
            return is;

        // lendo rotulos dos terminais na linha 2
        if (std::getline(is, line))
        {
            std::stringstream lineStream(line);

            lineStream >> instance.num_terminals;

            while (lineStream >> terminal)
            {
                instance.terminals.push_back(terminal);
            }
        }

        // lendo numero de nós e arestas
        if (!(is >> mark >> discard >> instance.num_nodes >> instance.num_edges))
            return is;

        // redimensiona o Grafo
        instance.G.clear();
        instance.G.resize(instance.num_nodes + 1);

        // lendo as arestas
        for (unsigned i = 0; i < instance.num_edges; i++)
        {
            is >> mark >> u >> v >> cost;
            instance.G[u].push_back({v, (unsigned int)cost});
            instance.G[v].push_back({u, (unsigned int)cost});

            // increment acumulative cost
            instance.cumulative_edge_cost += cost;
        }

        instance.init();
        return is;
    }

    std::ostream &operator<<(std::ostream &os, const Instance &instance)
    {
        os << "BMCP Instance:" << std::endl;
        os << "Nodes: " << instance.num_nodes << ", Edges: " << instance.num_edges << std::endl;
        os << "Terminals (" << instance.num_terminals << "): ";
        for (auto t : instance.terminals)
            os << t << " ";
        os << std::endl;
        os << "Cumulative Cost: " << instance.cumulative_edge_cost << std::endl;
        os << "Bounds: [" << instance.primal_bound[0] << ", " << instance.primal_bound[1] << "]" << std::endl;

        return os;
    }

    int Instance::get_edge_index(unsigned u, unsigned v) const
{
    const std::vector<edge>& u_list = this->G[u];

    for (unsigned edge_index = 0; edge_index < u_list.size(); edge_index++)
        if (u_list[edge_index].dst == v)
            return edge_index;

    return -1;
}

}
