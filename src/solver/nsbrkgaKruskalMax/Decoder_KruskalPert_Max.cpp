#include "solver/nsbrkgaKruskalMax/Decoder_KruskalPert_Max.hpp"
#include <limits>
#include <iostream>
#include <algorithm>
#include <queue>
#include <vector>
#include <iomanip>
#include <map>
#include <cmath>

namespace bmcp
{

    Decoder_KruskalPert_Max::Decoder_KruskalPert_Max(const Instance &instance) : instance(instance), list_edges(instance.num_edges)
    {
        unsigned u, v, cost;
        unsigned edge_position = 0;

        /// Inserts each edge into a list
        for (u = 0; u < instance.num_nodes; u++)
        {
            std::vector<Instance::edge> u_list = instance.G[u];

            for (unsigned i = 0; i < u_list.size(); i++)
            {
                v = u_list[i].dst;
                cost = u_list[i].cost;

                if (u < v)
                { // does not insert reverse arcs
                    list_edges[edge_position] = {u, v, cost};
                    edge_position++;
                }
            }
        }
    }

    Solution Decoder_KruskalPert_Max::decode_to_solution(const std::vector<double> &chromosome)
    {
        /// edges cuted
        double custo_corte = 0;

        /// Copy vector of edges
        std::vector<edge> edges = list_edges;

        /// Auxiliar vector for pertuberd cost of edges
        std::vector<double> perturbed_costs(instance.num_edges);

        /// Structures for union-find
        std::vector<unsigned> component(instance.num_nodes, 0);
        std::vector<int> terminal(instance.num_nodes, -1);
        std::vector<unsigned> rank(instance.num_nodes, 0);
        std::vector<unsigned> components_size(instance.num_nodes, 1);

        /// Mark who the component is and the terminal that each node is part of
        for (unsigned v = 0; v < instance.num_nodes; v++)
        {
            component[v] = v;
            terminal[v] = -1;
            rank[v] = 0;
        }

        for (unsigned s : instance.terminals)
        {
            terminal[s] = s;
        }

        int N = 10;

        /// Upsets the cost of edges
        for (unsigned i = 0; i < instance.num_edges; i++)
        {
            // perturbed_costs[i] = (edges[i].cost * chromosome[i]) * -1;
            perturbed_costs[i] = ((double)(pow(2, N / 2) * edges[i].cost) / (double)(pow(2, (N * (1 - chromosome[i]))))) * -1;
        }

        /// Order the chromosomesome based on the value of the alleles.
        /// Modifies the position of the edges together
        quick_sort(perturbed_costs, edges, 0, chromosome.size() - 1);

        /// Auxiliary variables
        unsigned u, v, cost;
        unsigned cu, cv;

        /// Traverses the edge vector by adding the edges that
        /// do not join components with different terminals.
        /// In the opposite case, the edge is added to the cut.
        for (unsigned i = 0; i < instance.num_edges; i++)
        {
            u = edges[i].src;
            v = edges[i].dst;
            cost = edges[i].cost;

            cu = find_element(component, u);
            cv = find_element(component, v);

            if (cu != cv)
            {
                if (terminal[cu] == -1 || terminal[cv] == -1)
                    // union atualiza components_size
                    union_elements(component, terminal, rank, components_size, u, v);
                else
                    // uses the original cost
                    custo_corte += cost;
            }
        }

        ////// Econtrando as componentes formadas

        // Usando map porque usamos o nome do terminal, que pode exceder o numero de terminais (Ex: terminais podem ser : 112 81 52 110 40 59 107 62 146 42)
        std::map<int,std::vector<unsigned>> componentes;

        // Percorre os nós do grafo encontando o termninal representante e então insere o vértice na componente desse terminal
        //  componentes[112] = {1, 5 75, 112, ...}
        
        for (unsigned v = 0; v < instance.num_nodes; v++)
        {
            componentes[terminal[find_element(component, v)]].push_back(v);
        }

        // Armazena as componentes da solução -> mapeando set para vector
        std::vector<std::vector<unsigned>> componentes_solucao;
       
        for(unsigned t : instance.terminals){
            componentes_solucao.push_back(componentes[t]);
        }

        std::vector<double> costs(instance.num_objectives, -1);

        // Objetivo 1
        costs[0] = custo_corte;

        // Objetivo 2
        int balanceamentoPerfeito = ceil((instance.num_nodes / (double)instance.num_terminals));
        int maxV = *std::max_element(components_size.begin(), components_size.end()); // maior num de vértices em uma componente

        costs[1] = maxV / (double)balanceamentoPerfeito;

        return Solution(instance, componentes_solucao, costs);
    }

