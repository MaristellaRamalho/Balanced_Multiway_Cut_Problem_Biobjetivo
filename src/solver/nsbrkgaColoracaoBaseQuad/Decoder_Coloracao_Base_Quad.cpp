#include "solver/nsbrkgaColoracaoBaseQuad/Decoder_Coloracao_Base_Quad.hpp"
#include "solver/localSearch_bal/localSearch_bal.hpp"
#include <limits>
#include <iostream>
#include <algorithm>
#include <queue>
#include <vector>
#include <iomanip>
#include <cmath>

#define DEBUG 0

namespace bmcp
{

     Decoder_Coloracao_Base_Quad::Decoder_Coloracao_Base_Quad(const Instance &instance, std::string local_search_type, unsigned max_local_search_iterations) :  instance(instance), local_search_type(local_search_type), max_local_search_iterations(max_local_search_iterations), init_adjacency_list(instance.num_nodes, -1), position_edge_vector(instance.num_edges * 2, -1),  list_edges(instance.num_edges)
    {
        unsigned list_position = 0;
        unsigned edge_position = 0;
        unsigned u, v, cost;

        for (u = 0; u < instance.num_nodes; u++)
        {
            init_adjacency_list[u] = list_position;

            std::vector<Instance::edge> u_list = instance.G[u];

            for (unsigned i = 0; i < u_list.size(); i++)
            {
                v = u_list[i].dst;
                cost = u_list[i].cost;

                if (u < v)
                {
                    position_edge_vector[list_position + i] = edge_position;
                    // does not insert reverse arcs
                    list_edges[edge_position] = {u, v, cost};
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



    Solution Decoder_Coloracao_Base_Quad::decode_to_solution(const std::vector<double>& chromosome)  {

        //cópia local do cromossomo 
        NSBRKGA::Chromosome local_chrom = chromosome;

        std::vector<int> color_node(instance.num_nodes,-1);

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

        if(DEBUG){
            for(unsigned i = 0; i < instance.num_nodes; i++){
                std::cout << "color_node[" << i << "] = " << color_node[i] << "\n";
            }
        }

        std::vector<unsigned> components_size(instance.num_terminals, 0);
        std::vector<std::vector<unsigned>> componentes_solucao(instance.num_terminals,std::vector<unsigned>(0));

        //Objetivo 1

        /// Copy vector of edges
        std::vector<edge> edges = list_edges;
        double custo_corte = 0;
        unsigned u, v, cost;

        for (unsigned i = 0; i < instance.num_edges; i++){
            u = edges[i].src;
            v = edges[i].dst;
            cost = edges[i].cost;

            if(color_node[u] != color_node[v]){
                // Grafo não direcionado -> aresta (u,v) = (v,u) -> inserida uma vez só na lista de arestas -> não precisa dividir por 2
                if(DEBUG){
                    std::cout << "\n ARESTA NO CORTE: (" << u << "," << v << "," << cost << ") \n";
                }
                custo_corte += cost;
            }
        }

        //Formando as componentes
        for(unsigned u = 0; u < instance.num_nodes; u++){
           components_size[color_node[u]]++;
           componentes_solucao[color_node[u]].push_back(u);
        }

        if(DEBUG){
            for(unsigned i = 0; i < instance.num_terminals; i++){
                std::cout << "Tamanho da componente do terminal " << instance.terminals[i] << " = " << components_size[i] << "\n";
            }
        }

        //Objetivo 2
        int balanceamentoPerfeito = ceil((instance.num_nodes / (double)instance.num_terminals));
        int maxV = *std::max_element(components_size.begin(), components_size.end()); // maior num de vértices em uma componente

        std::vector<double> costs(instance.num_objectives, -1);
        costs[0] = custo_corte;
        costs[1] = maxV / (double) balanceamentoPerfeito;

        if(DEBUG){
            std::cout << "f1-Custo do corte: " << custo_corte << "\n Balanceamento perfeito: " << balanceamentoPerfeito << "\n maxV: " << maxV << "\n f2-maxV/balPerfeito: " << costs[1] << "\n";
        }

        return Solution(instance, componentes_solucao, costs);

    }


    std::vector<double> Decoder_Coloracao_Base_Quad::decode(NSBRKGA::Chromosome &chromosome, bool)
    {

        /// Armazena a cor de cada nó
        std::vector<int> color_node(instance.num_nodes, -1);

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

        if(DEBUG){
            for(unsigned i = 0; i < instance.num_nodes; i++){
                std::cout << "color_node[" << i << "] = " << color_node[i] << "\n";
            }
        }


        std::vector<unsigned> components_size(instance.num_terminals, 0);
        std::vector<std::vector<unsigned>> componentes_solucao(instance.num_terminals,std::vector<unsigned>(0));


        //Objetivo 1

        /// Copy vector of edges
        std::vector<edge> edges = list_edges;
        double custo_corte = 0;
        unsigned u, v, cost;

        for (unsigned i = 0; i < instance.num_edges; i++){
            u = edges[i].src;
            v = edges[i].dst;
            cost = edges[i].cost;

            if(color_node[u] != color_node[v]){
                // Grafo não direcionado -> aresta (u,v) = (v,u) -> inserida uma vez só na lista de arestas -> não precisa dividir por 2
                if(DEBUG){
                    std::cout << "\n ARESTA NO CORTE: (" << u << "," << v << "," << cost << ") \n";
                }
                custo_corte += cost;
            }
        }

        for(unsigned u = 0; u < instance.num_nodes; u++){
           components_size[color_node[u]]++;
           componentes_solucao[color_node[u]].push_back(u);
        }

        if(DEBUG){
            for(unsigned i = 0; i < instance.num_terminals; i++){
                std::cout << "Tamanho da componente do terminal " << instance.terminals[i] << " = " << components_size[i] << "\n";
            }
        }

        //Objetivo 2 - balanceamento baseado na penalidade Quadrange -> normalizado por gd_max
        int balanceamentoPerfeito = ceil((instance.num_nodes / (double)instance.num_terminals));
        int maxV = *std::max_element(components_size.begin(), components_size.end()); // maior num de vértices em uma componente

        double gd = 0;

        //percorre todas as componentes
        for(int i = 0; i < instance.num_terminals; i++){
            int diferenca = std::max(0, (int)components_size[i] - balanceamentoPerfeito);
            gd += pow(diferenca, 2); 
        }

        double gd_max = instance.num_nodes - (instance.num_terminals - 1) - balanceamentoPerfeito;

        std::vector<double> costs(instance.num_objectives, -1);

        //Objetivo 1 - corte normalizado pela soma dos custos das arestas
        costs[0] = custo_corte / (double) (instance.cumulative_edge_cost);
        costs[1] = sqrt(gd) / gd_max;

        if(DEBUG){
            std::cout << "f1-Custo do corte: " << costs[0] << "\n Balanceamento perfeito: " << balanceamentoPerfeito << "\n maxV: " << maxV << " \ngd: " << gd << "\n gd_max: " << gd_max << "\n f2-gd/gd_max: " << costs[1] << "\n";
        }

        // vai aplicar busca local
        if(max_local_search_iterations > 0){
            // qual busca vai aplicar
            if(local_search_type == "switchSingleNodeColor"){
                switchSingleNodeColor::improve(instance,components_size, componentes_solucao, chromosome, costs, max_local_search_iterations, 'q');
            }
        }


        return costs;
    }


} // namespace bmcp