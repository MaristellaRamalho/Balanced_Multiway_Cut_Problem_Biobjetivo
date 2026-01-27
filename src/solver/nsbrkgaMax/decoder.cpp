#include "solver/nsbrkgaMax/decoder.hpp"
#include <limits>
#include <iostream>
#include <algorithm>
#include <queue>
#include <vector>
#include <iomanip>
#include <cmath>



namespace bmcp
{

    Decoder::Decoder(const Instance &instance) : instance(instance), init_adjacency_list(instance.num_nodes, -1), position_edge_vector(instance.num_edges * 2, -1)
    {
        unsigned list_position = 0;
        unsigned edge_position = 0;
        unsigned u, v;

        for (u = 0; u < instance.num_nodes; u++)
        {
            init_adjacency_list[u] = list_position;

            std::vector<Instance::edge> u_list = instance.G[u];

            for (unsigned i = 0; i < u_list.size(); i++)
            {
                v = u_list[i].dst;

                if (u < v)
                {
                    position_edge_vector[list_position + i] = edge_position;
                    edge_position++;
                }
                else
                {
                    position_edge_vector[list_position + i] = position_edge_vector[init_adjacency_list[v] + instance.get_edge_index(v, u)];
                }
            }
            list_position += u_list.size();
        }
    }


    Solution Decoder::decode_to_solution(const std::vector<double>& chromosome)  {

        //cópia local do cromossomo 
        NSBRKGA::Chromosome local_chrom = chromosome;

        std::vector<int> color_node(instance.num_nodes,-1);
        std::vector<bool> visited_node(instance.num_nodes, false);

        /// Determina a cor dos nós não-terminal
        for (unsigned u = 0; u < instance.num_nodes; u++)
        {
            color_node[u] = std::floor(local_chrom[u] * instance.num_terminals);
        }

        /// Determina a cor de cada dos nós terminal
        for (unsigned i = 0; i < instance.num_terminals; i++)
        {
            unsigned s = instance.terminals[i];
            color_node[s] = i;
            // TODO: atualizar cromossomo com a cor dos terminais também
        }

        std::vector<unsigned> components_size;
        std::vector<std::vector<unsigned>> componentes_solucao(instance.num_terminals,std::vector<unsigned>(0));

        // realiza a marcação dos nós que originalmente podem ser visitados a partir de um terminal
        double naturally_cut_cost = bfs_visited_nodes(color_node, visited_node, components_size);

        // recolore nós isolados e calcula valor do corte
        double discount_cut_cost = bfs_recolor_nodes(color_node, visited_node, local_chrom, components_size);

        //Objetivo 1
        double custo_corte = (naturally_cut_cost - discount_cut_cost);

        //Objetivo 2
        int balanceamentoPerfeito = ceil((instance.num_nodes / (double)instance.num_terminals));
        int maxV = *std::max_element(components_size.begin(), components_size.end()); // maior num de vértices em uma componente

        std::vector<double> costs(instance.num_objectives, -1);
        costs[0] = custo_corte;
        costs[1] = maxV / (double) balanceamentoPerfeito;

        for(unsigned i = 0; i < instance.num_terminals; i++){
            unsigned s = instance.terminals[i];
            //cout << s << " = {";
            for(unsigned u = 0; u < instance.num_nodes; u++){
                if(color_node[u] == color_node[s]){
                    //cout << u << " ";
                    componentes_solucao[i].push_back(u);
                }
            }
        }

        return Solution(instance, componentes_solucao, costs);


    }


    std::vector<double> Decoder::decode(NSBRKGA::Chromosome &chromosome, bool)
    {

        /// Armazena a cor de cada nó
        std::vector<int> color_node(instance.num_nodes, -1);

        /// Marcador de nós que originalmente podem ser visitados a partir de um terminal
        std::vector<bool> visited_node(instance.num_nodes, false);

        /// Determina a cor dos nós não-terminal
        for (unsigned u = 0; u < instance.num_nodes; u++)
        {
            color_node[u] = std::floor(chromosome[u] * instance.num_terminals);
        }

        /// Determina a cor de cada dos nós terminal
        for (unsigned i = 0; i < instance.num_terminals; i++)
        {
            unsigned s = instance.terminals[i];
            color_node[s] = i;
            // TODO: atualizar cromossomo com a cor dos terminais também
        }

        std::vector<unsigned> components_size;

        // realiza a marcação dos nós que originalmente podem ser visitados a partir de um terminal
        double naturally_cut_cost = bfs_visited_nodes(color_node, visited_node, components_size);

        // recolore nós isolados e calcula valor do corte
        double discount_cut_cost = bfs_recolor_nodes(color_node, visited_node, chromosome, components_size);

        //Objetivo 1 - corte normalizado pela soma dos custos das arestas
        double custo_corte = (naturally_cut_cost - discount_cut_cost)/ (double) (instance.cumulative_edge_cost);

        //Objetivo 2 - balanceamento baseado em penalidade do tipo Max -> normalizado por gd_max
        int balanceamentoPerfeito = ceil((instance.num_nodes / (double)instance.num_terminals));
        int maxV = *std::max_element(components_size.begin(), components_size.end()); // maior num de vértices em uma componente

        double gd = maxV - balanceamentoPerfeito;
        double gd_max = instance.num_nodes - (instance.num_terminals - 1) - balanceamentoPerfeito;

        std::vector<double> costs(instance.num_objectives, -1);
        costs[0] = custo_corte;
        costs[1] = gd / gd_max;

        return costs;
    }