    std::vector<double> Decoder_KruskalPert_Max::decode(NSBRKGA::Chromosome &chromosome, bool)
    {

        /// edges cuted
        double custo_corte = 0;

        /// Copy vector of edges
        std::vector<edge> edges = list_edges;

        /// Auxiliar vector for pertuberd cost of edges
        std::vector<double> perturbed_costs(instance.num_edges);

        /// Structures for union-find
        std::vector<unsigned> component(instance.num_nodes, 0);
        std::vector<int> terminal(instance.num_nodes, -1);
        std::vector<unsigned> rank(instance.num_nodes, 0);
        std::vector<unsigned> components_size(instance.num_nodes, 1);

        /// Mark who the component is and the terminal that each node is part of
        for (unsigned v = 0; v < instance.num_nodes; v++)
        {
            component[v] = v;
            terminal[v] = -1;
            rank[v] = 0;
        }

        for (unsigned s : instance.terminals)
        {
            terminal[s] = s;
        }

        int N = 10;

        /// Upsets the cost of edges
        for (unsigned i = 0; i < instance.num_edges; i++)
        {
            // perturbed_costs[i] = (edges[i].cost * chromosome[i]) * -1;
            perturbed_costs[i] = ((double)(pow(2, N / 2) * edges[i].cost) / (double)(pow(2, (N * (1 - chromosome[i]))))) * -1;
        }

        /// Order the chromosomesome based on the value of the alleles.
        /// Modifies the position of the edges together
        quick_sort(perturbed_costs, edges, 0, chromosome.size() - 1);

        /// Auxiliary variables
        unsigned u, v, cost;
        unsigned cu, cv;

        /// Traverses the edge vector by adding the edges that
        /// do not join components with different terminals.
        /// In the opposite case, the edge is added to the cut.
        for (unsigned i = 0; i < instance.num_edges; i++)
        {
            u = edges[i].src;
            v = edges[i].dst;
            cost = edges[i].cost;

            cu = find_element(component, u);
            cv = find_element(component, v);

            if (cu != cv)
            {
                if (terminal[cu] == -1 || terminal[cv] == -1)
                    // union atualiza components_size
                    union_elements(component, terminal, rank, components_size, u, v);
                else
                    // uses the original cost
                    custo_corte += cost;
            }
        }

        // Objetivo 2 - balanceamento baseado em penalidade do tipo Max -> normalizado por gd_max
        int balanceamentoPerfeito = ceil((instance.num_nodes / (double)instance.num_terminals));
        int maxV = *std::max_element(components_size.begin(), components_size.end()); // maior num de vértices em uma componente

        double gd = maxV - balanceamentoPerfeito;
        double gd_max = instance.num_nodes - (instance.num_terminals - 1) - balanceamentoPerfeito;

        std::vector<double> costs(instance.num_objectives, -1);
        // Objetivo 1 - corte normalizado pela soma dos custos das arestas
        costs[0] = custo_corte / (double)(instance.cumulative_edge_cost);
        costs[1] = gd / gd_max;

        return costs;
    }

    //-----------------------------[ Union ]--------------------------------//

    // Union retorna um vetor de components_size

    void Decoder_KruskalPert_Max::union_elements(std::vector<unsigned> &component, std::vector<int> &terminal, std::vector<unsigned> &rank,  std::vector<unsigned> &components_size, unsigned u, unsigned v)
    {
        unsigned c1 = find_element(component, u);
        unsigned c2 = find_element(component, v);

        if (rank[c1] == rank[c2])
            rank[c1]++;

        if (rank[c1] > rank[c2])
        {
            component[c2] = c1;

            //atualiza tamanho das componentes
            components_size[c1] += components_size[c2];
            components_size[c2] = 0;

            if (terminal[c1] == -1)
                terminal[c1] = terminal[c2];
        }
        else
        {
            component[c1] = c2;

            //atualiza tamanho das componentes
            components_size[c2] += components_size[c1];
            components_size[c1] = 0;

            if (terminal[c2] == -1)
                terminal[c2] = terminal[c1];
        }
    }

    //-----------------------------[ Find ]--------------------------------//

    unsigned Decoder_KruskalPert_Max::find_element(std::vector<unsigned> &component, unsigned v)
    {
        if (component[v] == v)
            return v;

        component[v] = find_element(component, component[v]);

        return component[v];
    }

    //-----------------------------[ Quick sort ]--------------------------------//

    void Decoder_KruskalPert_Max::troca_d(std::vector<double> &v, int a, int b)
    {
        double aux = v[a];
        v[a] = v[b];
        v[b] = aux;
    }

    void Decoder_KruskalPert_Max::troca_e(std::vector<edge> &edges, int a, int b)
    {
        edge aux = edges[a];
        edges[a] = edges[b];
        edges[b] = aux;
    }

    // separa v[p .. r] e devolve a posição do pivô
    int Decoder_KruskalPert_Max::separa(std::vector<double> &v, std::vector<edge> &edges, int p, int r)
    {
        int i, j;
        double c = v[r]; // c é o pivô
        i = p;
        for (j = p; j < r; j++)
            if (v[j] <= c) // crescente
            {
                troca_d(v, i, j);
                troca_e(edges, i, j);
                i++;
            }
        troca_d(v, i, r);
        troca_e(edges, i, r);
        return i;
    }

    // p indica a primeira posicao e r a ultima
    void Decoder_KruskalPert_Max::quick_sort(std::vector<double> &v, std::vector<edge> &edges, int p, int r)
    {
        int i;
        if (p < r) // se vetor corrente tem mais de um elemento
        {
            i = separa(v, edges, p, r); // i é a posição do pivô após a separação
            quick_sort(v, edges, p, i - 1);
            quick_sort(v, edges, i + 1, r);
        }
    }
}