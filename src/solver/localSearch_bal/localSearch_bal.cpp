#include "solver/localSearch_bal/localSearch_bal.hpp"
#include <algorithm>
#include <cmath>

#define DEBUG 0

namespace bmcp
{
    void switchSingleNodeColor::improve(const Instance &instance, std::vector<unsigned> &components_size, std::vector<std::vector<unsigned>> &componentes_solucao, std::vector<double> &chromosome, std::vector<double> &costs, unsigned max_local_search_iterations)
    {
        bool improve = true;
        unsigned cont = 0;

        int balanceamentoPerfeito = ceil((instance.num_nodes / (double)instance.num_terminals));

        while (improve && cont < max_local_search_iterations)
        {

            if(DEBUG) std::cout << "########## BUSCA LOCAL | iteração " << cont+1 << "##########\n";
           // Encontra a maior componente e seu índice 
            auto max_it = std::max_element(components_size.begin(), components_size.end());
            unsigned maxVindex = std::distance(components_size.begin(), max_it);

            if(DEBUG){
                std::cout << "maxV = " << components_size[maxVindex] << " | componente " << maxVindex << "\n";
            }

            // Itera sobre os vertices da maior componente
            unsigned u_target = 0;
            unsigned color_node_u = maxVindex;
            unsigned new_color_node_u = 0;
            bool encontrou = false;

            //procura um nó u valido para operação na maior componente
            const auto &maior_componente = componentes_solucao[maxVindex];

            for (unsigned i = 0; i < maior_componente.size(); i++)
            {
                unsigned u = maior_componente[i];

                // pula o vertice se ele for terminal (não mudamos a cor de um terminal)
                if(instance.is_terminal[u]) continue;

                //lista de adjacencia de u
                const auto &u_list = instance.G[u];

                if(DEBUG) std::cout << "Lista de adjacencia de " << u << ": \n";

                for (unsigned j = 0; j < u_list.size(); j++)
                {
                    unsigned v = u_list[j].dst;
                    unsigned color_node_v = std::floor(chromosome[v] * instance.num_terminals);

                    if(DEBUG){
                        unsigned cost = u_list[j].cost;
                         std::cout << "( " << u << "," << v << "," << cost << ") | color_node_" << v << ": " << color_node_v << "\n";
                    }

                    // Se u e v NÃO estão na mesma componente E v esta em uma componente de tamanho menor que u -> aplica operação
                    if (color_node_u != color_node_v && components_size[color_node_v] < components_size[color_node_u])
                    {
                        if(DEBUG){
                            std::cout << u << " e " << v << " NÃO estão na mesma componente e " << v << " esta em uma componente MENOR que a de " << u << "\n";
                            std::cout << u << " receberá a cor de " << v << "\n";
                        }

                        // u recebe cor de v
                        u_target = u;
                        new_color_node_u = color_node_v;

                        if(DEBUG) std::cout << "nova cor de " << u << ": " << new_color_node_u << "\n";
                        encontrou = true;
                        break; // para no primeiro vizinho que atende o criterio -> u recebe a cor de v
                    }
                }

                if (encontrou) break; // Se encontrou par (u,v) para fazer a operação não olha outros nós da maior componente
            }

            if(!encontrou) break; // não foi possivel aplicar operação -> olhou todos os nós da maior componente

            // foi possivel aplicar operação -> calula o custo da operação
            double delta_corte = 0;
            const auto &u_list = instance.G[u_target];

            if(DEBUG) std::cout << "Lista de adjacencia de " << u_target << ": \n";
            for (unsigned j = 0; j < u_list.size(); j++)
            {
                unsigned v = u_list[j].dst;
                unsigned cost = u_list[j].cost;

                unsigned color_node_v = std::floor(chromosome[v] * instance.num_terminals);

                if(DEBUG){
                    unsigned cost = u_list[j].cost;
                    std::cout << "( " << u_target << "," << v << "," << cost << ") | color_node_" << v << ": " << color_node_v << "\n";
                }

                // nova cor de u == cor de v -> aresta precisa ser descontada do corte
                if (new_color_node_u == color_node_v)
                {
                    delta_corte -= cost;
                    if(DEBUG) std::cout << "aresta ( " << u_target << " , " << v << ") tirada do corte \n";
                }
                else if (color_node_u == color_node_v)
                { // u e v eram da mesma cor e agr são de cores diferentes -> aresta entra no corte
                    delta_corte += cost;
                    if(DEBUG) std::cout << "aresta ( " << u_target << " , " << v << ") inserida do corte \n";
                } // (u, v) eram de cores distintas e continuam sendo -> aresta ja foi computada -> não muda nada
            }

            if (delta_corte <= 0) // aplicar operação não piora corte
            {   
                // muda cromossomo -> u recebe nova cor
                chromosome[u_target] = (new_color_node_u + 0.5) / (double) instance.num_terminals; // evita erro de arredondamento -> cair na cor errada
                costs[0] = costs[0] + delta_corte;

                // atualiza components_size
                components_size[color_node_u] -= 1;
                components_size[new_color_node_u] += 1;

                // atualiza componentes_solucao
                // remove u da componente antiga
                auto &comp_antiga = componentes_solucao[color_node_u];
                auto it = std::find(comp_antiga.begin(), comp_antiga.end(), u_target);
                if (it != comp_antiga.end()) {
                    *it = comp_antiga.back();
                    comp_antiga.pop_back();
                }
                // adiciona u na nova componente
                componentes_solucao[new_color_node_u].push_back(u_target);

                //atualiza balanceamento
                int newMaxV = *std::max_element(components_size.begin(), components_size.end()); // maior num de vértices em uma componente
                costs[1] = newMaxV / (double) balanceamentoPerfeito;
                improve = true;

               if(DEBUG)
                for (unsigned i = 0; i < componentes_solucao.size(); i++)
                {
                    std::cout << "Total de nós na componente " << i << " : " << componentes_solucao[i].size() << "\n";

                    std::cout << i << " = {";
                    for (unsigned u = 0; u < componentes_solucao[i].size(); u++)
                    {
                        std::cout << componentes_solucao[i][u] << " ";
                    }
                    std::cout << "}" << "\n";
                }

                if(DEBUG) std::cout << "cromossomo[ " << u_target << "] = " << chromosome[u_target] << "\nnovo custo do corte: " << costs[0] << "\n";
            }
            else
            {
                if(DEBUG){
                    std::cout << "Não houve melhora : novo custo do corte seria " << costs[0] + delta_corte << "\n";
                    std::cout << "PARANDO BUSCA \n";
                }

                improve = false; // não tem melhora -> para
            }
            cont++;
        }
    }
}