    //-----------------------------[ Calcula nós que podem ser visitados ]--------------------------------//

double Decoder::bfs_visited_nodes(
    std::vector<int> &color_node,
    std::vector<bool> &visited_node,
    std::vector<unsigned> &components_size)
{
    /// Armazena o custo acumulado dos cortes
    double cut_cost = 0;

    /// Fila que armazena os nós encontrados
    std::queue<unsigned> queue;

    /// Armazena o número de vezes que um arco apareceu na fronteira de um corte
    std::vector<unsigned> num_cuts_edge(instance.num_edges, 0);

    unsigned edge_index = 0;
    unsigned terminal_index = 0;
    components_size.resize(instance.num_terminals, 0);

    for (unsigned s : instance.terminals)
    {

        visited_node[s] = true;
        queue.push(s);

        while (!queue.empty())
        {

            unsigned u = queue.front();
            queue.pop();
            components_size[terminal_index]++;

            /// Obtem a lista de arestas que saem de u
            const std::vector<Instance::edge> &u_list = instance.G[u];

            for (unsigned i = 0; i < u_list.size(); i++)
            {
                unsigned v = u_list[i].dst;

                if (color_node[v] == color_node[u])
                {
                    if (visited_node[v] == false)
                    {
                        visited_node[v] = true;
                        queue.push(v);
                    }
                }
                else
                {
                    /// Calcula o índice do arco no vetor
                    edge_index = position_edge_vector[init_adjacency_list[u] + i];

                    /// Incrementa o número de fronteiras que o arco foi encontrado
                    num_cuts_edge[edge_index]++;

                    /// Considera o custo deste arco apenas uma vez
                    if (num_cuts_edge[edge_index] == 1)
                    {
                        cut_cost += u_list[i].cost;
                    }
                }
            }
        }
        terminal_index++;
    }

    return cut_cost;
}

//-----------------------------[ Recolore nós ]--------------------------------//

double Decoder::bfs_recolor_nodes(
    std::vector<int> &color_node,
    std::vector<bool> &naturally_visited_node,
    NSBRKGA::Chromosome &chromosome,
    std::vector<unsigned> &components_size)
{
    /// Armazena o custo acumulado das arestas que foram removidas de fronteiras de cortes
    double discount_edges_cost = 0;

    /// Fila  que armazena os nós encontrados
    std::queue<unsigned> queue;

    ///
    std::vector<bool> visited_node(instance.num_nodes, false);

    /////////////////////////////////////////////////
    // Breadth-first search para encontrar e recolorir
    // nós que não puderam ser originalmente visitados
    /////////////////////////////////////////////////

    for (unsigned w = 0; w < instance.num_nodes; w++)
    {

        if (naturally_visited_node[w] == false and visited_node[w] == false)
        {

            visited_node[w] = true;
            queue.push(w);

            /// Armazena o custo das arestas na fronteira da componente formada
            /// por essa busca separado por cada cor encontrada
            std::vector<unsigned> cost_edges_border_by_color(instance.num_terminals, 0);

            /// Armazena o rótulo dos nós que não foram "naturalmente" visitados para posterior recoloração
            std::vector<unsigned> nodes_to_recolor;

            while (!queue.empty())
            {

                /// Remove o primeiro nó da fila de encontrados
                unsigned u = queue.front();
                queue.pop();

                /// Insere u na lista de recoloração
                nodes_to_recolor.push_back(u);

                /// Obtém a lista de arestas que saem de u
                const std::vector<Instance::edge> &u_list = instance.G[u];

                for (unsigned i = 0; i < u_list.size(); i++)
                {

                    unsigned v = u_list[i].dst;
                    unsigned cost = u_list[i].cost;

                    if (naturally_visited_node[v] == false)
                    {
                        if (visited_node[v] == false)
                        {
                            visited_node[v] = true;
                            queue.push(v);
                        }
                        // else
                        // v já foi visitado nessa busca
                    }
                    else
                    {
                        cost_edges_border_by_color[color_node[v]] += cost;
                    }
                }
            }

            double best_border_cost = 0;
            double best_border_color = -1;

            for (unsigned color = 0; color < instance.num_terminals; color++)
            {
                if (cost_edges_border_by_color[color] > best_border_cost)
                {
                    best_border_cost = cost_edges_border_by_color[color];
                    best_border_color = color;
                }
            }

            // Encontra para a componente de qual terminal as componentes isoladas foram atribuídas
            components_size[best_border_color] += nodes_to_recolor.size();

            discount_edges_cost += best_border_cost;

            if (best_border_cost > 0)
            {
                for (unsigned u : nodes_to_recolor)
                {
                    // Altera a cor do nó u
                    color_node[u] = best_border_color;

                    // Converte o alelo do nó u no cromossomo
                    chromosome[u] = ((double)color_node[u] / (double)instance.num_terminals) + ((double)1 / (2 * instance.num_terminals));

                    // TODO: marcar ele como naturally visited também
                }
            }
        }
    }

    return discount_edges_cost;
}


} // namespace bmcp