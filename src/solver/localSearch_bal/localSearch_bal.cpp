#include "solver/localSearch_bal/localSearch_bal.hpp"
#include <algorithm>

namespace bmcp
{
    void switchSingleNodeColor::improve(const Instance &instance, std::vector<unsigned> &components_size, std::vector<std::vector<unsigned>> &componentes_solucao, std::vector<double> &chromosome, std::vector<double> &costs, unsigned max_local_search_iterations)
    {
        bool improve = 1;
        int cont = 0;

        //std::cout << "max_local_search_iterations: " << max_local_search_iterations << "\n\n";
        while (improve == 1 && cont < max_local_search_iterations)
        {
            //std::cout << "########################## iniciando iteração busca local (iteração " << cont + 1 <<") ########################### \n";
            double delta_corte = 0;

            // Tamanho da maior componente
            int maxV = *std::max_element(components_size.begin(), components_size.end());

            // Encontra indice da maior componente
            auto iterator = std::find(components_size.begin(), components_size.end(), maxV);
            unsigned maxVindex = iterator - components_size.begin();

            //std::cout << "maxV: " << maxV << "| maxVindex: " << maxVindex << "\n";

            // Itera sobre os vertices da maior componente
            unsigned u, v, cost;
            unsigned color_node_u, color_node_v, new_color_node_u;
            bool encontrou = 0;
            std::vector<Instance::edge> u_list;

            for (unsigned i = 0; i < components_size[maxVindex]; i++)
            {
                u = componentes_solucao[maxVindex][i];

                // pula o vertice se ele for terminal (não mudamos a cor de um terminal)
                auto iterator = std::find(instance.terminals.begin(), instance.terminals.end(), u);
                if (iterator != instance.terminals.end())
                {
                    //std::cout << u << " é um vertice terminal \n";
                    continue;
                }

                // olha para a lista de adjacencia de u (se u não for terminal)
                u_list = instance.G[u];
                //std::cout << "Lista de adjacencia de " << u << ": \n";
                for (unsigned j = 0; j < u_list.size(); j++)
                {
                    v = u_list[j].dst;
                    cost = u_list[j].cost;

                    color_node_u = std::floor(chromosome[u] * instance.num_terminals);
                    color_node_v = std::floor(chromosome[v] * instance.num_terminals);

                    //std::cout << "( " << u << "," << v << "," << cost << ") | color_node_" << v << ": " << color_node_v << "\n";

                    unsigned sizeComponentv = components_size[color_node_v];

                    // Se u e v NÃO estão na mesma componente E v esta em uma componente de tamanho menor que u -> aplica operação
                    if (color_node_u != color_node_v && components_size[color_node_v] < components_size[color_node_u])
                    {
                        //std::cout << u << " e " << v << " NÃO estão na mesma componente e " << v << " esta em uma componente MENOR que a de " << u << "\n";
                        //std::cout << u << " receberá a cor de " << v << "\n";
                        // u recebe cor de v
                        new_color_node_u = std::floor(chromosome[v] * instance.num_terminals);
                        //std::cout << "nova cor de " << u << ": " << new_color_node_u << "\n";
                        encontrou = 1;
                        break; // para na primeira ocorrencia -> não explora todos os vizinhos de u
                    }
                }

                if (encontrou)
                {
                    break; // não olha outros nós da componente de u
                }
            }

            if(!encontrou){ // para a busca pq não é possivel aplicar operação
                break;
            }

            // calula o custo da operação
            u_list = instance.G[u];
            //std::cout << "Lista de adjacencia de " << u << ": \n";
            for (unsigned j = 0; j < u_list.size(); j++)
            {
                v = u_list[j].dst;
                cost = u_list[j].cost;

                color_node_v = std::floor(chromosome[v] * instance.num_terminals);

                //std::cout << "( " << u << "," << v << "," << cost << ") | color_node_" << v << ": " << color_node_v << "\n";

                // nova cor de u == cor de v -> aresta precisa ser descontada do corte
                if (new_color_node_u == color_node_v)
                {
                    delta_corte -= cost;
                    //std::cout << "aresta ( " << u << " , " << v << ") tirada do corte \n";
                }
                else if (color_node_u == color_node_v && new_color_node_u != color_node_v)
                { // u e v eram da mesma cor e agr são de cores diferentes -> aresta entra no corte
                    delta_corte += cost;
                    //std::cout << "aresta ( " << u << " , " << v << ") inserida do corte \n";
                } // (u, v) eram de cores distintas e continuam sendo -> aresta ja foi computada -> não muda nada
            }

            if (costs[0] + delta_corte <= costs[0])
            {   // operação não piorou corte
                // muda cromossomo -> u recebe nova cor
                chromosome[u] = (new_color_node_u + 0.5) / (double) instance.num_terminals;
                costs[0] = costs[0] + delta_corte;

                // atualiza components_size
                components_size[color_node_u] -= 1;
                components_size[new_color_node_u] += 1;

                // atualiza componentes_solucao
                componentes_solucao[color_node_u].erase(std::remove(componentes_solucao[color_node_u].begin(), componentes_solucao[color_node_u].end(), u), componentes_solucao[color_node_u].end());
                componentes_solucao[new_color_node_u].push_back(u);

                //atualiza balanceamento
                int balanceamentoPerfeito = ceil((instance.num_nodes / (double)instance.num_terminals));
                int newMaxV = *std::max_element(components_size.begin(), components_size.end()); // maior num de vértices em uma componente
                costs[1] = newMaxV / (double) balanceamentoPerfeito;


               /* 
                for (unsigned i = 0; i < componentes_solucao.size(); i++)
                {
                    std::cout << "Total de nós na componente " << i << " : " << componentes_solucao[i].size() << "\n";

                    std::cout << i << " = {";
                    for (unsigned u = 0; u < componentes_solucao[i].size(); u++)
                    {
                        std::cout << componentes_solucao[i][u] << " ";
                    }
                    std::cout << "}" << "\n";
                }*/

                //std::cout << "cromossomo[ " << u << "] = " << chromosome[u] << "\nnovo custo do corte: " << costs[0] << "\n";
                improve = 1;
            }
            else
            {
                //std::cout << "Não houve melhora : novo custo do corte seria " << costs[0] + delta_corte << "\n";
                //std::cout << "PARANDO BUSCA \n";
                improve = 0; // não tem melhora -> para
            }
            cont += 1;
        }
    }
}